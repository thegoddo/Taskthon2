import sqlite3
from datetime import datetime

DB_NAME = "tasks.db"


def get_connection():
    """Established and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)

    # Let's us access columns by name(e.g., row['column_name'])
    conn.row_factory = sqlite3.Row
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


def add_task(title, description=""):
    """Inserts a new task into the database."""

    current_time = datetime.now().isoformat()  # Get current time in ISO format
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (title, description, status, created_at) VALUES (?, ?, ?, ?)""", 
            (title, description, "pending", current_time))
        conn.commit()
        return cursor.lastrowid  # Return the ID of the newly created task


def get_all_tasks():
    """Retrieves all tasks from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]  # Convert rows to list of dictionaries
    
def get_task_by_id(task_id: int):
    """Retrieves a single specific task from the database by its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_task_status(task_id, new_status):
    """Updates the status of a task."""
    
    if new_status not in ["pending","in_progress","completed"]:
        raise ValueError("Invalid status. Status must be 'pending', 'in_progress', or 'completed'.")
        
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        return cursor.rowcount > 0
        
def delete_task(task_id):
    """Deletes a task from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0