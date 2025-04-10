import random
import time
from typing import Dict, Any, Literal # Keep necessary type hints
import uuid
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


tickets_database = {}

def notify_support_team(summary, priority="Medium"):
    ticket_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
    
    # Store ticket in the dictionary
    tickets_database[ticket_id] = {
        "summary": summary,
        "priority": priority,
        "status": "Open",
        "created": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    sender_email = "amangithub36@gmail.com"  
    receiver_email = "wsl@gmail.com"  
    password = os.getenv("EMAIL_PASSWORD")  
    

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"[{priority}] New Support Ticket: {ticket_id}"
    
    body = f"""
    New support ticket created:
    
    Ticket ID: {ticket_id}
    Priority: {priority}
    Created: {time.strftime("%Y-%m-%d %H:%M:%S")}
    
    Summary:
    {summary}
    
    Please log into the support portal to handle this ticket.
    """
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP("smtp.yourcompany.com", 587)  # Replace with your SMTP server
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)
        server.quit()
        print(f"Email notification sent for ticket {ticket_id}")
    except Exception as e:
        print(f"Failed to send email notification: {e}")
    
    return ticket_id
def reset_password(username: str) -> str:
    """
    Initiates a password reset for a username. Only use when explicitly requested with username.
    Args: username (str): The user's login name.
    Returns: str: Confirmation or error message.
    """
    print(f"--- FUNCTION CALL: reset_password(username='{username}') ---")
    if not username or not isinstance(username, str) or len(username.strip()) < 3:
        print("--- FUNCTION ERROR: Invalid or missing username. ---")
        return "Error: Could not initiate password reset. Username is missing or invalid."
    time.sleep(0.5)
    print(f"--- Simulating password reset action for: {username} ---")
    return f"Password reset process successfully initiated for username '{username}'. User should check recovery email/SMS for instructions."


def check_knowledge_base(search_query: str) -> str:
    """
    Searches a simulated knowledge base using keywords for common IT issues (VPN, email, printer, slow, password).
    Args: search_query (str): Description of the user's problem or keywords.
    Returns: str: Relevant KB article snippet or 'not found' message.
    """
    print(f"--- FUNCTION CALL: check_knowledge_base(query='{search_query[:50]}...') ---")
    if not search_query or not isinstance(search_query, str):
        print("--- FUNCTION ERROR: Invalid or missing search query. ---")
        return "Error: Could not search knowledge base. Search query is missing."

    query_lower = search_query.lower()
    knowledge = {
        "vpn": "KB: VPN Steps: 1.Check internet. 2.Restart VPN client. 3.Restart PC. 4.Verify server/creds. Escalate with errors if fail.",
        "email": "KB: Email Steps: 1.Check user/pass (case-sensitive). 2.Check status page. 3.Try webmail. 4.Use self-service reset if possible.",
        "printer": "KB: Printer Steps: 1.Check power/status screen. 2.Verify network connection. 3.Restart PC & printer. 4.Check paper/ink. Note model/location if escalating.",
        "password": "KB: For password resets, confirm username and use 'reset_password' function.",
        "slow": "KB: Slow PC Steps: 1.Restart PC. 2.Close unused apps. 3.Check Task Manager (Ctrl+Shift+Esc) for high CPU/Memory/Disk use. Note app names."
    }
    time.sleep(0.3)
    found_solution = "No specific KB article found matching query keywords."
    for keyword, solution in knowledge.items():
        if keyword in query_lower:
            found_solution = f"Found KB Article related to '{keyword}': {solution}"
            print(f"--- Knowledge Base found entry for '{keyword}' ---")
            break
    return found_solution

