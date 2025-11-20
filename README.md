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
    - [Circle Endpoints](#circle-endpoints-1)
      - [Create Circle](#create-circle-1)
      - [Get Circles](#get-circles-1)
      - [Get Specific Circle](#get-specific-circle-1)
      - [Update Circle](#update-circle-1)
      - [Delete Circle](#delete-circle-1)
    - [Circle Member Endpoints](#circle-member-endpoints)
      - [Add Circle Member](#add-circle-member)
      - [Get Circle Members by Circle ID](#get-circle-members-by-circle-id)
      - [Remove Circle Member](#remove-circle-member)
    - [SOS Alert Endpoints](#sos-alert-endpoints)
      - [Send SOS Alert](#send-sos-alert)
      - [Update SOS Alert Status](#update-sos-alert-status)
      - [Get My SOS Alerts](#get-my-sos-alerts)
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
    The application will automatically create all necessary tables (`users`, `circles`, `circle_members`, `friend_requests`, `friendships`, `locations`, `notifications`, `sos_alerts`, `admin_logs`) when it starts, based on the SQLAlchemy models.

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
```

-   **`DATABASE_URL`**: Update with your MySQL connection string if your credentials or host differ.
-   **`SECRET_KEY`**: **Crucially, replace `your_super_secret_key` with a strong, unique, and random key for production security.**
-   **`GEMINI_API_KEY`**: Provide your API key for Google Gemini services.

### 6. Run the Application

Start the FastAPI application using Uvicorn:

```bash
python -m uvicorn run:app --reload
```

The server will typically run on `http://127.0.0.1:8000`. The `--reload` flag enables automatic server restarts on code changes, which is useful for development.

## API Documentation and Testing

Once the application is running, you can access the interactive API documentation (Swagger UI) at:

`http://127.0.0.1:8000/api/docs`

Or the ReDoc documentation at:

`http://127.0.0.1:8000/api/redoc`

These interfaces provide detailed information about all available endpoints, request/response schemas, and allow you to test the API directly from your browser.

## API Endpoints

This section provides examples for testing the API endpoints using Postman.

### Authentication Endpoints

#### Register User

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/register`
-   **Headers:**
    -   `Content-Type`: `application/json`
-   **Body:** (raw, JSON)
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
-   **Expected Response:** `201 Created` with user details.

#### Login User

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/login`
-   **Headers:**
    -   `Content-Type`: `application/x-www-form-urlencoded`
-   **Body:** (x-www-form-urlencoded)
    -   `username`: `testuser`
    -   `password`: `testpassword`
-   **Expected Response:** `200 OK` with `access_token` and `token_type`. **Copy the `access_token` for authenticated requests.**

#### Logout User (Authenticated)

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/logout`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Replace `YOUR_ACCESS_TOKEN` with your actual token)
-   **Expected Response:** `200 OK` with a success message.

### Friend Management Endpoints

All friend endpoints require authentication.

#### Send Friend Request

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/friend-requests`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the sender)
-   **Body:** (raw, JSON)
    ```json
    {
      "receiver_username": "friend_username"
    }
    ```
    (Replace `friend_username` with the username of the user you want to send a request to.)
-   **Expected Response:** `201 Created` with the new friend request details.

#### Get Pending Friend Requests

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/friend-requests/pending`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the receiver)
-   **Expected Response:** `200 OK` with a list of pending friend requests for the current user.

#### Accept Friend Request

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/friend-requests/{request_id}/accept` (Replace `{request_id}` with the ID of the pending request)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the receiver)
-   **Expected Response:** `200 OK` with the details of the newly created friendship.

#### Reject Friend Request

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/friend-requests/{request_id}/reject` (Replace `{request_id}` with the ID of the pending request)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Token of the receiver)
-   **Expected Response:** `200 OK` with the details of the rejected friend request.

#### Get User's Friends

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/friends`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with a list of `User` objects who are friends with the current user.

### Circle Endpoints

All circle endpoints require authentication.

#### Create Circle

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/circles`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "circle_name": "Family Circle",
      "description": "My family members"
    }
    ```
-   **Expected Response:** `201 Created` with new circle details.
    **Note:** When a new circle is created, any existing active circles for the user will be set to `inactive`, and the creator will automatically be added as a member with the role "owner".

#### Get Circles

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/circles`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with a list of circles owned by the current user.

#### Get Specific Circle

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}` (Replace `{circle_id}` with an actual circle ID)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with the specified circle's details.

#### Update Circle

-   **Method:** `PUT`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "circle_name": "Updated Family Circle",
      "status": "inactive"
    }
    ```
-   **Expected Response:** `200 OK` with the updated circle details.

#### Delete Circle

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `204 No Content`.

### Circle Endpoints

All circle endpoints require authentication.

#### Create Circle

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/circles`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "circle_name": "Family Circle",
      "description": "My family members"
    }
    ```
-   **Expected Response:** `201 Created` with new circle details.
    **Note:** When a new circle is created, any existing active circles for the user will be set to `inactive`, and the creator will automatically be added as a member with the role "owner".

#### Get Circles

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/circles`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with a list of circles owned by the current user.

#### Get Specific Circle

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}` (Replace `{circle_id}` with an actual circle ID)
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with the specified circle's details.

#### Update Circle

-   **Method:** `PUT`
-   **URL:** `http://127.0.0.1:8000/api/circles/{circle_id}`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "circle_name": "Updated Family Circle",
      "status": "inactive"
    }
    ```
-   **Expected Response:** `200 OK` with the updated circle details.

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
-   **URL:** `http://127.0.0.1:8000/api/circle_members`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "circle_id": 1,
      "member_id": 2,
      "role": "member"
    }
    ```
    (Replace `circle_id` and `member_id` with actual IDs. `member_id` should be an existing user's ID.)
-   **Expected Response:** `201 Created` with new circle member details.

#### Get Circle Members by Circle ID

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/circle_members/circle/{circle_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with a list of members in the specified circle.

#### Remove Circle Member

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/circle_members/{circle_member_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `204 No Content`.

### SOS Alert Endpoints

All SOS alert endpoints require authentication.

#### Send SOS Alert

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/sos`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "user_id": 1,
      "circle_id": 1,
      "message": "I need help!",
      "latitude": 34.052235,
      "longitude": -118.243683
    }
    ```
    (Replace `user_id` with the ID of the authenticated user sending the SOS, and `circle_id` with the ID of their active circle.)
-   **Expected Response:** `201 Created` with the new SOS alert details.

#### Update SOS Alert Status

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/sos/{alert_id}/status`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "status": "resolved"
    }
    ```
    (Replace `{alert_id}` with the ID of the SOS alert to update.)
-   **Expected Response:** `200 OK` with the updated SOS alert details.

#### Get My SOS Alerts

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/sos/my_alerts`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with a list of SOS alerts for the authenticated user.

### Notification Endpoints

All notification endpoints require authentication.

#### Create Notification

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/notifications`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "user_id": 1,
      "message": "Your friend accepted your request.",
      "is_read": false
    }
    ```
    (Replace `user_id` with the ID of the user to whom the notification is sent.)
-   **Expected Response:** `201 Created` with new notification details.

#### Get Notification by ID

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/notifications/{notification_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with the specified notification's details.

#### Get Notifications by User

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/notifications`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with a list of notifications for the authenticated user.

#### Update Notification

-   **Method:** `PUT`
-   **URL:** `http://127.0.0.1:8000/api/notifications/{notification_id}`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "is_read": true
    }
    ```
-   **Expected Response:** `200 OK` with the updated notification details.

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
-   **Body:** (raw, JSON)
    ```json
    {
      "admin_id": 1,
      "action": "User 'testuser' banned for inappropriate content."
    }
    ```
    (Replace `admin_id` with the ID of the admin performing the action.)
-   **Expected Response:** `201 Created` with new admin log details.

#### Get Admin Log by ID

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/admin_logs/{admin_log_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with the specified admin log's details.

#### Get Admin Logs by Admin

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/admins/{admin_id}/admin_logs`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with a list of admin logs for the specified admin.

#### Update Admin Log

-   **Method:** `PUT`
-   **URL:** `http://127.0.0.1:8000/api/admin_logs/{admin_log_id}`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "action": "User 'testuser' ban reviewed and confirmed."
    }
    ```
-   **Expected Response:** `200 OK` with the updated admin log details.

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
