# run_tests.py
import unittest
import sys

# Add the current directory to path so we can import budget_tracker
sys.path.append('.')

if __name__ == '__main__':
    # Discover and run all tests in test_budget_tracker.py
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_budget_tracker.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print(f"\n{len(result.failures)} failures, {len(result.errors)} errors")
        sys.exit(1)