# Gemini Project Memory: DistCapsule

## 📌 Identification
- **Project Name**: DistCapsule (Smart Capsule Dispenser)
- **Target Platform**: Raspberry Pi 5 (Bookworm OS)
- **Current State**: Stable S5 (Last updated: 2025-12-30)

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
- Fixed `RuntimeError` on fingerprint initialization by migrating button logic to `lgpio`.
- Refactored `main.py` into a threaded state-machine.
- Implemented real-time dynamic clock and countdown UI.

## 🔮 Next Steps
- Implement MQTT client in `main.py` for remote control.
- Develop a Flask/FastAPI web dashboard for log visualization.
- Add inventory tracking (capsule count) in the database.

---
*This file serves as a persistent context for Gemini CLI sessions within this project.*
