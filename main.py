import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime
import sqlite3

class Task:
    def __init__(self, name, priority, exec_name, start_date, deadline):
        self.name = name
        self.priority = priority
        self.exec_name = exec_name
        self.start_date = start_date
        self.deadline = deadline
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "Передана в работу"

    def save_to_db(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (name, priority, exec_name, start_date, deadline, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.name, self.priority, self.exec_name, self.start_date, self.deadline, self.timestamp, self.status))
        conn.commit()

    def delete_from_db(self, conn):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE name=? AND priority=? AND exec_name=? AND start_date=? AND deadline=? AND timestamp=? AND status=?",
                       (self.name, self.priority, self.exec_name, self.start_date, self.deadline, self.timestamp, self.status))
        conn.commit()

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")

        self.tasks = []

        self.task_name_var = tk.StringVar()
        self.priority_var = tk.StringVar()
        self.exec_name_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.deadline_var = tk.StringVar()

        self.create_widgets()
        self.connect_to_db()
        self.populate_task_list()

    def create_widgets(self):
        tk.Label(self.root, text="Задача:").grid(row=0, column=0, sticky="w")
        task_name_entry = tk.Entry(self.root, textvariable=self.task_name_var)
        task_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Приоритет:").grid(row=1, column=0, sticky="w")
        priority_values = ["Низкий", "Средний", "Высокий"]
        priority_dropdown = ttk.Combobox(self.root, textvariable=self.priority_var, values=priority_values)
        priority_dropdown.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Исполнитель:").grid(row=2, column=0, sticky="w")
        exec_name_entry = tk.Entry(self.root, textvariable=self.exec_name_var)
        exec_name_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Дата начала:").grid(row=3, column=0, sticky="w")
        start_date_entry = DateEntry(self.root, textvariable=self.start_date_var, date_pattern="yyyy-mm-dd")
        start_date_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Дедлайн:").grid(row=4, column=0, sticky="w")
        deadline_entry = DateEntry(self.root, textvariable=self.deadline_var, date_pattern="yyyy-mm-dd")
        deadline_entry.grid(row=4, column=1, padx=10, pady=5)

        add_task_button = tk.Button(self.root, text="Добавить задачу", command=self.add_task)
        add_task_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        self.task_list_treeview = ttk.Treeview(self.root, columns=("Priority", "Executive", "Start Date", "Deadline", "Timestamp", "Status"))
        self.task_list_treeview.grid(row=6, column=0, columnspan=2, padx=10, pady=5)
        self.task_list_treeview.heading("#0", text="Задача")
        self.task_list_treeview.heading("Priority", text="Приоритет")
        self.task_list_treeview.heading("Executive", text="Исполнитель")
        self.task_list_treeview.heading("Start Date", text="Дата начала")
        self.task_list_treeview.heading("Deadline", text="Дедлайн")
        self.task_list_treeview.heading("Timestamp", text="Таймстамп")
        self.task_list_treeview.heading("Status", text="Статус")

        delete_task_button = tk.Button(self.root, text="Удалить задачу", command=self.delete_task)
        delete_task_button.grid(row=7, column=0, padx=10, pady=5, sticky="w")

        clear_task_button = tk.Button(self.root, text="Очистить поля ввода", command=self.clear_task)
        clear_task_button.grid(row=7, column=1, padx=10, pady=5, sticky="e")

    def connect_to_db(self):
        self.conn = sqlite3.connect("tasks.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                name TEXT,
                priority TEXT,
                exec_name TEXT,
                start_date TEXT,
                deadline TEXT,
                timestamp TEXT,
                status TEXT
            )
        """)
        self.conn.commit()

    def populate_task_list(self):
        self.cursor.execute("SELECT * FROM tasks")
        tasks = self.cursor.fetchall()
        for task in tasks:
            self.task_list_treeview.insert("", tk.END, text=task[1], values=(task[2], task[3], task[4], task[5], task[6], task[7]))

    def add_task(self):
        name = self.task_name_var.get()
        priority = self.priority_var.get()
        exec_name = self.exec_name_var.get()
        start_date = self.start_date_var.get()
        deadline = self.deadline_var.get()

        if name and priority and exec_name and start_date and deadline:
            task = Task(name, priority, exec_name, start_date, deadline)
            task.save_to_db(self.conn)

            self.task_list_treeview.insert("", tk.END, text=task.name, values=(task.priority, task.exec_name, task.start_date, task.deadline, task.timestamp, task.status))

            self.task_name_var.set("")
            self.priority_var.set("")
            self.exec_name_var.set("")
            self.start_date_var.set("")
            self.deadline_var.set("")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля.")

    def delete_task(self):
        selected_item = self.task_list_treeview.selection()
        if selected_item:
            task_name = self.task_list_treeview.item(selected_item, "text")
            priority = self.task_list_treeview.item(selected_item, "values")[0]
            exec_name = self.task_list_treeview.item(selected_item, "values")[1]
            start_date = self.task_list_treeview.item(selected_item, "values")[2]
            deadline = self.task_list_treeview.item(selected_item, "values")[3]
            timestamp = self.task_list_treeview.item(selected_item, "values")[4]
            status = self.task_list_treeview.item(selected_item, "values")[5]
            task = Task(task_name, priority, exec_name, start_date, deadline)
            task.timestamp = timestamp
            task.status = status
            task.delete_from_db(self.conn)
            self.task_list_treeview.delete(selected_item)

    def clear_task(self):
        self.task_name_var.set("")
        self.priority_var.set("")
        self.exec_name_var.set("")
        self.start_date_var.set("")
        self.deadline_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
