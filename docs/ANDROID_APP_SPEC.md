# 📱 DistCapsule Android App Specification (V2.0)

**Project Name**: DistCapsule (Smart Coffee Capsule Dispenser)
**Target Platform**: Android (Min SDK 24+)
**Backend**: Raspberry Pi 5 (FastAPI REST)
**Version**: 1.1 (Updated 2026-01-18)

---

## 1. Project Overview

L'application Android sert d'interface de contrôle principale. Elle a été optimisée en version 1.1 avec une **Vivid UI** (palette de couleurs vive et contrastée) pour une meilleure lisibilité et une réactivité accrue.

---

## 2. User Roles & Features

### 2.1 Administrator (Admin)
*   **User Management**:
    *   Assign/Reassign coffee channels (Rails 1-5) via a **Visual Interface** (buttons with pop-up animations).
    *   Trigger remote biometric enrollment (Face/Fingerprint).
    *   Delete users (instant database update + hardware cleanup).
*   **Hardware Control**:
    *   Manually open any channel.
    *   View real-time channel occupancy map.

### 2.2 Standard User
*   **One-Tap Dispense**:
    *   Large button "Obtenir mon café" (Emerald Green).
*   **Self-Management**:
    *   Delete own account.
    *   **Self-Enrollment**: Launch face/fingerprint enrollment directly from the phone.

---

## 3. App Workflow & UX

### 3.1 Onboarding & Login (Token Based)
*   **Auto-Login**: L'application utilise un Token lié à l'appareil. Une fois enregistré, l'utilisateur accède directement au Dashboard.
*   **First Run (New User)**:
    1.  **One-Click Registration**: Entrez votre nom, cliquez sur "Créer et se connecter".
    2.  Le système attribue automatiquement le premier canal libre.
    3.  L'application génère et stocke le Token UUID.

### 3.2 Dashboard (Main Screen)
*   **Vivid Visuals**:
    *   **Emerald (#2ECC71)**: Actions réussies / Prêt.
    *   **Sunflower (#F1C40F)**: En attente / Sélectionné.
    *   **Coral (#FF5A5F)**: Occupé / Suppression.
*   **Header**: "Bonjour, [Name] ! Votre café est au Canal [X]." (ou message de bienvenue si pas de canal).

---

## 4. Technical Architecture

### 4.1 Network
*   **Smart IP Handling**: L'utilisateur entre simplement l'IP (ex: `192.168.4.1`). L'App gère automatiquement le protocole `http://` et le port `:8000`.
*   **Offline Hotspot**: Connection directe au Pi via `DistCapsule_Box`.

---

## 5. Developer Guide (Next Steps)
La version 1.1 a supprimé le "Mode Demo" pour garantir l'intégrité des sessions réelles. Tout test doit désormais s'appuyer sur une instance API active.