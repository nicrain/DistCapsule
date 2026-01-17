import cv2
import face_recognition
import sqlite3
import json
import numpy as np
import time
import warnings
import os

# 屏蔽无关紧要的警告
warnings.filterwarnings("ignore", category=UserWarning, module="face_recognition_models")

# 使用绝对路径定位数据库 (当前文件所在目录的上一级 -> 根目录)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATABASE_NAME = os.path.join(PROJECT_ROOT, "capsule_dispenser.db")

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.cap = None
        self.last_scan_time = 0
        self.scan_interval = 0.5  # 限制识别频率
        self.no_face_count = 0    # 调试计数器
        
        # 1. 加载已知人脸
        self.load_faces_from_db()
        
        # 2. 初始化摄像头
        self.init_camera()

    def load_faces_from_db(self):
        """从数据库加载所有已录入的人脸特征"""
        print("👤 [Face] 正在加载人脸数据库...")
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            # 只加载有人脸数据的用户
            cursor.execute("SELECT user_id, name, face_encoding FROM Users WHERE face_encoding IS NOT NULL")
            rows = cursor.fetchall()
            
            self.known_face_encodings = []
            self.known_face_ids = []
            count = 0
            
            for uid, name, encoding_json in rows:
                if encoding_json:
                    try:
                        # JSON -> List -> Numpy Array
                        encoding_list = json.loads(encoding_json)
                        encoding_np = np.array(encoding_list)
                        self.known_face_encodings.append(encoding_np)
                        self.known_face_ids.append(uid)
                        count += 1
                    except Exception as e:
                        print(f"  ⚠️ 用户 {name} (ID {uid}) 数据损坏: {e}")
            
            conn.close()
            print(f"👤 [Face] 已加载 {count} 个用户的人脸数据")
        except Exception as e:
            print(f"❌ [Face] 数据库加载失败: {e}")

    def init_camera(self):
        """使用 Pi 5 兼容策略初始化摄像头"""
        print("📷 [Face] 初始化摄像头...")
        
        # 1. 尝试 GStreamer 策略
        gst_pipelines = [
            (
                "libcamerasrc ! video/x-raw,format=NV12,width=640,height=480,framerate=30/1 ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1",
                "GStreamer (NV12)"
            ),
            (
                "libcamerasrc ! video/x-raw,width=640,height=480 ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1",
                "GStreamer (Auto)"
            )
        ]

        for pipeline, name in gst_pipelines:
            try:
                # print(f"  -> 尝试 {name}...")
                cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        print(f"✅ [Face] 摄像头就绪: {name}")
                        self.cap = cap
                        return
                    else:
                        cap.release()
            except Exception:
                pass

        print("❌ [Face] 无法初始化 GStreamer 摄像头，人脸识别将不可用")
        print("   提示: 请检查摄像头排线是否插好，以及是否安装了 gstreamer1.0-libcamera")
        self.cap = None

    def scan(self):
        """
        核心函数：尝试读取一帧并识别。
        返回: matched_user_id (int) 或 None
        """
        # 如果没摄像头或没人脸库，直接跳过，不做无用功
        if not self.cap or not self.known_face_encodings:
            return None

        # 频率控制 (Throttling)
        # 防止跑得太快占满 CPU，每秒只扫描 2 次 (1/0.5s)
        if time.time() - self.last_scan_time < self.scan_interval:
            return None
        self.last_scan_time = time.time()

        ret, frame = self.cap.read()
        if not ret:
            print("⚠️ [Face] 无法读取视频帧 (Stream broken)")
            return None

        # --- 旋转图像 (Rotation) ---
        # 适配物理安装：摄像头逆时针旋转了 90 度 (Counter-Clockwise)
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # --- 图像增强 (Image Enhancement) ---
        # 树莓派摄像头在室内往往光线不足。
        # 这里使用了 CLAHE (对比度受限自适应直方图均衡化) 算法。
        # 简单来说：它把画面切成小块，把太暗的地方提亮，把太亮的地方压暗。
        
        # 1. BGR 转 LAB: 因为在 RGB 模式下调亮度会改变颜色，LAB 模式把亮度(L)和颜色(A,B)分开了。
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab) # 拆分通道

        # 2. 对 L (亮度) 通道应用增强
        # clipLimit=3.0: 限制对比度增强的倍数，防止噪声也被放大
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        # 3. 合并通道并转回 RGB (人脸库需要 RGB)
        limg = cv2.merge((cl, a, b))
        enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)

        # --- 人脸检测 (Detection) ---
        # 寻找画面中哪里有人脸 (返回坐标框：top, right, bottom, left)
        face_locations = face_recognition.face_locations(enhanced_frame)
        
        if not face_locations:
            self.no_face_count += 1
            if self.no_face_count % 20 == 0: 
                pass # 连续没检测到人脸时，静默处理
            return None 
        
        if self.no_face_count > 0:
            self.no_face_count = 0

        # --- 特征提取 (Encoding) ---
        # 把人脸图像转换成一个 128维 的向量 (一组数字)。
        # 只要是同一个人，无论角度如何，这个向量的数值都很接近。
        face_encodings = face_recognition.face_encodings(enhanced_frame, face_locations)
        
        print(f"👀 [Face] 捕获到 {len(face_encodings)} 张人脸")

        # --- 人脸比对 (Matching) ---
        for face_encoding in face_encodings:
            # 计算当前人脸向量与数据库中所有向量的欧氏距离 (Euclidean Distance)
            # 距离越小 = 越相似。
            # 距离 = 0: 完全一样
            # 距离 > 0.6: 通常认为是不同的人
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            # 找到距离最小的那个 (最像的那个)
            # np.argmin 返回最小值所在的索引位置
            best_match_index = np.argmin(face_distances)
            min_distance = face_distances[best_match_index]

            # 阈值判定
            # 0.60: 标准严格阈值 (Standard)
            # 0.68: 针对当前环境调整 (User Obs: 0.65)
            if min_distance < 0.68: 
                user_id = self.known_face_ids[best_match_index]
                print(f"👤 [Face] 识别成功! ID: {user_id} (距离: {min_distance:.2f})")
                return user_id
            else:
                print(f"🤔 [Face] 陌生人 (最近距离: {min_distance:.2f})")
        
        return None

    def close(self):
        if self.cap:
            self.cap.release()
