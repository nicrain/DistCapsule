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

        # 2. 如果 GStreamer 失败，遍历搜索 V4L2 设备 (0-20)
        print("⚠️ [Face] GStreamer 失败，正在搜索 V4L2 设备...")
        for i in range(20):
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        print(f"✅ [Face] 成功连接 V4L2 设备 (Index: {i})")
                        self.cap = cap
                        
                        # 保存一张调试图，确保画面正常
                        cv2.imwrite("debug_camera_view.jpg", frame)
                        print(f"   [Debug] 已保存测试图到 debug_camera_view.jpg")
                        return
                    else:
                        cap.release()
            except:
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
            print("⚠️ [Face] 无法读取视频帧 (Stream broken)")
            # 尝试重连逻辑可以在这里添加
            return None

        # 优化策略: 强制图像增强
        # 1. 转为 LAB 颜色空间 (L=亮度, A/B=颜色)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # 2. 对 L (亮度) 通道应用 CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        # 3. 合并通道并转回 RGB
        limg = cv2.merge((cl, a, b))
        enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)

        # 3. 检测人脸 (使用增强后的图像)
        face_locations = face_recognition.face_locations(enhanced_frame)
        
        if not face_locations:
            self.no_face_count += 1
            # 连续未检测到人脸时，仅在控制台提示（不再保存图片）
            if self.no_face_count % 20 == 0: # 降低频率到约 10秒一次
                # print(f"⚠️ [Face] 连续 {self.no_face_count} 次未检测到人脸 (请检查光线或距离)")
                pass
            return None 
        
        # 如果检测到了，重置计数器
        if self.no_face_count > 0:
            # print("✨ [Face] 重新捕捉到人脸")
            self.no_face_count = 0

        # 4. 提取特征
        # 注意：虽然用增强图检测到了位置，但为了特征准确性，建议：
        # 方案A: 用增强图提取特征 (暗光下可能更好)
        # 方案B: 用原图提取特征 (颜色更自然)
        # 这里我们选择方案 A，因为原图可能太暗根本提不出特征
        face_encodings = face_recognition.face_encodings(enhanced_frame, face_locations)
        
        print(f"👀 [Face] 捕获到 {len(face_encodings)} 张人脸")

        # 4. 比对
        for face_encoding in face_encodings:
            # 计算与数据库中所有人脸的欧氏距离
            # 距离越小越相似。通常 0.6 是分界线。
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            # 找到最相似的那个
            best_match_index = np.argmin(face_distances)
            min_distance = face_distances[best_match_index]

            # 阈值调整说明:
            # 0.60: 标准严格阈值 (误识率极低，但拒识率高)
            # 0.72: 宽松阈值 (适合树莓派摄像头及非受控光线，体验更好)
            if min_distance < 0.72: 
                user_id = self.known_face_ids[best_match_index]
                print(f"👤 [Face] 识别成功! ID: {user_id} (距离: {min_distance:.2f})")
                return user_id
            else:
                print(f"🤔 [Face] 陌生人 (最近距离: {min_distance:.2f})")
        
        return None

    def close(self):
        if self.cap:
            self.cap.release()
