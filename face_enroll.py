import cv2
import face_recognition
import sqlite3
import json
import numpy as np
import time

DATABASE_NAME = "capsule_dispenser.db"

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, face_encoding FROM Users")
    rows = cursor.fetchall()
    conn.close()
    
    print("\n--- 用户列表 ---")
    for row in rows:
        uid, name, enc = row
        has_face = "✅ 已录入" if enc else "❌ 无人脸"
        print(f"ID: {uid:<3} | {name:<15} | {has_face}")
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
        print(f"数据库错误: {e}")
        return False

def enroll_face():
    list_users()
    try:
        user_id = int(input("请输入要录入人脸的用户 ID: "))
    except ValueError:
        print("无效 ID")
        return

    # 初始化摄像头
    print("正在搜索可用摄像头...")
    cap = None

    # 定义多种 GStreamer 管道尝试策略
    pipelines = [
        # 策略 1: 强制指定 NV12 格式和分辨率 (Pi 5 推荐)
        (
            "libcamerasrc ! "
            "video/x-raw,format=NV12,width=640,height=480,framerate=30/1 ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=1",
            "GStreamer (NV12 640x480)"
        ),
        # 策略 2: 仅指定分辨率，由驱动决定格式
        (
            "libcamerasrc ! "
            "video/x-raw,width=640,height=480 ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=1",
            "GStreamer (Auto 640x480)"
        ),
        # 策略 3: 不指定分辨率 (使用默认/最大)，后续由 OpenCV 缩放
        (
            "libcamerasrc ! "
            "video/x-raw ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=1",
            "GStreamer (Default Resolution)"
        )
    ]

    for pipeline, name in pipelines:
        try:
            print(f"尝试管道: {name}...")
            # print(f"  -> {pipeline}")
            cap_gst = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            if cap_gst.isOpened():
                ret, _ = cap_gst.read()
                if ret:
                    cap = cap_gst
                    print(f"✅ 成功打开摄像头 [{name}]")
                    break
                else:
                    print(f"  ❌ 管道打开但无法读取帧")
                    cap_gst.release()
            else:
                print(f"  ❌ 管道无法打开")
        except Exception as e:
            print(f"  ⚠️ 异常: {e}")

    # 方案 4: 如果 GStreamer 全部失败，尝试遍历 V4L2 设备
    if cap is None:
        print("尝试 V4L2 模式 (可能不稳定)...")
        for i in range(20): # 扩大搜索范围
            # print(f"尝试 index {i}...")
            temp_cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
            if temp_cap.isOpened():
                # 尝试读取一帧以确认真的可用
                ret, _ = temp_cap.read()
                if ret:
                    cap = temp_cap
                    print(f"✅ 成功打开 V4L2 设备 (Index: {i})")
                    break
                else:
                    temp_cap.release()
    
    if cap is None:
        print("❌ 无法打开任何摄像头。")
        print("请尝试运行 'libcamera-hello' 检查摄像头硬件是否正常。")
        return

    # 设置分辨率，太高会卡，320x240 足够识别
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # ... (前文代码不变)

    # 检查是否支持 GUI 显示
    import os
    has_display = os.environ.get('DISPLAY') is not None
    
    if has_display:
        print("\n--- GUI 模式指南 ---")
        print("1. 窗口中会出现人脸框。")
        print("2. 按 's' 键保存，'q' 键退出。")
    else:
        print("\n⚠️  未检测到显示器 (SSH模式)。切换到 [自动录入模式]。")
        print("➡️  请正对摄像头，保持静止...")
        print("➡️  系统将在检测到单张清晰人脸时自动保存。")

    start_time = time.time()
    last_log_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取图像帧")
            time.sleep(0.1)
            continue

        # 缩小图像以加快处理速度 (1/2)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5) 
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 检测人脸
        face_locations = face_recognition.face_locations(rgb_small_frame)

        # --- 分支 1: 无显示器 (自动模式) ---
        if not has_display:
            # 每秒打印一次状态点，避免刷屏
            if time.time() - last_log_time > 1.0:
                print(".", end="", flush=True)
                last_log_time = time.time()

            if len(face_locations) == 1:
                print(f"\n✅ 检测到人脸! 正在提取特征...")
                encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                if encodings:
                    if save_face_to_db(user_id, encodings[0]):
                        print(f"✅ ID {user_id} 人脸录入成功！")
                        break
            elif len(face_locations) > 1:
                if time.time() - last_log_time > 1.0:
                    print("\n[提示] 检测到多张人脸，请保留一人...", end="")
            
            # 超时保护 (60秒)
            if time.time() - start_time > 60:
                print("\n❌ 录入超时 (60s)，未检测到有效人脸。")
                break
            
            # 简单限速
            time.sleep(0.1)
            continue

        # --- 分支 2: GUI 模式 (原有逻辑) ---
        # 在原图上画框
        for (top, right, bottom, left) in face_locations:
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow('Face Enroll - Press s to Save', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("退出录入")
            break
        elif key == ord('s'):
            if len(face_locations) == 1:
                print("📸 正在提取特征...")
                encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                if encodings:
                    if save_face_to_db(user_id, encodings[0]):
                        print(f"✅ ID {user_id} 人脸录入成功！")
                        break
                    else:
                        print("保存失败")
            elif len(face_locations) == 0:
                print("⚠️  未检测到人脸")
            else:
                print("⚠️  多张人脸")

    cap.release()
    if has_display:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    enroll_face()
