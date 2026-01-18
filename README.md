# Distributeur de Capsules Intelligent (Smart Capsule Dispenser)

[![中文](https://img.shields.io/badge/Language-中文-red.svg)](./README_CN.md)

**Plateforme:** Raspberry Pi 5 (Bookworm OS) | **État:** Stable (S5) | **Dernière mise à jour:** 2026-01

Un système de distribution de capsules sécurisé et activé par biométrie. Il transforme un présentoir à capsules standard en un système de "boîte aux lettres" personnalisé où chaque utilisateur a un accès exclusif à un canal de stockage spécifique via une authentification par empreinte digitale. Le système prend en charge l'enregistrement multi-utilisateurs, la hiérarchie des permissions (Admin/Utilisateur) et l'allocation dynamique des canaux physiques.

---

## ✨ Fonctionnalités Clés

*   **Gestion des Rôles Multi-utilisateurs**: Prend en charge 1 super-administrateur et des utilisateurs en liste d'attente illimités. Les canaux physiques (servos) ne sont alloués qu'aux utilisateurs actifs (max 5).
*   **Architecture Multi-threadée**: Utilise des threads séparés pour la reconnaissance faciale et l'interface utilisateur, garantissant une **mise à jour fluide et linéaire** du compte à rebours sans saccades.
*   **Gestion de l'Énergie & Session**: 
    *   Mise en veille automatique après 30s.
    *   Réveil et **extension de temps** via un bouton physique dédié.
    *   Sécurité : limite de session maximale de 5 minutes pour éviter les blocages.
*   **Interface Interactive**: Écran IPS 1,3" affichant l'heure, le statut et un **compte à rebours en temps réel**. La couleur passe au rouge en dessous de 10s.
*   **Horloge en Temps Réel**: Affiche l'heure du système mise à jour dynamiquement en mode actif.
*   **Guide d'Enrôlement**: Outil CLI interactif avec sélection du doigt (ex: Right Thumb) et affichage automatique de l'état des utilisateurs actuels.
*   **Sécurité Biométrique**: Capteur optique DY-50 (compatible R307) pour une identification rapide.

---

## 🛠 Architecture Matérielle

*   **Contrôleur**: Raspberry Pi 5 (Recommandé 8Go).
*   **Actionneurs**: 5x Micro servomoteurs SG90 (9g).
*   **Capteur**: Module capteur d'empreintes optique DY-50 / R307 (UART).
*   **Interface**: Écran LCD IPS 1.3" (ST7789) + **Bouton Poussoir (Wake-Up)** pour le réveil du système.
*   **Base**: Composants imprimés en 3D sur mesure. Les premières ébauches sont disponibles dans le répertoire `3D/`.
*   **Alimentation**:
    *   Pi 5: Alimentation officielle USB-C 27W.
    *   Servos: **Alimentation externe 5V** (Masse commune avec le Pi obligatoire).

> **⚠️ Avertissement de Câblage**: Ne pas alimenter 5 servomoteurs directement depuis la broche 5V du GPIO du Pi. Utilisez une source d'alimentation externe. Voir [WIRING_GUIDE.md](docs/WIRING_GUIDE.md) pour les détails de câblage.

---

## 🚀 Installation et Configuration

### 1. Dépendances Système
Le projet dépend de `lgpio` pour le contrôle GPIO sur le Pi 5 et de `pyserial` pour le capteur.

```bash
sudo apt-get update
sudo apt-get install python3-serial python3-pip python3-lgpio python3-pil python3-rpi.gpio
```

### 2. Bibliothèques Python
```bash
sudo pip3 install adafruit-circuitpython-fingerprint st7789
```

### 3. Environnement de Reconnaissance Faciale (Pi 5 Bookworm)
Le système d'exploitation Raspberry Pi OS Bookworm empêche l'installation directe via `pip`. Utilisez l'une des méthodes suivantes :

**Pré-requis (Pi 5) : Pilotes GStreamer**
Pour que la caméra fonctionne avec OpenCV sur le Pi 5, vous devez installer les plugins GStreamer :
```bash
sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
gstreamer1.0-libcamera gstreamer1.0-tools
```

**Méthode A : APT (Recommandé)**
```bash
sudo apt update
sudo apt install python3-opencv python3-face-recognition
```

**Méthode B : PIP (Si APT échoue)**
```bash
# L'option --break-system-packages est requise hors d'un environnement virtuel
pip3 install opencv-python face_recognition setuptools --break-system-packages

# ⚠️ Si vous rencontrez l'erreur "Please install `face_recognition_models`" :
pip install git+https://github.com/ageitgey/face_recognition_models --break-system-packages
```

### 4. Configuration Matérielle
*   **UART**: Activez le matériel du port série via `sudo raspi-config`, mais désactivez le shell de connexion. Le module d'empreintes digitales utilise `/dev/ttyAMA0` (GPIO 14/15) sur le Pi 5.
*   **SPI**: Activez l'interface SPI via `sudo raspi-config` pour l'écran.

### 5. Configuration Réseau (Hotspot & API)
Le système est conçu pour fonctionner de manière autonome. Utilisez le script d'installation tout-en-un pour configurer le Hotspot Wi-Fi, le serveur API et le service principal :

```bash
cd tools
sudo ./install_service.sh
```
*   **Service Hotspot** : Crée le Wi-Fi `DistCapsule_Box` (192.168.4.1).
*   **Service API** : Lance le serveur REST sur le port 8000.
*   **Service Principal** : Lance la logique de contrôle matériel (`main.py`).
*   **Tout est automatique** au redémarrage du Pi.

---

## 📱 Application Android

L'application compagnon (dans le dossier `android/`) offre une interface complète pour les utilisateurs et les administrateurs.

*   **Connexion Automatique** : Détection intelligente de l'IP du Pi.
*   **Enregistrement Simplifié** : Entrez simplement votre nom, le système attribue automatiquement un canal libre.
*   **Gestion Administrateur** :
    *   Attribution visuelle des canaux (boutons interactifs).
    *   Gestion des utilisateurs (suppression instantanée).
    *   Contrôle direct du matériel (déverrouillage, enrôlement).
*   **Utilisateur Standard** :
    *   Bouton unique "Obtenir mon café".
    *   Auto-enrôlement (Visage/Empreinte) via l'application.

---

## 📖 Guide d'Utilisation

### 1. Initialiser le Système
Créer les tables de base de données (si nécessaire).

```bash
python3 tools/setup_database.py
```

### 2. Premier Démarrage (Admin)
1.  Connectez votre téléphone au Wi-Fi `DistCapsule_Box`.
2.  Lancez l'application Android.
3.  Entrez "Admin" (ou votre nom) pour créer le premier utilisateur.
4.  Via SSH, élevez ce premier utilisateur au rang d'Admin :
    ```bash
    sqlite3 capsule_dispenser.db "UPDATE Users SET auth_level=1 WHERE user_id=1;"
    ```
5.  Redémarrez l'application. Vous avez maintenant accès au panneau d'administration.

### 3. Enrôlement
*   Dans l'application, cliquez sur "Ajouter Face" ou "Ajouter Empreinte".
*   L'écran du Pi s'allumera et vous guidera.
*   L'application se mettra à jour (bouton vert) une fois l'enrôlement terminé.

---

## 📂 Structure du Projet

| Fichier/Dossier | Description |
| :--- | :--- |
| `main.py` | **Application Principale**. Gère la boucle d'authentification et le matériel. |
| `api/` | **Web API**. Serveur FastAPI (`server.py`) pour l'app mobile. |
| `android/` | **Code Source Android**. Projet Android Studio complet. |
| `hardware/` | **Pilotes**. Drivers (`servo_control`, `st7789`, `enrollment`). |
| `tools/` | **Scripts**. Installation, tests et maintenance. |
| `docs/` | **Documentation**. Spécifications, diapositives et archives. |

---

## 🔮 Feuille de Route Future

*   **Intégration Caméra**: Identification faciale via Raspberry Pi Camera 3 (En cours).
*   **Notifications**: Push notifications sur mobile lors de l'accès.
*   **Boîtier**: Finalisation du design 3D pour l'intégration des composants.

---

## 📜 Histoire & Décisions

*   **2026-01 (S6 - IoT & Mobile)**:
    *   **Écosystème Complet** : Intégration transparente App <-> API <-> Matériel.
    *   **UX Mobile** : Application Android native avec authentification par Token et mises à jour en temps réel.
    *   **Stabilité** : Gestion des conflits de base de données et des timeouts matériels.
*   **2025-12 (S5)**: 
    *   **Refonte Multi-threadée**: Architecture asynchrone pour la fluidité de l'UI.
    *   **Gestion Native GPIO**: Migration vers `lgpio` pour le Pi 5.

---

*   **2024-11**: Suppression de l'Arduino de l'architecture. Le Pi 5 est assez puissant pour gérer toutes les E/S directement.

## License
MIT License
