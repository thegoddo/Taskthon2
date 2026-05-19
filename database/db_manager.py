import sqlite3
from datetime import datetime

DB_NAME = "tasks.db"

def get_connection():
    """Established and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row # Let's us access columns by name(e.g., row['column_name'])
    return conn

