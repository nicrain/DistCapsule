import lgpio
import time
import sys

# 映射 PWM 通道 ID 到 BCM GPIO 编号 (Pi 5)
# Channel 0 -> GPIO 12
# Channel 1 -> GPIO 13
# Channel 2 -> GPIO 18
# Channel 3 -> GPIO 19
CHANNEL_TO_PIN = {
    0: 12,
    1: 13,
    2: 18,
    3: 19,
    5: 6
}

class ServoController:
    """
    使用 lgpio (软件 PWM) 控制 SG90 舵机。
    完全绕过硬件 PWM 限制，解决与风扇的冲突。
    """
    def __init__(self, channel=2):
        self.pin = CHANNEL_TO_PIN.get(channel, channel)
        # Pi 5 的 GPIO 通常在 chip 4
        try:
            self.h = lgpio.gpiochip_open(4)
        except:
            # Fallback for older Pis or different configs
            self.h = lgpio.gpiochip_open(0)
        
        try:
            lgpio.gpio_claim_output(self.h, self.pin)
        except:
            # 如果已经被占用，尝试先释放再占用 (虽然 lgpio 通常允许多个 handle)
            pass

        # SG90 参数
        self.FREQ = 50 # 50Hz
        # 0度 = 0.5ms / 20ms = 2.5%
        # 180度 = 2.5ms / 20ms = 12.5%
        self.DUTY_LOCK = 2.5
        self.DUTY_UNLOCK = 12.5
        self.current_duty = None # Track current position

    def _set_pwm(self, duty_percent):
        """设置 PWM 占空比 (0-100)"""
        lgpio.tx_pwm(self.h, self.pin, self.FREQ, duty_percent)

    def _smooth_move(self, start_duty, end_duty, steps=50, duration=2.0):
        """线性插值平滑移动，减少瞬时电流"""
        delay = duration / steps
        diff = end_duty - start_duty
        for i in range(steps):
            duty = start_duty + (diff * (i / steps))
            self._set_pwm(duty)
            time.sleep(delay)
        self._set_pwm(end_duty)
        time.sleep(0.1) # Final hold

    def lock(self):
        """转动到锁定位置 (0度)"""
        if self.current_duty is not None:
            self._smooth_move(self.current_duty, self.DUTY_LOCK)
        else:
            self._set_pwm(self.DUTY_LOCK)
            time.sleep(0.5) # Wait for movement
        
        self.current_duty = self.DUTY_LOCK
        # 关闭 PWM 以消除抖动并省电
        lgpio.tx_pwm(self.h, self.pin, 0, 0)

    def unlock(self):
        """转动到解锁位置 (180度)"""
        if self.current_duty is not None:
            self._smooth_move(self.current_duty, self.DUTY_UNLOCK)
        else:
            self._set_pwm(self.DUTY_UNLOCK)
            time.sleep(0.5)
            
        self.current_duty = self.DUTY_UNLOCK
        lgpio.tx_pwm(self.h, self.pin, 0, 0)

    def cleanup(self):
        lgpio.gpiochip_close(self.h)


