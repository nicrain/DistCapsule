import sqlite3
import os

# 动态获取数据库绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATABASE_NAME = os.path.join(PROJECT_ROOT, "capsule_dispenser.db")

def setup_database():
    """连接数据库并创建所有必需的表。"""
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # 1. 创建 Users 表
    # 更新：加入 face_encoding 用于人脸识别
    # face_encoding 将存储为 TEXT (JSON string of list[float])
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL,
        auth_level INTEGER NOT NULL DEFAULT 2,
        assigned_channel INTEGER,
        face_encoding TEXT,
        created_at TEXT,
        is_active INTEGER NOT NULL DEFAULT 1
    );
    """)

    # 2. 创建 Access_Logs 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Access_Logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        status TEXT,
        detail_message TEXT,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    );
    """)

    # 3. 创建 System_Settings 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS System_Settings (
        key_name TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        description TEXT
    );
    """)

    # 4. 创建 Pending_Commands 表 (用于远程控制)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pending_Commands (
        cmd_id INTEGER PRIMARY KEY AUTOINCREMENT,
        command_type TEXT NOT NULL,  -- 例如 'UNLOCK'
        target_id INTEGER,           -- 例如 1 (通道号)
        status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    settings = [
        ('UNLOCK_DURATION', '5', '舵机解锁后自动锁定的秒数'),
        ('MAX_USERS', '5', '最大拥有物理通道的用户数'),
    ]

    for key, val, desc in settings:
        cursor.execute("INSERT OR REPLACE INTO System_Settings (key_name, value, description) VALUES (?, ?, ?)", (key, val, desc))

    conn.commit()
    conn.close()
    print(f"数据库 {DATABASE_NAME} 结构已更新/确认。")

if __name__ == "__main__":
    setup_database()