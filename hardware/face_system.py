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
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

# 使用绝对路径定位数据库
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
        print("[Face] 正在加载人脸数据库 / Chargement de la BDD visages...")
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, name, face_encoding FROM Users WHERE face_encoding IS NOT NULL")
            rows = cursor.fetchall()
            
            self.known_face_encodings = []
            self.known_face_ids = []
            count = 0
            
            for uid, name, encoding_json in rows:
                if encoding_json:
                    try:
                        encoding_list = json.loads(encoding_json)
                        encoding_np = np.array(encoding_list)
                        self.known_face_encodings.append(encoding_np)
                        self.known_face_ids.append(uid)
                        count += 1
                    except Exception as e:
                        print(f"  用户 {name} (ID {uid}) 数据损坏 / Données corrompues: {e}")
            
            conn.close()
            print(f"[Face] 已加载 {count} 个用户的人脸数据 / {count} visages chargés")
        except Exception as e:
            print(f"[Face] 数据库加载失败 / Erreur de chargement BDD: {e}")

    def init_camera(self):
        """使用 Pi 5 兼容策略初始化摄像头"""
        print("[Face] 初始化摄像头 / Initialisation caméra...")
        
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
                cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        print(f"[Face] 摄像头就绪: {name} / Caméra prête")
                        self.cap = cap
                        return
                    else:
                        cap.release()
            except Exception:
                pass

        print("[Face] 无法初始化 GStreamer 摄像头 / Erreur init caméra")
        print("   提示: 请检查摄像头排线是否插好，以及是否安装了 gstreamer1.0-libcamera")
        self.cap = None

    def scan(self):
        """
        核心函数：尝试读取一帧并识别。
        """
        if not self.cap or not self.known_face_encodings:
            return None

        if time.time() - self.last_scan_time < self.scan_interval:
            return None
        self.last_scan_time = time.time()

        ret, frame = self.cap.read()
        if not ret:
            print("[Face] 无法读取视频帧 / Erreur lecture flux")
            return None

        # 旋转图像 (适应物理安装)
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # 图像增强 (CLAHE)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)

        # 人脸检测
        face_locations = face_recognition.face_locations(enhanced_frame)
        
        if not face_locations:
            return None 

        # 特征提取
        face_encodings = face_recognition.face_encodings(enhanced_frame, face_locations)
        
        print(f"[Face] 捕获到 {len(face_encodings)} 张人脸 / Visage détecté")

        # 人脸比对
        for face_encoding in face_encodings:
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            min_distance = face_distances[best_match_index]

            # 阈值判定 (0.68)
            if min_distance < 0.68: 
                user_id = self.known_face_ids[best_match_index]
                print(f"[Face] 识别成功 / Succès! ID: {user_id} (特征差异/Diff: {min_distance:.2f})")
                return user_id
            else:
                print(f"[Face] 陌生人 / Inconnu (最小差异/Min Diff: {min_distance:.2f})")
        
        return None

    def close(self):
        if self.cap:
            self.cap.release()