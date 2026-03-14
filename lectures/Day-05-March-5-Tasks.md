# DAY 5 — Thursday, March 5, 2026
## Classes & Object-Oriented Programming

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI explains and reviews  
**Commute**: CS50 Week 1 Part 2  
**Evening Session**: 7:00–9:00 PM (2 hours) — Build 2 projects

---

## COMMUTE: CS50 Week 1 Part 2

Finishing Week 1 of CS50. Pay attention to how Malan talks about types and data representation — tonight you'll create your own types using Python classes. Available on YouTube (search "CS50 2024 Week 1") or at https://cs50.harvard.edu/x/

---

## EVENING SESSION (7:00–9:00 PM)

Tonight is a big conceptual leap. Everything you've built so far used standalone variables, lists, and dictionaries. Tonight you learn to bundle data and behavior together into **classes** — Python's way of creating your own custom types. This is the foundation of object-oriented programming (OOP).

**Why this matters**: When you start reviewing AI-generated code in Week 3, most of it will use classes. You need to understand what `class`, `__init__`, and `self` mean to evaluate whether AI's class design makes sense.

---

### Project 9: `expense_tracker.py` (~55 min)

**What to build**: A program that tracks expenses. The user can add an expense (amount, category, description, date), view all expenses, view expenses filtered by category, and see a spending summary by category. All data persists to a JSON file between runs.

**Concepts to learn and use**:
- **`class` keyword** — defining your own type. An `Expense` class bundles amount, category, description, and date into one object instead of loose variables or a plain dictionary.
- **`__init__` method** — the constructor. Runs automatically when you create a new object: `expense = Expense(25.50, "Food", "Lunch")`. This is where you set the object's initial data.
- **`self`** — refers to the current object instance. Every method in a class takes `self` as its first parameter. Inside `__init__`, `self.amount = amount` stores the amount on that specific expense object.
- **`__str__` method** — controls what happens when you `print()` an object. Without it, you get something ugly like `<Expense object at 0x...>`. With it, you get a nice formatted string.
- **Methods** — functions that belong to a class. An `ExpenseTracker` class might have `add_expense()`, `get_by_category()`, `get_summary()`.
- **`datetime` module** — `datetime.now().strftime("%Y-%m-%d")` gives you today's date as a string.
- **JSON serialization** — you can't directly save a class to JSON. You'll need a `to_dict()` method that converts an Expense to a dictionary, and a `from_dict()` class method (or just build from the dict in `load`).

**Reference material**:
- Python docs — classes: https://docs.python.org/3/tutorial/classes.html
- Python docs — `__init__` and `__str__`: https://docs.python.org/3/reference/datamodel.html#basic-customization
- Python docs — `datetime`: https://docs.python.org/3/library/datetime.html
- Real Python — OOP in Python: https://realpython.com/python3-object-oriented-programming/

**Design questions to answer before you code**:
1. What data does an `Expense` hold? At minimum: amount (float), category (str), description (str), date (str). Should the date default to today if not provided?
2. Should you have two classes or one? Recommended: an `Expense` class (represents one expense) and an `ExpenseTracker` class (manages the list of expenses, handles saving/loading). This separation is a pattern you'll see constantly in professional code.
3. How do you save classes to JSON? Classes can't be directly serialized. Add a `to_dict()` method on `Expense` that returns `{"amount": self.amount, "category": self.category, ...}`. When loading, create `Expense` objects from the dictionaries.
4. What categories should exist? Let the user type any category, but suggest common ones: Food, Transport, Entertainment, Bills, Shopping, Other.
5. What does the spending summary look like? Group expenses by category, show total per category, and show overall total.

**Ask GLM-4.7-Flash before coding**: `Cmd+L` → "Explain Python classes for a beginner. Cover: the `class` keyword, `__init__`, `self`, `__str__`, and regular methods. Explain the difference between a class (the blueprint) and an instance (the actual object). Use a simple example like a `Dog` class, not my program."

**Write your code.** Structure it like this:
```
import json
from datetime import datetime

EXPENSES_FILE = "expenses.json"

class Expense:
    def __init__(self, amount, category, description, date=None):
        # store attributes with self.xxx = xxx
        # default date to today if not provided

    def to_dict(self):
        # return a dictionary representation

    def __str__(self):
        # return a nice formatted string

class ExpenseTracker:
    def __init__(self):
        self.expenses = self.load_expenses()

    def load_expenses(self):
        # read JSON, create Expense objects from dicts

    def save_expenses(self):
        # convert expenses to dicts, write JSON

    def add_expense(self):
        # get input from user, create Expense, append, save

    def view_expenses(self, category=None):
        # show all, or filter by category

    def get_summary(self):
        # group by category, show totals

def main():
    tracker = ExpenseTracker()
    while True:
        # menu: add, view all, view by category, summary, quit
        # call tracker methods based on choice

main()
```

**Ask GLM-4.7-Flash after coding**: Select all code → `Cmd+L` → "Review this expense tracker. Is my class design clean? Am I using `__init__`, `self`, and `__str__` correctly? Is my JSON serialization approach (to_dict) the right pattern? What would a senior developer change?"

**Commit when done**: `git add . && git commit -m "Project 9: expense_tracker.py — classes, __init__, self, __str__, OOP basics"`

---

### Project 10: `quiz_game.py` (~55 min)

**What to build**: A quiz game that loads questions from a JSON file. Each question has the question text, multiple choice options, and the correct answer. The program presents questions one at a time, tracks the user's score, and shows results at the end. The user should be able to create their own quiz files.

**Concepts to learn and use**:
- **Multiple classes working together** — a `Question` class (one question) and a `Quiz` class (manages the game). This reinforces the "one class per concept" pattern from the expense tracker.
- **Loading structured data from JSON** — the JSON file has a specific schema that your code expects. This is a real-world pattern: APIs return JSON, config files are JSON, data interchange is JSON.
- **`enumerate()`** — `for i, option in enumerate(options, 1)` gives you both the index and the value. Perfect for numbered multiple choice lists.
- **Class methods that interact** — `Quiz.ask_question()` calls methods on `Question` objects. Objects talking to each other is the core of OOP.
- **`random.shuffle()`** — optionally shuffle question order for variety.
- **f-strings with formatting** — display score as percentage: `f"{score}/{total} ({score/total*100:.0f}%)"`

**Reference material**:
- Python docs — `enumerate()`: https://docs.python.org/3/library/functions.html#enumerate
- Python docs — `random.shuffle()`: https://docs.python.org/3/library/random.html#random.shuffle
- Real Python — reading JSON files: https://realpython.com/python-json/
- Real Python — enumerate: https://realpython.com/python-enumerate/

**First: Create a quiz data file**

Before writing the program, create `python_quiz.json` by hand:
```json
{
    "title": "Python Basics Quiz",
    "questions": [
        {
            "question": "What keyword defines a function in Python?",
            "options": ["func", "def", "function", "define"],
            "answer": "def"
        },
        {
            "question": "Which method adds an item to the end of a list?",
            "options": ["add()", "insert()", "append()", "push()"],
            "answer": "append()"
        },
        {
            "question": "What does 'self' refer to in a class method?",
            "options": ["The class itself", "The current instance", "The parent class", "Nothing"],
            "answer": "The current instance"
        },
        {
            "question": "How do you open a file for reading in Python?",
            "options": ["open('file', 'w')", "open('file', 'r')", "read('file')", "file.open()"],
            "answer": "open('file', 'r')"
        },
        {
            "question": "What module is used for working with JSON in Python?",
            "options": ["data", "json", "serialize", "parse"],
            "answer": "json"
        }
    ]
}
```

Writing this quiz file by hand reinforces yesterday's JSON concepts — and notice the questions are about things you've learned this week.

**Design questions to answer before you code**:
1. What does a `Question` object hold? The question text, list of options, and the correct answer. It should have a method to display itself and a method to check if a given answer is correct.
2. What does a `Quiz` object do? Loads questions from a JSON file, presents them one by one, tracks score, and shows results. Consider: `load_questions()`, `run()`, `show_results()`.
3. How does the user answer? By typing the number of their choice (1, 2, 3, 4) — not the full answer text. Use `enumerate()` to display numbered options.
4. What happens with invalid input? If the user types "abc" or "5" for a 4-option question, prompt them again. Reuse the `try`/`except` and validation patterns you know.
5. Optional: Should questions be shuffled? Should options within each question be shuffled? Both add replay value. `random.shuffle()` on the list.

**Ask GLM-4.7-Flash before coding**: `Cmd+L` → "Explain `enumerate()` in Python. How does it work, what does the second argument do (start value), and when would you use it instead of a regular `for` loop? Give a quick example with a list of items, not my program."

**Write your code.** Structure it like this:
```
import json
import random

class Question:
    def __init__(self, question, options, answer):
        # store attributes

    def display(self, number):
        # print the question number, question text, and numbered options

    def check_answer(self, user_choice):
        # compare user's selected option to correct answer
        # return True/False

class Quiz:
    def __init__(self, filepath):
        self.questions = self.load_questions(filepath)
        self.score = 0

    def load_questions(self, filepath):
        # read JSON, create list of Question objects

    def run(self):
        # shuffle questions (optional)
        # loop through questions with enumerate
        # display each, get user answer, check, update score

    def show_results(self):
        # display final score with percentage
        # maybe show which questions were missed

def main():
    quiz = Quiz("python_quiz.json")
    quiz.run()
    quiz.show_results()

main()
```

**Ask GLM-4.7-Flash after coding**: Select all code → `Cmd+L` → "Review this quiz game. Are my two classes well-designed? Is the separation between Question and Quiz appropriate? Am I using enumerate correctly? What would make this more robust?"

**Commit when done**: `git add . && git commit -m "Project 10: quiz_game.py — multiple classes, enumerate, JSON data loading"`

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 5
- [ ] Day number: 5
- [ ] Hours coded: 2
- [ ] Projects completed: 2 (expense_tracker, quiz_game)
- [ ] Key concepts: class, __init__, self, __str__, to_dict, enumerate(), multiple classes working together
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 6 — Friday):
- **Commute**: Talk Python To Me episode (project structure)
- **Evening (7:00–9:00 PM)**: Projects 11–12
  - `password_generator.py` — Secure password generator (string module, argparse for CLI arguments)
  - `todo_manager.py` — Full-featured todo list with priorities, due dates, save/load (JSON, classes, CLI)
- **New concepts**: `argparse` (command-line arguments), more advanced class design, combining everything from the week
- **Also**: Kick off background downloads for qwen3.5:27b and llama.cpp

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

Building on Days 1–4, you should now also be able to explain:

1. What a class is and why you'd use one instead of plain dictionaries
2. What `__init__` does and when it runs (automatically when you create an object)
3. What `self` means and why every method needs it as the first parameter
4. What `__str__` does and how `print(my_object)` uses it
5. How to convert a class instance to a dictionary for JSON serialization (`to_dict()` pattern)
6. How `enumerate()` works and when to use it instead of `range(len(...))`
7. How two classes can work together (Question objects inside a Quiz)
8. The difference between a class (blueprint) and an instance (actual object)

**The mental model shift**: Before tonight, your programs had data (variables, lists, dicts) and functions that operated on that data separately. After tonight, you can bundle data and behavior together in objects. This is how most professional Python code is organized, and it's what you'll see constantly when reviewing AI-generated code starting Week 3.

---

**Day 5 of 365. Classes unlock everything that comes next.** 🚀
