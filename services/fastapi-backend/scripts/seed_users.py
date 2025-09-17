import requests
import json

# --- Configuration ---
BASE_URL = "https://fastapi-backend-1050008974311.europe-west1.run.app/api/v1"
REGISTER_URL = f"{BASE_URL}/auth/register"
LOGIN_URL = f"{BASE_URL}/auth/login"
ME_URL = f"{BASE_URL}/auth/me"
PASSWORD = "securepassword123"
DEPARTMENT_ID = 1

# --- Helper Functions ---
def get_user_id_by_login(email, password):
    """Logs in a user and returns their ID."""
    print(f"  Attempting to log in as {email} to fetch ID...")
    try:
        # Get a token
        login_payload = {'username': email, 'password': password}
        token_response = requests.post(LOGIN_URL, data=login_payload)
        
        if token_response.status_code != 200:
            print(f"    ✗ ERROR: Login failed. Status: {token_response.status_code}, Response: {token_response.text}")
            return None
            
        token = token_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user details
        me_response = requests.get(ME_URL, headers=headers)
        if me_response.status_code == 200:
            user_id = me_response.json()['id']
            print(f"    ✓ SUCCESS: Fetched ID for existing user '{email}': {user_id}")
            return user_id
        else:
            print(f"    ✗ ERROR: Could not fetch user details. Status: {me_response.status_code}, Response: {me_response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"    ✗ ERROR: An exception occurred while trying to fetch user ID: {e}")
        return None

def create_or_get_user(payload):
    """Creates a user or, if they exist, fetches their ID."""
    email = payload['email']
    print(f"Attempting to create user: {payload['name']} ({email})")
    
    try:
        response = requests.post(REGISTER_URL, json=payload)
        
        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data['id']
            print(f"  ✓ SUCCESS: User '{user_data['name']}' created with ID: {user_id}")
            return user_id
        
        elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
            print(f"  ℹ️ INFO: User with email '{email}' already exists.")
            return get_user_id_by_login(email, payload["password"])
        
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
    
    # 1. Create or get manager-level users
    print("\nStep 1: Creating/getting Manager-level users...")
    ops_manager_payload = {
        "email": "ops.manager@intellica.com", "name": "Ops Manager", "password": PASSWORD,
        "role": "ops-manager", "department_id": DEPARTMENT_ID
    }
    ops_manager_id = create_or_get_user(ops_manager_payload)

    admin_payload = {
        "email": "admin.user@intellica.com", "name": "Admin User", "password": PASSWORD,
        "role": "admin", "department_id": DEPARTMENT_ID
    }
    admin_id = create_or_get_user(admin_payload)

    if not ops_manager_id or not admin_id:
        print("\nERROR: Could not create or fetch necessary manager roles. Aborting further user creation.")
        return

    # 2. Create engineers who report to the Ops Manager
    print("\nStep 2: Creating/getting Engineer-level users...")
    l1_engineer_payload = {
        "email": "l1.engineer@intellica.com", "name": "L1 Engineer", "password": PASSWORD,
        "role": "l1-engineer", "department_id": DEPARTMENT_ID, "manager_id": ops_manager_id
    }
    create_or_get_user(l1_engineer_payload)

    l2_engineer_payload = {
        "email": "l2.engineer@intellica.com", "name": "L2 Engineer", "password": PASSWORD,
        "role": "l2-engineer", "department_id": DEPARTMENT_ID, "manager_id": ops_manager_id
    }
    create_or_get_user(l2_engineer_payload)

    # 3. Create other roles
    print("\nStep 3: Creating/getting other roles...")
    transition_manager_payload = {
        "email": "transition.manager@intellica.com", "name": "Transition Manager", "password": PASSWORD,
        "role": "transition-manager", "department_id": DEPARTMENT_ID, "manager_id": admin_id
    }
    create_or_get_user(transition_manager_payload)

    end_user_payload = {
        "email": "end.user@intellica.com", "name": "End User", "password": PASSWORD,
        "role": "end-user", "department_id": DEPARTMENT_ID
    }
    create_or_get_user(end_user_payload)

    print("\n--- User Seeding Script Finished ---")

if __name__ == "__main__":
    seed_all_users()