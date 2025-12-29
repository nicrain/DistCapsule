# Smart Capsule Dispenser (智能胶囊分配器 / Distributeur de Capsules Intelligent)

**Platform:** Raspberry Pi 5 (Bookworm OS) | **Status:** Stable (S5) | **Last Updated:** 2025-12

[中文]
这是一个安全的、支持生物识别的胶囊分配系统。它将标准的胶囊展示架转变为个性化的“信箱”系统，每个用户通过指纹认证拥有对特定存储通道的专属访问权。系统支持多用户录入、权限分级（管理员/普通用户）以及物理通道的动态分配。

[Français]
Un système de distribution de capsules sécurisé et activé par biométrie. Il transforme un présentoir à capsules standard en un système de "boîte aux lettres" personnalisé où chaque utilisateur a un accès exclusif à un canal de stockage spécifique via une authentification par empreinte digitale. Le système prend en charge l'enregistrement multi-utilisateurs, la hiérarchie des permissions (Admin/Utilisateur) et l'allocation dynamique des canaux physiques.

---

## 主要功能 / Fonctionnalités Clés

### [中文]
*   **多用户角色管理**: 支持 1 个超级管理员和无限候补用户。物理通道（舵机）仅分配给活跃用户（最多 5 人）。
*   **智能节能 (Eco Mode)**: 30秒无操作自动熄灭屏幕背光，触摸指纹传感器瞬间唤醒。大幅降低 CPU 占用与功耗。
*   **指纹录入引导**: 交互式 CLI 工具，支持手指部位选择（如 Right Thumb）并自动列出当前用户状态。
*   **精确权限控制**: 认证后，普通用户解锁专属舵机；管理员仅显示欢迎界面，**不触发**任何硬件动作（用于维护/管理）。
*   **生物识别安全**: 集成 DY-50 (兼容 R307) 光学指纹传感器，实现快速识别。

### [Français]
*   **Gestion des Rôles Multi-utilisateurs**: Prend en charge 1 super-administrateur et des utilisateurs en liste d'attente illimités。
*   **Mode Éco Intelligent**: Éteint automatiquement le rétroéclairage après 30s d'inactivité ; réveil instantané au toucher du capteur. Réduit considérablement l'utilisation du CPU et la consommation d'énergie.
*   **Guide d'Enrôlement**: Outil CLI interactif avec sélection du doigt (ex: Right Thumb) et affichage automatique de l'état des utilisateurs actuels.
*   **Contrôle de Précision**: Après authentification, l'utilisateur déverrouille son servo dédié ; l'administrateur voit un écran de bienvenue mais ne déclenche **aucune** action matérielle.
*   **Sécurité Biométrique**: Capteur optique DY-50 (compatible R307) pour une identification rapide.

---

## 硬件架构 / Architecture Matérielle

*   **控制器 (Contrôleur)**: Raspberry Pi 5 (推荐 8GB / Recommandé 8Go).
*   **执行器 (Actionneurs)**: 5x SG90 微型舵机 (9g) / 5x Micro servomoteurs SG90 (9g).
*   **传感器 (Capteur)**: DY-50 / R307 光学指纹模块 (UART).
*   **显示器 (Écran)**: 1.3" IPS LCD (240x240) 配备 ST7789 驱动 (SPI).
*   **底座 (Base)**: 定制 3D 打印组件 / Composants imprimés en 3D sur mesure.
*   **电源 (Alimentation)**: Pi 5 官方电源 + **外部 5V 舵机电源** (共地 / Masse commune).

---

## 安装与设置 / Installation et Configuration

### 1. 系统依赖 / Dépendances Système
```bash
sudo apt-get update
sudo apt-get install python3-serial python3-pip python3-lgpio python3-pil python3-rpi.gpio
```

### 2. Python 库 / Bibliothèques Python
```bash
sudo pip3 install adafruit-circuitpython-fingerprint st7789
```

---

## 使用指南 / Guide d'Utilisation

### 1. 初始化系统 / Initialiser le Système
[中文] 创建数据库表及初始化配置（此操作不会删除现有用户，除非手动删除 .db 文件）。
[Français] Crée les tables et initialise la config (ne supprime pas les utilisateurs sauf suppression manuelle du .db).
```bash
python3 setup_database.py
```

### 2. 管理用户与指纹 / Gérer Utilisateurs & Empreintes
[中文] 启动管理工具，您可以查看列表、录入管理员、录入用户并分配舵机（1-5号仓）。
[Français] Lancez l'outil de gestion pour lister, enrôler des admins ou des utilisateurs avec allocation de canal (Box 1-5).
```bash
sudo python3 fingerprint_enroll.py
```

### 3. 运行主程序 / Lancer le Programme Principal
[中文] 启动识别监听。系统将根据指纹权限自动驱动对应的舵机。
[Français] Lancez l'écoute. Le système actionnera automatiquement le servo correspondant selon les permissions de l'empreinte.
```bash
sudo python3 main_demo.py
```

---

## 项目结构 / Structure du Projet

| 文件 (Fichier) | 描述 (Description) |
| :--- | :--- |
| `main_demo.py` | **核心应用 / Application Principale**. 处理认证、UI 及按通道触发舵机。 |
| `fingerprint_enroll.py` | **管理工具 / Outil de Gestion**. 交互式录入指纹、分配通道及用户管理。 |
| `servo_control.py` | **驱动 / Pilote**. 封装 `lgpio` 以实现 5 通道软件 PWM 控制。 |
| `setup_database.py` | **数据库 / Base de données**. 定义用户权限和通道分配模型。 |

---

## 历史与决策 / Histoire & Décisions

*   **2025-12 (S5)**: 
    *   **权限重构**: 引入了角色等级和物理通道分配逻辑。
    *   **交互优化**: 录入过程增加手指部位菜单选择（英语）并实时打印用户统计。
    *   **硬件兼容**: 为 Pi 5 优化了软件 PWM，解决风扇 PWM 冲突。

## License
MIT License