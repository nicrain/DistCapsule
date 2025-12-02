import time
import serial
import adafruit_fingerprint

# --- 配置 ---
# Raspberry Pi 5 的默认串口通常映射到 /dev/serial0
# 如果失败，可能需要检查 /dev/ttyAMA0 或 /dev/ttyAMA10
# 用户测试确认: ttyAMA0 是工作正常的端口
uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)

def test_fingerprint():
    print("--- 指纹模块连接测试 ---")
    print(f"尝试连接串口: {uart.name} ...")

    try:
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        
        # 尝试读取指纹模块信息
        if finger.read_sysparam() != adafruit_fingerprint.OK:
            print("[错误] 无法读取系统参数 (通信失败)")
            return

        print("\n✅ 连接成功！")
        print(f"模块型号: {finger.library_size} 指纹容量")
        print(f"安全等级: {finger.security_level}")
        # print(f"设备地址: {finger.device_address:x}") # 这一行导致了格式化错误，先注释掉
        print(f"波特率: 57600")
        
        print("\n请把手指放在传感器上测试...")
        
        # 简单的循环检测手指
        start_time = time.time()
        while time.time() - start_time < 10:
            if finger.get_image() == adafruit_fingerprint.OK:
                print(" -> 检测到手指！(图像已获取)")
                break
            time.sleep(0.1)
        else:
            print(" -> 10秒内未检测到手指。")

    except Exception as e:
        print(f"\n[异常] 发生错误: {e}")
        print("请检查：")
        print("1. 接线是否正确 (TX接RX, RX接TX)")
        print("2. 串口是否被控制台占用 (sudo raspi-config -> Interface -> Serial Port)")

if __name__ == "__main__":
    test_fingerprint()
