import time
import serial
import sqlite3
import datetime
import adafruit_fingerprint
import os

# --- 配置 ---
SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 57600

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATABASE_NAME = os.path.join(PROJECT_ROOT, "capsule_dispenser.db")

try:
    uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
except Exception as e:
    print(f"警告 / Attention: 无法连接指纹模块 / Erreur connexion capteur ({e})")
    finger = None

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

def find_next_free_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users")
    used_ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    for i in range(1, 128):
        if i not in used_ids: return i
    return None

def get_available_channels():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT assigned_channel FROM Users WHERE assigned_channel IS NOT NULL")
    used_channels = {row[0] for row in cursor.fetchall()}
    conn.close()
    all_channels = {1, 2, 3, 4, 5}
    return sorted(list(all_channels - used_channels))

def enroll_finger_sensor(location):
    if finger is None:
        print("错误 / Erreur: 指纹硬件未连接 / Matériel déconnecté")
        return False

    print(f"\n准备录入指纹 / Enregistrement ID #{location}")
    print("请放置手指 / Placez le doigt...")

    while finger.get_image() != adafruit_fingerprint.OK: pass
    print(" -> 图像已获取 / Image acquise")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("错误: 图像太乱 / Image floue")
        return False

    print(" -> 请移开手指 / Retirez le doigt...")
    time.sleep(1)
    while finger.get_image() != adafruit_fingerprint.NOFINGER: pass

    print("请再次放置同一根手指 / Placez le même doigt...")
    while finger.get_image() != adafruit_fingerprint.OK: pass
    print(" -> 图像已获取 / Image acquise")
    if finger.image_2_tz(2) != adafruit_fingerprint.OK:
        print("错误: 图像太乱 / Image floue")
        return False

    print(" -> 创建模型 / Création modèle...")
    if finger.create_model() != adafruit_fingerprint.OK:
        print("错误: 两次指纹不匹配 / Non-concordance")
        return False
    
    print(f" -> 存储到位置 / Sauvegarde #{location}...")
    if finger.store_model(location) != adafruit_fingerprint.OK:
        print("错误: 存储错误 / Erreur stockage")
        return False

    print("指纹录入成功 / Succès!")
    return True

def delete_user_logic():
    list_users()
    try:
        uid = int(input("请输入要删除的用户 ID / Entrez ID à supprimer: "))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Users WHERE user_id=?", (uid,))
        res = cursor.fetchone()
        
        if not res:
            print("错误: 用户不存在 / Utilisateur inexistant")
            conn.close()
            return

        print(f"正在删除用户 / Suppression: {res[0]} (ID: {uid})")
        confirm = input("确认删除? / Confirmer? (y/N): ")
        if confirm.lower() == 'y':
            cursor.execute("DELETE FROM Users WHERE user_id=?", (uid,))
            conn.commit()
            if finger and finger.delete_model(uid) == adafruit_fingerprint.OK:
                print("指纹模板已从硬件删除 / Modèle supprimé du capteur")
            else:
                print("警告: 指纹硬件删除失败 / Echec suppression capteur")
            print("用户已删除 / Utilisateur supprimé")
        conn.close()
    except ValueError:
        print("无效输入 / Entrée invalide")

def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, auth_level, assigned_channel FROM Users")
    rows = cursor.fetchall()
    conn.close()

    admins, active, waitlist = [], [], []
    for row in rows:
        uid, name, level, ch = row
        user_info = f"ID: {uid:<3} | {name}"
        if level == 1: admins.append(user_info)
        elif ch is not None: active.append(f"{user_info} | Rail: {ch}")
        else: waitlist.append(user_info)

    print("\n" + "="*40)
    print(f"当前用户统计 / Stats Utilisateurs (Total: {len(rows)})")
    print("="*40)
    print(f"\n[Administrateurs] ({len(admins)})")
    for u in (admins or ["(Aucun)"]): print("  " + u)
    print(f"\n[Utilisateurs Actifs] ({len(active)})")
    for u in (active or ["(Aucun)"]): print("  " + u)
    print(f"\n[En Attente] ({len(waitlist)})")
    for u in (waitlist or ["(Aucun)"]): print("  " + u)
    print("="*40 + "\n")

def enroll_new_user(is_admin=False):
    list_users()
    print("\n--- 新用户注册 / Nouvel Utilisateur ---")
    name_input = input("请输入用户名 / Nom d'utilisateur: ").strip()
    if not name_input:
        print("错误: 用户名不能为空 / Nom vide")
        return

    finger_options = {
        "1": "Right Thumb / Pouce Droit", "2": "Right Index / Index Droit",
        "3": "Right Middle / Majeur Droit", "4": "Left Thumb / Pouce Gauche",
        "5": "Left Index / Index Gauche", "6": "Left Middle / Majeur Gauche", "7": "Other / Autre"
    }
    print("\nSelect Finger / Choisir doigt:")
    for key, val in finger_options.items(): print(f"{key}. {val}")
    f_choice = input("Choice (1-7): ").strip()
    finger_desc = finger_options.get(f_choice, "Unknown")
    if f_choice == "7":
        custom = input("Custom finger desc: ").strip()
        if custom: finger_desc = custom

    final_name = f"{name_input} ({finger_desc})"
    assigned_channel = None
    if not is_admin:
        available = get_available_channels()
        if not available:
            print("警告: 通道已满 / Plus de canal disponible!")
            confirm = input("Continuer? (y/n): ")
            if confirm.lower() != 'y': return
        else:
            print(f"可用通道 / Canaux dispos: {available}")
            while True:
                try:
                    ch_input = input(f"分配通道 / Choisir canal (0 = aucun): ")
                    ch = int(ch_input)
                    if ch == 0: break
                    if ch in available: assigned_channel = ch; break
                    print("错误: 无效选择 / Choix invalide")
                except ValueError: print("错误: 数字 / Chiffres uniquement")

    new_id = find_next_free_id()
    if new_id is None:
        print("错误: 数据库已满 / Base pleine")
        return
    print(f"分配 ID / ID Assigné: #{new_id}")

    if not enroll_finger_sensor(new_id):
        print("错误: 录入中断 / Annulé")
        return

    try:
        conn = get_db_connection()
        auth_level = 1 if is_admin else 2
        conn.execute("INSERT INTO Users (user_id, name, auth_level, assigned_channel, has_fingerprint, created_at) VALUES (?, ?, ?, ?, 1, ?)",
                    (new_id, final_name, auth_level, assigned_channel, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        print(f"用户 '{final_name}' 注册成功 / Enregistré!")
    except Exception as e:
        print(f"错误: 数据库保存失败 / Erreur sauvegarde: {e}")

def main_menu():
    while True:
        print("=== 智能胶囊分配器 / Distributeur - Gestion ===")
        print("1. 录入普通用户 / Enrôler Utilisateur")
        print("2. 录入管理员 / Enrôler Admin")
        print("3. 查看用户列表 / Liste Utilisateurs")
        print("4. 删除用户 / Supprimer Utilisateur")
        print("5. 退出 / Quitter")
        choice = input("请选择 / Choix: ")
        if choice == '1': enroll_new_user(is_admin=False)
        elif choice == '2': enroll_new_user(is_admin=True)
        elif choice == '3': list_users()
        elif choice == '4': delete_user_logic()
        elif choice == '5': print("再见 / Au revoir"); break
        else: print("无效选择 / Choix invalide")

if __name__ == "__main__":
    if finger and finger.read_sysparam() != adafruit_fingerprint.OK:
        print("错误: 无法读取指纹参数 / Erreur capteur")
    else:
        main_menu()
