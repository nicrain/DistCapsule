# 📱 DistCapsule Android App Specification (V2.0)

**Project Name**: DistCapsule (Smart Coffee Capsule Dispenser)
**Target Platform**: Android (Min SDK 24+)
**Backend**: Raspberry Pi 5 (FastAPI REST)
**Version**: 2.0 (Updated 2026-01-16)

---

## 1. Project Overview

The Android application serves as the primary **Control & Management Interface** for the DistCapsule system. It connects to the Raspberry Pi via local Wi-Fi (Hotspot `DistCapsule_Box`) and provides two distinct views based on user roles:
1.  **Administrator**: Full system management (Users, Channels, Hardware).
2.  **Standard User**: Personal coffee retrieval and profile management.

---

## 2. User Roles & Features

### 2.1 Administrator (Admin)
*   **User Management**:
    *   Create new users (Name, Permission).
    *   Assign/Reassign coffee channels (Rails 1-5).
    *   Trigger remote biometric enrollment (Face/Fingerprint).
    *   Delete users (including hardware data cleanup).
    *   *Note*: The App must handle **HTTP 400 errors** if assigning a channel that is already occupied by another user.
*   **Hardware Control**:
    *   Manually open any channel (Maintenance).
    *   View real-time channel occupancy map.

### 2.2 Standard User
*   **One-Tap Dispense**:
    *   Large button "Get My Coffee" (Ouvrir mon canal).
    *   Only works if the user has an assigned channel.
*   **Self-Management**:
    *   Delete own account (GDPR compliance / Unregister).
*   **Visualization**:
    *   View the "Coffee Map" (Which channel is occupied by whom).

---

## 3. App Workflow & UX

### 3.1 Onboarding & Login (Token Based)
*   **No Password**: The app uses a device-bound **Token** for authentication.
*   **First Run**:
    1.  App scans for the API (`GET /`).
    2.  User selects their name from a list (`GET /users`).
    3.  **Binding**: App sends a generated UUID to the server (`POST /bind`).
    4.  *Security Note*: For this prototype, we assume the local Wi-Fi is trusted. No PIN required.
*   **Subsequent Runs**:
    1.  App sends Token (`POST /auth`).
    2.  Server returns user profile.
    3.  App jumps directly to the Dashboard.

### 3.2 Dashboard (Main Screen)
*   **Header**: "Bonjour, [Name]".
*   **Status Card**: Display icons indicating biometric status (e.g., "Face: ✅ | Finger: ❌") so users know if they are fully enrolled.
*   **Center**:
    *   If **User** + **Assigned Channel**: Big Green Button `[ DISPENSE ]`.
    *   If **Admin**: Grid view of 5 Channels with control buttons.
    *   If **No Channel**: "Waiting for assignment / En attente".
*   **Footer**: "Channel Map" (List of who owns which channel).

### 3.3 Enrollment (Admin Only)
*   Inside User Details:
    *   Button `[ Enroll Face ]` -> Triggers Pi camera mode.
    *   Button `[ Enroll Finger ]` -> Triggers Pi fingerprint sensor mode.
*   **Feedback**: App should show a toast "Enrollment Started, please follow instructions on the machine screen".
*   **Best Practice**: The App should automatically **refresh the user list (`GET /users`)** after a few seconds to update the `has_face` / `has_fingerprint` status icons.

---

## 4. Technical Architecture

### 4.1 Network
*   **Protocol**: HTTP REST (JSON).
*   **Address**: `http://192.168.4.1:8000` (Default Hotspot Gateway).
*   **Constraint**: The phone must stay connected to the Pi's Wi-Fi.

### 4.2 Data Models
*   **User**: `id`, `name`, `auth_level` (1=Admin, 2=User), `assigned_channel` (1-5 or null), `has_face` (bool), `has_fingerprint` (bool).
*   **Command**: The App does not control servos directly. It sends **Commands** (`UNLOCK`, `ENROLL`) to the API, which queues them for the Hardware Agent (`main.py`).

---

## 5. Developer Guide (Next Steps)
For detailed API endpoints, parameters, and JSON examples, please refer to the **[API Reference Documentation](API_REFERENCE.md)**.