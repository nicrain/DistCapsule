# Gemini Project Memory: DistCapsule

## 📌 Identification
- **Project Name**: DistCapsule (Smart Capsule Dispenser)
- **Target Platform**: Raspberry Pi 5 (Bookworm OS)
- **Current State**: Prod V1.1 (Android Release) (Last updated: 2026-01-18)

## ⚠️ Environment Constraints
- **Current Host**: macOS (Darwin) - Development/Refactoring Mode.
- **Hardware Access**: ❌ NOT AVAILABLE (No GPIO, Camera, or Serial).
- **Execution Rule**: Do NOT attempt to run `main.py` or tools in `tools/` that depend on `lgpio`, `rpi_gpio`, or `picamera` while on this host. Only perform static code analysis, editing, and git operations.

## 🧠 Core Technical Context
- **Hardware Architecture**: 
    - 5x SG90 Servos (Soft-PWM via `lgpio`).
    - DY-50 Fingerprint Sensor (`/dev/ttyAMA0`).
    - ST7789 LCD (SPI).
    - Raspberry Pi Camera Module 3 (IMX708).
    - Wake-up Button (GPIO 26, BCM).
- **Software Architecture**: 
    - **Concurrency Model**: Producer-Consumer pattern using `threading` and `queue`. `face_worker` (Producer) scans in background; Main Loop (Consumer) handles UI/GPIO.
    - **API Layer**: `FastAPI` server (`api/server.py`) running on port 8000 to serve data to Android App.
    - **GPIO Library**: Exclusively using `lgpio` for all I/O to avoid Pi 5 hardware clock conflicts.
    - **Database**: SQLite3 with auto-migration logic (`setup_database.py`) for schema evolution.
- **Key Features**: 
    - 30s auto-sleep, 5min max session timeout.
    - Button wakeup and session extension ("Keep Alive").
    - Real-time linear countdown UI with color alerts.

## 🌐 Network Logic
- **Standard Hotspot**: Configured via `tools/setup_manual_hotspot.sh` (192.168.4.1) with Gateway ENABLED for maximum stability on Android 10+.
- **UX**: One-click Wi-Fi connection button in App.

## 🚀 Recent Accomplishments
- **Prod V1.1 (Android Release)**:
    - **UX Revolution**: Implemented "Vivid Palette" UI (Emerald Green/Sunflower Yellow/Coral Red). Added One-Click Wi-Fi connection logic (Android 9/10+ support).
    - **Admin Security**: Hardened security logic. Admins cannot delete themselves; Admin profile is locked from editing in the management console.
    - **Code Quality**: Massive cleanup of `strings.xml` (deduplicated, removed unused resources). Standardized `colors.xml` with clear functional comments.
    - **Build**: Successfully generated Debug APK.
- **S7 (Mobile Integration)**:
    - **API Backend**: Implemented `FastAPI` server in `api/` exposing User and Log data (serialization fixed, tested OK).
    - **App Control**: Implemented local Wi-Fi control (renamed from Remote) linking API to Hardware via `Pending_Commands`.
    - **App Integration**: Successfully merged initial Android Studio project (15MB) into `android/` directory.
    - **Hotspot Fix**: Re-enabled DHCP Gateway option to ensure stable Android/iOS connectivity.
    - **API Enhancements**: Added `has_face`/`has_fingerprint` flags and full User Management (`POST/DELETE` users) with hardware synchronization.
    - **Specs**: Created comprehensive Android App specification (`docs/ANDROID_APP_SPEC.md`).

## 🎓 Learning Progress (Python Study)
- **Status**: Phase 5 (Network & Communication) - **Completed**.
- **Completed**: 
    - Phase 1-4: Hardware, Logic, Concurrency.
    - Phase 5: Network & Communication (API Integration, Retrofit on Android).
- **Next Lesson**: Phase 6: System Integration & Deployment.

## 🔮 Next Steps
- **Hardware Deployment**: Final physical assembly (3D printed case).
- **Live Demo**: Demonstrate full flow: Boot -> Hotspot -> App Connect -> Enroll -> Dispense.
- **Maintenance**: Monitor SQLite locks during high concurrency.

## 📝 Operational Mandates
- **Environment**: Do NOT suggest `sudo` for python scripts (using `lgpio` in user space). Do NOT suggest running hardware scripts on macOS host.
- **Doc Sync**: When updating project status, ALWAYS update `README.md`, `docs/README_CN.md`, and `docs/PROJECT_STATUS_S6.md`.

---
*This file serves as a persistent context for Gemini CLI sessions within this project.*