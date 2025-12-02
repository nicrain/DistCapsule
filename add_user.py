import sqlite3

DATABASE_NAME = "capsule_dispenser.db"

def add_test_user(user_id, name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        # 尝试插入用户，如果 ID 已存在则忽略
        cursor.execute("INSERT OR IGNORE INTO Users (user_id, name, auth_level) VALUES (?, ?, 1)", (user_id, name))
        conn.commit()
        print(f"✅ 用户 '{name}' (ID: {user_id}) 已添加到数据库。")
    except Exception as e:
        print(f"❌ 添加用户失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # 假设您刚才录入的是 ID #1
    add_test_user(1, "Admin User")
