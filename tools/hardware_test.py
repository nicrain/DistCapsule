import time
import sys
import os
import serial
import adafruit_fingerprint
from PIL import Image, ImageDraw, ImageFont

# 将项目根目录添加到 python 路径，以便导入 hardware 包
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 导入项目驱动
from hardware.servo_control import ServoController
from hardware.st7789_driver import ST7789_Driver

# 配置
SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 57600

def test_servos():
    print("\n--- 舵机测试 ---")
    # 映射逻辑ID到物理通道参数 (参考 main_demo.py)
    # 1->2 (GPIO 18)
    # 2->0 (GPIO 12)
    # 3->1 (GPIO 13)
    # 4->3 (GPIO 19)
    # 5->5 (GPIO 6)
    servo_map = {
        1: 2,
        2: 0,
        3: 1,
        4: 3,
        5: 5
    }
    
    servos = {}
    try:
        print("初始化所有舵机...")
        for logic_id, channel_id in servo_map.items():
            servos[logic_id] = ServoController(channel=channel_id)
        
        while True:
            print("\n[舵机菜单]")
            print("1. 测试全部 (依次 开 -> 关)")
            print("2. 测试单个")
            print("0. 返回主菜单")
            choice = input("请选择: ")
            
            if choice == '1':
                print("全部解锁...")
                for s in servos.values():
                    s.unlock()
                time.sleep(1)
                print("全部锁定...")
                for s in servos.values():
                    s.lock()
                    
            elif choice == '2':
                sid = input("输入舵机编号 (1-5): ")
                try:
                    sid = int(sid)
                    if sid in servos:
                        print(f"舵机 {sid} 解锁...")
                        servos[sid].unlock()
                        time.sleep(1)
                        print(f"舵机 {sid} 锁定...")
                        servos[sid].lock()
                    else:
                        print("无效编号")
                except ValueError:
                    print("请输入数字")
                    
            elif choice == '0':
                break
    except Exception as e:
        print(f"舵机错误: {e}")
    finally:
        for s in servos.values():
            s.cleanup()

def test_screen():
    print("\n--- 屏幕测试 ---")
    try:
        disp = ST7789_Driver()
        print("屏幕初始化成功")
        
        # 颜色测试
        colors = [
            ("红色", (255, 0, 0)),
            ("绿色", (0, 255, 0)),
            ("蓝色", (0, 0, 255)),
            ("白色", (255, 255, 255)),
            ("黑色", (0, 0, 0))
        ]
        
        for name, color in colors:
            print(f"显示 {name}...")
            img = Image.new("RGB", (disp.width, disp.height), color)
            disp.display(img)
            time.sleep(0.5)
            
        # 文本测试
        print("显示文本测试...")
        img = Image.new("RGB", (disp.width, disp.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        # 尝试加载字体，失败则用默认
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        draw.text((10, 50), "Screen Test", font=font, fill="WHITE")
        draw.text((10, 90), "OK!", font=font, fill="GREEN")
        draw.rectangle((5, 5, disp.width-5, disp.height-5), outline="BLUE", width=3)
        
        disp.display(img)
        print("测试完成")
        time.sleep(1)
        
        # 清屏
        print("清屏...")
        img_clear = Image.new("RGB", (disp.width, disp.height), (0, 0, 0))
        disp.display(img_clear)
        
    except Exception as e:
        print(f"屏幕错误: {e}")

def test_fingerprint():
    print("\n--- 指纹模块测试 ---")
    try:
        uart = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        
        if finger.read_sysparam() != adafruit_fingerprint.OK:
            raise RuntimeError("无法读取模块参数")
            
        print("模块连接成功!")
        print(f"库容量: {finger.library_size}")
        print(f"安全等级: {finger.security_level}")
        # 处理地址可能是 bytes 或 int 的情况
        address = finger.device_address
        if isinstance(address, int):
            print(f"地址: {hex(address)}")
        else:
            print(f"地址: {address.hex() if hasattr(address, 'hex') else address}")
        
        print("\n请按手指进行图像测试 (按 Ctrl+C 返回)...")
        while True:
            if finger.get_image() == adafruit_fingerprint.OK:
                print(" -> 获取到图像!", end="")
                if finger.image_2_tz(1) == adafruit_fingerprint.OK:
                    print(" 特征转换成功", end="")
                else:
                    print(" 特征转换失败", end="")
                print("") # 换行
                
                print("等待手指移开...")
                while finger.get_image() != adafruit_fingerprint.NOFINGER:
                    pass
                print("就绪")
            
    except KeyboardInterrupt:
        print("\n取消测试")
    except Exception as e:
        print(f"指纹错误: {e}")

def main():
    while True:
        print("=== 硬件综合测试工具 ===")
        print("1. 测试舵机 (Servos)")
        print("2. 测试屏幕 (Screen)")
        print("3. 测试指纹模块 (Fingerprint)")
        print("0. 退出")
        
        choice = input("请选择: ")
        
        if choice == '1':
            test_servos()
        elif choice == '2':
            test_screen()
        elif choice == '3':
            test_fingerprint()
        elif choice == '0':
            print("退出")
            break
        else:
            print("无效选项")

if __name__ == "__main__":
    main()
