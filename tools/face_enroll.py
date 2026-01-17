import cv2
import face_recognition
import sqlite3
import json
import numpy as np
import time
import warnings
import os

# 屏蔽 pkg_resources 过时警告
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API")
# 或者更通用的屏蔽方式
warnings.filterwarnings("ignore", category=UserWarning, module="face_recognition_models")

# 动态获取数据库绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATABASE_NAME = os.path.join(PROJECT_ROOT, "capsule_dispenser.db")

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, face_encoding FROM Users")
    rows = cursor.fetchall()
    conn.close()
    
    print("\n--- 用户列表 / Liste des utilisateurs ---")
    for row in rows:
        uid, name, enc = row
        has_face = "OK" if enc else "Non"
        print(f"ID: {uid:<3} | {name:<15} | Face: {has_face}")
    print("-" * 40)

def save_face_to_db(user_id, encoding):
    """将特征向量(list)转为JSON字符串存入DB"""
    encoding_json = json.dumps(encoding.tolist())
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET face_encoding = ? WHERE user_id = ?", (encoding_json, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"数据库错误 / Erreur BDD: {e}")
        return False

def enroll_face():
    list_users()
    try:
        user_id = int(input("请输入要录入人脸的用户 ID / Entrez ID utilisateur: "))
    except ValueError:
        print("无效 ID / ID Invalide")
        return

    # 初始化摄像头
    print("正在搜索可用摄像头 / Recherche caméra...")
    cap = None

    pipelines = [
        (
            "libcamerasrc ! video/x-raw,format=NV12,width=640,height=480,framerate=30/1 ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1",
            "GStreamer (NV12 640x480)"
        ),
        (
            "libcamerasrc ! video/x-raw,width=640,height=480 ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1",
            "GStreamer (Auto 640x480)"
        ),
        (
            "libcamerasrc ! video/x-raw ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1",
            "GStreamer (Default)"
        )
    ]

    for pipeline, name in pipelines:
        try:
            print(f"尝试管道 / Essai pipeline: {name}...")
            cap_gst = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            if cap_gst.isOpened():
                ret, _ = cap_gst.read()
                if ret:
                    cap = cap_gst
                    print(f"成功打开摄像头 [{name}] / Caméra OK")
                    break
                else:
                    print(f"  管道打开但无法读取帧 / Erreur lecture")
                    cap_gst.release()
            else:
                print(f"  管道无法打开 / Erreur ouverture")
        except Exception as e:
            print(f"  异常 / Exception: {e}")

    if cap is None:
        print("尝试 V4L2 模式... / Essai V4L2...")
        for i in range(20):
            temp_cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
            if temp_cap.isOpened():
                ret, _ = temp_cap.read()
                if ret:
                    cap = temp_cap
                    print(f"成功打开 V4L2 设备 (Index: {i}) / V4L2 OK")
                    break
                else:
                    temp_cap.release()
    
    if cap is None:
        print("无法打开任何摄像头 / Erreur caméra")
        return

    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    import os
    has_display = os.environ.get('DISPLAY') is not None
    
    if has_display:
        print("\n--- GUI 模式指南 / Mode GUI ---")
        print("1. 按 's' 键保存，'q' 键退出。")
    else:
        print("\n未检测到显示器 (SSH模式) / Mode SSH Auto")
        print("请正对摄像头，保持静止... / Regardez la caméra...")

    start_time = time.time()
    last_log_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取图像帧 / Erreur frame")
            time.sleep(0.1)
            continue

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5) 
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)

        if not has_display:
            if time.time() - last_log_time > 1.0:
                print(".", end="", flush=True)
                last_log_time = time.time()

            if len(face_locations) == 1:
                print(f"\n检测到人脸! 正在提取特征... / Visage détecté!")
                encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                if encodings:
                    if save_face_to_db(user_id, encodings[0]):
                        print(f"ID {user_id} 人脸录入成功！ / Succès!")
                        break
            elif len(face_locations) > 1:
                if time.time() - last_log_time > 1.0:
                    print("\n[提示] 检测到多张人脸... / Trop de visages", end="")
            
            if time.time() - start_time > 60:
                print("\n录入超时 (60s) / Timeout")
                break
            
            time.sleep(0.1)
            continue

        for (top, right, bottom, left) in face_locations:
            top *= 2; right *= 2; bottom *= 2; left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow('Face Enroll - Press s to Save', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("退出录入 / Quitter")
            break
        elif key == ord('s'):
            if len(face_locations) == 1:
                print("正在提取特征... / Extraction...")
                encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                if encodings:
                    if save_face_to_db(user_id, encodings[0]):
                        print(f"ID {user_id} 人脸录入成功！ / Succès!")
                        break
                    else:
                        print("保存失败 / Erreur")
            elif len(face_locations) == 0:
                print("未检测到人脸 / Pas de visage")
            else:
                print("多张人脸 / Trop de visages")

    cap.release()
    if has_display:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    enroll_face()