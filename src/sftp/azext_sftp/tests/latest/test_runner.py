# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Test runner for SFTP extension tests.
Runs all unittest-based tests in the latest folder with comprehensive reporting.
"""

import unittest
import os
import sys
import time
from io import StringIO

def run_all_tests():
    """Run all tests in the latest folder with detailed reporting."""
    print("SFTP Extension Test Suite")
    print("=" * 50)
    
    # Get the directory containing this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all test files
    test_files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
    print(f"Test Directory: {test_dir}")
    print(f"Found {len(test_files)} test files:")
    for test_file in sorted(test_files):
        print(f"   • {test_file}")
    print()
    
    # Discover and run all tests
    start_time = time.time()
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Count total tests
    total_tests = suite.countTestCases()
    print(f"Total test cases discovered: {total_tests}")
    print("-" * 50)
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total time: {duration:.2f} seconds")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"   • {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"   • {test}")
            
    if result.skipped:
        print(f"\nSKIPPED ({len(result.skipped)}):")
        for test, reason in result.skipped:
            print(f"   • {test}: {reason}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
    
    return result.wasSuccessful()

def run_specific_test(test_module):
    """Run a specific test module with detailed reporting."""
    print(f"Running specific test: {test_module}")
    print("=" * 50)
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add test directory to path
    sys.path.insert(0, test_dir)
    
    start_time = time.time()
    loader = unittest.TestLoader()
    
    try:
        suite = loader.loadTestsFromName(test_module)
        total_tests = suite.countTestCases()
        print(f"Test cases in {test_module}: {total_tests}")
        print("-" * 50)
        
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
        result = runner.run(suite)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("=" * 50)
        print(f"{test_module.upper()} SUMMARY")
        print("=" * 50)
        print(f"Time: {duration:.2f} seconds")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        if result.wasSuccessful():
            print("ALL TESTS PASSED!")
        else:
            print("SOME TESTS FAILED!")
            
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Error loading test module '{test_module}': {e}")
        print("Available test modules:")
        test_files = [f[:-3] for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
        for test_file in sorted(test_files):
            print(f"   • {test_file}")
        return False

def run_specific_test_file(test_file):
    """Run all tests in a specific test file."""
    print(f"Running test file: {test_file}")
    print("=" * 50)
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add test directory to path
    sys.path.insert(0, test_dir)
    
    # Ensure .py extension
    if not test_file.endswith('.py'):
        test_file += '.py'
    
    test_path = os.path.join(test_dir, test_file)
    if not os.path.exists(test_path):
        print(f"Test file not found: {test_path}")
        return False
    
    start_time = time.time()
    loader = unittest.TestLoader()
    
    try:
        # Load tests from specific file
        suite = loader.discover(test_dir, pattern=test_file)
        total_tests = suite.countTestCases()
        print(f"Test cases in {test_file}: {total_tests}")
        print("-" * 50)
        
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
        result = runner.run(suite)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("=" * 50)
        print(f"{test_file.upper()} SUMMARY")
        print("=" * 50)
        print(f"Time: {duration:.2f} seconds")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        if result.wasSuccessful():
            print("ALL TESTS PASSED!")
        else:
            print("SOME TESTS FAILED!")
            
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Error loading test file '{test_file}': {e}")
        return False


def list_available_tests():
    """List all available test files and modules."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
    
    print("Available Test Files:")
    print("=" * 30)
    for test_file in sorted(test_files):
        print(f"   • {test_file}")
    print(f"\nTotal: {len(test_files)} test files")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run SFTP extension tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                                    # Run all tests
  python test_runner.py --test test_custom                 # Run specific test module
  python test_runner.py --file test_sftp_connect_comprehensive.py  # Run specific test file
  python test_runner.py --list                             # List available tests
  python test_runner.py --integration                      # Include integration tests
        """
    )
    parser.add_argument('--test', '-t', help='Specific test module to run (e.g., test_custom)')
    parser.add_argument('--file', '-f', help='Specific test file to run (e.g., test_custom.py)')
    parser.add_argument('--list', '-l', action='store_true', help='List available test files')
    parser.add_argument('--integration', '-i', action='store_true', 
                       help='Include integration tests (requires valid credentials)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    if args.list:
        list_available_tests()
        sys.exit(0)
    
    if args.quiet:
        # Redirect some output for quieter runs
        pass
    
    success = False
    
    if args.test:
        success = run_specific_test(args.test)
    elif args.file:
        success = run_specific_test_file(args.file)
    else:
        if not args.integration:
            print("Running unit tests only. Use --integration to include integration tests.")
            print("   Note: Integration tests require valid SFTP credentials.")
            print()
        
        success = run_all_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: All tests passed!")
    else:
        print("FAILURE: Some tests failed!")
    print("=" * 50)
    
    sys.exit(0 if success else 1)
