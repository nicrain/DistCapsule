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

# --- 全局配置 (Constants) ---
# 大写字母命名变量通常表示"常量"，程序运行中不应修改它们
SERIAL_PORT = "/dev/ttyAMA0" # 树莓派5 的 UART0 接口
BAUD_RATE = 57600            # 通信波特率 (必须与指纹模块一致)
UNLOCK_TIME = 5              # 舵机开锁保持时间 (秒)
DATABASE_NAME = "capsule_dispenser.db"
SCREEN_TIMEOUT = 30          # 屏幕自动休眠倒计时
MAX_SESSION_TIME = 300       # 最大活跃时间 (5分钟)，防止程序死在活跃状态耗电
WAKE_BUTTON_PIN = 26         # 唤醒按钮连接的 GPIO 引脚

# --- 全局变量 (Global Variables) ---
# 这些变量会被多个函数共享和修改
disp = None
font_large = None
font_small = None
servos = {}     # 字典，存储所有舵机对象 {1: ServoObj, 2: ServoObj...}
h_gpio = None   # lgpio 的句柄
face_queue = queue.Queue()      # 消息队列：后台线程把识别结果扔这里，主线程来取
face_running_event = threading.Event() # 事件标志：控制后台线程是"跑"还是"停"

def init_display_system():
    global disp, font_large, font_small
    try:
        disp = ST7789_Driver()
        try:
            # 尝试加载漂亮的 TrueType 字体
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        except:
            # 如果找不到字体文件，回退到系统默认的简陋字体
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        print("✅ 屏幕对象初始化完成")
    except Exception as e:
        print(f"⚠️ 屏幕初始化失败: {e}")

def update_screen(status_type, message, bg_color=(0, 0, 0), progress=None, countdown=None):
    """
    统一的屏幕刷新函数
    :param status_type: 大标题 (如 "GRANTED", "DENIED")
    :param message: 详细信息 (支持换行)
    :param bg_color: 背景颜色 (R, G, B) 元组
    :param progress: 进度条 (0.0 - 1.0)，None 表示不显示
    :param countdown: 右下角倒计时秒数
    """
    if disp is None:
        return
    # 只要刷新屏幕，就强制点亮背光
    disp.set_backlight(True)

    # 1. 创建一块新的画布 (Canvas)
    image = Image.new("RGB", (disp.width, disp.height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 2. 绘制边框和标题
    draw.rectangle((5, 5, disp.width-5, disp.height-5), outline="WHITE", width=2)
    draw.text((10, 30), status_type, font=font_large, fill="WHITE")
    
    # 3. 绘制多行文本 (自动换行逻辑)
    y_pos = 80
    line_height = 30
    raw_lines = message.split('\n')
    for raw_line in raw_lines:
        # 如果一行超过 18 个字，强制切断换行
        while len(raw_line) > 18:
            sub_line = raw_line[:18]
            draw.text((10, y_pos), sub_line, font=font_small, fill="WHITE")
            y_pos += line_height
            raw_line = raw_line[18:]
        if raw_line:
            draw.text((10, y_pos), raw_line, font=font_small, fill="WHITE")
            y_pos += line_height
    
    # 4. 绘制进度条 (如果有)
    if progress is not None:
        bar_x, bar_y, bar_w, bar_h = 20, 180, 200, 10
        draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline="WHITE", width=1)
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            draw.rectangle((bar_x + 1, bar_y + 1, bar_x + fill_w, bar_y + bar_h - 1), fill="WHITE")

    # 5. 绘制底部状态栏 (时间和倒计时)
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    draw.text((60, 205), current_time, font=font_small, fill="YELLOW")

    if countdown is not None:
        # 倒计时少于 10 秒变红，提醒用户
        color = "RED" if countdown < 10 else "GREEN"
        draw.text((180, 205), f"{int(countdown)}s", font=font_small, fill=color)

    # 6. 将画好的图推送到硬件显示
    disp.display(image)

def log_access(user_id, event_type, status, message=""):
    """
    记录访问日志到 SQLite 数据库
    """
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 使用 ? 占位符防止 SQL 注入
        cursor.execute("INSERT INTO Access_Logs (user_id, timestamp, event_type, status, detail_message) VALUES (?, ?, ?, ?, ?)", 
                       (user_id, timestamp, event_type, status, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ 日志记录失败: {e}")

def get_user_info(user_id):
    """
    查询用户信息
    返回: (name, auth_level, assigned_channel) 元组
    """
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name, auth_level, assigned_channel FROM Users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        # 三元表达式：如果查到了就返回结果，查不到就返回默认值
        return result if result else ("Unknown", 0, None)
    except Exception:
        return ("Unknown", 0, None)

def perform_unlock(user_id, method="Fingerprint"):
    """
    执行开锁流程
    这是程序中最关键的业务逻辑：验证 -> 记录 -> UI反馈 -> 物理开锁
    """
    # 1. 暂停后台人脸识别，防止它抢占 CPU 资源导致 UI 卡顿
    face_running_event.clear()
    
    # 2. 获取权限信息
    user_name, auth_level, assigned_channel = get_user_info(user_id)
    print(f"✅ [{method}] 验证通过！用户: {user_name} (ID: #{user_id})")
    
    # 3. 记日志
    log_access(user_id, f"{method.upper()}_UNLOCK", "SUCCESS", f"Lvl:{auth_level} Ch:{assigned_channel}")
    
    # 根据权限决定背景色 (管理员紫色，普通用户绿色)
    bg_color = (100, 0, 100) if auth_level == 1 else (0, 150, 0)
    
    # 4. 判断是否需要开锁
    if assigned_channel and assigned_channel in servos:
        print(f"🔓 打开通道 #{assigned_channel}")
        display_msg = f"{user_name} #{assigned_channel}\n({method})"
        
        # 显示开锁动画
        update_screen("GRANTED", display_msg, bg_color, progress=1.0)
        
        servos[assigned_channel].unlock()
        
        # 倒计时进度条效果
        steps = UNLOCK_TIME * 20 # 5秒 * 20fps = 100帧
        for i in range(steps, 0, -1):
            prog = i / steps
            update_screen("OPENING", display_msg, bg_color, progress=prog)
            time.sleep(0.05)
        
        print(f"🔒 关闭通道 #{assigned_channel}")
        servos[assigned_channel].lock()
        update_screen("LOCKED", "Dispense Complete", (0, 0, 100))
    else:
        # 如果是管理员或者未分配胶囊的用户
        if auth_level == 1:
            update_screen("ADMIN", f"Welcome Admin\n{user_name}", bg_color)
            time.sleep(3)
        else:
            print("⚠️  用户未分配通道")
            update_screen("WAITLIST", f"No Box Assigned\nHi, {user_name}", (200, 100, 0))
            time.sleep(3)
    
    print("--- 任务完成，准备进入休眠 ---")
    update_screen("READY", "System Active", (0, 0, 0))
    
    # 5. 任务结束，恢复后台人脸识别
    face_running_event.set()

def face_worker(face_rec):
    """
    后台线程：专门负责跑耗时的人脸识别 (Producer)
    如果不把它放在单独线程里，主界面的倒计时就会一卡一卡的。
    """
    print("📸 人脸识别后台线程已启动")
    while True:
        # face_running_event 就像一个红绿灯
        # is_set() == True (绿灯): 全速工作
        # is_set() == False (红灯): 休息
        if face_running_event.is_set():
            try:
                # 扫描人脸 (这是一个阻塞操作，可能耗时 0.2~0.5秒)
                face_uid = face_rec.scan()
                if face_uid:
                    # 将结果放入队列 (Queue)，发给主线程处理
                    if face_queue.empty(): # 避免积压
                        face_queue.put(face_uid)
            except Exception as e:
                print(f"⚠️ 线程人脸错误: {e}")
                time.sleep(1)
        else:
            # 暂停时短暂休眠，避免空转烧 CPU
            time.sleep(0.5)
        
        # 线程间歇，让出 CPU 给其他任务
        time.sleep(0.1)

def main():
    global servos, h_gpio
    print("--- 智能胶囊分配器 (Polling Mode) ---")
    
    # 1. 硬件初始化 (Display, GPIO, Servos)
    init_display_system()
    
    try:
        # GPIO 初始化 (使用 lgpio)
        h_gpio = lgpio.gpiochip_open(0)
        # 设置唤醒按钮 (输入模式，并开启下拉电阻)
        # 下拉电阻(Pull Down)意味着：没按按钮时，电压被拉低到 0 (GND)，按下去才变 1 (3.3V)
        lgpio.gpio_claim_input(h_gpio, WAKE_BUTTON_PIN, lgpio.SET_PULL_DOWN)
        print(f"✅ 唤醒按钮监听 GPIO {WAKE_BUTTON_PIN} (lgpio)")

        # 初始化 5 个舵机
        for i in range(1, 6):
            servos[i] = ServoController(channel=i)
        print(f"✅ {len(servos)} 个舵机已就绪 (Servo 1-5)")
    except Exception as e:
        print(f"❌ 硬件初始化失败: {e}")
        return

    # 指纹与人脸模块通常比较慢，放在基础 GPIO 之后
    time.sleep(0.5)

    try:
        uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        # 尝试读取参数来验证模块是否连接正常
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
        # 启动人脸识别后台线程 (Daemon=True 表示主程序退出时它也会自动死掉)
        t = threading.Thread(target=face_worker, args=(face_rec,), daemon=True)
        t.start()
    except Exception as e:
        print(f"⚠️ 人脸模块不可用: {e}")

    # --- 状态机初始状态 ---
    system_state = "SLEEP" # 两种状态: "SLEEP" (省电/黑屏) 或 "ACTIVE" (工作/亮屏)
    last_activity_time = 0 # 上次有人操作的时间戳
    session_start_time = 0 # 本次唤醒的时间戳
    last_clock_update = 0
    
    # 启动时先强制黑屏
    if disp: 
        disp.set_backlight(False)
        image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        disp.display(image)
    
    # 初始暂停人脸线程
    face_running_event.clear()
    
    # 按钮状态记忆 (用于上升沿检测)
    last_btn_state = 0

    print("💤 系统进入休眠模式，等待按钮唤醒...")

    try:
        while True:
            # --- 统一读取硬件状态 ---
            btn_val = lgpio.gpio_read(h_gpio, WAKE_BUTTON_PIN)
            
            # --- 状态机逻辑 (State Machine) ---
            
            if system_state == "SLEEP":
                # --- 休眠模式 ---
                # 只有一件事要做：检测按钮是否按下。
                # 暂停人脸识别以节省资源
                if face_running_event.is_set():
                    face_running_event.clear()

                # 简单轮询 (Polling)
                if btn_val == 1:
                    print("🔔 按钮按下！系统唤醒...")
                    
                    # 切换状态
                    now = time.time()
                    system_state = "ACTIVE"
                    last_activity_time = now
                    session_start_time = now
                    last_clock_update = now
                    
                    update_screen("READY", "Face/Finger Ready", (0, 0, 0), countdown=SCREEN_TIMEOUT)
                    
                    # 激活人脸识别线程
                    face_running_event.set()
                else:
                    # 没按按钮就睡 0.1秒 再看，避免 CPU 100% 占用
                    time.sleep(0.1)

            elif system_state == "ACTIVE":
                # --- 活跃模式 ---
                # 需要做的事：倒计时检查、按钮续命、检查人脸结果、检测指纹
                
                current_ts = time.time()
                elapsed = current_ts - last_activity_time
                remaining = max(0, SCREEN_TIMEOUT - elapsed)

                # 0. 强制会话超时 (5分钟) - 防止按钮卡住导致系统永不休眠
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
                
                # 2. 按钮续命检测 (非阻塞上升沿检测)
                # 只有当按钮"从松开变按下"的一瞬间才触发，防止长按刷屏
                if btn_val == 1 and last_btn_state == 0:
                    now = time.time()
                    last_activity_time = now # 重置倒计时
                    remaining = SCREEN_TIMEOUT
                    update_screen("EXTEND", "Time Extended!", (0, 100, 100), countdown=remaining)
                    # update_screen("READY", "Face/Finger Ready", (0, 0, 0), countdown=remaining)
                
                # 3. 检查人脸识别结果 (Consumer)
                # 这是一个"非阻塞"检查：看一眼队列里有没有东西，没有就马上走
                if not face_queue.empty():
                    face_uid = face_queue.get()
                    print(f"🤖 后台线程检测到人脸: {face_uid}")
                    perform_unlock(face_uid, method="Face")
                    # 开锁后重置倒计时，让用户有时间继续操作
                    now = time.time()
                    last_activity_time = now
                    last_clock_update = now
                    continue

                # 4. 指纹识别 (主线程直接执行)
                # get_image() 也是很快的，不会卡死主循环
                if finger:
                    try:
                        if finger.get_image() == adafruit_fingerprint.OK:
                            last_activity_time = current_ts
                            update_screen("SCANNING", "Processing...", (0, 0, 100))
                            
                            if finger.image_2_tz(1) == adafruit_fingerprint.OK:
                                if finger.finger_search() == adafruit_fingerprint.OK:
                                    perform_unlock(finger.finger_id, method="Fingerprint")
                                    now = time.time()
                                    last_activity_time = now
                                    last_clock_update = now
                                    
                                    # 等待手指移开，避免一次按压触发多次
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
                        pass 

                # 5. 刷新屏幕倒计时 (限制刷新率)
                # 只有当秒数变化时才重绘屏幕，避免闪烁
                if int(current_ts) != int(last_clock_update):
                    update_screen("READY", "Face/Finger Ready", (0, 0, 0), countdown=remaining)
                    last_clock_update = current_ts
                
            # --- 循环末尾：同步状态与释放 CPU ---
            last_btn_state = btn_val
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n用户退出")
    finally:
        # 清理工作：关背光、关GPIO、关摄像头
        if disp: disp.set_backlight(False)
        if h_gpio is not None:
            lgpio.gpiochip_close(h_gpio)
        if face_rec: face_rec.close()

if __name__ == "__main__":
    main()