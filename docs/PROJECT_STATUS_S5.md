# Status du Projet DistCapsule (S5) - 2025-12-30

## 🟢 État Actuel : Stable (S5)
Le système est fonctionnel avec une architecture matérielle complète et un logiciel optimisé pour le Raspberry Pi 5.

## 🛠 Modifications Récentes (S5)
1.  **Architecture Logicielle** :
    *   Passage au **Multi-threading** : `main.py` sépare la reconnaissance faciale (thread arrière-plan) de l'UI (thread principal) pour éviter les blocages.
    *   **Migration lgpio** : Abandon total de `RPi.GPIO` au profit de `lgpio` pour éviter les conflits matériels sur le Pi 5.
2.  **Expérience Utilisateur (UI/UX)** :
    *   **Compte à rebours linéaire** : Affichage fluide des secondes restantes.
    *   **Session Interactive** : Bouton physique (GPIO 26) pour le réveil et l'extension du temps ("Keep Alive").
    *   **Réactivité Instantanée** : Utilisation d'interruptions matérielles pour le bouton, éliminant toute latence.
    *   **Sécurité Session** : Timeout automatique après 30s d'inactivité, forçage de l'arrêt après 5 min.
3.  **Réseau** :
    *   Scripts de **Hotspot "Silencieux"** : Permet au téléphone de contrôler le Pi (MQTT/HTTP futur) tout en gardant la 4G (`tools/setup_manual_hotspot.sh`).

## 📋 Liste de Contrôle des Fonctionnalités
- [x] Contrôle Servo (lgpio)
- [x] Écran LCD (ST7789) + Horloge
- [x] Capteur Empreinte (DY-50)
- [x] Reconnaissance Faciale (OpenCV/GStreamer)
- [x] Base de données SQLite (Utilisateurs/Logs)
- [x] Bouton de Réveil/Extension
- [x] Installation Service systemd (`capsule.service`)
- [x] Documentation complète (FR/CN/Wiring)

## 🔮 Prochaines Étapes (To-Do)
1.  **Interface Web (Dashboard)** :
    *   Créer une app Flask/Django locale pour visualiser les logs et gérer les utilisateurs depuis le téléphone.
2.  **Protocole MQTT** :
    *   Implémenter le client MQTT dans `main.py` pour recevoir les commandes d'ouverture à distance.
3.  **Gestion de Stock** :
    *   Ajouter un compteur de capsules par canal dans la base de données.

## 📝 Notes pour la Reprise
*   Pour lancer le système manuellement : `sudo systemctl stop capsule` puis `sudo python3 main.py`.
*   Pour mettre à jour le service : `git pull` puis `sudo systemctl restart capsule`.
*   Le script de hotspot est `tools/setup_manual_hotspot.sh`.
