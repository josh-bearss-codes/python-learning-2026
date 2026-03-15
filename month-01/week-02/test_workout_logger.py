# test_workout_logger.py
import unittest
import json
import os
from datetime import date
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from workout_logger import (
    ExerciseEntry, ExerciseLog, WorkoutStats, WorkoutStore, 
    WorkoutManager, seed_data, DATA_FILE, CHARTS_DIR
)

class TestExerciseEntry(unittest.TestCase):
    def setUp(self):
        # Clean up before each test
        if DATA_FILE.exists():
            DATA_FILE.unlink()
    
    def test_volume_calculation(self):
        entry = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        self.assertEqual(entry.volume, 5550.0)
    
    def test_volume_with_zero_weight(self):
        entry = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 0)
        self.assertEqual(entry.volume, 0.0)
    
    def test_equality(self):
        entry1 = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        entry2 = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        self.assertEqual(entry1, entry2)
    
    def test_inequality_different_weights(self):
        entry1 = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        entry2 = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 190)
        self.assertNotEqual(entry1, entry2)
    
    def test_hash_equality(self):
        entry1 = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        entry2 = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        self.assertEqual(hash(entry1), hash(entry2))
    
    def test_sorting(self):
        entry1 = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        entry2 = ExerciseEntry("Squat", date(2026, 3, 10), 4, 8, 200)
        entry3 = ExerciseEntry("Deadlift", date(2026, 3, 14), 5, 5, 225)
        entries = [entry1, entry2, entry3]
        sorted_entries = sorted(entries)
        # Should sort by date first, then exercise name
        self.assertEqual(sorted_entries[0], entry2)  # Earlier date
        self.assertEqual(sorted_entries[1], entry1)  # Same date, "Bench Press" before "Deadlift"
        self.assertEqual(sorted_entries[2], entry3)
    
    def test_str_format(self):
        entry = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        result = str(entry)
        self.assertIn("Mar 14", result)
        self.assertIn("Bench Press", result)
        self.assertIn("3 sets", result)
        self.assertIn("10 reps", result)
        self.assertIn("185.0 lbs", result)
        self.assertIn("vol: 5550.0", result)
    
    def test_to_dict(self):
        entry = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        result = entry.to_dict()
        self.assertEqual(result["exercise"], "Bench Press")
        self.assertEqual(result["date_performed"], "2026-03-14")
        self.assertEqual(result["sets"], 3)
        self.assertEqual(result["reps"], 10)
        self.assertEqual(result["weight"], 185)
        self.assertEqual(result["volume"], 5550.0)
    
    def test_from_dict(self):
        data = {
            "exercise": "Bench Press",
            "date_performed": "2026-03-14",
            "sets": 3,
            "reps": 10,
            "weight": 185,
            "volume": 5550.0
        }
        entry = ExerciseEntry.from_dict(data)
        self.assertEqual(entry.exercise, "Bench Press")
        self.assertEqual(entry.date_performed, date(2026, 3, 14))
        self.assertEqual(entry.sets, 3)
        self.assertEqual(entry.reps, 10)
        self.assertEqual(entry.weight, 185)
        self.assertEqual(entry.volume, 5550.0)
    
    def test_repr_format(self):
        entry = ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185)
        result = repr(entry)
        self.assertIn("ExerciseEntry", result)
        self.assertIn("Bench Press", result)
        self.assertIn("2026-03-14", result)

class TestExerciseLog(unittest.TestCase):
    def setUp(self):
        self.entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 135),
            ExerciseEntry("Bench Press", date(2026, 3, 8), 3, 10, 140),
            ExerciseEntry("Bench Press", date(2026, 3, 15), 4, 8, 145),
        ]
        self.log = ExerciseLog("Bench Press", self.entries)
    
    def test_personal_record(self):
        self.assertEqual(self.log.personal_record, 145)
    
    def test_personal_record_empty(self):
        empty_log = ExerciseLog("Unknown", [])
        self.assertEqual(empty_log.personal_record, 0)
    
    def test_total_volume(self):
        expected = 135*3*10 + 140*3*10 + 145*4*8
        self.assertEqual(self.log.total_volume, expected)
    
    def test_session_count(self):
        self.assertEqual(self.log.session_count, 3)
    
    def test_average_weight(self):
        expected = (135 + 140 + 145) / 3
        self.assertEqual(self.log.average_weight, expected)
    
    def test_recent_trend_improving_with_4_entries(self):
        """Test improving trend: last 2 entries have higher weight than first 2."""
        entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 100),
            ExerciseEntry("Bench Press", date(2026, 3, 8), 3, 10, 100),
            ExerciseEntry("Bench Press", date(2026, 3, 15), 4, 8, 120),
            ExerciseEntry("Bench Press", date(2026, 3, 22), 4, 8, 120),
        ]
        log = ExerciseLog("Bench Press", entries)
        
        # recent_avg = (120 + 120) / 2 = 120.0
        # earlier_avg = (100 + 100) / 2 = 100.0
        # Since 120 > 100, should return "↑ improving"
        self.assertEqual(log.recent_trend, "↑ improving")
    
    def test_recent_trend_declining_with_4_entries(self):
        """Test declining trend: last 2 entries have lower weight than first 2."""
        entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 150),
            ExerciseEntry("Bench Press", date(2026, 3, 8), 3, 10, 150),
            ExerciseEntry("Bench Press", date(2026, 3, 15), 4, 8, 130),
            ExerciseEntry("Bench Press", date(2026, 3, 22), 4, 8, 130),
        ]
        log = ExerciseLog("Bench Press", entries)
        
        # recent_avg = (130 + 130) / 2 = 130.0
        # earlier_avg = (150 + 150) / 2 = 150.0
        # Since 130 < 150, should return "↓ declining"
        self.assertEqual(log.recent_trend, "↓ declining")
    
    def test_recent_trend_steady_with_4_entries(self):
        """Test steady trend: last 2 entries have same weight as first 2."""
        entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 140),
            ExerciseEntry("Bench Press", date(2026, 3, 8), 3, 10, 140),
            ExerciseEntry("Bench Press", date(2026, 3, 15), 4, 8, 140),
            ExerciseEntry("Bench Press", date(2026, 3, 22), 4, 8, 140),
        ]
        log = ExerciseLog("Bench Press", entries)
        
        # recent_avg = (140 + 140) / 2 = 140.0
        # earlier_avg = (140 + 140) / 2 = 140.0
        # Since equal (within tolerance), should return "→ steady"
        self.assertEqual(log.recent_trend, "→ steady")
    
    def test_recent_trend_fewer_than_4_entries_insufficient_data(self):
        """Test behavior with fewer than 4 entries returns 'Insufficient data'."""
        # 3 entries - should return "Insufficient data"
        entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 140),
            ExerciseEntry("Bench Press", date(2026, 3, 8), 3, 10, 140),
            ExerciseEntry("Bench Press", date(2026, 3, 15), 4, 8, 140),
        ]
        log = ExerciseLog("Bench Press", entries)
        self.assertEqual(log.recent_trend, "Insufficient data")
    
    def test_recent_trend_single_entry_insufficient_data(self):
        """Test behavior with only 1 entry returns 'Insufficient data'."""
        entries = [ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 140)]
        log = ExerciseLog("Bench Press", entries)
        self.assertEqual(log.recent_trend, "Insufficient data")
    
    def test_recent_trend_two_entries_insufficient_data(self):
        """Test behavior with 2 entries returns 'Insufficient data'."""
        entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 140),
            ExerciseEntry("Bench Press", date(2026, 3, 8), 3, 10, 140),
        ]
        log = ExerciseLog("Bench Press", entries)
        self.assertEqual(log.recent_trend, "Insufficient data")
    
    def test_recent_trend_floating_point_precision(self):
        """Test that floating-point precision issues don't affect trend detection."""
        # Use weights that might cause floating-point precision issues
        entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 140.1),
            ExerciseEntry("Bench Press", date(2026, 3, 8), 3, 10, 140.1),
            ExerciseEntry("Bench Press", date(2026, 3, 15), 4, 8, 140.1),
            ExerciseEntry("Bench Press", date(2026, 3, 22), 4, 8, 140.1),
        ]
        log = ExerciseLog("Bench Press", entries)
        
        # All weights are exactly the same, should return "→ steady"
        self.assertEqual(log.recent_trend, "→ steady")
    
    def test_recent_trend_with_mixed_weights(self):
        """Test with more varied weight values to ensure calculation is correct."""
        entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 1), 3, 10, 100),
            ExerciseEntry("Bench Press", date(2026, 3, 8), 3, 10, 110),
            ExerciseEntry("Bench Press", date(2026, 3, 15), 4, 8, 120),
            ExerciseEntry("Bench Press", date(2026, 3, 22), 4, 8, 130),
        ]
        log = ExerciseLog("Bench Press", entries)
        
        # recent_avg = (120 + 130) / 2 = 125.0
        # earlier_avg = (100 + 110) / 2 = 105.0
        # Since 125 > 105, should return "↑ improving"
        self.assertEqual(log.recent_trend, "↑ improving")   
    def test_str_format(self):
        result = str(self.log)
        self.assertIn("Bench Press", result)
        self.assertIn("3 sessions", result)
        self.assertIn("PR 145.0", result)
        self.assertIn("trend", result)

class TestWorkoutStats(unittest.TestCase):
    def setUp(self):
        self.entries = seed_data()
        self.stats = WorkoutStats(self.entries)
    
    def test_exercise_names(self):
        names = self.stats.exercise_names
        self.assertIn("Bench Press", names)
        self.assertIn("Squat", names)
        self.assertIn("Deadlift", names)
        # Should be sorted alphabetically
        self.assertEqual(names, sorted(names))
    
    def test_total_sessions(self):
        self.assertEqual(self.stats.total_sessions, 20)  # 19 unique dates in seed_data
    
    def test_total_volume(self):
        expected = sum(e.volume for e in self.entries)
        self.assertEqual(self.stats.total_volume, expected)
    
    def test_get_weekly_volume(self):
        weekly = self.stats.get_weekly_volume()
        self.assertIsInstance(weekly, dict)
        self.assertGreater(len(weekly), 0)
        # Check format of keys (should be ISO week strings)
        for key in weekly.keys():
            self.assertIn("W", key)  # ISO week format: "2026-W10"
    
    def test_get_day_of_week_frequency(self):
        frequency = self.stats.get_day_of_week_frequency()
        self.assertIn("Monday", frequency)
        self.assertIn("Tuesday", frequency)
        self.assertGreaterEqual(frequency["Monday"], 0)
    
    def test_get_exercise_log(self):
        log = self.stats.get_exercise_log("Bench Press")
        self.assertIsInstance(log, ExerciseLog)
        self.assertEqual(log.exercise_name, "Bench Press")
        self.assertEqual(len(log.entries), 8)  # 8 bench press entries in seed_data
    
    def test_get_exercise_log_nonexistent(self):
        log = self.stats.get_exercise_log("Unknown")
        self.assertIsNone(log)
    
    def test_group_by_exercise_bug(self):
        # This test specifically targets the bug in _group_by_exercise()
        # If the bug exists, the ExerciseLog will be created incorrectly
        log = self.stats.get_exercise_log("Bench Press")
        # Should have 8 entries, not an ExerciseLog object wrapped in another structure
        self.assertEqual(len(log.entries), 8)

class TestWorkoutStore(unittest.TestCase):
    def setUp(self):
        # Clean up before each test
        if DATA_FILE.exists():
            DATA_FILE.unlink()
    
    def test_save_and_load(self):
        entries = [
            ExerciseEntry("Bench Press", date(2026, 3, 14), 3, 10, 185),
            ExerciseEntry("Squat", date(2026, 3, 15), 4, 8, 200)
        ]
        store = WorkoutStore()
        store.save(entries)
        
        loaded_entries = store.load()
        self.assertEqual(len(loaded_entries), 2)
        self.assertEqual(loaded_entries[0].exercise, "Bench Press")
    
    def test_load_nonexistent_file(self):
        store = WorkoutStore()
        entries = store.load()
        self.assertEqual(entries, [])
    
    def test_save_empty_entries(self):
        store = WorkoutStore()
        store.save([])
        loaded = store.load()
        self.assertEqual(loaded, [])

class TestWorkoutManager(unittest.TestCase):
    def setUp(self):
        # Clean up before each test
        if DATA_FILE.exists():
            DATA_FILE.unlink()
        self.manager = WorkoutManager()
    
    def test_add_entry(self):
        entry = self.manager.add_entry("Bench Press", 3, 10, 185)
        self.assertIsInstance(entry, ExerciseEntry)
        self.assertEqual(entry.exercise, "Bench Press")
        self.assertEqual(entry.volume, 5550.0)
    
    def test_add_entry_validation_negative_sets(self):
        with self.assertRaises(ValueError):
            self.manager.add_entry("Bench Press", -1, 10, 185)
    
    def test_add_entry_validation_negative_reps(self):
        with self.assertRaises(ValueError):
            self.manager.add_entry("Bench Press", 3, -1, 185)
    
    def test_add_entry_validation_negative_weight(self):
        with self.assertRaises(ValueError):
            self.manager.add_entry("Bench Press", 3, 10, -10)
    
    def test_add_entry_validation_zero_sets(self):
        with self.assertRaises(ValueError):
            self.manager.add_entry("Bench Press", 0, 10, 185)
    
    def test_get_exercise_names(self):
        names = self.manager.get_exercise_names()
        self.assertIn("Bench Press", names)
        self.assertIn("Squat", names)
        self.assertIn("Deadlift", names)
    
    def test_get_exercise_log(self):
        log = self.manager.get_exercise_log("Bench Press")
        self.assertIsInstance(log, ExerciseLog)
        self.assertEqual(log.exercise_name, "Bench Press")
    
    def test_generate_charts(self):
        saved = self.manager.generate_all_charts()
        self.assertIsInstance(saved, list)
        self.assertGreater(len(saved), 0)
        # Check that files were actually created
        for filename in saved:
            filepath = CHARTS_DIR / filename
            self.assertTrue(filepath.exists(), f"Chart file {filename} was not created")

class TestWorkoutApp(unittest.TestCase):
    def setUp(self):
        # Clean up before each test
        if DATA_FILE.exists():
            DATA_FILE.unlink()
    
    def test_app_initialization(self):
        # This test will fail if the app constructor fails
        # It will reveal issues with WorkoutManager initialization
        try:
            from workout_logger import WorkoutApp
            app = WorkoutApp()
            self.assertIsNotNone(app.manager)
            self.assertIsNotNone(app.manager.entries)
        except Exception as e:
            self.fail(f"WorkoutApp initialization failed: {e}")

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Clean up before each test
        if DATA_FILE.exists():
            DATA_FILE.unlink()
        if CHARTS_DIR.exists():
            import shutil
            shutil.rmtree(CHARTS_DIR)
    
    def test_full_workflow(self):
        # 1. Create manager (should seed data)
        manager = WorkoutManager()
        self.assertGreater(len(manager.entries), 0)
        
        # 2. Add a new entry
        entry = manager.add_entry("Overhead Press", 3, 10, 100)
        self.assertEqual(len(manager.entries), 21)  # 20 seed + 1 new
        
        # 3. Get stats
        stats = manager.get_stats()
        self.assertEqual(stats.total_sessions, 21)  # Each entry is on a different date
        
        # 4. Generate charts
        saved = manager.generate_all_charts()
        self.assertGreater(len(saved), 0)
        
        # 5. Verify files exist
        for filename in saved:
            filepath = CHARTS_DIR / filename
            self.assertTrue(filepath.exists())
    
    def test_persistence(self):
        # 1. Add entry to manager
        manager1 = WorkoutManager()
        initial_count = len(manager1.entries)
        
        # 2. Add new entry
        entry = manager1.add_entry("Deadlift", 3, 5, 300)
        
        # 3. Create new manager instance (should load from file)
        manager2 = WorkoutManager()
        self.assertEqual(len(manager2.entries), initial_count + 1)
        self.assertEqual(manager2.entries[-1].exercise, "Deadlift")

if __name__ == '__main__':
    unittest.main()