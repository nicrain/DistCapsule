# 📱 DistCapsule Android App - 技术规格说明书 (V1.1)

**项目名称**: DistCapsule (Smart Capsule Dispenser)
**适用平台**: Android (Min SDK 24+)
**后端环境**: Raspberry Pi 5 (Python FastAPI)
**文档状态**: 已简化 (移除实时视频与远程开锁)

---

## 1. 项目概述 (Overview)

本应用是 DistCapsule 系统的管理终端，主要用于**用户信息管理**和**访问审计**。App 通过局域网/热点连接树莓派，允许管理员在手机上完成新用户的资料录入，并触发机器端的生物识别采集流程。

---

## 2. 功能模块划分

### 2.1 核心功能 (Phase 1)
*   **连接设置**: 允许手动配置树莓派 API 地址 (默认 `http://192.168.4.1:8000`)。
*   **用户列表**: 查看所有用户详情（ID、权限、分配通道、激活状态）。
*   **日志系统**: 查看系统历史访问记录（谁在何时通过何种方式尝试开锁）。

### 2.2 用户注册流程 (Phase 2)
App 充当注册的“遥控器”：
1.  **资料填写**: 在 App 端输入姓名、权限、目标通道。
2.  **触发采集**: 点击“开始采集人脸”或“开始采集指纹”。
3.  **机器反馈**: 树莓派硬件执行采集，App 接收采集成功/失败的状态反馈（无需在手机端看画面）。

---

## 3. API 接口规范

**Base URL**: `http://<PI_IP>:8000`

### 3.1 用户管理

#### A. 获取用户列表
*   **GET** `/users`
*   **返回**: `List<User>` (包含 ID, Name, AuthLevel, Channel, IsActive)

#### B. 注册用户资料 (初步)
*   **POST** `/users/enroll`
*   **Body**: `{"name": "string", "auth_level": int, "assigned_channel": int}`
*   **返回**: `{"status": "success", "user_id": int}`

### 3.2 硬件触发指令 (注册用)

#### A. 触发人脸录入
*   **POST** `/hardware/enroll_face`
*   **Body**: `{"user_id": int}`
*   **逻辑**: 告知树莓派：“请让 ID 为 X 的用户看向摄像头”。
*   **返回**: `{"status": "success", "message": "Face captured"}` 或 `{"status": "error"}`

#### B. 触发指纹录入
*   **POST** `/hardware/enroll_finger`
*   **Body**: `{"user_id": int}`
*   **逻辑**: 告知树莓派：“请让 ID 为 X 的用户按下指纹”。
*   **返回**: `{"status": "success"}`

### 3.3 审计日志

#### A. 获取日志
*   **GET** `/logs?limit=50`
*   **返回**: `List<Log>` (Timestamp, UserID, EventType, Status)

---

## 4. Android 开发注意事项

1.  **网络隔离**: 手机连接 Pi 热点时，Android 可能会因为该 Wi-Fi 无法上网而自动切回移动数据。开发时需在 App 内通过 `ConnectivityManager` 强制绑定网络到 Wi-Fi，或提醒用户保持 Wi-Fi 连接。
2.  **异步反馈**: 硬件采集（人脸/指纹）可能需要几秒钟。App 端在发起 `/hardware/enroll_...` 请求时，应显示进度条（Loading），直到后端返回结果。
3.  **配置持久化**: 使用 `SharedPreferences` 或 `DataStore` 存储树莓派的 IP 地址，避免每次打开 App 重新输入。

---
*文档更新日期: 2026-01-14*
