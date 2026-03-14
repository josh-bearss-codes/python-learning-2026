# DAY 7 — Saturday, March 7, 2026
## Lecture: Building Layered Applications

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI explains and reviews  
**Morning Session**: 8:00–11:00 AM (3 hours) — Build 2 projects  
**Today's theme**: Software architecture — why how you organize code matters more than what code you write

---

## OPENING LECTURE: WHY ARCHITECTURE MATTERS

Over the past six days, you've written 12 projects. Each one was a single file with functions and classes solving a problem. That approach works for small tools. It stops working the moment your program needs to do three things at once: store data, apply business rules to that data, and display results to a user.

Today we're going to talk about **separation of concerns** — one of the most important ideas in software engineering. Here's the core principle:

> Every piece of your code should have exactly one reason to change.

Think about what that means practically. If you have a function that reads data from a JSON file, calculates spending summaries, AND prints a formatted report — that function has three reasons to change. If you switch from JSON to CSV storage, you rewrite it. If the business rules change (say, you want to track tax categories), you rewrite it. If you want a different display format, you rewrite it again. One function, three unrelated reasons to break.

**The solution is layers.** Professional software is organized into layers where each layer handles one responsibility:

```
┌─────────────────────────────────────┐
│         PRESENTATION LAYER          │  ← How data is displayed to the user
│   (menus, formatting, user input)   │     Changes when: UI requirements change
├─────────────────────────────────────┤
│          BUSINESS LOGIC             │  ← Rules, calculations, decisions
│  (budgets, alerts, summaries)       │     Changes when: business rules change
├─────────────────────────────────────┤
│            DATA LAYER               │  ← How data is stored and retrieved
│    (JSON, CSV, database files)      │     Changes when: storage format changes
└─────────────────────────────────────┘
```

**Why should you care about this on Day 7 of learning Python?** Two reasons:

1. **This is what AI-generated code gets wrong.** When you start directing AI in Week 3, it will happily generate a single monolithic function that mixes storage, logic, and display. Your job as the architect is to specify the layers. If you don't understand layered design, you can't write good specs, and AI produces unmaintainable code.

2. **This is what clients pay for.** Nobody pays $150/hour for someone who can write a function. They pay for someone who designs systems that can change without breaking. Your data engineering background already gives you this instinct — you understand that an ETL pipeline has distinct extract, transform, and load stages. Today we apply the same thinking to application code.

Today's two projects build the same domain (personal finance) at two levels of complexity. Project 13 is a focused budget tracker with clear layers. Project 14 scales it up into a multi-account system that adds CSV import/export and proves that layered architecture makes scaling possible without rewriting everything.

Let's build.

---

## PROJECT 13: `budget_tracker.py` (~1 hour 15 min)

### The Concept

A budget tracker answers one question: **"Am I spending within my limits?"** The user sets a monthly budget for categories (Food: $600, Transport: $200, Entertainment: $150), logs expenses throughout the month, and the system tells them where they stand — including warnings when they're approaching or exceeding a budget.

This is a direct evolution of Day 5's expense tracker, but with a critical addition: **budget limits and alerts**. This means your code needs to know two things — what was spent AND what was allowed — and compare them. That comparison is a business rule, which should live in the business logic layer, not mixed into the display code or the storage code.

### The Architecture

Before writing a single line of code, understand the layers:

**Data Layer** — responsible for persistence:
- `BudgetData` class — loads and saves all data to a JSON file
- Knows nothing about budget rules or display formatting
- If you wanted to switch from JSON to SQLite tomorrow, you'd only change this class

**Business Logic Layer** — responsible for rules and calculations:
- `BudgetManager` class — sets budgets, adds expenses, calculates summaries, generates alerts
- Knows nothing about how data is stored or how results are displayed
- Contains the "intelligence": What percentage of budget is used? Is the user over budget? What's the daily spending rate?

**Presentation Layer** — responsible for user interaction:
- `BudgetApp` class (or a set of functions) — menus, formatted output, user prompts
- Knows nothing about storage format or budget calculation rules
- If you wanted to add a web interface later, you'd only change this layer

**Why three separate pieces instead of one big class?** Imagine a client asks you to add email alerts when spending exceeds 80% of budget. Where does that code go? In the layered design, the answer is clear: the business logic layer detects the threshold, and a new notification layer sends the email. In a monolithic design, you'd be hunting through hundreds of lines trying to figure out where to add it without breaking the display code.

### Concepts to Learn and Use

- **Layered architecture** — separating data, logic, and presentation into distinct classes
- **`datetime` module deeper** — `datetime.now().month`, `datetime.now().year` for filtering expenses to the current month
- **Dictionary comprehension** — `{cat: total for cat, total in ...}` for building summary dictionaries
- **Percentage calculations and thresholds** — business logic that compares actual vs. budgeted amounts
- **Conditional formatting** — displaying different warnings based on spending thresholds (under 50%, 50-80%, 80-100%, over 100%)
- **`defaultdict` from `collections`** — automatically creates missing keys: `spending = defaultdict(float)` means `spending["Food"] += 25.00` works even if "Food" hasn't been seen before

### Reference Material

- Python docs — `collections.defaultdict`: https://docs.python.org/3/library/collections.html#collections.defaultdict
- Python docs — `datetime`: https://docs.python.org/3/library/datetime.html
- Python docs — dictionary comprehension: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
- Real Python — defaultdict: https://realpython.com/python-defaultdict/

### Design Questions (Answer These BEFORE You Code)

These aren't optional warm-up questions — they're the architectural decisions that determine whether your code is clean or messy. Professional developers spend more time on design than on typing. Work through each one.

1. **What does the JSON file structure look like?** You need to store two kinds of data: budgets (category → monthly limit) and expenses (list of expense records). Sketch this out on paper or in a comment:
   ```json
   {
       "budgets": {"Food": 600, "Transport": 200, "Entertainment": 150},
       "expenses": [
           {"amount": 25.50, "category": "Food", "description": "Lunch", "date": "2026-03-07"}
       ]
   }
   ```
   Notice how the data structure stores raw facts — no calculations, no formatting. That's the data layer's job: store and retrieve, nothing else.

2. **What business rules exist?** List them explicitly:
   - Spending percentage = total spent in category / budget for category × 100
   - Alert levels: Green (under 50%), Yellow (50–80%), Orange (80–100%), Red (over 100%)
   - Daily budget remaining = (budget − spent) / days remaining in month
   - An expense in a category with no budget should still be tracked (uncategorized spending is still spending)

3. **What does `BudgetData` need to do?** Only four things: load data from file, save data to file, provide access to budgets, provide access to expenses. It should not calculate summaries or format output.

4. **What does `BudgetManager` need to do?** Set/update budget for a category. Add an expense. Get total spending by category for current month. Get spending percentage by category. Generate alerts for categories over threshold. Calculate daily budget remaining.

5. **What does the presentation layer need to do?** Show a menu. Display a budget summary table with color-coded status. Display recent expenses. Get input for new expenses and budgets. Format currency output.

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain Python's `collections.defaultdict`. How does it differ from a regular dictionary? When would you use `defaultdict(float)` vs `defaultdict(list)`? Also explain dictionary comprehensions — how do they work and when are they useful? Concept explanation only, don't write my program."

### Write Your Code

Build it layer by layer, bottom up. This is the professional approach: data layer first (because everything depends on it), business logic second (because it depends on data), presentation last (because it depends on everything).

```python
import json
from datetime import datetime
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

    def save(self):
        # Write self.data to JSON file

    @property
    def budgets(self):
        # Return the budgets dictionary

    @property
    def expenses(self):
        # Return the expenses list


# ──────────────────────────────────────
# BUSINESS LOGIC — rules and calculations
# ──────────────────────────────────────
class BudgetManager:
    def __init__(self, data: BudgetData):
        self.data = data

    def set_budget(self, category, amount):
        # Add or update a budget category

    def add_expense(self, amount, category, description):
        # Create expense record with today's date, append, save

    def get_monthly_spending(self):
        # Filter expenses to current month
        # Return dict: {category: total_spent}
        # Use defaultdict(float) for accumulation

    def get_budget_status(self):
        # For each budgeted category, return:
        # {category: {"budget": x, "spent": y, "percent": z, "alert": "green/yellow/orange/red"}}

    def get_daily_remaining(self, category):
        # (budget - spent) / days remaining in month


# ──────────────────────────────────────
# PRESENTATION — user interaction and display
# ──────────────────────────────────────
class BudgetApp:
    def __init__(self):
        self.data = BudgetData()
        self.manager = BudgetManager(self.data)

    def run(self):
        # Main menu loop

    def show_budget_summary(self):
        # Get status from manager, format and display
        # Use alert levels to show status indicators

    def add_expense_prompt(self):
        # Get input, validate, pass to manager

    def set_budget_prompt(self):
        # Get category and amount, pass to manager


if __name__ == "__main__":
    app = BudgetApp()
    app.run()
```

**The key insight**: Notice how `BudgetApp` creates a `BudgetData` and passes it to `BudgetManager`. The app layer depends on the logic layer, which depends on the data layer. Data flows upward. No layer reaches down past its immediate neighbor. This is called **dependency injection** — the app "injects" the data object into the manager rather than letting the manager create its own. This pattern makes testing and modification dramatically easier.

**A note on `@property`**: You may not have seen this decorator yet. `@property` lets you access a method like an attribute: `self.data.budgets` instead of `self.data.budgets()`. Ask Qwen3-Coder to explain it if it's unfamiliar — it's a small but useful Python feature.

### Ask GLM-4.7-Flash After Coding

Select all code → `Cmd+L` → "Review this budget tracker's architecture. Are my three layers (data, logic, presentation) properly separated? Does any layer reach into another layer's responsibilities? Is my use of defaultdict and datetime correct? If I wanted to switch from JSON to SQLite storage, how much code would I need to change? What would a senior developer refactor?"

### Commit

```bash
git add . && git commit -m "Project 13: budget_tracker.py — layered architecture, defaultdict, business logic separation"
```

---

## BREAK (10 minutes)

Stand up. Walk around. Get water. Your brain needs a few minutes to consolidate what you just built before moving to the next level.

---

## PROJECT 14: `personal_finance.py` (~1 hour 30 min)

### The Concept

The budget tracker handles one month, one account. Real personal finance involves multiple accounts (checking, savings, credit card), transactions flowing between them, and the need to import/export data from external sources (like a CSV from your bank).

This project takes the layered architecture from Project 13 and scales it. The data layer gets more complex (multiple accounts, transactions instead of simple expenses). The business logic gets richer (account balances, transfer tracking, category analysis across accounts). And you add a new capability: **CSV import/export** — your first time reading and writing CSV files, and a direct connection to your data engineering background.

### Why CSV Matters

CSV (Comma-Separated Values) is the most universal data interchange format. Every bank, every spreadsheet, every data system can export CSV. When you build AI data pipelines for clients later in this plan, CSV will be the format you encounter most often for initial data ingestion. Python's `csv` module handles it natively.

The important lesson here is that CSV is a **data layer concern**. Your business logic shouldn't know or care whether data came from a JSON file, a CSV import, or a database query. It receives transaction objects and operates on them. This is the layered architecture principle in action — the data layer translates between external formats and your internal data model.

### Concepts to Learn and Use

- **`csv` module** — `csv.DictReader` reads CSV rows as dictionaries (column headers become keys). `csv.DictWriter` writes dictionaries as CSV rows. This is more readable and less error-prone than the basic `csv.reader`.
- **Multiple related classes** — `Account`, `Transaction`, `FinanceManager`, `FinanceApp`. Each models a distinct concept in the domain.
- **Cross-object relationships** — a Transaction belongs to an Account. An Account contains many Transactions. Modeling these relationships cleanly is a core OOP skill.
- **`sum()` with generator expressions** — `sum(t.amount for t in transactions if t.category == "Food")` is a powerful one-liner for aggregation. Understand how this combines `sum()`, a generator, and a filter.
- **String formatting for tables** — `f"{'Category':<15} {'Amount':>10}"` uses alignment specifiers: `<` for left-align, `>` for right-align, with a width number. This produces clean columnar output.
- **`os.path.exists()`** — check if a file exists before trying to read it

### Reference Material

- Python docs — `csv` module: https://docs.python.org/3/library/csv.html
- Python docs — `csv.DictReader`: https://docs.python.org/3/library/csv.html#csv.DictReader
- Python docs — format spec mini-language (alignment): https://docs.python.org/3/library/string.html#format-specification-mini-language
- Real Python — reading and writing CSV: https://realpython.com/python-csv/

### Design Questions (Answer These BEFORE You Code)

1. **What is the data model?** You need two core entities:
   - `Account` — has a name (e.g., "Checking"), a type ("checking"/"savings"/"credit"), and a list of transactions
   - `Transaction` — has an amount, category, description, date, and a type ("expense"/"income"/"transfer")
   
   Think about how these relate: an Account *has* Transactions. A Transaction *belongs to* an Account. This "has-a" relationship is modeled by storing a list of Transaction objects inside each Account.

2. **How does the JSON storage work with multiple accounts?** Sketch the structure:
   ```json
   {
       "accounts": {
           "Checking": {
               "type": "checking",
               "transactions": [
                   {"amount": -45.00, "category": "Food", "description": "Groceries", "date": "2026-03-07", "type": "expense"}
               ]
           },
           "Savings": {
               "type": "savings",
               "transactions": []
           }
       }
   }
   ```
   Notice: expenses are negative amounts, income is positive. This is how real accounting works — it makes balance calculations simple: `balance = sum of all transaction amounts`.

3. **What does CSV import look like?** A bank CSV might have columns: `Date, Description, Amount, Category`. Your importer reads each row, creates a Transaction, and adds it to the specified account. The key design decision: the CSV reader (data layer) creates Transaction objects. The business logic layer doesn't know about CSV at all.

4. **What does CSV export look like?** The user selects an account, specifies a date range, and the system writes matching transactions to a CSV file. Again — the business logic layer gathers the transactions, the data layer writes the file format.

5. **What calculations does the business logic handle?**
   - Account balance (sum of all transaction amounts)
   - Category spending summary across one or all accounts
   - Monthly spending trend (total spent per month)
   - Net worth (sum of all account balances)

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain Python's csv module — specifically csv.DictReader and csv.DictWriter. How do they differ from the basic csv.reader and csv.writer? Show how DictReader maps CSV columns to dictionary keys. Also explain how to use sum() with a generator expression to total up specific values from a list of objects. Concepts only, don't write my program."

### Write Your Code

Same approach — build bottom up, layer by layer.

```python
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

    def __str__(self):
        # Formatted display: 2026-03-07 | Food | Groceries | -$45.00

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

    def add_transaction(self, transaction):
        # Append a Transaction object

    def get_transactions_by_category(self, category):
        # Filter and return

    def get_transactions_in_range(self, start_date, end_date):
        # Filter by date range — useful for CSV export


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

    def save(self):
        # Convert all accounts and transactions to dicts, write JSON

    def import_csv(self, filepath, account_name):
        # Read CSV with DictReader
        # Create Transaction objects from each row
        # Add to specified account
        # Save

    def export_csv(self, filepath, account_name, start_date=None, end_date=None):
        # Get transactions from account (optionally filtered by date)
        # Write with DictWriter
        # Include headers: Date, Category, Description, Amount, Type


# ──────────────────────────────────────
# BUSINESS LOGIC — analysis and rules
# ──────────────────────────────────────
class FinanceManager:
    def __init__(self, data: FinanceData):
        self.data = data

    def create_account(self, name, account_type):
        # Create new Account, add to data, save

    def add_transaction(self, account_name, amount, category, description, trans_type="expense"):
        # Validate account exists
        # Create Transaction, add to account, save

    def get_net_worth(self):
        # Sum of all account balances

    def get_spending_by_category(self, account_name=None):
        # If account_name provided, summarize that account
        # If None, summarize across all accounts
        # Return dict: {category: total}
        # Use defaultdict(float)

    def get_monthly_summary(self, account_name):
        # Group transactions by month
        # Return dict: {"2026-03": {"income": x, "expenses": y, "net": z}}


# ──────────────────────────────────────
# PRESENTATION — user interface
# ──────────────────────────────────────
class FinanceApp:
    def __init__(self):
        self.data = FinanceData()
        self.manager = FinanceManager(self.data)

    def run(self):
        # Main menu loop

    def show_accounts_overview(self):
        # Display all accounts with balances and net worth
        # Use formatted table output with alignment

    def show_category_breakdown(self):
        # Get spending by category from manager
        # Display as formatted table

    def add_transaction_prompt(self):
        # Get account, amount, category, description from user
        # Pass to manager

    def import_csv_prompt(self):
        # Get file path and account name
        # Call data.import_csv

    def export_csv_prompt(self):
        # Get file path, account, optional date range
        # Call data.export_csv


if __name__ == "__main__":
    app = FinanceApp()
    app.run()
```

### Understanding the Architecture Visually

Take a moment to see how this scales from Project 13:

```
Project 13 (Budget Tracker):          Project 14 (Personal Finance):
┌──────────────┐                      ┌──────────────┐
│  BudgetApp   │                      │  FinanceApp  │
└──────┬───────┘                      └──────┬───────┘
       │                                     │
┌──────┴───────┐                      ┌──────┴───────┐
│BudgetManager │                      │FinanceManager│
└──────┬───────┘                      └──────┬───────┘
       │                                     │
┌──────┴───────┐                      ┌──────┴───────┐
│  BudgetData  │                      │ FinanceData  │
│  (JSON)      │                      │ (JSON+CSV)   │
└──────────────┘                      └──────┬───────┘
                                             │
                                      ┌──────┴───────┐
                                      │Account       │
                                      │ └Transaction │
                                      └──────────────┘
```

The shape is the same. The layers are the same. But the data model is richer, the business logic is more complex, and the data layer gained CSV capability. That's what good architecture gives you — you can scale complexity without changing the fundamental structure.

### Create a Test CSV File

Before you code the CSV import, create a sample file to test with. Save this as `test_transactions.csv`:

```csv
Date,Description,Amount,Category,Type
2026-03-01,Paycheck,3200.00,Income,income
2026-03-02,Rent,-1200.00,Housing,expense
2026-03-03,Groceries Costco,-185.50,Food,expense
2026-03-04,Gas,-45.00,Transport,expense
2026-03-05,Netflix,-15.99,Entertainment,expense
2026-03-06,Side project payment,500.00,Income,income
2026-03-07,Protein powder,-42.00,Food,expense
```

Test your CSV import by loading this into a "Checking" account, then verify the balance calculates correctly: 3200 + (-1200) + (-185.50) + (-45) + (-15.99) + 500 + (-42) = **$2,211.51**.

### Formatted Table Output

For the presentation layer, practice alignment formatting. This is how you make terminal output look professional:

```python
# Header
print(f"{'Category':<15} {'Spent':>10} {'Budget':>10} {'Remaining':>10} {'Status':>8}")
print("-" * 58)

# Row
print(f"{'Food':<15} {'$285.50':>10} {'$600.00':>10} {'$314.50':>10} {'  ✓':>8}")
```

The `<15` means left-align in a 15-character wide field. The `>10` means right-align in a 10-character field. Numbers and currency should always be right-aligned — that's a universal formatting convention because it aligns the decimal points.

### Ask GLM-4.7-Flash After Coding

Select all code → `Cmd+L` → "Review this personal finance application's architecture. I'm trying to maintain separation between data layer (FinanceData), business logic (FinanceManager), and presentation (FinanceApp). Does my design achieve this? Is my CSV import/export properly contained in the data layer? Are my Transaction and Account classes well-designed? If I wanted to add a 'transfers between accounts' feature, where would that code go? What would a senior developer change about this architecture?"

### Commit

```bash
git add . && git commit -m "Project 14: personal_finance.py — multi-account architecture, CSV import/export, layered design"
```

---

## CLOSING LECTURE: WHAT YOU LEARNED TODAY

Today was different from the previous six days. On Days 1–6, the primary question was **"How do I make Python do X?"** — how to write a function, how to create a class, how to read a file. Those are syntax and mechanics.

Today the primary question was **"How should I organize code that does X, Y, and Z?"** — how to separate concerns, how to layer responsibilities, how to design for change. That's architecture.

Here's what I want you to internalize:

**1. Layers exist to isolate change.** When (not if) requirements change, layered code limits the blast radius. Change the storage format? Only the data layer changes. Change the business rules? Only the logic layer changes. Change the UI? Only the presentation layer changes. Monolithic code means every change touches everything.

**2. The data layer is a translator.** Its job is to convert between external formats (JSON, CSV, databases) and your internal data model (Python objects). The rest of your application should never know what format data is stored in. This is why `FinanceData` handles both JSON persistence and CSV import/export — both are external format concerns.

**3. Business logic should be testable without I/O.** If your `FinanceManager` doesn't read files or print output, you could theoretically test every calculation by feeding it mock data. You haven't learned testing yet (that's Month 4), but designing for testability now means your code is automatically cleaner.

**4. This pattern scales to every project you'll build.** RAG pipelines in Month 2 have the same layers: data ingestion (data layer), embedding and retrieval (logic layer), and chat interface (presentation layer). Client projects in Month 4+ will have the same shape. Enterprise AI systems in Month 6+ are the same architecture at larger scale. Learn it once, apply it everywhere.

**5. Your data engineering instincts already know this.** In your professional work, you don't mix Kafka ingestion code with Spark transformation code with output sink code. ETL has the same separation: Extract (data layer in), Transform (business logic), Load (data layer out). Today you applied that same thinking to application code.

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 7
- [ ] Day number: 7
- [ ] Hours coded: 3
- [ ] Projects completed: 2 (budget_tracker, personal_finance)
- [ ] Key concepts: layered architecture, separation of concerns, defaultdict, csv.DictReader/DictWriter, @property, formatted table output, dependency injection
- [ ] First 3-hour weekend session — how did the pacing feel? ___
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 8 — Sunday):
- **Morning (8:00–11:00 AM)**: 3 hours
  - `data_pipeline_mini.py` — Mini ETL pipeline: read CSV → validate → transform → output JSON
  - Your data engineering DNA takes over — this project is a miniature version of what you've done professionally
  - **The layered architecture from today becomes even more explicit**: each ETL stage is its own layer
- **Evening (7:00–8:30 PM)**: Week 1 review — reflect on all 15 projects and what you've learned

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

This is a deeper list than previous days because today was architecturally focused:

1. **Separation of concerns** — why every piece of code should have exactly one reason to change
2. **Three-layer architecture** — data layer (persistence), business logic (rules/calculations), presentation (UI)
3. **Dependency injection** — passing dependencies into a class rather than letting it create its own (e.g., passing `BudgetData` into `BudgetManager`)
4. **`collections.defaultdict`** — automatic key initialization, and when to use `defaultdict(float)` vs `defaultdict(list)`
5. **`@property` decorator** — accessing a method as an attribute, useful for derived values like `balance`
6. **`csv.DictReader` and `csv.DictWriter`** — reading/writing CSV as dictionaries mapped to column headers
7. **`sum()` with generator expressions** — `sum(t.amount for t in transactions if condition)` for aggregation
8. **String format alignment** — `f"{'text':<15}"` for left-align, `f"{'text':>10}"` for right-align
9. **The "has-a" relationship** in OOP — an Account has Transactions (composition, not inheritance)
10. **Why this matters for AI-directed development** — your job in Week 3+ is writing the architectural spec. AI fills in the implementation. Without understanding layers, your specs produce monolithic code.

---

**Day 7 of 365. First weekend session. Architecture is the skill that separates junior from senior. You're building that muscle now.** 🚀
