import time
import serial
import sqlite3
import datetime
import threading
import adafruit_fingerprint
from servo_control import ServoController
from PIL import Image, ImageDraw, ImageFont
from st7789_driver import ST7789_Driver

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

def update_screen(status_type, message, bg_color=(0, 0, 0)):
    """
    更新屏幕显示
    status_type: 状态标题 (如 "READY", "SUCCESS", "ERROR")
    message: 详细信息
    bg_color: 背景颜色 (R, G, B)
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
        
    # 底部时间
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    draw.text((60, 190), current_time, font=font_small, fill="YELLOW")
    
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

def main():
    print("--- 智能胶囊分配器 (Demo v2) ---")
    print("初始化硬件...")

    # 0. 初始化屏幕
    init_display_system()

    # 1. 初始化舵机 (5个通道)
    servos = {}
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
    try:
        uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        
        if finger.read_sysparam() != adafruit_fingerprint.OK:
            raise RuntimeError("无法读取指纹模块参数")
            
        print(f"✅ 指纹模块已就绪 (容量: {finger.library_size})")
        update_screen("READY", "Waiting for Finger...", (0, 0, 0))
        
    except Exception as e:
        print(f"❌ 指纹模块初始化失败: {e}")
        update_screen("ERROR", "Fingerprint Error", (255, 0, 0))
        return

    print("\n--- 系统启动完成，等待指纹 ---")
    print("(按 Ctrl+C 退出)")

    # 休眠相关变量
    last_activity_time = time.time()
    last_clock_update = 0
    is_screen_on = True

    while True:
        try:
            current_ts = time.time()
            
            # 1. 检查是否需要休眠
            if is_screen_on and (current_ts - last_activity_time > SCREEN_TIMEOUT):
                print("💤 系统闲置，关闭屏幕")
                if disp: disp.set_backlight(False)
                is_screen_on = False

            # 2. 尝试读取指纹图像 (这是最耗时的操作，也是唤醒源)
            if finger.get_image() != adafruit_fingerprint.OK:
                
                # --- 新增: 空闲时更新时钟 (检测秒数变化) ---
                # 使用 int(current_ts) != int(last_clock_update) 确保每秒只跳动一次，且不丢秒
                if is_screen_on and int(current_ts) != int(last_clock_update):
                    update_screen("READY", "Waiting...", (0, 0, 0))
                    last_clock_update = current_ts
                
                # 关键修改: 增加延时以降低 CPU 占用
                time.sleep(0.1) 
                continue
            
            # --- 检测到手指 ---
            
            # 唤醒屏幕
            last_activity_time = time.time() # 更新活动时间
            if not is_screen_on:
                print("💡 唤醒屏幕")
                if disp: disp.set_backlight(True)
                is_screen_on = True
                # 可选: 唤醒时重绘提示信息
                update_screen("SCANNING", "Processing...", (0, 0, 100))
            
            print("\n🔍 检测到手指，正在处理...")
            update_screen("SCANNING", "Processing...", (0, 0, 100)) # 深蓝色

            # 将图像转换为特征
            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                print("❌ 图像模糊，请重试")
                update_screen("RETRY", "Bad Image", (200, 100, 0)) # 橙色
                time.sleep(1)
                update_screen("READY", "Waiting...", (0, 0, 0))
                continue

            # 搜索指纹库
            print(" -> 正在比对...")
            if finger.finger_search() != adafruit_fingerprint.OK:
                print("🚫 验证失败：未注册的指纹")
                update_screen("DENIED", "Unknown Finger", (255, 0, 0)) # 红色
                time.sleep(2)
                update_screen("READY", "Waiting...", (0, 0, 0))
                continue

            # --- 验证通过 ---
            finger_id = finger.finger_id
            confidence = finger.confidence
            
            # 获取用户信息
            user_name, auth_level, assigned_channel = get_user_info(finger_id)
            
            print(f"✅ 验证通过！用户: {user_name} (ID: #{finger_id})")
            print(f"   权限: {auth_level}, 通道: {assigned_channel}")
            
            # 记录日志
            log_access(finger_id, "FINGERPRINT_UNLOCK", "SUCCESS", f"Lvl:{auth_level} Ch:{assigned_channel}")
            
            # 逻辑分支
            role_title = "User"
            bg_color = (0, 150, 0) # 默认绿色
            
            if auth_level == 1:
                role_title = "Admin"
                bg_color = (100, 0, 100) # 管理员紫色
                print("👑 管理员识别")

            # 2. 核心动作：开锁 (无论角色，只要有通道就开)
            if assigned_channel and assigned_channel in servos:
                print(f"🔓 打开通道 #{assigned_channel}")
                
                # 组合显示: "Admin Open #1" 或 "Open Box #1"
                display_msg = f"{role_title} Open #{assigned_channel}\n{user_name}"
                update_screen("GRANTED", display_msg, bg_color)
                
                # 执行开锁
                servos[assigned_channel].unlock()
                
                # 倒计时逻辑：合并显示用户信息和倒计时
                for i in range(UNLOCK_TIME, 0, -1):
                    # 组合消息：角色+通道、用户名、倒计时
                    combined_msg = f"{role_title} Open #{assigned_channel}\n{user_name}\nClosing in {i}s..."
                    update_screen("OPENING", combined_msg, bg_color)
                    time.sleep(1)
                
                print(f"🔒 关闭通道 #{assigned_channel}")
                servos[assigned_channel].lock()
                update_screen("LOCKED", "Dispense Complete", (0, 0, 100))
                
            else:
                # 3. 无通道情况
                if auth_level == 1:
                    # 管理员无通道 -> 仅显示欢迎
                    update_screen("ADMIN", f"Welcome Admin\n{user_name}", bg_color)
                    time.sleep(3)
                else:
                    # 普通用户无通道 -> 候补提示
                    print("⚠️  用户未分配通道")
                    update_screen("WAITLIST", f"No Box Assigned\nHi, {user_name}", (200, 100, 0)) # 橙色
                    time.sleep(3)
            
            # 操作完成后更新一次活动时间，确保不会马上黑屏
            last_activity_time = time.time()
            time.sleep(1)
            print("--- 等待下一次操作 ---")
            update_screen("READY", "Waiting...", (0, 0, 0))
            
            # 等待手指移开
            while finger.get_image() != adafruit_fingerprint.NOFINGER:
                # 此时也更新时间，防止一直按着时息屏
                last_activity_time = time.time()
                time.sleep(0.1) 

        except KeyboardInterrupt:
            print("\n用户退出")
            if disp:
                disp.clear() # 先清空显存
                disp.set_backlight(False) # 再彻底关闭背光
            break
        except Exception as e:
            print(f"运行错误: {e}")
            time.sleep(1)

    # 清理
    # servo.cleanup() 

if __name__ == "__main__":
    main()
