import time
import serial
import adafruit_fingerprint

# 使用已验证的端口
uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

def enroll_finger(location):
    """录入指纹到指定位置 (location ID)"""
    
    # --- 第一步：获取第一次图像 ---
    print(f"准备录入指纹到 ID #{location}...")
    print("请放置手指...")
    
    while finger.get_image() != adafruit_fingerprint.OK:
        pass # 等待手指

    print(" -> 正在获取图像...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("❌ 图像处理失败")
        return False

    print(" -> 移开手指...")
    time.sleep(1)
    while finger.get_image() != adafruit_fingerprint.NOFINGER:
        pass # 等待移开

    # --- 第二步：获取第二次图像 (验证) ---
    print("请再次放置同一根手指...")
    
    while finger.get_image() != adafruit_fingerprint.OK:
        pass

    print(" -> 正在获取图像...")
    if finger.image_2_tz(2) != adafruit_fingerprint.OK:
        print("❌ 图像处理失败")
        return False

    # --- 第三步：创建模型并存储 ---
    print(" -> 正在创建指纹模型...")
    if finger.create_model() != adafruit_fingerprint.OK:
        print("❌ 指纹不匹配，录入失败")
        return False
    
    print(f" -> 正在存储到 ID #{location}...")
    if finger.store_model(location) != adafruit_fingerprint.OK:
        print("❌ 存储失败")
        return False

    print(f"✅ 成功！指纹已录入到 ID #{location}")
    return True

def main():
    if finger.read_sysparam() != adafruit_fingerprint.OK:
        print("无法连接指纹模块")
        return

    print("--------------------------------")
    print(f"当前已存储指纹数: {finger.count_templates()}")
    print("--------------------------------")
    
    try:
        id_str = input("请输入要保存的指纹 ID (1-127): ")
        location = int(id_str)
        if 1 <= location <= 127:
            enroll_finger(location)
        else:
            print("ID 必须在 1 到 127 之间")
    except ValueError:
        print("请输入有效的数字")

if __name__ == "__main__":
    main()
