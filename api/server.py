from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from typing import List, Optional

app = FastAPI(title="DistCapsule API", description="API for Smart Capsule Dispenser")

# --- Database Config ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATABASE_NAME = os.path.join(PROJECT_ROOT, "capsule_dispenser.db")

# --- Pydantic Models (Data Structures) ---
class User(BaseModel):
    user_id: int
    name: str
    auth_level: int
    assigned_channel: Optional[int] = None
    has_face: int
    has_fingerprint: int
    app_token: Optional[str] = None
    created_at: Optional[str] = None
    is_active: int

class BindRequest(BaseModel):
    user_id: int
    token: str

class AuthRequest(BaseModel):
    token: str

class UserCreate(BaseModel):
    name: str
    auth_level: int = 2 # Default to normal user
    assigned_channel: Optional[int] = None

class AccessLog(BaseModel):
    log_id: int
    user_id: Optional[int]
    timestamp: str
    event_type: str
    status: Optional[str]
    detail_message: Optional[str]

# --- Helpers ---
def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row # Allow accessing columns by name
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

# --- Routes ---

@app.get("/")
def read_root():
    return {"status": "online", "message": "DistCapsule API is running"}

@app.get("/users", response_model=List[User])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                user_id, name, auth_level, assigned_channel, created_at, is_active,
                has_fingerprint, app_token,
                CASE WHEN face_encoding IS NOT NULL THEN 1 ELSE 0 END as has_face
            FROM Users
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)} | DB Path: {DATABASE_NAME}")

@app.post("/users", response_model=User)
def create_user(user: UserCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check channel availability if assigned
        if user.assigned_channel:
            cursor.execute("SELECT user_id FROM Users WHERE assigned_channel = ?", (user.assigned_channel,))
            if cursor.fetchone():
                conn.close()
                raise HTTPException(status_code=400, detail=f"Channel {user.assigned_channel} is already occupied")

        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO Users (name, auth_level, assigned_channel, created_at, has_face, has_fingerprint, is_active)
            VALUES (?, ?, ?, ?, 0, 0, 1)
        """, (user.name, user.auth_level, user.assigned_channel, now))
        
        new_id = cursor.lastrowid
        conn.commit()
        
        # Fetch the created user to return it
        cursor.execute("""
            SELECT 
                user_id, name, auth_level, assigned_channel, created_at, is_active,
                has_fingerprint, app_token,
                0 as has_face
            FROM Users WHERE user_id = ?
        """, (new_id,))
        new_user = cursor.fetchone()
        conn.close()
        return dict(new_user)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create Error: {str(e)}")

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")

        # Instead of deleting directly, queue a command so hardware can cleanup fingerprint
        cursor.execute(
            "INSERT INTO Pending_Commands (command_type, target_id, status) VALUES (?, ?, ?)",
            ("DELETE_USER", user_id, "pending")
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Delete command queued for user {user_id}"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete Error: {str(e)}")

@app.post("/bind")
def bind_user(req: BindRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Check user exists
        cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (req.user_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
            
        # 2. Update Token (Ensure uniqueness by clearing old binding first)
        cursor.execute("UPDATE Users SET app_token = NULL WHERE app_token = ?", (req.token,))
        cursor.execute("UPDATE Users SET app_token = ? WHERE user_id = ?", (req.token, req.user_id))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Device bound to user {req.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bind Error: {str(e)}")

@app.post("/auth", response_model=User)
def login_by_token(req: AuthRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                user_id, name, auth_level, assigned_channel, created_at, is_active,
                has_fingerprint, app_token,
                CASE WHEN face_encoding IS NOT NULL THEN 1 ELSE 0 END as has_face
            FROM Users WHERE app_token = ?
        """, (req.token,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        else:
            raise HTTPException(status_code=401, detail="Invalid Token")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth Error: {str(e)}")

@app.get("/logs", response_model=List[AccessLog])
def get_logs(limit: int = 20):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT log_id, user_id, timestamp, event_type, status, detail_message FROM Access_Logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@app.post("/command/unlock")
def remote_unlock(channel: int):
    if channel < 1 or channel > 5:
        raise HTTPException(status_code=400, detail="Invalid channel. Must be between 1 and 5.")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Pending_Commands (command_type, target_id, status) VALUES (?, ?, ?)",
            ("UNLOCK", channel, "pending")
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Unlock command for channel {channel} queued."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue command: {str(e)}")

@app.post("/command/enroll_face")
def enroll_face(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Ensure user exists first
        cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        cursor.execute(
            "INSERT INTO Pending_Commands (command_type, target_id, status) VALUES (?, ?, ?)",
            ("ENROLL_FACE", user_id, "pending")
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Face enrollment queued for user {user_id}"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/command/enroll_finger")
def enroll_finger(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Ensure user exists
        cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        cursor.execute(
            "INSERT INTO Pending_Commands (command_type, target_id, status) VALUES (?, ?, ?)",
            ("ENROLL_FINGER", user_id, "pending")
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Fingerprint enrollment queued for user {user_id}"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")