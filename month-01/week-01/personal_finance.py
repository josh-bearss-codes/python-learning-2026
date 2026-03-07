import json
import csv
import os
from datetime import datetime
from collections import defaultdict

DATA_FILE = "finance_data.json"

# ──────────────────────────────────────
# DATA MODELS — the entities in your system
# ──────────────────────────────────────
class Transaction:
    def __init__(self, amount, category, description, date=None, trans_type="expense"):
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.trans_type = trans_type  # "expense", "income", "transfer"

    def to_dict(self):
        # Convert to dictionary for JSON storage
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
            "trans_type": self.trans_type
        }

    def __str__(self):
        # Formatted display: 2026-03-07 | Food | Groceries | -$45.00
        return f"{self.date} | {self.category} | {self.description} | {self.trans_type}"

class Account:
    def __init__(self, name, account_type="checking", transactions=None):
        self.name = name
        self.account_type = account_type
        self.transactions = transactions or []

    @property
    def balance(self):
        # sum(t.amount for t in self.transactions)
        # This is a property because balance is derived from data,
        # not stored independently. It's always calculated fresh.
        balance = sum(t.amount for t in self.transactions)
        return balance

    def add_transaction(self, transaction):
        # Append a Transaction object
        self.transactions.append(transaction)

    def get_transactions_by_category(self, category):
        # Filter and return
        return [t for t in self.transactions if t.category == category]

    def get_transactions_in_range(self, start_date, end_date):
        # Filter by date range — useful for CSV export
        return [t for t in self.transactions if start_date <= t.date <= end_date]
        
    def get_transactions(self, start_date=None, end_date=None):
        # Get all transactions with optional date filtering
        if start_date and end_date:
            return [t for t in self.transactions if start_date <= t.date <= end_date]
        elif start_date:
            return [t for t in self.transactions if t.date >= start_date]
        elif end_date:
            return [t for t in self.transactions if t.date <= end_date]
        else:
            return self.transactions

# ──────────────────────────────────────
# DATA LAYER — persistence and import/export
# ──────────────────────────────────────
class FinanceData:
    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.accounts = self._load()

    def _load(self):
        # Read JSON, reconstruct Account and Transaction objects
        # Return dict: {"Checking": Account(...), "Savings": Account(...)}
        try:
            if not os.path.exists(self.filepath):
                return {}
                
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                accounts = {}
                for account_name, account_data in data.items():
                    # Reconstruct transactions from dict
                    transactions = []
                    for trans_dict in account_data['transactions']:
                        transaction = Transaction(
                            trans_dict['amount'],
                            trans_dict['category'],
                            trans_dict['description'],
                            trans_dict['date'],
                            trans_dict['trans_type']
                        )
                        transactions.append(transaction)
                    
                    accounts[account_name] = Account(
                        account_name, 
                        account_data['type'], 
                        transactions
                    )
            return accounts
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in data file")
            return {}
        except Exception as e:
            print(f"Error loading finance data: {e}")
            return {}

    def save(self):
        # Convert all accounts and transactions to dicts, write JSON
        try:
            data = {}
            for account_name, account in self.accounts.items():
                data[account_name] = {
                    "type": account.account_type,
                    "transactions": [t.to_dict() for t in account.transactions]
                }
            
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving finance data: {e}")
            return
                        
    def import_csv(self, filepath, account_name):
        # Read CSV with DictReader
        # Create Transaction objects from each row
        # Add to specified account
        # Save
        try:
            if account_name not in self.accounts:
                self.accounts[account_name] = Account(account_name)
                
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Handle different CSV formats - adjust column names as needed
                    amount = float(row.get('Amount', row.get('amount', 0)))
                    category = row.get('Category', row.get('category', 'Uncategorized'))
                    description = row.get('Description', row.get('description', ''))
                    date = row.get('Date', row.get('date', datetime.now().strftime("%Y-%m-%d")))
                    trans_type = row.get('Type', row.get('type', 'expense'))
                    
                    transaction = Transaction(amount, category, description, date, trans_type)
                    self.accounts[account_name].add_transaction(transaction)
            self.save()
        except FileNotFoundError:
            print("Error importing CSV: File not found")
            return
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return

    def export_csv(self, filepath, account_name, start_date=None, end_date=None):
        # Get transactions from account (optionally filtered by date)
        # Write with DictWriter
        # Include headers: Date, Category, Description, Amount, Type
        try:
            if account_name not in self.accounts:
                print(f"Account '{account_name}' not found")
                return
                
            transactions = self.accounts[account_name].get_transactions(start_date, end_date)
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Date', 'Category', 'Description', 'Amount', 'Type'])
                writer.writeheader()
                for transaction in transactions:
                    writer.writerow({
                        'Date': transaction.date,
                        'Category': transaction.category,
                        'Description': transaction.description,
                        'Amount': transaction.amount,
                        'Type': transaction.trans_type
                    })
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return

# ──────────────────────────────────────
# BUSINESS LOGIC — analysis and rules
# ──────────────────────────────────────
class FinanceManager:
    def __init__(self, data: FinanceData):
        self.data = data

    @property
    def accounts(self):
        return self.data.accounts

    @property
    def net_worth(self):
        # Sum of all account balances
        # Return float
        total = sum(account.balance for account in self.data.accounts.values())
        return total

    def create_account(self, name, account_type):
        # Create new Account, add to data, save
        self.data.accounts[name] = Account(name, account_type)
        self.data.save()

    def add_transaction(self, account_name, amount, category, description, trans_type="expense"):
        # Validate account exists
        # Create Transaction, add to account, save
        if account_name not in self.data.accounts:
            print("Error adding transaction: Account not found")
            return
        else:
            transaction = Transaction(amount, category, description, trans_type=trans_type)
            self.data.accounts[account_name].add_transaction(transaction)
        self.data.save()

    def get_spending_by_category(self, account_name=None):
        # If account_name provided, summarize that account
        # If None, summarize across all accounts
        # Return dict: {category: total}
        # Use defaultdict(float)
        summary = defaultdict(float)
        
        if account_name:
            # Summarize single account
            for transaction in self.data.accounts[account_name].transactions:
                if transaction.trans_type == "expense":
                    summary[transaction.category] += transaction.amount
        else:
            # Summarize all accounts
            for account in self.data.accounts.values():
                for transaction in account.transactions:
                    if transaction.trans_type == "expense":
                        summary[transaction.category] += transaction.amount
                        
        return dict(summary)  # Return regular dict instead of defaultdict

    def get_monthly_summary(self, account_name):
        # Group transactions by month
        # Return dict: {"2026-03": {"income": x, "expenses": y, "net": z}}
        if account_name not in self.data.accounts:
            raise ValueError(f"Account '{account_name}' not found")
            
        summary = defaultdict(lambda: {"income": 0, "expenses": 0, "net": 0})
        for transaction in self.data.accounts[account_name].transactions:
            month = transaction.date[:7]  # YYYY-MM format
            if transaction.amount > 0:
                summary[month]["income"] += transaction.amount
            else:
                summary[month]["expenses"] += abs(transaction.amount)
                
        # Calculate net for each month
        for month in summary:
            summary[month]["net"] = summary[month]["income"] - summary[month]["expenses"]
            
        return dict(summary)

    def transfer_between_accounts(self, from_account, to_account, amount, description="Transfer"):
        # Handle transfers between accounts
        if from_account not in self.data.accounts or to_account not in self.data.accounts:
            print("Error: One or both accounts not found")
            return False
            
        if self.data.accounts[from_account].balance < amount:
            print("Error: Insufficient funds for transfer")
            return False
            
        # Create expense in from account
        expense = Transaction(-amount, "Transfer", description, trans_type="transfer")
        self.data.accounts[from_account].add_transaction(expense)
        
        # Create income in to account  
        income = Transaction(amount, "Transfer", description, trans_type="transfer")
        self.data.accounts[to_account].add_transaction(income)
        
        self.data.save()
        return True

# ──────────────────────────────────────
# PRESENTATION — user interface
# ──────────────────────────────────────
class FinanceApp:
    def __init__(self):
        self.data = FinanceData()
        self.manager = FinanceManager(self.data)

    def run(self):
        # Main menu loop
        while True:
            print("\nPersonal Finance Manager")
            print("1. Show Accounts Overview")
            print("2. Show Category Breakdown")
            print("3. Add Transaction")
            print("4. Import CSV")
            print("5. Export CSV")
            print("6. Transfer Between Accounts")
            print("7. Exit")
            choice = input("Enter your choice: ")
            if choice == "1":
                self.show_accounts_overview()
            elif choice == "2":
                self.show_category_breakdown()
            elif choice == "3":    
                self.add_transaction_prompt()
            elif choice == "4":
                self.import_csv_prompt()
            elif choice == "5":
                self.export_csv_prompt()
            elif choice == "6":
                self.transfer_prompt()
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please try again.")
                print()

    def show_accounts_overview(self):
        # Display all accounts with balances and net worth
        # Use formatted table output with alignment
        # Header
        print(f"\n{'Account':<15} {'Balance':>10}")
        print("-" * 45)
        # Rows
        for account in self.manager.accounts.values():
            print(f"{account.name:<15} ${account.balance:,.2f}")
        # Footer
        print(f"{'Net Worth':<15} {'':>10} ${self.manager.net_worth:,.2f}")

    def show_category_breakdown(self):
        # Get spending by category from manager
        # Display as formatted table
        # Header
        print(f"\n{'Category':<15} {'Spending':>10}")
        print("-" * 45)
        # Rows
        spending = self.manager.get_spending_by_category()
        for category, amount in spending.items():
            print(f"{category:<15} ${amount:<10,.2f}")
        # Footer
        total = sum(spending.values())
        print(f"{'Total Spending':<15} {'':>10} ${total:,.2f}")

    def add_transaction_prompt(self):
        # Get account, amount, category, description from user
        # Pass to manager
        # Confirm with user
        # Handle errors
        # Return success/failure message
        try:
            account_name = input("Enter account name: ")
            amount = float(input("Enter amount: "))
            category = input("Enter category: ")
            description = input("Enter description: ")
            trans_type = input("Enter type (expense/income/transfer) or press Enter for expense: ").lower()
            if not trans_type:
                trans_type = "expense"
            elif trans_type not in ["expense", "income", "transfer"]:
                trans_type = "expense"
                
            self.manager.add_transaction(account_name, amount, category, description, trans_type)
            return "Transaction added successfully!"
        except ValueError:
            return "Invalid amount. Please enter a number."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def import_csv_prompt(self):
        # Get file path and account name
        # Call data.import_csv
        try:
            file_path = input("Enter file path: ")
            account_name = input("Enter account name: ")
            self.data.import_csv(file_path, account_name)
            return "CSV imported successfully!"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def export_csv_prompt(self):
        # Get file path, account, optional date range
        # Call data.export_csv
        try:
            file_path = input("Enter file path: ")
            account_name = input("Enter account name: ")
            start_date = input("Enter start date (YYYY-MM-DD) or leave blank: ")
            end_date = input("Enter end date (YYYY-MM-DD) or leave blank: ")
            
            # Handle empty dates
            if not start_date:
                start_date = None
            if not end_date:
                end_date = None
                
            self.data.export_csv(file_path, account_name, start_date, end_date)
            return "CSV exported successfully!"
        except Exception as e:
            return f"An error occurred: {str(e)}"
            
    def transfer_prompt(self):
        # Handle transfers between accounts
        try:
            from_account = input("Enter source account name: ")
            to_account = input("Enter destination account name: ")
            amount = float(input("Enter transfer amount: "))
            description = input("Enter description (optional): ") or "Transfer"
            
            success = self.manager.transfer_between_accounts(from_account, to_account, amount, description)
            if success:
                return "Transfer completed successfully!"
            else:
                return "Transfer failed!"
        except ValueError:
            return "Invalid amount. Please enter a number."
        except Exception as e:
            return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    app = FinanceApp()
    app.run()