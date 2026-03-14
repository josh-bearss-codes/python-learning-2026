# DAY 14 — Saturday, March 14, 2026
## Lecture: Making Data Visible — Visualization, the Observer Pattern, and Objects That Draw Themselves

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI reviews more aggressively  
**Morning Session**: 8:00–11:00 AM (3 hours) — Build 1 substantial project  
**Today's theme**: The leap from data-as-numbers to data-as-pictures, and the OOP patterns that make visualization clean

---

## OPENING LECTURE: WHY VISUALIZE?

You've spent 13 days building programs that process data and print text. Text is precise. You can see exact numbers, exact dates, exact calculations. But text has a fundamental limitation: **the human brain cannot detect patterns in tables of numbers.**

Look at this data:

```
Week 1:  Mon 3, Tue 3, Wed 0, Thu 3, Fri 3, Sat 3, Sun 3
Week 2:  Mon 3, Tue 3, Wed 3, Thu 3, Fri 0, Sat 3, Sun 3
Week 3:  Mon 3, Tue 0, Wed 3, Thu 3, Fri 3, Sat 3, Sun 3
Week 4:  Mon 3, Tue 3, Wed 3, Thu 0, Fri 3, Sat 3, Sun 3
```

Those are sets logged per workout day over four weeks. Can you immediately tell whether the user is improving? Which days they tend to skip? Whether their volume is trending up or down? It takes deliberate mental effort to parse those numbers into meaning.

Now imagine a line chart where the X-axis is time and the Y-axis is total weekly sets. Or a bar chart showing sets per exercise over the month. Or a heatmap showing which days of the week are most consistent. The same data becomes instantly readable. Patterns leap out. Trends become obvious. Missing days stand out visually.

This is why visualization matters:

1. **For yourself**: Your workout data becomes motivating when you can *see* your progress. A chart showing your bench press going from 135lbs to 185lbs over three months is more powerful than a JSON file saying the same thing.

2. **For clients**: When you build AI systems for regulated industries, dashboards and charts are how you communicate results to non-technical stakeholders. A lawyer doesn't want to see a vector similarity score of 0.87 — they want a chart showing which documents are most relevant to their case.

3. **For data engineering**: Every data pipeline needs observability. Charts showing throughput, error rates, and latency over time are the standard way to monitor pipeline health. You'll build these dashboards in Months 4–6.

Today you learn `matplotlib` — Python's foundational visualization library. It's not the prettiest (libraries like `plotly` and `seaborn` make better-looking charts), but it's the most widely used, the most well-documented, and the one every other library builds on. Understanding matplotlib gives you the mental model for all Python visualization.

---

## LECTURE: MATPLOTLIB'S MENTAL MODEL — FIGURES, AXES, AND THE ARTIST METAPHOR

Matplotlib uses a metaphor that confuses most beginners because it doesn't match how you'd naturally think about drawing a chart. Let me demystify it.

### The Three Layers

Think of matplotlib like a physical painting:

```
┌─────────────────────────────────────────────────┐
│                    FIGURE                        │  ← The canvas/paper
│                                                  │
│  ┌────────────────────┐  ┌────────────────────┐ │
│  │       AXES 1       │  │       AXES 2       │ │  ← Individual plots
│  │                    │  │                    │ │     (you can have many)
│  │  ╭───────────╮     │  │  █ █               │ │
│  │  │           ╰──╮  │  │  █ █ █             │ │  ← Artists
│  │  │              │  │  │  █ █ █ █           │ │     (lines, bars, text)
│  │  ╰──────────────╯  │  │  █ █ █ █ █         │ │
│  │  (a line chart)    │  │  (a bar chart)     │ │
│  └────────────────────┘  └────────────────────┘ │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Figure**: The entire image. The canvas. One figure can contain multiple plots. When you save a PNG, you save the figure.

**Axes**: One individual plot within the figure. Despite the confusing name, "Axes" means "one chart" — not "the X and Y axis lines." A figure with two side-by-side charts has two Axes objects.

**Artists**: Everything drawn on an Axes — lines, bars, text labels, legends. These are the actual visual elements.

### The Two APIs

Matplotlib has two ways to create charts. This is the #1 source of confusion for beginners, because tutorials mix them:

**The pyplot API (state-based, quick):**

```python
import matplotlib.pyplot as plt

plt.plot([1, 2, 3, 4], [10, 20, 25, 30])
plt.title("My Chart")
plt.xlabel("Week")
plt.ylabel("Sets")
plt.savefig("chart.png")
plt.close()
```

This is quick and works for simple charts. But it uses hidden global state — `plt` remembers which figure and axes you're working on. This breaks down when you have multiple charts or when your code is inside classes.

**The object-oriented API (explicit, professional):**

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()           # Create figure + axes explicitly
ax.plot([1, 2, 3, 4], [10, 20, 25, 30])    # Draw on the specific axes
ax.set_title("My Chart")           # Set title on the specific axes
ax.set_xlabel("Week")
ax.set_ylabel("Sets")
fig.savefig("chart.png")           # Save the specific figure
plt.close(fig)                     # Clean up the specific figure
```

**Always use the object-oriented API.** It's more explicit, works inside classes, and doesn't rely on hidden state. Every professional Python developer and data scientist uses this form.

### The Key Pattern: `fig, ax = plt.subplots()`

This one line does three things:
1. Creates a new Figure object (`fig`)
2. Creates a new Axes object inside that figure (`ax`)
3. Returns both so you can work with them explicitly

For multiple charts:

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
# Creates a 2×2 grid of charts
# axes is a 2D array: axes[0][0], axes[0][1], axes[1][0], axes[1][1]

axes[0][0].plot(...)        # Top-left chart
axes[0][1].bar(...)         # Top-right chart
axes[1][0].scatter(...)     # Bottom-left chart
axes[1][1].pie(...)         # Bottom-right chart
```

### Saving vs. Showing

```python
# Save to file (what you want for automated reports)
fig.savefig("chart.png", dpi=150, bbox_inches='tight')
# dpi=150 → resolution (higher = sharper, larger file)
# bbox_inches='tight' → removes excess whitespace

# Show interactively (what you want during development)
plt.show()
# This opens a window — only works if you have a display
# On a server or in a script, always use savefig

# IMPORTANT: always close figures to free memory
plt.close(fig)
```

### The Five Chart Types You Need Today

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

# 1. LINE CHART — trends over time
ax.plot(dates, values, marker='o', linewidth=2, color='#2196F3', label='Bench Press')
# marker='o' puts dots at data points
# label='...' is used by ax.legend()

# 2. BAR CHART — comparing categories
ax.bar(categories, values, color=['#4CAF50', '#2196F3', '#FF9800'])
# Can also use barh() for horizontal bars

# 3. SCATTER PLOT — relationship between two variables
ax.scatter(x_values, y_values, alpha=0.6, s=50)
# alpha = transparency (0-1)
# s = dot size

# 4. PIE CHART — parts of a whole (use sparingly — bars are usually better)
ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
# autopct formats the percentage labels

# 5. HEATMAP (via imshow) — 2D data like weekly schedules
ax.imshow(data_2d, cmap='YlOrRd', aspect='auto')
# cmap = color map (YlOrRd = yellow-orange-red gradient)
```

### Common Formatting

```python
ax.set_title("Monthly Progress", fontsize=14, fontweight='bold')
ax.set_xlabel("Date", fontsize=11)
ax.set_ylabel("Weight (lbs)", fontsize=11)
ax.legend(loc='upper left')                  # Show legend
ax.grid(True, alpha=0.3)                     # Light grid lines
ax.tick_params(axis='x', rotation=45)        # Rotate x-axis labels

fig.tight_layout()                           # Prevent label overlap
```

---

## LECTURE: OBJECTS THAT RENDER THEMSELVES — THE CHART-GENERATION PATTERN

Here's the OOP design question for today: **who is responsible for generating charts?**

You could put all chart code in the presentation layer. That works for one or two charts. But when your system generates 5-10 different visualizations, the presentation class becomes enormous and tangled.

The better pattern: **objects generate their own visual representations.** Just like `__str__` lets an object define how it appears as text, a `plot()` or `generate_chart()` method lets an object define how it appears as a picture.

```python
class ExerciseHistory:
    """Tracks all sessions for one exercise over time."""
    
    def __init__(self, name, sessions):
        self.name = name
        self.sessions = sessions   # list of (date, sets, reps, weight)
    
    def plot_progress(self, ax):
        """Draw this exercise's progress on the given axes.
        
        The object knows its own data and how to visualize it.
        The caller provides the axes — the canvas to draw on.
        
        This separation is powerful: the object controls WHAT is drawn,
        the caller controls WHERE it's drawn (which figure, which subplot,
        what size). Neither needs to know about the other's concerns.
        """
        dates = [s[0] for s in self.sessions]
        weights = [s[3] for s in self.sessions]
        ax.plot(dates, weights, marker='o', label=self.name)
        ax.set_ylabel("Weight (lbs)")
        ax.legend()
```

The key insight: the method takes an `ax` parameter (the Axes to draw on) rather than creating its own figure. This means the caller can:
- Put one exercise on one chart
- Put three exercises on three subplots in one figure
- Compare two exercises on the same axes with different colors

The object provides the visualization logic. The caller provides the layout context. This is **separation of concerns** applied to visualization.

### Why `ax` Gets Passed In (Dependency Injection for Charts)

This is the same dependency injection principle from Day 7. The `BudgetManager` received its `BudgetData` from the caller rather than creating its own. The `ExerciseHistory.plot_progress()` receives its `ax` from the caller rather than creating its own figure.

Why? Because the object doesn't know the layout context. Maybe you want one chart per page. Maybe you want a 2×3 grid. Maybe you want to overlay two exercises on the same axes. The object can't predict this. So it draws on whatever axes it receives, and the caller decides the layout.

```python
# Caller decides: one chart
fig, ax = plt.subplots(figsize=(10, 6))
bench_press.plot_progress(ax)
fig.savefig("bench_press.png")

# Caller decides: three charts in a row
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
bench_press.plot_progress(axes[0])
squat.plot_progress(axes[1])
deadlift.plot_progress(axes[2])
fig.savefig("all_lifts.png")

# Caller decides: overlaid on same axes
fig, ax = plt.subplots(figsize=(10, 6))
bench_press.plot_progress(ax)
squat.plot_progress(ax)    # Same axes — both lines appear together
ax.set_title("Bench Press vs Squat")
fig.savefig("comparison.png")
```

One method on the object, three completely different visual layouts. The object's code didn't change at all.

---

## LECTURE: INSTALLING MATPLOTLIB

Before you code, you need to install matplotlib. It's not in the standard library:

```bash
# Make sure your venv is active (you should see (dev) in your prompt)
pip install matplotlib
```

Verify it works:

```python
python3 -c "import matplotlib; print(matplotlib.__version__)"
```

If you get a version number (3.8+), you're good.

### Saving Charts Without a Display

On your Mac Studio, `plt.show()` will open a window — that works fine for development. But when generating charts programmatically (like in today's project), always use `fig.savefig()` to write to a file. This works regardless of whether a display is available:

```python
import matplotlib
matplotlib.use('Agg')    # Use non-interactive backend — no display needed
import matplotlib.pyplot as plt
```

The `'Agg'` backend renders to files without trying to open a window. Put this at the top of your script if you want to generate charts in a script or on a server. For today's interactive work, you can skip this line and use `plt.show()` to preview your charts during development.

---

## PROJECT 21: `workout_logger.py` (~2.5 hours)

### The Problem

Build a workout tracking system. The user logs exercise sessions (exercise name, sets, reps, weight, date). The system stores the data, calculates statistics (personal records, volume over time, frequency), and generates visual charts showing progress. Charts are saved as PNG files.

This is the household use case from your life — you and your household lift weights regularly. Build something you'd actually use.

### Concepts to Learn and Use

- **`matplotlib`** — line charts, bar charts, subplots, formatting, saving to PNG
- **Objects that render themselves** — `plot_progress(ax)` method pattern
- **Dependency injection for visualization** — objects receive `ax`, callers control layout
- **Data aggregation** — grouping sessions by week/month, calculating totals and averages
- **`defaultdict` with list** — `defaultdict(list)` for grouping sessions by exercise
- **`max()` with `key`** — finding personal records: `max(sessions, key=lambda s: s.weight)`
- **Date grouping** — `date.isocalendar()` gives (year, week_number, weekday) for weekly grouping
- **`@property` for computed stats** — total volume, session count, personal records
- **f-string formatting for weight** — `f"{weight:.1f} lbs"` for clean decimal display

### Reference Material

- Matplotlib tutorials: https://matplotlib.org/stable/tutorials/index.html
- Matplotlib pyplot reference: https://matplotlib.org/stable/api/pyplot_summary.html
- Real Python — matplotlib guide: https://realpython.com/python-matplotlib-guide/
- Python docs — `date.isocalendar()`: https://docs.python.org/3/library/datetime.html#datetime.date.isocalendar

### Design Questions (Answer These BEFORE You Code)

1. **What is the data model?**

   An individual session record needs: exercise name, date, number of sets, reps per set, and weight used. But real workouts have multiple exercises per session. So the hierarchy is:
   
   - A **WorkoutSession** represents one gym visit: a date and a list of exercise entries
   - An **ExerciseEntry** represents one exercise within a session: exercise name, sets, reps, weight
   
   Alternatively, you can flatten this: every entry is independent with its own date and exercise name. The flattened approach is simpler for charting (no nested objects to traverse). For tonight, **use the flat approach** — each entry is self-contained. You can always add the WorkoutSession grouping later.

2. **What charts should the system generate?**

   | Chart | Type | What It Shows |
   |-------|------|--------------|
   | Exercise progress | Line chart | Weight over time for one exercise (dates on X, weight on Y) |
   | Weekly volume | Bar chart | Total sets × reps × weight per week |
   | Exercise frequency | Bar chart | How many sessions per exercise (which exercises you do most) |
   | Workout heatmap | Heatmap/calendar | Which days of the week you train (Mon-Sun) |
   | Personal records | Horizontal bar | Heaviest weight per exercise |
   | Multi-exercise comparison | Multi-line chart | Progress lines for 2-3 exercises overlaid |

   You don't need all of these tonight. Start with 3-4 and add more if time permits. The exercise progress line chart and the weekly volume bar chart are the most useful.

3. **Where do charts get saved?**

   Create a `charts/` directory. Each chart saves to a descriptive filename:
   ```
   charts/bench_press_progress.png
   charts/weekly_volume.png
   charts/exercise_frequency.png
   charts/personal_records.png
   ```

4. **How does the `plot_progress(ax)` pattern work?**

   Each visualization method lives on the class that owns the data. The `ExerciseLog` (which tracks one exercise's history) has a `plot_progress(ax)` method. The `WorkoutStats` class (which aggregates across exercises) has `plot_weekly_volume(ax)` and `plot_frequency(ax)` methods. The presentation layer creates figures, passes axes to these methods, and saves the results.

5. **What does `isocalendar()` give you?**

   ```python
   from datetime import date
   today = date(2026, 3, 14)
   year, week, weekday = today.isocalendar()
   # year=2026, week=11, weekday=6 (Saturday)
   # weekday: 1=Monday, 7=Sunday
   ```
   
   This is perfect for grouping sessions by week: use `(year, week)` as the grouping key. Two sessions in the same ISO week get grouped together regardless of which day they fall on.

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain these Python concepts:

1. Matplotlib's object-oriented API — how `fig, ax = plt.subplots()` works, the difference between Figure and Axes, and how to create multi-chart layouts with `plt.subplots(2, 2)`. Show a simple example of creating a line chart and saving it to a PNG file.

2. The pattern of passing `ax` to a method for drawing — why an object's `plot_progress(ax)` should receive the axes rather than creating its own figure. Explain how this enables different layouts from the same visualization method.

3. `date.isocalendar()` — what it returns and how to use the (year, week_number) tuple as a grouping key for weekly aggregation.

Explain each concept clearly with examples. Don't write my program."

### Skeletal Structure

```python
import json
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving charts
import matplotlib.pyplot as plt
from datetime import date, timedelta
from collections import defaultdict
from pathlib import Path
from functools import total_ordering

DATA_FILE = Path("workouts.json")
CHARTS_DIR = Path("charts")


# ──────────────────────────────────────
# DATA MODEL
# ──────────────────────────────────────

@total_ordering
class ExerciseEntry:
    """One exercise performed on one date.
    
    Flat model: each entry is self-contained with its own date.
    This makes charting simple — no nested session objects to traverse.
    
    Natural ordering: by date, then by exercise name.
    This means sorted(entries) gives chronological order.
    """

    def __init__(self, exercise: str, date_performed: date,
                 sets: int, reps: int, weight: float):
        self.exercise = exercise
        self.date_performed = date_performed
        self.sets = sets
        self.reps = reps
        self.weight = weight

    @property
    def volume(self) -> float:
        """Total volume = sets × reps × weight.
        This is the standard measure of workout load.
        """
        # YOUR IMPLEMENTATION

    def __eq__(self, other) -> bool:
        # Equal if same exercise, date, sets, reps, weight
        # (exact duplicate detection)

    def __lt__(self, other) -> bool:
        # Sort by date first, then exercise name

    def __hash__(self) -> int:
        # Hash on (exercise, date_performed, sets, reps, weight)

    def __repr__(self) -> str:
        # "ExerciseEntry('Bench Press', 2026-03-14, 3×10@185lbs)"

    def __str__(self) -> str:
        # "Mar 14: Bench Press — 3 sets × 10 reps @ 185.0 lbs (vol: 5550.0)"

    def to_dict(self) -> dict:
        # JSON serialization — date as ISO string

    @classmethod
    def from_dict(cls, data: dict):
        # JSON deserialization — parse ISO date string


# ──────────────────────────────────────
# ANALYSIS — per-exercise statistics
# ──────────────────────────────────────

class ExerciseLog:
    """All entries for ONE exercise across time.
    
    This class answers: 'How is my Bench Press progressing?'
    It holds a filtered subset of entries and computes exercise-specific stats.
    
    VISUALIZATION: This class knows how to draw its own progress chart.
    The plot_progress(ax) method receives axes from the caller.
    """

    def __init__(self, exercise_name: str, entries: list):
        self.exercise_name = exercise_name
        self.entries = sorted(entries)  # Chronological via __lt__

    @property
    def personal_record(self) -> float:
        """Heaviest weight ever used for this exercise."""
        # max() with key=lambda

    @property
    def total_volume(self) -> float:
        """Sum of volume across all sessions."""
        # sum() with generator

    @property
    def session_count(self) -> int:
        """Number of sessions (unique dates) for this exercise."""
        # len(set(dates))

    @property
    def average_weight(self) -> float:
        """Average weight across all entries."""

    @property
    def recent_trend(self) -> str:
        """Is the weight trending up, down, or flat over last 4 sessions?
        Compare average of last 2 sessions vs average of 2 before that.
        """
        # Split entries into recent vs earlier
        # Compare averages
        # Return "↑ improving", "↓ declining", or "→ steady"

    def plot_progress(self, ax) -> None:
        """Draw a line chart of weight over time on the given axes.
        
        This is the 'objects render themselves' pattern.
        The object knows its data and how to visualize it.
        The caller controls WHERE this chart appears.
        
        Includes:
          - Line connecting data points
          - Dots at each session
          - Horizontal dashed line at personal record
          - Title, labels, grid
        """
        dates = [e.date_performed for e in self.entries]
        weights = [e.weight for e in self.entries]

        ax.plot(dates, weights, marker='o', linewidth=2, label=self.exercise_name)
        ax.axhline(y=self.personal_record, color='red', linestyle='--',
                    alpha=0.5, label=f'PR: {self.personal_record:.1f} lbs')
        ax.set_title(f"{self.exercise_name} Progress")
        ax.set_xlabel("Date")
        ax.set_ylabel("Weight (lbs)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)

    def __str__(self) -> str:
        # "Bench Press: 12 sessions, PR 185.0 lbs, avg 165.0 lbs, trend ↑"


# ──────────────────────────────────────
# ANALYSIS — cross-exercise statistics
# ──────────────────────────────────────

class WorkoutStats:
    """Aggregate statistics across ALL exercises.
    
    This class answers: 'How is my overall training going?'
    It operates on the full list of entries and computes cross-exercise metrics.
    
    VISUALIZATION: Charts that compare across exercises or show totals.
    """

    def __init__(self, entries: list):
        self.entries = sorted(entries)
        self._by_exercise = self._group_by_exercise()

    def _group_by_exercise(self) -> dict:
        """Group entries by exercise name.
        Returns: {exercise_name: ExerciseLog}
        
        Uses defaultdict(list) to collect entries, then wraps in ExerciseLog.
        """
        grouped = defaultdict(list)
        # Group entries
        # Return {name: ExerciseLog(name, entries)}

    def get_exercise_log(self, exercise_name: str):
        """Get the ExerciseLog for a specific exercise, or None."""

    @property
    def exercise_names(self) -> list:
        """All unique exercise names, sorted alphabetically."""

    @property
    def total_sessions(self) -> int:
        """Total number of unique workout dates."""
        # len(set(e.date_performed for e in self.entries))

    @property
    def total_volume(self) -> float:
        """Total volume across all exercises."""

    def get_weekly_volume(self) -> dict:
        """Total volume per ISO week.
        Returns: {(year, week): total_volume}
        
        Uses date.isocalendar() to get (year, week_number, weekday).
        Groups by (year, week_number) and sums volume within each group.
        """
        weekly = defaultdict(float)
        for entry in self.entries:
            year, week, _ = entry.date_performed.isocalendar()
            weekly[(year, week)] += entry.volume
        return dict(weekly)

    def get_day_of_week_frequency(self) -> dict:
        """How many sessions on each day of the week.
        Returns: {"Monday": 5, "Tuesday": 3, ...}
        """
        # Use Counter on weekday names

    def plot_weekly_volume(self, ax) -> None:
        """Bar chart of total volume per week."""
        weekly = self.get_weekly_volume()
        # Sort by week
        # Create labels like "Wk 10", "Wk 11"
        # Draw bar chart

    def plot_exercise_frequency(self, ax) -> None:
        """Horizontal bar chart showing session count per exercise."""
        # Get session_count from each ExerciseLog
        # Sort by frequency
        # Draw horizontal bar chart

    def plot_personal_records(self, ax) -> None:
        """Horizontal bar chart of personal record weight per exercise."""
        # Get PR from each ExerciseLog
        # Sort by weight
        # Draw horizontal bar chart

    def plot_day_heatmap(self, ax) -> None:
        """Bar chart showing training frequency by day of week."""
        # Get day frequency
        # Draw bar chart Mon-Sun


# ──────────────────────────────────────
# DATA LAYER — persistence
# ──────────────────────────────────────

class WorkoutStore:
    """JSON persistence for workout entries."""

    def __init__(self, filepath: Path = DATA_FILE):
        self.filepath = filepath

    def load(self) -> list:
        """Load entries from JSON. Returns list of ExerciseEntry."""

    def save(self, entries: list) -> None:
        """Save all entries to JSON."""


# ──────────────────────────────────────
# BUSINESS LOGIC
# ──────────────────────────────────────

class WorkoutManager:
    """Manages workout entries and chart generation."""

    def __init__(self, store: WorkoutStore = None):
        self.store = store or WorkoutStore()
        self.entries = self.store.load()

    def add_entry(self, exercise: str, sets: int, reps: int, weight: float,
                  entry_date: date = None) -> ExerciseEntry:
        """Log a new exercise entry. Defaults to today's date."""
        # Create ExerciseEntry, append, save, return

    def get_stats(self) -> WorkoutStats:
        """Get aggregate statistics across all entries."""
        return WorkoutStats(self.entries)

    def get_exercise_log(self, exercise_name: str):
        """Get log for a specific exercise."""
        # Filter entries, create ExerciseLog

    def get_exercise_names(self) -> list:
        """All unique exercise names."""

    def generate_all_charts(self) -> list:
        """Generate all charts and save to charts/ directory.
        
        This is the CALLER that controls layout.
        It creates figures, passes axes to visualization methods,
        and saves the results.
        
        Returns list of saved file paths.
        """
        CHARTS_DIR.mkdir(exist_ok=True)
        saved = []
        stats = self.get_stats()

        # Chart 1: Individual exercise progress (one chart per exercise)
        for exercise_name in stats.exercise_names:
            log = stats.get_exercise_log(exercise_name)
            if log and log.session_count >= 2:  # Need at least 2 points for a line
                fig, ax = plt.subplots(figsize=(10, 6))
                log.plot_progress(ax)
                fig.tight_layout()
                filename = f"{exercise_name.lower().replace(' ', '_')}_progress.png"
                fig.savefig(CHARTS_DIR / filename, dpi=150, bbox_inches='tight')
                plt.close(fig)
                saved.append(filename)

        # Chart 2: Weekly volume bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        stats.plot_weekly_volume(ax)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "weekly_volume.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved.append("weekly_volume.png")

        # Chart 3: Exercise frequency
        fig, ax = plt.subplots(figsize=(10, 6))
        stats.plot_exercise_frequency(ax)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "exercise_frequency.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved.append("exercise_frequency.png")

        # Chart 4: Personal records
        fig, ax = plt.subplots(figsize=(10, 6))
        stats.plot_personal_records(ax)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "personal_records.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved.append("personal_records.png")

        # Chart 5: Multi-exercise comparison (top 3 exercises on one chart)
        top_exercises = sorted(stats.exercise_names,
                              key=lambda n: stats.get_exercise_log(n).session_count,
                              reverse=True)[:3]
        if len(top_exercises) >= 2:
            fig, ax = plt.subplots(figsize=(12, 6))
            for name in top_exercises:
                stats.get_exercise_log(name).plot_progress(ax)
            ax.set_title("Top Exercises — Progress Comparison")
            fig.tight_layout()
            fig.savefig(CHARTS_DIR / "comparison.png", dpi=150, bbox_inches='tight')
            plt.close(fig)
            saved.append("comparison.png")

        return saved


# ──────────────────────────────────────
# PRESENTATION
# ──────────────────────────────────────

class WorkoutApp:
    def __init__(self):
        self.manager = WorkoutManager()

    def run(self):
        while True:
            print("\n--- Workout Logger ---")
            print("1. Log exercise")
            print("2. View exercise history")
            print("3. View exercise stats")
            print("4. View overall stats")
            print("5. Generate progress charts")
            print("6. Log a past workout (backfill)")
            print("7. Quit")

            choice = input("\nChoose: ").strip()
            # Route to methods

    def log_exercise_prompt(self):
        """Get exercise details from user and log them.
        
        Tip for good UX: remember the last exercise name and offer it
        as a default. Gym sessions usually repeat the same exercises.
        """
        # Get exercise name, sets, reps, weight
        # Validate all inputs (positive numbers)
        # Add entry, show confirmation with volume

    def view_history(self):
        """Show all entries for one exercise, chronologically."""
        # List available exercises
        # User picks one
        # Display sorted entries with __str__

    def view_exercise_stats(self):
        """Show detailed stats for one exercise."""
        # List exercises
        # User picks one
        # Display: PR, average weight, total volume, session count, trend

    def view_overall_stats(self):
        """Show cross-exercise summary."""
        # Total sessions, total volume, exercises tracked
        # Display each exercise's one-line summary

    def generate_charts(self):
        """Generate all charts and report which files were saved."""
        print("Generating charts...")
        saved = self.manager.generate_all_charts()
        print(f"\n📊 {len(saved)} charts saved to {CHARTS_DIR}/:")
        for filename in saved:
            print(f"   {filename}")

    def log_past_workout(self):
        """Log an exercise for a past date (backfill).
        Uses the same date parsing pattern from the habit tracker.
        """
        # Get exercise details + date in YYYY-MM-DD format
        # Parse with date.fromisoformat()
        # Add entry for that date


if __name__ == "__main__":
    app = WorkoutApp()
    app.run()
```

### Seed Data for Testing

After building the app, add realistic data to test your charts. Log at least 3-4 weeks of workouts across 3+ exercises. Here's a quick way to seed data for testing (run in Python shell or add a `seed_data()` method):

```python
# Example: 4 weeks of bench press, progressing weight
entries_to_add = [
    ("Bench Press", "2026-02-17", 3, 10, 135),
    ("Bench Press", "2026-02-20", 3, 10, 140),
    ("Bench Press", "2026-02-24", 4, 8, 145),
    ("Bench Press", "2026-02-27", 4, 8, 145),
    ("Bench Press", "2026-03-03", 4, 8, 150),
    ("Bench Press", "2026-03-06", 3, 10, 155),
    ("Bench Press", "2026-03-10", 4, 8, 155),
    ("Bench Press", "2026-03-13", 4, 6, 160),
    ("Squat", "2026-02-18", 3, 8, 185),
    ("Squat", "2026-02-21", 4, 8, 185),
    ("Squat", "2026-02-25", 4, 6, 195),
    ("Squat", "2026-03-01", 4, 8, 195),
    ("Squat", "2026-03-04", 4, 6, 205),
    ("Squat", "2026-03-08", 3, 8, 205),
    ("Squat", "2026-03-11", 4, 6, 210),
    ("Deadlift", "2026-02-19", 3, 5, 225),
    ("Deadlift", "2026-02-26", 3, 5, 235),
    ("Deadlift", "2026-03-05", 3, 5, 245),
    ("Deadlift", "2026-03-12", 3, 3, 255),
]
```

After generating charts, open the `charts/` directory and verify:
- Bench press line trends upward (135 → 160)
- Squat line trends upward (185 → 210)  
- Deadlift line trends upward (225 → 255)
- Weekly volume bars show consistency
- Personal records bar: Deadlift highest (255), Squat (210), Bench (160)

### Ask GLM-4.7-Flash After Coding — The Review Step

Select all code → `Cmd+L` →

"Review this workout logger as a senior developer. Specifically evaluate:

1. Is my chart generation using matplotlib's object-oriented API correctly (fig, ax = plt.subplots, methods on ax, fig.savefig)?
2. Is the pattern of `plot_progress(ax)` on ExerciseLog a good design? Does passing axes in enable flexible layouts?
3. Am I closing figures properly with `plt.close(fig)` to prevent memory leaks?
4. Is my data model (flat ExerciseEntry rather than nested WorkoutSession) appropriate? What would I gain or lose by nesting?
5. Is my weekly volume grouping using `isocalendar()` correct?
6. Are my chart formatting choices good? What would make the charts more readable?
7. What would a senior developer change?"

**Read the suggestions. Implement the changes yourself. Commit the improved version.**

```bash
git add . && git commit -m "Project 21: workout_logger.py — matplotlib, objects render themselves, data visualization, weekly aggregation"
```

---

## CLOSING LECTURE: DATA BECOMES VISIBLE

Today marked a transition. For 13 days, your programs produced text — numbers, tables, formatted cards. Today your programs produced *pictures*. A line chart of your bench press progress. A bar chart of weekly volume. Visual artifacts that communicate at a glance what tables of numbers cannot.

The OOP pattern you learned — objects that render themselves via `plot_progress(ax)` — will be essential in your AI work. When you build dashboards for clients in Month 6+, every data component will have a `render()` or `plot()` method. The RAG system's retrieval results will generate a relevance chart. The pipeline monitor will generate a throughput graph. The pattern is always the same: the object knows its data and how to visualize it, the caller controls the layout context.

Tomorrow is the last Foundation phase project: `reading_list.py`. It's the Week 2 capstone that pulls together everything — composition, serialization, comparison operators, sorting, filtering, search, and formatted output. Then Monday begins Week 3: the shift to AI-directed development.

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 14
- [ ] Day number: 14
- [ ] Hours coded: 3
- [ ] Projects completed: 1 (workout_logger)
- [ ] Key concepts: matplotlib OOP API, fig/ax/subplots, objects that render themselves (plot_progress(ax)), dependency injection for visualization, isocalendar for weekly grouping, savefig vs show, chart types (line, bar, hbar)
- [ ] AI review: What was the most useful suggestion? What change did you make?
- [ ] Generated charts look correct? Which is your favorite? ___
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 15 — Sunday, Week 2 Capstone):
- **Morning (8:00–11:00 AM)**: 3 hours
  - `reading_list.py` — Comprehensive book tracker with ratings, recommendations, and export
  - **Week 2 capstone** — pulls together composition, serialization, comparison operators, sorting, filtering, search, formatted output
  - **Afternoon**: Week 2 review and reflection — preparing for the Week 3 shift to AI-directed development

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

1. **Matplotlib's three layers** — Figure (canvas), Axes (individual plot), Artists (lines, bars, text)
2. **The object-oriented API** — `fig, ax = plt.subplots()` for explicit figure/axes creation, methods on `ax` not `plt`
3. **Multi-plot layouts** — `plt.subplots(rows, cols)` returns a grid of axes for side-by-side charts
4. **Objects that render themselves** — `plot_progress(ax)` pattern where the object draws on provided axes
5. **Dependency injection for visualization** — passing `ax` in so callers control layout
6. **Chart types** — line (`ax.plot`), bar (`ax.bar`), horizontal bar (`ax.barh`), scatter (`ax.scatter`)
7. **Chart formatting** — `set_title`, `set_xlabel`, `set_ylabel`, `legend`, `grid`, `tick_params`, `tight_layout`
8. **Saving charts** — `fig.savefig("file.png", dpi=150, bbox_inches='tight')` for publication-quality output
9. **Memory management** — `plt.close(fig)` to free figure memory after saving
10. **`date.isocalendar()`** — returns `(year, week_number, weekday)` for ISO week-based grouping
11. **`matplotlib.use('Agg')`** — non-interactive backend for scripts that generate charts without a display

---

**Day 14 of 365. Your data has eyes now. Lines go up, bars compare, patterns emerge. Numbers became pictures.** 🚀
