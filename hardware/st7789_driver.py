import time
import spidev  # Python 的 SPI 接口库，用于和屏幕高速通信
import RPi.GPIO as GPIO # 树莓派 GPIO 控制库
import numpy as np # 强大的数学库，这里用来做大规模的像素矩阵计算
from PIL import Image

class ST7789_Driver:
    """
    ST7789 屏幕底层驱动类
    这个类演示了如何不依赖高级库，直接通过发送十六进制指令(Hex Codes)来控制硬件。
    """
    def __init__(self, dc=24, rst=25, blk=27, spi_port=0, spi_device=0, speed_hz=24000000):
        # 1. 硬件引脚定义 (BCM 编号)
        self.dc_pin = dc   # Data/Command: 高电平发数据，低电平发命令
        self.rst_pin = rst # Reset: 复位引脚
        self.blk_pin = blk # Backlight: 背光控制
        self.width = 240
        self.height = 240
        
        # 2. GPIO 初始化
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.blk_pin, GPIO.OUT)
        
        # 3. SPI 总线初始化
        # SPI 是一种同步串行通信协议，像一条高速公路
        self.spi = spidev.SpiDev()
        self.spi.open(spi_port, spi_device) # 打开 /dev/spidev0.0
        self.spi.max_speed_hz = speed_hz    # 设定速度 24MHz
        self.spi.mode = 0b11 # Mode 3 (CPOL=1, CPHA=1): 这是 ST7789 要求的通信模式
        
        self.init_display()
        
    def send_cmd(self, cmd):
        """发送命令 (DC引脚置低)"""
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])

    def send_data(self, data):
        """发送数据 (DC引脚置高)"""
        GPIO.output(self.dc_pin, GPIO.HIGH)
        if isinstance(data, list) or isinstance(data, tuple):
            self.spi.writebytes(list(data))
        else:
            self.spi.writebytes([data])

    def init_display(self):
        """屏幕上电初始化流程 (Datasheet 规定的标准动作)"""
        # 1. 硬件复位 (Reset)
        # 拉高 -> 拉低(保持一会) -> 拉高，相当于按了一下重启键
        GPIO.output(self.blk_pin, GPIO.HIGH)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.15)
        
        # 2. 发送魔法指令 (Magic Codes)
        # 这些十六进制数字可以在 ST7789 芯片的数据手册(Datasheet)里查到
        self.send_cmd(0x11) # Sleep Out: 唤醒屏幕
        time.sleep(0.12)
        self.send_cmd(0x36) # MADCTL (Memory Data Access Control): 设置屏幕旋转方向
        self.send_data(0x00) 
        self.send_cmd(0x3A) # COLMOD (Interface Pixel Format): 设置颜色格式
        self.send_data(0x05) # 0x05 代表 16-bit/pixel (RGB565格式)
        self.send_cmd(0x21) # Inversion On: 反色显示 (解决某些屏幕颜色不对的问题)
        self.send_cmd(0x29) # Display On: 开启显示
        time.sleep(0.05)

    def set_window(self, x0, y0, x1, y1):
        """设定接下来要写入像素的矩形区域"""
        # x0 >> 8 是位运算"右移"，取出高8位。 x0 & 0xFF 是"按位与"，取出低8位。
        # 因为 SPI 每次只能发 8位(1字节)，而坐标可能是 240 (需要多于8位)，所以要拆开发。
        self.send_cmd(0x2A) # Column Addr (列地址)
        self.send_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self.send_cmd(0x2B) # Row Addr (行地址)
        self.send_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self.send_cmd(0x2C) # Memory Write (准备开始写像素数据)

    def display(self, image):
        """
        核心函数：将 PIL 图片显示到屏幕上
        关键点：颜色空间转换 (RGB888 -> RGB565)
        """
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))
        
        # 1. 格式转换
        # 电脑图片通常是 RGB888 (红绿蓝各8位，共24位)
        # 嵌入式屏幕为了省带宽，通常用 RGB565 (红5位，绿6位，蓝5位，共16位)
        image_rgb = image.convert("RGB")
        pixels = np.array(image_rgb, dtype=np.uint16)
        
        # 2. 位运算魔法 (Bitwise Magic)
        # R >> 3: 扔掉低3位，保留高5位
        # G >> 2: 扔掉低2位，保留高6位
        # B >> 3: 扔掉低3位，保留高5位
        # << 11/5: 左移，把它们挪到正确的位置拼起来
        r = (pixels[:, :, 0] >> 3) << 11
        g = (pixels[:, :, 1] >> 2) << 5
        b = (pixels[:, :, 2] >> 3)
        rgb565 = r | g | b # 按位或，拼接成最终的 16位 整数
        
        # 3. 大小端转换 (Endianness)
        # SPI 发送是按字节发的，需要把 16位 拆成两个 8位
        high_byte = (rgb565 >> 8).astype(np.uint8)
        low_byte = (rgb565 & 0xFF).astype(np.uint8)
        
        # 4. 展平成一维数组
        data = np.dstack((high_byte, low_byte)).flatten().tolist()
        
        # 5. 发送数据
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # 分块发送 (Chunking) 以避免缓冲区溢出 (SPI Buffer Overflow)
        chunk_size = 4096
        GPIO.output(self.dc_pin, GPIO.HIGH)
        for i in range(0, len(data), chunk_size):
            self.spi.writebytes(data[i:i+chunk_size])

    def clear(self, color=(0,0,0)):
        img = Image.new("RGB", (self.width, self.height), color)
        self.display(img)

    def set_backlight(self, val):
        """控制背光: True=亮, False=灭"""
        GPIO.output(self.blk_pin, GPIO.HIGH if val else GPIO.LOW)
