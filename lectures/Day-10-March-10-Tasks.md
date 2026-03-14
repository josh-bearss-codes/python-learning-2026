# DAY 10 — Tuesday, March 10, 2026
## Lecture: Time as Data — How Objects Remember Their History

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI reviews more aggressively  
**Commute**: CS50 Week 2 continued (Arrays) or Talk Python To Me  
**Evening Session**: 7:00–9:00 PM (2 hours) — Build 1 project  
**Today's theme**: How programs model the passage of time, and how objects track their own state across days, weeks, and months

---

## OPENING LECTURE: THE DIMENSION MOST BEGINNERS IGNORE

Every project you've built so far has existed in a single moment. You run the program, interact with it, and it does its work. Some projects persisted data to JSON, but the data itself didn't have a meaningful relationship with *when* it was created or *how it changed over time.*

Today that changes. We're going to build a system where **time is a first-class dimension of the data.** A habit tracker doesn't just record *what* you did — it records *when* you did it, *how consistently* you did it, and *what patterns emerge* over days and weeks.

This is fundamentally different from the recipe manager or the budget tracker. Those systems manage collections of things. Today's system manages **the behavior of a thing across time.** A habit isn't a static piece of data — it's a living record that grows every day and whose meaning changes based on temporal patterns.

Why does this matter for your trajectory?

1. **Time-series data is everywhere in AI systems.** Log analysis, user behavior tracking, model performance monitoring, document versioning — all are data-over-time problems. If you can't model temporal relationships in Python, you can't build these systems.

2. **Streak logic is business logic that requires temporal reasoning.** "Has this user completed this habit every day for the past 7 days?" sounds simple. Implementing it correctly requires understanding date arithmetic, edge cases around gaps, and the difference between calendar days and elapsed time.

3. **Python's `datetime` module is one of the most frequently used and most frequently misused parts of the standard library.** Today we're going to understand it thoroughly — not just the syntax, but the conceptual model underneath.

Let's start with the fundamentals.

---

## LECTURE: PYTHON'S MODEL OF TIME

Python represents time through four core types in the `datetime` module. Understanding the relationships between them is critical — they are not interchangeable, and using the wrong one is a common source of bugs.

### The Four Types

```python
from datetime import date, time, datetime, timedelta
```

**`date`** — A calendar date with no time component. Year, month, day. Nothing else.

```python
today = date.today()              # date(2026, 3, 10)
birthday = date(1995, 7, 15)      # date(1995, 7, 15)

print(today.year)                 # 2026
print(today.month)                # 3
print(today.day)                  # 10
```

Think of `date` as a square on a calendar. It knows it's "March 10, 2026" but it doesn't know what hour it is. This is the right type for habits — you care whether someone exercised *on March 10*, not whether they exercised at 3:47 PM.

**`time`** — A time of day with no date component. Hour, minute, second.

```python
alarm = time(6, 30, 0)            # 06:30:00
print(alarm.hour)                 # 6
print(alarm.minute)               # 30
```

We won't use `time` today, but know it exists. It represents a point within a day, disconnected from any specific calendar date.

**`datetime`** — A specific moment: both date AND time together.

```python
now = datetime.now()              # datetime(2026, 3, 10, 19, 30, 0)
print(now.date())                 # date(2026, 3, 10) — extract just the date
print(now.time())                 # time(19, 30, 0) — extract just the time
```

`datetime` is the most commonly used type, but it's often **overkill.** If you only care about which day something happened, use `date`. Using `datetime` when you only need `date` creates subtle bugs — two events on the same day might compare as "not equal" because their times differ.

**`timedelta`** — A duration. Not a point in time, but a *distance between* two points in time.

```python
one_day = timedelta(days=1)
one_week = timedelta(weeks=1)
three_hours = timedelta(hours=3)

print(one_week)                   # 7 days, 0:00:00
print(one_week.days)              # 7
```

`timedelta` is the result of subtracting two dates or datetimes. It's also what you add to a date to get a future or past date. This is **date arithmetic** — and it's the backbone of today's project.

### Date Arithmetic: The Four Operations

There are exactly four meaningful arithmetic operations with dates:

**1. Date - Date = Timedelta** (How far apart are two dates?)

```python
from datetime import date

today = date(2026, 3, 10)
started = date(2026, 3, 1)

difference = today - started
print(difference)                 # 9 days, 0:00:00
print(difference.days)            # 9
print(type(difference))           # <class 'datetime.timedelta'>
```

This is the most important operation for streak tracking. If the last time a habit was completed was yesterday, `(today - last_completed).days == 1` — the streak continues. If it was two days ago, `.days == 2` — the streak is broken.

**2. Date + Timedelta = Date** (What date is N days from now?)

```python
from datetime import date, timedelta

today = date(2026, 3, 10)
next_week = today + timedelta(days=7)
print(next_week)                  # 2026-03-17

yesterday = today - timedelta(days=1)
print(yesterday)                  # 2026-03-09
```

Note: subtracting a timedelta from a date also gives a date (going backward). This is useful for calculating date ranges: "show me the last 7 days" means `today - timedelta(days=6)` through `today`.

**3. Timedelta + Timedelta = Timedelta** (Combining durations)

```python
from datetime import timedelta

a = timedelta(days=5)
b = timedelta(days=3)
print(a + b)                      # 8 days, 0:00:00
```

Less common, but useful when accumulating total time.

**4. Date compared to Date = Boolean** (Is one date before/after another?)

```python
from datetime import date

today = date(2026, 3, 10)
yesterday = date(2026, 3, 9)

print(today > yesterday)          # True
print(today == yesterday)         # False
print(today >= today)             # True
```

Dates support all comparison operators. This lets you sort completion dates, filter to date ranges, and check whether a habit was completed "today or earlier."

### What Date Arithmetic CANNOT Do

One operation you might expect to work **does not**:

```python
# THIS DOES NOT WORK:
date(2026, 3, 10) + date(2026, 3, 9)   # TypeError!
```

Adding two dates is meaningless — what would "March 10 plus March 9" even mean? Python correctly prevents this. Only `date ± timedelta` and `date - date` are valid.

### Converting Between Strings and Dates

Dates need to be stored as strings in JSON (JSON has no date type). You need to convert back and forth:

**Date → String** (serialization):
```python
from datetime import date

today = date.today()
date_string = today.isoformat()       # "2026-03-10"
# OR
date_string = today.strftime("%Y-%m-%d")  # "2026-03-10"

# strftime lets you format however you want:
print(today.strftime("%B %d, %Y"))    # "March 10, 2026"
print(today.strftime("%m/%d/%Y"))     # "03/10/2026"
```

The format codes: `%Y` = 4-digit year, `%m` = 2-digit month, `%d` = 2-digit day, `%B` = full month name, `%b` = abbreviated month name, `%A` = full weekday name.

**String → Date** (deserialization):
```python
from datetime import date

date_string = "2026-03-10"
parsed = date.fromisoformat(date_string)   # date(2026, 3, 10)
# OR
from datetime import datetime
parsed = datetime.strptime(date_string, "%Y-%m-%d").date()
```

`fromisoformat()` is the cleanest approach when your strings are in standard ISO format (YYYY-MM-DD). `strptime()` is necessary when the format varies (like the MM/DD/YYYY dates in yesterday's pipeline).

**For today's project**: Always store dates as ISO format strings in JSON (`"2026-03-10"`). Always convert back to `date` objects inside your program. The data layer handles the conversion. The business logic works exclusively with `date` objects, never with date strings.

---

## LECTURE: OBJECTS THAT TRACK STATE OVER TIME

Yesterday's recipe was static — a recipe doesn't change day to day. A habit is fundamentally different. A `Habit` object needs to know:

- Its definition (name, description, frequency target)
- Its complete history (which dates it was completed)
- Its current state (current streak, longest streak, completion rate)

The history grows every day. The state is **derived from** the history — you don't store "current streak = 5" as a permanent value. You **calculate** it from the completion dates every time it's needed. This is the same principle as the `balance` property on yesterday's Account class: derived values are computed, not stored.

Why not store the streak directly? Because stored derived values go stale. If you store "streak = 5" on Monday and the user doesn't complete the habit on Tuesday, the stored value is wrong on Wednesday. But if you calculate the streak from the completion dates, it's always correct.

This leads to a fundamental OOP pattern: **objects with an append-only history and computed properties.**

```python
class Habit:
    def __init__(self, name, completions=None):
        self.name = name
        self.completions = completions or []   # list of date objects — the history
    
    @property
    def current_streak(self):
        """Computed from completions. Always accurate. Never stored."""
        # Walk backward from today counting consecutive days
        ...
    
    @property
    def longest_streak(self):
        """Computed from completions. Always accurate. Never stored."""
        # Find the longest run of consecutive dates in history
        ...
```

The `completions` list is the **source of truth.** Everything else — streak, completion rate, statistics — is derived from it. This is a pattern called **event sourcing** in software architecture: store the events (completions), derive the state (streaks, stats). You'll encounter this pattern in production systems, especially in event-driven architectures that Kafka powers. Your data engineering background makes this intuitive — it's the same reason you'd store raw events in a data lake and compute aggregations on demand rather than storing pre-computed summaries.

### The Streak Algorithm

Let me walk through the streak calculation step by step, because this is the most algorithmically interesting part of today's project.

**Current streak**: How many consecutive days (ending today or yesterday) has this habit been completed?

```
Completions: [Mar 5, Mar 6, Mar 7, Mar 9, Mar 10]
Today: Mar 10

Step 1: Sort completions, remove duplicates
         → [Mar 5, Mar 6, Mar 7, Mar 9, Mar 10]

Step 2: Check if today (Mar 10) is in the list → Yes
        So the streak is at least 1

Step 3: Check if yesterday (Mar 9) is in the list → Yes
        Streak is at least 2

Step 4: Check if Mar 8 is in the list → No
        STOP. Current streak = 2 (Mar 9 and Mar 10)
```

What if the user hasn't completed the habit today yet?

```
Completions: [Mar 5, Mar 6, Mar 7, Mar 8, Mar 9]
Today: Mar 10

Step 1: Sort, deduplicate → [Mar 5, Mar 6, Mar 7, Mar 8, Mar 9]

Step 2: Check if today (Mar 10) is in the list → No
        But the user hasn't had a chance yet! Don't break the streak.
        Check if YESTERDAY (Mar 9) is in the list → Yes
        Streak starts from yesterday.

Step 3: Check Mar 8 → Yes. Mar 7 → Yes. Mar 6 → Yes. Mar 5 → Yes.
        Mar 4 → No. STOP.
        Current streak = 5 (Mar 5 through Mar 9)
```

This is the key insight: **the current streak starts from either today or yesterday** (whichever was most recently completed), then walks backward until it finds a gap. If neither today nor yesterday is in the completions, the current streak is 0.

In code, the algorithm looks like this:

```python
def _calculate_current_streak(self, completion_dates: set) -> int:
    """Walk backward from today counting consecutive completed days."""
    today = date.today()
    
    # Start from today if completed, otherwise from yesterday
    if today in completion_dates:
        check_date = today
    elif (today - timedelta(days=1)) in completion_dates:
        check_date = today - timedelta(days=1)
    else:
        return 0  # Neither today nor yesterday — streak is broken
    
    streak = 0
    while check_date in completion_dates:
        streak += 1
        check_date -= timedelta(days=1)   # Move one day backward
    
    return streak
```

Notice that we use a `set` of dates for `completion_dates` rather than a `list`. Why? Because checking `date in my_set` is O(1) — instant, regardless of how many dates exist. Checking `date in my_list` is O(n) — it has to scan every item. For a streak algorithm that checks dozens of dates in a loop, this matters.

**Longest streak**: What's the longest consecutive run in the entire history?

This algorithm is different — it scans the full sorted history and tracks runs:

```
Sorted completions: [Mar 1, Mar 2, Mar 3, Mar 5, Mar 6, Mar 7, Mar 8, Mar 10]

Walk through the list:
  Mar 1 → start a new run. current_run = 1
  Mar 2 → Mar 2 - Mar 1 = 1 day → consecutive! current_run = 2
  Mar 3 → Mar 3 - Mar 2 = 1 day → consecutive! current_run = 3
  Mar 5 → Mar 5 - Mar 3 = 2 days → GAP. Save longest = 3. current_run = 1
  Mar 6 → Mar 6 - Mar 5 = 1 day → consecutive! current_run = 2
  Mar 7 → Mar 7 - Mar 6 = 1 day → consecutive! current_run = 3
  Mar 8 → Mar 8 - Mar 7 = 1 day → consecutive! current_run = 4
  Mar 10 → Mar 10 - Mar 8 = 2 days → GAP. Save longest = 4. current_run = 1

End: longest = max(longest, current_run) = max(4, 1) = 4
Answer: Longest streak is 4 (Mar 5–8)
```

The key operation is `(current_date - previous_date).days == 1` — checking if two adjacent dates in the sorted list are exactly one day apart. This is date arithmetic in action.

### Understanding `@property` More Deeply

You saw `@property` briefly on Day 7. Let me explain what it's actually doing, because today it becomes essential.

In Python, you normally access attributes directly:

```python
habit = Habit("Exercise")
print(habit.name)          # Accesses the attribute directly
```

And you call methods with parentheses:

```python
print(habit.get_current_streak())   # Calls a method
```

`@property` lets you define something that **looks like an attribute but behaves like a method**:

```python
class Habit:
    @property
    def current_streak(self):
        # Complex calculation here
        return streak_value

# Usage — no parentheses!
print(habit.current_streak)     # Looks like an attribute access
                                 # But actually runs the calculation
```

Why use `@property` instead of a regular method?

1. **It communicates intent.** When someone reads `habit.current_streak`, it feels like reading a fact about the habit — "what is this habit's current streak?" If they had to write `habit.get_current_streak()`, it feels like asking the habit to *do* something. Properties express "what is" — methods express "do something."

2. **It allows you to change the implementation without changing the interface.** Today, `current_streak` is computed on the fly. Later, you might cache it for performance. With `@property`, the calling code never changes — it still writes `habit.current_streak`. If you used a regular method, switching from a stored value to a computed one (or vice versa) would require changing every call site.

3. **Convention.** In Python, `@property` is the standard way to expose derived values. `balance`, `current_streak`, `longest_streak`, `completion_rate` — anything that's calculated from other data rather than stored independently should be a property.

---

## PROJECT 17: `habit_tracker.py` (~2 hours)

### The Problem

Build a habit tracking system. The user defines habits they want to build (exercise daily, read 30 minutes, drink 8 glasses of water). Each day, they mark habits as completed. The system tracks their history and computes streaks, completion rates, and statistics. All data persists to JSON.

### Concepts to Learn and Use

- **`datetime.date` and `datetime.timedelta`** — the core types for all temporal logic
- **`date.today()`** — get the current date
- **`date.fromisoformat()` and `.isoformat()`** — convert between date objects and strings for JSON
- **`set` data structure** — storing completion dates as a set for O(1) membership testing
- **`@property` decorator** — computed properties for streaks, completion rate, statistics
- **Event sourcing pattern** — store events (completions), derive state (streaks, stats)
- **`sorted()` on dates** — date objects are naturally sortable in chronological order
- **`zip()` function** — pairing consecutive items: `zip(sorted_dates, sorted_dates[1:])` gives you pairs of adjacent dates for gap detection
- **`collections.Counter`** — counting completions by day-of-week to find patterns

### Reference Material

- Python docs — `datetime.date`: https://docs.python.org/3/library/datetime.html#date-objects
- Python docs — `datetime.timedelta`: https://docs.python.org/3/library/datetime.html#timedelta-objects
- Python docs — sets: https://docs.python.org/3/tutorial/datastructures.html#sets
- Python docs — `zip()`: https://docs.python.org/3/library/functions.html#zip
- Python docs — `collections.Counter`: https://docs.python.org/3/library/collections.html#collections.Counter
- Real Python — datetime: https://realpython.com/python-datetime/
- Real Python — sets: https://realpython.com/python-sets/

### Design Questions (Answer These BEFORE You Code)

1. **What does a Habit object track?**
   
   | Attribute | Type | Stored or Computed? | Notes |
   |-----------|------|-------------------|-------|
   | `name` | str | Stored | "Exercise", "Read 30 min" |
   | `description` | str | Stored | Optional longer description |
   | `created_date` | date | Stored | When the habit was created |
   | `target_frequency` | str | Stored | "daily", "weekdays", "3x/week" |
   | `completions` | set of date | Stored | The dates this habit was completed |
   | `current_streak` | int | **Computed** | Calculated from completions |
   | `longest_streak` | int | **Computed** | Calculated from completions |
   | `completion_rate` | float | **Computed** | Calculated from completions + created_date |
   | `total_completions` | int | **Computed** | len(completions) |

   The key principle: **only raw facts are stored.** Everything else is calculated. This is event sourcing — the completions set is the event log, everything else is a derived view.

2. **Why a `set` instead of a `list` for completions?**
   
   Three reasons:
   - **No duplicates.** Adding the same date twice (user marks a habit complete twice in one day) automatically does nothing. With a list, you'd need to check `if date not in completions` manually.
   - **O(1) lookup.** `date(2026, 3, 10) in completions_set` is instant. `date(2026, 3, 10) in completions_list` scans every element. The streak algorithm checks membership for potentially dozens of dates in a loop — set performance matters.
   - **Semantic correctness.** A completion is either done or not done on a given date. There's no concept of "completing a habit 3 times on March 10." A set naturally models this binary state.

   **Gotcha for JSON serialization**: JSON has no set type. When saving, convert to a sorted list of ISO strings: `sorted(d.isoformat() for d in self.completions)`. When loading, convert back: `{date.fromisoformat(s) for s in data["completions"]}`. Note the curly braces `{}` — that's a set comprehension (like a list comprehension but produces a set).

3. **How is completion rate calculated?**
   
   Completion rate = (number of days completed) / (number of days since habit was created) × 100
   
   ```python
   days_since_creation = (date.today() - self.created_date).days + 1  # +1 to include today
   rate = (len(self.completions) / days_since_creation) * 100
   ```
   
   The `+1` is subtle but important. If you created a habit today and completed it today, that's 1 completion in 1 day = 100%. Without `+1`, you'd get 1/0 = division error (or 1/0 days depending on when you measure). Edge cases like this are where bugs hide.
   
   What about the `target_frequency`? If the target is "weekdays" (5 days/week), the denominator should be weekday count, not total days. For "3x/week," the denominator should be `total_weeks * 3`. This is a design decision — for tonight, start with "daily" frequency and compute against total days. You can add frequency-aware rates later.

4. **How does the `zip()` trick work for finding streaks?**
   
   `zip()` combines two iterables element by element:
   ```python
   zip([1, 2, 3], ['a', 'b', 'c'])  →  [(1, 'a'), (2, 'b'), (3, 'c')]
   ```
   
   The trick: zip a sorted list with itself shifted by one position:
   ```python
   dates = [Mar 1, Mar 2, Mar 3, Mar 5, Mar 6]
   
   zip(dates, dates[1:])
   →  [(Mar 1, Mar 2), (Mar 2, Mar 3), (Mar 3, Mar 5), (Mar 5, Mar 6)]
   ```
   
   Now you have pairs of adjacent dates. Check each pair: `(b - a).days == 1` means they're consecutive. This is an elegant way to scan for gaps without nested loops. You can use this to implement `longest_streak` as an alternative to the walk-forward approach described in the lecture above.

5. **What statistics should the system compute?**
   - Current streak (consecutive days ending today/yesterday)
   - Longest streak ever
   - Total completions
   - Completion rate (percentage)
   - Completions this week (Mon–Sun)
   - Most common completion day (using `Counter` on weekday names)
   - Days since last completion

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain these Python concepts:

1. The `set` data structure — how it differs from a list, how to create sets, add to them, check membership with `in`, and why membership checking is O(1) in a set vs O(n) in a list. Also explain set comprehensions.

2. The `zip()` function — how it pairs elements from two iterables, and the pattern of `zip(list, list[1:])` for pairing adjacent elements.

3. How to convert between `date` objects and strings using `isoformat()` and `fromisoformat()`, and why this conversion is necessary for JSON serialization.

Explain each concept clearly with examples. Don't write my program."

### Write Your Code

```python
import json
from datetime import date, timedelta
from collections import Counter
from pathlib import Path

HABITS_FILE = Path("habits.json")


# ──────────────────────────────────────
# DATA MODEL
# ──────────────────────────────────────

class Habit:
    """A habit that tracks completion dates and computes streaks.
    
    Design principle: completions (set of dates) is the source of truth.
    All statistics are derived from completions via @property.
    Nothing computed is ever stored — it's always calculated fresh.
    """

    def __init__(self, name: str, description: str = "",
                 target_frequency: str = "daily",
                 created_date: date = None,
                 completions: set = None):
        self.name = name
        self.description = description
        self.target_frequency = target_frequency
        self.created_date = created_date or date.today()
        self.completions = completions if completions is not None else set()

    def complete_today(self) -> bool:
        """Mark this habit as completed today.
        Returns True if this is a new completion, False if already completed today.
        
        Because completions is a set, adding a duplicate date does nothing.
        But we return a boolean so the UI can give appropriate feedback.
        """
        today = date.today()
        if today in self.completions:
            return False  # Already completed today
        self.completions.add(today)
        return True

    def complete_date(self, target_date: date) -> bool:
        """Mark a specific date as completed (for backfilling missed days)."""
        if target_date in self.completions:
            return False
        if target_date > date.today():
            return False  # Can't complete future dates
        self.completions.add(target_date)
        return True

    # ── Computed Properties ──────────────

    @property
    def current_streak(self) -> int:
        """Consecutive days ending today or yesterday.
        
        Algorithm:
        1. Check if today is in completions → start from today
        2. Else check yesterday → start from yesterday
        3. Else streak = 0
        4. Walk backward counting consecutive days
        """
        if not self.completions:
            return 0
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Determine starting point
        # Walk backward with while loop
        # Return count
        pass  # YOUR IMPLEMENTATION HERE

    @property
    def longest_streak(self) -> int:
        """Longest consecutive run in entire completion history.
        
        Algorithm:
        1. Sort all completion dates
        2. Walk through sorted list tracking current run length
        3. When gap > 1 day, save run length and start new run
        4. Return the maximum run length found
        
        Alternative: use zip(sorted_dates, sorted_dates[1:])
        to pair adjacent dates and check gaps.
        """
        if not self.completions:
            return 0
        
        sorted_dates = sorted(self.completions)
        # Implement the walk-through algorithm
        pass  # YOUR IMPLEMENTATION HERE

    @property
    def total_completions(self) -> int:
        """Total number of days this habit was completed."""
        return len(self.completions)

    @property
    def completion_rate(self) -> float:
        """Percentage of days completed since habit creation.
        
        Note the +1: if created today and completed today,
        that's 1/1 = 100%, not 1/0 = error.
        """
        days_active = (date.today() - self.created_date).days + 1
        if days_active <= 0:
            return 0.0
        return round((len(self.completions) / days_active) * 100, 1)

    @property
    def days_since_last(self) -> int:
        """Days since the most recent completion. -1 if never completed."""
        if not self.completions:
            return -1
        last = max(self.completions)
        return (date.today() - last).days

    @property
    def completions_this_week(self) -> int:
        """Number of completions in the current week (Monday–Sunday)."""
        today = date.today()
        # Monday of this week:
        monday = today - timedelta(days=today.weekday())
        # Count completions from monday through today
        return sum(1 for d in self.completions if monday <= d <= today)

    @property
    def favorite_day(self) -> str:
        """Most common day of week for completions."""
        if not self.completions:
            return "N/A"
        day_names = [d.strftime("%A") for d in self.completions]
        counter = Counter(day_names)
        return counter.most_common(1)[0][0]

    # ── Display ──────────────────────────

    def status_line(self) -> str:
        """Brief one-line status for list views."""
        streak_indicator = "🔥" * min(self.current_streak, 5) if self.current_streak > 0 else "  "
        today_done = "✓" if date.today() in self.completions else " "
        return f"[{today_done}] {self.name:<20} Streak: {self.current_streak:>3}d  {streak_indicator}"

    def full_stats(self) -> str:
        """Detailed statistics display."""
        lines = [
            f"═══ {self.name} ═══",
            f"  {self.description}" if self.description else "",
            f"  Created: {self.created_date.isoformat()}",
            f"  Target: {self.target_frequency}",
            f"",
            f"  Current streak:  {self.current_streak} days",
            f"  Longest streak:  {self.longest_streak} days",
            f"  Total completions: {self.total_completions}",
            f"  Completion rate: {self.completion_rate}%",
            f"  This week:       {self.completions_this_week}",
            f"  Favorite day:    {self.favorite_day}",
            f"  Last completed:  {self.days_since_last} day(s) ago" if self.days_since_last >= 0 else "  Never completed",
        ]
        return "\n".join(line for line in lines if line is not None)

    # ── Serialization ────────────────────

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary.
        
        Completions (set of dates) → sorted list of ISO strings.
        Created date (date object) → ISO string.
        """
        return {
            "name": self.name,
            "description": self.description,
            "target_frequency": self.target_frequency,
            "created_date": self.created_date.isoformat(),
            "completions": sorted(d.isoformat() for d in self.completions)
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Reconstruct a Habit from a dictionary loaded from JSON.
        
        ISO strings → date objects. List → set.
        
        @classmethod means you call this on the CLASS, not an instance:
            habit = Habit.from_dict(some_dict)
        It's a factory method — an alternative constructor.
        """
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            target_frequency=data.get("target_frequency", "daily"),
            created_date=date.fromisoformat(data["created_date"]),
            completions={date.fromisoformat(s) for s in data["completions"]}
            #            ^ set comprehension — curly braces make a set
        )


# ──────────────────────────────────────
# DATA LAYER — persistence
# ──────────────────────────────────────

class HabitStore:
    """Handles saving and loading habits to/from JSON."""

    def __init__(self, filepath: Path = HABITS_FILE):
        self.filepath = filepath

    def load(self) -> list:
        """Load habits from JSON file.
        Returns list of Habit objects, or empty list if file doesn't exist.
        """
        # Handle missing file
        # Read JSON → list of dicts
        # Convert each dict to Habit using Habit.from_dict()
        pass

    def save(self, habits: list) -> None:
        """Save habits to JSON file."""
        # Convert each Habit to dict using .to_dict()
        # Write with json.dump, indent=2
        pass


# ──────────────────────────────────────
# BUSINESS LOGIC
# ──────────────────────────────────────

class HabitManager:
    """Manages the collection of habits."""

    def __init__(self, store: HabitStore = None):
        self.store = store or HabitStore()
        self.habits = self.store.load()

    def add_habit(self, name: str, description: str = "",
                  target_frequency: str = "daily") -> Habit:
        # Check for duplicate names
        # Create Habit, append, save, return it
        pass

    def complete_habit(self, name: str, target_date: date = None) -> bool:
        """Mark a habit as completed. Optionally for a specific past date."""
        # Find habit by name
        # Call complete_today() or complete_date()
        # Save
        pass

    def get_habit(self, name: str):
        """Find a habit by name (case-insensitive)."""
        pass

    def get_all_sorted(self) -> list:
        """Return habits sorted by current streak (highest first)."""
        return sorted(self.habits, key=lambda h: h.current_streak, reverse=True)

    def get_daily_summary(self) -> dict:
        """Summary for today: how many habits, how many completed, which are pending."""
        total = len(self.habits)
        completed_today = sum(1 for h in self.habits if date.today() in h.completions)
        pending = [h.name for h in self.habits if date.today() not in h.completions]
        return {
            "total": total,
            "completed": completed_today,
            "pending": pending,
            "all_done": completed_today == total
        }

    def delete_habit(self, name: str) -> bool:
        # Find and remove, save
        pass


# ──────────────────────────────────────
# PRESENTATION
# ──────────────────────────────────────

class HabitApp:
    def __init__(self):
        self.manager = HabitManager()

    def run(self):
        # Show daily summary on startup
        # Then main menu loop
        self._show_daily_summary()

        while True:
            print("\n--- Habit Tracker ---")
            print("1. Mark habit complete")
            print("2. View all habits")
            print("3. View habit details")
            print("4. Add new habit")
            print("5. Backfill a past date")
            print("6. Daily summary")
            print("7. Delete habit")
            print("8. Quit")

            choice = input("\nChoose: ").strip()
            # Route to methods

    def _show_daily_summary(self):
        """Show on app startup — what's done, what's pending."""
        summary = self.manager.get_daily_summary()
        print(f"\n📊 Today: {summary['completed']}/{summary['total']} habits completed")
        if summary['all_done']:
            print("🎉 All habits completed today!")
        elif summary['pending']:
            print(f"⏳ Pending: {', '.join(summary['pending'])}")

    def mark_complete_prompt(self):
        # Show pending habits
        # User picks one
        # Mark complete, show updated streak

    def view_all(self):
        # Show each habit's status_line()
        # Sorted by streak (highest first)

    def view_details_prompt(self):
        # Ask for habit name
        # Show full_stats()

    def add_habit_prompt(self):
        # Get name, description, frequency
        # Create via manager

    def backfill_prompt(self):
        """Let user mark a past date as completed.
        Useful for: 'I exercised yesterday but forgot to log it.'
        """
        # Ask for habit name and date (YYYY-MM-DD)
        # Parse date, call manager.complete_habit(name, target_date)


if __name__ == "__main__":
    app = HabitApp()
    app.run()
```

### Understanding `@classmethod` — A New OOP Concept

The `Habit.from_dict()` method uses `@classmethod`. This is different from regular methods and `@property`:

```python
class Habit:
    @classmethod
    def from_dict(cls, data: dict):
        return cls(name=data["name"], ...)
```

**Regular method**: First parameter is `self` — the instance. Called on an object: `my_habit.complete_today()`

**`@classmethod`**: First parameter is `cls` — the class itself. Called on the class: `Habit.from_dict(some_dict)`. It's a **factory method** — an alternative way to create instances. Instead of the normal constructor (`Habit(name="Exercise", ...)`), you can create a Habit from a dictionary (`Habit.from_dict(dict_from_json)`).

Why not just put this logic in `__init__`? Because `__init__` already has one clear job: create a Habit from explicit parameters. Overloading it to also accept a dictionary makes the interface confusing. `from_dict` is a separate "doorway" into creating Habit objects — same result, different input format.

You'll see `from_dict`, `from_json`, `from_csv` classmethods throughout professional Python code. They're the standard pattern for creating objects from serialized data.

### Testing Your Streak Logic

This is the most important thing to test. Create a habit and add specific completion dates to verify your algorithms:

```python
# In a Python shell or test script:
from datetime import date, timedelta

h = Habit("Test")
today = date.today()

# Add a 5-day streak ending yesterday
for i in range(5, 0, -1):
    h.completions.add(today - timedelta(days=i))

print(h.current_streak)   # Should be 5 (if today not yet completed)
                           # OR 0 if your algorithm requires today

h.complete_today()
print(h.current_streak)   # Should be 6

# Add a gap, then older streak
h.completions.add(today - timedelta(days=10))
h.completions.add(today - timedelta(days=11))
h.completions.add(today - timedelta(days=12))

print(h.longest_streak)   # Should be 6 (the current one, not the old 3-day one)
```

If your streaks don't match, debug by printing the sorted completions and walking through the algorithm by hand.

### Ask GLM-4.7-Flash After Coding — The Review Step

Select all code → `Cmd+L` →

"Review this habit tracker as a senior developer. Specifically evaluate:

1. Is my streak algorithm correct? Walk through an example with a gap in completions and verify the logic.
2. Am I using `set` correctly for completions? Are there any places where I accidentally treat it as a list?
3. Are my `@property` decorators used appropriately — are all computed values truly derived from the completions set?
4. Is the `@classmethod from_dict` pattern used correctly? Is my set comprehension for deserializing dates right?
5. Is my date arithmetic correct? Are there edge cases I'm missing (habit created today, empty completions, future dates)?
6. What would a senior developer change about this code?"

**Read the suggestions. Implement the changes yourself. Commit the improved version.**

```bash
git add . && git commit -m "Project 17: habit_tracker.py — date arithmetic, streaks, set, @property, @classmethod, event sourcing"
```

---

## CLOSING LECTURE: TIME CHANGES EVERYTHING

Today you learned that adding time as a dimension transforms the nature of your data. A recipe is static. A habit is dynamic. Static data needs storage and retrieval. Dynamic data needs storage, retrieval, *and temporal reasoning.*

The patterns from today show up everywhere in professional software:

- **Event sourcing** (store events, derive state) is the architecture behind Kafka event streams, Git version history, and blockchain ledgers. You've been working with event-driven systems professionally — today you implemented the same principle in application code.

- **Computed properties** (derive, don't store) prevent stale data bugs and reduce storage complexity. In your future AI systems, a document's "relevance score" should be computed fresh at query time from the embeddings, not stored when the document was ingested.

- **Date arithmetic** (date ± timedelta, date - date) is how every scheduling system, reporting dashboard, and analytics pipeline reasons about time. The streak algorithm you wrote today is structurally identical to "calculate user retention" or "find gaps in sensor data" — problems you'll solve for clients.

And a meta-lesson: **the hardest part of today wasn't the Python syntax.** It was the streak algorithm — pure logic about how consecutive days work. The syntax (`date`, `timedelta`, `set`, `@property`) is just the vocabulary. The algorithm is the thinking. AI can generate the syntax. It struggles with the logic. That's your value.

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 10
- [ ] Day number: 10
- [ ] Hours coded: 2
- [ ] Projects completed: 1 (habit_tracker)
- [ ] Key concepts: date, timedelta, date arithmetic, set vs list, @property, @classmethod, event sourcing, streak algorithms
- [ ] AI review: What was the most useful suggestion? What change did you make?
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 11 — Wednesday):
- **Commute**: CS50 Week 3 (Algorithms) or Talk Python To Me
- **Evening (7:00–9:00 PM)**: `inventory_system.py`
  - Product management with low-stock alerts, reorder points
  - **OOP focus**: Objects that enforce business rules — a Product rejects invalid stock levels, an Inventory triggers alerts based on thresholds
  - **New concepts**: Comparison operators on objects (`__lt__`, `__eq__`), more advanced sorting and filtering

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

1. **`date` vs `datetime` vs `timedelta`** — when to use each, and why `date` is preferred when you don't need time-of-day
2. **The four date arithmetic operations** — date - date = timedelta, date + timedelta = date, timedelta + timedelta = timedelta, date compared to date = boolean
3. **`date.fromisoformat()` / `.isoformat()`** — converting between date objects and strings for JSON serialization
4. **`set` data structure** — uniqueness guarantee, O(1) membership testing, set comprehensions with `{}`
5. **Why sets matter for performance** — O(1) vs O(n) lookup in a loop changes algorithm viability
6. **`@property` in depth** — computed values that look like attributes, why derived values should be computed not stored
7. **`@classmethod` and factory methods** — alternative constructors like `Habit.from_dict()`, the difference between `self` and `cls`
8. **Event sourcing pattern** — store raw events (completions), derive all state (streaks, rates) from those events
9. **Streak algorithm** — walking backward from today counting consecutive days, using `(date_b - date_a).days == 1` for gap detection
10. **`zip(list, list[1:])` pattern** — pairing adjacent elements for comparing consecutive items
11. **`collections.Counter`** — counting occurrences, `most_common()` for finding the top item

---

**Day 10 of 365. Time is now a dimension of your data. Your objects have memory. They know their own history.** 🚀
