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
*   **First Run (New User)**:
    1.  App scans for the API (`GET /`).
    2.  **One-Click Registration**: User enters Name and clicks "Créer et se connecter".
    3.  **Auto-Assignment**: The server automatically assigns the first available channel (1-5).
    4.  **Instant Access**: App saves the token and jumps directly to the Dashboard.
*   **Auto-Login**: Subsequent runs use the stored Token to log in silently.

### 3.2 Dashboard (Main Screen)
*   **Header**: "Bonjour, [Name]".
*   **Status Card**:
    *   **Self-Enrollment Buttons**: "Ajouter Face" / "Ajouter Empreinte".
    *   Buttons turn **Green** ("Mettre à jour") once enrolled.
*   **Center**:
    *   If **User** + **Assigned Channel**: Big Green Button `[ OBTENIR MON CAFE ]`.
    *   If **Admin**: Visual Channel Map with 5 interactive buttons.
*   **Admin Channel Management**:
    *   **Visual Interface**: 5 Buttons (Red=Occupied, Green=Free, Orange=Selected).
    *   **Pop-up Animation**: Selected channel pops up visually.
    *   **Action**: "Attribuer Canal X" or "Retirer le Canal".

### 3.3 Enrollment (Sync)
*   **Process**:
    *   User clicks "Ajouter Empreinte" in App.
    *   **Hardware Sync**: Pi screen wakes up and shows instructions.
    *   **Real-time**: App updates button status automatically upon completion.

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