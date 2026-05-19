import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import initialize_db, add_task, get_all_tasks, update_task_status, delete_task, get_task_by_id


class TodoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Enhanced To-Do Studio")
        # Slightly widened to accommodate description header nicely
        self.root.geometry("950x550")
        self.root.minsize(850, 450)

        # Ensure database is configured
        initialize_db()

        # Main Layout
        self.setup_layout()
        self.build_task_panel()
        self.build_ai_panel()

        # Initial data load
        self.refresh_task_list()

    def setup_layout(self):
        """Creates the structural left and right layouts."""
        self.left_frame = ttk.Frame(self.root, padding=10)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        separator = ttk.Separator(self.root, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.right_frame = ttk.Frame(self.root, padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def build_task_panel(self):
        """Constructs the visual task viewer and creation form on the left."""
        # --- Form Area ---
        form_frame = ttk.LabelFrame(
            self.left_frame, text=" Create New Task ", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text="Title:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        self.title_entry = ttk.Entry(form_frame)
        self.title_entry.grid(row=0, column=1, sticky=tk.W + tk.E, pady=2)

        ttk.Label(form_frame, text="Desc:").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        self.desc_entry = ttk.Entry(form_frame)
        self.desc_entry.grid(row=1, column=1, sticky=tk.W + tk.E, pady=2)

        # Configure weight so columns expand cleanly
        form_frame.columnconfigure(1, weight=1)

        btn_add = ttk.Button(form_frame, text="Add Task",
                             command=self.ui_add_task)
        btn_add.grid(row=2, column=0, columnspan=2, pady=(5, 0), sticky=tk.E)

        # --- Treeview Task List Area ---
        list_frame = ttk.LabelFrame(
            self.left_frame, text=" Task Inventory (Double-click to inspect) ", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # FIX: Added 'description' to columns tuple
        columns = ("id", "title", "status", "description")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse")

        # FIX: Configured headings and widths, including the new description column
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Task Title")
        self.tree.heading("status", text="Status")
        self.tree.heading("description", text="Description")

        self.tree.column("id", width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.tree.column("title", width=150, stretch=tk.YES)
        self.tree.column("status", width=90, stretch=tk.NO, anchor=tk.CENTER)
        # Description column config
        self.tree.column("description", width=180, stretch=tk.YES)

        # Bind the Double-Click event to open our modal detail viewer
        self.tree.bind("<Double-1>", self.ui_open_task_modal)

        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Action Control Buttons ---
        btn_frame = ttk.Frame(self.left_frame, padding=5)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Mark Complete", command=lambda: self.ui_update_status(
            "completed")).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Mark In-Progress",
                   command=lambda: self.ui_update_status("in_progress")).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Task",
                   command=self.ui_delete_task).pack(side=tk.RIGHT, padx=2)

    def build_ai_panel(self):
        """Constructs the conversation box for the upcoming LangChain/MCP setup."""
        ai_frame = ttk.LabelFrame(
            self.right_frame, text=" LangChain AI Assistant ", padding=5)
        ai_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_display = tk.Text(
            ai_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f4f4f6", fg="#333333")
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_frame = ttk.Frame(ai_frame)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        self.chat_entry = ttk.Entry(input_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.bind(
            "<Return>", lambda event: self.ui_send_ai_prompt())

        btn_send = ttk.Button(input_frame, text="Ask AI",
                              command=self.ui_send_ai_prompt)
        btn_send.pack(side=tk.RIGHT)

        self.append_to_chat(
            "System", "Welcome! Once Phase 3 and 4 are complete, you can chat with your database here using natural language.")

    # --- Database Interaction Actions ---
    def refresh_task_list(self):
        """Clears the Treeview UI grid and repopulates it directly from SQLite."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in get_all_tasks():
            # Handle empty fields elegantly
            desc = task['description'] if task['description'] else "No description provided."
            # FIX: Included description dictionary value inside the row insertion tuple
            self.tree.insert("", tk.END, values=(
                task['id'], task['title'], task['status'], desc))

    def ui_add_task(self):
        title = self.title_entry.get().strip()
        desc = self.desc_entry.get().strip()
        if not title:
            messagebox.showwarning(
                "Validation Error", "The task title cannot be empty!")
            return

        add_task(title, desc)
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.refresh_task_list()

    def get_selected_task_id(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Selection Error", "Please select a task from the list first.")
            return None
        return self.tree.item(selected_item)['values'][0]

    def ui_update_status(self, target_status):
        task_id = self.get_selected_task_id()
        if task_id:
            update_task_status(task_id, target_status)
            self.refresh_task_list()

    def ui_delete_task(self):
        task_id = self.get_selected_task_id()
        if task_id:
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove Task {task_id}?"):
                delete_task(task_id)
                self.refresh_task_list()

    # --- NEW: Task Modal Detail Inspector Window ---
    def ui_open_task_modal(self, event):
        """Intercepts row double-clicks, fetches fresh data, and opens a detail modal."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        # 1. Grab ONLY the task ID from the selected row
        row_values = self.tree.item(selected_item)['values']
        if not row_values:
            return
        task_id = row_values[0]

        # 2. Fetch the fresh, complete record directly from SQLite
        from database.db_manager import get_task_by_id
        task = get_task_by_id(task_id)
        if not task:
            messagebox.showerror(
                "Error", "Could not retrieve task details from database.")
            return

        title = task['title']
        status = task['status']
        description = task['description'] if task['description'] else "No description provided."

        # 3. Instantiate the modal overlay window
        modal = tk.Toplevel(self.root)
        modal.title(f"Task Details - ID: {task_id}")
        modal.geometry("450x320")
        modal.transient(self.root)  # Keep on top of main window
        modal.wait_visibility() # Ensure it appears before grab_set
        modal.grab_set()            # Block interaction with main window

        # Padding content container frame
        container = ttk.Frame(modal, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # UI Display elements
        ttk.Label(container, text="Task Title:", font=(
            "Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 2))
        title_lbl = ttk.Label(container, text=title, font=(
            "Arial", 11), wraplength=400, justify=tk.LEFT)
        title_lbl.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(container, text="Current Status:", font=(
            "Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 2))
        status_color = "#2a75d3" if status == "in_progress" else "#1b8a5a" if status == "completed" else "#555555"
        status_lbl = ttk.Label(container, text=status.upper(
        ), foreground=status_color, font=("Arial", 10, "bold"))
        status_lbl.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(container, text="Detailed Description:", font=(
            "Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 2))

        # Text view for long/multi-line descriptions
        desc_text = tk.Text(container, height=6, wrap=tk.WORD,
                            bg="#ffffff", bd=1, relief=tk.SOLID, font=("Arial", 10))
        desc_text.insert(tk.END, description)
        desc_text.config(state=tk.DISABLED)  # Make read-only
        desc_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Close Button
        ttk.Button(container, text="Close Details", command=modal.destroy).pack(
            side=tk.BOTTOM, anchor=tk.E)

    # --- Simulated AI Window Controls ---
    def append_to_chat(self, sender, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{sender}]: {text}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def ui_send_ai_prompt(self):
        """Routes natural language strings into LangChain, updates chat, and refreshes tables."""
        prompt = self.chat_entry.get().strip()
        if not prompt:
            return

        # 1. Post user question immediately onto chat log
        self.append_to_chat("You", prompt)
        self.chat_entry.delete(0, tk.END)
        
        # 2. Tell the user the assistant is processing the query
        self.append_to_chat("Agent", "Thinking... Processing database transaction.")
        self.root.update_idletasks()  # Forces Tkinter to redraw the screen immediately

        # 3. Import and execute our async LangChain engine
        try:
            import asyncio
            from ai_agent.agent import run_ai_command
            
            # Execute the asynchronous pipeline safely inside our GUI window callback
            ai_response = asyncio.run(run_ai_command(prompt))
            
            # 4. Append the tool completion response into the chat panel log
            self.append_to_chat("Agent", ai_response)
            
            # 5. Instantly refresh the left-hand task view grid!
            self.refresh_task_list()
            
        except Exception as e:
            self.append_to_chat("System Error", f"Failed to reach AI Core: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoGUI(root)
    root.mainloop()
