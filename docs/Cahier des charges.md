## 智能胶囊分配器项目规格说明书 (Cahier des Charges - V1.1 As-Built)

### I. 整体目标与概念 (Objectifs Généraux)

| 编号 | 项目名称 | 描述 |
| :--- | :--- | :--- |
| **P1.0** | **项目名称** | DistCapsule: Distributeur de Capsules Intelligent (智能胶囊分配器) |
| **P1.1** | **核心理念** | 将商用胶囊展示架改造为具有**生物识别身份认证**和**通道访问控制**功能的个人专属存储系统。 |
| **P1.2** | **架构演进** | V1.1 版本已完全摒弃单片机辅助（Arduino/ESP32），采用 **Raspberry Pi 5 全托管架构**，通过 `lgpio` 直接驱动硬件，配合 FastAPI 提供移动端服务。 |
| **P1.3** | **用户支持** | 支持多用户管理，每位用户可绑定 1 个物理通道，并通过 Android App 进行可视化管理。 |

### II. 功能需求 (Exigences Fonctionnelles)

| 编号 | 模块 | 功能描述 | 状态 |
| :--- | :--- | :--- | :--- |
| **F2.1** | **用户管理** | 数据库 (SQLite) 存储用户 ID、Token、权限 (Admin/User) 及生物识别状态。 | ✅ V1.0 |
| **F2.1.1** | **App 注册/登录** | Android App 基于 UUID Token 实现**一键注册**与**自动登录**。 | ✅ V1.1 |
| **F2.1.2** | **通道分配** | 管理员可通过 App 的可视化界面 (Vivid UI) 为用户分配或收回物理通道 (1-5)。 | ✅ V1.1 |
| **F2.2** | **人脸认证** | Pi 5 + Camera Module 3 实时识别人脸，比对特征向量 (Tolerance 0.35)。 | ✅ V1.0 |
| **F2.3** | **指纹认证** | DY-50 光学指纹模块 (UART) 实现秒级解锁，含 Watchdog 自愈机制防止硬件死锁。 | ✅ V1.1 |
| **F2.4** | **通道控制** | 认证成功后，SG90 舵机自动开启对应通道闸门，3秒后自动关闭。 | ✅ V1.0 |
| **F2.5** | **远程指令** | App 可通过 Wi-Fi (HTTP API) 发送远程解锁或触发录入模式指令。 | ✅ V1.0 |
| **F2.6** | **反馈交互** | 1.3" IPS 屏幕实时显示欢迎信息、操作提示及错误代码；App 端同步显示状态。 | ✅ V1.0 |

### III. 技术架构与硬件配置 (Architecture Technique)

| 编号 | 约束 | 描述 |
| :--- | :--- | :--- |
| **T3.1** | **主控平台** | **Raspberry Pi 5 (8GB)**。负责所有业务逻辑、视觉处理、API 服务及 GPIO 控制。 |
| **T3.2** | **IO 控制** | **`lgpio` (Python)**。替代 RPi.GPIO，解决 Pi 5 RP1 芯片的兼容性问题，实现 Soft-PWM 舵机控制。 |
| **T3.3** | **通信协议** | **HTTP (FastAPI)**。替代 MQTT，简化架构，提供 RESTful 接口供 Android 调用。 |
| **T3.4** | **供电策略** | **双路供电**：Pi 5 使用官方 27W USB-C 电源；舵机使用**独立 5V/4A 电源适配器**（共地）。 |
| **T3.5** | **生物识别** | 指纹 (UART /dev/ttyAMA0) + 人脸 (OpenCV/Face_Recognition)。 |

---

## 硬件清单 (Liste Matériel Finalisée)

### 一、核心组件 (Unité Centrale)

| 组件 | 规格 | 用途 |
| :--- | :--- | :--- |
| **Raspberry Pi 5** | 8GB RAM | 核心计算单元 |
| **Micro SD** | 32GB Class 10 | 操作系统 (Bookworm) |
| **Camera Module 3** | Wide Angle | 人脸数据采集与识别 |
| **LCD Screen** | 1.3" ST7789 SPI | 本地状态显示 |
| **Fingerprint Sensor** | DY-50 / R307 (UART) | 指纹采集与比对 |
| **Button** | Momentary Push Button | 系统唤醒 (GPIO 26) |

### 二、执行机构 (Actionneurs)

| 组件 | 规格 | 用途 |
| :--- | :--- | :--- |
| **SG90 Servo** | 180° Micro Servo (x5) | 控制 5 个胶囊通道闸门 |
| **3D Printed Parts** | PLA (Custom Design) | 舵机支架、闸门、传感器外壳 |

### 三、电源 (Alimentation)

| 组件 | 规格 | 备注 |
| :--- | :--- | :--- |
| **Pi Power Supply** | USB-C PD 27W | 树莓派官方电源 |
| **Servo Power** | 5V 4A DC Adapter | **独立供电**，防止电流反噬 |
| **DC Jack** | 5.5x2.1mm Socket | 接入外部 5V 电源 |

### 四、软件栈 (Software Stack)

*   **OS**: Raspberry Pi OS (Bookworm)
*   **Backend**: Python 3.11, FastAPI, SQLite, Pydantic
*   **Hardware**: lgpio, opencv-python, adafruit-circuitpython-fingerprint
*   **Mobile**: Android Native (Java), Retrofit, Material Design 3
