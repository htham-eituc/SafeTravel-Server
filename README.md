# SafeTravel Backend API

This project provides a backend API for a SafeTravel application, built with FastAPI, SQLAlchemy, and MySQL. It includes modules for user management, circles, circle members, friends, locations, notifications, SOS alerts, and admin logs.

## Table of Contents

- [SafeTravel Backend API](#safetravel-backend-api)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create a Virtual Environment](#2-create-a-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Database Setup](#4-database-setup)
    - [5. Environment Variables](#5-environment-variables)
    - [6. Run the Application](#6-run-the-application)
    - [7. Run Mock Database Test](#7-run-mock-database-test)
  - [API Testing with Postman](#api-testing-with-postman)
    - [Accessing API Documentation](#accessing-api-documentation)
    - [Authentication Endpoints](#authentication-endpoints)
      - [Register User](#register-user)
      - [Login User](#login-user)
      - [Get Current User (Authenticated)](#get-current-user-authenticated)
    - [Circle Endpoints](#circle-endpoints)
      - [Create Circle](#create-circle)
      - [Get Circles](#get-circles)
      - [Get Specific Circle](#get-specific-circle)
      - [Update Circle](#update-circle)
      - [Delete Circle](#delete-circle)
    - [Circle Member Endpoints](#circle-member-endpoints)
      - [Add Circle Member](#add-circle-member)
      - [Get Circle Members by Circle ID](#get-circle-members-by-circle-id)
      - [Remove Circle Member](#remove-circle-member)
    - [Friend Endpoints](#friend-endpoints)
      - [Create Friend](#create-friend)
      - [Get Friends by User ID](#get-friends-by-user-id)
      - [Delete Friend](#delete-friend)
    - [Other Endpoints (Conceptual)](#other-endpoints-conceptual)

## Features

- User authentication (registration, login, token generation)
- User management (CRUD operations)
- Circle management (create, retrieve, update, delete circles)
- Automatic deactivation of old circles when a new one is created by a user
- Automatic addition of circle owner as a member with 'owner' role
- Circle member management (add, retrieve, remove members)
- Friend management
- Location tracking (conceptual)
- Notification system (conceptual)
- SOS alert system (conceptual)
- Admin logging (conceptual)
- Mock database test for initial data population

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- MySQL Server (e.g., via XAMPP, WAMP, or a standalone installation)
- Postman (for API testing)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository_url>
cd SafeTravel-Server
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

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

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Database Setup

This project uses MySQL.

1.  **Create a MySQL database:**
    Open your MySQL client (e.g., phpMyAdmin, MySQL Workbench, or MySQL command-line client) and create a database named `safetravel`.

    ```sql
    CREATE DATABASE safetravel;
    ```

2.  **Ensure tables are created:**
    The application will automatically create the necessary tables (`users`, `circles`, `circle_members`, `friends`, `locations`, `notifications`, `sos_alerts`, `admin_logs`) when it starts, based on the SQLAlchemy models.

    **Important Note for Schema Updates:** If you modify any database models (e.g., add a new column), you might need to update your database schema. In a development environment, the simplest way to do this is to drop the affected tables and let the application recreate them. For example, if you modified the `circles` table and are encountering errors like "Unknown column 'description' in 'field list'", you would need to drop the `sos_alerts`, `circle_members`, and `circles` tables in that order due to foreign key constraints.

    ```sql
    -- Drop tables in reverse dependency order
    DROP TABLE IF EXISTS safetravel.sos_alerts;
    DROP TABLE IF EXISTS safetravel.circle_members;
    DROP TABLE IF EXISTS safetravel.circles;
    -- The application will recreate them on startup
    ```

### 5. Environment Variables

Create a `.env` file in the root of your project directory by copying `.env.example`:

```bash
cp .env.example .env
```

Open the `.env` file and configure your database connection string and secret key:

```
DATABASE_URL="mysql+mysqlconnector://root:@127.0.0.1/safetravel"
SECRET_KEY="your_super_secret_key"
GEMINI_API_KEY="your_api_key_here"
```

-   **`DATABASE_URL`**: Update this if your MySQL credentials or host are different.
-   **`SECRET_KEY`**: **Change `your_super_secret_key` to a strong, random key for production environments.**
-   **`GEMINI_API_KEY`**: Provide your API key for Gemini AI services.

### 6. Run the Application

Start the FastAPI application using Uvicorn:

```bash
python -m uvicorn run:app --reload
```

The application will run on `http://127.0.0.1:8000`. The `--reload` flag will automatically restart the server when code changes are detected.

### 7. Run Mock Database Test

The mock database test (`src/tests/mock_db_test.py`) is configured to run automatically once when the server starts. It will create a `test.db` SQLite file and populate the `users` table with a mock user if one doesn't already exist. This is useful for development and testing purposes.

## API Testing with Postman

Once the application is running, you can test the API endpoints using Postman.

### Accessing API Documentation

You can access the interactive API documentation (Swagger UI) at:

`http://127.0.0.1:8000/api/docs`

Or the ReDoc documentation at:

`http://127.0.0.1:8000/api/redoc`

### Authentication Endpoints

#### Register User

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/register`
-   **Headers:**
    -   `Content-Type`: `application/json`
-   **Body:** (raw, JSON)
    ```json
    {
      "name": "Test User",
      "email": "test@example.com",
      "phone": "1234567890",
      "password": "testpassword"
    }
    ```
-   **Expected Response:** `201 Created` with user details.

#### Login User

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/token`
-   **Headers:**
    -   `Content-Type`: `application/x-www-form-urlencoded`
-   **Body:** (x-www-form-urlencoded)
    -   `username`: `test@example.com`
    -   `password`: `testpassword`
-   **Expected Response:** `200 OK` with `access_token` and `token_type`. **Copy the `access_token` for authenticated requests.**

#### Get Current User (Authenticated)

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/users/me`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (Replace `YOUR_ACCESS_TOKEN` with your actual token)
-   **Expected Response:** `200 OK` with current user details.

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

### Friend Endpoints

All friend endpoints require authentication.

#### Create Friend

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:8000/api/friends`
-   **Headers:**
    -   `Content-Type`: `application/json`
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Body:** (raw, JSON)
    ```json
    {
      "user_id": 1,
      "friend_id": 2
    }
    ```
    (Replace `user_id` with the current authenticated user's ID, and `friend_id` with another existing user's ID.)
-   **Expected Response:** `201 Created` with new friend relationship details.

#### Get Friends by User ID

-   **Method:** `GET`
-   **URL:** `http://127.0.0.1:8000/api/friends`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `200 OK` with a list of friends for the current user.

#### Delete Friend

-   **Method:** `DELETE`
-   **URL:** `http://127.0.0.1:8000/api/friends/{friend_id}`
-   **Headers:**
    -   `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
-   **Expected Response:** `204 No Content`.

### Other Endpoints (Conceptual)

The following endpoints are part of the project structure but require further implementation and testing:

-   **Location Endpoints:** For managing user locations.
-   **Notification Endpoints:** For handling user notifications.
-   **SOS Alert Endpoints:** For managing SOS alerts.
-   **Admin Log Endpoints:** For administrative logging.
