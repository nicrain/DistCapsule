import time
import sqlite3
import json
import adafruit_fingerprint
import cv2
import face_recognition
from hardware.st7789_driver import ST7789_Driver
from PIL import Image, ImageDraw, ImageFont

def update_enroll_screen(disp, title, msg, color="BLUE", cmd_id=None, db_path=None):
    # 1. Update Physical Screen
    if disp:
        disp.set_backlight(True) # Ensure backlight is ON
        bg_color = (0, 0, 150) 
        if color == "GREEN": bg_color = (0, 150, 0)
        if color == "RED": bg_color = (150, 0, 0)
        image = Image.new("RGB", (disp.width, disp.height), bg_color)
        draw = ImageDraw.Draw(image)
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        draw.rectangle((5, 5, disp.width-5, disp.height-5), outline="WHITE", width=2)
        draw.text((10, 20), title, font=font_large, fill="WHITE")
        y = 70
        for line in msg.split('\n'):
            draw.text((10, y), line, font=font_small, fill="WHITE")
            y += 30
        disp.display(image)

    # 2. Update Database for App Sync
    if cmd_id and db_path:
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("UPDATE Pending_Commands SET detail_message = ? WHERE cmd_id = ?", (msg, cmd_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Sync Error: {e}")

def save_face_to_db(user_id, encoding, db_path):
    # ... (unchanged)
    encoding_json = json.dumps(encoding.tolist())
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET face_encoding = ? WHERE user_id = ?", (encoding_json, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DB Error: {e}")
        return False

def run_face_enrollment(disp, face_rec, user_id, db_path, cmd_id=None):
    print(f"开始为人脸录入 ID: {user_id} / Enrollment Face")
    update_enroll_screen(disp, "ENROLL FACE", "Regardez camera\nLook at camera", cmd_id=cmd_id, db_path=db_path)
    start_time = time.time()
    while time.time() - start_time < 20:
        ret, frame = face_rec.cap.read()
        if not ret:
            time.sleep(0.1); continue
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb_frame)
        if len(locs) == 1:
            update_enroll_screen(disp, "CAPTURE", "Visage detecte\nNe bougez pas!", cmd_id=cmd_id, db_path=db_path)
            encodings = face_recognition.face_encodings(rgb_frame, locs)
            if encodings:
                if save_face_to_db(user_id, encodings[0], db_path):
                    update_enroll_screen(disp, "SUCCES", "Visage Enregistre", "GREEN", cmd_id=cmd_id, db_path=db_path)
                    time.sleep(2); return True
        elif len(locs) > 1:
            update_enroll_screen(disp, "ERREUR", "Trop de visages\nOnly one person", "RED", cmd_id=cmd_id, db_path=db_path)
        time.sleep(0.1)
    update_enroll_screen(disp, "ECHEC", "Timeout (20s)", "RED", cmd_id=cmd_id, db_path=db_path)
    time.sleep(2); return False

def run_finger_enrollment(disp, finger, user_id, db_path, cmd_id=None, finger_label=None):
    title = f"FINGER: {finger_label}" if finger_label else "ENROLL FINGER"
    print(f"开始为指纹录入 ID: {user_id} ({finger_label}) / Enrollment")
    update_enroll_screen(disp, title, "Placez doigt\nPlace finger", cmd_id=cmd_id, db_path=db_path)
    
    start_time = time.time()
    timeout = 30 # 30秒超时
    
    # 第一次按压
    while finger.get_image() != adafruit_fingerprint.OK:
        if time.time() - start_time > timeout:
            update_enroll_screen(disp, "TIMEOUT", "Trop long", "RED", cmd_id=cmd_id, db_path=db_path)
            time.sleep(2)
            return False
    
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        update_enroll_screen(disp, "ECHEC", "Erreur Image 1", "RED", cmd_id=cmd_id, db_path=db_path)
        time.sleep(2); return False
        
    update_enroll_screen(disp, "ETAPE 1 OK", "Retirez doigt\nRemove finger", cmd_id=cmd_id, db_path=db_path)
    time.sleep(1)
    
    # 等待移开手指
    start_time = time.time()
    while finger.get_image() != adafruit_fingerprint.NOFINGER:
        if time.time() - start_time > timeout: return False
        
    update_enroll_screen(disp, "ETAPE 2", "Placez encore\nSame finger", cmd_id=cmd_id, db_path=db_path)
    
    # 第二次按压
    start_time = time.time()
    while finger.get_image() != adafruit_fingerprint.OK:
        if time.time() - start_time > timeout:
            update_enroll_screen(disp, "TIMEOUT", "Trop long", "RED", cmd_id=cmd_id, db_path=db_path)
            time.sleep(2); return False
            
    if finger.image_2_tz(2) != adafruit_fingerprint.OK:
        update_enroll_screen(disp, "ECHEC", "Erreur Image 2", "RED", cmd_id=cmd_id, db_path=db_path)
        time.sleep(2); return False
        
    if finger.create_model() == adafruit_fingerprint.OK:
        if finger.store_model(user_id) == adafruit_fingerprint.OK:
            try:
                conn = sqlite3.connect(db_path)
                conn.execute("UPDATE Users SET has_fingerprint=1 WHERE user_id=?", (user_id,))
                conn.commit(); conn.close()
            except: pass
            update_enroll_screen(disp, "SUCCES", "Empreinte OK", "GREEN", cmd_id=cmd_id, db_path=db_path)
            time.sleep(2); return True
    
    update_enroll_screen(disp, "ECHEC", "Erreur Match", "RED", cmd_id=cmd_id, db_path=db_path)
    time.sleep(2); return False