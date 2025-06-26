#!/usr/bin/env python3
"""Basic unit tests for XHS SDK"""

import sys
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from xhs_sdk import XhsClient

# Test cookie (expired, for testing purposes only)
TEST_COOKIE = "test_cookie_placeholder"

def test_client_initialization():
    """Test XHS client initialization"""
    client = XhsClient(cookie=TEST_COOKIE, debug=False)
    assert client is not None
    assert client.cookie == TEST_COOKIE

def test_client_with_debug():
    """Test XHS client initialization with debug mode"""
    client = XhsClient(cookie=TEST_COOKIE, debug=True)
    assert client is not None
    assert client.debug is True

if __name__ == "__main__":
    print("Running basic unit tests...")
    test_client_initialization()
    test_client_with_debug()
    print("✅ Basic unit tests passed!")