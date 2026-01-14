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
    created_at: Optional[str] = None
    is_active: int

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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, auth_level, assigned_channel, created_at, is_active FROM Users")
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.get("/logs", response_model=List[AccessLog])
def get_logs(limit: int = 20):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT log_id, user_id, timestamp, event_type, status, detail_message FROM Access_Logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Future endpoint for App to trigger actions (Phase 2)
@app.post("/command/unlock")
def remote_unlock(channel: int):
    # This will eventually communicate with main.py
    return {"status": "queued", "message": f"Unlock request for channel {channel} received (Not implemented yet)"}
