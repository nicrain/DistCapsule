# Smart Capsule Dispenser (智能胶囊分配器)

**Platform:** Raspberry Pi 5 (Bookworm OS) | **Status:** Stable (S5) | **Last Updated:** 2025-12

A secure, biometric-enabled capsule dispenser system. It transforms a standard capsule rack into a personalized "mailbox" system where each user has exclusive access to a specific storage channel via fingerprint authentication.

## ✨ Key Features

*   **Biometric Security**: Integrated DY-50 (R307 compatible) optical fingerprint sensor for fast user identification.
*   **Precision Control**: Controls 5x SG90 servos using **Software PWM (`lgpio`)**, specifically optimized for the Raspberry Pi 5 to avoid hardware PWM conflicts with the system fan.
*   **Interactive UI**: 1.3" IPS Display (ST7789) provides real-time status, feedback, and user prompts.
*   **Local Database**: SQLite-backed user management and access logging.
*   **Robust Design**: Includes jitter-prevention logic (auto-cutoff after movement) and robust error handling for serial communications.

## 🛠 Hardware Architecture

*   **Controller**: Raspberry Pi 5 (8GB recommended).
*   **Actuators**: 5x SG90 Micro Servos (9g).
*   Sensor: DY-50 / R307 Optical Fingerprint Module (UART).
*   **Display**: 1.3" IPS LCD (240x240) with ST7789 driver (SPI).
*   **Base Unit (Mechanical)**: Custom 3D Printed Components - The mechanical structure will be custom-designed and 3D printed. Initial drafts are available in the `3D/` directory.
*   **Power**:
    *   Pi 5: Official 27W USB-C Power Supply.
    *   Servos: **External 5V Power Supply** (Common Ground with Pi is mandatory).

> **⚠️ Wiring Warning**: Do not power 5 servos directly from the Pi's GPIO 5V pin. Use an external power source. See [WIRING_GUIDE.md](WIRING_GUIDE.md) for detailed pinouts.

## 🚀 Installation & Setup

### 1. System Dependencies
The project relies on `lgpio` for GPIO control on the Pi 5 and `pyserial` for the sensor.

```bash
sudo apt-get update
sudo apt-get install python3-serial python3-pip python3-lgpio python3-pil python3-rpi.gpio
```

### 2. Python Libraries
```bash
sudo pip3 install adafruit-circuitpython-fingerprint st7789
```

### 3. Hardware Configuration
*   **UART**: Enable Serial Port hardware but disable the login shell via `sudo raspi-config`. The fingerprint module uses `/dev/ttyAMA0` (GPIO 14/15) on Pi 5.
*   **SPI**: Enable SPI interface via `sudo raspi-config` for the display.

## 📖 Usage Guide

### 1. Initialize System
Create the database tables for users and logs.
```bash
python3 setup_database.py
```

### 2. Enroll Users (Fingerprint)
Register a new user and capture their fingerprint. Follow the on-screen prompts.
```bash
sudo python3 fingerprint_enroll.py
```
*   *Note: Ensure the database is initialized first.*

### 3. Hardware Test
To verify that all components (Servos, Screen, Fingerprint) are connected and working correctly, run the integrated test tool.
```bash
sudo python3 hardware_test.py
```
*   Select '1' to test all servos.
*   Select '2' to test the screen colors.
*   Select '3' to check fingerprint sensor connection and image capture.

### 4. Run Main Program
Start the dispenser system. This runs the fingerprint listening loop, updates the display, and controls servos based on authentication.
```bash
sudo python3 main_demo.py
```

## 📂 Project Structure

| File | Description |
| :--- | :--- |
| `main_demo.py` | **Core Application**. Handles auth loop, UI updates, and servo triggering. |
| `servo_control.py` | **Driver**. Wrapper for `lgpio` to control SG90 servos via Software PWM. |
| `st7789_driver.py` | **Driver**. Custom SPI driver for the IPS display. |
| `fingerprint_enroll.py` | **Tool**. Standalone script to register new fingerprints. |
| `setup_database.py` | **Tool**. Initializes the SQLite database schema. |
| `WIRING_GUIDE.md` | **Documentation**. Detailed pinout and wiring diagrams. |
| `capsule_dispenser.db` | **Data**. Local SQLite database (created after setup). |

## 🔮 Future Roadmap

*   **Camera Integration**: Add Raspberry Pi Camera Module 3 for Face ID or QR Code unlock (Secondary Auth).
*   **Web Dashboard**: Develop a local Flask/Django interface for remote log viewing, user management, and emergency unlock.
*   **Inventory & Social**: 
    *   Track capsule counts per channel.
    *   "Capsule Sharing" feature: Allow users to offer surplus capsules to others via the app.
*   **Enclosure**: Design a fully 3D-printed enclosure to hide wires and mount the Pi/Screen securely to the base unit.

## 📜 History & Decisions

*   **2025-12 (S5)**: Migrated Servo control from Hardware PWM to **Software PWM** (`lgpio`).
    *   *Reason*: The Raspberry Pi 5's hardware PWM clock is shared with the cooling fan. When the fan activates, it forces the PWM frequency to ~25kHz, causing servos (which need 50Hz) to fail. Software PWM avoids this conflict entirely.
    *   *Update*: Implemented **Soft Start (Smooth Move)** logic in `servo_control.py` (tuned to 2.0s duration) to drastically reduce peak current draw during servo actuation, preventing voltage sag on the shared power rail.
*   **2024-11**: Removed Arduino from architecture. The Pi 5 is powerful enough to handle all IO directly.

## 📄 License
MIT License