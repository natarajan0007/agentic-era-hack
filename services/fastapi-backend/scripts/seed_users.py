
import requests
import json

# --- Configuration ---
BASE_URL = "http://localhost:8000/api/v1"
REGISTER_URL = f"{BASE_URL}/auth/register"
PASSWORD = "securepassword123"
DEPARTMENT_ID = 1

# --- Helper Function ---
def create_user(payload):
    """Sends a POST request to create a user and returns the new user's ID."""
    email = payload['email']
    print(f"Attempting to create user: {payload['name']} ({email})")
    
    try:
        response = requests.post(REGISTER_URL, json=payload)
        
        # Check for success
        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data['id']
            print(f"  ✓ SUCCESS: User '{user_data['name']}' created with ID: {user_id}")
            return user_id
        
        # Check if user already exists
        elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
            print(f"  ℹ️ INFO: User with email '{email}' already exists. Skipping.")
            # In a more complex script, you might want to fetch the existing user's ID here.
            return None
        
        # Handle other errors
        else:
            print(f"  ✗ ERROR: Failed to create user '{payload['name']}'. Status: {response.status_code}, Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"\n✗ FATAL: Could not connect to the API at {BASE_URL}.")
        print("Please ensure the backend server is running.")
        return None

# --- Main Execution ---
def seed_all_users():
    """Creates a suite of users with a defined reporting structure."""
    print("--- Starting User Seeding Script ---")
    
    # 1. Create users who will be managers to establish a hierarchy
    print("\nStep 1: Creating Manager-level users...")
    ops_manager_payload = {
        "email": "ops.manager@intellica.com", "name": "Ops Manager", "password": PASSWORD,
        "role": "ops-manager", "department_id": DEPARTMENT_ID
    }
    ops_manager_id = create_user(ops_manager_payload)

    admin_payload = {
        "email": "admin.user@intellica.com", "name": "Admin User", "password": PASSWORD,
        "role": "admin", "department_id": DEPARTMENT_ID
    }
    admin_id = create_user(admin_payload)

    # Exit if we couldn't create the managers we need for mapping
    if not ops_manager_id or not admin_id:
        print("\nERROR: Could not create necessary manager roles. Aborting further user creation.")
        print("This may be because they already exist. If so, the script needs to be modified to fetch their IDs.")
        return

    # 2. Create engineers who report to the Ops Manager
    print("\nStep 2: Creating Engineer-level users with manager mapping...")
    l1_engineer_payload = {
        "email": "l1.engineer@intellica.com", "name": "L1 Engineer", "password": PASSWORD,
        "role": "l1-engineer", "department_id": DEPARTMENT_ID, "manager_id": ops_manager_id
    }
    create_user(l1_engineer_payload)

    l2_engineer_payload = {
        "email": "l2.engineer@intellica.com", "name": "L2 Engineer", "password": PASSWORD,
        "role": "l2-engineer", "department_id": DEPARTMENT_ID, "manager_id": ops_manager_id
    }
    create_user(l2_engineer_payload)

    # 3. Create other roles
    print("\nStep 3: Creating other roles...")
    transition_manager_payload = {
        "email": "transition.manager@intellica.com", "name": "Transition Manager", "password": PASSWORD,
        "role": "transition-manager", "department_id": DEPARTMENT_ID, "manager_id": admin_id
    }
    create_user(transition_manager_payload)

    end_user_payload = {
        "email": "end.user@intellica.com", "name": "End User", "password": PASSWORD,
        "role": "end-user", "department_id": DEPARTMENT_ID
    }
    create_user(end_user_payload)

    print("\n--- User Seeding Script Finished ---")

if __name__ == "__main__":
    seed_all_users()
