# Status du Projet DistCapsule (S6) - 2026-01-02
# DistCapsule 项目状态报告 (S6)

## 🔵 État Actuel : Terminé / Completed (S6 - IoT & Mobile)
**Focus**: Transition d'un système autonome (Standalone) vers un écosystème connecté (IoT).
**核心目标**: 从单机智能系统向物联网互联生态转型。

## 🎯 Objectifs de la Phase S6 / 本阶段目标

### 1. Infrastructure Réseau (Pi-Side) / 网络基础设施 (树莓派端)
- [x] **API Web (Flask/FastAPI)**:
    - Créer une API légère pour exposer les logs (`/api/logs`) et l'état du système (`/api/status`).
    - **Web API**: 开发轻量级 API 接口，用于手机端获取日志和系统状态 (GET endpoints OK, POST pending).

### 2. Application Mobile (Android) / 移动端应用
- [x] **App Architecture**: 
    - Tech: Android (Kotlin/Java) ou Cross-platform (Flutter).
    - **App 架构**: 确定技术栈（原生 Android Java）。
- [x] **Fonctionnalités Clés**:
    - **Dashboard**: Visualisation des niveaux de stock et des derniers accès.
    - **App Control**: Bouton "Ouvrir" via App (Wi-Fi Local).
    - **Notifications**: Alerte sur le téléphone quand un utilisateur déverrouille une boîte.
    - **核心功能**: 仪表盘、App 无线开锁(Wi-Fi)、实时通知。

### 3. Sécurité & Stabilité / 安全与稳定
- [x] **Network Recovery**: Gestion automatique de la reconnexion Wi-Fi en cas de coupure.
- [x] **安全加固**: 网络断连后的自动重连机制。

---

## 📅 Journal des Modifications (Changelog)
*   **2026-01-18 (Final S6 Release - V1.1)**:
    *   **Android App v1.1**: Refonte totale de l'UX (Vivid Palette), icône personnalisée, auto-login via Token.
    *   **Wi-Fi Automation**: Bouton de connexion automatique au hotspot `DistCapsule_Box` avec gestion des permissions.
    *   **Logic Cleanup**: Suppression du Mode Demo et de la création d'utilisateur côté Admin au profit du self-service. Nettoyage massif des ressources (strings.xml) pour une stabilité de build accrue.
    *   **Sécurité**: Suppression automatique du token d'accès lors de la suppression du compte. Protection contre la suppression accidentelle de l'administrateur.
    *   **Micro-interactions**: Ajout d'un effet "Pop-up" (TranslationY + OvershootInterpolator) sur les boutons de sélection de canal pour un feedback tactile visuel.
    *   **Fiabilité Matérielle**: Implémentation d'un thread "Watchdog" pour le capteur d'empreintes (DY-50). Il détecte les timeouts UART et effectue un "Soft Reset" automatique sans redémarrage du Pi.
    *   **Documentation**: Finalisation des diapositives de soutenance (LaTeX V2.1) avec focus sur l'architecture et les défis techniques. 
        - Blocage total de la suppression des comptes administrateurs (côté API et App).
        - Interface de gestion dynamique : les boutons d'action sont masqués tant qu'un utilisateur n'est pas sélectionné.
        - Verrouillage automatique de l'UI si le profil sélectionné est l'administrateur.
    *   **UX Revolution**: Boutons de retour, gestion intelligente du clavier, et messages Toast conviviaux. Distinction sémantique entre "Supprimer l'utilisateur" (Admin) et "Supprimer mon compte" (Utilisateur).
*   **2026-01-14 (V1.0 Initial IoT Release)**:
    *   Intégration du code source de l'application dans le répertoire `android/`.
    *   Nettoyage des logs (Suppression des Emojis, style professionnel).
    *   Implémentation de la gestion complète des utilisateurs (`POST /users` pour créer, `DELETE /users` pour supprimer avec nettoyage matériel).
*   **2026-01-16**: 
    *   **Docs**: Création des diapositives de présentation (`docs/slides/`) avec architecture AAA et histoire du design 3D.
    *   **Fix Caméra**: Correction de la rotation de 90° (Counter-Clockwise) dans `face_system.py` et `face_enroll.py`.
    *   **IA**: Ajustement du seuil de reconnaissance faciale à 0.68 (vs 0.72) pour réduire les faux positifs.
    *   **UX**: Interface bilingue (Chinois / Français) pour tous les logs, menus et affichages LCD.
    *   **UX**: Clarification des logs (Remplacement du terme "Distance" par "Différence de caractéristiques").
    *   **Wiring**: Mise à jour des broches pour les Servos 2-5 (GPIO 6, 12, 13, 19).
    *   **Architecture**: Simplification (Suppression de MQTT). Focus sur l'API HTTP.
    *   **API**: Correction de la sérialisation Pydantic/SQLite. Endpoints `/users` et `/logs` fonctionnels.
    *   **IoT**: Implémentation du contrôle App via table `Pending_Commands` (Renommé de Remote -> App).
    *   **Hotspot**: Ajout de la passerelle DHCP (192.168.4.1) pour résoudre les problèmes de connexion Android/iOS.
    *   **API**: Ajout des statuts biométriques (`has_face`, `has_fingerprint`) dans la réponse `/users`.
*   **2026-01-02**: Initialisation de la Phase S6. Archivage de la version S5 (Standalone Stable).
    *   **Auth**: Simplification du flux (Suppression de `/bind`, intégration du Token dans `/users` pour l'enregistrement direct).
*   **2026-01-02**: Initialisation de la Phase S6. Archivage de la version S5 (Standalone Stable).

---

## 📝 Notes Techniques
*   L'architecture S5 (Threading/Queue/Event) servira de base solide.
*   S5 的多线程架构将作为坚实基础。
