import time
import spidev
import RPi.GPIO as GPIO
import numpy as np
from PIL import Image

class ST7789_Driver:
    def __init__(self, dc=24, rst=25, blk=27, spi_port=0, spi_device=0, speed_hz=24000000):
        self.dc_pin = dc
        self.rst_pin = rst
        self.blk_pin = blk
        self.width = 240
        self.height = 240
        
        # GPIO Init
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.blk_pin, GPIO.OUT)
        
        # SPI Init
        self.spi = spidev.SpiDev()
        self.spi.open(spi_port, spi_device)
        self.spi.max_speed_hz = speed_hz
        self.spi.mode = 0b11 # Mode 3
        
        self.init_display()
        
    def send_cmd(self, cmd):
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])

    def send_data(self, data):
        GPIO.output(self.dc_pin, GPIO.HIGH)
        if isinstance(data, list) or isinstance(data, tuple):
            self.spi.writebytes(list(data))
        else:
            self.spi.writebytes([data])

    def init_display(self):
        # Reset
        GPIO.output(self.blk_pin, GPIO.HIGH)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.15)
        
        self.send_cmd(0x11) # Sleep Out
        time.sleep(0.12)
        self.send_cmd(0x36) # MADCTL
        self.send_data(0x00) 
        self.send_cmd(0x3A) # COLMOD
        self.send_data(0x05) # 16-bit
        self.send_cmd(0x21) # Inversion On
        self.send_cmd(0x29) # Display On
        time.sleep(0.05)

    def set_window(self, x0, y0, x1, y1):
        self.send_cmd(0x2A) # Column Addr
        self.send_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self.send_cmd(0x2B) # Row Addr
        self.send_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self.send_cmd(0x2C) # Memory Write

    def display(self, image):
        """显示 PIL Image 对象"""
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))
        
        # 转换为 RGB565
        image_rgb = image.convert("RGB")
        pixels = np.array(image_rgb, dtype=np.uint16)
        r = (pixels[:, :, 0] >> 3) << 11
        g = (pixels[:, :, 1] >> 2) << 5
        b = (pixels[:, :, 2] >> 3)
        rgb565 = r | g | b
        
        # 转换为字节流 (Big Endian)
        high_byte = (rgb565 >> 8).astype(np.uint8)
        low_byte = (rgb565 & 0xFF).astype(np.uint8)
        
        # 组合并展平
        data = np.dstack((high_byte, low_byte)).flatten().tolist()
        
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # 分块发送以避免缓冲区溢出
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
