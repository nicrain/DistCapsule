import time
import serial
import sqlite3
import datetime
import threading
import adafruit_fingerprint
from hardware.servo_control import ServoController
from PIL import Image, ImageDraw, ImageFont
from hardware.st7789_driver import ST7789_Driver
from hardware.face_system import FaceRecognizer

# --- 配置 ---
SERIAL_PORT = "/dev/ttyAMA0"  # Pi 5 专用端口
BAUD_RATE = 57600
UNLOCK_TIME = 5  # 开锁保持时间 (秒)
DATABASE_NAME = "capsule_dispenser.db"
SCREEN_TIMEOUT = 30 # 30秒无操作自动息屏

# --- 屏幕相关全局变量 ---
disp = None
font_large = None
font_small = None
servos = {} # 全局舵机字典

def init_display_system():
    global disp, font_large, font_small
    try:
        disp = ST7789_Driver()
        # 加载字体
        try:
            # 增大字体大小: 标题 24->32, 正文 16->22
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        update_screen("BOOT", "System Starting...", (0, 0, 255))
        print("✅ 屏幕初始化完成")
    except Exception as e:
        print(f"⚠️ 屏幕初始化失败: {e}")

def update_screen(status_type, message, bg_color=(0, 0, 0), progress=None):
    """
    更新屏幕显示
    status_type: 状态标题 (如 "READY", "SUCCESS", "ERROR")
    message: 详细信息
    bg_color: 背景颜色 (R, G, B)
    progress: 进度条 (0.0 - 1.0), None 则不显示
    """
    if disp is None:
        return

    # 只要更新屏幕，就确保背光是亮的
    disp.set_backlight(True)

    image = Image.new("RGB", (disp.width, disp.height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 绘制边框
    draw.rectangle((5, 5, disp.width-5, disp.height-5), outline="WHITE", width=2)
    
    # 绘制标题
    draw.text((10, 30), status_type, font=font_large, fill="WHITE")
    
    # 绘制消息 (改进的换行逻辑)
    y_pos = 80
    line_height = 30  # 增加行高以防止重叠 (22pt font)
    
    # 1. 先按显式换行符分割
    raw_lines = message.split('\n')
    
    for raw_line in raw_lines:
        # 2. 如果单行太长 (>18字符)，强制切分
        while len(raw_line) > 18:
            sub_line = raw_line[:18]
            draw.text((10, y_pos), sub_line, font=font_small, fill="WHITE")
            y_pos += line_height
            raw_line = raw_line[18:]
        
        # 绘制剩余部分 (或原短行)
        if raw_line:
            draw.text((10, y_pos), raw_line, font=font_small, fill="WHITE")
            y_pos += line_height
    
    # 绘制进度条 (如果有)
    if progress is not None:
        # 进度条位置: 下移到 180 像素处，避免遮挡文字
        bar_x = 20
        bar_y = 180
        bar_w = 200
        bar_h = 10
        # 绘制背景框
        draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline="WHITE", width=1)
        # 绘制进度填充
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            draw.rectangle((bar_x + 1, bar_y + 1, bar_x + fill_w, bar_y + bar_h - 1), fill="WHITE")

    # 底部时间
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    draw.text((60, 205), current_time, font=font_small, fill="YELLOW")
    
    disp.display(image)

def log_access(user_id, event_type, status, message=""):
    """记录访问日志到数据库"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO Access_Logs (user_id, timestamp, event_type, status, detail_message)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, timestamp, event_type, status, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ 日志记录失败: {e}")

def get_user_info(user_id):
    """
    根据 ID 获取用户详细信息
    返回: (name, auth_level, assigned_channel)
    """
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
    """
    统一的开锁逻辑
    method: 'Fingerprint' 或 'Face'
    """
    user_name, auth_level, assigned_channel = get_user_info(user_id)
    
    print(f"✅ [{method}] 验证通过！用户: {user_name} (ID: #{user_id})")
    print(f"   权限: {auth_level}, 通道: {assigned_channel}")
    
    # 记录日志
    log_access(user_id, f"{method.upper()}_UNLOCK", "SUCCESS", f"Lvl:{auth_level} Ch:{assigned_channel}")
    
    # 逻辑分支
    bg_color = (0, 150, 0) # 默认绿色
    
    if auth_level == 1:
        bg_color = (100, 0, 100) # 管理员紫色
        print("👑 管理员识别")

    # 核心动作：开锁
    if assigned_channel and assigned_channel in servos:
        print(f"🔓 打开通道 #{assigned_channel}")
        
        display_msg = f"{user_name} #{assigned_channel}\n({method})"
        
        # 初始显示 (满进度)
        update_screen("GRANTED", display_msg, bg_color, progress=1.0)
        
        # 执行开锁
        servos[assigned_channel].unlock()
        
        # 倒计时逻辑
        steps = UNLOCK_TIME * 20
        for i in range(steps, 0, -1):
            prog = i / steps
            update_screen("OPENING", display_msg, bg_color, progress=prog)
            time.sleep(0.05)
        
        print(f"🔒 关闭通道 #{assigned_channel}")
        servos[assigned_channel].lock()
        update_screen("LOCKED", "Dispense Complete", (0, 0, 100))
        
    else:
        # 无通道情况
        if auth_level == 1:
            update_screen("ADMIN", f"Welcome Admin\n{user_name}", bg_color)
            time.sleep(3)
        else:
            print("⚠️  用户未分配通道")
            update_screen("WAITLIST", f"No Box Assigned\nHi, {user_name}", (200, 100, 0))
            time.sleep(3)
    
    print("--- 等待下一次操作 ---")
    update_screen("READY", "Waiting...", (0, 0, 0))

def main():
    global servos
    print("--- 智能胶囊分配器 (Demo v2.1) ---")
    print("初始化硬件...")

    # 0. 初始化屏幕
    init_display_system()

    # 1. 初始化舵机 (5个通道)
    try:
        # 映射: 胶囊仓ID -> ServoController
        # 恢复 5 个仓位 (软件 PWM 模式下无冲突)
        servos[1] = ServoController(channel=2) # GPIO 18
        servos[2] = ServoController(channel=0) # GPIO 12
        servos[3] = ServoController(channel=1) # GPIO 13
        servos[4] = ServoController(channel=3) # GPIO 19
        servos[5] = ServoController(channel=5) # GPIO 6 (Mapped in servo_control)
            
        print(f"✅ {len(servos)} 个舵机已就绪")
    except Exception as e:
        print(f"❌ 舵机初始化失败: {e}")
        return

    # 2. 初始化指纹模块
    finger = None
    try:
        uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        if finger.read_sysparam() != adafruit_fingerprint.OK:
            raise RuntimeError("无法读取指纹模块参数")
        print(f"✅ 指纹模块已就绪 (容量: {finger.library_size})")
    except Exception as e:
        print(f"❌ 指纹模块初始化失败: {e}")
        update_screen("ERROR", "Fingerprint Error", (255, 0, 0))
        # 指纹失败不一定终止，可能还能用人脸

    # 3. 初始化人脸系统
    face_rec = None
    try:
        face_rec = FaceRecognizer()
    except Exception as e:
        print(f"❌ 人脸模块初始化失败: {e}")

    update_screen("READY", "Face/Finger Ready", (0, 0, 0))

    print("\n--- 系统启动完成，等待验证 ---")
    print("(按 Ctrl+C 退出)")

    last_activity_time = time.time()
    last_clock_update = 0
    is_screen_on = True

    while True:
        try:
            current_ts = time.time()
            
            # --- 休眠检查 ---
            if is_screen_on and (current_ts - last_activity_time > SCREEN_TIMEOUT):
                print("💤 系统闲置，关闭屏幕")
                if disp: disp.set_backlight(False)
                is_screen_on = False

            # --- A. 人脸识别检查 (非阻塞, 内部有频率控制) ---
            if face_rec:
                face_uid = face_rec.scan()
                if face_uid:
                    # 唤醒屏幕
                    last_activity_time = current_ts
                    if not is_screen_on:
                        if disp: disp.set_backlight(True)
                        is_screen_on = True
                    
                    perform_unlock(face_uid, method="Face")
                    continue # 开锁后重新开始循环

            # --- B. 指纹检查 ---
            if finger and finger.get_image() == adafruit_fingerprint.OK:
                # 唤醒屏幕
                last_activity_time = current_ts
                if not is_screen_on:
                    if disp: disp.set_backlight(True)
                    is_screen_on = True
                    update_screen("SCANNING", "Processing...", (0, 0, 100))
                
                print("\n🔍 检测到手指...")
                if finger.image_2_tz(1) == adafruit_fingerprint.OK:
                    if finger.finger_search() == adafruit_fingerprint.OK:
                        # 指纹验证成功
                        perform_unlock(finger.finger_id, method="Fingerprint")
                        
                        # 等待手指移开，防止重复触发
                        while finger.get_image() != adafruit_fingerprint.NOFINGER:
                            last_activity_time = time.time()
                            time.sleep(0.1)
                        continue
                    else:
                        print("🚫 未知指纹")
                        update_screen("DENIED", "Unknown Finger", (255, 0, 0))
                        time.sleep(1)
                        update_screen("READY", "Face/Finger Ready", (0, 0, 0))
                else:
                    print("❌ 图像模糊")
                    update_screen("RETRY", "Bad Image", (200, 100, 0))

            # --- C. 空闲时钟更新 ---
            if is_screen_on and int(current_ts) != int(last_clock_update):
                # 只有在没有提示信息时才更新 "Ready" 状态下的时钟
                # 这里简单起见，假设当前是 READY 状态就刷新
                # update_screen 会刷新底部时间
                # update_screen("READY", "Face/Finger Ready", (0, 0, 0)) 
                # (频繁刷新可能会闪烁，根据 update_screen 实现逻辑决定)
                last_clock_update = current_ts
            
            # 短暂休眠，防止 CPU 100%
            time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n用户退出")
            if disp:
                disp.clear()
                disp.set_backlight(False)
            if face_rec:
                face_rec.close()
            break
        except Exception as e:
            print(f"运行错误: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()