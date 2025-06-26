#!/usr/bin/env python3
"""Test runner for XHS Python SDK"""

import sys
import os
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_unit_tests():
    """Run unit tests"""
    print("=" * 50)
    print("Running Unit Tests")
    print("=" * 50)
    
    try:
        from tests.unit.test_basic import test_client_initialization, test_client_with_debug
        
        print("Running basic unit tests...")
        test_client_initialization()
        test_client_with_debug()
        print("✅ Unit tests passed!\n")
        return True
    except Exception as e:
        print(f"❌ Unit tests failed: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("=" * 50)
    print("Running Integration Tests")
    print("=" * 50)
    
    try:
        # Run demo tests (safe with expired cookies)
        from tests.integration.test_demo import test_client_basic_functionality
        print("Running demo integration tests...")
        test_client_basic_functionality()
        
        # Check if live testing is available
        if os.getenv("XHS_COOKIE"):
            print("\nRunning live integration tests...")
            from tests.integration.test_api_live import test_with_real_cookie
            test_with_real_cookie()
        else:
            print("\n⚠️  Skipping live tests - set XHS_COOKIE environment variable to enable")
        
        print("✅ Integration tests completed!\n")
        return True
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    print("XHS Python SDK Test Suite")
    print("⚠️  This SDK is for learning purposes only!")
    print("⚠️  Do not use for commercial purposes!")
    
    # Run all tests
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()
    
    # Summary
    print("=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    print(f"Unit Tests: {'✅ PASS' if unit_success else '❌ FAIL'}")
    print(f"Integration Tests: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if unit_success and integration_success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())