import json
from datetime import datetime
from collections import defaultdict

EXPENSES_FILE = "expenses.json"

class Expense:
    def __init__(self, amount, category, description, date=None):
        # store attributes with self.xxx = xxx
        # default date to today if not provided
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        # add any other attributes you need

    def to_dict(self):
        # return a dictionary representation
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date
        }

    def __str__(self):
        # return a nice formatted string
        return f"{self.date} - {self.category} - {self.amount:.2f} - {self.description}"

class ExpenseTracker:
    def __init__(self):
        self.expenses = self.load_expenses()

    def load_expenses(self):
        # read JSON, create Expense objects from dicts
        try:
            with open(EXPENSES_FILE, 'r') as file:
                expenses_data = json.load(file)
                return [Expense(**expense_data) for expense_data in expenses_data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_expenses(self):
        # convert expenses to dicts, write JSON
        expenses_data = [expense.to_dict() for expense in self.expenses]
        try:
            with open(EXPENSES_FILE, 'w') as file:
                json.dump(expenses_data, file, indent=4)
                return True
        except Exception as e:
            print(f"Error saving expenses: {e}")
            return False

    def add_expense(self):
        # get input from user, create Expense, append, save
        try:
            amount = float(input("Enter expense amount: "))
            category = input("Enter expense category, example: 'Groceries' or 'Utilities' or 'Entertainment' or 'Travel': ").strip()
            description = input("Enter expense description: ").strip()
            date = input("Enter expense date (YYYY-MM-DD) or press Enter for today: ").strip()
            
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')

            expense = Expense(amount, category, description, date)
            self.expenses.append(expense)
            self.save_expenses()
            print("Expense added successfully!")
        except ValueError:
            print("Invalid amount. Please enter a valid amount.")

    def view_expenses(self, category=None):
        # show all, or filter by category
        if not self.expenses:
            print("No expenses found.")
            return
        
        filtered_expenses = self.expenses 
        if category:
            filtered_expenses = [e for e in self.expenses if e.category.lower() == category.lower()]

        for expense in filtered_expenses:
            print(expense)    

    def get_summary(self):
        # group by category, show totals
        total_expenses = 0
        category_totals = defaultdict(float)
        for expense in self.expenses:
            total_expenses += expense.amount
            category_totals[expense.category] += expense.amount

        print(f"Total expenses: {total_expenses:.2f}")
        for category, total in category_totals.items():
            print(f"{category}: {total:.2f}")
        

def main():
    tracker = ExpenseTracker()
    while True:
        # menu: add, view all, view by category, summary, quit
        # call tracker methods based on choice
        print("\nExpense Tracker")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View Expenses by Category")
        print("4. Get Summary")
        print("5. Quit")
        choice = input("Enter your choice: ")
        if choice == '1':
            tracker.add_expense()

        elif choice == '2':
            tracker.view_expenses()

        elif choice == '3':
            category = input("Enter category: ").strip()
            tracker.view_expenses(category)

        elif choice == '4':
            tracker.get_summary()

        elif choice == '5':
            print("Exiting the tracker.")
            tracker.save_expenses()  # Save before exiting
            break
        else:
            print("Invalid choice. Please try again.")
    # end of main loop

main()