from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from typing import List, Optional

app = FastAPI(title="DistCapsule API", description="API for Smart Capsule Dispenser")

# --- Database Config ---
# Ensure we find the DB relative to this file, assuming structure:
# /project_root
#   /api/server.py
#   capsule_dispenser.db
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
    created_at: Optional[str] = None
    is_active: int

# ...

@app.get("/users", response_model=List[User])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Calculate has_face on the fly, but read has_fingerprint from column
        cursor.execute("""
            SELECT 
                user_id, name, auth_level, assigned_channel, created_at, is_active,
                has_fingerprint,
                CASE WHEN face_encoding IS NOT NULL THEN 1 ELSE 0 END as has_face
            FROM Users
        """)
        rows = cursor.fetchall()
        conn.close()
        # Convert sqlite3.Row objects to dicts for Pydantic
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)} | DB Path: {DATABASE_NAME}")

@app.get("/logs", response_model=List[AccessLog])
def get_logs(limit: int = 20):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT log_id, user_id, timestamp, event_type, status, detail_message FROM Access_Logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Future endpoint for App to trigger actions (Phase 2)
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
