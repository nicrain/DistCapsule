import time
import serial
import sqlite3
import datetime
import threading
import queue
import adafruit_fingerprint
import lgpio
from hardware.servo_control import ServoController
from PIL import Image, ImageDraw, ImageFont
from hardware.st7789_driver import ST7789_Driver
from hardware.face_system import FaceRecognizer

# --- 配置 ---
SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 57600
UNLOCK_TIME = 5
DATABASE_NAME = "capsule_dispenser.db"
SCREEN_TIMEOUT = 30  # 无操作几秒后自动休眠
MAX_SESSION_TIME = 300 # 最长连续工作时间 (5分钟)，防止死锁
WAKE_BUTTON_PIN = 26  # 唤醒按钮 GPIO 编号

# --- 全局变量 ---
disp = None
font_large = None
font_small = None
servos = {}
h_gpio = None # lgpio handle
face_queue = queue.Queue() # 线程通信队列
face_running_event = threading.Event() # 控制人脸线程开关

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
        
        # 初始只显示一行文字，不亮背光
        print("✅ 屏幕对象初始化完成")
    except Exception as e:
        print(f"⚠️ 屏幕初始化失败: {e}")

def update_screen(status_type, message, bg_color=(0, 0, 0), progress=None, countdown=None):
    if disp is None:
        return
    # 强制开启背光
    disp.set_backlight(True)

    image = Image.new("RGB", (disp.width, disp.height), bg_color)
    draw = ImageDraw.Draw(image)
    
    draw.rectangle((5, 5, disp.width-5, disp.height-5), outline="WHITE", width=2)
    draw.text((10, 30), status_type, font=font_large, fill="WHITE")
    
    y_pos = 80
    line_height = 30
    raw_lines = message.split('\n')
    for raw_line in raw_lines:
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

    # 底部时间
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    draw.text((60, 205), current_time, font=font_small, fill="YELLOW")

    # 底部右侧倒计时
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
        print(f"⚠️ 日志记录失败: {e}")

def get_user_info(user_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name, auth_level, assigned_channel FROM Users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result if result else ("Unknown", 0, None)
    except Exception:
        return ("Unknown", 0, None)

def perform_unlock(user_id, method="Fingerprint"):
    # 暂停人脸识别线程，防止开锁过程中抢资源
    face_running_event.clear()
    
    user_name, auth_level, assigned_channel = get_user_info(user_id)
    print(f"✅ [{method}] 验证通过！用户: {user_name} (ID: #{user_id})")
    log_access(user_id, f"{method.upper()}_UNLOCK", "SUCCESS", f"Lvl:{auth_level} Ch:{assigned_channel}")
    
    bg_color = (100, 0, 100) if auth_level == 1 else (0, 150, 0)
    
    if assigned_channel and assigned_channel in servos:
        print(f"🔓 打开通道 #{assigned_channel}")
        display_msg = f"{user_name} #{assigned_channel}\n({method})"
        update_screen("GRANTED", display_msg, bg_color, progress=1.0)
        
        servos[assigned_channel].unlock()
        steps = UNLOCK_TIME * 20
        for i in range(steps, 0, -1):
            prog = i / steps
            update_screen("OPENING", display_msg, bg_color, progress=prog)
            time.sleep(0.05)
        
        print(f"🔒 关闭通道 #{assigned_channel}")
        servos[assigned_channel].lock()
        update_screen("LOCKED", "Dispense Complete", (0, 0, 100))
    else:
        if auth_level == 1:
            update_screen("ADMIN", f"Welcome Admin\n{user_name}", bg_color)
            time.sleep(3)
        else:
            print("⚠️  用户未分配通道")
            update_screen("WAITLIST", f"No Box Assigned\nHi, {user_name}", (200, 100, 0))
            time.sleep(3)
    
    print("--- 任务完成，准备进入休眠 ---")
    update_screen("READY", "System Active", (0, 0, 0))
    
    # 恢复人脸识别
    face_running_event.set()

def face_worker(face_rec):
    """后台线程：专门负责跑耗时的人脸识别"""
    print("📸 人脸识别后台线程已启动")
    while True:
        # 如果事件被清除 (clear)，则暂停扫描 (省 CPU 或防止冲突)
        if face_running_event.is_set():
            try:
                # 扫描人脸 (这是一个阻塞操作)
                face_uid = face_rec.scan()
                if face_uid:
                    # 将结果放入队列，让主线程处理
                    if face_queue.empty(): # 避免积压
                        face_queue.put(face_uid)
            except Exception as e:
                print(f"⚠️ 线程人脸错误: {e}")
                time.sleep(1)
        else:
            # 暂停时短暂休眠
            time.sleep(0.5)
        
        # 线程间歇，避免占满单核
        time.sleep(0.1)

def main():
    global servos, h_gpio
    print("--- 智能胶囊分配器 (Multi-threaded) ---")
    
    # 1. 硬件初始化
    init_display_system()
    
    try:
        # GPIO 初始化 (使用 lgpio)
        h_gpio = lgpio.gpiochip_open(0)
        # 设置唤醒按钮 (输入，下拉电阻)
        lgpio.gpio_claim_input(h_gpio, WAKE_BUTTON_PIN, lgpio.SET_PULL_DOWN)
        print(f"✅ 唤醒按钮监听 GPIO {WAKE_BUTTON_PIN} (lgpio)")

        servos[1] = ServoController(channel=2)
        servos[2] = ServoController(channel=0)
        servos[3] = ServoController(channel=1)
        servos[4] = ServoController(channel=3)
        servos[5] = ServoController(channel=5)
        print(f"✅ {len(servos)} 个舵机已就绪")
    except Exception as e:
        print(f"❌ 硬件初始化失败: {e}")
        return

    # 指纹与人脸 (放在 GPIO 初始化之后)
    time.sleep(0.5)

    try:
        uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        if finger.read_sysparam() != adafruit_fingerprint.OK:
             print("⚠️ 指纹模块连接不稳定，尝试重试...")
             time.sleep(1)
             if finger.read_sysparam() != adafruit_fingerprint.OK:
                 raise RuntimeError("无法读取指纹模块参数")
        print(f"✅ 指纹模块已就绪 (容量: {finger.library_size})")
    except Exception as e:
        print(f"❌ 指纹模块初始化失败: {e}")
        finger = None
    
    face_rec = None
    try:
        face_rec = FaceRecognizer()
        # 启动人脸识别后台线程
        t = threading.Thread(target=face_worker, args=(face_rec,), daemon=True)
        t.start()
    except Exception as e:
        print(f"⚠️ 人脸模块不可用: {e}")

    # 初始状态
    system_state = "SLEEP" # "SLEEP" 或 "ACTIVE"
    last_activity_time = 0
    session_start_time = 0
    last_clock_update = 0
    
    # 启动时先黑屏
    if disp: 
        disp.set_backlight(False)
        image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        disp.display(image)
    
    # 初始暂停人脸线程
    face_running_event.clear()

    print("💤 系统进入休眠模式，等待按钮唤醒...")

    try:
        while True:
            # --- 状态机逻辑 ---
            
            if system_state == "SLEEP":
                # 休眠模式: 暂停人脸识别，只检测按钮
                if face_running_event.is_set():
                    face_running_event.clear()

                btn_val = lgpio.gpio_read(h_gpio, WAKE_BUTTON_PIN)
                if btn_val == 1:
                    print("🔔 按钮按下！系统唤醒...")
                    system_state = "ACTIVE"
                    last_activity_time = time.time()
                    session_start_time = time.time()
                    last_clock_update = time.time()
                    
                    update_screen("HELLO", "System Waking Up...", (0, 0, 100))
                    time.sleep(0.5) 
                    update_screen("READY", "Face/Finger Ready", (0, 0, 0), countdown=SCREEN_TIMEOUT)
                    
                    # 激活人脸识别线程
                    face_running_event.set()
                else:
                    time.sleep(0.1)

            elif system_state == "ACTIVE":
                current_ts = time.time()
                elapsed = current_ts - last_activity_time
                remaining = max(0, SCREEN_TIMEOUT - elapsed)

                # 0. 强制会话超时 (5分钟)
                if current_ts - session_start_time > MAX_SESSION_TIME:
                     print("🛑 达到最大会话时间 (5分钟)，强制休眠")
                     system_state = "SLEEP"
                     if disp: disp.set_backlight(False)
                     face_running_event.clear()
                     continue

                # 1. 自动休眠超时检查
                if remaining == 0:
                    print("💤 超过 30秒 无操作，进入休眠")
                    system_state = "SLEEP"
                    if disp: disp.set_backlight(False)
                    face_running_event.clear()
                    continue
                
                # 2. 按钮续命检测 (非阻塞)
                btn_val = lgpio.gpio_read(h_gpio, WAKE_BUTTON_PIN)
                if btn_val == 1:
                    last_activity_time = current_ts
                    remaining = SCREEN_TIMEOUT
                    update_screen("EXTEND", "Time Extended!", (0, 100, 100), countdown=remaining)
                    time.sleep(0.2)
                    update_screen("READY", "Face/Finger Ready", (0, 0, 0), countdown=remaining)

                # 3. 检查人脸识别结果 (从队列获取，非阻塞)
                if not face_queue.empty():
                    face_uid = face_queue.get()
                    print(f"🤖 后台线程检测到人脸: {face_uid}")
                    perform_unlock(face_uid, method="Face")
                    last_activity_time = time.time()
                    last_clock_update = time.time()
                    # 注意: perform_unlock 内部已经处理了暂停/恢复人脸线程的逻辑
                    continue

                # 4. 指纹识别 (轻量级，依然在主线程)
                if finger:
                    try:
                        if finger.get_image() == adafruit_fingerprint.OK:
                            last_activity_time = current_ts
                            update_screen("SCANNING", "Processing...", (0, 0, 100))
                            
                            if finger.image_2_tz(1) == adafruit_fingerprint.OK:
                                if finger.finger_search() == adafruit_fingerprint.OK:
                                    perform_unlock(finger.finger_id, method="Fingerprint")
                                    last_activity_time = time.time()
                                    last_clock_update = time.time()
                                    
                                    while finger.get_image() != adafruit_fingerprint.NOFINGER:
                                        time.sleep(0.1)
                                        last_activity_time = time.time()
                                else:
                                    update_screen("DENIED", "Unknown Finger", (255, 0, 0))
                                    time.sleep(1)
                                    last_activity_time = time.time()
                                    update_screen("READY", "Try Again", (0, 0, 0), countdown=SCREEN_TIMEOUT)
                            else:
                                update_screen("RETRY", "Bad Image", (200, 100, 0))
                    except Exception:
                        pass # 忽略指纹临时错误，保持流畅

                # 5. 刷新屏幕 (极速刷新，保证倒计时线性)
                # 我们不再每秒刷新，而是每 0.1 秒检查一次，让倒计时看起来更平滑
                # 但为了不频繁刷 SPI，还是限制在秒级跳变时刷新
                if int(current_ts) != int(last_clock_update):
                    update_screen("READY", "Face/Finger Ready", (0, 0, 0), countdown=remaining)
                    last_clock_update = current_ts
                
                # 极短的休眠，保证主循环高频运行
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n用户退出")
    finally:
        if disp: disp.set_backlight(False)
        if h_gpio is not None:
            lgpio.gpiochip_close(h_gpio)
        if face_rec: face_rec.close()

if __name__ == "__main__":
    main()
