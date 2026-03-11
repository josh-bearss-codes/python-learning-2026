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
        start_date = None
        if today in self.completions:
            start_date = today
        elif yesterday in self.completions:
            start_date = yesterday
        else:
            return 0
        # Walk backward with while loop
        current_date = start_date
        current_streak = 0
        while current_date in self.completions:
            current_streak += 1
            current_date -= timedelta(days=1)
        return current_streak
        # Return count
        
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
        current_streak = 1
        maximum_streak = 1

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                maximum_streak = max(maximum_streak, current_streak)
            else:
                current_streak = 1

        return maximum_streak
    
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
        try:
            with self.filepath.open("r") as f:
                data = json.load(f)
                habits = [Habit.from_dict(d) for d in data]
                return habits
        # Handle missing file
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def save(self, habits: list) -> None:
        """Save habits to JSON file."""
        # Convert each Habit to dict using .to_dict()
        # Write with json.dump, indent=2
        try:
            with self.filepath.open("w") as f:
                data = [habit.to_dict() for habit in habits]
                json.dump(data, f, indent=2)
                print("Habits saved successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

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
        for habit in self.habits:
            if habit.name.lower() == name.lower():
                raise ValueError(f"Habit '{name}' already exists.")
        
        habit = Habit(name, description, target_frequency)
        self.habits.append(habit)
        self.store.save(self.habits)
        return habit

    def complete_habit(self, name: str, target_date: date = None) -> bool:
        """Mark a habit as completed. Optionally for a specific past date."""
        # Find habit by name
        # Call complete_today() or complete_date()
        # Save
        for habit in self.habits:
            if habit.name.lower() == name.lower():
                if target_date:
                    result = habit.complete_date(target_date)
                else:
                    result = habit.complete_today()
            self.store.save(self.habits)
            return result
        return False

    def get_habit(self, name: str):
        """Find a habit by name (case-insensitive)."""
        if name:
            for habit in self.habits:
                if habit.name.lower() == name.lower():
                    return habit
        return None

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
        if name:
            for i, habit in enumerate(self.habits):
                if habit.name.lower() == name.lower():
                    self.habits.pop(i)
                    self.store.save(self.habits)
                    return True
        return False

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
            if choice == '1':
                self.mark_complete_prompt()
            elif choice == '2':
                self.view_all()
            elif choice == '3':
                self.view_details_prompt()
            elif choice == '4':
                self.add_habit_prompt()
            elif choice == '5':
                self.backfill_prompt()
            elif choice == '6':
                self._show_daily_summary()
            elif choice == '7':
                self.delete_habit_prompt()
                # Quit
            elif choice == '8':
                break
            else:
                print("\nInvalid choice. Please try again.")

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
        pending = [h for h in self.manager.get_pending_habits()]
        if not pending:
            print("No pending habits to complete today.")
            return
        
        print("Pending habits:")
        for i, habit in enumerate(pending, 1):
            print(f"{i}. {habit.name}")
            
        try:
            choice = int(input("Which habit did you complete? ")) - 1
            if 0 <= choice < len(pending):
                habit = pending[choice]
                self.manager.complete_habit(habit.name)
                print(f"✅ {habit.name} marked as complete!")
                print(f"🔥 Streak: {self.manager.get_habit(habit.name).streak}")
            else:
                print("Invalid choice try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    def view_all(self):
        # Show each habit's status_line()
        # Sorted by streak (highest first)
        sorted_habits = self.manager.get_all_sorted()
        if not sorted_habits:
            print("No habits to display.")
            return
        
        for habit in sorted_habits:
            print(habit.status_line())

    def view_details_prompt(self):
        # Ask for habit name
        # Show full_stats()
        name = input("Enter habit name: ")
        habit = self.manager.get_habit(name)
        if habit:
            print(habit.full_stats())
            print("Details displayed.")
        else:
            print("Habit not found. Try again.")

    def add_habit_prompt(self):
        # Get name, description, frequency
        # Create via manager
        name = input("Enter habit name: ")
        description = input("Enter habit description: ")
        frequency = input("Enter habit frequency (daily/weekly): ")
        habit = Habit(name, description, frequency)
        self.manager.add_habit(habit)
        print("Habit added successfully.")

    def backfill_prompt(self):
        """Let user mark a past date as completed.
        Useful for: 'I exercised yesterday but forgot to log it.'
        """
        # Ask for habit name and date (YYYY-MM-DD)
        # Parse date, call manager.complete_habit(name, target_date)
        name = input("Enter habit name: ")
        date_str = input("Enter date (YYYY-MM-DD): ")
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        self.manager.complete_habit(name, target_date)
        print("Habit completed successfully for the specified date.")

if __name__ == "__main__":
    app = HabitApp()
    app.run()