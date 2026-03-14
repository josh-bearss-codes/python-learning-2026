# DAY 6 — Friday, March 6, 2026
## CLI Tools & Comprehensive OOP

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI explains and reviews  
**Commute**: Talk Python To Me podcast  
**Evening Session**: 7:00–9:00 PM (2 hours) — Build 2 projects  
**Background**: Kick off overnight model downloads before bed

---

## COMMUTE: Talk Python To Me

Search for a recent Talk Python To Me episode about project structure, packaging, or best practices. If you can't find one, episode #482 "Project Structure and Packaging" or any episode on CLI tools is a good pick. The podcast is available on Spotify, Apple Podcasts, or https://talkpython.fm/

Focus on how professional Python developers structure their projects — files, folders, naming conventions. You'll start noticing how your own projects are growing beyond single files.

---

## EVENING SESSION (7:00–9:00 PM)

Tonight wraps up your first full week of Python with two projects that combine everything you've learned. Project 11 introduces `argparse` (command-line arguments — how real CLI tools work). Project 12 is your most complex build yet — a full todo manager that pulls together classes, JSON persistence, sorting, filtering, and clean program structure.

**End-of-week energy check**: It's Friday. You've coded every day this week. If you're tired, that's normal — push through these two and you've earned a strong weekend session tomorrow. Consistency matters more than perfection.

---

### Project 11: `password_generator.py` (~45 min)

**What to build**: A command-line tool that generates secure random passwords. The user controls the output through command-line arguments: password length, number of passwords to generate, and whether to include/exclude uppercase, digits, or special characters. Running `python3 password_generator.py --length 16 --count 5 --no-special` should print 5 passwords of 16 characters with no special characters.

**Concepts to learn and use**:
- **`argparse` module** — the standard way to handle command-line arguments in Python. This is how every real CLI tool works (pip, git, pytest all use it under the hood).
- `ArgumentParser()` — creates the parser object
- `add_argument()` — defines each flag/option: name, type, default, help text
- `parser.parse_args()` — parses the command line and returns an object with your arguments as attributes
- **`string` module revisited** — `string.ascii_uppercase`, `string.ascii_lowercase`, `string.digits`, `string.punctuation` give you character pools
- **`random.choice()`** — pick a random character from a string
- **`random.shuffle()`** — shuffle a list in place (to ensure the password isn't predictable in structure)
- **List comprehension** — `[random.choice(pool) for _ in range(length)]` generates a list of random characters
- **`''.join()`** — converts a list of characters into a string

**Reference material**:
- Python docs — argparse tutorial: https://docs.python.org/3/howto/argparse.html
- Python docs — argparse reference: https://docs.python.org/3/library/argparse.html
- Python docs — `string` constants: https://docs.python.org/3/library/string.html
- Real Python — argparse: https://realpython.com/command-line-interfaces-python-argparse/

**Design questions to answer before you code**:
1. What arguments should the tool accept? Suggested:
   - `--length` (int, default 16) — password length
   - `--count` (int, default 1) — how many passwords to generate
   - `--no-upper` (flag) — exclude uppercase letters
   - `--no-digits` (flag) — exclude digits
   - `--no-special` (flag) — exclude special characters
2. How do you build the character pool? Start with lowercase (always included), then conditionally add uppercase, digits, and special characters based on the flags.
3. How do you ensure the password contains at least one of each required type? Generate one character from each required pool first, then fill the rest randomly from the combined pool, then shuffle.
4. What if the user passes `--length 4` but requires all 4 character types? The password can still work — 4 characters, one from each pool. But `--length 2` with 4 types is impossible. Handle that edge case.

**Ask GLM-4.7-Flash before coding**: `Cmd+L` → "Explain Python's argparse module. How do I create an ArgumentParser, add arguments with types and defaults, add boolean flags (store_true), and access the parsed values? Show the pattern with a simple example, not my program."

**Write your code.** Structure it like this:
```
import argparse
import random
import string

def build_char_pool(use_upper, use_digits, use_special):
    # start with lowercase, conditionally add others
    # return the combined string

def generate_password(length, char_pool):
    # generate a random password from the pool
    # ensure at least one char from each included type
    # shuffle and return as string

def main():
    parser = argparse.ArgumentParser(description="Generate secure passwords")
    # add arguments: --length, --count, --no-upper, --no-digits, --no-special
    args = parser.parse_args()

    char_pool = build_char_pool(...)
    for _ in range(args.count):
        print(generate_password(args.length, char_pool))

if __name__ == "__main__":
    main()
```

**Test it from the terminal** (not just by running in VS Code):
```bash
# Default: 1 password, 16 characters, all types
python3 password_generator.py

# 5 passwords, 20 characters each
python3 password_generator.py --length 20 --count 5

# No special characters
python3 password_generator.py --no-special

# Show help
python3 password_generator.py --help
```

**New pattern: `if __name__ == "__main__"`**: This line means "only run `main()` if this file is executed directly." If someone imports your file as a module, `main()` won't run automatically. It's standard practice for any Python script that can also be imported. Ask Qwen3-Coder to explain it if it's unclear.

**Ask GLM-4.7-Flash after coding**: Select all code → `Cmd+L` → "Review this password generator. Is my argparse setup correct? Is the password generation cryptographically reasonable? Am I handling edge cases? What would make this more robust?"

**Commit when done**: `git add . && git commit -m "Project 11: password_generator.py — argparse CLI, string module, random generation"`

---

### Project 12: `todo_manager.py` (~1 hour)

**What to build**: A full-featured todo list manager. Each task has a title, priority (High/Medium/Low), due date (optional), and completion status. The user can add tasks, view tasks (sorted by priority or due date), mark tasks complete, delete tasks, and filter by status or priority. Everything persists to JSON.

This is your most complex project yet — it pulls together functions, classes, JSON file I/O, dictionaries, lists, sorting, filtering, input validation, and clean program architecture. Think of it as a "Week 1 final exam" that proves you've internalized the foundations.

**Concepts to learn and use**:
- **Everything from this week** — classes, `__init__`, `self`, `__str__`, JSON persistence, functions, loops, error handling
- **`sorted()` with `key` parameter** — `sorted(tasks, key=lambda t: t.priority)` sorts a list by a specific attribute. The `key` argument takes a function that extracts the comparison value.
- **`lambda`** — small anonymous function: `lambda t: t.due_date` is shorthand for a function that takes `t` and returns `t.due_date`
- **`datetime.strptime()`** — parse a date string into a datetime object: `datetime.strptime("2026-03-10", "%Y-%m-%d")`
- **Filtering with list comprehensions** — `[t for t in tasks if t.priority == "High"]` or `[t for t in tasks if not t.completed]`
- **Multiple sort keys** — sort by priority first, then by due date within each priority

**Reference material**:
- Python docs — `sorted()`: https://docs.python.org/3/library/functions.html#sorted
- Python docs — sorting HOW TO: https://docs.python.org/3/howto/sorting.html
- Python docs — `datetime.strptime()`: https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime
- Real Python — sorting: https://realpython.com/python-sort/
- Real Python — lambda: https://realpython.com/python-lambda/

**Design questions to answer before you code**:
1. What data does a `Task` hold? Title (str), priority (str: "High"/"Medium"/"Low"), due_date (str or None), completed (bool). Should there also be a created_date?
2. How do you handle priorities for sorting? One approach: map priorities to numbers (`{"High": 1, "Medium": 2, "Low": 3}`) so `sorted()` puts High first.
3. How does the view display tasks? Number them so the user can reference them for mark-complete or delete operations. Show completion status with a visual indicator: `[✓]` or `[ ]`.
4. What does the menu look like? Options: Add task, View all, View incomplete, View by priority, Mark complete, Delete, Quit.
5. Due date input: How does the user enter a date? Suggest the format `YYYY-MM-DD` and validate it with `try`/`except` around `strptime()`. Allow blank for no due date.

**Ask GLM-4.7-Flash before coding**: `Cmd+L` → "Explain Python's `sorted()` function with the `key` parameter, and explain `lambda` functions. How do I sort a list of objects by one attribute, and then by multiple attributes? Simple examples, not my program."

**Write your code.** Structure it like this:
```
import json
from datetime import datetime

TASKS_FILE = "tasks.json"

PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}

class Task:
    def __init__(self, title, priority="Medium", due_date=None, completed=False):
        # store attributes

    def to_dict(self):
        # for JSON serialization

    def __str__(self):
        # formatted display: [✓] Buy groceries (High) - Due: 2026-03-10

class TodoManager:
    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self):
        # read JSON, create Task objects

    def save_tasks(self):
        # convert to dicts, write JSON

    def add_task(self):
        # get title, priority (validate: must be High/Medium/Low),
        # due date (validate format or blank), create Task, save

    def view_tasks(self, filter_fn=None, sort_key=None):
        # apply optional filter, apply optional sort
        # display numbered list

    def mark_complete(self):
        # show incomplete tasks, user picks number

    def delete_task(self):
        # show all tasks, user picks number to delete

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
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
```

**Notice**: The `view_tasks` method takes optional `filter_fn` and `sort_key` parameters — this is a powerful pattern where you pass functions as arguments. The `main()` function decides what filter/sort to use, and `view_tasks` applies them generically. This is a taste of higher-order functions, a concept you'll use heavily in Month 2.

**Ask GLM-4.7-Flash after coding**: Select all code → `Cmd+L` → "Review this todo manager. Is my class design solid? Am I using `sorted()` with `key` and `lambda` correctly? Is the `filter_fn` parameter pattern a good approach? What edge cases am I missing? What would a senior developer refactor?"

**Commit when done**: `git add . && git commit -m "Project 12: todo_manager.py — comprehensive OOP, sorted/lambda, filter patterns, Week 1 capstone"`

---

## BEFORE BED: Background Downloads

Kick these off before sleeping — they'll run overnight:

```bash
# General purpose model (~17GB)
ollama pull qwen3.5:27b

# Premium coding model (~52GB) — Sonnet 4.5-level, start overnight
ollama pull qwen3-coder-next

# llama.cpp for massive MoE models later in the plan
brew install llama.cpp

# Apple MLX framework (venv should already be active)
pip install mlx mlx-lm
```

These aren't needed this week but having them ready means you're prepared when the plan calls for them.

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 6
- [ ] Day number: 6
- [ ] Hours coded: 2
- [ ] Projects completed: 2 (password_generator, todo_manager)
- [ ] Key concepts: argparse, command-line arguments, if __name__ == "__main__", sorted() with key, lambda, passing functions as arguments, comprehensive class design
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 7 — Saturday, first Mac weekend!):
- **Morning (8:00–11:00 AM)**: 3 hours, Projects 13–14
  - `budget_tracker.py` — Monthly budget with categories, spending alerts (builds on expense_tracker)
  - `personal_finance.py` — Multiple accounts, transaction history, category analysis, CSV import/export
- **New concepts**: CSV reading/writing, more advanced class hierarchies, building on top of previous projects
- **This is your first 3-hour weekend session — pace yourself, take breaks**

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

Building on Days 1–5, you should now also be able to explain:

1. What `argparse` is and how to use `ArgumentParser`, `add_argument`, and `parse_args`
2. The difference between positional arguments and optional flags (like `--length` or `--no-special`)
3. What `if __name__ == "__main__"` means and why it's used
4. How `sorted()` works with a `key` parameter
5. What a `lambda` function is — shorthand for a small function you pass as an argument
6. How to pass a function as an argument to another function (higher-order functions)
7. How to filter a list with a comprehension: `[x for x in items if condition]`
8. How to validate user input for dates using `try`/`except` with `strptime()`

**Week 1 weeknight wrap-up**: You've now built 12 projects across 6 days. You can write functions, classes, handle files (JSON), parse command-line arguments, sort and filter data, and validate input. Tomorrow starts your first weekend session — longer blocks, bigger builds.

---

**Day 6 of 365. Last weeknight of Week 1. The weekend is where things get interesting.** 🚀
