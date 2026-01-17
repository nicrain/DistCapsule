# Status du Projet DistCapsule (S6) - 2026-01-02
# DistCapsule 项目状态报告 (S6)

## 🔵 État Actuel : En Développement (S6 - IoT & Mobile)
**Focus**: Transition d'un système autonome (Standalone) vers un écosystème connecté (IoT).
**核心目标**: 从单机智能系统向物联网互联生态转型。

## 🎯 Objectifs de la Phase S6 / 本阶段目标

### 1. Infrastructure Réseau (Pi-Side) / 网络基础设施 (树莓派端)
- [x] **API Web (Flask/FastAPI)**:
    - Créer une API légère pour exposer les logs (`/api/logs`) et l'état du système (`/api/status`).
    - **Web API**: 开发轻量级 API 接口，用于手机端获取日志和系统状态 (GET endpoints OK, POST pending).

### 2. Application Mobile (Android) / 移动端应用
- [ ] **App Architecture**: 
    - Tech: Android (Kotlin/Java) ou Cross-platform (Flutter).
    - **App 架构**: 确定技术栈（建议原生 Android Kotlin）。
- [ ] **Fonctionnalités Clés**:
    - **Dashboard**: Visualisation des niveaux de stock et des derniers accès.
    - **Remote Control**: Bouton "Ouvrir" à distance via API REST.
    - **Notifications**: Alerte sur le téléphone quand un utilisateur déverrouille une boîte.
    - **核心功能**: 仪表盘查看状态、远程一键开锁、实时访问通知。

### 3. Sécurité & Stabilité / 安全与稳定
- [ ] **Network Recovery**: Gestion automatique de la reconnexion Wi-Fi en cas de coupure.
- [ ] **安全加固**: 网络断连后的自动重连机制。

---

## 📅 Journal des Modifications (Changelog)
*   **2026-01-16**: 
    *   **Docs**: Création des diapositives de présentation (`docs/slides/`) avec architecture AAA et histoire du design 3D.
    *   **Fix Caméra**: Correction de la rotation de 90° (Counter-Clockwise) dans `face_system.py` et `face_enroll.py`.
    *   **IA**: Ajustement du seuil de reconnaissance faciale à 0.68 (vs 0.72) pour réduire les faux positifs.
    *   **UX**: Interface bilingue (Chinois / Français) pour tous les logs, menus et affichages LCD.
    *   **UX**: Clarification des logs (Remplacement du terme "Distance" par "Différence de caractéristiques").
    *   **Wiring**: Mise à jour des broches pour les Servos 2-5 (GPIO 6, 12, 13, 19).
    *   **Architecture**: Simplification (Suppression de MQTT). Focus sur l'API HTTP.
    *   **API**: Correction de la sérialisation Pydantic/SQLite. Endpoints `/users` et `/logs` fonctionnels.
*   **2026-01-02**: Initialisation de la Phase S6. Archivage de la version S5 (Standalone Stable).

---

## 📝 Notes Techniques
*   L'architecture S5 (Threading/Queue/Event) servira de base solide.
*   S5 的多线程架构将作为坚实基础。
