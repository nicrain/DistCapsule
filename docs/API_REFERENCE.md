# 📡 DistCapsule API Reference (V2.0)

**Base URL**: `http://<PI_IP>:8000` (Default: `192.168.4.1:8000`)
**Format**: JSON

---

## 1. Authentication & Session

### 1.1 Login (Auto Auth)
Retrieves current user info using the stored token.
*   **POST** `/auth`
*   **Body**:
    ```json
    { "token": "uuid-string-generated-by-android" }
    ```
*   **Response**: `User Object` (see below) or `401 Unauthorized`.

---

## 2. User Management

### 2.1 Get All Users
Returns a list of all users and their status.
*   **GET** `/users`
*   **Response**: `[User, User, ...]`

### 2.2 Create User (Register & Bind)
Creates a new user and optionally binds the current device token.
*   **POST** `/users`
*   **Body**:
    ```json
    {
      "name": "Jean Dupont",
      "auth_level": 2,        // 1=Admin, 2=User
      "assigned_channel": 1,  // Optional (1-5)
      "app_token": "uuid..."  // Optional: Bind device immediately
    }
    ```
*   **Response**: `User Object` (Newly created)

### 2.3 Update User (Reassign Channel)
*   **PATCH** `/users/{user_id}`
*   **Body** (All fields optional):
    ```json
    {
      "name": "New Name",
      "assigned_channel": 2   // Send null to release channel
    }
    ```
*   **Response**: `User Object` (Updated)
*   **Errors**: Returns `400` if the target channel is already occupied.

### 2.4 Delete User
Removes database record AND clears fingerprint data.
*   **DELETE** `/users/{user_id}`
*   **Response**: `{"status": "success"}`

---

## 3. Remote Commands (Control)

### 3.1 Dispense / Unlock
Opens a specific channel.
*   **POST** `/command/unlock?channel=1`
*   **Response**: `{"status": "success"}`

### 3.2 Trigger Face Enrollment
Puts the machine into face recording mode.
*   **POST** `/command/enroll_face?user_id=12`

### 3.3 Trigger Fingerprint Enrollment
Puts the machine into fingerprint recording mode.
*   **POST** `/command/enroll_finger?user_id=12`

### 3.4 Poll Command Status (Enrollment)
Checks the status of the latest asynchronous command (e.g., enrollment) for a user.
*   **GET** `/command/poll/{user_id}`
*   **Response**:
    ```json
    {
      "cmd_id": 55,
      "command_type": "ENROLL_FINGER",
      "status": "success",     // pending, success, failed, timeout
      "detail_message": "Fingerprint stored at ID 12"
    }
    ```

---

## 4. Data Models

### User Object
```json
{
  "user_id": 12,
  "name": "Jean Dupont",
  "auth_level": 2,
  "assigned_channel": 1,    // null if no channel
  "has_face": 1,            // 1=Yes, 0=No
  "has_fingerprint": 0,     // 1=Yes, 0=No
  "is_active": 1
}
```

### Log Object
```json
{
  "log_id": 101,
  "user_id": 12,
  "timestamp": "2026-01-16 14:30:00",
  "event_type": "APP_UNLOCK",
  "status": "SUCCESS",
  "detail_message": "Channel 1 unlocked via App"
}
```
