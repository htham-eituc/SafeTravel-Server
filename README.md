# SafeTravel-Server

This project provides the backend API for the SafeTravel application, built with FastAPI, SQLAlchemy, and MySQL. It offers robust functionalities for user management, safety circles, friend connections, location tracking, notifications, SOS alerts, and administrative logging.

## Table of Contents

- [SafeTravel-Server](#safetravel-server)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Technologies Used](#technologies-used)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Database Setup](#4-database-setup)
    - [5. Environment Variables](#5-environment-variables)
    - [6. Run the Application](#6-run-the-application)
  - [API Documentation and Testing](#api-documentation-and-testing)
  - [API Endpoints](#api-endpoints)
    - [Authentication Endpoints](#authentication-endpoints)
      - [Register User](#register-user)
      - [Login User](#login-user)
      - [Logout User (Authenticated)](#logout-user-authenticated)
      - [Get Current User Information](#get-current-user-information)
    - [User Management Endpoints](#user-management-endpoints)
      - [Get User by ID](#get-user-by-id)
      - [Delete User](#delete-user)
    - [Friend Management Endpoints](#friend-management-endpoints)
      - [Send Friend Request](#send-friend-request)
      - [Get Pending Friend Requests](#get-pending-friend-requests)
      - [Accept Friend Request](#accept-friend-request)
      - [Reject Friend Request](#reject-friend-request)
      - [Get User's Friends](#get-users-friends)
    - [Circle Endpoints](#circle-endpoints)
      - [Create Circle](#create-circle)
      - [Get Circles](#get-circles)
      - [Get Specific Circle](#get-specific-circle)
      - [Update Circle](#update-circle)
      - [Delete Circle](#delete-circle)
    - [Circle Member Endpoints](#circle-member-endpoints)
      - [Add Circle Member](#add-circle-member)
      - [Remove Circle Member](#remove-circle-member)
      - [Get Circle Members](#get-circle-members)
    - [SOS Alert Endpoints](#sos-alert-endpoints)
      - [Send SOS Alert](#send-sos-alert)
      - [Update SOS Alert Status](#update-sos-alert-status)
      - [Get My SOS Alerts](#get-my-sos-alerts)
    - [Map Incidents Endpoints](#map-incidents-endpoints)
      - [Get Map Incidents (P0/P1/P2)](#get-map-incidents-p0p1p2)
      - [Report Incident Warning (P1)](#report-incident-warning-p1)
    - [News Incident Endpoints](#news-incident-endpoints)
      - [Extract News Incidents (AI + Geocoding)](#extract-news-incidents-ai--geocoding)
      - [Get News Incidents by Radius](#get-news-incidents-by-radius)
    - [AI Endpoints](#ai-endpoints)
      - [Get Weather Report by Coordinates](#get-weather-report-by-coordinates)
      - [Get Weather Report by Place Name](#get-weather-report-by-place-name)
    - [Trip Endpoints](#trip-endpoints)
      - [Create Trip](#create-trip-1)
      - [Get Trip by ID](#get-trip-by-id-1)
      - [Get Trips by User](#get-trips-by-user)
      - [Update Trip](#update-trip-1)
      - [Delete Trip](#delete-trip-1)
    - [Notification Endpoints](#notification-endpoints)
      - [Create Notification](#create-notification)
      - [Get Notification by ID](#get-notification-by-id)
      - [Get Notifications by User](#get-notifications-by-user)
      - [Update Notification](#update-notification)
      - [Delete Notification](#delete-notification)
    - [Admin Log Endpoints](#admin-log-endpoints)
      - [Create Admin Log](#create-admin-log)
      - [Get Admin Log by ID](#get-admin-log-by-id)
      - [Get Admin Logs by Admin](#get-admin-logs-by-admin)
      - [Update Admin Log](#update-admin-log)
      - [Delete Admin Log](#delete-admin-log)
  - [Project Structure](#project-structure)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **User Management:** Secure user registration, authentication (JWT), and profile management.
- **Safety Circles:** Create and manage private circles for family and friends, with automatic owner assignment and status management.
- **Friend Connections:** Establish and manage friend relationships between users, including sending, accepting, and rejecting friend requests.
- **Location Tracking:** (Conceptual) Infrastructure for real-time location updates.
- **Notifications:** (Conceptual) System for sending alerts and updates.
- **SOS Alerts:** (Conceptual) Mechanism for users to send emergency alerts to their circles.
- **Map Incidents Feed:** Unified `GET /api/incidents` feed grouped into P0/P1/P2 for map rendering.
- **User-Reported Warnings:** Users can report on-map warnings via `POST /api/incidents/report` (P1).
- **News-Based Warnings:** Extract negative incidents from news sources, geocode them to lat/long, store and query by radius (P2).
- **Admin Logging:** (Conceptual) System for tracking administrative actions.
- **Google Gemini AI Integration:** For potential future AI-powered features.
- **Mock Database Test:** Automatically populates initial data for development and testing.

## Technologies Used

- **Backend Framework:** FastAPI
- **Database:** MySQL (via SQLAlchemy ORM)
- **Authentication:** JWT (JSON Web Tokens)
- **Dependency Management:** `pip` with `requirements.txt`
- **AI Integration:** Google Gemini API
- **Deployment:** Uvicorn ASGI server

## Prerequisites

Ensure you have the following installed on your system:

-   Python 3.8+
-   MySQL Server
-   `git` (for cloning the repository)

## Setup Instructions

Follow these steps to get the SafeTravel-Server up and running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/htham-eituc/SafeTravel-Server.git
cd SafeTravel-Server
```

### 2. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to isolate project dependencies.

```bash
python -m venv venv
```

Activate the virtual environment:

-   **Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
-   **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 3. Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Database Setup

This project uses MySQL.

1.  **Create a MySQL database:**
    Using your preferred MySQL client (e.g., MySQL Workbench, phpMyAdmin, or command line), create a new database named `safetravel`.

    ```sql
    CREATE DATABASE safetravel;
    ```

2.  **Database Schema:**
    The application will automatically create all necessary tables (`users`, `circles`, `circle_members`, `friend_requests`, `friendships`, `locations`, `notifications`, `sos_alerts`, `news_incidents`, `user_report_incidents`, `admin_logs`, `trips`) when it starts (development mode), based on the SQLAlchemy models.

    **Note on Schema Updates:** If you modify database models, you may need to drop existing tables to allow the application to recreate them with the updated schema. Always back up your data before performing such operations in a production environment.

### 5. Environment Variables

Create a `.env` file in the root directory of the project by copying the provided example:

```bash
cp .env.example .env
```

Open the newly created `.env` file and configure the following variables:

```
DATABASE_URL="mysql+mysqlconnector://root:@127.0.0.1/safetravel"
SECRET_KEY="your_super_secret_key"
GEMINI_API_KEY="your_api_key_here"
GEOAPIFY_KEY="your_geoapify_key_here"
```

-   **`DATABASE_URL`**: Update with your MySQL connection string if your credentials or host differ.
-   **`SECRET_KEY`**: **Crucially, replace `your_super_secret_key` with a strong, unique, and random key for production security.**
-   **`GEMINI_API_KEY`**: Provide your API key for Google Gemini services.
-   **`GEOAPIFY_KEY`**: Required for reverse geocoding and geocoding used by the AI/weather and news-incident modules.

### 6. Run the Application

Start the FastAPI application using Uvicorn:

```bash
python -m uvicorn run:app --reload
```

The server will typically run on `http://127.0.0.1:8000`. The `--reload` flag enables automatic server restarts on code changes, which is useful for development.

## API Documentation and Testing

Once the application is running, you can access the interactive API documentation (Swagger UI) at:

`http://127.0.0.1:8000/docs`

Or the ReDoc documentation at:

`http://127.0.0.1:8000/redoc`

These interfaces provide detailed information about all available endpoints, request/response schemas, and allow you to test the API directly from your browser.

## API Endpoints

This section provides examples for testing the API endpoints using Postman.

### Authentication Endpoints

#### Register User

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/register`
-   **Headers:**
    -   `Content-Type`: `application/json`
-   **Request Body (`UserRegisterDTO`):**
    ```json
    {
      "username": "testuser",
      "email": "test@example.com",
      "phone": "1234567890",
      "password": "testpassword",
      "full_name": "Test User",
      "avatar_url": "https://example.com/default_avatar.jpg"
    }
    ```
-   **Expected Response (`UserDTO`):** `201 Created`
    ```json
    {
      "username": "testuser",
      "email": "test@example.com",
      "phone": "1234567890",
      "avatar_url": "https://example.com/default_avatar.jpg",
      "full_name": "Test User",
      "id": 1,
      "created_at": "2023-10-27T10:00:00.000000"
    }
    ```

#### Login User

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/login`
-   **Headers:**
    -   `Content-Type`: `application/x-www-form-urlencoded`
-   **Request Body (`OAuth2PasswordRequestForm`):**
    -   `username`: `testuser`
    -   `password`: `testpassword`
-   **Expected Response (`AuthTokenDTO`):** `200 OK`
    ```json
    {
      "access_token": "your_jwt_access_token",
      "token_type": "bearer"
    }
    ```
    **Copy the `access_token` for authenticated requests.**

#### Logout User (Authenticated)

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/logout`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK`
    ```json
    {
      "message": "Successfully logged out"
    }
    ```

#### Get Current User Information

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/users/me`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (`UserDTO`):** `200 OK`
    ```json
    {
      "username": "testuser",
      "email": "test@example.com",
      "phone": "1234567890",
      "avatar_url": "https://example.com/default_avatar.jpg",
      "full_name": "Test User",
      "id": 1,
      "created_at": "2023-10-27T10:00:00.000000"
    }
    ```

### User Management Endpoints

All user endpoints require authentication.

#### Get User by ID

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/users/{user_id}` (Replace `{user_id}` with an actual user ID)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (`UserDTO`):** `200 OK`
    ```json
    {
      "username": "anotheruser",
      "email": "another@example.com",
      "phone": "0987654321",
      "avatar_url": null,
      "full_name": "Another User",
      "id": 2,
      "created_at": "2023-10-27T10:05:00.000000"
    }
    ```

#### Delete User

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/users/{user_id}` (Replace `{user_id}` with the ID of the user to delete)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the user to be deleted)
-   **Expected Response:** `204 No Content`.

### Friend Management Endpoints

All friend endpoints require authentication.

#### Send Friend Request

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/friend-requests`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the sender)
-   **Request Body (`FriendRequestCreate`):**
    ```json
    {
      "receiver_username": "friend_username"
    }
    ```
-   **Expected Response (`FriendRequestResponse`):** `201 Created`
    ```json
    {
      "id": 1,
      "sender_id": 1,
      "receiver_id": 2,
      "status": "pending",
      "created_at": "2023-10-27T10:10:00.000000",
      "updated_at": "2023-10-27T10:10:00.000000"
    }
    ```

#### Get Pending Friend Requests

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/friend-requests/pending`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the receiver)
-   **Expected Response (List of `FriendRequestResponse`):** `200 OK`
    ```json
    [
      {
        "id": 1,
        "sender_id": 1,
        "receiver_id": 2,
        "status": "pending",
        "created_at": "2023-10-27T10:10:00.000000",
        "updated_at": "2023-10-27T10:10:00.000000"
      }
    ]
    ```

#### Accept Friend Request

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/friend-requests/{request_id}/accept` (Replace `{request_id}` with the ID of the pending request)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the receiver)
-   **Expected Response (`FriendshipResponse`):** `200 OK`
    ```json
    {
      "id": 1,
      "user_id": 2,
      "friend_id": 1,
      "created_at": "2023-10-27T10:15:00.000000"
    }
    ```

#### Reject Friend Request

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/friend-requests/{request_id}/reject` (Replace `{request_id}` with the ID of the pending request)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the receiver)
-   **Expected Response (`FriendRequestResponse`):** `200 OK`
    ```json
    {
      "id": 1,
      "sender_id": 1,
      "receiver_id": 2,
      "status": "rejected",
      "created_at": "2023-10-27T10:10:00.000000",
      "updated_at": "2023-10-27T10:20:00.000000"
    }
    ```

#### Get User's Friends

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/friends`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (List of `UserDTO`):** `200 OK`
    ```json
    [
      {
        "username": "frienduser",
        "email": "friend@example.com",
        "phone": "1122334455",
        "avatar_url": null,
        "full_name": "Friend User",
        "id": 3,
        "created_at": "2023-10-27T10:07:00.000000"
      }
    ]
    ```

### Circle Endpoints

All circle endpoints require authentication.

#### Create Circle

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/circles`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`CircleCreate`):**
    ```json
    {
      "circle_name": "Family Circle",
      "description": "My family members"
    }
    ```
-   **Expected Response (`CircleInDB`):** `201 Created`
    ```json
    {
      "circle_name": "Family Circle",
      "description": "My family members",
      "status": "active",
      "id": 1,
      "created_at": "2023-10-27T10:25:00.000000"
    }
    ```
    **Note:** When a new circle is created, any existing active circles for the user will be set to `inactive`, and the creator will automatically be added as a member with the role "owner".

#### Get Circles

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/circles`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (List of `CircleInDB`):** `200 OK`
    ```json
    [
      {
        "circle_name": "Family Circle",
        "description": "My family members",
        "status": "active",
        "id": 1,
        "created_at": "2023-10-27T10:25:00.000000"
      }
    ]
    ```

#### Get Specific Circle

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}` (Replace `{circle_id}` with an actual circle ID)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (`CircleInDB`):** `200 OK`
    ```json
    {
      "circle_name": "Family Circle",
      "description": "My family members",
      "status": "active",
      "id": 1,
      "created_at": "2023-10-27T10:25:00.000000"
    }
    ```

#### Update Circle

-   **Method:** `PUT`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`CircleUpdate`):**
    ```json
    {
      "circle_name": "Updated Family Circle",
      "status": "inactive"
    }
    ```
-   **Expected Response (`CircleInDB`):** `200 OK`
    ```json
    {
      "circle_name": "Updated Family Circle",
      "description": "My family members",
      "status": "inactive",
      "id": 1,
      "created_at": "2023-10-27T10:25:00.000000"
    }
    ```

#### Delete Circle

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `204 No Content`.

### Circle Member Endpoints

All circle member endpoints require authentication.

#### Add Circle Member

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}/members` (Replace `{circle_id}` with the ID of the circle)
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the circle owner)
-   **Request Body (`CircleMemberCreate`):**
    ```json
    {
      "circle_id": 1,
      "member_id": 2,
      "role": "member"
    }
    ```
-   **Expected Response (`CircleMemberInDB`):** `201 Created`
    ```json
    {
      "circle_id": 1,
      "member_id": 2,
      "role": "member",
      "id": 1
    }
    ```

#### Remove Circle Member

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}/members/{member_id}` (Replace `{circle_id}` and `{member_id}` with actual IDs)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the circle owner)
-   **Expected Response:** `204 No Content`.

#### Get Circle Members

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}/members` (Replace `{circle_id}` with an actual circle ID)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (List of `UserDTO`):** `200 OK`
    ```json
    [
      {
        "username": "testuser",
        "email": "test@example.com",
        "phone": "1234567890",
        "avatar_url": "https://example.com/default_avatar.jpg",
        "full_name": "Test User",
        "id": 1,
        "created_at": "2023-10-27T10:00:00.000000"
      },
      {
        "username": "anotheruser",
        "email": "another@example.com",
        "phone": "0987654321",
        "avatar_url": null,
        "full_name": "Another User",
        "id": 2,
        "created_at": "2023-10-27T10:05:00.000000"
      }
    ]
    ```

### SOS Alert Endpoints

All SOS alert endpoints require authentication.

#### Send SOS Alert

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/sos`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`SOSAlertCreate`):**
    ```json
    {
      "user_id": 1,
      "message": "I need help!",
      "latitude": 34.052235,
      "longitude": -118.243683
    }
    ```
    **Note:** The `circle_id` will be automatically determined from the user's active circle.
-   **Expected Response (`SOSAlertInDB`):** `201 Created`
    ```json
    {
      "user_id": 1,
      "circle_id": 1,
      "message": "I need help!",
      "latitude": 34.052235,
      "longitude": -118.243683,
      "status": "pending",
      "id": 1,
      "created_at": "2023-10-27T10:30:00.000000",
      "resolved_at": null
    }
    ```

#### Update SOS Alert Status

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/sos/{alert_id}/status` (Replace `{alert_id}` with the ID of the SOS alert to update)
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`SOSAlertUpdate`):**
    ```json
    {
      "status": "resolved"
    }
    ```
-   **Expected Response (`SOSAlertInDB`):** `200 OK`
    ```json
    {
      "user_id": 1,
      "circle_id": 1,
      "message": "I need help!",
      "latitude": 34.052235,
      "longitude": -118.243683,
      "status": "resolved",
      "id": 1,
      "created_at": "2023-10-27T10:30:00.000000",
      "resolved_at": "2023-10-27T10:35:00.000000"
    }
    ```

#### Get My SOS Alerts

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/sos/my_alerts`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (List of `SOSAlertInDB`):** `200 OK`
    ```json
    [
      {
        "user_id": 1,
        "circle_id": 1,
        "message": "I need help!",
        "latitude": 34.052235,
        "longitude": -118.243683,
        "status": "resolved",
        "id": 1,
        "created_at": "2023-10-27T10:30:00.000000",
        "resolved_at": "2023-10-27T10:35:00.000000"
      }
    ]
    ```

### Map Incidents Endpoints

All map-incident endpoints require authentication.

#### Get Map Incidents (P0/P1/P2)

This endpoint is designed for map rendering: it returns incidents grouped by priority/source.

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/incidents?latitude=10.782&longitude=106.693&radius=0.5`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Query Params:**
    -   `latitude` (float, required)
    -   `longitude` (float, required)
    -   `radius` (float, optional, default `0.5`) — currently treated as a *degree-based bounding radius* (not meters)
-   **Response:** `200 OK`
    ```json
    {
      "p0_sos_friends": [
        {
          "alert": {
            "user_id": 2,
            "circle_id": 1,
            "message": "Help!",
            "latitude": 10.782,
            "longitude": 106.693,
            "status": "pending",
            "id": 10,
            "created_at": "2025-12-14T10:30:00.000000",
            "resolved_at": null
          },
          "user": {
            "id": 2,
            "username": "friend_user",
            "full_name": "Friend User",
            "avatar_url": null
          },
          "sources": ["friend"]
        }
      ],
      "p1_sos_nearby_strangers": [],
      "p1_user_reports": [],
      "p2_news_warnings": []
    }
    ```

**Meaning**
-   `p0_sos_friends`: SOS from friends/circle members (highest priority).
-   `p1_sos_nearby_strangers`: SOS from non-friends within radius.
-   `p1_user_reports`: user-submitted warnings within radius.
-   `p2_news_warnings`: negative incidents extracted from news sources and stored in DB.

#### Report Incident Warning (P1)

Users can report an on-map warning. It will appear in `p1_user_reports` when querying `GET /api/incidents`.

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/incidents/report`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body:**
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
-   **Expected Response:** `201 Created`
    ```json
    {
      "id": 1,
      "reporter_id": 7,
      "title": "Suspicious area",
      "description": "Be careful with your belongings",
      "category": "crime",
      "latitude": 10.7825,
      "longitude": 106.6935,
      "severity": 60,
      "status": "active",
      "created_at": "2025-12-14T10:40:00.000000"
    }
    ```

### News Incident Endpoints

All news-incident endpoints require authentication.

#### Extract News Incidents (AI + Geocoding)

Extracts negative incidents from news sources using Google Search grounding, converts locations to `lat/long` via Geoapify, then stores them in `news_incidents`.

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/news-incidents/extract`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Server Requirements:**
    -   `GEMINI_API_KEY` and `GEOAPIFY_KEY` set
    -   network access enabled on the server
-   **Request Body:**
    ```json
    {
      "query": "Vietnam",
      "days": 3,
      "max_items": 10
    }
    ```
-   **Expected Response:** `201 Created` (list)
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
        "created_at": "2025-12-14T10:45:00.000000",
        "updated_at": "2025-12-14T10:45:00.000000"
      }
    ]
    ```

#### Get News Incidents by Radius

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/news-incidents?latitude=10.782&longitude=106.693&radius=0.5`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` (list of stored news incidents)

### AI Endpoints

All AI endpoints require authentication.

#### Get Weather Report by Coordinates

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/weather`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body:**
    ```json
    {
      "lat": 10.782,
      "long": 106.693
    }
    ```
-   **Notes:**
    -   Coordinates must be within Vietnam (server-side validation).
    -   Requires `GEOAPIFY_KEY` + `GEMINI_API_KEY` and network access.

#### Get Weather Report by Place Name

This endpoint currently accepts `province_name` as a query parameter.

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/weather_place?province_name=Ho%20Chi%20Minh%20City`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`

### Trip Endpoints

All trip endpoints require authentication.

#### Create Trip

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/trips/`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`TripBase`):** See `src/application/trip/dto.py`
-   **Expected Response (`TripDTO`):** `201 Created`

#### Get Trip by ID

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/trips/{trip_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`

#### Get Trips by User

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/users/{user_id}/trips`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`

#### Update Trip

-   **Method:** `PUT`
-   **URL:** `http://127.0.0.1:8000/api/trips/{trip_id}`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`

#### Delete Trip

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/trips/{trip_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `204 No Content`

### Notification Endpoints

All notification endpoints require authentication.

#### Create Notification

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/notifications`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`NotificationCreate`):**
    ```json
    {
      "user_id": 1,
      "title": "Friend Request Accepted",
      "message": "Your friend 'anotheruser' accepted your request.",
      "type": "FRIEND_REQUEST_ACCEPTED",
      "is_read": false
    }
    ```
-   **Expected Response (`NotificationInDB`):** `201 Created`
    ```json
    {
      "user_id": 1,
      "title": "Friend Request Accepted",
      "message": "Your friend 'anotheruser' accepted your request.",
      "type": "FRIEND_REQUEST_ACCEPTED",
      "is_read": false,
      "id": 1,
      "created_at": "2023-10-27T10:40:00.000000"
    }
    ```

#### Get Notification by ID

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/notifications/{notification_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (`NotificationInDB`):** `200 OK`
    ```json
    {
      "user_id": 1,
      "title": "Friend Request Accepted",
      "message": "Your friend 'anotheruser' accepted your request.",
      "type": "FRIEND_REQUEST_ACCEPTED",
      "is_read": false,
      "id": 1,
      "created_at": "2023-10-27T10:40:00.000000"
    }
    ```

#### Get Notifications by User

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/notifications`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (List of `NotificationInDB`):** `200 OK`
    ```json
    [
      {
        "user_id": 1,
        "title": "Friend Request Accepted",
        "message": "Your friend 'anotheruser' accepted your request.",
        "type": "FRIEND_REQUEST_ACCEPTED",
        "is_read": false,
        "id": 1,
        "created_at": "2023-10-27T10:40:00.000000"
      }
    ]
    ```

#### Update Notification

-   **Method:** `PUT`
-   **URL:** `http://127.0.0.1:8000/api/notifications/{notification_id}`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`NotificationUpdate`):**
    ```json
    {
      "is_read": true
    }
    ```
-   **Expected Response (`NotificationInDB`):** `200 OK`
    ```json
    {
      "user_id": 1,
      "title": "Friend Request Accepted",
      "message": "Your friend 'anotheruser' accepted your request.",
      "type": "FRIEND_REQUEST_ACCEPTED",
      "is_read": true,
      "id": 1,
      "created_at": "2023-10-27T10:40:00.000000"
    }
    ```

#### Delete Notification

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/notifications/{notification_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `204 No Content`.

### Admin Log Endpoints

All admin log endpoints require authentication.

#### Create Admin Log

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/admin_logs`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`AdminLogCreate`):**
    ```json
    {
      "admin_id": 1,
      "action": "User 'testuser' banned for inappropriate content.",
      "target_id": 2
    }
    ```
-   **Expected Response (`AdminLogInDB`):** `201 Created`
    ```json
    {
      "admin_id": 1,
      "action": "User 'testuser' banned for inappropriate content.",
      "target_id": 2,
      "id": 1,
      "created_at": "2023-10-27T10:45:00.000000"
    }
    ```

#### Get Admin Log by ID

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/admin_logs/{admin_log_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (`AdminLogInDB`):** `200 OK`
    ```json
    {
      "admin_id": 1,
      "action": "User 'testuser' banned for inappropriate content.",
      "target_id": 2,
      "id": 1,
      "created_at": "2023-10-27T10:45:00.000000"
    }
    ```

#### Get Admin Logs by Admin

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/admins/{admin_id}/admin_logs`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response (List of `AdminLogInDB`):** `200 OK`
    ```json
    [
      {
        "admin_id": 1,
        "action": "User 'testuser' banned for inappropriate content.",
        "target_id": 2,
        "id": 1,
        "created_at": "2023-10-27T10:45:00.000000"
      }
    ]
    ```

#### Update Admin Log

-   **Method:** `PUT`
-   **URL:** `http://127.0.0.1:8000/api/admin_logs/{admin_log_id}`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Request Body (`AdminLogUpdate`):**
    ```json
    {
      "action": "User 'testuser' ban reviewed and confirmed."
    }
    ```
-   **Expected Response (`AdminLogInDB`):** `200 OK`
    ```json
    {
      "admin_id": 1,
      "action": "User 'testuser' ban reviewed and confirmed.",
      "target_id": 2,
      "id": 1,
      "created_at": "2023-10-27T10:45:00.000000"
    }
    ```

#### Delete Admin Log

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/admin_logs/{admin_log_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `204 No Content`.

## Project Structure

The project follows a clean architecture pattern, separating concerns into `application`, `domain`, `infrastructure`, and `presentation` layers. This structure promotes maintainability, scalability, and testability by ensuring a clear separation of responsibilities.

```
SafeTravel-Server/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── run.py                  # Application entry point
├── docs/                   # Project documentation
├── logs/                   # Application logs
└── src/
    ├── application/        # Business logic and use cases
    │   ├── admin_log/      # DTOs and use cases for admin logs
    │   ├── circle/         # DTOs and use cases for circles and members
    │   ├── friend/         # DTOs and use cases for friend connections
    │   ├── location/       # DTOs and use cases for location tracking
    │   ├── notification/   # DTOs and use cases for notifications
    │   ├── security/       # Interfaces for security services (e.g., password hashing, token management)
    │   ├── sos/            # Services for SOS functionalities
    │   ├── sos_alert/      # DTOs and use cases for SOS alerts
    │   └── user/           # DTOs and use cases for user management
    ├── config/             # Configuration settings
    ├── domain/             # Core entities, interfaces, and business rules
    │   ├── admin_log/      # Admin log entities and repository interface
    │   ├── circle/         # Circle entities and repository interfaces
    │   ├── friend/         # Friend entities and repository interface
    │   ├── location/       # Location entities and repository interface
    │   ├── notification/   # Notification entities and repository interface
    │   ├── sos_alert/      # SOS alert entities and repository interface
    │   └── user/           # User entities and repository interface
    ├── infrastructure/     # Database implementations, external services, AI clients
    │   ├── admin_log/      # Admin log models and repository implementation
    │   ├── ai/             # Google Gemini AI client
    │   ├── circle/         # Circle models and repository implementations
    │   ├── database/       # Database connection and ORM setup
    │   │   ├── firebase/   # Firebase database implementation (if used)
    │   │   └── sql/        # SQL database implementation (e.g., SQLAlchemy)
    │   ├── external_service/ # External service integrations
    │   ├── friend/         # Friend models and repository implementation
    │   ├── location/       # Location models and repository implementation
    │   ├── notification/   # Notification models and repository implementation
    │   ├── security/       # Security implementations (e.g., Bcrypt, JWT)
    │   ├── sos_alert/      # SOS alert models and repository implementation
    │   └── user/           # User models and repository implementation
    ├── presentation/       # FastAPI routes and API endpoints
    │   ├── auth_routes.py  # Authentication related API routes
    │   └── friend_routes.py # Friend management API routes
    └── shared/             # Shared utilities (e.g., logger)
        └── utils/          # Utility functions
```

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
