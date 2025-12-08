import time
import serial
import sqlite3
import datetime
import adafruit_fingerprint
from servo_control import ServoController

# --- 配置 ---
SERIAL_PORT = "/dev/ttyAMA0"  # Pi 5 专用端口
BAUD_RATE = 57600
UNLOCK_TIME = 5  # 开锁保持时间 (秒)
DATABASE_NAME = "capsule_dispenser.db"

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

    # 1. 初始化舵机 (4个通道)
    servos = {}
    try:
        # 映射: 胶囊仓ID -> ServoController
        # 假设我们有4个仓位
        servos[1] = ServoController(channel=2) # GPIO 18 (原有的)
        servos[2] = ServoController(channel=0) # GPIO 12
        servos[3] = ServoController(channel=1) # GPIO 13
        servos[4] = ServoController(channel=3) # GPIO 19
        
        # 上电先全部锁住
        for s in servos.values():
            s.lock()
        print(f"✅ {len(servos)} 个舵机已就绪 (锁定状态)")
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
        
    except Exception as e:
        print(f"❌ 指纹模块初始化失败: {e}")
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

            # 将图像转换为特征
            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                print("❌ 图像模糊，请重试")
                continue

            # 搜索指纹库
            print(" -> 正在比对...")
            if finger.finger_search() != adafruit_fingerprint.OK:
                print("🚫 验证失败：未注册的指纹")
                # 可以在这里闪烁红灯
                time.sleep(1) # 防止重复刷
                continue

            # --- 验证通过 ---
            finger_id = finger.finger_id
            confidence = finger.confidence
            
            # 查询数据库获取用户名
            user_name = get_user_name(finger_id)
            
            print(f"✅ 验证通过！用户: {user_name} (ID: #{finger_id})")
            print(f"   置信度: {confidence}")
            
            # 记录日志
            log_access(finger_id, "FINGERPRINT_UNLOCK", "SUCCESS", f"Confidence: {confidence}")
            
            print("🔓 执行开锁...")
            # 简单演示：所有舵机一起动作
            # 实际应用中，可以根据 finger_id 决定打开哪个仓位
            for s in servos.values():
                s.unlock()
            
            print(f"⏳ 保持开启 {UNLOCK_TIME} 秒...")
            time.sleep(UNLOCK_TIME)
            
            print("🔒 自动上锁...")
            for s in servos.values():
                s.lock()
            
            print("--- 等待下一次操作 ---")
            # 等待手指移开，防止连续触发
            while finger.get_image() != adafruit_fingerprint.NOFINGER:
                pass

        except KeyboardInterrupt:
            print("\n用户退出")
            break
        except Exception as e:
            print(f"运行错误: {e}")
            time.sleep(1)

    # 清理
    servo.cleanup()

if __name__ == "__main__":
    main()
