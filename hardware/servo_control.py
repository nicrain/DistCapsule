import lgpio
import time
import sys

# 映射逻辑编号 (Servo 1-5) 到 BCM GPIO 编号 (Pi 5)
# 遵循 docs/WIRING_GUIDE.md
CHANNEL_TO_PIN = {
    1: 18, # Servo 1 (Pin 12)
    2: 6,  # Servo 2 (Pin 31)
    3: 12, # Servo 3 (Pin 32)
    4: 13, # Servo 4 (Pin 33)
    5: 19  # Servo 5 (Pin 35)
}

class ServoController:
    """
    使用 lgpio (软件 PWM) 控制 SG90 舵机。
    完全绕过硬件 PWM 限制，解决与风扇的冲突。
    """
    def __init__(self, channel):
        self.pin = CHANNEL_TO_PIN.get(channel, channel)
        # Pi 5 的 GPIO 通常在 chip 4
        try:
            self.h = lgpio.gpiochip_open(4)
        except:
            # Fallback for older Pis or different configs
            self.h = lgpio.gpiochip_open(0)
        
        try:
            lgpio.gpio_claim_output(self.h, self.pin)
        except Exception as e:
            # 如果已经被占用，打印警告但继续尝试运行
            print(f"⚠️ Warning: GPIO {self.pin} already claimed or busy: {e}")

        # SG90 参数
        self.FREQ = 50 # 50Hz
        # 0度 = 0.5ms / 20ms = 2.5%
        # 180度 = 2.5ms / 20ms = 12.5%
        self.DUTY_LOCK = 2.5
        self.DUTY_UNLOCK = 12.5

    def _set_pwm(self, duty_percent):
        """设置 PWM 占空比 (0-100)"""
        lgpio.tx_pwm(self.h, self.pin, self.FREQ, duty_percent)

    def lock(self):
        """转动到锁定位置 (0度)"""
        self._set_pwm(self.DUTY_LOCK)
        time.sleep(0.5) # 等待转动
        # 关闭 PWM 以消除抖动并省电
        lgpio.tx_pwm(self.h, self.pin, 0, 0)

    def unlock(self):
        """转动到解锁位置 (180度)"""
        self._set_pwm(self.DUTY_UNLOCK)
        time.sleep(0.5)
        lgpio.tx_pwm(self.h, self.pin, 0, 0)

    def cleanup(self):
        lgpio.gpiochip_close(self.h)


