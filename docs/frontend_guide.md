# Frontend Integration Guide (SafeTravel)

This guide is for frontend/mobile developers integrating with `SafeTravel-Server`.

## Base URLs

- Local dev API: `http://127.0.0.1:8000`
- Swagger (recommended): `http://127.0.0.1:8000/docs`
- All API endpoints are under the `/api` prefix.

## Auth (JWT Bearer)

### Register

- `POST /api/register` (JSON) → returns `UserDTO`

### Login (important: form-encoded)

- `POST /api/login`
- Content-Type: `application/x-www-form-urlencoded`
- Body fields: `username`, `password`
- Response: `{ "access_token": "...", "token_type": "bearer" }`

### Auth header for protected routes

Send on every protected request:

`Authorization: Bearer <access_token>`

To get the logged-in user:

- `GET /api/users/me`

Token expiry defaults to 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`).

## Common Conventions

- IDs are integers (`id`, `user_id`, `circle_id`, …).
- Datetimes are JSON strings (ISO 8601) for fields like `created_at`, `start_date`, `end_date`.
- Most endpoints return `400` for validation/business-rule errors and `401` for missing/invalid token.

## Recommended Frontend Flows

### 1) App start / session restore

1. Load stored token (secure storage).
2. Call `GET /api/users/me`.
   - If `401`, clear token and send user to login.

### 2) Friends

- Send request by username: `POST /api/friend-requests` with `{ "receiver_username": "..." }`
- Inbox: `GET /api/friend-requests/pending`
- Accept/reject: `POST /api/friend-requests/{id}/accept` or `/reject`
- Friends list: `GET /api/friends` (returns `UserDTO` list)

### 3) Circles

- Create: `POST /api/circles`
  - Server makes it the active circle and auto-adds the owner as `role="owner"`.
- List: `GET /api/circles`
- Members: `GET /api/circles/{circle_id}/members`
- Add/remove members:
  - `POST /api/circles/{circle_id}/members` with `{ "circle_id": <same>, "member_id": <userId>, "role": "member" }`
  - `DELETE /api/circles/{circle_id}/members/{member_id}`

### 4) SOS

- Send SOS: `POST /api/sos`
  - Body requires `user_id` (must be the current user), `latitude`, `longitude`, optional `message`.
  - Do not set `circle_id`; the server assigns the current active circle.
- My SOS history: `GET /api/sos/my_alerts`
- Resolve an SOS: `POST /api/sos/{alert_id}/status` with `{ "status": "resolved" }`

### 5) Map incidents feed

- `GET /api/incidents?latitude=...&longitude=...&radius=...`
  - Returns a single list with `priority` and `item` (union of SOS vs Incident).
  - `priority=0`: SOS from friends/circle members
  - `priority=1`: SOS from nearby users
  - `priority=2`: incidents created via `POST /api/incidents`

User-reported warnings (separate endpoint):

- `POST /api/incidents/report` (creates a `user_report_incident` record)

### 6) News incidents

- `POST /api/news-incidents/extract` triggers AI + geocoding and stores results (server must have `GEMINI_API_KEY` + `GEOAPIFY_KEY` and network access).
- `GET /api/news-incidents?latitude=...&longitude=...&radius=0.5` reads stored incidents.

### 7) Trips

- Create: `POST /api/trips/`
- List by user: `GET /api/users/{user_id}/trips`
- Get/update/delete: `GET|PUT|DELETE /api/trips/{trip_id}`

Front-end should always set `TripBase.user_id` to the current user id.

### 8) Notifications

- Fetch my notifications: `GET /api/notifications`
- Mark read: `PUT /api/notifications/{notification_id}` with `{ "is_read": true }`

## Dev Notes / Gotchas

- CORS middleware is not configured in `run.py`. If your frontend runs on a different origin, use a dev proxy (or ask backend to enable CORS).
- `radius` is not consistent across features:
  - SOS + News incidents use a degree-based bounding box (`lat/lon ± radius`)
  - Incidents (`/api/incidents` P2 items) use Haversine distance in kilometers
- Some endpoints are currently unauthenticated (Notifications CRUD, Admin Logs, AI). Treat them as internal; they may be locked down later.

## Minimal Axios Example

```ts
import axios from "axios";

export const api = axios.create({ baseURL: "http://127.0.0.1:8000" });

export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password });
  const res = await api.post("/api/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return res.data.access_token as string;
}

export function setToken(token: string) {
  api.defaults.headers.common.Authorization = `Bearer ${token}`;
}
```

