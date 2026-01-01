# SafeTravel-Server

Backend API for the SafeTravel application, built with **FastAPI + SQLAlchemy + MySQL**.

## 🌐 Access URLs

### Local Development (không Docker)
| Service | URL |
|---------|-----|
| API Base URL | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

### Docker Deployment
| Service | URL | Mô tả |
|---------|-----|-------|
| API Base URL | `http://localhost:8001` | API chính |
| Swagger UI | `http://localhost:8001/docs` | Chỉ có ở mode development |
| MySQL | `localhost:3307` | Database (port 3307 để tránh conflict) |

> **Note:** Tất cả API routes đều có prefix `/api`. Ví dụ: `http://localhost:8001/api/login`

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
  - [Quick Start với Docker](#quick-start-với-docker)
  - [Development với Docker](#development-với-docker)
  - [Production Deployment](#production-deployment)
  - [Docker Commands](#docker-commands)
- [Environment Variables](#environment-variables)
- [Authentication (JWT Bearer)](#authentication-jwt-bearer)
- [API (Request/Response Examples)](#api-requestresponse-examples)
  - [Health](#health)
  - [Auth](#auth)
  - [Users](#users)
  - [Friends](#friends)
  - [Circles](#circles)
  - [SOS + User Reports](#sos--user-reports)
  - [Map Incidents Feed](#map-incidents-feed)
  - [News Incidents](#news-incidents)
  - [Trips](#trips)
  - [Notifications](#notifications)
  - [Admin Logs](#admin-logs)
  - [AI Report](#ai-report)
- [Project Docs](#project-docs)
- [Local Tools](#local-tools)
- [Notes / Gotchas](#notes--gotchas)
- [License](#license)

## Overview

Key modules:

- Auth: register/login JWT
- Friends: friend requests by username + accept/reject + list/remove friends
- Circles: safety circles (active/inactive) + manage members
- SOS: create SOS alerts, update status, list my alerts
- Map incidents: prioritized mixed feed (friends/circle SOS, nearby SOS, incident reports)
- News incidents: AI extraction + geocoding + query by radius
- Trips: CRUD trips
- Notifications / Admin Logs / AI: currently **partially unauthenticated** (see gotchas)

## Tech Stack

- FastAPI + Uvicorn
- SQLAlchemy 2.x
- MySQL (via `mysql-connector-python`)
- JWT auth (`python-jose`, `passlib`, `bcrypt`)
- AI / Geocoding:
  - Gemini (`google-genai`)
  - Geoapify (HTTP via `httpx`)

## Local Development

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn run:app --reload
```

When `ENVIRONMENT=development`, the app will attempt to:

- create the database (if the MySQL user has `CREATE DATABASE` permission)
- create tables from SQLAlchemy models on startup

## Docker Deployment

Dự án hỗ trợ deploy bằng Docker với 2 chế độ: **Development** và **Production**.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0+)

### Quick Start với Docker

1. **Clone repository và tạo file .env:**

```bash
git clone https://github.com/htham-eituc/SafeTravel-Server.git
cd SafeTravel-Server

# Copy file environment mẫu
cp .env.example .env
```

2. **Cập nhật các biến trong .env:**

```env
# MySQL Configuration
MYSQL_ROOT_PASSWORD=your_strong_root_password
MYSQL_DATABASE=safetravel
MYSQL_USER=safetravel_user
MYSQL_PASSWORD=your_strong_password

# Security - THAY ĐỔI TRONG PRODUCTION!
SECRET_KEY=your_super_secret_key_at_least_32_characters

# API Keys (bắt buộc)
GEMINI_API_KEY=your_gemini_api_key
GEOAPIFY_KEY=your_geoapify_api_key

# Environment
ENVIRONMENT=production
```

3. **Build và chạy containers:**

```bash
# Build và start tất cả services
docker-compose up -d --build

# Xem logs
docker-compose logs -f
```

4. **Truy cập API:**

| Service | URL |
|---------|-----|
| API Base URL | `http://localhost:8001` |
| Swagger UI | `http://localhost:8001/docs` (chỉ development mode) |
| MySQL | `localhost:3307` |

**Test API hoạt động:**
```bash
# Kiểm tra health
curl http://localhost:8001/

# Response:
# {"message":"Welcome to SafeTravel API!","status":"online","environment":"production"}
```

### Development với Docker

Sử dụng `docker-compose.dev.yml` để có **hot reload** khi code thay đổi:

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d --build

# Xem logs realtime
docker-compose -f docker-compose.dev.yml logs -f api

# Stop containers
docker-compose -f docker-compose.dev.yml down
```

**Tính năng Development mode:**
- ✅ Hot reload khi thay đổi code
- ✅ Debug logs
- ✅ Swagger UI enabled
- ✅ Source code được mount vào container

### Production Deployment

#### 1. Chuẩn bị server

```bash
# Cài đặt Docker và Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

#### 2. Clone và cấu hình

```bash
git clone https://github.com/htham-eituc/SafeTravel-Server.git
cd SafeTravel-Server

# Tạo .env với các giá trị production
cp .env.example .env
nano .env  # Chỉnh sửa các giá trị
```

**Lưu ý cấu hình Production:**

```env
# Bắt buộc đổi trong production
SECRET_KEY=generate_a_long_random_string_here
MYSQL_ROOT_PASSWORD=strong_root_password
MYSQL_PASSWORD=strong_user_password

# Set môi trường
ENVIRONMENT=production

# Optional: đổi port
API_PORT=8000
```

#### 3. Deploy

```bash
# Build và start (detached mode)
docker-compose up -d --build

# Kiểm tra status
docker-compose ps

# Xem logs
docker-compose logs -f
```

#### 4. Cấu hình Reverse Proxy (Nginx)

Tạo file `/etc/nginx/sites-available/safetravel`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/safetravel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# (Optional) Cài SSL với Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Docker Commands

| Lệnh | Mô tả |
|------|-------|
| `docker-compose up -d --build` | Build và start containers |
| `docker-compose down` | Stop và remove containers |
| `docker-compose down -v` | Stop, remove containers và volumes (⚠️ xóa data) |
| `docker-compose logs -f` | Xem logs realtime |
| `docker-compose logs -f api` | Xem logs của service api |
| `docker-compose ps` | Liệt kê containers đang chạy |
| `docker-compose exec api bash` | Truy cập shell trong container api |
| `docker-compose exec db mysql -u root -p` | Truy cập MySQL CLI |
| `docker-compose restart api` | Restart service api |
| `docker-compose pull` | Pull images mới nhất |

### Cấu trúc Docker Files

```
SafeTravel-Server/
├── Dockerfile              # Production Dockerfile
├── Dockerfile.dev          # Development Dockerfile (with hot reload)
├── docker-compose.yml      # Production compose
├── docker-compose.dev.yml  # Development compose
├── .dockerignore           # Files to exclude from Docker build
├── .env.example            # Environment variables template
└── init.sql                # MySQL initialization script
```

### Troubleshooting Docker

**1. Container không start được:**
```bash
# Xem logs chi tiết
docker-compose logs api

# Kiểm tra health của MySQL
docker-compose exec db mysqladmin ping -h localhost -u root -p
```

**2. Lỗi kết nối database:**
```bash
# Đảm bảo MySQL đã sẵn sàng
docker-compose logs db

# Test connection từ container api
docker-compose exec api python -c "from src.infrastructure.database.sql.database import engine; print(engine.connect())"
```

**3. Reset database:**
```bash
# Xóa volume và restart
docker-compose down -v
docker-compose up -d --build
```

**4. Rebuild sau khi thay đổi requirements.txt:**
```bash
docker-compose build --no-cache api
docker-compose up -d
```

## Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Minimal example:

```env
DATABASE_URL=mysql+mysqlconnector://root:@127.0.0.1/safetravel
SECRET_KEY=your_super_secret_key_here

# Settings currently expects these to exist (even if you don't call AI endpoints)
GEMINI_API_KEY=your_api_key_here
GEOAPIFY_KEY=your_geoapify_key_here

# Optional
ENVIRONMENT=development
GEMINI_MODEL=gemini-2.5-flash
LOG_LEVEL=INFO
```

## Authentication (JWT Bearer)

- Login issues a JWT: `POST /api/login`
- Send token to protected routes:

`Authorization: Bearer <access_token>`

Typical auth error:

```json
{ "detail": "Could not validate credentials" }
```

## API (Request/Response Examples)

General notes:

- JSON endpoints use `Content-Type: application/json`
- `POST /api/login` uses **form data**: `application/x-www-form-urlencoded`
- Some endpoints return `204 No Content` (no response body)
- Datetimes are ISO 8601 strings (`created_at`, `start_date`, ...)

### Health

#### `GET /`

- Auth: No
- Response `200`:

```json
{ "message": "Welcome to SafeTravel API!" }
```

### Auth

#### `POST /api/register`

- Auth: No
- Request body (`UserRegisterDTO`):

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

- Auth: No
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

- Auth: Yes
- Response `200` (`UserDTO`): same shape as register response

#### `POST /api/logout`

- Auth: Yes
- Request body: none
- Response `200`:

```json
{ "message": "Successfully logged out" }
```

### Users

#### `GET /api/users/{user_id}`

- Auth: Yes
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

- Auth: Yes (must be self)
- Response `204`: no body

### Friends

#### `POST /api/friend-requests`

- Auth: Yes
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

- Auth: Yes
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

- Auth: Yes
- Request body: none
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

- Auth: Yes
- Request body: none
- Response `200` (`FriendRequestResponse`): same shape as create, with `status: "rejected"`

#### `GET /api/friends`

- Auth: Yes
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

- Auth: Yes
- Response `204`: no body

### Circles

#### `POST /api/circles`

- Auth: Yes
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

Notes:

- Creating a new circle deactivates any existing `active` circles for that owner.
- The owner is automatically added as a circle member with `role: "owner"`.

#### `GET /api/circles`

- Auth: Yes
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

- Auth: Yes (owner-only)
- Response `200`: `CircleInDB`

#### `PUT /api/circles/{circle_id}`

- Auth: Yes (owner-only)
- Request body (`CircleUpdate`) (you may send a subset of fields):

```json
{
  "circle_name": "Updated Family Circle",
  "description": "Updated description",
  "status": "inactive"
}
```

- Response `200`: `CircleInDB`

#### `DELETE /api/circles/{circle_id}`

- Auth: Yes (owner-only)
- Response `204`: no body

#### `POST /api/circles/{circle_id}/members`

- Auth: Yes (owner-only)
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

- Auth: Yes (owner-only)
- Response `204`: no body

#### `GET /api/circles/{circle_id}/members`

- Auth: Yes (owner or member)
- Response `200`: `List[UserDTO]`

### SOS + User Reports

#### `POST /api/sos`

- Auth: Yes
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

Notes:

- `user_id` must match the authenticated user.
- `circle_id` is assigned server-side from the user's `active` circle (your input may be overwritten).

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

- Auth: Yes (must own the alert)
- Request body (`SOSAlertUpdate`) (usually only `status` is needed):

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

- Auth: Yes
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

Create a user-submitted on-map warning (stored as a `user_report_incident`).

- Auth: Yes
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

- Auth: Yes
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

Create an incident record (P2) that appears in the map feed.

- Auth: Yes
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

Extract negative safety-related incidents from news (Gemini + Google Search), geocode via Geoapify, then store in DB.

- Auth: Yes
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

- Auth: Yes
- Query params:
  - `latitude` (float, required)
  - `longitude` (float, required)
  - `radius` (float, optional, default `0.5`, `> 0`)
- Response `200` (`List[NewsIncidentInDB]`): same shape as extract response

### Trips

#### `POST /api/trips/`

- Auth: Yes
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

- Auth: Yes
- Response `200`: `TripDTO` (same shape as create response)

#### `PUT /api/trips/{trip_id}`

- Auth: Yes
- Request body: `TripBase` (same schema as create)
- Response `200`: `TripDTO`

#### `DELETE /api/trips/{trip_id}`

- Auth: Yes
- Response `204`: no body

#### `GET /api/users/{user_id}/trips`

- Auth: Yes
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

Note: notification CRUD endpoints are currently **partially unauthenticated** (see gotchas).

#### `POST /api/notifications`

- Auth: No
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

- Auth: Yes
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

- Auth: No
- Response `200`: `NotificationInDB`

#### `PUT /api/notifications/{notification_id}`

- Auth: No
- Request body (`NotificationUpdate`) (you may send a subset):

```json
{ "is_read": true }
```

- Response `200`: `NotificationInDB`

#### `DELETE /api/notifications/{notification_id}`

- Auth: No
- Response `204`: no body

### Admin Logs

Note: admin log endpoints are currently **unauthenticated** (see gotchas).

#### `POST /api/admin_logs`

- Auth: No
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

- Auth: No
- Response `200`: `AdminLogInDB` (same shape as create response)

#### `GET /api/admins/{admin_id}/admin_logs`

- Auth: No
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

- Auth: No
- Request body (`AdminLogUpdate`):

```json
{ "action": "UNBAN_USER", "target_id": 42 }
```

- Response `200`: `AdminLogInDB`

#### `DELETE /api/admin_logs/{admin_log_id}`

- Auth: No
- Response `204`: no body

### AI Report

Notes:

- AI endpoints are currently **unauthenticated**
- Require outbound network + valid keys (Gemini + Geoapify)

#### `POST /api/weather`

- Auth: No
- Request body:

```json
{ "lat": 10.7825, "long": 106.6935 }
```

- Response `200` (`VietnamReport`) (shortened):

```json
{
  "provinces": [
    {
      "province_name": "Ho Chi Minh City",
      "report_date": "2025-12-16",
      "weather_forecast": [
        { "date": "2025-12-16", "temperature": "24-31°C", "condition": "Cloudy" },
        { "date": "2025-12-17", "temperature": "24-31°C", "condition": "Showers" },
        { "date": "2025-12-18", "temperature": "24-30°C", "condition": "Cloudy" }
      ],
      "travel_advice": [
        { "category": "Transport", "advice": "..." },
        { "category": "Safety", "advice": "..." },
        { "category": "Clothing", "advice": "..." }
      ],
      "executive_summary": "...",
      "sources": ["https://..."],
      "score": 80
    }
  ]
}
```

#### `POST /api/weather_place`

- Auth: No
- Request body: none (parameter is a query string)
- Example: `POST /api/weather_place?province_name=Ho%20Chi%20Minh%20City`
- Response: `VietnamReport`

## Project Docs

- `docs/routes.md` — full route list + POST request bodies
- `docs/frontend_guide.md` — frontend/mobile integration guide
- `docs/architecture.md` — DDD / clean architecture overview
- `docs/Gemini.md` — Gemini client notes

## Local Tools

### Auto-post TP.HCM news as SOS (dev)

Dev-only script that pulls incident-like news for Ho Chi Minh City (Google News RSS), geocodes via Nominatim, then auto-creates a user/circle and posts many SOS alerts.

- File: `tools/fetch_hcm_news_incidents.py` (gitignored)
- Cache: `generated/geocode_cache.json` (gitignored)
- Requires internet (RSS + Nominatim)

```bash
# 1) Start server
uvicorn run:app --reload

# 2) In another terminal
python3 tools/fetch_hcm_news_incidents.py --server http://127.0.0.1:8000 --count 50
```

## Notes / Gotchas

- CORS: `run.py` does not configure `CORSMiddleware`. If your frontend runs on a different origin, use a dev proxy or add CORS middleware.
- `radius` is not consistent across features:
  - SOS + News incidents use a degree-based bounding box (`lat/lon ± radius`)
  - Incident P2 uses a Haversine distance in kilometers
- Auth is not consistent yet:
  - Some endpoints are public (Notifications CRUD, Admin Logs, AI). Lock them down before production.
- No `LICENSE` file is currently included in this repository.

## License

No license is specified yet in this repository.

