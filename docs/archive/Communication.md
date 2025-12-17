##  Pi ↔ Arduino 串行通信协议设计

### 协议目标

1.  **指令清晰：** Pi 向 Arduino 发送明确的指令（如“打开 3 号通道”）。
2.  **反馈可靠：** Arduino 向 Pi 返回执行结果（如“3 号通道已打开”），确保 Pi 收到确认。

### 1. 指令格式 (Pi → Arduino)

Pi 发送的指令将是一个短小的字符串，包含 **[动作]** 和 **[通道编号]**，并以 **换行符 `\n`** 结束，以便 Arduino 轻松读取。

| 动作代码 | 描述 | 示例指令 (Pi 发送) | Arduino 解释 |
| :--- | :--- | :--- | :--- |
| **OPEN** | 请求打开指定通道。 | `OPEN:3\n` | 驱动 3 号通道的 SG90 舵机到 **解锁角度**。 |
| **LOCK** | 请求关闭（锁定）指定通道。 | `LOCK:5\n` | 驱动 5 号通道的 SG90 舵机到 **锁定角度**。 |
| **INIT** | 系统启动或重置时，请求 Arduino 将所有通道初始化为锁定状态。 | `INIT:ALL\n` | 驱动所有 5 个 SG90 舵机到 **锁定角度**。 |

### 2. 反馈格式 (Arduino → Pi)

Arduino 在执行完 Pi 的指令后，将返回一个确认消息。

| 动作代码 | 描述 | 示例反馈 (Arduino 发送) | Pi 解释 |
| :--- | :--- | :--- | :--- |
| **OK\_OPEN** | 确认通道已成功打开。 | `OK_OPEN:3\n` | Pi 可以继续计时，并通过 MQTT 更新 App 状态。 |
| **OK\_LOCK** | 确认通道已成功锁定。 | `OK_LOCK:5\n` | Pi 通过 MQTT 更新 App 状态。 |
| **ERROR** | 执行指令时发生错误（例如舵机未连接）。 | `ERROR:2\n` | Pi 记录错误并向 App 发送警告。 |
| **ACK\_INIT** | 确认所有通道已初始化锁定。 | `ACK_INIT:ALL\n` | Pi 可以开始运行主认证循环。 |

### 3. 通信流程示例：开锁

1.  **App → Pi (MQTT):** 用户认证成功，App 发送开锁请求（例如 3 号通道）。
2.  **Pi 内部逻辑:** Pi 启动 **10 秒计时器**。
3.  **Pi → Arduino (Serial):** Pi 发送指令 $\rightarrow$ `OPEN:3\n`
4.  **Arduino 执行:** Arduino 驱动 3 号舵机到解锁角度。
5.  **Arduino → Pi (Serial):** Arduino 返回确认 $\rightarrow$ `OK_OPEN:3\n`
6.  **Pi 计时结束:** 10 秒后，Pi 发送关闭指令 $\rightarrow$ `LOCK:3\n`
7.  **Arduino 执行:** Arduino 驱动 3 号舵机到锁定角度。
8.  **Arduino → Pi (Serial):** Arduino 返回确认 $\rightarrow$ `OK_LOCK:3\n`

### 4. 软件实现要点

* **Pi (Python):** 使用 `pyserial` 库来发送和接收数据。
* **Arduino (C++):** 使用内置的 `Serial.readStringUntil('\n')` 函数来接收 Pi 的指令，并使用 `Servo.write()` 函数来控制舵机角度。

---