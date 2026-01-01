# Gemini Project Memory: DistCapsule

## 📌 Identification
- **Project Name**: DistCapsule (Smart Capsule Dispenser)
- **Target Platform**: Raspberry Pi 5 (Bookworm OS)
- **Current State**: Stable S5 (Last updated: 2025-12-30)

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
    - **Multi-threaded**: Face recognition runs in a background thread to keep UI (countdown) fluid and linear.
    - **GPIO Library**: Exclusively using `lgpio` for all I/O to avoid Pi 5 hardware clock conflicts.
    - **Database**: SQLite3 (`capsule_dispenser.db`) for user mapping and access logs.
- **Key Features**: 
    - 30s auto-sleep, 5min max session timeout.
    - Button wakeup and session extension ("Keep Alive").
    - Real-time linear countdown UI with color alerts.

## 🌐 Network Logic
- **Offline Hotspot**: Configured via `tools/setup_manual_hotspot.sh` (192.168.4.1).
- **Silent Mode**: No gateway assigned in DHCP to allow phones to keep 4G/5G internet access while connected to the Pi.

## 🚀 Recent Accomplishments
- **Logic Optimization**: Removed blocking `sleep`, implemented non-blocking button debounce (edge detection), and centralized timestamp sync in `main.py`.
- **Refactoring**: Aligned servo channel mapping (1-5) across `main.py`, `hardware/servo_control.py`, and `tools/hardware_test.py`.
- **Documentation**: 
    - Updated `PROJECT_STATUS_S5.md` to be bilingual (FR/CN).
    - Synchronized `README.md` and `README_CN.md` with latest S5 logic.
- **Deep Dive Learning**: Added comprehensive Chinese educational comments to core files (`st7789`, `face_system`, `main`) covering SPI, CLAHE, and Threading/State Machine.

## 🎓 Learning Progress (Python Study)
- **Status**: Phase 4 (Advanced Concurrency) - **Next Lesson (Not Started)**.
- **Completed**: 
    - Phase 1: Classes & Hardware (`servo_control`, `st7789`).
    - Phase 2: Logic & Database (`log_access`, `get_user_info`).
    - Phase 3: Control Flow (`State Machine`, `Timestamps`, `Edge Detection`).
- **Next Lesson**: Phase 4: Concurrency (`Threading`, `Queue`, `Event`).

## 🔮 Next Steps
- Implement MQTT client in `main.py` for remote control.
- Develop a Flask/FastAPI web dashboard for log visualization.
- Add inventory tracking (capsule count) in the database.

---
*This file serves as a persistent context for Gemini CLI sessions within this project.*
