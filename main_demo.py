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

    image = Image.new("RGB", (disp.width, disp.height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 绘制边框
    draw.rectangle((5, 5, disp.width-5, disp.height-5), outline="WHITE", width=2)
    
    # 绘制标题
    draw.text((10, 30), status_type, font=font_large, fill="WHITE")
    
    # 绘制消息 (自动换行简单处理)
    # 调整坐标以适应更大的字体
    if len(message) > 18: # 字体变大，每行字符数减少
        msg1 = message[:18]
        msg2 = message[18:]
        draw.text((10, 80), msg1, font=font_small, fill="WHITE")
        draw.text((10, 110), msg2, font=font_small, fill="WHITE")
    else:
        draw.text((10, 80), message, font=font_small, fill="WHITE")
        
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

def get_user_name(user_id):
    """根据 ID 获取用户名"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Unknown"
    except Exception:
        return "Unknown"

def main():
    print("--- 智能胶囊分配器 (Demo v2) ---")
    print("初始化硬件...")

    # 0. 初始化屏幕
    init_display_system()

        # 1. 初始化舵机 (4个通道)
    servos = {}
    try:
        # 映射: 胶囊仓ID -> ServoController
        # 恢复 4 个仓位 (软件 PWM 模式下无冲突)
        servos[1] = ServoController(channel=2) # GPIO 18
        servos[2] = ServoController(channel=0) # GPIO 12
        servos[3] = ServoController(channel=1) # GPIO 13
        servos[4] = ServoController(channel=3) # GPIO 19
        
        # 上电自检: 先解锁再锁定，确保用户看到舵机动作
        print("   ...执行舵机自检 (Unlock -> Lock)...")
        for i, s in servos.items():
            print(f"   - 舵机 {i} 解锁")
            s.unlock()
            time.sleep(0.2)
        
        time.sleep(1)
        
        for i, s in servos.items():
            print(f"   - 舵机 {i} 锁定")
            s.lock()
            time.sleep(0.2)
            
        print(f"✅ {len(servos)} 个舵机已就绪")
    except Exception as e:
        print(f"❌ 舵机初始化失败: {e}")
        return
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

    while True:
        try:
            # 尝试读取指纹图像
            if finger.get_image() != adafruit_fingerprint.OK:
                # 没有手指，稍微休息一下避免 CPU 占用过高
                # time.sleep(0.1) 
                continue

            print("\n🔍 检测到手指，正在处理...")
            update_screen("SCANNING", "Processing...", (0, 0, 100)) # 深蓝色

            # 将图像转换为特征
            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                print("❌ 图像模糊，请重试")
                update_screen("RETRY", "Bad Image", (200, 100, 0)) # 橙色
                time.sleep(1)
                update_screen("READY", "Waiting for Finger...", (0, 0, 0))
                continue

            # 搜索指纹库
            print(" -> 正在比对...")
            if finger.finger_search() != adafruit_fingerprint.OK:
                print("🚫 验证失败：未注册的指纹")
                update_screen("DENIED", "Unknown Finger", (255, 0, 0)) # 红色
                # 可以在这里闪烁红灯
                time.sleep(2) # 防止重复刷
                update_screen("READY", "Waiting for Finger...", (0, 0, 0))
                continue

            # --- 验证通过 ---
            finger_id = finger.finger_id
            confidence = finger.confidence
            
            # 查询数据库获取用户名
            user_name = get_user_name(finger_id)
            
            print(f"✅ 验证通过！用户: {user_name} (ID: #{finger_id})")
            print(f"   置信度: {confidence}")
            
            update_screen("GRANTED", f"Welcome {user_name}\nID: #{finger_id}", (0, 150, 0)) # 绿色
            
            # 记录日志
            log_access(finger_id, "FINGERPRINT_UNLOCK", "SUCCESS", f"Confidence: {confidence}")
            
            print("🔓 执行开锁...")
            # 简单演示：所有舵机一起动作
            # 实际应用中，可以根据 finger_id 决定打开哪个仓位
            for s in servos.values():
                s.unlock()
            
            print(f"⏳ 保持开启 {UNLOCK_TIME} 秒...")
            # 倒计时显示
            for i in range(UNLOCK_TIME, 0, -1):
                update_screen("OPEN", f"Closing in {i}s...", (0, 150, 0))
                time.sleep(1)
            
            print("🔒 自动上锁...")
            for s in servos.values():
                s.lock()
            
            update_screen("LOCKED", "Dispense Complete", (0, 0, 100))
            time.sleep(1)
            
            print("--- 等待下一次操作 ---")
            update_screen("READY", "Waiting for Finger...", (0, 0, 0))
            
            # 等待手指移开，防止连续触发
            while finger.get_image() != adafruit_fingerprint.NOFINGER:
                pass

        except KeyboardInterrupt:
            print("\n用户退出")
            if disp:
                disp.clear()
            break
        except Exception as e:
            print(f"运行错误: {e}")
            time.sleep(1)

    # 清理
    servo.cleanup()

if __name__ == "__main__":
    main()
