# Distributeur de Capsules Intelligent (Smart Capsule Dispenser)

[![中文](https://img.shields.io/badge/Language-中文-red.svg)](./README_CN.md)

**Plateforme:** Raspberry Pi 5 (Bookworm OS) | **État:** Stable (S5) | **Dernière mise à jour:** 2025-12

Un système de distribution de capsules sécurisé et activé par biométrie. Il transforme un présentoir à capsules standard en un système de "boîte aux lettres" personnalisé où chaque utilisateur a un accès exclusif à un canal de stockage spécifique via une authentification par empreinte digitale. Le système prend en charge l'enregistrement multi-utilisateurs, la hiérarchie des permissions (Admin/Utilisateur) et l'allocation dynamique des canaux physiques.

---

## ✨ Fonctionnalités Clés

*   **Gestion des Rôles Multi-utilisateurs**: Prend en charge 1 super-administrateur et des utilisateurs en liste d'attente illimités. Les canaux physiques (servos) ne sont alloués qu'aux utilisateurs actifs (max 5).
*   **Mode Éco Intelligent**: Éteint automatiquement le rétroéclairage après 30s d'inactivité ; réveil instantané au toucher du capteur. Réduit considérablement l'utilisation du CPU et la consommation d'énergie.
*   **Horloge en Temps Réel**: Affiche l'heure du système mise à jour dynamiquement en mode veille, mise en pause pendant le sommeil.
*   **Guide d'Enrôlement**: Outil CLI interactif avec sélection du doigt (ex: Right Thumb) et affichage automatique de l'état des utilisateurs actuels.
*   **Interface Interactive**: Écran IPS 1,3" affichant le nom de l'utilisateur et le numéro de boîte. Le compte à rebours de déverrouillage utilise une **barre de progression visuelle**.
*   **Contrôle de Précision**: Après authentification, l'utilisateur déverrouille son servo dédié ; l'administrateur voit un écran de bienvenue mais ne déclenche **aucune** action matérielle.
*   **Sécurité Biométrique**: Capteur optique DY-50 (compatible R307) pour une identification rapide.

---

## 🛠 Architecture Matérielle

*   **Contrôleur**: Raspberry Pi 5 (Recommandé 8Go).
*   **Actionneurs**: 5x Micro servomoteurs SG90 (9g).
*   **Capteur**: Module capteur d'empreintes optique DY-50 / R307 (UART).
*   **Écran**: LCD IPS 1.3" (240x240) avec pilote ST7789 (SPI).
*   **Base**: Composants imprimés en 3D sur mesure. Les premières ébauches sont disponibles dans le répertoire `3D/`.
*   **Alimentation**:
    *   Pi 5: Alimentation officielle USB-C 27W.
    *   Servos: **Alimentation externe 5V** (Masse commune avec le Pi obligatoire).

> **⚠️ Avertissement de Câblage**: Ne pas alimenter 5 servomoteurs directement depuis la broche 5V du GPIO du Pi. Utilisez une source d'alimentation externe. Voir [WIRING_GUIDE.md](WIRING_GUIDE.md) pour les détails de câblage.

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

### 3. Configuration Matérielle
*   **UART**: Activez le matériel du port série via `sudo raspi-config`, mais désactivez le shell de connexion. Le module d'empreintes digitales utilise `/dev/ttyAMA0` (GPIO 14/15) sur le Pi 5.
*   **SPI**: Activez l'interface SPI via `sudo raspi-config` pour l'écran.

---

## 📖 Guide d'Utilisation

### 1. Initialiser le Système
Créer les tables de base de données pour les utilisateurs et les journaux (ne supprime pas les utilisateurs sauf suppression manuelle du .db).

```bash
python3 setup_database.py
```

### 2. Gérer Utilisateurs & Empreintes
Lancez l'outil de gestion pour lister, enrôler des admins ou des utilisateurs avec allocation de canal (Box 1-5).

```bash
sudo python3 fingerprint_enroll.py
```
*   *Remarque : Assurez-vous d'abord que la base de données est initialisée.*

### 3. Test Matériel
Pour vérifier que tous les composants (Servos, Écran, Empreinte) sont connectés et fonctionnent correctement, exécutez l'outil de test intégré.

```bash
sudo python3 hardware_test.py
```
*   Sélectionnez '1' pour tester tous les servomoteurs.
*   Sélectionnez '2' pour tester les couleurs de l'écran.
*   Sélectionnez '3' pour vérifier la connexion du capteur d'empreintes digitales et la capture d'image.

### 4. Lancer le Programme Principal
Démarrer le système de distribution. Cela lance la boucle d'écoute des empreintes digitales, met à jour l'affichage et contrôle les servomoteurs en fonction de l'authentification.

```bash
sudo python3 main_demo.py
```

---

## 📂 Structure du Projet

| Fichier | Description |
| :--- | :--- |
| `main_demo.py` | **Application Principale**. Gère la boucle d'authentification, les mises à jour de l'interface utilisateur et le déclenchement des servomoteurs. |
| `fingerprint_enroll.py` | **Outil de Gestion**. Script autonome pour enregistrer de nouvelles empreintes digitales et gérer les utilisateurs. |
| `servo_control.py` | **Pilote**. Wrapper pour `lgpio` afin de contrôler les servos SG90 via PWM logiciel. |
| `st7789_driver.py` | **Pilote**. Pilote SPI personnalisé pour l'écran IPS. |
| `setup_database.py` | **Outil**. Initialise le schéma de la base de données SQLite. |
| `WIRING_GUIDE.md` | **Documentation**. Schémas détaillés du brochage et du câblage. |
| `capsule_dispenser.db` | **Données**. Base de données SQLite locale (créée après la configuration). |

---

## 🔮 Feuille de Route Future

*   **Intégration Caméra**: Ajout du module caméra Raspberry Pi 3 pour l'identification faciale ou le déverrouillage par code QR (authentification secondaire).
*   **Tableau de Bord Web**: Développement d'une interface Flask/Django locale pour la consultation des journaux à distance, la gestion des utilisateurs et le déverrouillage d'urgence.
*   **Inventaire & Social**: 
    *   Suivi du nombre de capsules par canal.
    *   Fonctionnalité "Partage de capsules" : permet aux utilisateurs d'offrir leurs capsules excédentaires via l'application.
*   **Boîtier**: Conception d'un boîtier entièrement imprimé en 3D pour cacher les fils et fixer solidement le Pi et l'écran à l'unité de base.

---

## 📜 Histoire & Décisions

*   **2025-12 (S5)**: 
    *   **Refonte des Permissions**: Introduction des niveaux de rôle et de l'allocation des canaux physiques.
    *   **Amélioration de l'Interaction**: Ajout d'un menu de sélection des doigts (anglais) lors de l'enrôlement et affichage des statistiques utilisateur en temps réel.
    *   **Compatibilité Matérielle**: Migration du contrôle servo du PWM matériel vers le **PWM Logiciel (`lgpio`)**. L'horloge PWM matérielle du Raspberry Pi 5 est partagée avec le ventilateur de refroidissement, causant des conflits. Implémentation également de la logique de **Démarrage Progressif**.

*   **2024-11**: Suppression de l'Arduino de l'architecture. Le Pi 5 est assez puissant pour gérer toutes les E/S directement.

## License
MIT License
