# DAY 4 — Wednesday, March 4, 2026
## First Mac Coding Session! 🚀

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue in VS Code)  
**Phase**: Foundation — you write, AI explains and reviews  
**Commute**: CS50 Week 1 Part 1  
**Evening Session**: 7:00–9:00 PM (2 hours) — Setup (30 min) + Build 2 projects (1.5 hrs)

---

## COMMUTE: CS50 Week 1 Part 1

This is where CS50 transitions from Scratch to C — but the concepts are universal. Focus on how David Malan explains variables, types, conditionals, and loops at a lower level. You already know these from Python, but seeing them explained differently strengthens your mental model. Available on YouTube (search "CS50 2024 Week 1") or at https://cs50.harvard.edu/x/

---

## EVENING SESSION PART 1 (7:00–7:30 PM): Finish AI Stack Setup

Run through these in order. If you already completed some last night, skip to what's left.

### Verify Last Night's Setup
```bash
# Is Ollama running?
curl http://localhost:11434
# Should respond: "Ollama is running"

# Did the Qwen3-Coder download finish?
ollama list
# Should show glm-4.7-flash (19GB)
# If not, run: ollama pull glm-4.7-flash
```

### Pull Remaining Models
```bash
# IDE autocomplete — small and fast (~5GB)
ollama pull qwen2.5-coder:7b

# Reasoning model (~20GB) — start this, let it download while you code
# If internet is slow, skip and download overnight
ollama pull deepseek-r1:32b
```

### Set Up Python Virtual Environment
```bash
# Create your dev tools venv
python3 -m venv ~/.venvs/dev

# Activate it — you'll see (dev) in your prompt
source ~/.venvs/dev/bin/activate

# Install dev tools (works because you're in a venv)
pip install pytest black ruff ipython

# Make it activate automatically in every new terminal
echo 'source ~/.venvs/dev/bin/activate' >> ~/.zshrc

# Verify
pytest --version
black --version
ruff --version
```

### Configure Continue IDE

Open VS Code, then set up your config:

```bash
# Open your project
cd ~/dev/year-1
code .
```

Create/edit the Continue config file:
```bash
nano ~/.continue/config.yaml
```

Paste this entire config:
```yaml
name: Josh Local AI Stack
version: 1.0.0
schema: v1

models:
  - name: GLM-4.7 Flash
    provider: ollama
    model: glm-4.7-flash
    roles:
      - chat
      - edit
      - apply
    defaultCompletionOptions:
      contextLength: 32768
      temperature: 0.7

  - name: DeepSeek R1 32B
    provider: ollama
    model: deepseek-r1:32b
    roles:
      - chat
    defaultCompletionOptions:
      contextLength: 32768
      temperature: 0.6

  - name: Qwen2.5 Coder 7B
    provider: ollama
    model: qwen2.5-coder:7b
    roles:
      - autocomplete
    autocompleteOptions:
      debounceDelay: 200
      maxPromptTokens: 1024
      onlyMyCode: true

context:
  - provider: file
  - provider: code
  - provider: diff
  - provider: terminal

rules:
  - >
    When reviewing code, focus on: correctness, error handling,
    edge cases, and Python best practices. Be specific about
    what to change and why.
```

Save (`Ctrl+O`, Enter, `Ctrl+X`).

### Quick Verification
1. In VS Code, press `Cmd+L` to open Continue chat
2. Verify "GLM-4.7 Flash" appears in the model dropdown
3. Type: "What does Python's `def` keyword do? One paragraph."
4. Confirm you get a fast, detailed response
5. Open a .py file and start typing — ghost text suggestions should appear (from 7B autocomplete)

**If anything fails**, refer to the troubleshooting section in Mac-Studio-Setup-Verification.md.

### Setup Checklist
- [ ] Ollama running with glm-4.7-flash loaded
- [ ] qwen2.5-coder:7b pulled (for autocomplete)
- [ ] deepseek-r1:32b pulling or queued for tonight
- [ ] (dev) venv active, pytest/black/ruff installed
- [ ] Continue config.yaml saved, GLM-4.7 Flash responding
- [ ] Autocomplete ghost text working

**Setup done? Start coding!**

---

## EVENING SESSION PART 2 (7:30–9:00 PM): First Mac Projects

Still Foundation phase — write every line yourself. But now you have a much more capable AI assistant for concept explanations and code reviews. Feel the difference.

---

### Project 7: `password_checker.py` (~40 min)

**What to build**: A program that takes a password from the user and evaluates its strength. Check for length, uppercase letters, lowercase letters, digits, and special characters. Output a strength rating (Weak / Medium / Strong) with specific feedback on what's missing.

**Concepts to learn and use**:
- **Defining functions with `def`** — this is the big new concept today. Break your logic into reusable functions instead of one long script.
- `str` methods — `.isupper()`, `.islower()`, `.isdigit()` work on individual characters
- `any()` — checks if any item in an iterable is True (e.g., `any(c.isupper() for c in password)`)
- Generator expressions — `c.isupper() for c in password` iterates through each character
- `len()` — measuring string length
- `string` module — `string.punctuation` gives you all special characters
- Returning values from functions with `return`

**Reference material**:
- Python docs — defining functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
- Python docs — string methods: https://docs.python.org/3/library/stdtypes.html#string-methods
- Python docs — `any()` built-in: https://docs.python.org/3/library/functions.html#any
- Real Python — functions: https://realpython.com/defining-your-own-python-function/

**Design questions to answer before you code**:
1. What makes a password "Strong" vs "Medium" vs "Weak"? Define your criteria before writing code. For example: Strong = 12+ chars, has upper, lower, digit, and special. Medium = 8+ chars, has at least 3 of the 4 categories. Weak = everything else.
2. How will you structure the functions? Consider: `check_length(password)`, `check_complexity(password)`, `get_strength(password)`, `get_feedback(password)`. Each function does one thing.
3. What does `get_feedback` return? A list of strings like `["Add uppercase letters", "Add special characters"]`? Or a single summary string?
4. Should the function return the strength rating, or print it directly? (Returning is better — it separates logic from display.)

**Ask GLM-4.7-Flash before coding**: `Cmd+L` → "Explain how to define functions in Python with `def`. Cover parameters, return values, and why breaking code into functions is better than one long script. Don't write my program."

**Write your code.** Structure it like this:
```
import string

def check_length(password):
    # your logic

def check_complexity(password):
    # your logic

def get_strength(password):
    # uses check_length and check_complexity
    # returns "Weak", "Medium", or "Strong"

def get_feedback(password):
    # returns list of suggestions

# Main program
password = input(...)
strength = get_strength(password)
feedback = get_feedback(password)
# display results
```

**Ask GLM-4.7-Flash after coding**: Select all code → `Cmd+L` → "Review this password checker. Are my functions well-structured? Am I using `any()` and string methods effectively? What would a senior developer change?"

**Commit when done**: `git add . && git commit -m "Project 7: password_checker.py — functions, string methods, any()"`

---

### Project 8: `contact_book.py` (~45 min)

**What to build**: A contact book where the user can add contacts (name, phone, email), view all contacts, search by name, and delete contacts. The key feature: contacts are saved to a JSON file so they persist between program runs. When the program starts, it loads existing contacts. When the program exits, it saves them.

**Concepts to learn and use**:
- **JSON file I/O** — `json.dump()` to save, `json.load()` to read. This is how you persist data without a database.
- `import json` — your second module import (after `random`)
- **File handling** — `open()` with `'r'` (read) and `'w'` (write) modes
- `with` statement — ensures files are properly closed (context manager)
- **Dictionaries** — each contact is a dict: `{"name": "Josh", "phone": "555-1234", "email": "josh@example.com"}`
- **List of dictionaries** — the full contact book is a list containing contact dicts
- List comprehensions (optional) — `[c for c in contacts if search_term in c["name"].lower()]`
- Functions for each action: `add_contact()`, `view_contacts()`, `search_contacts()`, `delete_contact()`, `save_contacts()`, `load_contacts()`
- Menu loop — the `while True` + `break` pattern from Day 2's number_guesser, but now as a menu

**Reference material**:
- Python docs — `json` module: https://docs.python.org/3/library/json.html
- Python docs — reading and writing files: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
- Python docs — `with` statement: https://docs.python.org/3/reference/compound_stmts.html#with
- Real Python — working with JSON: https://realpython.com/python-json/
- Python docs — dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries

**Design questions to answer before you code**:
1. Where does the JSON file live? Use a constant at the top: `CONTACTS_FILE = "contacts.json"`. Keep it in the same directory as the script for now.
2. What happens if the file doesn't exist yet (first run)? Your `load_contacts()` function needs to handle this — use a `try`/`except FileNotFoundError` to return an empty list.
3. When do you save? After every add/delete operation? Or only when the user chooses "Quit"? Saving after every change is safer (no data loss if the program crashes).
4. How does search work? Case-insensitive partial match is most useful: searching "jo" finds "Josh" and "Jordan".
5. How does delete work? Show the user a numbered list and let them pick by number? Or by name? Number is more reliable.

**Ask GLM-4.7-Flash before coding**: `Cmd+L` → "Explain how to read and write JSON files in Python using the json module. Show how `with open()` works for both reading and writing, and explain what happens if you try to read a file that doesn't exist. Don't write my program."

**Write your code.** Structure it like this:
```
import json

CONTACTS_FILE = "contacts.json"

def load_contacts():
    # try to read from file, return [] if not found

def save_contacts(contacts):
    # write contacts list to JSON file

def add_contact(contacts):
    # get name, phone, email from user
    # append to contacts, save

def view_contacts(contacts):
    # display all contacts formatted nicely

def search_contacts(contacts):
    # get search term, find matches, display

def delete_contact(contacts):
    # show numbered list, user picks number to delete, save

def main():
    contacts = load_contacts()
    while True:
        # show menu
        # get choice
        # call appropriate function
        # break on quit

main()
```

**Ask GLM-4.7-Flash after coding**: Select all code → `Cmd+L` → "Review this contact book. Is my JSON file handling correct? What happens if the JSON file gets corrupted? Is my function structure clean? What error cases am I missing?"

**Commit when done**: `git add . && git commit -m "Project 8: contact_book.py — JSON file I/O, dictionaries, with statement"`

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 4
- [ ] Day number: 4
- [ ] Hours coded: 1.5 (+ 0.5 setup)
- [ ] Projects completed: 2 (password_checker, contact_book)
- [ ] Key concepts: def functions, return values, string methods, any(), json module, file I/O, with statement, dictionaries
- [ ] First Mac coding session! How does GLM-4.7-Flash compare to CodeLlama 34B? ___
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 5 — Thursday):
- **Commute**: CS50 Week 1 Part 2
- **Evening (7:00–9:00 PM)**: Projects 9–10
  - `expense_tracker.py` — Track expenses with categories (classes, lists, basic OOP)
  - `quiz_game.py` — Quiz from JSON file (file I/O, classes, scoring)
- **New concepts**: classes (`class`), `__init__`, `self`, object-oriented programming basics

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

Building on Days 1–2, you should now also be able to explain:

1. How to define a function with `def`, pass parameters, and return values
2. Why functions are better than one long script (reusability, readability, testability)
3. How `any()` works with a generator expression
4. How to import and use the `json` module
5. How `with open(filename, 'r') as f:` works and why `with` is better than manual `open()`/`close()`
6. The difference between `json.load()` (reads file) and `json.loads()` (reads string)
7. How dictionaries work — creating, accessing keys, adding key-value pairs
8. How to handle a missing file with `try`/`except FileNotFoundError`

Functions and file I/O are the two biggest building blocks you pick up today. Every project from here forward uses both.

---

**Day 4 of 365. First code on the Mac Studio. You'll feel the difference immediately.** 🚀
