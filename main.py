import time
import serial   # 串口通信库 (用于指纹模块)
import sqlite3  # SQLite 数据库库
import datetime # 时间日期库
import threading # 多线程库 (让程序能"分心"做两件事)
import queue    # 线程安全的队列 (用于线程间传话)
import adafruit_fingerprint # 指纹模块驱动
import lgpio    # 树莓派 GPIO 库 (Pi 5 专用)
from hardware.servo_control import ServoController
from PIL import Image, ImageDraw, ImageFont # 图像处理库
from hardware.st7789_driver import ST7789_Driver
from hardware.face_system import FaceRecognizer
import hardware.enrollment as enrollment

# --- 全局配置 (Constants) ---
SERIAL_PORT = "/dev/ttyAMA0" # 树莓派5 的 UART0 接口
BAUD_RATE = 57600            # 通信波特率 (必须与指纹模块一致)
UNLOCK_TIME = 5              # 舵机开锁保持时间 (秒)
DATABASE_NAME = "capsule_dispenser.db"
SCREEN_TIMEOUT = 30          # 屏幕自动休眠倒计时
MAX_SESSION_TIME = 300       # 最大活跃时间 (5分钟)，防止程序死在活跃状态耗电
WAKE_BUTTON_PIN = 26         # 唤醒按钮连接的 GPIO 引脚

# --- 全局变量 (Global Variables) ---
disp = None
font_large = None
font_small = None
servos = {}
h_gpio = None   
face_queue = queue.Queue()      
face_running_event = threading.Event() 

# 核心硬件对象 (全局化以便录入模块调用)
face_rec = None
finger = None

def init_display_system():
    global disp, font_large, font_small
    try:
        disp = ST7789_Driver()
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        print("✅ 屏幕对象初始化完成 / Écran initialisé")
    except Exception as e:
        print(f"⚠️ 屏幕初始化失败 / Erreur init écran: {e}")

def update_screen(status_type, message, bg_color=(0, 0, 0), progress=None, countdown=None):
    if disp is None: return
    disp.set_backlight(True)
    image = Image.new("RGB", (disp.width, disp.height), bg_color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((5, 5, disp.width-5, disp.height-5), outline="WHITE", width=2)
    draw.text((10, 30), status_type, font=font_large, fill="WHITE")
    
    y_pos = 80
    line_height = 30
    for raw_line in message.split('\n'):
        while len(raw_line) > 18:
            sub_line = raw_line[:18]
            draw.text((10, y_pos), sub_line, font=font_small, fill="WHITE")
            y_pos += line_height
            raw_line = raw_line[18:]
        if raw_line:
            draw.text((10, y_pos), raw_line, font=font_small, fill="WHITE")
            y_pos += line_height
    
    if progress is not None:
        bar_x, bar_y, bar_w, bar_h = 20, 180, 200, 10
        draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline="WHITE", width=1)
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            draw.rectangle((bar_x + 1, bar_y + 1, bar_x + fill_w, bar_y + bar_h - 1), fill="WHITE")

    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    draw.text((60, 205), current_time, font=font_small, fill="YELLOW")

    if countdown is not None:
        color = "RED" if countdown < 10 else "GREEN"
        draw.text((180, 205), f"{int(countdown)}s", font=font_small, fill=color)

    disp.display(image)

def log_access(user_id, event_type, status, message=""):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Access_Logs (user_id, timestamp, event_type, status, detail_message) VALUES (?, ?, ?, ?, ?)", 
                       (user_id, timestamp, event_type, status, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ 日志记录失败 / Erreur Log: {e}")

def get_user_info(user_id):
    if user_id == 0: return ("Mobile App", 1, None)
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name, auth_level, assigned_channel FROM Users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result if result else ("Unknown", 0, None)
    except Exception:
        return ("Unknown", 0, None)

def perform_unlock(user_id, method="Fingerprint", override_channel=None):
    face_running_event.clear()
    user_name, auth_level, assigned_channel = get_user_info(user_id)
    if override_channel is not None: assigned_channel = override_channel
        
    print(f"✅ [{method}] 验证通过 / Vérifié！用户: {user_name} (ID: #{user_id})")
    log_access(user_id, f"{method.upper()}_UNLOCK", "SUCCESS", f"Lvl:{auth_level} Ch:{assigned_channel}")
    
    bg_color = (100, 0, 100) if auth_level == 1 else (0, 150, 0)
    
    if assigned_channel and assigned_channel in servos:
        print(f"🔓 打开通道 #{assigned_channel} / Ouvrir Canal #{assigned_channel}")
        display_msg = f"{user_name} #{assigned_channel}\n({method})"
        update_screen("ACCES", display_msg, bg_color, progress=1.0)
        servos[assigned_channel].unlock()
        steps = UNLOCK_TIME * 20 
        for i in range(steps, 0, -1):
            prog = i / steps
            update_screen("OUVERTURE", display_msg, bg_color, progress=prog)
            time.sleep(0.05)
        print(f"🔒 关闭通道 #{assigned_channel} / Fermer Canal")
        servos[assigned_channel].lock()
        update_screen("FERME", "Fini", (0, 0, 100))
    else:
        if auth_level == 1:
            update_screen("ADMIN", f"Bienvenue\n{user_name}", bg_color)
            time.sleep(3)
        else:
            print("⚠️  用户未分配通道 / Aucun canal assigné")
            update_screen("EN ATTENTE", f"Aucun Canal\nHi, {user_name}", (200, 100, 0))
            time.sleep(3)
    
    print("--- 任务完成 / Tâche terminée ---")
    update_screen("PRET", "Systeme Actif", (0, 0, 0))
    face_running_event.set()

def check_app_commands():
    """
    处理远程指令：开锁、录入人脸、录入指纹
    """
    global face_rec, finger
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT cmd_id, command_type, target_id FROM Pending_Commands WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            cmd_id, cmd_type, target_id = row
            print(f"📲 [App] 收到指令: {cmd_type} target: {target_id}")
            cursor.execute("UPDATE Pending_Commands SET status = 'processing' WHERE cmd_id = ?", (cmd_id,))
            conn.commit()
            
            # --- 核心处理逻辑 ---
            if cmd_type == 'UNLOCK':
                perform_unlock(user_id=0, method="App", override_channel=target_id)
            
            elif cmd_type == 'ENROLL_FACE':
                print("🔄 暂停后台识别，进入人脸录入模式...")
                face_running_event.clear()
                time.sleep(0.5) 
                
                if face_rec:
                    success = enrollment.run_face_enrollment(disp, face_rec, target_id, DATABASE_NAME)
                    if success:
                        print("✅ 录入成功，重新加载人脸库...")
                        face_rec.load_faces_from_db()
                        time.sleep(3)
                        update_screen("PRET", "Scanner...", (0, 0, 0), countdown=SCREEN_TIMEOUT)
                else:
                    update_screen("ERREUR", "Camera HS", (200, 0, 0))
                    time.sleep(2)
                
                print("🔄 恢复后台识别")
                face_running_event.set()

            elif cmd_type == 'ENROLL_FINGER':
                print("🔄 暂停后台识别，进入指纹录入模式...")
                face_running_event.clear()
                time.sleep(0.5)
                
                if finger:
                    enrollment.run_finger_enrollment(disp, finger, target_id, DATABASE_NAME)
                else:
                    update_screen("ERREUR", "Capteur HS", (200, 0, 0))
                    time.sleep(2)
                
                face_running_event.set()

            elif cmd_type == 'DELETE_USER':
                print(f"🗑️ 删除用户 ID: {target_id}")
                face_running_event.clear()
                time.sleep(0.5)
                
                if finger:
                    if finger.delete_model(target_id) == adafruit_fingerprint.OK:
                        print("✅ 指纹已删除")
                    else:
                        print("⚠️ 指纹删除失败或不存在")
                
                try:
                    cursor.execute("DELETE FROM Users WHERE user_id = ?", (target_id,))
                    conn.commit()
                    print("✅ 数据库记录已删除")
                    update_screen("INFO", f"User {target_id} Deleted\nSupprime", (0, 0, 150))
                    time.sleep(2)
                except Exception as e:
                    print(f"❌ 删除失败: {e}")
                    update_screen("ERREUR", "Delete Fail", (200, 0, 0))
                
                update_screen("PRET", "Systeme Actif", (0, 0, 0))
                face_running_event.set()

            # 标记完成
            cursor.execute("UPDATE Pending_Commands SET status = 'completed' WHERE cmd_id = ?", (cmd_id,))
            conn.commit()
            conn.close()
            return True 
            
        conn.close()
    except Exception as e:
        print(f"⚠️ App指令检查失败: {e}")
    return False

def face_worker(rec_obj):
    print("📸 人脸识别后台线程已启动 / Thread Visage Démarré")
    while True:
        if face_running_event.is_set():
            try:
                face_uid = rec_obj.scan()
                if face_uid:
                    if face_queue.empty():
                        face_queue.put(face_uid)
            except Exception as e:
                print(f"⚠️ 线程人脸错误 / Erreur Thread Visage: {e}")
                time.sleep(1)
        else:
            time.sleep(0.5)
        time.sleep(0.1)

def main():
    global servos, h_gpio, face_rec, finger
    print("--- 智能胶囊分配器 / Distributeur de Capsules (Polling Mode) ---")
    
    init_display_system()
    
    try:
        h_gpio = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(h_gpio, WAKE_BUTTON_PIN, lgpio.SET_PULL_DOWN)
        print(f"✅ 唤醒按钮监听 GPIO {WAKE_BUTTON_PIN} (lgpio)")
        for i in range(1, 6):
            servos[i] = ServoController(channel=i)
        print(f"✅ {len(servos)} 个舵机已就绪 (Servo 1-5) / Servos Prêts")
    except Exception as e:
        print(f"❌ 硬件初始化失败 / Erreur init matériel: {e}")
        return

    time.sleep(0.5)

    try:
        uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        if finger.read_sysparam() != adafruit_fingerprint.OK:
             print("⚠️ 指纹模块不稳定 / Connexion capteur instable...")
        print(f"✅ 指纹模块已就绪 / Capteur Prêt")
    except Exception as e:
        print(f"❌ 指纹模块初始化失败 / Erreur init capteur: {e}")
        finger = None
    
    try:
        face_rec = FaceRecognizer()
        t = threading.Thread(target=face_worker, args=(face_rec,), daemon=True)
        t.start()
    except Exception as e:
        print(f"⚠️ 人脸模块不可用 / Module Visage indisponible: {e}")
        face_rec = None

    system_state = "SLEEP" 
    last_activity_time = 0 
    session_start_time = 0 
    last_clock_update = 0
    
    if disp: 
        disp.set_backlight(False)
        image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        disp.display(image)
    
    face_running_event.clear()
    last_btn_state = 0

    print("💤 系统进入休眠模式，等待按钮唤醒... / Mode Veille (Attente bouton)...")

    try:
        while True:
            btn_val = lgpio.gpio_read(h_gpio, WAKE_BUTTON_PIN)
            
            # --- 按钮检测 ---
            # (已移除长按二维码逻辑，保持简单的唤醒功能)

            # --- 检查远程指令 ---
            app_cmd_processed = check_app_commands()
            
            if system_state == "SLEEP":
                if face_running_event.is_set(): face_running_event.clear()

                if app_cmd_processed: 
                    now = time.time()
                    system_state = "ACTIVE"
                    last_activity_time = now
                    session_start_time = now
                    last_clock_update = now
                    if not face_running_event.is_set(): face_running_event.set()

                elif btn_val == 1:
                    print("🔔 按钮按下！系统唤醒... / Réveil système...")
                    now = time.time()
                    system_state = "ACTIVE"
                    last_activity_time = now
                    session_start_time = now
                    last_clock_update = now
                    update_screen("PRET", "Scanner...", (0, 0, 0), countdown=SCREEN_TIMEOUT)
                    face_running_event.set()
                else:
                    time.sleep(0.1)

            elif system_state == "ACTIVE":
                if app_cmd_processed:
                    last_activity_time = time.time() 

                current_ts = time.time()
                elapsed = current_ts - last_activity_time
                remaining = max(0, SCREEN_TIMEOUT - elapsed)

                if current_ts - session_start_time > MAX_SESSION_TIME:
                     print("🛑 强制休眠 / Timeout Session")
                     system_state = "SLEEP"
                     if disp: disp.set_backlight(False)
                     face_running_event.clear()
                     continue

                if remaining == 0:
                    print("💤 自动休眠 / Timeout Inactivité")
                    system_state = "SLEEP"
                    if disp: disp.set_backlight(False)
                    face_running_event.clear()
                    continue
                
                if btn_val == 1 and last_btn_state == 0:
                    last_activity_time = time.time()
                    remaining = SCREEN_TIMEOUT
                    update_screen("PROLONGE", "+30 Sec", (0, 100, 100), countdown=remaining)
                
                if not face_queue.empty():
                    face_uid = face_queue.get()
                    print(f"🤖 人脸检测: {face_uid}")
                    perform_unlock(face_uid, method="Face")
                    last_activity_time = time.time()
                    continue

                if finger:
                    try:
                        if finger.get_image() == adafruit_fingerprint.OK:
                            update_screen("SCAN", "Analyse...", (0, 0, 100))
                            if finger.image_2_tz(1) == adafruit_fingerprint.OK:
                                if finger.finger_search() == adafruit_fingerprint.OK:
                                    perform_unlock(finger.finger_id, method="Fingerprint")
                                    last_activity_time = time.time()
                                    while finger.get_image() != adafruit_fingerprint.NOFINGER:
                                        time.sleep(0.1)
                                else:
                                    update_screen("REFUSE", "Inconnu", (255, 0, 0))
                                    time.sleep(1)
                                    update_screen("PRET", "Reessayer", (0, 0, 0), countdown=SCREEN_TIMEOUT)
                            else:
                                update_screen("ERREUR", "Image HS", (200, 100, 0))
                    except Exception: pass

                if int(current_ts) != int(last_clock_update):
                    update_screen("PRET", "Scanner...", (0, 0, 0), countdown=remaining)
                    last_clock_update = current_ts
                
            last_btn_state = btn_val
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n用户退出 / Sortie utilisateur")
    finally:
        if disp: disp.set_backlight(False)
        if h_gpio is not None: lgpio.gpiochip_close(h_gpio)
        if face_rec: face_rec.close()

if __name__ == "__main__":
    main()
