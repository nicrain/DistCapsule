import os
import time
import sys

class ServoController:
    """
    用于控制 MG996R 舵机的硬件 PWM 控制器 (Raspberry Pi 5)。
    基于 /sys/class/pwm/pwmchip0/pwm2 接口。
    """
    def __init__(self):
        self.pwm_chip = "/sys/class/pwm/pwmchip0"
        self.pwm_channel = 2
        self.pwm_path = os.path.join(self.pwm_chip, f"pwm{self.pwm_channel}")
        self.period_ns = 20000000 # 50Hz (20ms)
        
        # --- 最终校准参数 ---
        # 0度 (锁定): 380 us
        # 180度 (解锁): 2375 us (取 2360-2390 的中间值)
        self.LOCK_PULSE_NS = 380000
        self.UNLOCK_PULSE_NS = 2375000 

        self._setup_pwm()

    def _write_file(self, filename, value):
        full_path = os.path.join(self.pwm_path, filename)
        # 对于 export/unexport，路径在 chip 目录下
        if filename in ['export', 'unexport']:
            full_path = os.path.join(self.pwm_chip, filename)
            
        try:
            with open(full_path, 'w') as f:
                f.write(str(value))
        except OSError as e:
            # 忽略 "Device or resource busy" (通常意味着已导出)
            if e.errno != 16: 
                print(f"[Servo Error] 写入 {filename} 失败: {e}")

    def _setup_pwm(self):
        """初始化 PWM 通道 (增强版: 强制重置)"""
        # 如果已经存在，先尝试 unexport 以便重置状态
        if os.path.exists(self.pwm_path):
            try:
                self._write_file("unexport", self.pwm_channel)
                time.sleep(0.1)
            except:
                pass

        # 重新 export
        if not os.path.exists(self.pwm_path):
            self._write_file("export", self.pwm_channel)
            time.sleep(0.2) # 给足时间让文件系统生成节点
        
        # 再次检查路径是否存在
        if not os.path.exists(self.pwm_path):
            raise RuntimeError(f"无法导出 PWM 通道 {self.pwm_channel}")

        # 先禁用以进行配置
        self._write_file("enable", 0)
        self._write_file("period", self.period_ns)
        
        # 默认先不开启 enable，等到 lock/unlock 时再开启

    def _enable(self, enabled: bool):
        self._write_file("enable", "1" if enabled else "0")

    def _set_duty_cycle(self, duty_ns):
        self._write_file("duty_cycle", duty_ns)

    def lock(self):
        """转动到锁定位置 (0度) 并切断信号防抖"""
        # print("[Servo] 执行锁定...")
        self._set_duty_cycle(self.LOCK_PULSE_NS)
        self._enable(True)
        time.sleep(0.8) # 给足时间转动
        self._enable(False) # 切断信号，消除抖动

    def unlock(self):
        """转动到解锁位置 (180度) 并切断信号防抖"""
        # print("[Servo] 执行解锁...")
        self._set_duty_cycle(self.UNLOCK_PULSE_NS)
        self._enable(True)
        time.sleep(0.8)
        self._enable(False)

    def cleanup(self):
        """清理资源"""
        self._enable(False)
        self._write_file("unexport", self.pwm_channel)

# 简单的自测代码
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("错误: 需要 sudo 权限运行硬件 PWM。")
        sys.exit(1)
        
    servo = ServoController()
    try:
        print("--- 最终舵机控制模块测试 ---")
        print("1. 解锁 (Open)")
        servo.unlock()
        time.sleep(1)
        
        print("2. 锁定 (Close)")
        servo.lock()
        time.sleep(1)
        
        print("测试完成。")
    finally:
        # 注意：通常我们在程序结束时不 unexport，以便下次快速启动
        # 这里为了演示完整性调用 cleanup，实际使用中可保留
        # servo.cleanup()
        pass
