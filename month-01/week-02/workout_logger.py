import json
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving charts
import matplotlib.pyplot as plt
from datetime import date, timedelta
from collections import defaultdict, Counter
from pathlib import Path
from functools import total_ordering
import logging

DATA_FILE = Path("workouts.json")
CHARTS_DIR = Path("charts")

# Set up logging — this replaces print() for pipeline observability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("pipeline")

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
        return self.sets * self.reps * self.weight

    def __eq__(self, other) -> bool:
        # Equal if same exercise, date, sets, reps, weight
        # (exact duplicate detection)
        if not isinstance(other, ExerciseEntry):
            return NotImplemented
        return (self.exercise, self.date_performed, self.sets, self.reps, self.weight) == (other.exercise, other.date_performed, other.sets, other.reps, other.weight)

    def __lt__(self, other) -> bool:
        # Sort by date first, then exercise name
        if not isinstance(other, ExerciseEntry):
            return NotImplemented
        return (self.date_performed, self.exercise) < (other.date_performed, other.exercise)

    def __hash__(self) -> int:
        # Hash on (exercise, date_performed, sets, reps, weight)
        return hash((self.exercise, self.date_performed, self.sets, self.reps, self.weight))

    def __repr__(self) -> str:
        # "ExerciseEntry('Bench Press', 2026-03-14, 3×10@185lbs)"
        return f"ExerciseEntry('{self.exercise}', {self.date_performed}, {self.sets}x{self.reps}@{self.weight:.0f}lbs)"

    def __str__(self) -> str:
        # "Mar 14: Bench Press — 3 sets × 10 reps @ 185.0 lbs (vol: 5550.0)"
        return f"{self.date_performed.strftime('%b %d'):<10} {self.exercise:<15} — {self.sets} sets × {self.reps} reps @ {self.weight:.1f} lbs (vol: {self.volume:.1f})"

    def to_dict(self) -> dict:
        # JSON serialization — date as ISO string
        return {
            "exercise": self.exercise,
            "date_performed": self.date_performed.isoformat(),
            "sets": self.sets,
            "reps": self.reps,
            "weight": self.weight,
            "volume": self.volume
        }

    @classmethod
    def from_dict(cls, data: dict):
        # JSON deserialization — parse ISO date string
        return cls(
            exercise=data["exercise"],
            date_performed=date.fromisoformat(data["date_performed"]),
            sets=data["sets"],
            reps=data["reps"],
            weight=data["weight"]
        )


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
        return max(entry.weight for entry in self.entries) if self.entries else 0

    @property
    def total_volume(self) -> float:
        """Sum of volume across all sessions."""
        # sum() with generator
        return sum(entry.weight * entry.reps * entry.sets for entry in self.entries)

    @property
    def session_count(self) -> int:
        """Number of sessions (unique dates) for this exercise."""
        # len(set(dates))
        return len({entry.date_performed for entry in self.entries})

    @property
    def average_weight(self) -> float:
        """Average weight across all entries."""
        # sum(weights) / len(entries)
        return sum(entry.weight for entry in self.entries) / len(self.entries)

    @property
    def recent_trend(self) -> str:
        """Is the weight trending up, down, or flat over last 4 sessions?
        Compare average of last 2 sessions vs average of 2 before that.
        """
        # Split entries into recent vs earlier
        # Compare averages
        # Return "↑ improving", "↓ declining", or "→ steady"
        if len(self.entries) < 4:
            return "Insufficient data"
        else:
            recent_avg = sum(entry.weight for entry in self.entries[-2:]) / 2
            earlier_avg = sum(entry.weight for entry in self.entries[:-2]) / 2
            if abs(recent_avg - earlier_avg) < 0.0001:
                return "→ steady"
            elif recent_avg > earlier_avg:
                return "↑ improving"
            else:
                return "↓ declining"
            
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
        return f"{self.exercise_name}: {len(self.entries)} sessions, PR {self.personal_record:.1f} sessions, avg {self.average_weight:.1f} lbs, trend {self.recent_trend}"
    
    def __iter__(self):
        return iter(self.entries)
    
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

    def __iter__(self):
        return iter(self.entries)

    def _group_by_exercise(self) -> dict:
        """Group entries by exercise name.
        Returns: {exercise_name: ExerciseLog}
        
        Uses defaultdict(list) to collect entries, then wraps in ExerciseLog.
        """
        # Group entries
        # Return {name: ExerciseLog(name, entries)}
        grouped = defaultdict(list)
        for entry in self.entries:
            grouped[entry.exercise].append(entry)
        return {exercise_name: ExerciseLog(exercise_name, entries) for exercise_name, entries in grouped.items()}
                

    def get_exercise_log(self, exercise_name: str):
        """Get the ExerciseLog for a specific exercise, or None."""
        return self._by_exercise.get(exercise_name)

    @property
    def exercise_names(self) -> list:
        """All unique exercise names, sorted alphabetically."""
        return sorted(self._by_exercise.keys())

    @property
    def total_sessions(self) -> int:
        """Total number of unique workout dates."""
        # len(set(e.date_performed for e in self.entries))
        return len(set(e.date_performed for e in self.entries))

    @property
    def total_volume(self) -> float:
        """Total volume across all exercises."""
        return sum(e.volume for e in self.entries)

    def get_weekly_volume(self) -> dict:
        """Total volume per ISO week.
        Returns: {(year, week): total_volume}
        
        Uses date.isocalendar() to get (year, week_number, weekday).
        Groups by (year, week_number) and sums volume within each group.
        """
        weekly = defaultdict(float)
        for entry in self.entries:
            iso_cal = entry.date_performed.isocalendar()
            iso_week_str = f"{iso_cal[0]}-W{iso_cal[1]:02d}"
            weekly[iso_week_str] += entry.volume
        return dict(weekly)

    def get_day_of_week_frequency(self) -> dict:
        """How many sessions on each day of the week.
        Returns: {"Monday": 5, "Tuesday": 3, ...}
        """
        # Use Counter on weekday names
        return Counter(entry.date_performed.strftime("%A") for entry in self.entries)

    def plot_weekly_volume(self, ax) -> None:
        """Bar chart of total volume per week."""
        # Sort by week
        # Create labels like "Wk 10", "Wk 11"
        # Draw bar chart
        weekly_data = sorted(self.get_weekly_volume().items())
        for (week_num), volume in weekly_data:
            ax.bar(f"Wk {week_num}", volume) # week is (year, week_num) tuple
        ax.set_xlabel(f"Week")
        ax.set_ylabel("Volume")
        ax.set_title("Weekly Volume")
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        return ax
            
    def plot_exercise_frequency(self, ax) -> None:
        """Horizontal bar chart showing session count per exercise."""
        # Get session_count from each ExerciseLog
        # Sort by frequency
        # Draw horizontal bar chart
        exercise_logs = [(name, log) for name, log in self._by_exercise.items()]
        for exercise_name, log in sorted(exercise_logs):
            sessions = log.session_count
            ax.barh(exercise_name, sessions)
        ax.set_xlabel("Session Count")
        ax.set_ylabel("Excercise")
        ax.set_title("Exercise Frequency")
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='y', rotation=45)
        return ax


    def plot_personal_records(self, ax) -> None:
        """Horizontal bar chart of personal record weight per exercise."""
        # Get PR from each ExerciseLog
        # Sort by weight
        # Draw horizontal bar chart
        exercise_logs = [(name, log) for name, log in self._by_exercise.items()]
        for exercise_name, log in sorted(exercise_logs, key=lambda x: x[1].personal_record,):
            pr = log.personal_record
            ax.barh(exercise_name, pr)
        ax.set_xlabel("Weight (lbs)")
        ax.set_ylabel("Exercise")
        ax.set_title("Personal Records")
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='y', rotation=45)
        return ax

    def plot_day_heatmap(self, ax) -> None:
        """Bar chart showing training frequency by day of week."""
        # Get day frequency
        # Draw bar chart Mon-Sun
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        frequencies =  [self.get_day_of_week_frequency().get(day,0) for day in day_order]
        ax.bar(day_order, frequencies, color='steelblue')
        ax.set_xlabel("Day of Week")
        ax.set_ylabel("Frequency")
        ax.set_title("Training Frequency")
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='y', rotation=4)
        return ax


# ──────────────────────────────────────
# DATA LAYER — persistence
# ──────────────────────────────────────

class WorkoutStore:
    """JSON persistence for workout entries."""

    def __init__(self, filepath: Path = DATA_FILE):
        self.filepath = filepath

    def load(self) -> list:
        """Load entries from JSON. Returns list of ExerciseEntry."""
        if not self.filepath.exists():
            return []
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                return [ExerciseEntry.from_dict(item) for item in data]
        except FileNotFoundError:
            logger.error(f"File not found: {self.filepath}")
            return []
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from {self.filepath}")
            return []
        except Exception as e:
            logger.error(f"Failed to read file {self.filepath}: {e}")
            return []

    def save(self, entries: list) -> None:
        """Save all entries to JSON."""
        try:
            # Convert ExerciseEntry objects to dictionaries
            data = [entry.to_dict() for entry in entries]
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=4)
                logger.info(f"Saved {len(entries)} entries to {self.filepath}")
            return
        except Exception as e:
            logger.error(f"Failed to write file {self.filepath}: {e}")
            return

# ──────────────────────────────────────
# BUSINESS LOGIC
# ──────────────────────────────────────

class WorkoutManager:
    """Manages workout entries and chart generation."""

    def __init__(self, store: WorkoutStore = None):
        self.store = store or WorkoutStore()
        self.entries = self.store.load()
        if not self.entries: #Only seed if empty
            logger.info("No entries found, seeding with default data.")
            self.entries = seed_data()
            self.store.save(self.entries)

    def add_entry(self, exercise: str, sets: int, reps: int, weight: float,
                  entry_date: date = None) -> ExerciseEntry:
        """Log a new exercise entry. Defaults to today's date."""
        # Create ExerciseEntry, append, save, return
        if sets <= 0 or reps <= 0 or weight < 0:
            raise ValueError("Sets and reps must be positive, weight must be non-negative")
        else:
            entry_date = entry_date or date.today()
            entry = ExerciseEntry(exercise, entry_date, sets, reps, weight)
            self.entries.append(entry)
            self.store.save(self.entries)
        return entry

    def get_stats(self) -> WorkoutStats:
        """Get aggregate statistics across all entries."""
        return WorkoutStats(self.entries)

    def get_exercise_log(self, exercise_name: str):
        """Get log for a specific exercise."""
        # Filter entries, create ExerciseLog
        return ExerciseLog(exercise_name, [entry for entry in self.entries if entry.exercise == exercise_name])            

    def get_exercise_names(self) -> list:
        """All unique exercise names."""
        return list(set(entry.exercise for entry in self.entries))

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
            if choice == "1":
                self.log_exercise_prompt()
            elif choice == "2":
                self.view_history()
            elif choice == "3":
                self.view_exercise_stats()
            elif choice == "4":
                self.view_overall_stats()
            elif choice == "5":
                self.generate_charts()
            elif choice == "6":
                self.log_past_workout()
            elif choice == "7":
                break
            else:
                print("Invalid choice. Try again.")

    def log_exercise_prompt(self):
        """Get exercise details from user and log them.
        
        Tip for good UX: remember the last exercise name and offer it
        as a default. Gym sessions usually repeat the same exercises.
        """
        # Get exercise name, sets, reps, weight
        # Validate all inputs (positive numbers)
        # Add entry, show confirmation with volume
        last_exercise = None
        while True:
            try:
                print("Log an exercise session.")
                print("Press enter to use the last exercise name")
                exercise_name = input("Enter exercise name: ")
                if exercise_name == "":
                    exercise_name = last_exercise
                    print(f"Last exercise: {last_exercise}")
                else:
                   last_exercise = exercise_name
                # Get other details
                sets = int(input("Enter number of sets: "))
                reps = int(input("Enter number of reps: "))
                weight = float(input("Enter weight lifted lbs): "))
                # Add entry
                self.manager.add_entry(exercise_name, date.today(), sets, reps, weight)
                # Show confirmation
                volume = sets * reps * weight
                print(f"Added {volume}lbs of {exercise_name} for {volume}lbs total volume.")
                # Ask if user wants to log another session
                another_session = input("Log another session? (y/n): ")
                if another_session.lower() != "y":
                    break
            except FloatingPointError as e:
                logger.error(f"Weight {weight} is not a valid number. Please enter a number")
                print(f"Weight {weight} is not a valid number. Please enter a number")
                continue
            except ValueError as e:
                logger.error(f"Error: {e}")
                print(f"Error: {e}")
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"Error: {e}")
                continue
        print("Thank you for using the workout logger!")
        return

    def view_history(self):
        """Show all entries for one exercise, chronologically."""
        # List available exercises
        # User picks one
        # Display sorted entries with __str__
        print("Viewing workout history...")
        exercise_names = self.manager.get_exercise_names()
        for exercise_name in exercise_names:
            print(f"  - {exercise_name}")
        exercise_name = input("Enter the name of the exercise you want to view: ")
        for entry in self.manager.get_exercise_log(exercise_name):
            print(entry)
        return

    def view_exercise_stats(self):
        """Show detailed stats for one exercise."""
        # List exercises
        # User picks one
        # Display: PR, average weight, total volume, session count, trend
        print("Viewing exercise stats...")
        exercise_names = self.manager.get_exercise_names()
        for exercise_name in exercise_names:
            print(f"  - {exercise_name}")
        exercise_name = input("Enter the name of the exercise you want to view: ")
        entry = self.manager.get_exercise_log(exercise_name)
        print(entry)
        return

    def view_overall_stats(self):
        """Show cross-exercise summary."""
        # Total sessions, total volume, exercises tracked
        # Display each exercise's one-line summary
        print("Viewing overall stats...")
        for stat in self.manager.get_stats():
            print(f"{stat}")
        return

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
        print("Logging past workout...")
        exercise_name = input("Enter exercise name: ")
        date_str = input("Enter date (YYYY-MM-DD): ")
        sets = int(input("Enter number of sets: "))
        reps = int(input("Enter number of reps: "))
        weight = float(input("Enter weight lifted (lbs)): "))
        target_date = date.fromisoformat(date_str)
        self.manager.add_entry(exercise_name, target_date, sets, reps, weight)

def seed_data():
    """Seed the database with some sample data."""
    # Example: 4 weeks of bench press, progressing weight
    entries_to_add = [
        ExerciseEntry("Bench Press", date.fromisoformat("2026-02-17"), 3, 10, 135),
        ExerciseEntry("Bench Press", date.fromisoformat("2026-02-20"), 3, 10, 140),
        ExerciseEntry("Bench Press", date.fromisoformat("2026-02-24"), 4, 8, 145),
        ExerciseEntry("Bench Press", date.fromisoformat("2026-02-27"), 4, 8, 145),
        ExerciseEntry("Bench Press", date.fromisoformat("2026-03-03"), 4, 8, 150),
        ExerciseEntry("Bench Press", date.fromisoformat("2026-03-06"), 3, 10, 155),
        ExerciseEntry("Bench Press", date.fromisoformat("2026-03-10"), 4, 8, 155),
        ExerciseEntry("Bench Press", date.fromisoformat("2026-03-13"), 4, 6, 160),
        ExerciseEntry("Squat", date.fromisoformat("2026-02-18"), 3, 8, 185),
        ExerciseEntry("Squat", date.fromisoformat("2026-02-21"), 4, 8, 185),
        ExerciseEntry("Squat", date.fromisoformat("2026-02-25"), 4, 6, 195),
        ExerciseEntry("Squat", date.fromisoformat("2026-03-01"), 4, 8, 195),
        ExerciseEntry("Squat", date.fromisoformat("2026-03-04"), 4, 6, 205),
        ExerciseEntry("Squat", date.fromisoformat("2026-03-08"), 3, 8, 205),
        ExerciseEntry("Squat", date.fromisoformat("2026-03-11"), 4, 6, 210),
        ExerciseEntry("Deadlift", date.fromisoformat("2026-02-19"), 3, 5, 225),
        ExerciseEntry("Deadlift", date.fromisoformat("2026-02-26"), 3, 5, 235),
        ExerciseEntry("Deadlift", date.fromisoformat("2026-03-05"), 3, 5, 245),
        ExerciseEntry("Deadlift", date.fromisoformat("2026-03-12"), 3, 3, 255),
        ExerciseEntry("Deadlift", date.fromisoformat("2026-03-02"), 3, 5, 265)
    ]
    return entries_to_add

if __name__ == "__main__":
    app = WorkoutApp()
    app.run()