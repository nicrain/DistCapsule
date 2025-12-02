import sqlite3

DATABASE_NAME = "capsule_dispenser.db"

def setup_database():
    """连接数据库并创建所有必需的表。"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # 1. 创建 Users 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        auth_level INTEGER NOT NULL DEFAULT 2,
        finger_print_path TEXT UNIQUE,
        face_template_path TEXT UNIQUE,
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

    # 3. 创建 System_Settings 表，并插入默认配置
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS System_Settings (
        key_name TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        description TEXT
    );
    """)
    
    # 插入默认设置，防止重复插入使用 REPLACE
    settings = [
        ('UNLOCK_DURATION', '15', '舵机解锁后自动锁定的秒数'),
        ('MAX_AUTH_ATTEMPTS', '5', '指纹/人脸识别最大尝试次数'),
        ('MIN_AUTH_LEVEL', '2', '允许解锁的最低权限级别 (2: 普通用户)'),
    ]

    for key, val, desc in settings:
        cursor.execute("INSERT OR REPLACE INTO System_Settings (key_name, value, description) VALUES (?, ?, ?)", (key, val, desc))

    conn.commit()
    conn.close()
    print(f"数据库 {DATABASE_NAME} 初始化完成。")

if __name__ == "__main__":
    setup_database()
    print(f"数据库 '{DATABASE_NAME}' 初始化完成，包含 3 个表和默认设置。")

# 运行初始化函数
# setup_database()
