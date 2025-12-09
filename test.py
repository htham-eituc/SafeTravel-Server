import requests
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000/api"
OUTPUT_FILE = "res_trip_test.txt"

def log_response(endpoint, response, message=""):
    """Ghi log phản hồi từ API ra file và console."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        log_str = f"\n--- {endpoint} ---\n"
        if message:
            log_str += f"Message: {message}\n"
        
        if response is not None:
            log_str += f"Status Code: {response.status_code}\n"
            try:
                log_str += f"Response JSON: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n"
            except json.JSONDecodeError:
                log_str += f"Response Text: {response.text}\n"
        else:
            log_str += "No response received (connection error).\n"
        
        f.write(log_str)
        print(log_str) # In ra màn hình để dễ theo dõi

def main():
    # Xóa file log cũ nếu tồn tại
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    print(f"Starting Trip API tests. Logs will be saved to {OUTPUT_FILE}...\n")

    # Dữ liệu test
    username = "tripuser_test"
    password = "password123"
    email = "tripuser@example.com"
    
    token = None
    user_id = None
    trip_id = None

    # --- 1. ĐĂNG KÝ USER (REGISTER) ---
    print(">>> Step 1: Register User")
    register_data = {
        "username": username,
        "email": email,
        "phone": "0909000111",
        "password": password,
        "full_name": "Trip Tester",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/register", json=register_data)
        if res.status_code == 201:
            log_response("Register", res, "Đăng ký thành công.")
        elif res.status_code == 400 and "already registered" in res.text:
             log_response("Register", res, "User đã tồn tại, chuyển sang đăng nhập.")
        else:
            log_response("Register", res, "Đăng ký thất bại.")
            # Nếu đăng ký lỗi mà không phải do trùng user thì dừng
            if res.status_code != 400: return 
    except Exception as e:
        print(f"Error registering: {e}")
        return

    # --- 2. ĐĂNG NHẬP (LOGIN) ---
    print(">>> Step 2: Login User")
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        # FastAPI OAuth2PasswordRequestForm yêu cầu gửi form data, không phải json
        res = requests.post(f"{BASE_URL}/login", data=login_data)
        if res.status_code == 200:
            token = res.json().get("access_token")
            log_response("Login", res, "Đăng nhập thành công, đã lấy token.")
        else:
            log_response("Login", res, "Đăng nhập thất bại. Dừng test.")
            return
    except Exception as e:
        print(f"Error logging in: {e}")
        return

    # Header xác thực cho các request sau
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # --- 3. LẤY THÔNG TIN USER (GET ME) ---
    # Cần bước này để lấy user_id chính xác cho việc tạo trip
    print(">>> Step 3: Get User Info")
    try:
        res = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if res.status_code == 200:
            user_info = res.json()
            user_id = user_info["id"]
            log_response("Get Me", res, f"Lấy thông tin user thành công. ID: {user_id}")
        else:
            log_response("Get Me", res, "Không lấy được thông tin user.")
            return
    except Exception as e:
        print(f"Error getting user info: {e}")
        return

    # --- 4. TẠO CHUYẾN ĐI (CREATE TRIP) ---
    print(">>> Step 4: Create Trip")
    # Lưu ý: Dữ liệu này cần khớp với TripBase trong dto.py (đã sửa)
    trip_data = {
        "user_id": user_id,
        "tripname": "Du lịch Phú Quốc",
        "destination": "Phú Quốc, Kiên Giang",
        "start_date": "2023-12-20T08:00:00",
        "end_date": "2023-12-25T17:00:00",
        "notes": "Mang kem chống nắng, đồ bơi",
        "trip_type": "leisure",      # Trường mới thêm
        "have_elderly": False,       # Trường mới thêm
        "have_children": True        # Trường mới thêm
    }
    
    try:
        res = requests.post(f"{BASE_URL}/trips/", json=trip_data, headers=headers)
        if res.status_code == 201:
            created_trip = res.json()
            trip_id = created_trip["id"]
            log_response("Create Trip", res, f"Tạo chuyến đi thành công. ID: {trip_id}")
        else:
            log_response("Create Trip", res, "Tạo chuyến đi thất bại.")
            # Nếu tạo thất bại thì không thể test các bước sau
            return
    except Exception as e:
        print(f"Error creating trip: {e}")
        return

    # --- 5. LẤY DANH SÁCH CHUYẾN ĐI CỦA USER (GET USER TRIPS) ---
    print(">>> Step 5: Get All Trips for User")
    try:
        res = requests.get(f"{BASE_URL}/users/{user_id}/trips", headers=headers)
        log_response("Get User Trips", res, "Lấy danh sách chuyến đi thành công.")
    except Exception as e:
        print(f"Error getting user trips: {e}")

    # --- 6. LẤY CHI TIẾT CHUYẾN ĐI (GET TRIP BY ID) ---
    print(">>> Step 6: Get Specific Trip")
    if trip_id:
        try:
            res = requests.get(f"{BASE_URL}/trips/{trip_id}", headers=headers)
            log_response("Get Trip Detail", res, "Lấy chi tiết chuyến đi thành công.")
        except Exception as e:
            print(f"Error getting trip detail: {e}")

    # --- 7. CẬP NHẬT CHUYẾN ĐI (UPDATE TRIP) ---
    print(">>> Step 7: Update Trip")
    if trip_id:
        update_data = {
            "user_id": user_id,
            "tripname": "Du lịch Phú Quốc (Đã cập nhật)",
            "destination": "Phú Quốc, Kiên Giang",
            "start_date": "2023-12-21T09:00:00", # Dời ngày đi
            "end_date": "2023-12-26T18:00:00",
            "notes": "Đã đặt vé máy bay",
            "trip_type": "leisure",
            "have_elderly": True, # Thay đổi thông tin này
            "have_children": True
        }
        try:
            res = requests.put(f"{BASE_URL}/trips/{trip_id}", json=update_data, headers=headers)
            log_response("Update Trip", res, "Cập nhật chuyến đi thành công.")
        except Exception as e:
            print(f"Error updating trip: {e}")

    # --- 8. XÓA CHUYẾN ĐI (DELETE TRIP) ---
    print(">>> Step 8: Delete Trip")
    if trip_id:
        try:
            res = requests.delete(f"{BASE_URL}/trips/{trip_id}", headers=headers)
            if res.status_code == 204:
                # 204 No Content thường không có body, tự tạo message log
                with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n--- Delete Trip ---\nStatus Code: 204\nMessage: Xóa chuyến đi thành công.\n")
                print("\n--- Delete Trip ---\nStatus Code: 204\nMessage: Xóa chuyến đi thành công.")
            else:
                log_response("Delete Trip", res, "Xóa chuyến đi thất bại.")
        except Exception as e:
            print(f"Error deleting trip: {e}")

    # --- 9. ĐĂNG XUẤT (LOGOUT) ---
    print(">>> Step 9: Logout")
    try:
        res = requests.post(f"{BASE_URL}/logout", headers=headers)
        log_response("Logout", res, "Đăng xuất thành công.")
    except Exception as e:
        print(f"Error logging out: {e}")

    print(f"\nTest hoàn tất. Xem chi tiết tại file {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
