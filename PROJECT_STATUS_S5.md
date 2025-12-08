# 智能胶囊分配器 - 项目状态文档 (S5.1)
**日期:** 2025-12-08
**平台:** Raspberry Pi 5 (Bookworm OS)

## 1. 项目概况
本项目旨在构建一个基于 Raspberry Pi 5 的离线智能胶囊分配器。系统通过生物识别（指纹/人脸）验证用户身份，并控制高扭矩舵机分配胶囊。

## 2. 核心架构决策

| 模块 | 决策/规格 | 状态 | 备注 |
| :--- | :--- | :--- | :--- |
| **主控** | Raspberry Pi 5 | ✅ 就绪 | 运行 Raspberry Pi OS (Bookworm) |
| **舵机控制** | **SG90 (9g)** / 软件 PWM | ✅ 更新 | **关键变更**: 从硬件 PWM 迁移到软件 PWM (`lgpio`) 以解决与系统风扇的冲突 |
| **显示屏** | **1.3" IPS (ST7789)** | ✅ 完成 | 240x240, SPI 接口, 自定义驱动 `st7789_driver.py` |
| **数据库** | SQLite (`capsule_dispenser.db`) | ✅ 完成 | 已集成到主程序，支持用户查询和日志记录 |
| **指纹模块** | DY-50 (类 R307) | ✅ 完成 | 解决了 Pi 5 特有的串口映射问题 (`ttyAMA0`) |
| **散热** | 系统风扇 (Active Cooler) | ✅ 恢复 | 由系统内核自动控制，不再占用 GPIO 19 |

---

## 3. 详细技术实现

### 3.1 舵机控制系统 (Servo System)
**重大架构变更 (2025-12-08)**:
由于 Raspberry Pi 5 的硬件 PWM 模块与系统风扇驱动 (`pwm-fan`) 共享时钟源，当风扇启动时，PWM 频率会被强制锁定在 ~25kHz，导致舵机 (需要 50Hz) 失效。
因此，我们将舵机控制迁移到了 **软件 PWM (Software PWM)**，使用 `lgpio` 库直接控制 GPIO 电平。

*   **硬件型号**: SG90 (Micro Servo 9g) x 4
*   **接口分配**:
    *   **Servo 1**: GPIO 18
    *   **Servo 2**: GPIO 12
    *   **Servo 3**: GPIO 13
    *   **Servo 4**: GPIO 19 (已恢复)
*   **系统配置**:
    不再需要复杂的 `config.txt` PWM 覆盖。只需将引脚配置为普通输出模式。
    1.  **配置脚本**: `/usr/local/bin/setup_pwm_pins.sh`
        ```bash
        #!/bin/bash
        # 将 GPIO 12, 13, 18, 19 设置为普通输出模式 (Output)
        pinctrl set 12 op
        pinctrl set 13 op
        pinctrl set 18 op
        pinctrl set 19 op
        ```
*   **核心代码**: `servo_control.py`
    *   使用 `lgpio` 库生成 50Hz PWM 信号。
    *   **防抖逻辑**: 动作完成后立即关闭 PWM 输出 (`duty=0`)，防止舵机抖动并节省电力。

### 3.2 显示系统 (Display)
*   **硬件**: 1.3寸 IPS 屏幕 (ST7789 驱动芯片)。
*   **驱动**: 自研驱动 `st7789_driver.py`。
    *   使用 `spidev` 直接操作 SPI 总线。
    *   解决了第三方库在 Pi 5 上无法初始化的问题。
*   **功能**: 显示系统状态、指纹提示、时间等。
*   **UI 优化**:
    *   安装了 `fonts-dejavu-core` 以支持矢量字体。
    *   字体大小已调整为 **32px (标题)** 和 **22px (正文)**，提升可读性。

### 3.3 数据库设计 (Database)
*   **文件**: `capsule_dispenser.db`
*   **表结构**:
    1.  **Users**: 存储 `user_id`, `name`, `auth_level`, `finger_print_path` 等。
    2.  **Access_Logs**: 记录所有操作日志 (`timestamp`, `event_type`, `status`)。
    3.  **System_Settings**: 键值对配置 (如 `UNLOCK_DURATION=15`)。

### 3.4 指纹模块 (Fingerprint)
*   **硬件**: DY-50 (光学指纹模块, 6线制)。
*   **通信接口**: **UART0** (GPIO 14/15)。
*   **关键配置**:
    *   **端口映射**: 在 Pi 5 上必须使用 **`/dev/ttyAMA0`**。
    *   **系统设置**: 必须禁用 Serial Console。

---

## 4. 当前文件清单

```text
/home/cafe/projet/
├── main_demo.py           # [主程序] 集成指纹、屏幕、舵机 (软件 PWM)
├── servo_control.py       # [驱动] 基于 lgpio 的软件 PWM 舵机控制器
├── st7789_driver.py       # [驱动] 自研 ST7789 屏幕驱动
├── fingerprint_enroll.py  # [工具] 指纹录入脚本
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
