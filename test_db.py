# test_db.py
from database.db_manager import initialize_db, add_task, get_all_tasks, update_task_status, delete_task

def run_tests():
    print("--- 1. Initializing Database ---")
    initialize_db()

    print("\n--- 2. Adding Tasks ---")
    task1_id = add_task("Buy groceries for dinner")
    task2_id = add_task("Finish MCA major project proposal", "Draft a PPT for our GIS project.")
    print(f"Added task 1 with ID: {task1_id}")
    print(f"Added task 2 with ID: {task2_id}")

    print("\n--- 3. Fetching All Tasks ---")
    tasks = get_all_tasks()
    for t in tasks:
        print(f"[{t['id']}] {t['title']} - Status: {t['status']} (Created: {t['created_at']})")

    print(f"\n--- 4. Updating Task {task1_id} to Completed ---")
    update_task_status(task1_id, "completed")
    
    print("\n--- 5. Verifying Update & Deleting Task 2 ---")
    remaining_tasks = get_all_tasks()
    for t in remaining_tasks:
        print(f"[{t['id']}] {t['title']} - Status: {t['status']}")
        
    print(f"Deleting task {task2_id}...")
    delete_task(task2_id)

    print("\n--- 6. Final Task List ---")
    print(get_all_tasks())

if __name__ == "__main__":
    run_tests()