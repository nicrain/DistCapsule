# 智能胶囊分配器 - 项目状态文档 (S5.0)
**日期:** 2025-12-02
**平台:** Raspberry Pi 5 (Bookworm OS)

## 1. 项目概况
本项目旨在构建一个基于 Raspberry Pi 5 的离线智能胶囊分配器。系统通过生物识别（指纹/人脸）验证用户身份，并控制高扭矩舵机分配胶囊。

## 2. 核心架构决策

| 模块 | 决策/规格 | 状态 | 备注 |
| :--- | :--- | :--- | :--- |
| **主控** | Raspberry Pi 5 | ✅ 就绪 | 运行 Raspberry Pi OS (Bookworm) |
| **舵机控制** | **SG90 (9g)** / 硬件 PWM | ✅ 更新 | 已从 MG996R 替换为 SG90，参数已调整 |
| **数据库** | SQLite (`capsule_dispenser.db`) | ✅ 完成 | 已集成到主程序，支持用户查询和日志记录 |
| **指纹模块** | DY-50 (类 R307) | ✅ 完成 | 解决了 Pi 5 特有的串口映射问题 (`ttyAMA0`) |
| **供电** | 舵机独立 6V 供电 | ✅ 就绪 | 必须与 Pi 共地 |

---

## 3. 详细技术实现

### 3.1 舵机控制系统 (Servo System)
经过多次测试（软件 PWM -> lgpio -> 硬件 PWM），最终确定使用 Linux 内核级硬件 PWM 以确保绝对稳定。

*   **硬件型号**: SG90 (Micro Servo 9g) x 4
*   **接口分配**:
    *   **Servo 1**: GPIO 18 (PWM2)
    *   **Servo 2**: GPIO 12 (PWM0)
    *   **Servo 3**: GPIO 13 (PWM1)
    *   **Servo 4**: GPIO 19 (PWM3)
*   **系统配置 (Raspberry Pi 5 专用)**:
    由于 `config.txt` 在 Pi 5 上配置多路 PWM 存在兼容性问题，采用 **Systemd 服务 + pinctrl** 强制配置引脚模式。
    1.  **配置脚本**: `/usr/local/bin/setup_pwm_pins.sh`
        ```bash
        #!/bin/bash
        pinctrl set 12 a0  # PWM0
        pinctrl set 13 a0  # PWM1
        pinctrl set 18 a3  # PWM2 (注意: Pi 5 上 GPIO 18/19 需设为 Alt3)
        pinctrl set 19 a3  # PWM3
        ```
    2.  **自启动服务**: `/etc/systemd/system/pwm-setup.service` (开机自动运行上述脚本)
*   **校准参数 (SG90)**:
    *   **0度 (锁定)**: `500 us` (500,000 ns)
    *   **180度 (解锁)**: `2500 us` (2,500,000 ns)
*   **核心代码**: `servo_control.py`
    *   支持多通道初始化 `ServoController(channel=N)`。
    *   包含**自动防抖逻辑**：动作完成后立即切断 PWM 信号。

### 3.2 数据库设计 (Database)
*   **文件**: `capsule_dispenser.db`
*   **表结构**:
    1.  **Users**: 存储 `user_id`, `name`, `auth_level`, `finger_print_path` 等。
    2.  **Access_Logs**: 记录所有操作日志 (`timestamp`, `event_type`, `status`)。
    3.  **System_Settings**: 键值对配置 (如 `UNLOCK_DURATION=15`)。

### 3.3 指纹模块 (Fingerprint)
*   **硬件**: DY-50 (光学指纹模块, 6线制)。
*   **通信接口**: **UART0** (GPIO 14/15)。
*   **关键配置**:
    *   **端口映射**: 在 Pi 5 上必须使用 **`/dev/ttyAMA0`** (而非 `/dev/serial0` 或 `/dev/ttyAMA10`)。
    *   **系统设置**: 必须禁用 Serial Console (`sudo raspi-config nonint do_serial 2`)。
*   **接线方案**:
    *   **VCC (3v3)** -> Pin 1 (3.3V)
    *   **GND** -> Pin 6 (GND)
    *   **TX** -> Pin 10 (GPIO 15 RXD) **(交叉连接)**
    *   **RX** -> Pin 8 (GPIO 14 TXD) **(交叉连接)**
*   **状态**: 已成功连接，完成指纹录入，并集成到主程序。

---

## 4. 当前文件清单

```text
/home/cafe/projet/
├── main_demo.py           # [主程序] 演示 "指纹 -> 数据库验证 -> 舵机开锁" 的完整闭环
├── servo_control.py       # [核心] 最终封装的舵机控制类 (含硬件 PWM 和防抖)
├── fingerprint_enroll.py  # [工具] 指纹录入脚本
├── fingerprint_test.py    # [工具] 指纹连接测试脚本
├── setup_database.py      # [配置] 数据库初始化脚本
├── add_user.py            # [工具] 添加测试用户脚本
├── capsule_dispenser.db   # [数据] SQLite 数据库文件
├── WIRING_GUIDE.md        # [文档] 硬件接线指南
└── PROJECT_STATUS_S5.md   # [文档] 本文件
```

## 5. 下一步计划 (Next Steps)

1.  **摄像头集成 (Camera)**:
    *   配置 Pi Camera。
    *   实现人脸识别或二维码扫描，作为第二验证手段。
2.  **Web 管理界面**:
    *   搭建 Flask 服务器。
    *   实现远程查看日志、管理用户和远程开锁。
3.  **硬件封装**:
    *   设计外壳，将所有模块固定。
