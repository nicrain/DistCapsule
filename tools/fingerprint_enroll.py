import time
import serial
import sqlite3
import datetime
import adafruit_fingerprint
import os

# --- 配置 ---
# 根据实际情况调整端口，Pi 5 通常是 /dev/ttyAMA0
SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 57600

# 动态获取数据库绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATABASE_NAME = os.path.join(PROJECT_ROOT, "capsule_dispenser.db")

# 初始化串口和指纹模块
try:
    uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
except Exception as e:
    print(f"⚠️  警告 / Attention: 无法连接指纹模块 / Erreur connexion capteur ({e})")
    print("这可能是在非 Pi 环境下运行，或者接线错误。")
    finger = None

# ...

def enroll_finger_sensor(location):
    """交互式指纹录入流程"""
    if finger is None:
        print("❌ 错误 / Erreur: 指纹硬件未连接 / Matériel déconnecté")
        return False

    print(f"\n👉 准备录入指纹 / Enregistrement ID #{location}")
    print("请放置手指 / Placez le doigt...")

    # 第一次采集
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print(" -> 图像已获取 / Image acquise")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("❌ 图像太乱 / Image floue")
        return False

    print(" -> 请移开手指 / Retirez le doigt...")
    time.sleep(1)
    while finger.get_image() != adafruit_fingerprint.NOFINGER:
        pass

    # 第二次采集
    print("请再次放置同一根手指 / Placez le même doigt...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print(" -> 图像已获取 / Image acquise")
    if finger.image_2_tz(2) != adafruit_fingerprint.OK:
        print("❌ 图像太乱 / Image floue")
        return False

    # 匹配与存储
    print(" -> 创建模型 / Création modèle...")
    if finger.create_model() != adafruit_fingerprint.OK:
        print("❌ 两次指纹不匹配 / Non-concordance")
        return False
    
    print(f" -> 存储到位置 / Sauvegarde #{location}...")
    if finger.store_model(location) != adafruit_fingerprint.OK:
        print("❌ 存储错误 / Erreur stockage")
        return False

    print("✅ 指纹录入成功 / Succès!")
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
            print("❌ 用户不存在 / Utilisateur inexistant")
            conn.close()
            return

        print(f"⚠️  正在删除用户 / Suppression: {res[0]} (ID: {uid})")
        confirm = input("确认删除? / Confirmer? (y/N): ")
        if confirm.lower() == 'y':
            # 1. 删数据库
            cursor.execute("DELETE FROM Users WHERE user_id=?", (uid,))
            conn.commit()
            
            # 2. 删指纹模块
            if finger and finger.delete_model(uid) == adafruit_fingerprint.OK:
                print("✅ 指纹模板已从硬件删除 / Modèle supprimé du capteur")
            else:
                print("⚠️  指纹硬件删除失败 (可能已为空) / Echec suppression capteur")
                
            print("✅ 用户已删除 / Utilisateur supprimé")
        
        conn.close()
    except ValueError:
        print("无效输入 / Entrée invalide")

# ... (list_users is fine, headers can stay or be updated if needed, but skipping for brevity as context is clearer in enrollment)

def enroll_new_user(is_admin=False):
    """注册新用户主逻辑"""
    # 1. 先列出当前用户
    list_users()

    print("\n--- 新用户注册 / Nouvel Utilisateur ---")
    
    # 2. 基本信息录入
    name_input = input("请输入用户名 (例: Tom) / Nom d'utilisateur: ").strip()
    if not name_input:
        print("❌ 用户名不能为空 / Nom vide")
        return

    # 手指选择菜单 (Option translation not critical, context is clear)
    finger_options = {
        "1": "Right Thumb / Pouce Droit",
        "2": "Right Index / Index Droit",
        "3": "Right Middle / Majeur Droit",
        "4": "Left Thumb / Pouce Gauche",
        "5": "Left Index / Index Gauche",
        "6": "Left Middle / Majeur Gauche",
        "7": "Other / Autre"
    }
    
    print("\nSelect Finger / Choisir doigt:")
    for key, val in finger_options.items():
        print(f"{key}. {val}")
    
    f_choice = input("Select finger (1-7): ").strip()
    finger_desc = finger_options.get(f_choice, "Unknown")
    
    # 如果选择 Other，允许手动输入
    if f_choice == "7":
        custom = input("Enter custom finger description: ").strip()
        if custom:
            finger_desc = custom

    # 将手指信息合并到名字中显示，方便查看
    final_name = f"{name_input} ({finger_desc})"

    # 3. 通道分配 (仅普通用户)
    assigned_channel = None
    if not is_admin:
        available = get_available_channels()
        if not available:
            print("⚠️  警告: 所有 5 个通道均已分配！ / Plus de canal disponible!")
            print("该用户将作为 [候补/无通道] 用户注册。")
            confirm = input("继续吗? / Continuer? (y/n): ")
            if confirm.lower() != 'y':
                return
        else:
            print(f"可用通道 / Canaux dispos: {available}")
            while True:
                try:
                    ch_input = input(f"请分配一个通道 {available} (输入 0 不分配) / Choisir canal (0 = aucun): ")
                    ch = int(ch_input)
                    if ch == 0:
                        break
                    if ch in available:
                        assigned_channel = ch
                        break
                    print("❌ 无效的通道选择 / Choix invalide")
                except ValueError:
                    print("❌ 请输入数字 / Chiffres uniquement")

    # 3. 寻找空闲 ID
    new_id = find_next_free_id()
    if new_id is None:
        print("❌ 错误: 数据库/指纹库已满 / Base pleine (Max 127)")
        return
    print(f"分配 ID / ID Assigné: #{new_id}")

    # 4. 录入指纹
    if not enroll_finger_sensor(new_id):
        print("❌ 录入中断 / Annulé")
        return

    # 5. 保存数据库
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        auth_level = 1 if is_admin else 2
        cursor.execute("""
            INSERT INTO Users (user_id, name, auth_level, assigned_channel, has_fingerprint, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (new_id, final_name, auth_level, assigned_channel, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        print(f"✅ 用户 '{final_name}' 注册成功 / Enregistré!")
        
        if assigned_channel:
            print(f"🚀 已分配通道 / Canal: #{assigned_channel}")
        else:
            print("ℹ️  未分配通道 / Aucun canal")
            
    except Exception as e:
        print(f"❌ 数据库保存失败 / Erreur sauvegarde: {e}")

def main_menu():
    while True:
        print("=== 智能胶囊分配器 / Distributeur - 用户管理 ===")
        print("1. 录入普通用户 (分配通道) / Enrôler Utilisateur")
        print("2. 录入管理员 (无通道) / Enrôler Admin")
        print("3. 查看用户列表 / Liste Utilisateurs")
        print("4. 删除用户 / Supprimer Utilisateur")
        print("5. 退出 / Quitter")
        
        choice = input("请选择 / Choix: ")
        
        if choice == '1':
            enroll_new_user(is_admin=False)
        elif choice == '2':
            # 检查是否已有管理员? 题目说 "1个超级管理员"，但逻辑上不强制限制只能录一个，只是一种角色
            enroll_new_user(is_admin=True)
        elif choice == '3':
            list_users()
        elif choice == '4':
            delete_user_logic()
        elif choice == '5':
            print("再见 / Au revoir")
            break
        else:
            print("无效选择 / Choix invalide")

if __name__ == "__main__":
    if finger and finger.read_sysparam() != adafruit_fingerprint.OK:
        print("❌ 无法读取指纹参数，请检查接线")
    else:
        main_menu()