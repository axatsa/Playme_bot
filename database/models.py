import sqlite3

DATABASE_PATH = "users.db"

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            garden TEXT,
            phone_number TEXT)""")
    conn.commit()
except sqlite3.Error as e:
    print("Error creating database:", e)

finally:
    if conn:
        conn.close()