# SafeTravel-Server

Backend API cho ứng dụng SafeTravel, xây dựng bằng **FastAPI + SQLAlchemy + MySQL**.

- Base URL (local): `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Tất cả API bên dưới dùng prefix: `/api` (xem `run.py`)

## Mục lục

- [Tổng quan](#tổng-quan)
- [Chạy local (dev)](#chạy-local-dev)
- [Cấu hình môi trường](#cấu-hình-môi-trường)
- [Xác thực (JWT Bearer)](#xác-thực-jwt-bearer)
- [API (Request/Response mẫu)](#api-requestresponse-mẫu)
  - [Health](#health)
  - [Auth](#auth)
  - [Users](#users)
  - [Friends](#friends)
  - [Circles](#circles)
  - [SOS + User Report](#sos--user-report)
  - [Map Incidents Feed](#map-incidents-feed)
  - [News Incidents](#news-incidents)
  - [Trips](#trips)
  - [Notifications](#notifications)
  - [Admin Logs](#admin-logs)
  - [AI Report](#ai-report)
- [Tài liệu bổ sung](#tài-liệu-bổ-sung)
- [Local tools](#local-tools)
- [Ghi chú & gotchas](#ghi-chú--gotchas)

## Tổng quan

Các module chính:

- Auth: đăng ký/đăng nhập JWT
- Friends: kết bạn theo username + duyệt yêu cầu
- Circles: nhóm an toàn (active/inactive) + quản lý thành viên
- SOS: gửi SOS theo vị trí, cập nhật trạng thái, lấy lịch sử
- Map incidents: feed tổng hợp ưu tiên (SOS bạn bè/vòng tròn, SOS gần đó, incident tự tạo)
- News incidents: trích xuất sự kiện tiêu cực từ tin tức (AI + geocoding) và truy vấn theo bán kính
- Trips: CRUD chuyến đi
- Notifications/Admin logs/AI: hiện tại **một phần chưa khóa auth** (xem phần gotchas)

## Chạy local (dev)

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn run:app --reload
```

Mặc định `ENVIRONMENT=development` (nếu bạn set trong `.env`) thì app sẽ:

- thử tạo database (nếu MySQL user có quyền `CREATE DATABASE`)
- tạo tables theo SQLAlchemy models khi khởi động (xem `run.py` + `src/infrastructure/database/sql/database.py`)

## Cấu hình môi trường

Tạo `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Ví dụ `.env` tối thiểu:

```env
DATABASE_URL=mysql+mysqlconnector://root:@127.0.0.1/safetravel
SECRET_KEY=your_super_secret_key_here

# Hiện tại Settings bắt buộc có 2 key này (dù bạn có dùng AI hay không)
GEMINI_API_KEY=your_api_key_here
GEOAPIFY_KEY=your_geoapify_key_here

# Optional
ENVIRONMENT=development
GEMINI_MODEL=gemini-2.5-flash
LOG_LEVEL=INFO
```

## Xác thực (JWT Bearer)

- Login trả về token JWT: `POST /api/login`
- Gửi token vào header cho các endpoint yêu cầu đăng nhập:

`Authorization: Bearer <access_token>`

Lỗi auth thường có format:

```json
{ "detail": "Could not validate credentials" }
```

## API (Request/Response mẫu)

Ghi chú chung:

- `Content-Type` mặc định với JSON: `application/json`
- `POST /api/login` dùng **form**: `application/x-www-form-urlencoded`
- Thời gian (`created_at`, `start_date`, …) trả về dạng ISO 8601 string
- Một số endpoint trả `204 No Content` (không có body)

### Health

#### `GET /`

- Auth: Không
- Response `200`:

```json
{ "message": "Welcome to SafeTravel API!" }
```

### Auth

#### `POST /api/register`

- Auth: Không
- Request body:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "phone": "1234567890",
  "avatar_url": "https://example.com/avatar.png",
  "full_name": "Test User",
  "password": "StrongPass123"
}
```

- Response `201` (`UserDTO`):

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "phone": "1234567890",
  "avatar_url": "https://example.com/avatar.png",
  "full_name": "Test User",
  "id": 1,
  "created_at": "2025-12-16T12:00:00.000000"
}
```

#### `POST /api/login`

- Auth: Không
- Content-Type: `application/x-www-form-urlencoded`
- Body:

```
username=testuser&password=StrongPass123
```

- Response `200` (`AuthTokenDTO`):

```json
{
  "access_token": "YOUR_JWT_ACCESS_TOKEN",
  "token_type": "bearer"
}
```

#### `GET /api/users/me`

- Auth: Có
- Response `200` (`UserDTO`): như `register`

#### `POST /api/logout`

- Auth: Có
- Request body: không có
- Response `200`:

```json
{ "message": "Successfully logged out" }
```

### Users

#### `GET /api/users/{user_id}`

- Auth: Có
- Response `200` (`UserDTO`):

```json
{
  "username": "anotheruser",
  "email": "another@example.com",
  "phone": null,
  "avatar_url": null,
  "full_name": "Another User",
  "id": 2,
  "created_at": "2025-12-16T12:05:00.000000"
}
```

#### `DELETE /api/users/{user_id}`

- Auth: Có (chỉ được xóa chính mình)
- Response `204`: không có body

### Friends

#### `POST /api/friend-requests`

- Auth: Có
- Request body (`FriendRequestCreate`):

```json
{ "receiver_username": "friend_username" }
```

- Response `201` (`FriendRequestResponse`):

```json
{
  "id": 10,
  "sender_id": 1,
  "receiver_id": 2,
  "status": "pending",
  "created_at": "2025-12-16T12:10:00.000000",
  "updated_at": "2025-12-16T12:10:00.000000"
}
```

#### `GET /api/friend-requests/pending`

- Auth: Có
- Response `200`:

```json
[
  {
    "id": 10,
    "sender_id": 1,
    "receiver_id": 2,
    "status": "pending",
    "created_at": "2025-12-16T12:10:00.000000",
    "updated_at": "2025-12-16T12:10:00.000000"
  }
]
```

#### `POST /api/friend-requests/{request_id}/accept`

- Auth: Có
- Request body: không có
- Response `200` (`FriendshipResponse`):

```json
{
  "id": 20,
  "user_id": 2,
  "friend_id": 1,
  "created_at": "2025-12-16T12:15:00.000000"
}
```

#### `POST /api/friend-requests/{request_id}/reject`

- Auth: Có
- Request body: không có
- Response `200` (`FriendRequestResponse`): `status` sẽ là `rejected`

#### `GET /api/friends`

- Auth: Có
- Response `200` (`List[UserDTO]`):

```json
[
  {
    "username": "friend_username",
    "email": "friend@example.com",
    "phone": null,
    "avatar_url": null,
    "full_name": "Friend User",
    "id": 2,
    "created_at": "2025-12-16T12:05:00.000000"
  }
]
```

#### `DELETE /api/friends/{friend_id}`

- Auth: Có
- Response `204`: không có body

### Circles

#### `POST /api/circles`

- Auth: Có
- Request body (`CircleCreate`):

```json
{
  "circle_name": "Family Circle",
  "description": "My family members",
  "status": "active"
}
```

- Response `201` (`CircleInDB`):

```json
{
  "circle_name": "Family Circle",
  "description": "My family members",
  "status": "active",
  "id": 1,
  "created_at": "2025-12-16T12:20:00.000000"
}
```

Ghi chú:

- Khi tạo circle mới, server sẽ set các circle đang `active` của user thành `inactive`
- User tạo circle được auto add vào circle với `role="owner"`

#### `GET /api/circles`

- Auth: Có
- Response `200` (`List[CircleInDB]`):

```json
[
  {
    "circle_name": "Family Circle",
    "description": "My family members",
    "status": "active",
    "id": 1,
    "created_at": "2025-12-16T12:20:00.000000"
  },
  {
    "circle_name": "Old Circle",
    "description": null,
    "status": "inactive",
    "id": 2,
    "created_at": "2025-12-10T09:00:00.000000"
  }
]
```

#### `GET /api/circles/{circle_id}`

- Auth: Có (owner-only)
- Response `200` (`CircleInDB`)

#### `PUT /api/circles/{circle_id}`

- Auth: Có (owner-only)
- Request body (`CircleUpdate`) (bạn có thể gửi subset fields):

```json
{
  "circle_name": "Updated Family Circle",
  "description": "Updated description",
  "status": "inactive"
}
```

- Response `200` (`CircleInDB`)

#### `DELETE /api/circles/{circle_id}`

- Auth: Có (owner-only)
- Response `204`: không có body

#### `POST /api/circles/{circle_id}/members`

- Auth: Có (owner-only)
- Request body (`CircleMemberCreate`):

```json
{
  "circle_id": 1,
  "member_id": 2,
  "role": "member"
}
```

- Response `201` (`CircleMemberInDB`):

```json
{
  "circle_id": 1,
  "member_id": 2,
  "role": "member",
  "id": 5
}
```

#### `DELETE /api/circles/{circle_id}/members/{member_id}`

- Auth: Có (owner-only)
- Response `204`: không có body

#### `GET /api/circles/{circle_id}/members`

- Auth: Có (owner hoặc member)
- Response `200` (`List[UserDTO]`)

### SOS + User Report

#### `POST /api/sos`

- Auth: Có
- Request body (`SOSAlertCreate`):

```json
{
  "user_id": 1,
  "circle_id": null,
  "message": "I need help!",
  "latitude": 10.7825,
  "longitude": 106.6935,
  "status": "pending"
}
```

Ghi chú:

- `user_id` **phải** là user đang đăng nhập
- `circle_id` sẽ được server tự set theo circle `active` của user (giá trị bạn gửi có thể bị overwrite)

- Response `201` (`SOSAlertInDB`):

```json
{
  "user_id": 1,
  "circle_id": 1,
  "message": "I need help!",
  "latitude": 10.7825,
  "longitude": 106.6935,
  "status": "pending",
  "id": 100,
  "created_at": "2025-12-16T12:30:00.000000",
  "resolved_at": null
}
```

#### `POST /api/sos/{alert_id}/status`

- Auth: Có (phải là owner của alert)
- Request body (`SOSAlertUpdate`) (thực tế thường chỉ cần `status`):

```json
{ "status": "resolved" }
```

- Response `200` (`SOSAlertInDB`):

```json
{
  "user_id": 1,
  "circle_id": 1,
  "message": "I need help!",
  "latitude": 10.7825,
  "longitude": 106.6935,
  "status": "resolved",
  "id": 100,
  "created_at": "2025-12-16T12:30:00.000000",
  "resolved_at": "2025-12-16T12:40:00.000000"
}
```

#### `GET /api/sos/my_alerts`

- Auth: Có
- Response `200` (`List[SOSAlertInDB]`):

```json
[
  {
    "user_id": 1,
    "circle_id": 1,
    "message": "I need help!",
    "latitude": 10.7825,
    "longitude": 106.6935,
    "status": "resolved",
    "id": 100,
    "created_at": "2025-12-16T12:30:00.000000",
    "resolved_at": "2025-12-16T12:40:00.000000"
  }
]
```

#### `POST /api/incidents/report`

User báo cáo cảnh báo trên bản đồ (P1 user_report_incident).

- Auth: Có
- Request body (`UserReportIncidentCreate`):

```json
{
  "title": "Suspicious area",
  "description": "Be careful with your belongings",
  "category": "crime",
  "latitude": 10.7825,
  "longitude": 106.6935,
  "severity": 60
}
```

- Response `201` (`UserReportIncidentInDB`):

```json
{
  "id": 1,
  "reporter_id": 1,
  "title": "Suspicious area",
  "description": "Be careful with your belongings",
  "category": "crime",
  "latitude": 10.7825,
  "longitude": 106.6935,
  "severity": 60,
  "status": "active",
  "created_at": "2025-12-16T12:35:00.000000"
}
```

### Map Incidents Feed

#### `GET /api/incidents`

- Auth: Có
- Query params:
  - `latitude` (float, required)
  - `longitude` (float, required)
  - `radius` (float, required, `> 0`)

- Response `200` (`GetIncidentsResponseDTO`):

```json
{
  "items": [
    {
      "priority": 0,
      "item": {
        "id": 100,
        "user_id": 2,
        "latitude": 10.78,
        "longitude": 106.69,
        "message": "Help!",
        "created_at": "2025-12-16T12:20:00.000000",
        "user": { "id": 2, "username": "friend_username", "full_name": "Friend User" }
      }
    },
    {
      "priority": 2,
      "item": {
        "id": 55,
        "title": "Road blocked",
        "description": "Construction is blocking the street",
        "category": "accident",
        "latitude": 10.7825,
        "longitude": 106.6935,
        "severity": 40,
        "created_at": "2025-12-16T12:10:00.000000"
      }
    }
  ]
}
```

#### `POST /api/incidents`

Tạo incident (P2) cho feed bản đồ.

- Auth: Có
- Request body (`IncidentCreateDTO`):

```json
{
  "title": "Road blocked",
  "description": "Construction is blocking the street",
  "category": "accident",
  "latitude": 10.7825,
  "longitude": 106.6935,
  "severity": 40
}
```

- Response `201` (`IncidentDTO`):

```json
{
  "id": 55,
  "title": "Road blocked",
  "description": "Construction is blocking the street",
  "category": "accident",
  "latitude": 10.7825,
  "longitude": 106.6935,
  "severity": 40,
  "created_at": "2025-12-16T12:10:00.000000"
}
```

### News Incidents

#### `POST /api/news-incidents/extract`

Trích xuất incidents tiêu cực từ tin tức (Gemini + Google Search) + geocode qua Geoapify, sau đó lưu DB.

- Auth: Có
- Request body (`NewsIncidentExtractRequest`):

```json
{
  "query": "Vietnam",
  "days": 3,
  "max_items": 20
}
```

- Response `201` (`List[NewsIncidentInDB]`):

```json
[
  {
    "title": "Flooding causes travel disruption",
    "summary": "Road closures reported in multiple districts...",
    "category": "disaster",
    "location_name": "Da Nang, Vietnam",
    "latitude": 16.0544,
    "longitude": 108.2022,
    "source_url": "https://example.com/news/...",
    "published_at": "2025-12-12T00:00:00.000000",
    "severity": 75,
    "id": 1,
    "created_at": "2025-12-16T12:45:00.000000",
    "updated_at": "2025-12-16T12:45:00.000000"
  }
]
```

#### `GET /api/news-incidents`

- Auth: Có
- Query params:
  - `latitude` (float, required)
  - `longitude` (float, required)
  - `radius` (float, optional, default `0.5`, `> 0`)
- Response `200` (`List[NewsIncidentInDB]`):

```json
[
  {
    "title": "Flooding causes travel disruption",
    "summary": "Road closures reported in multiple districts...",
    "category": "disaster",
    "location_name": "Da Nang, Vietnam",
    "latitude": 16.0544,
    "longitude": 108.2022,
    "source_url": "https://example.com/news/...",
    "published_at": "2025-12-12T00:00:00.000000",
    "severity": 75,
    "id": 1,
    "created_at": "2025-12-16T12:45:00.000000",
    "updated_at": "2025-12-16T12:45:00.000000"
  }
]
```

### Trips

#### `POST /api/trips/`

- Auth: Có
- Request body (`TripBase`):

```json
{
  "user_id": 1,
  "tripname": "Holiday trip",
  "destination": "Da Nang",
  "start_date": "2025-12-20T09:00:00Z",
  "end_date": "2025-12-25T18:00:00Z",
  "notes": "Bring raincoat",
  "trip_type": "family",
  "have_elderly": false,
  "have_children": false
}
```

- Response `201` (`TripDTO`):

```json
{
  "user_id": 1,
  "tripname": "Holiday trip",
  "destination": "Da Nang",
  "start_date": "2025-12-20T09:00:00Z",
  "end_date": "2025-12-25T18:00:00Z",
  "notes": "Bring raincoat",
  "trip_type": "family",
  "have_elderly": false,
  "have_children": false,
  "id": 1,
  "created_at": "2025-12-16T12:50:00.000000"
}
```

#### `GET /api/trips/{trip_id}`

- Auth: Có
- Response `200` (`TripDTO`): như response của `POST /api/trips/`

#### `PUT /api/trips/{trip_id}`

- Auth: Có
- Request body: `TripBase` (đang dùng cùng schema với create)
- Response `200`: `TripDTO`

#### `DELETE /api/trips/{trip_id}`

- Auth: Có
- Response `204`: không có body

#### `GET /api/users/{user_id}/trips`

- Auth: Có
- Response `200` (`List[TripDTO]`):

```json
[
  {
    "user_id": 1,
    "tripname": "Holiday trip",
    "destination": "Da Nang",
    "start_date": "2025-12-20T09:00:00Z",
    "end_date": "2025-12-25T18:00:00Z",
    "notes": "Bring raincoat",
    "trip_type": "family",
    "have_elderly": false,
    "have_children": false,
    "id": 1,
    "created_at": "2025-12-16T12:50:00.000000"
  }
]
```

### Notifications

Lưu ý: CRUD notifications hiện tại có endpoint **chưa khóa auth** (xem gotchas).

#### `POST /api/notifications`

- Auth: Không
- Request body (`NotificationCreate`):

```json
{
  "user_id": 1,
  "title": "SOS Alert from Friend",
  "message": "Your friend alice has sent an SOS alert!",
  "type": "SOS_FRIEND",
  "is_read": false
}
```

- Response `201` (`NotificationInDB`):

```json
{
  "user_id": 1,
  "title": "SOS Alert from Friend",
  "message": "Your friend alice has sent an SOS alert!",
  "type": "SOS_FRIEND",
  "is_read": false,
  "id": 1,
  "created_at": "2025-12-16T12:55:00.000000"
}
```

#### `GET /api/notifications`

- Auth: Có
- Response `200` (`List[NotificationInDB]`):

```json
[
  {
    "user_id": 1,
    "title": "SOS Alert from Friend",
    "message": "Your friend alice has sent an SOS alert!",
    "type": "SOS_FRIEND",
    "is_read": false,
    "id": 1,
    "created_at": "2025-12-16T12:55:00.000000"
  }
]
```

#### `GET /api/notifications/{notification_id}`

- Auth: Không
- Response `200`: `NotificationInDB`

#### `PUT /api/notifications/{notification_id}`

- Auth: Không
- Request body (`NotificationUpdate`) (có thể gửi subset fields):

```json
{ "is_read": true }
```

- Response `200`: `NotificationInDB`

#### `DELETE /api/notifications/{notification_id}`

- Auth: Không
- Response `204`: không có body

### Admin Logs

Lưu ý: admin logs hiện tại **chưa khóa auth** (xem gotchas).

#### `POST /api/admin_logs`

- Auth: Không
- Request body (`AdminLogCreate`):

```json
{
  "admin_id": 1,
  "action": "BAN_USER",
  "target_id": 42
}
```

- Response `201` (`AdminLogInDB`):

```json
{
  "admin_id": 1,
  "action": "BAN_USER",
  "target_id": 42,
  "id": 1,
  "created_at": "2025-12-16T13:00:00.000000"
}
```

#### `GET /api/admin_logs/{admin_log_id}`

- Auth: Không
- Response `200` (`AdminLogInDB`): như response của `POST /api/admin_logs`

#### `GET /api/admins/{admin_id}/admin_logs`

- Auth: Không
- Response `200` (`List[AdminLogInDB]`):

```json
[
  {
    "admin_id": 1,
    "action": "BAN_USER",
    "target_id": 42,
    "id": 1,
    "created_at": "2025-12-16T13:00:00.000000"
  }
]
```

#### `PUT /api/admin_logs/{admin_log_id}`

- Auth: Không
- Request body (`AdminLogUpdate`):

```json
{ "action": "UNBAN_USER", "target_id": 42 }
```

- Response `200`: `AdminLogInDB`

#### `DELETE /api/admin_logs/{admin_log_id}`

- Auth: Không
- Response `204`: không có body

### AI Report

Lưu ý:

- AI endpoints hiện tại **chưa khóa auth**
- Cần outbound network + key hợp lệ (Gemini + Geoapify)

#### `POST /api/weather`

- Auth: Không
- Request body:

```json
{ "lat": 10.7825, "long": 106.6935 }
```

- Response `200` (`VietnamReport`) (rút gọn):

```json
{
  "provinces": [
    {
      "province_name": "Ho Chi Minh City",
      "report_date": "2025-12-16",
      "weather_forecast": [
        { "date": "2025-12-16", "temperature": "24-31°C", "condition": "Có mây" },
        { "date": "2025-12-17", "temperature": "24-31°C", "condition": "Mưa rào" },
        { "date": "2025-12-18", "temperature": "24-30°C", "condition": "Có mây" }
      ],
      "travel_advice": [
        { "category": "Di chuyển", "advice": "..." },
        { "category": "An toàn", "advice": "..." },
        { "category": "Trang phục", "advice": "..." }
      ],
      "executive_summary": "...",
      "sources": ["https://..."],
      "score": 80
    }
  ]
}
```

#### `POST /api/weather_place`

- Auth: Không
- Request body: không có (tham số là query string)
- Response: `VietnamReport`

## Tài liệu bổ sung

- `docs/routes.md` — danh sách route đầy đủ + request body cho tất cả `POST`
- `docs/frontend_guide.md` — guide tích hợp cho frontend/mobile
- `docs/architecture.md` — DDD / clean architecture overview
- `docs/Gemini.md` — ghi chú về `GeminiClient`

## Local tools

### Auto-post TP.HCM news as SOS (dev)

Script dev để lấy tin “incident-like” cho TP.HCM (Google News RSS), geocode qua Nominatim, rồi tự tạo user/circle và bắn hàng loạt SOS.

- File: `tools/fetch_hcm_news_incidents.py` (bị ignore bởi git)
- Cache: `generated/geocode_cache.json` (bị ignore bởi git)
- Cần internet (RSS + Nominatim)

```bash
# 1) Start server
uvicorn run:app --reload

# 2) In another terminal
python3 tools/fetch_hcm_news_incidents.py --server http://127.0.0.1:8000 --count 50
```

## Ghi chú & gotchas

- **CORS**: `run.py` chưa cấu hình `CORSMiddleware`. Nếu frontend chạy khác origin, cần dev proxy hoặc thêm CORS ở backend.
- **radius không đồng nhất**:
  - SOS + News incidents: lọc theo bounding box `lat/lon ± radius` (không phải km/meters)
  - Incident P2 (`/api/incidents`): repository dùng Haversine (km)
- **Auth chưa đồng nhất**:
  - Một số endpoint hiện tại public (Notifications CRUD, Admin Logs, AI). Nếu deploy production nên khóa lại.
- **License**: repo hiện chưa có `LICENSE` file.
