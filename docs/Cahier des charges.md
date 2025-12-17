## 智能胶囊分配器项目规格说明书(Cahier des Charges)

### I. 整体目标与概念 (Objectifs Généraux)


| 编号 | 项目名称 | 描述 |
| :--- | :--- | :--- |
| **P1.0** | **项目名称** | Projet AAA: Distributeur de Capsules Intelligent (智能胶囊分配器) |
| **P1.1** | **核心理念** | 将商用胶囊**多通道展示架**改造为具有身份认证和**通道访问控制**功能的个人**专属通道系统**（实现个人信箱功能）。 |
| **P1.2** | **用户支持** | 系统需支持 **5 个独立用户**，每用户对应展示架上的 **1 个垂直分配通道 (Canal de Distribution)**。 |
| **P1.3** | **通道访问** | 认证成功后，系统需驱动相应的闸门，允许用户在**限定时间内**自由地 **存入或取出** 胶囊。 |
| **P1.4** | **设计简化** | 利用现成的 **5 通道胶囊展示架**，机械设计重点仅在于**通道出口**的 **锁定与解锁机构**。 |

### II. 功能需求 (Exigences Fonctionnelles)


| 编号 | 模块 | 功能描述 | 优先度 |
| :--- | :--- | :--- | :--- |
| **F2.1** | **用户管理** | Pi 需存储并管理至少 5 个用户的 ID、权限和认证信息（指纹/人脸模板）。 | 必须 |
| **F2.1.1** | **App 注册引导** | Android App 需提供新用户**注册引导流程**，包括采集**人脸/指纹模板**并将其安全存储在 Pi 数据库中。 | 必须 |
| **F2.1.2** | **通道命名配置** | Android App 需允许用户为其分配的通道设置**个性化名称**（例如：“我的特浓咖啡”）。 | 必须 |
| **F2.1.3** | **超时时间设置** | Android App 需允许用户自定义其通道的**自动关闭延迟时间**（$T$ 秒），该设置需存储在 Pi 数据库。 | 必须 |
| **F2.2** | **人脸认证** | 用户通过摄像头进行人脸扫描，Pi 需在本地完成认证并在 **3 秒内** 完成身份确认。 | 必须 |
| **F2.3** | **指纹认证** | 用户通过指纹模块进行指纹扫描，Pi 需在本地完成认证并在 **2 秒内** 完成身份确认。 | 必须 |
| **F2.4** | **QR 码认证** | Android App 扫码并发送 QR 码信息给 Pi，Pi 进行认证。 | 必须 |
| **F2.5** | **通道解锁** | 认证成功后，系统需驱动相应的 **SG90 舵机**，将通道闸门移动到**完全解锁**位置。 | 必须 |
| **F2.6** | **通道自动锁定** | Pi 负责计时。解锁后，通道需保持开启 **用户设定的限定时间 ($T$)**，时间结束后自动驱动舵机恢复**锁定状态**。 | 必须 |
| **F2.7** | **App 通信** | Android App 需通过 **本地 Wi-Fi/MQTT 协议** 实时与 Pi 交换数据和指令。 | 必须 |
| **F2.8** | **状态反馈** | App 需实时显示所有通道的锁定/解锁状态、系统是否在线以及认证结果。 | 必须 |
| **F2.8.1** | **屏幕提示** | **OLED 屏幕** 需显示系统状态、唤醒指令、认证结果（成功/失败）和通道关闭倒计时提示。 | 必须 |
| **F2.9** | **控制隔离** | Pi 和舵机控制逻辑必须通过 **串行通信** 进行隔离，确保舵机运动不干扰 Pi 操作系统。 | 必须 |

### III. 技术要求与约束 (Exigences Techniques)


| 编号 | 约束 | 描述 |
| :--- | :--- | :--- |
| **T3.1** | **主控平台** | **Raspberry Pi 5** (需具备 $5A$ 供电和强大的运算能力)。 |
| **T3.2** | **运动控制** | **Arduino 或 ESP32** (用于精确控制 5 个 SG90 舵机，实现锁定/解锁两点定位)。 |
| **T3.3** | **供电** | 需使用一个高质量、高电流的 **5V / $5.0A$** 的独立稳压电源，以确保 Pi 5 和所有舵机的稳定运行。 |
| **T3.4** | **机械设计** | 5 套独立的 **3D 打印闸门 (Gate)** 和 SG90 支架，闸门设计必须确保**通道的完全打开和完全关闭**。 |
| **T3.5** | **通信协议** | Pi ↔ App 使用 **MQTT 协议**；Pi ↔ Arduino 使用**串行通信协议**。 |
| **T3.6** | **传感器唤醒** | **摄像头和认证程序**必须在 Pi 处于休眠待机状态时**保持关闭**，只有在用户按下 **唤醒按钮 (H10.0)** 后才启动。 | 必须 |

---

## 硬件采购清单 (Liste d'Achat Matériel)

### 一、核心处理与控制 (Unité Centrale et Contrôle)

| 编号 | 组件 | 规格/型号建议 | 数量 | 主要用途 | 采购备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A1.0** | **主控计算机** | **[Raspberry Pi 5 8GB ](https://letmeknow.fr/fr/cartes-officielles/3354-raspberry-pi-5-8gb-5056561803319.html)** | 1 | 认证、数据库、网络中心 | |
| **A1.1** | **运动控制器** | [ADAFRUIT ESP32-S3 4MB FLASH 2MB PSRAM](https://letmeknow.fr/fr/feather/2849-adafruit-feather-esp32-s3-4mb-flash-2mb-psram-652733343048.html) | 1 | 精确控制 5 个舵机 | 通过 USB Serial 连接 Pi |
| **A1.2** | **主动散热风扇** | [Refroidisseur Active Cooler Raspberry Pi 5](https://letmeknow.fr/fr/autres/3421-refroidisseur-active-cooler-raspberry-pi-5-5056561803357.html) | 1 | 保证 Pi 5 高负荷下稳定运行 | |
| **A1.3** | **存储卡** | [Carte Micro-SD 32Gb Ultra SanDisk Classe 10](https://letmeknow.fr/fr/raspberry-pi/3541-carte-micro-sd-32gb-ultra-sandisk-classe-10-619659134785.html) | 1 | Pi 操作系统和数据存储 | |

### 二、电源与基础布线 (Alimentation et Infrastructure)

| 编号 | 组件 | 规格/型号建议 | 数量 | 主要用途 | 采购备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A2.0** | **Pi 主电源适配器** | **5V / 5.0A** ([Alimentation officielle Raspberry Pi 5 27W USB-C](https://letmeknow.fr/fr/raspberry-pi/3332-alimentation-officielle-raspberry-pi-5-27w-usb-c-5056561803401.html)) | 1 | 专供 Pi 5 和 ESP32 (通过 USB L4.0 供电)。 | **关键组件！** |
| **A2.1** | **舵机独立电源** | [Boîtier coupleur de piles 4 AA (R6) avec interrupteur](https://letmeknow.fr/fr/coupleurs/613-boitier-coupleur-de-piles-4-aa-r6-avec-interrupteur-0711978441602.html) | 1 | **为 5 个 SG90 舵机 提供独立 $6\text{V}$ 供电，实现电流隔离。** | |
| **A2.2** | **面包板** | [GRAND BREADBOARD(830 trous)](https://letmeknow.fr/fr/cablages/258-grande-breadboard-3614408217068.html) | 1 | 舵机电源分发、地线汇集和信号跳线中心。 | |

### 三、输入与输出外设 (Périphériques I/O)

| 编号 | 组件 | 规格/型号建议 | 数量 | 主要用途 | 采购备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A3.0** | **摄像头** | **[Raspberry Pi Camera Module 3](https://letmeknow.fr/fr/raspberry-pi/2907-module-camera-v3-raspberry-pi-5056561803241.html)** | 1 | 人脸识别和 QR 码扫描 | |
| **A3.1** | **指纹识别模块** | [Module de reconnaissance d'empreintes digitales FPM10A](https://letmeknow.fr/fr/capteurs/1992-module-de-reconnaissance-d-empreintes-digitales-fpm10a-642613441629.html) | 1 | 指纹认证 | |
| **A3.2** | **RFID/NFC 模块(可选)** | **PN532 或 RC522 模块** | 1 | RFID/NFC 认证（可选） | |
| **A3.3** | **状态显示屏** | [Afficheur LCD 2 lignes 16 caractères vert I2C](https://letmeknow.fr/fr/ecrans/167-afficheur-16-caracteres-2-lignes-i2c-vert-4894479454558.html) | 1 | I2C 接口接入 Pi 5 的 GPIO，显示状态。 | |
| **A3.4** | **唤醒按钮** | [Adafruit Bouton Poussoir Led Vert 16 mm Momentané](https://letmeknow.fr/fr/boutons-et-interrupteurs/3834-adafruit-bouton-poussoir-led-vert-16-mm-momentane-0711978444146.html) | 1 | 连接 Pi 5 的 GPIO，用于从休眠模式唤醒系统。 | |

### 四、执行与机械结构 (Actionneurs et Mécanique)

| 编号 | 组件 | 规格/型号建议 | 数量 | 主要用途 | 采购备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A4.0** | **胶囊展示架主体** | [Rangement Capsule](https://amzn.eu/d/jfPP7i2) | 1 | 机械改装基础 | |
| **A4.1** | **动作执行器** | **[SG90 Nano Servo (微型舵机)](https://letmeknow.fr/fr/moteurs-et-servo-moteurs/30-micro-servo-moteur-sg90-nano-4894479459935.html)** | 5 | 驱动 5 个胶囊通道的锁定/解锁闸门 | |
| **A4.2** | **3D 打印材料** | PLA/PETG 耗材 | 适量 | 打印舵机支架和通道闸门 | |

### 五、连接线材 (Câbles)

| 编号 | 组件 | 规格/型号建议 | 数量 | 主要用途 | 采购备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A5.0** | **[Nappe de 40 jumpers mâle - mâle 20cm](https://letmeknow.fr/fr/cablages/492-nappe-de-40-jumpers-male-male-20cm-0711978444962.html)** | **主要采购 $20\text{cm}$ 长度。** | **1** | **核心连接线：** 连接 **舵机** (母头) 到 **面包板孔** (母头)。 | **用于舵机连接时需加固。** |
| **A5.1** | **[Nappe de 40 jumpers mâle - femelle 20cm](https://letmeknow.fr/fr/cablages/96-nappe-de-40-jumpers-male-femelle-20cm-6915671063107.html)** | **主要采购 $10\text{cm}$ 到 $20\text{cm}$ 长度。** | **1** | 主控连接：用于连接 **Pi 5/ESP32** (公头) 到 **传感器** 或 **面包板跳线**。 | |
| **A5.2** | **[Cable USB-C](https://letmeknow.fr/fr/cablages/2926-cable-usb-c-642613923354.html)** | 高速数据线 | 1 | 连接 **Raspberry Pi 5** 和 **ESP32-S3**（供电 + USB 虚拟串口通信）。 | |