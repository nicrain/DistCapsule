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
    print("正在打开摄像头 (Libcamera/V4L2)...")
    # Pi 5 通常使用 index 0，配合 V4L2 后端
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    # 设置分辨率，太高会卡，320x240 足够识别
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("❌ 无法打开摄像头。请检查连接或是否被占用。\n")
        return

    print("\n--- 操作指南 ---")
    print("1. 确保光线充足，正对摄像头。")
    print("2. 窗口中会出现人脸框。")
    print("3. 按 's' 键保存当前帧人脸。")
    print("4. 按 'q' 键取消退出。")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取图像帧")
            break

        # 缩小图像以加快处理速度 (1/2)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5) 
        
        # BGR 转 RGB (face_recognition 需要 RGB)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 检测人脸位置
        face_locations = face_recognition.face_locations(rgb_small_frame)

        # 在原图上画框
        for (top, right, bottom, left) in face_locations:
            # 坐标还原回原图比例 (*2)
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # 显示预览
        cv2.imshow('Face Enroll - Press s to Save', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("退出录入")
            break
        elif key == ord('s'):
            if len(face_locations) == 0:
                print("⚠️  未检测到人脸，无法保存！")
            elif len(face_locations) > 1:
                print("⚠️  检测到多张人脸，请确保画面中只有一个人！")
            else:
                print("📸 正在提取特征...")
                # 提取特征编码 (128维向量)
                encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                if encodings:
                    if save_face_to_db(user_id, encodings[0]):
                        print(f"✅ ID {user_id} 人脸录入成功！")
                        break
                    else:
                        print("保存失败")
                else:
                    print("❌ 特征提取失败，请调整角度重试")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    enroll_face()
