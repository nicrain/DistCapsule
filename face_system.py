import cv2
import face_recognition
import sqlite3
import json
import numpy as np
import time
import warnings

# 屏蔽无关紧要的警告
warnings.filterwarnings("ignore", category=UserWarning, module="face_recognition_models")

DATABASE_NAME = "capsule_dispenser.db"

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.cap = None
        self.last_scan_time = 0
        self.scan_interval = 0.5  # 限制识别频率，每 0.5 秒一次，防止 CPU 满载
        
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
        
        # 定义多种 GStreamer 管道尝试策略 (同 face_enroll.py)
        pipelines = [
            (
                "libcamerasrc ! video/x-raw,format=NV12,width=640,height=480,framerate=30/1 ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1",
                "GStreamer (NV12 640x480)"
            ),
            (
                "libcamerasrc ! video/x-raw,width=640,height=480 ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1",
                "GStreamer (Auto 640x480)"
            ),
            # 兼容非 Pi 5 环境
            (0, "V4L2 Index 0") 
        ]

        for source, name in pipelines:
            try:
                if isinstance(source, int):
                    self.cap = cv2.VideoCapture(source)
                else:
                    self.cap = cv2.VideoCapture(source, cv2.CAP_GSTREAMER)
                
                if self.cap.isOpened():
                    # 尝试读一帧
                    ret, _ = self.cap.read()
                    if ret:
                        print(f"✅ [Face] 摄像头就绪: {name}")
                        return
                    else:
                        self.cap.release()
            except Exception:
                pass
        
        print("❌ [Face] 无法初始化任何摄像头，人脸识别将不可用")
        self.cap = None

    def scan(self):
        """
        尝试读取一帧并识别。
        返回: matched_user_id (int) 或 None
        """
        # 如果没摄像头或没人脸库，直接跳过
        if not self.cap or not self.known_face_encodings:
            return None

        # 频率控制
        if time.time() - self.last_scan_time < self.scan_interval:
            return None
        self.last_scan_time = time.time()

        ret, frame = self.cap.read()
        if not ret:
            print("⚠️ [Face] 无法读取视频帧")
            return None

        # 1. 图像预处理
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 2. 检测人脸
        face_locations = face_recognition.face_locations(rgb_small_frame)
        if not face_locations:
            # 没人脸时保持静默，以免刷屏
            return None 

        # 3. 提取特征
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        # print(f"👀 [Face] 检测到 {len(face_encodings)} 张人脸，正在分析...")

        # 4. 比对
        for face_encoding in face_encodings:
            # 计算与数据库中所有人脸的欧氏距离
            # 距离越小越相似。通常 0.6 是分界线。
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            # 找到最相似的那个
            best_match_index = np.argmin(face_distances)
            min_distance = face_distances[best_match_index]

            if min_distance < 0.6: # 放宽阈值到 0.6
                user_id = self.known_face_ids[best_match_index]
                print(f"👤 [Face] 识别成功! ID: {user_id} (距离: {min_distance:.2f})")
                return user_id
            else:
                pass
                # print(f"🤔 [Face] 未知用户 (最近距离: {min_distance:.2f})")
        
        return None

    def close(self):
        if self.cap:
            self.cap.release()
