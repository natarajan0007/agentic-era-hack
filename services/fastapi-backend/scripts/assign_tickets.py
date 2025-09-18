#!/usr/bin/env python3
import requests
import random
import sys
import logging
from typing import Optional, Dict, List

# --- Configuration ---
# BASE_URL = "https://fastapi-backend-1050008974311.europe-west1.run.app/api/v1"
BASE_URL = "http://localhost:9090/api/v1"

LOGIN_URL = f"{BASE_URL}/auth/login"
TICKETS_URL = f"{BASE_URL}/tickets/"
ME_URL = f"{BASE_URL}/auth/me"
ADMIN_EMAIL = "admin.user@intellica.com"
L1_ENGINEER_EMAIL = "l1.engineer@intellica.com"
L2_ENGINEER_EMAIL = "l2.engineer@intellica.com"
PASSWORD = "securepassword123"  # Consider using environment variables or a secrets manager

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Constants ---
STATUS_OPEN = "OPEN"
STATUS_IN_PROGRESS = "IN_PROGRESS"
LIMIT = 100

# --- Helper Functions ---
def get_auth_token(email: str, password: str) -> Optional[str]:
    """Logs in a user and returns an auth token."""
    logger.info(f"Attempting to log in as {email} to get auth token...")
    try:
        login_payload = {'username': email, 'password': password}
        token_response = requests.post(LOGIN_URL, data=login_payload)
        token_response.raise_for_status()
        token = token_response.json()['access_token']
        logger.info(f"  ✓ SUCCESS: Got auth token for {email}.")
        return token
    except requests.exceptions.RequestException as e:
        logger.error(
            f"  ✗ ERROR: Login failed for {email}. "
            f"Status: {e.response.status_code if e.response else 'N/A'}, "
            f"Response: {e.response.text if e.response else 'N/A'}"
        )
        return None

def get_user_id_from_token(token: str, email: str) -> Optional[int]:
    """Gets a user's ID using their token."""
    logger.info(f"Attempting to get user ID for {email}...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(ME_URL, headers=headers)
        response.raise_for_status()
        user_id = response.json()['id']
        logger.info(f"  ✓ SUCCESS: Got user ID for {email}: {user_id}")
        return user_id
    except requests.exceptions.RequestException as e:
        logger.error(
            f"  ✗ ERROR: Could not get user details for {email}. "
            f"Status: {e.response.status_code if e.response else 'N/A'}, "
            f"Response: {e.response.text if e.response else 'N/A'}"
        )
        return None

def get_open_tickets(token: str) -> List[Dict]:
    """Gets all open tickets."""
    logger.info("Attempting to get all open tickets...")
    headers = {"Authorization": f"Bearer {token}"}
    params = {"status": STATUS_OPEN, "limit": LIMIT}
    try:
        response = requests.get(TICKETS_URL, headers=headers, params=params)
        response.raise_for_status()
        tickets = response.json().get('tickets', [])
        logger.info(f"  ✓ SUCCESS: Found {len(tickets)} open tickets.")
        return tickets
    except requests.exceptions.RequestException as e:
        logger.error(
            f"  ✗ ERROR: Failed to get open tickets. "
            f"Status: {e.response.status_code if e.response else 'N/A'}, "
            f"Response: {e.response.text if e.response else 'N/A'}"
        )
        return []

def assign_ticket(token: str, ticket_id: int, assignee_id: int) -> bool:
    """Assigns a ticket to a user and sets status to IN_PROGRESS."""
    logger.info(f"  Assigning ticket {ticket_id} to user {assignee_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"assigned_to_id": assignee_id, "status": STATUS_IN_PROGRESS}
    try:
        response = requests.put(f"{TICKETS_URL}{ticket_id}", headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"    ✓ SUCCESS: Assigned ticket {ticket_id} to user {assignee_id}.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(
            f"    ✗ ERROR: Failed to assign ticket. "
            f"Status: {e.response.status_code if e.response else 'N/A'}, "
            f"Response: {e.response.text if e.response else 'N/A'}"
        )
        return False

# --- Main Execution ---
def assign_open_tickets() -> None:
    """Assigns all open tickets to L1 and L2 engineers."""
    logger.info("--- Starting Ticket Assignment Script ---")

    admin_token = get_auth_token(ADMIN_EMAIL, PASSWORD)
    if not admin_token:
        logger.error("ERROR: Could not get admin auth token. Aborting.")
        sys.exit(1)

    l1_token = get_auth_token(L1_ENGINEER_EMAIL, PASSWORD)
    l2_token = get_auth_token(L2_ENGINEER_EMAIL, PASSWORD)
    if not l1_token or not l2_token:
        logger.error("ERROR: Could not get engineer auth tokens. Aborting.")
        sys.exit(1)

    l1_engineer_id = get_user_id_from_token(l1_token, L1_ENGINEER_EMAIL)
    l2_engineer_id = get_user_id_from_token(l2_token, L2_ENGINEER_EMAIL)
    if not l1_engineer_id or not l2_engineer_id:
        logger.error("ERROR: Could not get engineer user IDs. Aborting.")
        sys.exit(1)

    open_tickets = get_open_tickets(admin_token)
    if not open_tickets:
        logger.info("No open tickets to assign.")
        logger.info("--- Ticket Assignment Script Finished ---")
        return

    logger.info(f"Found {len(open_tickets)} open tickets. Assigning them to L1 and L2 engineers...")

    l1_count = 0
    l2_count = 0
    for i, ticket in enumerate(open_tickets, 1):
        ticket_id = ticket['id']
        logger.info(f"Processing ticket {i}/{len(open_tickets)}: {ticket_id} - '{ticket['title']}'")

        assignee_id = l1_engineer_id if random.random() < 0.8 else l2_engineer_id
        if assign_ticket(admin_token, ticket_id, assignee_id):
            if assignee_id == l1_engineer_id:
                l1_count += 1
            else:
                l2_count += 1

    logger.info("--- Ticket Assignment Summary ---")
    logger.info(f"Successfully assigned {l1_count} tickets to L1 Engineer (ID: {l1_engineer_id})")
    logger.info(f"Successfully assigned {l2_count} tickets to L2 Engineer (ID: {l2_engineer_id})")
    logger.info("--- Ticket Assignment Script Finished ---")

if __name__ == "__main__":
    assign_open_tickets()
