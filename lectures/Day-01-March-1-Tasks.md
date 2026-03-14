# DAY 1 — Sunday, March 1, 2026 🚀
## Your First Day as a Python Developer

**System**: Ubuntu (CodeLlama 34B via Continue in VS Code)  
**Total Time**: ~4.5 hours  
**Morning Session**: 8:00–11:00 AM (3 hours) — Build 4 projects  
**Evening Session**: 7:00–8:30 PM (1.5 hours) — Setup & planning

---

## MORNING SESSION (8:00–11:00 AM)

### Pre-Flight: Environment Check (~15 min)

Make sure your Ubuntu dev environment is ready before writing any code.

```bash
# Verify Python is installed (need 3.10+)
python3 --version

# If not installed:
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify Git
git --version

# If not installed:
sudo apt install git

# Verify VS Code (or install)
code --version

# If not installed:
sudo snap install code --classic

# Install VS Code Python extension from the command line
code --install-extension ms-python.python
```

Set up your project repo:
```bash
# Create your year-long repo structure
mkdir -p ~/dev/year-1/month-01/week-01
cd ~/dev/year-1

# Initialize Git
git init
git branch -M main

# Create a .gitignore
# (you write the contents — think about what Python files you don't want tracked)

# Connect to GitHub
# Create a new repo on github.com first, then:
git remote add origin git@github.com:josh-bearss-codes/python-learning-2026.git
```

---

### Using Continue + CodeLlama 34B as Your Learning Partner

You have CodeLlama 34B running through Continue in VS Code — that's your AI coding assistant for the next 4 days until the Mac Studio arrives. Here's how to use it effectively as a *learning tool*, not a code generator.

**The golden rule**: Never ask it to write your project for you. You learn by struggling, not by copying. Use it the way you'd use a senior developer sitting next to you — ask questions, get explanations, then write the code yourself.

#### How to Talk to Continue (Cmd+L or Ctrl+L to open chat)

**Good prompts for learning** (use these today):
- "Explain how Python's `input()` function works and what type it returns"
- "What's the difference between `int()` and `float()` for type conversion?"
- "Why does Python use `try/except` instead of checking errors beforehand?"
- "I wrote this function but it's not returning what I expect — can you explain what's happening?" (then paste your broken code)
- "What are the common Python conventions for naming variables and functions?"
- "Is there a better way to structure this?" (paste your working code for review)

**Bad prompts that short-circuit your learning** (avoid these):
- "Write me a calculator in Python"
- "Write a function that converts Fahrenheit to Celsius"
- "Give me the code for a tip calculator"
- "Finish this program for me"

#### The 3-Step Workflow for Each Project

**Step 1 — Plan before you type**: Open Continue and describe what you're about to build. Ask it to explain the concepts you'll need. Don't ask for code — ask for understanding.

Example: "I'm about to build a unit converter that handles temperature, distance, and weight. What Python concepts should I understand before starting? Don't write the code — just explain the concepts."

**Step 2 — Write your code first, then ask for review**: Attempt the project yourself. When you get stuck or finish, highlight your code in the editor and press Cmd+L (or Ctrl+L) to send it to Continue.

Example: "Here's my calculator. It works but I'm not sure if my error handling covers all the edge cases. What could still crash this program?" 

**Step 3 — Debug with explanations, not fixes**: When something breaks, paste the error message and ask Continue to *explain* what went wrong — not to fix it for you.

Example: "I'm getting this error: `ValueError: invalid literal for int() with base 10: 'hello'`. Explain what this means and what concept I'm missing."

#### CodeLlama 34B Quirks to Know

- It's strong at explaining Python concepts and reviewing code structure
- It can be inconsistent on longer outputs — if a response seems off, rephrase and ask again
- It may occasionally suggest outdated patterns — when in doubt, check the Python docs links provided for each project
- It's better at answering specific questions than open-ended "teach me everything" requests
- Keep your prompts focused — one concept or one question at a time gets better results than dumping a wall of text

#### Quick Reference: Continue Shortcuts in VS Code

| Action | Shortcut |
|--------|----------|
| Open chat panel | `Ctrl+L` |
| Send highlighted code to chat | Select code → `Ctrl+L` |
| Inline edit suggestion | `Ctrl+I` (use sparingly — you want to type it yourself today) |
| Accept autocomplete | `Tab` |
| Reject autocomplete | `Esc` |

**Bottom line**: CodeLlama 34B is your tutor, not your ghostwriter. Ask it "why" and "what does this mean" — not "write this for me."

---

### Project 1: `hello.py` (~30 min)

**What to build**: A program that greets the user by name, asks their age, and tells them what year they were born. Use formatted output.

**Concepts to learn and use** (look these up, don't just guess):
- `input()` function — how to get user input as a string
- `int()` — type conversion from string to integer
- `f-strings` — Python's preferred string formatting (f"Hello {name}")
- `print()` — with formatted output
- Basic arithmetic with variables

**Reference material**:
- Python docs — `input()`: https://docs.python.org/3/library/functions.html#input
- Python docs — f-strings: https://docs.python.org/3/tutorial/inputoutput.html#fancier-output-formatting
- Real Python — f-strings guide: https://realpython.com/python-f-strings/

**Challenge yourself**: What happens if the user types "twenty" instead of "20" for their age? Your program will crash. That leads directly into Project 2.

**Ask CodeLlama 34B**: After you write it, highlight your code, hit `Ctrl+L`, and ask: "What would happen if the user entered a blank name or typed letters for their age? What am I not handling?"

**Commit when done**: `git add . && git commit -m "Project 1: hello.py — input, variables, f-strings"`

---

### Project 2: `calculator.py` (~45 min)

**What to build**: A calculator that asks for two numbers and an operation (+, -, *, /), performs the calculation, and displays the result. Handle errors gracefully — don't let the program crash.

**Concepts to learn and use**:
- `try` / `except` blocks — catching errors before they crash your program
- `if` / `elif` / `else` — conditional logic
- `float()` — converting strings to decimal numbers
- `ValueError` — what Python raises when type conversion fails
- `ZeroDivisionError` — what happens when you divide by zero

**Reference material**:
- Python docs — errors and exceptions: https://docs.python.org/3/tutorial/errors.html
- Python docs — `if` statements: https://docs.python.org/3/tutorial/controlflow.html#if-statements
- Real Python — exception handling: https://realpython.com/python-exceptions/

**Design questions to answer before you code**:
1. Should you use `int()` or `float()` for the numbers? Why?
2. What are ALL the ways a user could cause this program to crash? Handle each one.
3. Should the program quit after one calculation, or loop and ask again?

**Ask CodeLlama 34B before coding**: "I'm about to build a basic calculator. Explain how `try/except` works in Python with a simple example — don't write the calculator, just show me the error handling pattern."

**Ask CodeLlama 34B after coding**: Highlight your code → `Ctrl+L` → "Review my error handling. Are there any user inputs that would still crash this program?"

**Commit when done**: `git add . && git commit -m "Project 2: calculator.py — conditionals, error handling"`

---

### Project 3: `tip_calculator.py` (~45 min)

**What to build**: A restaurant tip calculator. Takes the bill amount, number of people splitting, and desired tip percentage. Displays the tip amount, total with tip, and each person's share. Format all money output to 2 decimal places.

**Concepts to learn and use**:
- String formatting for currency — `f"${amount:.2f}"` (the `:.2f` part)
- Multiple `input()` calls building a workflow
- Arithmetic with floats (and why floating point math can be weird)
- Reuse your `try`/`except` pattern from Project 2

**Reference material**:
- Python docs — format specification: https://docs.python.org/3/library/string.html#format-specification-mini-language
- Real Python — number formatting: https://realpython.com/python-formatted-output/

**Design questions**:
1. What should happen if someone enters 0 people splitting?
2. What's a reasonable range for tip percentages? Should you validate that?
3. Can you make the output look clean and professional, like a receipt?

**Ask CodeLlama 34B before coding**: "Explain how Python's f-string format specifier `:.2f` works for displaying currency. Just the formatting concept — don't write the program."

**Ask CodeLlama 34B after coding**: Highlight your code → `Ctrl+L` → "I'm reusing try/except from my last project. Is my pattern correct, or am I catching too broadly? Also, does my output look professional?"

**Commit when done**: `git add . && git commit -m "Project 3: tip_calculator.py — formatted output, input validation"`

---

### Project 4: `unit_converter.py` (~45 min)

**What to build**: A converter that handles temperature (F↔C), distance (miles↔km), and weight (lbs↔kg). User picks a category, then a conversion direction, enters a value, and gets the result.

**Concepts to learn and use**:
- **Functions** (`def`) — this is the big one today. Write a separate function for each conversion.
- **Dictionaries** — store conversion options as key-value pairs
- `while` loops — let the user convert multiple values without restarting
- Program structure — a `main()` function that organizes the flow

**Reference material**:
- Python docs — defining functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
- Python docs — dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
- Python docs — `while` loops: https://docs.python.org/3/tutorial/introduction.html#first-steps-towards-programming
- Real Python — functions: https://realpython.com/defining-your-own-python-functions/

**Design questions**:
1. How do you organize the menu? Nested if/elif, or a dictionary mapping choices to functions?
2. Each conversion formula should be its own function. Why is that better than one giant function?
3. How does the user quit the program? (`q` to quit, loop with a break condition)

**Ask CodeLlama 34B before coding**: "Explain the concept of using a Python dictionary to map user choices to functions. I want to understand the pattern — don't write my converter for me. Just explain how a dictionary can hold function references."

**Ask CodeLlama 34B after coding**: Highlight your code → `Ctrl+L` → "Review the structure of this program. Did I use functions well? Is there a more Pythonic way to organize the menu and dispatch logic?"

**Conversion formulas** (the only "answers" I'll give you — the math isn't the point):
- °F to °C: (F - 32) × 5/9
- Miles to km: miles × 1.60934
- Lbs to kg: lbs × 0.453592

**Commit when done**: `git add . && git commit -m "Project 4: unit_converter.py — functions, dictionaries, while loops"`

---

### Morning Wrap-Up

After all 4 projects, push to GitHub:
```bash
git push -u origin main
```

Take a break. You've earned it.

---

## EVENING SESSION (7:00–8:30 PM)

### Task 1: Organize Your Repo (~20 min)

- [ ] Make sure all 4 `.py` files are in `~/dev/year-1/month-01/week-01/`
- [ ] Each file should have a comment at the top explaining what it does
- [ ] Verify everything is committed and pushed to GitHub
- [ ] Create a `README.md` in the repo root — write a brief description of the project and your goals (this is for you, not the public yet)

### Task 2: Set Up Your Tracker (~30 min)

Create a tracking system you'll use every day for 12 months. This can be a spreadsheet, a markdown file, or whatever you'll actually stick with.

**Track daily**:
- [ ] Date
- [ ] Day number (today is Day 1)
- [ ] Hours coded
- [ ] Projects completed
- [ ] Key concepts learned
- [ ] Commit message
- [ ] Mood/energy level (1–5) — useful for identifying patterns later

**Track weekly** (Sundays):
- [ ] Total hours
- [ ] Total projects
- [ ] Cumulative hours and projects
- [ ] Biggest win
- [ ] Biggest struggle
- [ ] Next week's focus

### Task 3: Queue Commute Content (~20 min)

Download or bookmark for tomorrow's commute:

- [ ] **CS50 Week 0 Part 1** — Harvard's intro to computer science (YouTube or cs50.harvard.edu)
  - This covers computational thinking, abstraction, and problem decomposition
  - Even though you know data engineering, CS50 fills in CS fundamentals you may have gaps in
- [ ] **Talk Python To Me** — bookmark 2–3 recent episodes for later in the week
  - https://talkpython.fm/
- [ ] **Real Python podcast** — bookmark for Week 2+
  - https://realpython.com/podcasts/rpp/

### Task 4: Plan Tomorrow (~10 min)

Review what's on deck for Day 2 (Monday):

- **Commute**: CS50 Week 0 Part 1
- **Evening (7:00–9:00 PM)**: Projects 5–6
  - `grade_calculator.py` — convert numeric scores to letter grades (if/elif chains, lists)
  - `number_guesser.py` — computer picks a number, you guess with hints (while loops, random module)
- **Concepts to preview**: `random` module, `while` loops with break conditions, list basics

---

## DAY 1 CHECKLIST

### Morning (8:00–11:00 AM)
- [ ] Environment verified (Python 3.10+, Git, VS Code)
- [ ] Repo created and connected to GitHub
- [ ] **Project 1**: `hello.py` — input, variables, f-strings
- [ ] **Project 2**: `calculator.py` — conditionals, try/except error handling
- [ ] **Project 3**: `tip_calculator.py` — formatted currency output, input validation
- [ ] **Project 4**: `unit_converter.py` — functions, dictionaries, while loops
- [ ] All code committed and pushed to GitHub

### Evening (7:00–8:30 PM)
- [ ] Repo organized with comments and README
- [ ] Daily/weekly tracker created
- [ ] Commute content queued (CS50 Week 0)
- [ ] Tomorrow's plan reviewed

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

By the end of Day 1, you should be able to explain in your own words:

1. How `input()` works and why it always returns a string
2. How to convert types with `int()`, `float()`, and `str()`
3. What an f-string is and why Python developers prefer them
4. How `try`/`except` prevents crashes and which exceptions to catch
5. How `if`/`elif`/`else` chains work
6. How to define and call a function with `def`
7. What a dictionary is and when to use one vs. a list
8. How a `while` loop works and how to break out of it
9. How to commit and push code to GitHub
10. How to use Continue + CodeLlama 34B to ask concept questions and get code reviews without having it write code for you

If any of these feel shaky, that's normal — you'll reinforce all of them over the next few days.

---

**Day 1 of 365. Let's go.** 🚀
