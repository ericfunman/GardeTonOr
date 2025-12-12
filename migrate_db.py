import sqlite3
from src.config import DATABASE_URL


def migrate():
    # Extract path from sqlite:///path/to/db
    db_path = DATABASE_URL.replace("sqlite:///", "")

    print(f"Migrating database at {db_path}...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(contracts)")
        columns = [info[1] for info in cursor.fetchall()]

        if "is_simulation" not in columns:
            print("Adding is_simulation column...")
            cursor.execute("ALTER TABLE contracts ADD COLUMN is_simulation INTEGER DEFAULT 0")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column is_simulation already exists.")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
