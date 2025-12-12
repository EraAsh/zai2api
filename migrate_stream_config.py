import sqlite3
import os

DB_PATH = os.path.join('instance', 'zai2api.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database not found. Skipping migration.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("SELECT stream_conversion_enabled FROM system_config LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding stream_conversion_enabled column...")
        cursor.execute("ALTER TABLE system_config ADD COLUMN stream_conversion_enabled BOOLEAN DEFAULT 0")
        conn.commit()
        print("Migration done.")
    except Exception as e:
        print(f"Error checking column: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

