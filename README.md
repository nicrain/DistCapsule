# Smart Capsule Dispenser (智能胶囊分配器 / Distributeur de Capsules Intelligent)

**Platform:** Raspberry Pi 5 (Bookworm OS) | **Status:** Stable (S5) | **Last Updated:** 2025-12

[中文]
这是一个安全的、支持生物识别的胶囊分配系统。它将标准的胶囊展示架转变为个性化的“信箱”系统，每个用户通过指纹认证拥有对特定存储通道的专属访问权。

[Français]
Un système de distribution de capsules sécurisé et activé par biométrie. Il transforme un présentoir à capsules standard en un système de "boîte aux lettres" personnalisé où chaque utilisateur a un accès exclusif à un canal de stockage spécifique via une authentification par empreinte digitale.

---

## 主要功能 / Fonctionnalités Clés

### [中文]
*   **生物识别安全**: 集成 DY-50 (兼容 R307) 光学指纹传感器，实现快速用户识别。
*   **精确控制**: 使用 **软件 PWM (`lgpio`)** 控制 5 个 SG90 舵机，专为 Raspberry Pi 5 优化，避免与系统风扇产生硬件 PWM 冲突。
*   **交互式 UI**: 1.3英寸 IPS 显示屏 (ST7789) 提供实时状态、反馈和用户提示。
*   **本地数据库**: 基于 SQLite 的用户管理和访问日志记录。
*   **稳健设计**: 包含防抖动逻辑（运动后自动切断）和针对串行通信的强大错误处理。

### [Français]
*   **Sécurité Biométrique**: Capteur d'empreintes digitales optique DY-50 (compatible R307) intégré pour une identification rapide de l'utilisateur.
*   **Contrôle de Précision**: Contrôle de 5 servomoteurs SG90 utilisant le **PWM Logiciel (`lgpio`)**, spécifiquement optimisé pour le Raspberry Pi 5 afin d'éviter les conflits de PWM matériel avec le ventilateur du système.
*   **Interface Utilisateur Interactive**: Écran IPS 1,3" (ST7789) fournissant un état en temps réel, des retours et des invites utilisateur.
*   **Base de Données Locale**: Gestion des utilisateurs et journalisation des accès via SQLite.
*   **Conception Robuste**: Inclut une logique anti-gigue (coupure automatique après mouvement) et une gestion robuste des erreurs pour les communications série.

---

## 硬件架构 / Architecture Matérielle

*   **控制器 (Contrôleur)**: Raspberry Pi 5 (推荐 8GB / Recommandé 8Go).
*   **执行器 (Actionneurs)**: 5x SG90 微型舵机 (9g) / 5x Micro servomoteurs SG90 (9g).
*   **传感器 (Capteur)**: DY-50 / R307 光学指纹模块 (UART) / Module capteur d'empreintes optique DY-50 / R307 (UART).
*   **显示器 (Écran)**: 1.3" IPS LCD (240x240) 配备 ST7789 驱动 (SPI) / LCD IPS 1.3" (240x240) avec pilote ST7789 (SPI).
*   **机械底座 (Base Mécanique)**: 定制 3D 打印组件 - 机械结构将采用定制设计并进行 3D 打印。初始草稿可在 `3D/` 目录中找到。
    *   *Composants imprimés en 3D sur mesure - La structure mécanique sera conçue sur mesure et imprimée en 3D. Les premières ébauches sont disponibles dans le répertoire `3D/`.*
*   **电源 (Alimentation)**:
    *   Pi 5: 官方 27W USB-C 电源。 / Alimentation officielle USB-C 27W.
    *   舵机 (Servos): **外部 5V 电源** (必须与 Pi 共地)。 / **Alimentation externe 5V** (Masse commune avec le Pi obligatoire).

> **⚠️ 接线警告 / Avertissement de Câblage**: 
> [中文] 不要直接从 Pi 的 GPIO 5V 引脚为 5 个舵机供电。请使用外部电源。详见 [WIRING_GUIDE.md](WIRING_GUIDE.md)。
>
> [Français] Ne pas alimenter 5 servomoteurs directement depuis la broche 5V du GPIO du Pi. Utilisez une source d'alimentation externe. Voir [WIRING_GUIDE.md](WIRING_GUIDE.md) pour les détails de câblage.

---

## 安装与设置 / Installation et Configuration

### 1. 系统依赖 / Dépendances Système
[中文] 该项目依赖 `lgpio` 进行 Pi 5 的 GPIO 控制，以及 `pyserial` 用于传感器通信。
[Français] Le projet dépend de `lgpio` pour le contrôle GPIO sur le Pi 5 et de `pyserial` pour le capteur.

```bash
sudo apt-get update
sudo apt-get install python3-serial python3-pip python3-lgpio python3-pil python3-rpi.gpio
```

### 2. Python 库 / Bibliothèques Python
```bash
sudo pip3 install adafruit-circuitpython-fingerprint st7789
```

### 3. 硬件配置 / Configuration Matérielle
*   **UART**: 通过 `sudo raspi-config` 启用串行端口硬件，但禁用登录 shell。Pi 5 上指纹模块使用 `/dev/ttyAMA0` (GPIO 14/15)。
    *   *Activez le matériel du port série via `sudo raspi-config`, mais désactivez le shell de connexion. Le module d'empreintes digitales utilise `/dev/ttyAMA0` (GPIO 14/15) sur le Pi 5.*
*   **SPI**: 通过 `sudo raspi-config` 启用 SPI 接口用于显示屏。
    *   *Activez l'interface SPI via `sudo raspi-config` pour l'écran.*

---

## 使用指南 / Guide d'Utilisation

### 1. 初始化系统 / Initialiser le Système
[中文] 创建用于用户和日志的数据库表。
[Français] Créer les tables de base de données pour les utilisateurs et les journaux.

```bash
python3 setup_database.py
```

### 2. 录入用户 (指纹) / Enrôler des Utilisateurs (Empreinte Digitale)
[中文] 注册新用户并采集指纹。按照屏幕提示操作。
[Français] Enregistrer un nouvel utilisateur et capturer son empreinte digitale. Suivez les instructions à l'écran.

```bash
sudo python3 fingerprint_enroll.py
```
*   *[中文] 注意：请确保先初始化数据库。*
*   *[Français] Remarque : Assurez-vous d'abord que la base de données est initialisée.*

### 3. 硬件测试 / Test Matériel
[中文] 运行集成测试工具以验证所有组件（舵机、屏幕、指纹）是否连接并工作正常。
[Français] Pour vérifier que tous les composants (Servos, Écran, Empreinte) sont connectés et fonctionnent correctement, exécutez l'outil de test intégré.

```bash
sudo python3 hardware_test.py
```
*   [中文] 选择 '1' 测试所有舵机。
*   [中文] 选择 '2' 测试屏幕颜色。
*   [中文] 选择 '3' 检查指纹传感器连接和图像捕获。
*   [Français] Sélectionnez '1' pour tester tous les servomoteurs.
*   [Français] Sélectionnez '2' pour tester les couleurs de l'écran.
*   [Français] Sélectionnez '3' pour vérifier la connexion du capteur d'empreintes digitales et la capture d'image.

### 4. 运行主程序 / Lancer le Programme Principal
[中文] 启动分配器系统。这将运行指纹监听循环，更新显示屏，并根据认证控制舵机。
[Français] Démarrer le système de distribution. Cela lance la boucle d'écoute des empreintes digitales, met à jour l'affichage et contrôle les servomoteurs en fonction de l'authentification.

```bash
sudo python3 main_demo.py
```

---

## 项目结构 / Structure du Projet

| 文件 (Fichier) | 描述 (Description) |
| :--- | :--- |
| `main_demo.py` | **核心应用 / Application Principale**. 处理认证循环、UI 更新和舵机触发。 / *Gère la boucle d'authentification, les mises à jour de l'interface utilisateur et le déclenchement des servomoteurs.* |
| `servo_control.py` | **驱动 / Pilote**. `lgpio` 的封装，用于通过软件 PWM 控制 SG90 舵机。 / *Wrapper pour `lgpio` afin de contrôler les servos SG90 via PWM logiciel.* |
| `st7789_driver.py` | **驱动 / Pilote**. 用于 IPS 显示屏的自定义 SPI 驱动。 / *Pilote SPI personnalisé pour l'écran IPS.* |
| `fingerprint_enroll.py` | **工具 / Outil**. 用于注册新指纹的独立脚本。 / *Script autonome pour enregistrer de nouvelles empreintes digitales.* |
| `setup_database.py` | **工具 / Outil**. 初始化 SQLite 数据库模式。 / *Initialise le schéma de la base de données SQLite.* |
| `WIRING_GUIDE.md` | **文档 / Documentation**. 详细的引脚和接线图。 / *Schémas détaillés du brochage et du câblage.* |
| `capsule_dispenser.db` | **数据 / Données**. 本地 SQLite 数据库（设置后创建）。 / *Base de données SQLite locale (créée après la configuration).* |

---

## 未来规划 / Feuille de Route Future

*   **摄像头集成 / Intégration Caméra**: 
    *   [中文] 添加 Raspberry Pi Camera Module 3 用于面部 ID 或二维码解锁（二级认证）。
    *   [Français] *Ajout du module caméra Raspberry Pi 3 pour l'identification faciale ou le déverrouillage par code QR (authentification secondaire).*
*   **Web 仪表板 / Tableau de Bord Web**: 
    *   [中文] 开发本地 Flask/Django 界面，用于远程日志查看、用户管理和紧急解锁。
    *   [Français] *Développement d'une interface Flask/Django locale pour la consultation des journaux à distance, la gestion des utilisateurs et le déverrouillage d'urgence.*
*   **库存与社交 / Inventaire & Social**: 
    *   [中文] 跟踪每个通道的胶囊计数。 / [Français] *Suivi du nombre de capsules par canal.*
    *   [中文] “胶囊分享”功能：允许用户通过 App 将多余的胶囊提供给他人。 / [Français] *Fonctionnalité "Partage de capsules" : permet aux utilisateurs d'offrir leurs capsules excédentaires via l'application.*
*   **外壳 / Boîtier**: 
    *   [中文] 设计全 3D 打印外壳，隐藏线路并将 Pi/屏幕安全固定在底座上。
    *   [Français] *Conception d'un boîtier entièrement imprimé en 3D pour cacher les fils et fixer solidement le Pi et l'écran à l'unité de base.*

---

## 历史与决策 / Histoire & Décisions

*   **2025-12 (S5)**: 将舵机控制从硬件 PWM 迁移到 **软件 PWM (`lgpio`)**。
    *   *[中文]* Raspberry Pi 5 的硬件 PWM 时钟与冷却风扇共享。当风扇启动时，会强制 PWM 频率达到 ~25kHz，导致舵机（需要 50Hz）失效。软件 PWM 完全避免了这种冲突。
    *   *[Français]* L'horloge PWM matérielle du Raspberry Pi 5 est partagée avec le ventilateur de refroidissement. Lorsque le ventilateur s'active, il force la fréquence PWM à ~25kHz, ce qui fait échouer les servomoteurs (qui ont besoin de 50Hz). Le PWM logiciel évite entièrement ce conflit.
    *   *[中文] 更新*: 在 `servo_control.py` 中实现了 **软启动 (平滑移动)** 逻辑（调整为 2.0秒持续时间），以大幅减少舵机动作期间的峰值电流消耗，防止共享电源轨电压骤降。
    *   *[Français] Mise à jour*: Implémentation de la logique de **Démarrage Progressif (Mouvement Fluide)** dans `servo_control.py` (réglée sur une durée de 2,0 s) pour réduire considérablement le pic de courant pendant l'actionnement du servo, empêchant ainsi la chute de tension sur le rail d'alimentation partagé.

*   **2024-11**: 移除了架构中的 Arduino。Pi 5 足够强大，可以直接处理所有 IO。 / Suppression de l'Arduino de l'architecture. Le Pi 5 est assez puissant pour gérer toutes les E/S directement.

## License
MIT License
