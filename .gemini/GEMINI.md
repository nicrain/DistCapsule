# Gemini Project Memory: DistCapsule

## 📌 Identification
- **Project Name**: DistCapsule (Smart Capsule Dispenser)
- **Target Platform**: Raspberry Pi 5 (Bookworm OS)
- **Current State**: Dev S7 (Android API & App Prep) (Last updated: 2026-01-14)

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
- **Offline Hotspot**: Configured via `tools/setup_manual_hotspot.sh` (192.168.4.1).
- **Silent Mode**: No gateway assigned in DHCP to allow phones to keep 4G/5G internet access while connected to the Pi.

## 🚀 Recent Accomplishments
- **S7 (Mobile Integration)**:
    - **Documentation**: Created LaTeX presentation slides in `docs/slides/` featuring AAA architecture and 3D design iteration history.
    - **Architecture Change**: Removed MQTT from roadmap; decided to focus exclusively on REST API (`FastAPI`) for simplicity and reliability.
    - **API Backend**: Implemented `FastAPI` server in `api/` exposing User and Log data (serialization fixed, tested OK).
    - **Remote Control**: Integrated Database-driven Command Queue (`Pending_Commands`) linking REST API to Hardware Loop for remote unlocking.
    - **Specs**: Created comprehensive Android App specification (`docs/ANDROID_APP_SPEC.md`).
- **S5 (Intelligent Core) & Fixes**: 
    - **Camera Fix**: Implemented 90-degree counter-clockwise rotation in `face_system.py` and `face_enroll.py` to match physical mounting.
    - **UI/UX**: Full bilingual support (Chinese/French) added to Console Logs, CLI Tools, and LCD Display.
    - **AI Optimization**: Tightened face recognition threshold to 0.68 and clarified log terminology ("Feature Diff") to avoid confusion.
    - **Wiring**: Updated Servo 2-5 pin assignments to avoid conflicts and improve layout.
    - **Concurrency**: Implemented robust Thread/Queue/Event architecture. Removed all blocking `time.sleep` from Main Loop.
    - **Persistence**: Added auto-migration to `setup_database.py` to handle schema updates (e.g., `face_encoding`).
    - **UI/UX**: Real-time linear countdown and non-blocking button debounce.

## 🎓 Learning Progress (Python Study)
- **Status**: Phase 5 (Network & Communication) - **Started**.
- **Completed**: 
    - Phase 1: Classes & Hardware (`servo_control`, `st7789`).
    - Phase 2: Logic & Database (`log_access`, `get_user_info`).
    - Phase 3: Control Flow (`State Machine`, `Timestamps`, `Edge Detection`).
    - Phase 4: Concurrency (`Threading`, `Queue`, `Event`, `Database Migration`).
- **Next Lesson**: Phase 5: Network & Communication (API Integration, Retrofit on Android).

## 🔮 Next Steps
- Android Team: Build the app based on `ANDROID_APP_SPEC.md`.
- Backend: Integrate `main.py` hardware control into the `FastAPI` server (Phase 2).
- Add inventory tracking (capsule count) in the database.

## 📝 Operational Mandates
- **Environment**: Do NOT suggest `sudo` for python scripts (using `lgpio` in user space). Do NOT suggest running hardware scripts on macOS host.
- **Doc Sync**: When updating project status, ALWAYS update `README.md`, `docs/README_CN.md`, and `docs/PROJECT_STATUS_S6.md`.

---
*This file serves as a persistent context for Gemini CLI sessions within this project.*