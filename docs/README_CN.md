# 智能胶囊分配器 (Smart Capsule Dispenser)

[![Français](https://img.shields.io/badge/Language-Français-blue.svg)](../README.md)

**平台:** Raspberry Pi 5 (Bookworm OS) | **状态:** 稳定 (S5) | **最后更新:** 2026-01

这是一个安全的、支持生物识别的胶囊分配系统。它将标准的胶囊展示架转变为个性化的“信箱”系统，每个用户通过指纹或人脸认证拥有对特定存储通道的专属访问权。系统支持多用户录入、权限分级（管理员/普通用户）以及物理通道的动态分配。

---

## ✨ 主要功能

*   **多线程架构**: 人脸识别在后台线程运行，主线程负责 UI 刷新，确保倒计时**平滑线性**，无卡顿。
*   **智能电源与会话管理**: 
    *   30秒无操作自动休眠。
    *   物理按钮支持**唤醒及续命**功能（增加 30s）。
    *   安全保护：设置 5 分钟强制休眠上限。
*   **实时交互界面**: 1.3" IPS 屏幕实时显示时间、状态及**秒级倒计时**。倒计时少于 10s 时自动变红提醒。
*   **多用户角色管理**: 支持 1 个超级管理员和无限候补用户。物理通道（舵机）仅分配给活跃用户（最多 5 人）。

---

## 🛠 硬件架构

*   **控制器**: Raspberry Pi 5 (推荐 8GB)。
*   **执行器**: 5x SG90 微型舵机 (9g)。
*   **传感器**: DY-50 / R307 光学指纹模块 (UART) + Camera Module 3 (IMX708)。
*   **人机交互**: 1.3" IPS LCD (ST7789) + **唤醒按钮 (Wake-Up Button)**。
*   **供电**: 舵机必须使用 **外部 5V 电源** (必须与 Pi 共地)。

> **⚠️ 接线警告**: 不要直接从 Pi 的 GPIO 5V 引脚为 5 个舵机供电。请使用外部电源。详见 [WIRING_GUIDE.md](WIRING_GUIDE.md)。

---

## 🚀 安装与设置

### 1. 系统依赖
```bash
sudo apt-get update
sudo apt-get install python3-serial python3-pip python3-lgpio python3-pil python3-rpi.gpio
```

### 2. Python 库
```bash
sudo pip3 install adafruit-circuitpython-fingerprint st7789
```

### 3. 人脸识别环境 (Pi 5 Bookworm)

**前提条件: 安装 GStreamer 插件 (Pi 5 必须)**
```bash
sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-libcamera gstreamer1.0-tools
```

**安装 OpenCV 与 Face Recognition**
```bash
sudo apt update
sudo apt install python3-opencv python3-face-recognition
```

### 4. 网络配置 (离线热点)
为了让手机 App 能在没有外网的情况下控制 Pi，同时保持手机自身的 4G/5G 上网，请配置“无网关”热点模式：

**开启热点:**
```bash
sudo ./tools/setup_manual_hotspot.sh
```
*   这将创建 Wi-Fi `DistCapsule_Box` (IP: 192.168.4.1)。手机连接后会自动保持 4G 上网。

**关闭热点 (恢复正常 Wi-Fi):**
```bash
sudo ./tools/stop_hotspot.sh
```

---

## 📖 使用指南

### 1. 初始化系统
创建数据库表及初始化配置。
```bash
python3 tools/setup_database.py
```

### 2. 管理指纹用户
启动指纹管理工具，录入管理员或分配舵机通道。
```bash
sudo python3 tools/fingerprint_enroll.py
```

### 3. 录入人脸
为现有用户录入人脸数据（支持 SSH 无头模式自动录入）：
```bash
python3 tools/face_enroll.py
```

### 4. 硬件测试
验证所有组件（舵机、屏幕、指纹、相机）是否工作正常。
```bash
sudo python3 tools/hardware_test.py
```

### 5. 运行主程序
启动系统。系统默认进入 **休眠模式 (Sleep Mode)**（屏幕关闭）以节省能源。
*   **唤醒**: 按下 **物理唤醒按钮**。
*   **自动休眠**: 无操作 30 秒后自动重新进入休眠。

```bash
sudo python3 main.py
```

### 6. 设置开机自启
```bash
./tools/install_service.sh
```

---

## 📂 项目结构

| 文件/目录 | 描述 |
| :--- | :--- |
| `main.py` | **核心应用**. 处理认证循环、UI 更新和业务逻辑。 |
| `hardware/` | **硬件驱动**. 包含舵机、屏幕、人脸识别系统等封装类。 |
| `tools/` | **工具脚本**. 包含安装、测试、录入等辅助脚本。 |
| `docs/` | **文档**. 接线指南、中文说明、归档文档及**演示文稿 (slides/)**。 |
| `capsule_dispenser.db` | **数据库**. 存储用户信息、指纹 ID 及人脸特征。 |

---

## 📜 历史与决策

*   **2025-12 (S5)**: 
    *   **数据库自动迁移**: 优化 `setup_database.py`，实现旧版数据库结构的自动检测与无损升级（自动补充人脸字段）。
    *   **多线程重构**: 引入 Python `threading` 和 `queue` 模块，将 AI 识别与 UI 刷新分离，极大提升交互流畅度。
    *   **响应性能优化**: 彻底移除阻塞式延迟 (`time.sleep`)，引入非阻塞按钮检测和统一时间戳同步。
    *   **全量 lgpio 迁移**: 移除 `RPi.GPIO`，所有 GPIO 操作（舵机、按钮）统一使用 `lgpio`，解决 Pi 5 硬件冲突。
    *   **UI 体验升级**: 增加秒级动态倒计时和颜色预警。
    *   **权限与分配**: 实现用户角色分级及物理通道的动态绑定。

---## License
MIT License