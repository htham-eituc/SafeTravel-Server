# SafeTravel API Routes

Base URL (local dev): `http://127.0.0.1:8000`

- Interactive docs: `GET /docs` (Swagger UI), `GET /redoc`
- All API routes below are prefixed with `/api` (see `run.py`).

## Authentication

- Login issues a JWT access token: `POST /api/login`
- Send the token on protected routes: `Authorization: Bearer <access_token>`
- Token expiry defaults to `ACCESS_TOKEN_EXPIRE_MINUTES=30` (see `src/config/settings.py`).

## Routes

### Health

- `GET /` — Public — Welcome message

### Auth (`src/presentation/auth_routes.py`)

- `POST /api/register` — Public — JSON `UserRegisterDTO` (`src/application/user/dto.py`) → `UserDTO`
- `POST /api/login` — Public — Form (`application/x-www-form-urlencoded`) `username`, `password` → `AuthTokenDTO`
- `GET /api/users/me` — Auth — → `UserDTO`
- `POST /api/logout` — Auth — → `{ "message": "Successfully logged out" }`

### Users (`src/presentation/user_routes.py`)

- `GET /api/users/{user_id}` — Auth — → `UserDTO`
- `DELETE /api/users/{user_id}` — Auth (must be self) — → `204 No Content`

### Friends (`src/presentation/friend_routes.py`)

- `POST /api/friend-requests` — Auth — JSON `FriendRequestCreate` (`src/application/friend/dto.py`) → `FriendRequestResponse`
- `GET /api/friend-requests/pending` — Auth — → `List[FriendRequestResponse]`
- `POST /api/friend-requests/{request_id}/accept` — Auth — → `FriendshipResponse`
- `POST /api/friend-requests/{request_id}/reject` — Auth — → `FriendRequestResponse`
- `GET /api/friends` — Auth — → `List[UserDTO]`
- `DELETE /api/friends/{friend_id}` — Auth — → `204 No Content`

### Circles (`src/presentation/circle_routes.py`)

- `POST /api/circles` — Auth — JSON `CircleCreate` (`src/application/circle/dto.py`) → `CircleInDB`
- `GET /api/circles` — Auth — → `List[CircleInDB]`
- `GET /api/circles/{circle_id}` — Auth (owner only) — → `CircleInDB`
- `PUT /api/circles/{circle_id}` — Auth (owner only) — JSON `CircleUpdate` → `CircleInDB`
- `DELETE /api/circles/{circle_id}` — Auth (owner only) — → `204 No Content`
- `POST /api/circles/{circle_id}/members` — Auth (owner only) — JSON `CircleMemberCreate` (`src/application/circle/member_dto.py`) → `CircleMemberInDB`
- `DELETE /api/circles/{circle_id}/members/{member_id}` — Auth (owner only) — → `204 No Content`
- `GET /api/circles/{circle_id}/members` — Auth (owner or member) — → `List[UserDTO]`

### SOS + User Reports (`src/presentation/sos_routes.py`)

- `POST /api/sos` — Auth — JSON `SOSAlertCreate` (`src/application/sos_alert/dto.py`) → `SOSAlertInDB`
  - Note: `circle_id` is set server-side (active circle); `user_id` must match the authenticated user.
- `POST /api/sos/{alert_id}/status` — Auth (must own alert) — JSON `SOSAlertUpdate` → `SOSAlertInDB`
- `GET /api/sos/my_alerts` — Auth — → `List[SOSAlertInDB]`
- `POST /api/incidents/report` — Auth — JSON `UserReportIncidentCreate` (`src/application/user_report_incident/dto.py`) → `UserReportIncidentInDB`

### Map Incidents Feed (`src/presentation/incident_routes.py`)

- `GET /api/incidents` — Auth — Query: `latitude`, `longitude`, `radius` → `GetIncidentsResponseDTO` (`src/application/incident/dto.py`)
- `POST /api/incidents` — Auth — JSON `IncidentCreateDTO` (`src/application/incident/dto.py`) → `IncidentDTO`

### News Incidents (`src/presentation/news_incident_routes.py`)

- `POST /api/news-incidents/extract` — Auth — JSON `NewsIncidentExtractRequest` (`src/application/news_incident/dto.py`) → `List[NewsIncidentInDB]`
  - Requires `GEMINI_API_KEY` + `GEOAPIFY_KEY` configured on the server and outbound network access.
- `GET /api/news-incidents` — Auth — Query: `latitude`, `longitude`, `radius` (default `0.5`) → `List[NewsIncidentInDB]`

### Trips (`src/presentation/trip_routes.py`)

- `POST /api/trips/` — Auth — JSON `TripBase` (`src/application/trip/dto.py`) → `TripDTO`
- `GET /api/trips/{trip_id}` — Auth — → `TripDTO`
- `PUT /api/trips/{trip_id}` — Auth — JSON `TripBase` → `TripDTO`
- `DELETE /api/trips/{trip_id}` — Auth — → `204 No Content`
- `GET /api/users/{user_id}/trips` — Auth — → `List[TripDTO]`

### Notifications (`src/presentation/notification_routes.py`)

- `POST /api/notifications` — Public — JSON `NotificationCreate` (`src/application/notification/dto.py`) → `NotificationInDB`
- `GET /api/notifications/{notification_id}` — Public — → `NotificationInDB`
- `GET /api/notifications` — Auth — → `List[NotificationInDB]` (for current user)
- `PUT /api/notifications/{notification_id}` — Public — JSON `NotificationUpdate` → `NotificationInDB`
- `DELETE /api/notifications/{notification_id}` — Public — → `204 No Content`

### Admin Logs (`src/presentation/admin_log_routes.py`)

- `POST /api/admin_logs` — Public — JSON `AdminLogCreate` (`src/application/admin_log/dto.py`) → `AdminLogInDB`
- `GET /api/admin_logs/{admin_log_id}` — Public — → `AdminLogInDB`
- `GET /api/admins/{admin_id}/admin_logs` — Public — → `List[AdminLogInDB]`
- `PUT /api/admin_logs/{admin_log_id}` — Public — JSON `AdminLogUpdate` → `AdminLogInDB`
- `DELETE /api/admin_logs/{admin_log_id}` — Public — → `204 No Content`

### AI Report (`src/presentation/ai_routes.py`)

- `POST /api/weather` — Public — JSON `{ "lat": number, "long": number }` → `VietnamReport`
- `POST /api/weather_place` — Public — Query: `province_name` → `VietnamReport`

## Notes / Gotchas

- `radius` is currently used inconsistently across features:
  - SOS + News incidents use a degree-based bounding box (`lat/lon ± radius`)
  - Incident reports (`/api/incidents` P2 items) use a Haversine distance in kilometers
- Some routes are currently unauthenticated (Notifications CRUD, Admin Logs, AI); treat them as internal until access control is added.

## POST Request Bodies

Below are copy/paste-friendly request bodies for every `POST` route.

### `POST /api/register` (JSON)

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

### `POST /api/login` (form-encoded)

Content-Type: `application/x-www-form-urlencoded`

```
username=testuser&password=StrongPass123
```

### `POST /api/logout`

- No request body

### `POST /api/friend-requests` (JSON)

```json
{
  "receiver_username": "friend_username"
}
```

### `POST /api/friend-requests/{request_id}/accept`

- No request body

### `POST /api/friend-requests/{request_id}/reject`

- No request body

### `POST /api/circles` (JSON)

```json
{
  "circle_name": "Family Circle",
  "description": "My family members",
  "status": "active"
}
```

### `POST /api/circles/{circle_id}/members` (JSON)

```json
{
  "circle_id": 1,
  "member_id": 2,
  "role": "member"
}
```

### `POST /api/sos` (JSON)

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
- `circle_id` is set/overwritten server-side (active circle).

### `POST /api/sos/{alert_id}/status` (JSON)

```json
{
  "status": "resolved"
}
```

### `POST /api/incidents/report` (JSON)

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

### `POST /api/incidents` (JSON)

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

### `POST /api/news-incidents/extract` (JSON)

```json
{
  "query": "Vietnam",
  "days": 3,
  "max_items": 20
}
```

### `POST /api/trips/` (JSON)

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

### `POST /api/notifications` (JSON)

```json
{
  "user_id": 1,
  "title": "SOS Alert from Friend",
  "message": "Your friend alice has sent an SOS alert!",
  "type": "SOS_FRIEND",
  "is_read": false
}
```

### `POST /api/admin_logs` (JSON)

```json
{
  "admin_id": 1,
  "action": "BAN_USER",
  "target_id": 42
}
```

### `POST /api/weather` (JSON)

```json
{
  "lat": 10.7825,
  "long": 106.6935
}
```

### `POST /api/weather_place`

- No JSON body (parameter is query string)
- Example: `POST /api/weather_place?province_name=Ho%20Chi%20Minh%20City`
