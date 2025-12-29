import sqlite3
import os

DATABASE_NAME = "capsule_dispenser.db"

def setup_database():
    """连接数据库并创建所有必需的表。"""
    # 如果为了开发方便，可以先删除旧库(慎用)
    # if os.path.exists(DATABASE_NAME):
    #     os.remove(DATABASE_NAME)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # 1. 创建 Users 表
    # 更新：加入 assigned_channel (1-5) 用于分配舵机
    # auth_level: 1=Admin, 2=User
    # user_id 实际上应该对应指纹模块里的 ID (0-127)，所以我们手动指定 user_id 而不是 AUTOINCREMENT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL,
        auth_level INTEGER NOT NULL DEFAULT 2,
        assigned_channel INTEGER,
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