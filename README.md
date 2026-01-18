# Distributeur de Capsules Intelligent (Smart Capsule Dispenser)

[![中文](https://img.shields.io/badge/Language-中文-red.svg)](./README_CN.md)

**Plateforme:** Raspberry Pi 5 (Bookworm OS) | **État:** Stable (V1.1) | **Dernière mise à jour:** 2026-01-18

Un système de distribution de capsules sécurisé et activé par biométrie. Il transforme un présentoir à capsules standard en un système de "boîte aux lettres" personnalisé où chaque utilisateur a un accès exclusif à un canal de stockage spécifique via une authentification par empreinte digitale. Le système prend en charge l'enregistrement multi-utilisateurs, la hiérarchie des permissions (Admin/Utilisateur) et l'allocation dynamique des canaux physiques.

---

## ✨ Fonctionnalités Clés

*   **Gestion des Rôles Multi-utilisateurs**: Authentification par Token persistante avec connexion automatique (Auto-Login).
*   **Architecture IoT Moderne**: Écosystème complet intégrant l'App Android, le serveur FastAPI et le contrôle matériel en temps réel.
*   **Architecture Multi-threadée**: Threads séparés pour l'IA (visage), l'UI et la gestion des commandes réseau.
*   **UX Mobile Avancée (V1.1)**: Interface visuelle et colorée (Vivid Palette), icône d'application personnalisée, animations de sélection et retour haptique visuel.


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

### 5. Configuration Réseau (Zéro-Config)
Utilisez le script d'installation automatisé pour configurer le Hotspot, l'API et le contrôleur matériel comme services système :

```bash
cd tools
sudo ./install_service.sh
```
*   **SSID** : `DistCapsule_Box` (IP: 192.168.4.1)
*   **Port API** : 8000
*   **Démarrage** : Automatique au boot du Pi.

---

## 📱 Application Android (V1.1)

L'application (dossier `android/`) a été optimisée pour une fluidité maximale :

*   **Vivid UI** : Palette de couleurs moderne (Émeraude, Tournesol, Corail) avec texte contrasté pour une lisibilité parfaite.
*   **Auto-Login** : Une fois enregistré, l'accès au Dashboard est instantané.
*   **Connexion Wi-Fi Simplifiée** : Un bouton dédié permet de se connecter automatiquement au hotspot `DistCapsule_Box` sans saisir de mot de passe (Android 10+) ou en ouvrant directement les paramètres (Android 9).
*   **Saisie d'IP Simplifiée** : Entrez simplement l'IP, le protocole et le port sont gérés automatiquement.
*   **Gestion de Compte Sécurisée** : Bouton "Supprimer mon compte" avec nettoyage automatique du token local et des données biométriques sur le matériel.
*   **Feedback Visuel Avancé** : Animation "Pop-up" lors de la sélection des canaux (style réservation de place) et transitions fluides entre les menus.
*   **Navigation Fluide** : Ajout de boutons de retour et gestion intelligente du clavier virtuel pour une expérience sans friction.
*   **Sécurité Administrateur** : Protection contre la suppression accidentelle du compte admin et verrouillage des modifications pour le profil administrateur dans la console de gestion.
*   **Version Production V1.1** : Écosystème IoT complet avec application Android native (Java), serveur FastAPI et agent Python sur Pi 5.
*   **Auto-Guérison (Watchdog)** : Surveillance active du capteur d'empreintes avec réinitialisation automatique en cas de défaillance.
*   **Soutenance & Documentation** : Support de présentation LaTeX complet (21 slides) détaillant l'architecture AAA, les défis techniques et les choix d'ingénierie.
*   **Sécurité \& RGPD** : Authentification par token, protection des comptes administrateurs et fonction "Droit à l'oubli" (nettoyage complet des données biométriques).

---

## 📖 Guide d'Utilisation

### 1. Inscription
Ouvrez l'application, entrez votre nom et cliquez sur "Créer et se connecter". Un canal libre vous sera automatiquement attribué si disponible.

### 2. Administration
Pour activer les privilèges Admin sur un compte :
```bash
sqlite3 capsule_dispenser.db "UPDATE Users SET auth_level=1 WHERE user_id=1;"
```

### 3. Enrôlement Biométrique
Les utilisateurs peuvent lancer l'enrôlement de leur visage ou empreinte directement depuis leur Dashboard. L'écran du Pi s'allume alors automatiquement pour guider l'utilisateur.

---

## 📂 Structure du Projet

| Fichier/Dossier | Description |
| :--- | :--- |
| `main.py` | Cœur du système (Hardware Loop). |
| `api/server.py` | API REST FastAPI. |
| `android/` | Projet Android Studio (Java). |
| `hardware/` | Drivers et logique d'enrôlement. |
| `tools/` | Scripts d'installation et maintenance. |

---

## 🔮 Feuille de Route Future

*   **Notifications Push** : Alertes mobiles en cas d'accès non autorisé.
*   **Logs Avancés** : Historique détaillé des accès avec photos des visages.
*   **Design 3D** : Finalisation de la coque de protection.

---

## 📜 Histoire & Décisions

*   **2026-01-18 (V1.1)** : Refonte de l'UX Android, ajout de l'auto-login et sécurisation des timeouts matériels.
*   **2026-01-14 (V1.0)** : Première release stable IoT (App + API + Pi).
*   **2025-12 (S5)** : Migration vers `lgpio` et architecture asynchrone.

---

*   **Note** : Le projet a abandonné le support MQTT et le suivi des stocks physiques pour se concentrer sur la fiabilité de l'accès biométrique.

## License
MIT License
