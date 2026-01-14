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

### 5. Configuration Réseau (Hotspot hors ligne)
Pour permettre à l'application Android de contrôler le Pi tout en conservant sa connexion 4G/5G (sans Internet via le Pi), configurez le hotspot en mode "sans passerelle" :

```bash
sudo chmod +x tools/setup_manual_hotspot.sh
sudo ./tools/setup_manual_hotspot.sh
```
*   Cela crée un réseau Wi-Fi `DistCapsule_Box` (IP: 192.168.4.1).
*   **Important** : Le téléphone utilisera ce Wi-Fi pour MQTT mais gardera la 4G pour Internet.

Pour arrêter le hotspot et reconnecter le Pi au Wi-Fi domestique :
```bash
sudo ./tools/stop_hotspot.sh
```

---

## 📖 Guide d'Utilisation

### 1. Initialiser le Système
Créer les tables de base de données pour les utilisateurs et les journaux (ne supprime pas les utilisateurs sauf suppression manuelle du .db).

```bash
python3 tools/setup_database.py
```

### 2. Gérer Utilisateurs & Empreintes
Lancez l'outil de gestion pour lister, enrôler des admins ou des utilisateurs avec allocation de canal (Box 1-5).

```bash
sudo python3 tools/fingerprint_enroll.py
```
*   *Remarque : Assurez-vous d'abord que la base de données est initialisée.*

### 3. Test Matériel
Pour vérifier que tous les composants (Servos, Écran, Empreinte) sont connectés et fonctionnent correctement, exécutez l'outil de test intégré.

```bash
sudo python3 tools/hardware_test.py
```
*   Sélectionnez '1' pour tester tous les servomoteurs.
*   Sélectionnez '2' pour tester les couleurs de l'écran.
*   Sélectionnez '3' pour vérifier la connexion du capteur d'empreintes digitales et la capture d'image.

### 4. Enrôlement Visage (Nouveau)
Pour enregistrer le visage d'un utilisateur pour la reconnaissance faciale :

```bash
python3 tools/face_enroll.py
```
*   Assurez-vous que l'utilisateur existe déjà (ID créé via l'étape 2 ou `add_user.py`).
*   Suivez les instructions à l'écran pour capturer le visage.
*   **Note Pi 5**: Le script utilise GStreamer/Libcamera automatiquement.

### 5. Lancer le Programme Principal
Démarrer le système. Le système démarre en **Mode Veille (Sleep Mode)** (écran éteint) pour économiser l'énergie.
*   **Pour réveiller** : Appuyez sur le **bouton physique**.
*   **Durée d'activité** : Le système reste actif pendant 30 secondes après la dernière action.

```bash
sudo python3 main.py
```

### 6. Service Automatique (Démarrage)
Pour installer le service systemd afin que le programme se lance au démarrage :

```bash
./tools/install_service.sh
```

### 7. API REST (App Mobile)
Pour activer le contrôle à distance via l'application Android, démarrez le serveur API :
```bash
pip install -r api/requirements.txt
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

---

## 📂 Structure du Projet

| Fichier/Dossier | Description |
| :--- | :--- |
| `main.py` | **Application Principale**. Gère la boucle d'authentification et la logique métier. |
| `api/` | **Web API**. Serveur FastAPI pour l'application mobile Android (Logs/Utilisateurs). |
| `hardware/` | **Pilotes**. Contient les drivers (`servo_control`, `st7789`, `face_system`). |
| `tools/` | **Outils**. Scripts d'installation, de test et d'enrôlement (`xxx_enroll.py`). |
| `docs/` | **Documentation**. Guides de câblage et archives. |
| `capsule_dispenser.db` | **Données**. Base de données SQLite locale. |

---

## 🔮 Feuille de Route Future

*   **Intégration Caméra**: Ajout du module caméra Raspberry Pi 3 pour l'identification faciale ou le déverrouillage par code QR (authentification secondaire).
*   **Tableau de Bord Web**: Développement d'une interface Flask/Django locale pour la consultation des journaux à distance, la gestion des utilisateurs et le déverrouillage d'urgence. (En cours: API FastAPI)
*   **Inventaire & Social**: 
    *   Suivi du nombre de capsules par canal.
    *   Fonctionnalité "Partage de capsules" : permet aux utilisateurs d'offrir leurs capsules excédentaires via l'application.
*   **Boîtier**: Conception d'un boîtier entièrement imprimé en 3D pour cacher les fils et fixer solidement le Pi et l'écran à l'unité de base.

---

## 📜 Histoire & Décisions

*   **2025-12 (S5)**: 
    *   **Refonte Multi-threadée**: Migration vers une architecture à threads pour l'asynchronisme de l'IA (visage) et la fluidité de l'UI (compte à rebours linéaire).
    *   **Gestion Native GPIO**: Migration complète vers `lgpio` pour tous les contrôles (舵机 et boutons) afin de garantir la stabilité sur Pi 5.
    *   **Optimisation de la Réactivité**: Suppression des délais bloquants (`time.sleep`) au profit d'une détection d'état non-bloquante et d'une synchronisation centralisée des horloges.
    *   **UI Avancée**: Ajout d'un compte à rebours numérique en temps réel avec changement de couleur dynamique.
    *   **Refonte des Permissions**: Introduction des niveaux de rôle et de l'allocation des canaux physiques.

---

*   **2024-11**: Suppression de l'Arduino de l'architecture. Le Pi 5 est assez puissant pour gérer toutes les E/S directement.

## License
MIT License
