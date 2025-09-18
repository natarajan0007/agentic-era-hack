import requests
import random

# --- Configuration ---
BASE_URL = "https://fastapi-backend-1050008974311.europe-west1.run.app/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
TICKETS_URL = f"{BASE_URL}/tickets/"
END_USER_EMAIL = "end.user@intellica.com"
PASSWORD = "securepassword123"
DEPARTMENT_ID = 1

# --- Helper Function ---
def get_auth_token(email, password):
    """Logs in a user and returns an auth token."""
    print(f"Attempting to log in as {email} to get auth token...")
    try:
        login_payload = {'username': email, 'password': password}
        token_response = requests.post(LOGIN_URL, data=login_payload)
        
        if token_response.status_code == 200:
            token = token_response.json()['access_token']
            print("  \u2713 SUCCESS: Got auth token.")
            return token
        else:
            print(f"  \u2717 ERROR: Login failed. Status: {token_response.status_code}, Response: {token_response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  \u2717 ERROR: An exception occurred while trying to log in: {e}")
        return None

# --- Ticket Data ---
TICKET_DATA = [
    {"title": "Cannot connect to the VPN", "description": "I'm trying to connect to the VPN from home, but it's giving me a connection error. I've tried restarting my computer."}, 
    {"title": "Printer is not working", "description": "The printer on the 3rd floor is not printing. I've sent a document to print, but nothing is coming out."}, 
    {"title": "Slow computer performance", "description": "My computer has been very slow for the past few days. It takes a long time to open applications."}, 
    {"title": "Email is not syncing on my phone", "description": "I'm not receiving new emails on my phone. I've tried to refresh the app, but it's not working."}, 
    {"title": "Request for new software installation", "description": "I need to have the new design software installed on my machine. The software is called 'Creative Suite'."}, 
    {"title": "Password reset for my account", "description": "I've forgotten my password and I'm locked out of my account. Can you please reset my password?"}, 
    {"title": "Cannot access the shared drive", "description": "I'm getting an 'access denied' error when I try to open the shared drive 'X:'. I need to access a file in the 'Projects' folder."}, 
    {"title": "Wi-Fi connection is unstable", "description": "The Wi-Fi connection in the main conference room is very unstable. It keeps disconnecting."}, 
    {"title": "Issue with my desk phone", "description": "My desk phone is not working. I can't make or receive calls."}, 
    {"title": "Request for a new monitor", "description": "My current monitor is flickering. I would like to request a new one."}, 
]

# --- Main Execution ---
def seed_tickets():
    """Creates a set of random IT tickets."""
    print("--- Starting Ticket Seeding Script ---")
    
    token = get_auth_token(END_USER_EMAIL, PASSWORD)
    
    if not token:
        print("\nERROR: Could not get auth token. Aborting ticket creation.")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    for i, ticket in enumerate(TICKET_DATA):
        print(f"\nCreating ticket {i+1}/10: {ticket['title']}")
        
        payload = {
            "title": ticket["title"],
            "description": ticket["description"],
            "category": random.choice(["INCIDENT", "REQUEST"]),
            "priority": random.choice(["LOW", "MEDIUM", "HIGH"]),
            "department_id": DEPARTMENT_ID,
        }
        
        try:
            # The endpoint expects form data, not JSON
            response = requests.post(TICKETS_URL, headers=headers, data=payload)
            
            if response.status_code == 201:
                ticket_data = response.json()
                print(f"  \u2713 SUCCESS: Ticket '{ticket_data['id']}' created.")
            else:
                print(f"  \u2717 ERROR: Failed to create ticket. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"  \u2717 ERROR: An exception occurred while creating ticket: {e}")

    print("\n--- Ticket Seeding Script Finished ---")

if __name__ == "__main__":
    seed_tickets()
