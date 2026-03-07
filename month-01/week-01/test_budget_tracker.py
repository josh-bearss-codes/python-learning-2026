# test_budget_tracker.py

import unittest
from unittest.mock import patch, mock_open
import json
from datetime import datetime, date
from collections import defaultdict

# Import the classes from the budget_tracker module
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from budget_tracker import BudgetData, BudgetManager, BudgetApp

class TestBudgetData(unittest.TestCase):
    def setUp(self):
        # Create a temporary data file for testing
        self.test_file = "test_budget_data.json"
        
    def tearDown(self):
        # Clean up test file after each test
        try:
            os.remove(self.test_file)
        except FileNotFoundError:
            pass

    @patch("builtins.open", new_callable=mock_open, read_data='{"budgets": {}, "expenses": []}')
    def test_load_existing_file(self, mock_file):
        # Test loading existing file
        data = BudgetData(filepath=self.test_file)
        self.assertEqual(data.data["budgets"], {})
        self.assertEqual(data.data["expenses"], [])

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_missing_file(self, mock_file):
        # Test handling missing file
        data = BudgetData(filepath=self.test_file)
        self.assertEqual(data.data["budgets"], {})
        self.assertEqual(data.data["expenses"], [])

    @patch("builtins.open", side_effect=json.JSONDecodeError("Expecting value", "test", 0))
    def test_load_invalid_json(self, mock_file):
        # Test handling invalid JSON
        data = BudgetData(filepath=self.test_file)
        self.assertEqual(data.data["budgets"], {})
        self.assertEqual(data.data["expenses"], [])

    @patch("builtins.open", new_callable=mock_open)
    def test_save_success(self, mock_file):
        # Test successful save
        data = BudgetData(filepath=self.test_file)
        data.data = {"budgets": {"food": 500}, "expenses": []}
        data.save()
        mock_file.assert_called_once_with(self.test_file, "w")
        
    @patch("builtins.open", side_effect=IOError("Test error"))
    def test_save_failure(self, mock_file):
        # Test save failure handling
        data = BudgetData(filepath=self.test_file)
        data.data = {"budgets": {"food": 500}, "expenses": []}
        # Should not raise an exception
        data.save()

    def test_budgets_property(self):
        # Test budgets property getter/setter
        data = BudgetData(filepath=self.test_file)
        data.budgets = {"food": 500, "transport": 200}
        self.assertEqual(data.budgets, {"food": 500, "transport": 200})

    def test_expenses_property(self):
        # Test expenses property getter/setter
        data = BudgetData(filepath=self.test_file)
        data.expenses = [{"date": "2023-01-01", "amount": 50, "category": "food"}]
        self.assertEqual(data.expenses, [{"date": "2023-01-01", "amount": 50, "category": "food"}])

class TestBudgetManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary data file for testing
        self.test_file = "test_budget_data.json"
        self.data = BudgetData(filepath=self.test_file)
        self.manager = BudgetManager(self.data)

    def tearDown(self):
        # Clean up test file after each test
        try:
            os.remove(self.test_file)
        except FileNotFoundError:
            pass

    def test_set_budget(self):
        # Test setting a budget
        self.manager.set_budget("food", 500)
        self.assertEqual(self.data.budgets["food"], 500)

    def test_add_expense(self):
        # Test adding an expense
        self.manager.add_expense(50, "food", "Groceries")
        
        # Check that expense was added to the data
        self.assertEqual(len(self.data.expenses), 1)
        expense = self.data.expenses[0]
        self.assertEqual(expense["amount"], 50)
        self.assertEqual(expense["category"], "food")
        self.assertEqual(expense["description"], "Groceries")
        
        # Check that date is in correct format
        self.assertTrue("date" in expense)
        datetime.strptime(expense["date"], "%Y-%m-%d")

    @patch('budget_tracker.datetime')
    def test_get_monthly_spending(self, mock_datetime):
        # Mock current date to be January 15, 2023
        mock_datetime.now.return_value = datetime(2023, 1, 15)
        
        # Add some expenses for different months and categories
        self.data.expenses = [
            {"date": "2023-01-01", "amount": 50, "category": "food"},
            {"date": "2023-01-10", "amount": 30, "category": "transport"},
            {"date": "2022-12-15", "amount": 20, "category": "food"},  # Previous month
            {"date": "2023-01-20", "amount": 40, "category": "food"},  # Same category
        ]
        
        result = self.manager.get_monthly_spending()
        expected = {"food": 90.0, "transport": 30.0}
        self.assertEqual(result, expected)

    @patch('budget_tracker.datetime')
    def test_get_monthly_spending_invalid_date(self, mock_datetime):
        # Mock current date to be January 15, 2023
        mock_datetime.now.return_value = datetime(2023, 1, 15)
        
        # Add expense with invalid date format
        self.data.expenses = [
            {"date": "2023-01-01", "amount": 50, "category": "food"},
            {"date": "invalid-date", "amount": 30, "category": "transport"},  # Invalid date
        ]
        
        result = self.manager.get_monthly_spending()
        expected = {"food": 50.0}
        self.assertEqual(result, expected)

    @patch('budget_tracker.datetime')
    def test_get_budget_status(self, mock_datetime):
        # Mock current date to be January 15, 2023
        mock_datetime.now.return_value = datetime(2023, 1, 15)
        
        # Set up budgets and expenses
        self.data.budgets = {"food": 100, "transport": 50}
        self.data.expenses = [
            {"date": "2023-01-01", "amount": 60, "category": "food"},
            {"date": "2023-01-10", "amount": 30, "category": "transport"},
        ]
        
        result = self.manager.get_budget_status()
        expected = {
            "food": {"budget": 100, "spent": 60.0, "percent": 60.0, "alert": "yellow"},
            "transport": {"budget": 50, "spent": 30.0, "percent": 60.0, "alert": "yellow"}
        }
        self.assertEqual(result, expected)

    @patch('budget_tracker.datetime')
    def test_get_budget_status_with_zero_budget(self, mock_datetime):
        # Mock current date to be January 15, 2023
        mock_datetime.now.return_value = datetime(2023, 1, 15)
        
        # Set up budgets and expenses with zero budget
        self.data.budgets = {"food": 0}
        self.data.expenses = [
            {"date": "2023-01-01", "amount": 60, "category": "food"},
        ]
        
        result = self.manager.get_budget_status()
        expected = {
            "food": {"budget": 0, "spent": 60.0, "percent": 0, "alert": "green"}
        }
        self.assertEqual(result, expected)

    @patch('budget_tracker.date')
    def test_get_daily_remaining(self, mock_date):
        # Mock current date to be January 15, 2023
        mock_date.today.return_value = date(2023, 1, 15)
        
        # Set up budgets and expenses
        self.data.budgets = {"food": 100}
        self.data.expenses = [
            {"date": "2023-01-01", "amount": 60, "category": "food"},
        ]
        
        result = self.manager.get_daily_remaining("food")
        # Days in January: 31, days remaining: 31 - 15 = 16
        # Remaining budget: 100 - 60 = 40
        # Daily remaining: 40 / 16 = 2.5
        self.assertEqual(result, 2.5)

    @patch('budget_tracker.date')
    def test_get_daily_remaining_no_budget(self, mock_date):
        # Mock current date to be January 15, 2023
        mock_date.today.return_value = date(2023, 1, 15)
        
        # Set up budgets and expenses with no budget
        self.data.budgets = {}
        self.data.expenses = [
            {"date": "2023-01-01", "amount": 60, "category": "food"},
        ]
        
        result = self.manager.get_daily_remaining("food")
        self.assertEqual(result, 0)

    @patch('budget_tracker.date')
    def test_get_daily_remaining_spent_exceeds_budget(self, mock_date):
        # Mock current date to be January 15, 2023
        mock_date.today.return_value = date(2023, 1, 15)
        
        # Set up budgets and expenses where spent exceeds budget
        self.data.budgets = {"food": 50}
        self.data.expenses = [
            {"date": "2023-01-01", "amount": 60, "category": "food"},
        ]
        
        result = self.manager.get_daily_remaining("food")
        self.assertEqual(result, 0)

    @patch('budget_tracker.date')
    def test_get_daily_remaining_december(self, mock_date):
        # Mock current date to be December 15, 2023 (to test year transition)
        mock_date.today.return_value = date(2023, 12, 15)
        
        # Set up budgets and expenses
        self.data.budgets = {"food": 100}
        self.data.expenses = [
            {"date": "2023-12-01", "amount": 60, "category": "food"},
        ]
        
        result = self.manager.get_daily_remaining("food")
        # Days in December: 31, days remaining: 31 - 15 = 16
        # Remaining budget: 100 - 60 = 40
        # Daily remaining: 40 / 16 = 2.5
        self.assertEqual(result, 2.5)

class TestBudgetApp(unittest.TestCase):
    def setUp(self):
        # Create a temporary data file for testing
        self.test_file = "test_budget_data.json"
        
    def tearDown(self):
        # Clean up test file after each test
        try:
            os.remove(self.test_file)
        except FileNotFoundError:
            pass

    @patch('budget_tracker.BudgetData')
    @patch('budget_tracker.BudgetManager')
    def test_app_initialization(self, mock_manager, mock_data):
        # Test that app initializes correctly
        app = BudgetApp()
        self.assertIsNotNone(app.data)
        self.assertIsNotNone(app.manager)

if __name__ == '__main__':
    unittest.main()