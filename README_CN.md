# 智能胶囊分配器 (Smart Capsule Dispenser)

[![Français](https://img.shields.io/badge/Language-Français-blue.svg)](./README.md)

**平台:** Raspberry Pi 5 (Bookworm OS) | **状态:** 稳定 (S5) | **最后更新:** 2025-12

这是一个安全的、支持生物识别的胶囊分配系统。它将标准的胶囊展示架转变为个性化的“信箱”系统，每个用户通过指纹认证拥有对特定存储通道的专属访问权。系统支持多用户录入、权限分级（管理员/普通用户）以及物理通道的动态分配。

---

## ✨ 主要功能

*   **多用户角色管理**: 支持 1 个超级管理员和无限候补用户。物理通道（舵机）仅分配给活跃用户（最多 5 人）。
*   **智能节能 (Eco Mode)**: 30秒无操作自动熄灭屏幕背光，触摸指纹传感器瞬间唤醒。大幅降低 CPU 占用与功耗。
*   **实时时钟**: 待机界面显示动态更新的系统时间，休眠时自动暂停刷新。
*   **指纹录入引导**: 交互式 CLI 工具，支持手指部位选择（如 Right Thumb）并自动列出当前用户状态。
*   **交互式 UI**: 1.3" IPS 屏实时显示用户姓名、分配的箱号。开锁倒计时采用**可视化进度条**显示。
*   **精确权限控制**: 认证后，普通用户解锁专属舵机；管理员仅显示欢迎界面，**不触发**任何硬件动作（用于维护/管理）。
*   **生物识别安全**: 集成 DY-50 (兼容 R307) 光学指纹传感器，实现快速识别。

---

## 🛠 硬件架构

*   **控制器**: Raspberry Pi 5 (推荐 8GB)。
*   **执行器**: 5x SG90 微型舵机 (9g)。
*   **传感器**: DY-50 / R307 光学指纹模块 (UART)。
*   **显示器**: 1.3" IPS LCD (240x240) 配备 ST7789 驱动 (SPI)。
*   **底座**: 定制 3D 打印组件。
*   **电源**: 
    *   Pi 5: 官方 27W USB-C 电源。
    *   舵机: **外部 5V 电源** (必须与 Pi 共地)。

> **⚠️ 接线警告**: 不要直接从 Pi 的 GPIO 5V 引脚为 5 个舵机供电。请使用外部电源。详见 [WIRING_GUIDE.md](WIRING_GUIDE.md)。

---

## 🚀 安装与设置

### 1. 系统依赖
该项目依赖 `lgpio` 进行 Pi 5 的 GPIO 控制，以及 `pyserial` 用于传感器通信。

```bash
sudo apt-get update
sudo apt-get install python3-serial python3-pip python3-lgpio python3-pil python3-rpi.gpio
```

### 2. Python 库
```bash
sudo pip3 install adafruit-circuitpython-fingerprint st7789
```

### 3. 人脸识别环境 (Pi 5 Bookworm)
Raspberry Pi OS Bookworm 系统默认禁止直接使用 `pip` 安装系统级包。请选择以下一种方法：

**方法 A: 使用 APT (推荐)**
```bash
sudo apt update
sudo apt install python3-opencv python3-face-recognition
```

**方法 B: 使用 PIP (如 APT 安装失败)**
```bash
# 在非虚拟环境下，必须添加 --break-system-packages 参数
pip3 install opencv-python face_recognition --break-system-packages
```

### 4. 硬件配置
*   **UART**: 通过 `sudo raspi-config` 启用串行端口硬件，但禁用登录 shell。Pi 5 上指纹模块使用 `/dev/ttyAMA0` (GPIO 14/15)。
*   **SPI**: 通过 `sudo raspi-config` 启用 SPI 接口用于显示屏。

---

## 📖 使用指南

### 1. 初始化系统
创建数据库表及初始化配置（此操作不会删除现有用户，除非手动删除 .db 文件）。

```bash
python3 setup_database.py
```

### 2. 管理用户与指纹
启动管理工具，您可以查看列表、录入管理员、录入用户并分配舵机（1-5号仓）。

```bash
sudo python3 fingerprint_enroll.py
```

### 3. 硬件测试
运行集成测试工具以验证所有组件（舵机、屏幕、指纹）是否连接并工作正常。

```bash
sudo python3 hardware_test.py
```
*   选择 '1' 测试所有舵机。
*   选择 '2' 测试屏幕颜色。
*   选择 '3' 检查指纹传感器连接和图像捕获。

### 4. 运行主程序
启动识别监听。系统将根据指纹权限自动驱动对应的舵机。

```bash
sudo python3 main_demo.py
```

---

## 📂 项目结构

| 文件 | 描述 |
| :--- | :--- |
| `main_demo.py` | **核心应用**. 处理认证循环、UI 更新和舵机触发。 |
| `fingerprint_enroll.py` | **管理工具**. 交互式录入指纹、分配通道及用户管理。 |
| `servo_control.py` | **驱动**. `lgpio` 的封装，用于通过软件 PWM 控制 SG90 舵机。 |
| `st7789_driver.py` | **驱动**. 用于 IPS 显示屏的自定义 SPI 驱动。 |
| `setup_database.py` | **工具**. 初始化 SQLite 数据库模式。 |
| `WIRING_GUIDE.md` | **文档**. 详细的引脚和接线图。 |
| `capsule_dispenser.db` | **数据**. 本地 SQLite 数据库。 |

---

## 🔮 未来规划

*   **摄像头集成**: 添加 Raspberry Pi Camera Module 3 用于面部 ID 或二维码解锁（二级认证）。
*   **Web 仪表板**: 开发本地 Flask/Django 界面，用于远程日志查看、用户管理和紧急解锁。
*   **库存与社交**: 
    *   跟踪每个通道的胶囊计数。
    *   “胶囊分享”功能：允许用户通过 App 将多余的胶囊提供给他人。
*   **外壳**: 设计全 3D 打印外壳，隐藏线路并将 Pi/屏幕安全固定在底座上。

---

## 📜 历史与决策

*   **2025-12 (S5)**: 
    *   **权限重构**: 引入了角色等级和物理通道分配逻辑。
    *   **交互优化**: 录入过程增加手指部位菜单选择（英语）并实时打印用户统计。
    *   **硬件兼容**: 将舵机控制从硬件 PWM 迁移到 **软件 PWM (`lgpio`)**。因为 Raspberry Pi 5 的硬件 PWM 时钟与冷却风扇共享，会导致冲突。同时实现了 **软启动** 逻辑。

## License
MIT License
