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

class UserCreate(BaseModel):
    name: str
    auth_level: int = 2 # Default to normal user
    assigned_channel: Optional[int] = None
    app_token: Optional[str] = None # New: Bind immediately on creation

class UserUpdate(BaseModel):
    name: Optional[str] = None
    auth_level: Optional[int] = None
    assigned_channel: Optional[int] = None # Use None to release

class AuthRequest(BaseModel):
    token: str

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
        
        # Fixed: 'has_face' column does not exist in DB (it is derived from face_encoding).
        # Removed has_face from INSERT. has_fingerprint exists and defaults to 0.
        cursor.execute("""
            INSERT INTO Users (name, auth_level, assigned_channel, app_token, created_at, has_fingerprint, is_active)
            VALUES (?, ?, ?, ?, ?, 0, 1)
        """, (user.name, user.auth_level, user.assigned_channel, user.app_token, now))
        
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

@app.patch("/users/{user_id}", response_model=User)
def update_user(user_id: int, update_data: UserUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Check if user exists
        cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Check channel conflict
        if update_data.assigned_channel is not None:
            cursor.execute("SELECT user_id FROM Users WHERE assigned_channel = ? AND user_id != ?", 
                           (update_data.assigned_channel, user_id))
            conflict_user = cursor.fetchone()
            if conflict_user:
                conn.close()
                raise HTTPException(status_code=400, detail=f"Channel {update_data.assigned_channel} is already assigned to user {conflict_user['user_id']}")

        # 3. Dynamic Update
        data_dict = update_data.model_dump(exclude_unset=True)
        if not data_dict and update_data.assigned_channel is None and "assigned_channel" not in update_data.model_fields_set:
             conn.close()
             raise HTTPException(status_code=400, detail="No fields provided")

        update_fields = []
        params = []
        for key, value in data_dict.items():
            update_fields.append(f"{key} = ?")
            params.append(value)
            
        params.append(user_id)
        sql = f"UPDATE Users SET {', '.join(update_fields)} WHERE user_id = ?"
        cursor.execute(sql, params)
        conn.commit()
        
        # 4. Return result
        cursor.execute("""
            SELECT 
                user_id, name, auth_level, assigned_channel, created_at, is_active,
                has_fingerprint, app_token,
                CASE WHEN face_encoding IS NOT NULL THEN 1 ELSE 0 END as has_face
            FROM Users WHERE user_id = ?
        """, (user_id,))
        updated_user = cursor.fetchone()
        conn.close()
        return dict(updated_user)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update Error: {str(e)}")

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists and check permission
        cursor.execute("SELECT user_id, auth_level FROM Users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
            
        # Protect Admin
        if user['user_id'] == 1 or user['auth_level'] <= 1:
            conn.close()
            raise HTTPException(status_code=403, detail="Cannot delete Administrator")

        # Queue command for hardware
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
