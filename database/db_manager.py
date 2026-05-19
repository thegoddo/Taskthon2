import sqlite3
from datetime import datetime

DB_NAME = "tasks.db"

def get_connection():
    """Established and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row # Let's us access columns by name(e.g., row['column_name'])
    return conn

def initialize_db():
    """Creates the tasks table if it doesn't already exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       title TEXT NOT NULL,
                       description TEXT,
                       status TEXT DEFAULT 'pending',
                       created_at TEXT NOT NULL)
                       """)
        conn.commit()
    print("Database initialized successfully.")
