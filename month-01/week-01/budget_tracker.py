import json
from datetime import datetime, date
from collections import defaultdict

DATA_FILE = "budget_data.json"

# ──────────────────────────────────────
# DATA LAYER — storage and retrieval only
# ──────────────────────────────────────
class BudgetData:
    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.data = self._load()

    def _load(self):
        # Read JSON file, return dict with "budgets" and "expenses"
        # Handle missing file (first run) — return empty structure
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            print("No data found. Starting with an empty budget.")
            # Return empty structure
            initial_data = {"budgets": {}, "expenses": []}
            return initial_data
        except json.JSONDecodeError:
            print("Invalid JSON format. Starting with an empty budget.")
            # Return empty structure
            initial_data = {"budgets": {}, "expenses": []}
            return initial_data

    def save(self):
        # Write self.data to JSON file
        # Handle file write errors
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=4)
            print("Data saved successfully.")
        except IOError as e:
            print(f"Error saving data: {e}")

    @property
    def budgets(self):
        # Return the budgets dictionary
        return self.data["budgets"]

    @budgets.setter
    def budgets(self, value):
        # Set the budgets dictionary
        self.data["budgets"] = value

    @property
    def expenses(self):
        # Return the expenses list
        return self.data["expenses"]
    
    @expenses.setter
    def expenses(self, value):
        # Set the expenses list
        self.data["expenses"] = value


# ──────────────────────────────────────
# BUSINESS LOGIC — rules and calculations
# ──────────────────────────────────────
class BudgetManager:
    def __init__(self, data: BudgetData):
        self.data = data

    def set_budget(self, category, amount):
        # Add or update a budget category
        self.data.budgets[category] = amount
        self.data.save()

    def add_expense(self, amount, category, description):
        # Create expense record with today's date, append, save
        expense = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "description": description,
            "category": category
        }
        self.data.expenses.append(expense)
        self.data.save()

    def get_monthly_spending(self):
        # Filter expenses to current month
        # Return dict: {category: total_spent}
        # Use defaultdict(float) for accumulation
        monthly_spending = defaultdict(float)
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        for expense in self.data.expenses:
            try:
                expense_date = datetime.strptime(expense["date"], "%Y-%m-%d")
                if expense_date.month == current_month and expense_date.year == current_year:
                    monthly_spending[expense["category"]] += expense["amount"]
            except (ValueError, KeyError):
                # Skip invalid dates or malformed entries
                continue

        return dict(monthly_spending)

    def get_budget_status(self):
        # For each budgeted category, return:
        # {category: {"budget": x, "spent": y, "percent": z, "alert": "green/yellow/orange/red"}}
        spending = self.get_monthly_spending()
        status = {}

        for category, budget in self.data.budgets.items():
            spent = spending.get(category, 0)
            percent = (spent / budget) * 100 if budget > 0 else 0

            # Determine alert level based on percent spent
            if percent >= 90:
                alert = "red"
            elif percent >= 75:
                alert = "orange"
            elif percent >= 50:
                alert = "yellow"
            else:
                alert = "green"

            status[category] = {
                "budget": budget,
                "spent": spent,
                "percent": round(percent, 2),
                "alert": alert,
            }

        return status

    def get_daily_remaining(self, category):
        # (budget - spent) / days remaining in month
        spending = self.get_monthly_spending()
        budget = self.data.budgets.get(category, 0)
        spent = spending.get(category, 0)
        
        if budget <= spent:
            return 0
        
        today = date.today()
        if today.month == 12:
            next_month = date(today.year + 1, 1, 1)
        else:
            next_month = date(today.year, today.month + 1, 1)
        
        days_in_month = (next_month - date(today.year, today.month, 1)).days
        days_remaining = days_in_month - today.day

        if days_remaining <= 0:
            return 0
        
        remaining_budget = budget - spent
        return remaining_budget / days_remaining


# ──────────────────────────────────────
# PRESENTATION — user interaction and display
# ──────────────────────────────────────
class BudgetApp:
    def __init__(self):
        self.data = BudgetData()
        self.manager = BudgetManager(self.data)

    def run(self):
        # Main menu loop
        while True:
            print("\n1. View Budget Summary")
            print("2. Add Expense")
            print("3. Set Monthly Budget")
            print("4. Exit")
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.show_budget_summary()
            elif choice == '2':
                self.add_expense_prompt()
            elif choice == '3':
                self.set_budget_prompt()
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def show_budget_summary(self):
        # Get status from manager, format and display
        # Use alert levels to show status indicators
        status = self.manager.get_budget_status()
        
        if not status:
            print("\nNo budget data available.")
            return
        
        print("\n--- Budget Summary ---")
        for category, info in status.items():
            alert_symbol = {
                "green": "🟢",
                "yellow": "🟡",
                "orange": "🟠",
                "red": "🔴"
            }[info["alert"]]

            print(f"{alert_symbol} {category}")
            print(f"  - Budget: ${info['budget']}")
            print(f"  - Spent: ${info['spent']}")
            print(f"  - Percent: {info['percent']}%")
        print("--- End Summary ---")

    def add_expense_prompt(self):
        # Get input, validate, pass to manager
        try:
            amount = float(input("Enter expense amount: "))
            category = input("Enter expense category: ")
            description = input("Enter expense description: ")

            self.manager.add_expense(amount, category, description)
            print("Expense added successfully.")
        except ValueError:
            print(f"Invalid amount for {category}. Please enter a number")
        except Exception as e:
            print(f"An error occurred: {e}")

    def set_budget_prompt(self):
        # Get category and amount, pass to manager
        try:
            category = input("Enter category: ")
            amount = float(input("Enter budget amount: $"))
            
            self.manager.set_budget(category, amount)
            print("Budget set successfully!")
        except ValueError:
            print(f"Invalid amount for {category}. Please enter a number")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    app = BudgetApp()
    app.run()