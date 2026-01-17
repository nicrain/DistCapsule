import time
import sqlite3
import json
import adafruit_fingerprint
import cv2
import face_recognition
from hardware.st7789_driver import ST7789_Driver
from PIL import Image, ImageDraw, ImageFont

def update_enroll_screen(disp, title, msg, color="BLUE"):
    if not disp: return
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

def save_face_to_db(user_id, encoding, db_path):
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

def run_face_enrollment(disp, face_rec, user_id, db_path):
    print(f"开始为人脸录入 ID: {user_id} / Enrollment Face")
    update_enroll_screen(disp, "ENROLL FACE", "Regardez camera\nLook at camera")
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
            update_enroll_screen(disp, "CAPTURE", "Visage detecte\nNe bougez pas!")
            encodings = face_recognition.face_encodings(rgb_frame, locs)
            if encodings:
                if save_face_to_db(user_id, encodings[0], db_path):
                    update_enroll_screen(disp, "SUCCES", "Visage Enregistre", "GREEN")
                    time.sleep(2); return True
        elif len(locs) > 1:
            update_enroll_screen(disp, "ERREUR", "Trop de visages\nOnly one person", "RED")
        time.sleep(0.1)
    update_enroll_screen(disp, "ECHEC", "Timeout (20s)", "RED")
    time.sleep(2); return False

def run_finger_enrollment(disp, finger, user_id, db_path):
    print(f"开始为指纹录入 ID: {user_id} / Enrollment Finger")
    update_enroll_screen(disp, "ENROLL FINGER", "Placez doigt\nPlace finger")
    while finger.get_image() != adafruit_fingerprint.OK: pass
    finger.image_2_tz(1)
    update_enroll_screen(disp, "ETAPE 1 OK", "Retirez doigt\nRemove finger")
    time.sleep(1)
    while finger.get_image() != adafruit_fingerprint.NOFINGER: pass
    update_enroll_screen(disp, "ETAPE 2", "Placez encore\nSame finger")
    while finger.get_image() != adafruit_fingerprint.OK: pass
    finger.image_2_tz(2)
    if finger.create_model() == adafruit_fingerprint.OK:
        if finger.store_model(user_id) == adafruit_fingerprint.OK:
            try:
                conn = sqlite3.connect(db_path)
                conn.execute("UPDATE Users SET has_fingerprint=1 WHERE user_id=?", (user_id,))
                conn.commit(); conn.close()
            except: pass
            update_enroll_screen(disp, "SUCCES", "Empreinte OK", "GREEN")
            time.sleep(2); return True
    update_enroll_screen(disp, "ECHEC", "Erreur Match", "RED")
    time.sleep(2); return False