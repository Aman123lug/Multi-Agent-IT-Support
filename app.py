import autogen
from dotenv import load_dotenv
import os
from utils import check_knowledge_base, reset_password, notify_support_team

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file or environment.")
else:
    print(f"OPENAI API Key loaded (starts with: {OPENAI_API_KEY[:4]}...)")


config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": OPENAI_API_KEY,
        "api_type": "openai" 
    },
]

llm_config = {
    "config_list": config_list, 
    "cache_seed": 42,
}

# 1. User Intake Agent
user_intake_agent = autogen.AssistantAgent(
    name="User_Intake_Agent",
    llm_config=llm_config,
    system_message="""You are the User Intake Agent. 
    Your role is to receive employee requests related to IT issues, extract key details (e.g., username, issue description, error messages),
    and clearly state who you are assigning the request to (Resolution Agent (preperred) or Escalation Agent) based on the complexity and nature of the issue."""
)

resolution_agent = autogen.AssistantAgent(
    name="Resolution_Agent",
    llm_config=llm_config,
    system_message = """You are the Resolution Agent in an IT Helpdesk system. Your primary objective is to diagnose and resolve common employee IT issues efficiently using the available tools and information. If you cannot resolve the issue after reasonable initial attempts, you must escalate it clearly.

    **Available Tools:**
    *   `check_knowledge_base(search_query: str)`: Searches internal KB for solutions to common problems (VPN, email, printer, slow computer). Use this first for general issues.
    *   `reset_password(username: str)`: Initiates a password reset. Use this *ONLY* when explicitly requested by the user AND they provide their username.

    **Your Workflow:**
    1.  **Analyze Request:** Carefully review the issue details provided by the User Intake Agent. Identify keywords and the core problem.
    2.  **Initial Checks (Optional but Recommended):**
        
    3.  **Knowledge Base Search:** Use `check_knowledge_base()` with relevant keywords from the user's request to find standard troubleshooting procedures or known issues. Report the findings from the KB.
    4.  **Suggest ONE Action/Step:** Based on the KB findings, service status, or general knowledge:
        *   Suggest **one single, clear troubleshooting step** for the user to try (e.g., "Could you please try restarting the VPN application?").
        *   **Document this step** in your response.
        *   Ask for confirmation from the user (via User_Proxy_Internal): "Please let me know if that step resolved the issue."
    5.  **Evaluate Outcome:** Analyze the simulated response from User_Proxy_Internal.
    6.  **Password Reset Handling:** If the *initial request* was specifically for a password reset and included a username, use `reset_password()`. Report the outcome clearly. Do NOT ask to reset passwords otherwise.
    7.  **Decide Next Step (Resolve or Escalate):**
        *   **If Resolved:** If the tool output confirms resolution (e.g., password reset initiated) or if the KB provided a clear solution the user could follow, state the resolution clearly. (e.g., "Password reset initiated, user should check email." or "The KB suggests checking [X], which should resolve the issue."). You might still end your turn here or wait for one more confirmation cycle if appropriate.
        *   **If Unresolved/Complex:** If the simulated user response indicates the suggested step failed, if the tools revealed a deeper issue (e.g., service outage, disabled account), if the KB suggests escalation, or if the problem is clearly beyond basic steps, you MUST escalate.
    8.  **Escalation Procedure:** If escalation is necessary, state **exactly**: 'Issue unresolved. Escalating to Escalation Agent for further assistance because [provide specific, concise reason - e.g., 'basic troubleshooting step failed', 'service outage confirmed', 'KB indicates requires manual check', 'complex issue requires deeper analysis'].'

    **Important Rules:**
    *   **Document Steps:** Clearly state what checks you performed (KB, status) and what steps you suggested in your responses.
    *   **One Step at a Time:** Only suggest one troubleshooting action for the user per turn.
    *   **Use Only Provided Tools:** Do not invent functions or try actions not listed.
    *   **Be Explicit:** Clearly state when you are checking KB, checking status, suggesting a step, or escalating.
    """,
    
    
)
# 2. Escalation Agent

escalation_agent = autogen.AssistantAgent(
    name="Escalation_Agent",
    llm_config=llm_config,
    system_message="""You are the Escalation Agent. You activate only when the Resolution Agent explicitly escalates an issue.
    Your role is to:
    1. Acknowledge the escalation explicitly.
    2. Generate a structured summary for human IT support, clearly outlining:
        - User Request
        - Steps Taken by Resolution Agent
        - Reason for Escalation
    3. Trigger a notification to IT support by creating a ticket with the notify_support_team() function, assigning an appropriate priority.
    4. Clearly state: 'Notifying human IT support team with ticket [TICKET_ID].'
    5. End your response with: TERMINATE""",

)


#  Group Chat Setup

groupchat = autogen.GroupChat(
    agents=[ user_intake_agent, resolution_agent, escalation_agent],
    messages=[],
    max_round=15 
)


master_agent = autogen.GroupChatManager(
    name="IT_Helpdesk_Coordinator", 
    groupchat=groupchat,
    llm_config=llm_config, 
    system_message="""You are the Master Agent (Coordinator).
    Your responsibility is overseeing all agents, ensuring effective communication and collaboration,
    and maintaining memory of past user requests to improve resolution tracking and future handling.
    Clearly document the flow and outcome of each request.""",
    max_consecutive_auto_reply=5,
   
    is_termination_msg=lambda msg: isinstance(msg, dict) and msg.get("content") and msg.get("content", "").strip().endswith("TERMINATE"),
)


# --- Chat Initiation Function ---

def initiate_it_helpdesk(user_request: str):
    """Initiates the IT help desk process with a user request."""
    if not user_request:
        print("Error: No user request provided.")
        return []

    groupchat.reset()

    try:
       
        user_intake_agent.initiate_chat(
            recipient=master_agent, 
            message=user_request,
            clear_history=True 
        )
        print(f"--- Helpdesk Chat Finished for: '{user_request}' ---")

    except Exception as e:
        print(f"\n!!! Error during chat execution: {e} !!!")
        import traceback
        traceback.print_exc()

    return groupchat.messages


if __name__ == "__main__":
    user_request_message = "My VPN is not working. I keep getting a 'connection failed' error when trying to log in."
    conversation_history = initiate_it_helpdesk(user_request_message)

    if conversation_history:
        for message in conversation_history:
            sender = message.get('name', message.get('role', 'Unknown'))
            content = message.get('content', '').strip()
            print(f"[{sender}]:\n{content}\n" + "-"*30)
    else:
        print("No conversation history recorded.")