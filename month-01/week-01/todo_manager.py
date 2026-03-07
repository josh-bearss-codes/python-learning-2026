import json
from datetime import datetime

TASKS_FILE = "tasks.json"

PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}

class Task:
    def __init__(self, title, priority="Medium", due_date=None, completed=False):
        # store attributes
        self.title = title
        self.priority = priority
        self.due_date = due_date or datetime.now().strftime("%Y-%m-%d")
        self.completed = completed

    def to_dict(self):
        # for JSON serialization
        return {
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date if self.due_date else None,
            "completed": self.completed
            }

    def __str__(self):
        # formatted display: [✓] Buy groceries (High) - Due: 2026-03-10
        return f"[{'✓' if self.completed else ' '}] {self.title} ({self.priority} - Due: {self.due_date.strftime("%Y-%m-%d") if self.due_date else 'N/A'})"

class TodoManager:
    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self):
        # read JSON, create Task objects, return list
        try:
            with open("tasks.json", "r") as file:
                tasks_data = json.load(file)
                task_list = [Task(**task) for task in tasks_data]
                return task_list
        except (FileNotFoundError, json.JSONDecodeError):
           return []

    def save_tasks(self):
        # convert to dicts, write JSON
        tasks_dicts = [task.to_dict() for task in self.tasks]
        with open("tasks.json", "w") as file:
            json.dump(tasks_dicts, open("tasks.json", "w"), indent=4)
        return self.tasks

    def add_task(self):
        # get title, priority (validate: must be High/Medium/Low),
        # due date (validate format or blank), create Task, save
        title = input("Enter task title: ").strip()
        if not title:
            print("Title cannot be empty.")
            return
        
        while True:
            priority = input("Enter task priority (High/Medium/Low): ").strip().capitalize()
            if priority in ["High", "Medium", "Low"]:
                break
            else: print("Invalid priority. Please enter High, Medium, or Low.")

        # due date validation
        due_date = None
        while True:
            date_str = input("Enter due date (YYYY-MM-DD) or leave blank: ").strip()
            if not date_str:
                break
            try:
                due_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Invalid date format. Please enter YYYY-MM-DD format.")

        # create task and save
        task = Task(title, priority, due_date)
        self.tasks.append(task)
        self.save_tasks()
        print(f"Task '{title}' has been added successfully!")


    def view_tasks(self, filter_fn=None, sort_key=None):
        # apply optional filter, apply optional sort
        # display numbered list
        filtered_tasks = self.tasks[:]
        
        if filter_fn:
            self.tasks = list(filter(filter_fn, filtered_tasks))

        if sort_key:
            filtered_tasks.sort(key=sort_key)

        if not filtered_tasks:
            print("No tasks found.")
            return

        for i, task in enumerate(self.tasks, 1):
            status = "✓" if task.completed else "○"
            due_info = f"Due: {task.due_date}" if task.due_date else "No due date"
            print(f"{i}. [{status}] {task.title} - {task.priority} - {due_info}")
        

    def mark_complete(self):
        # show incomplete tasks, user picks number
        incomplete_tasks = [task for task in self.tasks if not task.completed]
        
        if not incomplete_tasks:
            print("No incomplete tasks.")
            return
        
        for i, task in enumerate(incomplete_tasks, 1):
            due_info = f"Due: {task.due_date}" if task.due_date else "No due date"
            print(f"{i}. {task.title} - {task.priority} - Due: {due_info}")

        print("Select a task to mark as complete:")
        while True:
            try:
                task_number = int(input("Task number: "))
                if 1 <= task_number <= len(incomplete_tasks):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(incomplete_tasks)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

            incomplete_tasks[task_number - 1].completed = True
            self.save_tasks()
            print("Task marked as complete.")
        
    def delete_task(self):
        # show all tasks, user picks number to delete
        if not self.tasks:
            print("No tasks to delete.")
            return

        for i, task in enumerate(self.tasks, 1):
            due_info = f"Due: {task.due_date}" if task.due_date else "No due date"
            print(f"{i}. {task.title} - {task.priority} - Due: {due_info}")
        
        print("Select a task to delete:")
        while True:
            try:
                task_number = int(input("Task number: "))
                if 1 <= task_number <= len(self.tasks):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(self.tasks)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        deleted_task = self.tasks.pop(task_number - 1)
        self.save_tasks()
        print(f"Task '{deleted_task.title}' deleted.")

def main():
    manager = TodoManager()
    while True:
        print("\n--- Todo Manager ---")
        print("1. Add task")
        print("2. View all tasks")
        print("3. View incomplete tasks")
        print("4. View by priority (High first)")
        print("5. Mark task complete")
        print("6. Delete task")
        print("7. Quit")
        choice = input("Choose: ")

        if choice == "1":
            manager.add_task()
        elif choice == "2":
            manager.view_tasks()
        elif choice == "3":
            manager.view_tasks(filter_fn=lambda t: not t.completed)
        elif choice == "4":
            manager.view_tasks(sort_key=lambda t: PRIORITY_ORDER.get(t.priority, 99))
        elif choice == "5":
            manager.mark_complete()
        elif choice == "6":
            manager.delete_task()
        elif choice == "7":
            manager.save_tasks()
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()