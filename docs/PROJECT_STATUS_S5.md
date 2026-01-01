# Status du Projet DistCapsule (S5) - 2025-12-30
# DistCapsule 项目状态报告 (S5)

## 🟢 État Actuel : Stable (S5) / 当前状态：稳定
Le système est fonctionnel avec une architecture matérielle complète et un logiciel optimisé pour le Raspberry Pi 5.
系统功能正常，拥有完整的硬件架构，且软件已针对 Raspberry Pi 5 进行了优化。

## 🛠 Modifications Récentes (S5) / 近期修改
1.  **Architecture Logicielle (软件架构)** :
    *   Passage au **Multi-threading** : `main.py` sépare la reconnaissance faciale (thread arrière-plan) de l'UI (thread principal) pour éviter les blocages.
    *   **多线程重构**：`main.py` 将人脸识别（后台线程）与 UI 界面（主线程）分离，彻底消除了卡顿。
    *   **Migration lgpio** : Abandon total de `RPi.GPIO` au profit de `lgpio` pour éviter les conflits matériels sur le Pi 5.
    *   **迁移至 lgpio**：为了解决 Pi 5 上的硬件冲突，全面弃用 `RPi.GPIO`，转而使用更底层的 `lgpio` 库。

2.  **Expérience Utilisateur (UI/UX) (用户体验)** :
    *   **Compte à rebours linéaire** : Affichage fluide des secondes restantes.
    *   **线性倒计时**：流畅显示剩余秒数。
    *   **Session Interactive** : Bouton physique (GPIO 26) pour le réveil et l'extension du temps ("Keep Alive").
    *   **交互式会话**：通过物理按钮 (GPIO 26) 实现系统唤醒和会话时间延长（“保活”）。
    *   **Réactivité Instantanée** : Utilisation d'interruptions matérielles pour le bouton, éliminant toute latence.
    *   **即时响应**：按钮检测采用边缘检测机制，消除了延迟。
    *   **Sécurité Session** : Timeout automatique après 30s d'inactivité, forçage de l'arrêt après 5 min.
    *   **会话安全**：30秒无操作自动休眠，5分钟强制结束会话。

3.  **Réseau (网络)** :
    *   Scripts de **Hotspot "Silencieux"** : Permet au téléphone de contrôler le Pi (MQTT/HTTP futur) tout en gardant la 4G (`tools/setup_manual_hotspot.sh`).
    *   **静默热点脚本**：允许手机连接树莓派（用于未来的 MQTT/HTTP 控制）的同时，保持手机自身的 4G 上网功能。

## 📋 Liste de Contrôle des Fonctionnalités / 功能核对表
- [x] Contrôle Servo (lgpio) / 舵机控制
- [x] Écran LCD (ST7789) + Horloge / LCD 屏幕 + 时钟
- [x] Capteur Empreinte (DY-50) / 指纹传感器
- [x] Reconnaissance Faciale (OpenCV/GStreamer) / 人脸识别
- [x] Base de données SQLite (Utilisateurs/Logs) / SQLite 数据库
- [x] Bouton de Réveil/Extension / 唤醒与续命按钮
- [x] Installation Service systemd (`capsule.service`) / 系统服务安装
- [x] Documentation complète (FR/CN/Wiring) / 完整文档 (中/法/接线图)

## 🔮 Prochaines Étapes (To-Do) / 下一步计划
1.  **Interface Web (Dashboard)** :
    *   Créer une app Flask/Django locale pour visualiser les logs et gérer les utilisateurs depuis le téléphone.
    *   **Web 仪表盘**：开发一个本地 Flask/Django 应用，以便在手机上查看日志和管理用户。
2.  **Protocole MQTT** :
    *   Implémenter le client MQTT dans `main.py` pour recevoir les commandes d'ouverture à distance.
    *   **MQTT 协议**：在 `main.py` 中实现 MQTT 客户端，以接收远程开锁指令。
3.  **Gestion de Stock** :
    *   Ajouter un compteur de capsules par canal dans la base de données.
    *   **库存管理**：在数据库中增加每个通道的胶囊计数功能。

## 📝 Notes pour la Reprise / 复工备注
*   Pour lancer le système manuellement : `sudo systemctl stop capsule` puis `sudo python3 main.py`.
*   手动启动系统：先停止服务 `sudo systemctl stop capsule`，再运行 `sudo python3 main.py`。
*   Pour mettre à jour le service : `git pull` puis `sudo systemctl restart capsule`.
*   更新服务代码：执行 `git pull` 后运行 `sudo systemctl restart capsule`。
*   Le script de hotspot est `tools/setup_manual_hotspot.sh`.
*   热点配置脚本位于 `tools/setup_manual_hotspot.sh`。
