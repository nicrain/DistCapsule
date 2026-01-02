# Status du Projet DistCapsule (S6) - 2026-01-02
# DistCapsule 项目状态报告 (S6)

## 🔵 État Actuel : En Développement (S6 - IoT & Mobile)
**Focus**: Transition d'un système autonome (Standalone) vers un écosystème connecté (IoT).
**核心目标**: 从单机智能系统向物联网互联生态转型。

## 🎯 Objectifs de la Phase S6 / 本阶段目标

### 1. Infrastructure Réseau (Pi-Side) / 网络基础设施 (树莓派端)
- [ ] **MQTT Broker/Client**: 
    - Installer et configurer Mosquitto sur le Pi.
    - Implémenter un client MQTT asynchrone dans `main.py` pour écouter les commandes (ex: `distcapsule/open/1`).
    - **MQTT 部署**: 安装 Mosquitto，并在 `main.py` 中集成异步 MQTT 客户端，监听远程开锁指令。
- [ ] **API Web (Flask/FastAPI)**:
    - Créer une API légère pour exposer les logs (`/api/logs`) et l'état du système (`/api/status`).
    - **Web API**: 开发轻量级 API 接口，用于手机端获取日志和系统状态。

### 2. Application Mobile (Android) / 移动端应用
- [ ] **App Architecture**: 
    - Tech: Android (Kotlin/Java) ou Cross-platform (Flutter).
    - **App 架构**: 确定技术栈（建议原生 Android Kotlin）。
- [ ] **Fonctionnalités Clés**:
    - **Dashboard**: Visualisation des niveaux de stock et des derniers accès.
    - **Remote Control**: Bouton "Ouvrir" à distance via MQTT.
    - **Notifications**: Alerte sur le téléphone quand un utilisateur déverrouille une boîte.
    - **核心功能**: 仪表盘查看状态、远程一键开锁、实时访问通知。

### 3. Sécurité & Stabilité / 安全与稳定
- [ ] **TLS/SSL**: Sécuriser les communications MQTT.
- [ ] **Network Recovery**: Gestion automatique de la reconnexion Wi-Fi/MQTT en cas de coupure.
- [ ] **安全加固**: MQTT 通信加密，以及网络断连后的自动重连机制。

---

## 📅 Journal des Modifications (Changelog)
*   **2026-01-02**: Initialisation de la Phase S6. Archivage de la version S5 (Standalone Stable).

---

## 📝 Notes Techniques
*   L'architecture S5 (Threading/Queue/Event) servira de base solide. Le client MQTT tournera probablement dans son propre thread, similaire à `face_worker`.
*   S5 的多线程架构将作为坚实基础。MQTT 客户端预计将运行在独立的后台线程中，类似于现有的人脸识别线程。
