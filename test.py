import requests
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000/api"
OUTPUT_FILE = "res.txt"

def log_response(endpoint, response, message=""):
    with open(OUTPUT_FILE, "a") as f:
        f.write(f"--- {endpoint} ---\n")
        if message:
            f.write(f"Message: {message}\n")
        if response:
            f.write(f"Status Code: {response.status_code}\n")
            try:
                f.write(f"Response JSON: {json.dumps(response.json(), indent=2)}\n")
            except json.JSONDecodeError:
                f.write(f"Response Text: {response.text}\n")
        else:
            f.write("No response received (connection error or unexpected issue).\n")
        f.write("\n")

def cleanup_data(tokens, users):
    print("Cleaning up test data...")
    with open(OUTPUT_FILE, "a") as f:
        f.write("\n--- CLEANUP --- \n")

    # Logout all users
    for username, token in tokens.items():
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(f"{BASE_URL}/logout", headers=headers)
            log_response(f"Cleanup: Logout User {username}", response)
        except requests.exceptions.ConnectionError as e:
            log_response(f"Cleanup: Logout User {username}", None, f"Connection Error: {e}")
        except Exception as e:
            log_response(f"Cleanup: Logout User {username}", None, f"An unexpected error occurred: {e}")

    # Delete users (this should cascade delete related data like circles, friends, notifications, sos alerts)
    # Iterate in reverse to avoid issues with IDs changing if not properly handled by cascade
    for user in reversed(users):
        user_id = user["id"]
        username = user["username"]
        
        # Re-login to get a fresh token for deletion if needed
        temp_token = None
        try:
            login_data = {"username": username, "password": "testpassword"}
            login_response = requests.post(f"{BASE_URL}/login", data=login_data)
            if login_response.status_code == 200:
                temp_token = login_response.json()["access_token"]
        except Exception as e:
            print(f"Could not re-login {username} for cleanup: {e}")

        if temp_token:
            headers = {"Authorization": f"Bearer {temp_token}"}
            try:
                response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
                log_response(f"Cleanup: Delete User {username} (ID: {user_id})", response)
            except requests.exceptions.ConnectionError as e:
                log_response(f"Cleanup: Delete User {username} (ID: {user_id})", None, f"Connection Error: {e}")
            except Exception as e:
                log_response(f"Cleanup: Delete User {username} (ID: {user_id})", None, f"An unexpected error occurred: {e}")
        else:
            print(f"Skipping deletion for user {username} (ID: {user_id}) due to missing token.")
            log_response(f"Cleanup: Delete User {username} (ID: {user_id})", None, "Skipped due to missing token.")


def main():
    # Clear previous output
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    users = []
    tokens = {}
    friend_request_id = None
    circle_id = None
    sos_alert_id = None
    notification_id = None
    admin_log_id = None

    # --- Cleanup previous data before starting new tests ---
    # This is a simplified cleanup. In a real app, you might truncate tables directly
    # or use a dedicated test database.
    # For now, we'll try to delete users if they exist from previous runs.
    # This requires logging in first, so it's a bit circular.
    # A better approach for full cleanup would be to drop/recreate the database.
    # Given the user's constraint "do not fix all bug like aldredy, just file 500 bug",
    # and previous issues with database deletion, I will rely on the `create_database_if_not_exists`
    # in `src/infrastructure/database/sql/database.py` to handle a fresh start on server restart.
    # The `test.py` will now focus on idempotent operations or creating new data.

    # --- 1. Register Users ---
    print("Registering users...")
    for i in range(1, 3):
        username = f"testuser{i}"
        email = f"test{i}@example.com"
        password = "testpassword"
        full_name = f"Test User {i}"

        register_data = {
            "username": username,
            "email": email,
            "phone": f"123456789{i}",
            "password": password,
            "full_name": full_name,
            "avatar_url": f"https://example.com/avatar{i}.jpg"
        }
        try:
            response = requests.post(f"{BASE_URL}/register", json=register_data)
            if response.status_code == 201:
                users.append(response.json())
                log_response(f"Register User {i}", response, "User registered successfully.")
            elif response.status_code == 400 and "Username already registered" in response.text:
                print(f"User {username} already registered. Attempting to log in instead.")
                log_response(f"Register User {i}", response, "User already registered.")
                # If user exists, try to get their info to add to 'users' list
                login_data = {"username": username, "password": password}
                login_response = requests.post(f"{BASE_URL}/login", data=login_data)
                if login_response.status_code == 200:
                    tokens[username] = login_response.json()["access_token"]
                    # Get user details to add to 'users' list
                    headers = {"Authorization": f"Bearer {tokens[username]}"}
                    user_me_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
                    if user_me_response.status_code == 200:
                        users.append(user_me_response.json())
                        log_response(f"Get User {username} (after existing registration)", user_me_response, "Fetched existing user details.")
                    else:
                        log_response(f"Get User {username} (after existing registration)", user_me_response, "Failed to fetch existing user details.")
                else:
                    log_response(f"Login User {username} (after existing registration)", login_response, "Failed to login existing user.")
            else:
                log_response(f"Register User {i}", response, "Failed to register user.")
                print(f"Failed to register user {i}. Status: {response.status_code}. Response: {response.text}")
        except requests.exceptions.ConnectionError as e:
            log_response(f"Register User {i}", None, f"Connection Error: {e}")
            print(f"Connection error during registration for user {i}. Is the server running? {e}")
            return
        except Exception as e:
            log_response(f"Register User {i}", None, f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred during registration for user {i}: {e}")
            return

    # Ensure we have at least two users for subsequent tests
    if len(users) < 2:
        print("Not enough users registered/logged in to proceed with tests. Exiting.")
        return

    # --- 2. Login Users (for those not already logged in) ---
    print("Logging in users...")
    for user in users:
        username = user["username"]
        if username not in tokens: # Only login if not already logged in during registration check
            password = "testpassword"
            login_data = {
                "username": username,
                "password": password
            }
            try:
                response = requests.post(f"{BASE_URL}/login", data=login_data)
                if response.status_code == 200:
                    tokens[username] = response.json()["access_token"]
                    log_response(f"Login User {username}", response, "User logged in successfully.")
                else:
                    log_response(f"Login User {username}", response, "Failed to login user.")
                    print(f"Failed to login user {username}. Status: {response.status_code}. Response: {response.text}")
                    return
            except requests.exceptions.ConnectionError as e:
                log_response(f"Login User {username}", None, f"Connection Error: {e}")
                print(f"Connection error during login for user {username}. Is the server running? {e}")
                return
            except Exception as e:
                log_response(f"Login User {username}", None, f"An unexpected error occurred: {e}")
                print(f"An unexpected error occurred during login for user {username}: {e}")
                return

    user1_id = users[0]["id"]
    user1_username = users[0]["username"]
    user1_token = tokens.get(user1_username)

    user2_id = users[1]["id"]
    user2_username = users[1]["username"]
    user2_token = tokens.get(user2_username)

    if not user1_token or not user2_token:
        print("Failed to get tokens for both users. Exiting.")
        return

    headers1 = {"Authorization": f"Bearer {user1_token}"}
    headers2 = {"Authorization": f"Bearer {user2_token}"}

    # --- 3. Get Current User Information (User1) ---
    print(f"Getting current user information for {user1_username}...")
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers1)
        log_response(f"Get Current User ({user1_username})", response, "Fetched current user details.")
    except Exception as e:
        log_response(f"Get Current User ({user1_username})", None, f"Error: {e}")

    # --- 4. Get User by ID (User2 by User1) ---
    print(f"Getting user {user2_username} by ID (as {user1_username})...")
    try:
        response = requests.get(f"{BASE_URL}/users/{user2_id}", headers=headers1)
        log_response(f"Get User by ID ({user2_username} by {user1_username})", response, "Fetched user by ID.")
    except Exception as e:
        log_response(f"Get User by ID ({user2_username} by {user1_username})", None, f"Error: {e}")

    # --- 5. User1 sends friend request to User2 ---
    print(f"User {user1_username} sending friend request to {user2_username}...")
    friend_request_data = {"receiver_username": user2_username}
    try:
        response = requests.post(f"{BASE_URL}/friend-requests", json=friend_request_data, headers=headers1)
        if response.status_code == 201:
            friend_request_id = response.json()["id"]
            log_response(f"Send Friend Request ({user1_username} to {user2_username})", response, "Friend request sent.")
        elif response.status_code == 400 and "already friends" in response.text:
            log_response(f"Send Friend Request ({user1_username} to {user2_username})", response, "Already friends, skipping request.")
            # If already friends, try to find an existing friend request to accept
            response_pending = requests.get(f"{BASE_URL}/friend-requests/pending", headers=headers2)
            if response_pending.status_code == 200 and response_pending.json():
                friend_request_id = response_pending.json()[0]["id"]
                log_response(f"Found existing pending request for {user2_username}", response_pending)
            else:
                # If no pending request, assume friendship already established and skip accept step
                print(f"No pending friend request found for {user2_username}. Assuming friendship already exists.")
        else:
            log_response(f"Send Friend Request ({user1_username} to {user2_username})", response, "Failed to send friend request.")
            print(f"Failed to send friend request. Status: {response.status_code}. Response: {response.text}")
    except requests.exceptions.ConnectionError as e:
        log_response(f"Send Friend Request ({user1_username} to {user2_username})", None, f"Connection Error: {e}")
        print(f"Connection error sending friend request: {e}")
    except Exception as e:
        log_response(f"Send Friend Request ({user1_username} to {user2_username})", None, f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred sending friend request: {e}")

    # --- 6. User2 gets pending friend requests ---
    print(f"User {user2_username} getting pending friend requests...")
    try:
        response = requests.get(f"{BASE_URL}/friend-requests/pending", headers=headers2)
        log_response(f"Get Pending Friend Requests ({user2_username})", response, "Fetched pending friend requests.")
    except Exception as e:
        log_response(f"Get Pending Friend Requests ({user2_username})", None, f"Error: {e}")

    # --- 7. User2 accepts friend request (if pending) ---
    if friend_request_id:
        print(f"User {user2_username} accepting friend request {friend_request_id}...")
        try:
            response = requests.post(f"{BASE_URL}/friend-requests/{friend_request_id}/accept", headers=headers2)
            log_response(f"Accept Friend Request ({user2_username})", response, "Friend request accepted.")
        except Exception as e:
            log_response(f"Accept Friend Request ({user2_username})", None, f"Error: {e}")
    else:
        print("No pending friend request to accept.")
        log_response(f"Accept Friend Request ({user2_username})", None, "No pending request to accept.")

    # --- 8. User1 gets friends ---
    print(f"User {user1_username} getting friends...")
    try:
        response = requests.get(f"{BASE_URL}/friends", headers=headers1)
        log_response(f"Get Friends ({user1_username})", response, "Fetched friends list.")
    except Exception as e:
        log_response(f"Get Friends ({user1_username})", None, f"Error: {e}")

    # --- 9. User1 creates a circle ---
    print(f"User {user1_username} creating a circle...")
    circle_data = {"circle_name": "My Test Circle", "description": "A circle for testing"}
    try:
        response = requests.post(f"{BASE_URL}/circles", json=circle_data, headers=headers1)
        if response.status_code == 201:
            circle_id = response.json()["id"]
            log_response(f"Create Circle ({user1_username})", response, "Circle created successfully.")
        else:
            log_response(f"Create Circle ({user1_username})", response, "Failed to create circle.")
            print(f"Failed to create circle. Status: {response.status_code}. Response: {response.text}")
    except Exception as e:
        log_response(f"Create Circle ({user1_username})", None, f"Error: {e}")

    # --- 10. User1 gets circles ---
    print(f"User {user1_username} getting circles...")
    try:
        response = requests.get(f"{BASE_URL}/circles", headers=headers1)
        log_response(f"Get Circles ({user1_username})", response, "Fetched circles list.")
    except Exception as e:
        log_response(f"Get Circles ({user1_username})", None, f"Error: {e}")

    # --- 11. User1 gets specific circle ---
    if circle_id:
        print(f"User {user1_username} getting specific circle {circle_id}...")
        try:
            response = requests.get(f"{BASE_URL}/circles/{circle_id}", headers=headers1)
            log_response(f"Get Specific Circle ({user1_username})", response, "Fetched specific circle.")
        except Exception as e:
            log_response(f"Get Specific Circle ({user1_username})", None, f"Error: {e}")

    # --- 12. User1 updates circle ---
    if circle_id:
        print(f"User {user1_username} updating circle {circle_id}...")
        update_circle_data = {"description": "Updated description for test circle"}
        try:
            response = requests.put(f"{BASE_URL}/circles/{circle_id}", json=update_circle_data, headers=headers1)
            log_response(f"Update Circle ({user1_username})", response, "Circle updated.")
        except Exception as e:
            log_response(f"Update Circle ({user1_username})", None, f"Error: {e}")

    # --- 13. User1 adds User2 to the circle ---
    if circle_id:
        print(f"User {user1_username} adding {user2_username} to circle {circle_id}...")
        add_member_data = {"circle_id": circle_id, "member_id": user2_id, "role": "member"}
        try:
            response = requests.post(f"{BASE_URL}/circles/{circle_id}/members", json=add_member_data, headers=headers1)
            log_response(f"Add Member to Circle ({user1_username} adds {user2_username})", response, "Member added to circle.")
        except Exception as e:
            log_response(f"Add Member to Circle ({user1_username} adds {user2_username})", None, f"Error: {e}")

    # --- 14. User1 gets circle members ---
    if circle_id:
        print(f"User {user1_username} getting circle members for circle {circle_id}...")
        try:
            response = requests.get(f"{BASE_URL}/circles/{circle_id}/members", headers=headers1)
            log_response(f"Get Circle Members ({user1_username})", response, "Fetched circle members.")
        except Exception as e:
            log_response(f"Get Circle Members ({user1_username})", None, f"Error: {e}")

    # --- 15. User1 sends SOS alert for the circle ---
    if circle_id:
        print(f"User {user1_username} sending SOS alert for circle {circle_id}...")
        sos_data = {
            "user_id": user1_id,
            "message": "Emergency in test circle!",
            "latitude": 10.0,
            "longitude": 20.0
        }
        try:
            response = requests.post(f"{BASE_URL}/sos", json=sos_data, headers=headers1)
            if response.status_code == 201:
                sos_alert_id = response.json()["id"]
                log_response(f"Send SOS Alert ({user1_username} for circle {circle_id})", response, "SOS alert sent.")
            else:
                log_response(f"Send SOS Alert ({user1_username} for circle {circle_id})", response, "Failed to send SOS alert.")
                print(f"Failed to send SOS alert. Status: {response.status_code}. Response: {response.text}")
        except Exception as e:
            log_response(f"Send SOS Alert ({user1_username} for circle {circle_id})", None, f"Error: {e}")

    # --- 16. User2 gets notifications (should have one for SOS alert) ---
    print(f"User {user2_username} getting notifications (after SOS)...")
    try:
        response = requests.get(f"{BASE_URL}/notifications", headers=headers2)
        log_response(f"Get Notifications ({user2_username} after SOS)", response, "Fetched notifications after SOS.")
        if response.status_code == 200 and response.json():
            notification_id = response.json()[0]["id"]
    except Exception as e:
        log_response(f"Get Notifications ({user2_username} after SOS)", None, f"Error: {e}")

    # --- 17. User1 updates SOS alert status ---
    if sos_alert_id:
        print(f"User {user1_username} updating SOS alert {sos_alert_id} status...")
        update_sos_data = {"status": "resolved"}
        try:
            response = requests.post(f"{BASE_URL}/sos/{sos_alert_id}/status", json=update_sos_data, headers=headers1)
            log_response(f"Update SOS Alert Status ({user1_username})", response, "SOS alert status updated.")
        except Exception as e:
            log_response(f"Update SOS Alert Status ({user1_username})", None, f"Error: {e}")

    # --- 18. User1 gets my SOS alerts ---
    print(f"User {user1_username} getting my SOS alerts...")
    try:
        response = requests.get(f"{BASE_URL}/sos/my_alerts", headers=headers1)
        log_response(f"Get My SOS Alerts ({user1_username})", response, "Fetched my SOS alerts.")
    except Exception as e:
        log_response(f"Get My SOS Alerts ({user1_username})", None, f"Error: {e}")

    # --- 19. User1 creates an admin log (requires admin privileges, will likely fail) ---
    print(f"User {user1_username} creating an admin log (expected to fail without admin privileges)...")
    admin_log_data = {"admin_id": user1_id, "action": "Attempted to create admin log", "target_id": user2_id}
    try:
        response = requests.post(f"{BASE_URL}/admin_logs", json=admin_log_data, headers=headers1)
        if response.status_code == 201:
            admin_log_id = response.json()["id"]
            log_response(f"Create Admin Log ({user1_username})", response, "Admin log created (unexpected success).")
        else:
            log_response(f"Create Admin Log ({user1_username})", response, "Failed to create admin log (expected).")
    except Exception as e:
        log_response(f"Create Admin Log ({user1_username})", None, f"Error: {e}")

    # --- 20. User1 gets notifications by ID (if any) ---
    if notification_id:
        print(f"User {user1_username} getting notification {notification_id} by ID...")
        try:
            response = requests.get(f"{BASE_URL}/notifications/{notification_id}", headers=headers1)
            log_response(f"Get Notification by ID ({user1_username})", response, "Fetched notification by ID.")
        except Exception as e:
            log_response(f"Get Notification by ID ({user1_username})", None, f"Error: {e}")

    # --- 21. User1 updates notification (if any) ---
    if notification_id:
        print(f"User {user1_username} updating notification {notification_id}...")
        update_notification_data = {"is_read": True}
        try:
            response = requests.put(f"{BASE_URL}/notifications/{notification_id}", json=update_notification_data, headers=headers1)
            log_response(f"Update Notification ({user1_username})", response, "Notification updated.")
        except Exception as e:
            log_response(f"Update Notification ({user1_username})", None, f"Error: {e}")

    # --- 22. User1 deletes notification (if any) ---
    if notification_id:
        print(f"User {user1_username} deleting notification {notification_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/notifications/{notification_id}", headers=headers1)
            log_response(f"Delete Notification ({user1_username})", response, "Notification deleted.")
        except Exception as e:
            log_response(f"Delete Notification ({user1_username})", None, f"Error: {e}")

    # --- 23. User1 deletes User2 from circle ---
    if circle_id:
        print(f"User {user1_username} removing {user2_username} from circle {circle_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/circles/{circle_id}/members/{user2_id}", headers=headers1)
            log_response(f"Remove Member from Circle ({user1_username} removes {user2_username})", response, "Member removed from circle.")
        except Exception as e:
            log_response(f"Remove Member from Circle ({user1_username} removes {user2_username})", None, f"Error: {e}")

    # --- 24. User1 deletes circle ---
    if circle_id:
        print(f"User {user1_username} deleting circle {circle_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/circles/{circle_id}", headers=headers1)
            log_response(f"Delete Circle ({user1_username})", response, "Circle deleted.")
        except Exception as e:
            log_response(f"Delete Circle ({user1_username})", None, f"Error: {e}")

    # --- 25. User1 deletes friendship with User2 ---
    print(f"User {user1_username} deleting friendship with {user2_username}...")
    try:
        response = requests.delete(f"{BASE_URL}/friends/{user2_id}", headers=headers1)
        log_response(f"Delete Friendship ({user1_username} deletes {user2_username})", response, "Friendship deleted.")
    except Exception as e:
        log_response(f"Delete Friendship ({user1_username} deletes {user2_username})", None, f"Error: {e}")

    # --- 26. User1 rejects friend request (if any pending from previous runs) ---
    # This might be tricky if the request was already accepted.
    # For a clean test, it's better to ensure no pending requests exist before running.
    # Assuming previous tests might leave pending requests, we'll try to reject.
    if friend_request_id:
        print(f"User {user2_username} rejecting friend request {friend_request_id}...")
        try:
            response = requests.post(f"{BASE_URL}/friend-requests/{friend_request_id}/reject", headers=headers2)
            log_response(f"Reject Friend Request ({user2_username})", response, "Friend request rejected.")
        except Exception as e:
            log_response(f"Reject Friend Request ({user2_username})", None, f"Error: {e}")

    # --- 27. User1 logs out ---
    print(f"User {user1_username} logging out...")
    try:
        response = requests.post(f"{BASE_URL}/logout", headers=headers1)
        log_response(f"Logout User {user1_username}", response, "User logged out.")
    except Exception as e:
        log_response(f"Logout User {user1_username}", None, f"Error: {e}")

    # --- 28. User2 logs out ---
    print(f"User {user2_username} logging out...")
    try:
        response = requests.post(f"{BASE_URL}/logout", headers=headers2)
        log_response(f"Logout User {user2_username}", response, "User logged out.")
    except Exception as e:
        log_response(f"Logout User {user2_username}", None, f"Error: {e}")

    # --- Final Cleanup (delete users) ---
    cleanup_data(tokens, users)

    print(f"\nAll API responses logged to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
