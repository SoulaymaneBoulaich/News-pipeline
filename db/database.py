import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "news.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the articles table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source      TEXT,
            author      TEXT,
            title       TEXT UNIQUE,
            description TEXT,
            url         TEXT,
            published_at TEXT,
            category    TEXT,
            fetched_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized.")


if __name__ == "__main__":
    init_db()
