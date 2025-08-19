import sqlite3

# Path to your SQLite database
DB_PATH = "social_scheduler.db"

ALTERS = [
    "ALTER TABLE posts ADD COLUMN x_post_id TEXT;",
    "ALTER TABLE posts ADD COLUMN likes INTEGER DEFAULT 0;",
    "ALTER TABLE posts ADD COLUMN reposts INTEGER DEFAULT 0;",
    "ALTER TABLE posts ADD COLUMN replies INTEGER DEFAULT 0;"
]

def run_migrations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for sql in ALTERS:
        try:
            cursor.execute(sql)
            print(f"Executed: {sql}")
        except sqlite3.OperationalError as e:
            print(f"Skipped: {sql} (Reason: {e})")
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    run_migrations()
