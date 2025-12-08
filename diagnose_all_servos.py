import os
import time
import sys

def check_root():
    if os.geteuid() != 0:
        print("❌ 错误: 必须使用 sudo 运行此脚本！")
        sys.exit(1)

def test_channel(channel, pin_name):
    print(f"\n--- 测试通道 PWM {channel} (对应 {pin_name}) ---")
    
    chip_path = "/sys/class/pwm/pwmchip0"
    pwm_path = os.path.join(chip_path, f"pwm{channel}")
    
    # 1. 检查/导出
    if not os.path.exists(pwm_path):
        print(f"   ℹ️ 通道未导出，尝试导出...")
        try:
            with open(os.path.join(chip_path, "export"), "w") as f:
                f.write(str(channel))
            time.sleep(0.2)
        except OSError as e:
            print(f"   ❌ 导出失败: {e}")
            print(f"      可能原因: config.txt 中未配置该引脚的 dtoverlay")
            return False

    if not os.path.exists(pwm_path):
        print(f"   ❌ 导出后路径仍不存在，跳过。")
        return False
        
    print(f"   ✅ 通道已就绪")

    # 2. 配置并运动
    try:
        # 设置周期 20ms
        with open(os.path.join(pwm_path, "period"), "w") as f:
            f.write("20000000")
            
        # 启用
        with open(os.path.join(pwm_path, "enable"), "w") as f:
            f.write("1")
            
        print("   👉 动作: 转到 0度 (0.5ms)")
        with open(os.path.join(pwm_path, "duty_cycle"), "w") as f:
            f.write("500000")
        time.sleep(1.0)
        
        print("   👉 动作: 转到 180度 (2.5ms)")
        with open(os.path.join(pwm_path, "duty_cycle"), "w") as f:
            f.write("2500000")
        time.sleep(1.0)
        
        print("   👉 动作: 回到 0度 (0.5ms)")
        with open(os.path.join(pwm_path, "duty_cycle"), "w") as f:
            f.write("500000")
        time.sleep(0.5)
        
        # 禁用
        with open(os.path.join(pwm_path, "enable"), "w") as f:
            f.write("0")
        print("   ✅ 测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 运行时错误: {e}")
        return False

if __name__ == "__main__":
    check_root()
    print("=== 多路舵机独立诊断工具 ===")
    print("注意: 请观察哪个舵机在动，以及是否有报错。\n")
    
    # 定义映射关系
    # Servo 1: GPIO 18 -> PWM 2
    # Servo 2: GPIO 12 -> PWM 0
    # Servo 3: GPIO 13 -> PWM 1
    # Servo 4: GPIO 19 -> PWM 3
    
    results = {}
    
    results["Servo 1 (GPIO 18)"] = test_channel(2, "GPIO 18")
    time.sleep(0.5)
    
    results["Servo 2 (GPIO 12)"] = test_channel(0, "GPIO 12")
    time.sleep(0.5)
    
    results["Servo 3 (GPIO 13)"] = test_channel(1, "GPIO 13")
    time.sleep(0.5)
    
    results["Servo 4 (GPIO 19)"] = test_channel(3, "GPIO 19")
    
    print("\n=== 总结 ===")
    for name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{name}: {status}")
