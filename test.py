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

def main():
    # Clear previous output
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    users = []
    tokens = {}

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

    # --- 3. User1 sends friend request to User2 ---
    print(f"User {user1_username} sending friend request to {user2_username}...")
    friend_request_data = {"receiver_username": user2_username}
    friend_request_id = None
    try:
        response = requests.post(f"{BASE_URL}/friend-requests", json=friend_request_data, headers=headers1)
        if response.status_code == 201:
            friend_request_id = response.json()["id"]
            log_response(f"Send Friend Request ({user1_username} to {user2_username})", response, "Friend request sent.")
        else:
            log_response(f"Send Friend Request ({user1_username} to {user2_username})", response, "Failed to send friend request.")
            print(f"Failed to send friend request. Status: {response.status_code}. Response: {response.text}")
    except requests.exceptions.ConnectionError as e:
        log_response(f"Send Friend Request ({user1_username} to {user2_username})", None, f"Connection Error: {e}")
        print(f"Connection error sending friend request: {e}")
    except Exception as e:
        log_response(f"Send Friend Request ({user1_username} to {user2_username})", None, f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred sending friend request: {e}")

    # --- 4. User2 gets pending friend requests ---
    print(f"User {user2_username} getting pending friend requests...")
    try:
        response = requests.get(f"{BASE_URL}/friend-requests/pending", headers=headers2)
        log_response(f"Get Pending Friend Requests ({user2_username})", response, "Fetched pending friend requests.")
    except requests.exceptions.ConnectionError as e:
        log_response(f"Get Pending Friend Requests ({user2_username})", None, f"Connection Error: {e}")
        print(f"Connection error getting pending friend requests: {e}")
    except Exception as e:
        log_response(f"Get Pending Friend Requests ({user2_username})", None, f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred getting pending friend requests: {e}")

    # --- 5. User2 accepts friend request ---
    if friend_request_id:
        print(f"User {user2_username} accepting friend request {friend_request_id}...")
        try:
            response = requests.post(f"{BASE_URL}/friend-requests/{friend_request_id}/accept", headers=headers2)
            log_response(f"Accept Friend Request ({user2_username})", response, "Friend request accepted.")
        except requests.exceptions.ConnectionError as e:
            log_response(f"Accept Friend Request ({user2_username})", None, f"Connection Error: {e}")
            print(f"Connection error accepting friend request: {e}")
        except Exception as e:
            log_response(f"Accept Friend Request ({user2_username})", None, f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred accepting friend request: {e}")

    # --- 6. User1 gets notifications (should have one for accepted friend request) ---
    print(f"User {user1_username} getting notifications...")
    try:
        response = requests.get(f"{BASE_URL}/notifications", headers=headers1)
        log_response(f"Get Notifications ({user1_username})", response, "Fetched notifications.")
    except requests.exceptions.ConnectionError as e:
        log_response(f"Get Notifications ({user1_username})", None, f"Connection Error: {e}")
        print(f"Connection error getting notifications: {e}")
    except Exception as e:
        log_response(f"Get Notifications ({user1_username})", None, f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred getting notifications: {e}")

    # --- 7. User1 creates a circle ---
    print(f"User {user1_username} creating a circle...")
    circle_data = {"circle_name": "My Test Circle", "description": "A circle for testing"}
    circle_id = None
    try:
        response = requests.post(f"{BASE_URL}/circles", json=circle_data, headers=headers1)
        if response.status_code == 201:
            circle_id = response.json()["id"]
            log_response(f"Create Circle ({user1_username})", response, "Circle created successfully.")
        else:
            log_response(f"Create Circle ({user1_username})", response, "Failed to create circle.")
            print(f"Failed to create circle. Status: {response.status_code}. Response: {response.text}")
    except requests.exceptions.ConnectionError as e:
        log_response(f"Create Circle ({user1_username})", None, f"Connection Error: {e}")
        print(f"Connection error creating circle: {e}")
    except Exception as e:
        log_response(f"Create Circle ({user1_username})", None, f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred creating circle: {e}")

    # --- 8. User1 adds User2 to the circle ---
    if circle_id:
        print(f"User {user1_username} adding {user2_username} to circle {circle_id}...")
        add_member_data = {"circle_id": circle_id, "member_id": user2_id, "role": "member"}
        try:
            response = requests.post(f"{BASE_URL}/circles/{circle_id}/members", json=add_member_data, headers=headers1)
            log_response(f"Add Member to Circle ({user1_username} adds {user2_username})", response, "Member added to circle.")
        except requests.exceptions.ConnectionError as e:
            log_response(f"Add Member to Circle ({user1_username} adds {user2_username})", None, f"Connection Error: {e}")
            print(f"Connection error adding member to circle: {e}")
        except Exception as e:
            log_response(f"Add Member to Circle ({user1_username} adds {user2_username})", None, f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred adding member to circle: {e}")

    # --- 9. User1 sends SOS alert for the circle ---
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
            log_response(f"Send SOS Alert ({user1_username} for circle {circle_id})", response, "SOS alert sent.")
        except requests.exceptions.ConnectionError as e:
            log_response(f"Send SOS Alert ({user1_username} for circle {circle_id})", None, f"Connection Error: {e}")
            print(f"Connection error sending SOS alert: {e}")
        except Exception as e:
            log_response(f"Send SOS Alert ({user1_username} for circle {circle_id})", None, f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred sending SOS alert: {e}")

    # --- 10. User2 gets notifications (should have one for SOS alert) ---
    print(f"User {user2_username} getting notifications (after SOS)...")
    try:
        response = requests.get(f"{BASE_URL}/notifications", headers=headers2)
        log_response(f"Get Notifications ({user2_username} after SOS)", response, "Fetched notifications after SOS.")
    except requests.exceptions.ConnectionError as e:
        log_response(f"Get Notifications ({user2_username} after SOS)", None, f"Connection Error: {e}")
        print(f"Connection error getting notifications after SOS: {e}")
    except Exception as e:
        log_response(f"Get Notifications ({user2_username} after SOS)", None, f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred getting notifications after SOS: {e}")

    # --- 11. User1 logs out ---
    print(f"User {user1_username} logging out...")
    try:
        response = requests.post(f"{BASE_URL}/logout", headers=headers1)
        log_response(f"Logout User {user1_username}", response, "User logged out.")
    except requests.exceptions.ConnectionError as e:
        log_response(f"Logout User {user1_username}", None, f"Connection Error: {e}")
        print(f"Connection error logging out user {user1_username}: {e}")
    except Exception as e:
        log_response(f"Logout User {user1_username}", None, f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred logging out user {user1_username}: {e}")

    # --- 12. User2 logs out ---
    print(f"User {user2_username} logging out...")
    try:
        response = requests.post(f"{BASE_URL}/logout", headers=headers2)
        log_response(f"Logout User {user2_username}", response, "User logged out.")
    except requests.exceptions.ConnectionError as e:
        log_response(f"Logout User {user2_username}", None, f"Connection Error: {e}")
        print(f"Connection error logging out user {user2_username}: {e}")
    except Exception as e:
        log_response(f"Logout User {user2_username}", None, f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred logging out user {user2_username}: {e}")

    print(f"\nAll API responses logged to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
