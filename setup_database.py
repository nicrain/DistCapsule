import sqlite3
import os

DATABASE_NAME = "capsule_dispenser.db"

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

    # 检查 face_encoding 列是否存在 (针对旧库升级)
    cursor.execute("PRAGMA table_info(Users)")
    columns = [info[1] for info in cursor.fetchall()]
    if "face_encoding" not in columns:
        print("⚡️ 检测到旧表结构，正在添加 face_encoding 列...")
        cursor.execute("ALTER TABLE Users ADD COLUMN face_encoding TEXT")

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