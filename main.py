import time
import serial
import sqlite3
import datetime
import threading
import adafruit_fingerprint
import RPi.GPIO as GPIO
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
WAKE_BUTTON_PIN = 26  # 唤醒按钮 GPIO 编号

# --- 全局变量 ---
disp = None
font_large = None
font_small = None
servos = {}

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

def update_screen(status_type, message, bg_color=(0, 0, 0), progress=None):
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

    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    draw.text((60, 205), current_time, font=font_small, fill="YELLOW")
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

def main():
    global servos
    print("--- 智能胶囊分配器 (Button Wakeup) ---")
    
    # 1. 硬件初始化
    init_display_system()
    
    try:
        # GPIO 初始化 (BCM 模式)
        GPIO.setmode(GPIO.BCM)
        # 设置唤醒按钮 (下拉电阻，按下为 HIGH)
        GPIO.setup(WAKE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print(f"✅ 唤醒按钮监听 GPIO {WAKE_BUTTON_PIN}")

        servos[1] = ServoController(channel=2)
        servos[2] = ServoController(channel=0)
        servos[3] = ServoController(channel=1)
        servos[4] = ServoController(channel=3)
        servos[5] = ServoController(channel=5)
        print(f"✅ {len(servos)} 个舵机已就绪")
    except Exception as e:
        print(f"❌ 硬件初始化失败: {e}")
        return

    # 指纹与人脸
    uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
    
    face_rec = None
    try:
        face_rec = FaceRecognizer()
    except Exception as e:
        print(f"⚠️ 人脸模块不可用: {e}")

    # 初始状态
    system_state = "SLEEP" # "SLEEP" 或 "ACTIVE"
    last_activity_time = 0
    
    # 启动时先黑屏
    if disp: 
        disp.set_backlight(False)
        # 清屏
        image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        disp.display(image)

    print("💤 系统进入休眠模式，等待按钮唤醒...")

    try:
        while True:
            # --- 状态机逻辑 ---
            
            if system_state == "SLEEP":
                # 休眠模式下只检测按钮
                # 防抖动检测
                if GPIO.input(WAKE_BUTTON_PIN) == GPIO.HIGH:
                    print("🔔 按钮按下！系统唤醒...")
                    system_state = "ACTIVE"
                    last_activity_time = time.time()
                    update_screen("HELLO", "System Waking Up...", (0, 0, 100))
                    time.sleep(0.5) # 消除按键抖动
                    update_screen("READY", "Face/Finger Ready", (0, 0, 0))
                else:
                    # 极低功耗循环
                    time.sleep(0.1)

            elif system_state == "ACTIVE":
                current_ts = time.time()

                # 1. 超时检查
                if current_ts - last_activity_time > SCREEN_TIMEOUT:
                    print("💤 超过 30秒 无操作，进入休眠")
                    system_state = "SLEEP"
                    if disp: disp.set_backlight(False)
                    continue

                # 2. 人脸识别
                if face_rec:
                    face_uid = face_rec.scan()
                    if face_uid:
                        last_activity_time = current_ts # 重置计时
                        perform_unlock(face_uid, method="Face")
                        continue

                # 3. 指纹识别
                if finger.read_sysparam() == adafruit_fingerprint.OK:
                    if finger.get_image() == adafruit_fingerprint.OK:
                        last_activity_time = current_ts # 重置计时
                        update_screen("SCANNING", "Processing...", (0, 0, 100))
                        
                        if finger.image_2_tz(1) == adafruit_fingerprint.OK:
                            if finger.finger_search() == adafruit_fingerprint.OK:
                                perform_unlock(finger.finger_id, method="Fingerprint")
                                # 等手指拿开
                                while finger.get_image() != adafruit_fingerprint.NOFINGER:
                                    time.sleep(0.1)
                                    last_activity_time = time.time()
                            else:
                                update_screen("DENIED", "Unknown Finger", (255, 0, 0))
                                time.sleep(1)
                                update_screen("READY", "Try Again", (0, 0, 0))
                        else:
                            update_screen("RETRY", "Bad Image", (200, 100, 0))

                # 4. 刷新时间 (降低刷新率避免闪烁)
                if int(current_ts * 10) % 10 == 0: 
                     # 可以在这里更新时钟，但为了效率略过频繁重绘
                     pass
                
                time.sleep(0.01) # 活跃模式稍微快一点的循环

    except KeyboardInterrupt:
        print("\n用户退出")
    finally:
        if disp: disp.set_backlight(False)
        GPIO.cleanup()
        if face_rec: face_rec.close()

if __name__ == "__main__":
    main()
