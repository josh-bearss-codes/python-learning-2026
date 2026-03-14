# DAY 2 — Monday, March 2, 2026
## First Weeknight Session

**System**: Ubuntu (CodeLlama 34B via Continue in VS Code)  
**Phase**: Foundation — you write, AI explains and reviews  
**Commute**: CS50 Week 0 Part 1  
**Evening Session**: 7:00–9:00 PM (2 hours) — Build 2 projects  

---

## COMMUTE: CS50 Week 0 Part 1

Watch or listen during your commute. This lecture covers computational thinking, abstraction, and how to decompose problems — concepts that apply directly to tonight's projects. Available on YouTube (search "CS50 2024 Week 0") or at https://cs50.harvard.edu/x/

Don't worry about the Scratch portion — focus on the problem-solving framework David Malan walks through. That thinking process is what matters, not the specific tool.

---

## EVENING SESSION (7:00–9:00 PM)

You're still in the Foundation phase — write every line yourself, use CodeLlama 34B to explain concepts and review your finished code.

---

### Project 5: `grade_calculator.py` (~45 min)

**What to build**: A program that takes a list of numeric scores from the user, converts each to a letter grade, and displays a summary — individual grades, the average score, and the overall letter grade for the average.

**Concepts to learn and use**:
- `if` / `elif` / `else` chains — mapping score ranges to letter grades (A, B, C, D, F)
- **Lists** — storing multiple scores (this is your first real data structure)
- `append()` — adding items to a list
- `while` or `for` loops — iterating through scores
- `len()`, `sum()` — built-in functions that work on lists
- `round()` — cleaning up the average

**Reference material**:
- Python docs — lists: https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
- Python docs — `for` loops: https://docs.python.org/3/tutorial/controlflow.html#for-statements
- Real Python — lists and tuples: https://realpython.com/python-lists-tuples/

**Design questions to answer before you code**:
1. How does the user enter scores? One at a time in a loop, or all at once separated by commas? Try the loop approach — it's more natural for learning `while` and `append()`.
2. How does the user signal they're done entering scores? (Hint: an empty input, or typing "done")
3. What grading scale will you use? Decide before coding — write the ranges as comments first, then implement the if/elif chain.
4. What happens if the user enters no scores at all? What about negative numbers or scores above 100?

**Ask CodeLlama 34B before coding**: Open Continue (`Ctrl+L`) and ask: "Explain how Python lists work — how to create one, add items with append, and loop through them with a for loop. Don't write my program, just explain the data structure."

**Ask CodeLlama 34B after coding**: Highlight your finished code → `Ctrl+L` → "Review this grade calculator. Am I using lists effectively? Is my if/elif grading logic clean, or is there a better pattern?"

**Commit when done**: `git add . && git commit -m "Project 5: grade_calculator.py — lists, loops, if/elif chains"`

---

### Project 6: `number_guesser.py` (~45 min)

**What to build**: The computer picks a random number between 1 and 100. The user guesses, and the program says "too high" or "too low" until they get it right. Track and display the number of guesses it took.

**Concepts to learn and use**:
- `import random` — your first module import
- `random.randint(a, b)` — generating a random integer in a range
- `while True` with `break` — a loop that runs until a condition is met (the correct guess)
- Counter variable — incrementing a number each loop iteration
- Comparison operators — `<`, `>`, `==`

**Reference material**:
- Python docs — `random` module: https://docs.python.org/3/library/random.html
- Python docs — `import` statement: https://docs.python.org/3/tutorial/modules.html
- Python docs — `break` and `continue`: https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops
- Real Python — while loops: https://realpython.com/python-while-loop/

**Design questions to answer before you code**:
1. What's the structure? You need a loop that keeps asking for guesses until the answer is correct. A `while True` loop with a `break` when they guess right is the cleanest pattern.
2. How do you count guesses? Initialize a variable to 0 before the loop, increment it inside the loop each time.
3. What happens if the user types "abc" instead of a number? Reuse the `try`/`except` pattern from yesterday's calculator.
4. **Stretch goal**: After they win, ask "Play again? (y/n)" and restart the game if yes. This means wrapping your game in another loop — think about how to nest them.

**Ask CodeLlama 34B before coding**: "Explain how `while True` with `break` works in Python. When would you use this pattern instead of a regular while loop with a condition? Just explain the concept."

**Ask CodeLlama 34B after coding**: Highlight your code → `Ctrl+L` → "Review this number guessing game. Is my loop structured well? Is there anything that could still crash, and is my guess counter in the right place?"

**Commit when done**: `git add . && git commit -m "Project 6: number_guesser.py — while loops, random module, break"`

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 2
- [ ] Day number: 2
- [ ] Hours coded: 2
- [ ] Projects completed: 2 (grade_calculator, number_guesser)
- [ ] Key concepts: lists, append, for loops, while True/break, random module, imports
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 3 — Tuesday):
- **Commute**: CS50 Week 0 Part 2
- **Evening (7:00–9:00 PM)**: Projects 7–8
  - `password_checker.py` — Check password strength using functions and string methods
  - `contact_book.py` — Save and load contacts with JSON file I/O
- **New concepts**: defining functions with `def`, string methods, JSON, reading/writing files

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

Building on yesterday, you should now also be able to explain:

1. What a list is and how to create, append to, and loop through one
2. How to use `len()` and `sum()` on a list
3. How to import and use a module (`import random`)
4. How a `while True` loop with `break` works and when to use it
5. How to use a counter variable to track iterations
6. The difference between `for` (iterate through a collection) and `while` (loop until a condition)

If the `while True` / `break` pattern feels weird, that's normal. You'll use it constantly — it becomes second nature fast.

---

**Day 2 of 365. First weeknight in the books.** 🚀
