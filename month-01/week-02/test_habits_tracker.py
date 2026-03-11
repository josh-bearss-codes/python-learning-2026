# In a Python shell or test script:
from datetime import date, timedelta
from habit_tracker import Habit

h = Habit("Test")
today = date.today()

# Add a 5-day streak ending yesterday
for i in range(5, 0, -1):
    h.completions.add(today - timedelta(days=i))
print(h.completions)
print(h.current_streak)   # Should be 5 (if today not yet completed)
                           # OR 0 if your algorithm requires today

h.complete_today()
print(h.current_streak)   # Should be 6

# Add a gap, then older streak
h.completions.add(today - timedelta(days=10))
h.completions.add(today - timedelta(days=11))
h.completions.add(today - timedelta(days=12))

print(h.longest_streak)   # Should be 6 (the current one, not the old 3-day one)