import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add the parent directory to the system path to allow imports from there
from mcp.server.fastmcp import FastMCP
from database.db_manager import add_task, get_all_tasks, update_task_status, delete_task, get_task_by_id



# initialize the FastMCP server
mcp = FastMCP("TskthonStudio")


@mcp.tool()
def create_todo_task(title: str, description: str) -> str:
    """
    Creates a brand new to-do task item inside the database.
    Use this tool whenever the user explicitly asks to add, save, or write down a task.
    """
    try:
        task_id = add_task(title, description)
        return f"Task created with ID: {task_id}"
    except Exception as e:
        return f"Error creating task: {str(e)}"


@mcp.tool()
def fetch_all_tasks() -> list:
    """
    Retrieves the complete catalog list of all tasks currently registered in the database.
    Use this tool when the user wants to check, view, or look over their to-do items.
    """
    try:
        tasks = get_all_tasks()
        if not tasks:
            return "No tasks found."

        # Format tasks for better readability
        output = "Here are your current tasks:\n"
        for t in tasks:
            desc = f" ({t['description']})" if t['description'] else ""
            output += f"- [ID: {t['id']}] {t['title']} | Status: {t['status']}{desc}\n"
        return output
    except Exception as e:
        return f"Error fetching tasks: {str(e)}"


@mcp.tool()
def modify_todo_task_status(task_id: int, new_status: str) -> str:
    """
    Updates the current progress state of a specific task using its numerical ID.
    The status variable must strictly be one of: 'pending', 'in_progress', or 'completed'.
    Use this tool when the user says they finished a task, started working on it, or want to reset it.
    """

    status_clean = new_status.strip().lower().replace("-", "_")
    if status_clean not in ['pending', 'in_progress', 'completed']:
        return "Invalid status. Please use 'pending', 'in_progress', or 'completed'."
    
    try:
        task = get_task_by_id(task_id)
        if not task:
            return f"No task found with ID: {task_id}"
        
        update_task_status(task_id, status_clean)
        return f"Task ID {task_id} status updated to '{status_clean}'."
    except Exception as e:
        return f"Error updating task status: {str(e)}"
    
@mcp.tool()
def remove_todo_task(task_id: int) -> str:
    """
    Permanently deletes a specific task from the database using its unique numerical ID.
    Use this tool when the user explicitly asks to delete or remove a task from their list.
    """
    try:
        task = get_task_by_id(task_id)
        if not task:
            return f"No task found with ID: {task_id}"
        
        delete_task(task_id)
        return f"Task ID {task_id} has been deleted."
    except Exception as e:
        return f"Error deleting task: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")