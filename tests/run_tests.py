#!/usr/bin/env python3
"""
Test runner for Paketbox simulation environment.

This script provides a convenient way to run all tests with proper environment setup
for simulating the Raspberry Pi environment without requiring actual hardware.
"""

import unittest
import sys
import os

def main():
    """Run all paketbox tests"""
    print("=" * 60)
    print("Paketbox Test Environment")
    print("=" * 60)
    print("Running comprehensive test suite to simulate Raspberry Pi environment...")
    print()
    
    # Set up test discovery
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall: {'SUCCESS' if success else 'FAILED'}")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())