# 操作与维护手册 / Manuel d'Opération et de Maintenance

**项目名称 / Projet**: DistCapsule (Smart Capsule Dispenser)
**部署位置 / Emplacement**: 教室部署 / Salle de Classe
**版本 / Version**: 1.1 (Production)

---

## 1. 快速启动 / Démarrage Rapide

### 1.1 开机 (Mise sous tension)
*   将 **USB-C 电源 (27W)** 插入树莓派。
    *   *Brancher l'alimentation USB-C (27W) au Raspberry Pi 5.*
*   将 **外部 5V 电源 ** 插入以供电舵机。
    *   *Brancher l'alimentation externe 5V pour les moteurs.*
*   **等待 10 秒**：系统后台服务启动需要时间。
    *   *Attendre 10 secondes : Le système démarre les services.*
*   当系统准备就绪，LCD 屏幕将显示欢迎画面。
    *   *L'écran LCD affichera le message de bienvenue une fois prêt.*

### 1.2 网络连接 / Connexion Réseau

系统提供两种连接模式。
*Le système propose deux modes de connexion.*

#### A. Wi-Fi 热点模式 (App 专用) / Mode Wi-Fi (Pour App Android)
这是日常使用的默认模式。
*C'est le mode par défaut pour l'utilisation normale.*

*   **SSID (Wi-Fi名称)** : `DistCapsule_Box`
*   **密码 / Mot de passe** : `capsule_admin`
*   **网关 IP / IP du Pi** : `192.168.4.1`

#### B. 以太网模式 (维护专用) / Mode Ethernet (Pour Maintenance)
用于 SSH 远程管理或系统更新。
*Utilisez ce mode pour l'administration SSH.*

*   **固定 IP / IP Statique** : `192.168.3.14`
*   **连接方式** : 使用网线连接到交换机/路由器。
    *   *Connecter le câble Ethernet au switch/routeur.*

---

## 2. 物理交互 / Interaction Physique

### 唤醒按钮 (Bouton de Réveil)
*   **位置**: 机器**背面**，位于 **5号通道 (Canal 5)** 的后方。
    *   *Emplacement : Au **DOS** de la machine, derrière le **Canal 5**.*
*   **功能**: 当屏幕熄灭进入省电模式时，**短按一次**即可唤醒系统并点亮屏幕。
    *   *Fonction : Appuyez **une fois** pour réveiller le système et allumer l'écran lorsqu'il est en veille.*

---

## 3. 管理员访问 / Accès Administrateur

如需查看日志或维护数据库，请通过 SSH 连接。
*Pour la maintenance (logs, base de données), connectez-vous via SSH.*

### 账号信息 / Identifiants

| 服务 / Service | 用户名 / User | 密码 / Password | IP 地址 / Adresse IP |
| :--- | :--- | :--- | :--- |
| **系统 (SSH)** | `cafe` | `capsule` | `192.168.3.14` (Eth) / `192.168.4.1` (Wi-Fi) |
| **Wi-Fi 热点** | - | `capsule_admin` | - |

### SSH 连接示例 / Connexion SSH

在终端中输入 / Dans le terminal :

```bash
# 通过网线连接 / Via Ethernet (Recommandé)
ssh cafe@192.168.3.14

# 通过 Wi-Fi 连接 / Via Wi-Fi
ssh cafe@192.168.4.1
```

---

## 4. 服务管理 / Gestion des Services

### 检查状态 / Vérifier l'état
```bash
sudo systemctl status capsule      # 主程序 (Hardware)
sudo systemctl status capsule_api  # API 服务 (App)
```

### 重启系统 / Redémarrer le système
如果系统卡死或 App 无法连接：
*Si le système est figé ou l'application ne se connecte pas :*
```bash
sudo reboot
```

### 安全关机 / Arrêt Propre (Shutdown)
**拔电前请务必执行关机命令**，防止损坏 SD 卡。
*Toujours éteindre proprement avant de débrancher pour éviter la corruption de la carte SD.*
```bash
sudo shutdown -h now
```

---

## 5. 数据库维护 / Dépannage Base de Données

如果需要紧急恢复管理员权限或重置通道状态。
*Commandes SQL d'urgence pour restaurer l'admin ou libérer un canal.*

**1. 进入数据库 / Entrer SQL Console**
```bash
cd ~/DistCapsule
sqlite3 capsule_dispenser.db
```

**2. 紧急恢复管理员 / Restauration Admin**
如果不小心删除了唯一的管理员 (ID 1) / *Si le compte admin a été supprimé* :
```sql
UPDATE Users SET auth_level=1 WHERE user_id=1;
```

**3. 释放卡住的通道 / Libérer un canal bloqué**
如果通道 1 显示被占用但实际上无人使用 / *Si le canal 1 est bloqué* :
```sql
UPDATE Users SET assigned_channel=NULL WHERE assigned_channel=1;
```

**4. 退出 / Quitter**
```sql
.quit
```
