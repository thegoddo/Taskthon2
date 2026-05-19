import argparse
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_manager import initialize_db, add_task, get_all_tasks, update_task_status, delete_task

def handle_add(arg):
    """Handler for adding a new task."""
    task_id = add_task(arg.title, arg.desc)
    print(f"Task added successfully with ID: {task_id}")
    
def handle_list(arg):
    """Handler for listing all tasks."""
    tasks = get_all_tasks()
    if not tasks:
        print("No tasks found.")
        return
    
    for task in tasks:
        print(f"ID: {task['id']} | Title: {task['title']} | Status: {task['status']} | Created At: {task['created_at']}")
        if task['description']:
            print(f"   Description: {task['description']}")
            
def handle_update(arg):
    """Handler for updating a task's status."""
    try:
        if update_task_status(arg.id, arg.status):
            print(f"Task with ID {arg.id} updated successfully.")
        else:
            print(f"Error: Task with ID {arg.id} not found.")
    except ValueError as e:
        print(f"Error: {e}")
        
def handle_delete(arg):
    """Handler for deleting a task."""
    try:
        if delete_task(arg.id):
            print(f"Task with ID {arg.id} deleted successfully.")
        else:
            print(f"Error: Task with ID {arg.id} not found.")
    except Exception as e:
        print(f"Error: {e}")
        
def handle_ask(arg):
    """Handler for asking the AI agent."""
    from ai_agent.agent import run_ai_command
    import asyncio
    
    print(f"Prompting AI Agent with: \"{arg.prompt}\"")
    response = asyncio.run(run_ai_command(arg.prompt))
    print(f"AI Agent Response:\n{response}")
        
    
def main():
    initialize_db()
    
    parser = argparse.ArgumentParser(description="Task Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    
    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new task")
    parser_add.add_argument("title", type=str, help="Title of the task")
    parser_add.add_argument("--desc", type=str, default="", help="Description of the task")
    parser_add.set_defaults(func=handle_add)
    
    # List command
    parser_list = subparsers.add_parser("list", help="List all tasks")
    parser_list.set_defaults(func=handle_list)
    
    # Update command
    parser_update = subparsers.add_parser("update", help="Update a task's status")
    parser_update.add_argument("id", type=int, help="ID of the task to update")
    parser_update.add_argument("--status", type=str, help="New status for the task")
    parser_update.set_defaults(func=handle_update)
    
    # Delete command
    parser_delete = subparsers.add_parser("delete", help="Delete a task")
    parser_delete.add_argument("id", type=int, help="ID of the task to delete")
    parser_delete.set_defaults(func=handle_delete)

    # Ask command (Cleaned up duplicate)
    parser_ask = subparsers.add_parser("ask", help="Ask the AI agent to manage your tasks")
    parser_ask.add_argument("prompt", type=str, help="Natural language request for the AI")
    parser_ask.set_defaults(func=handle_ask)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()