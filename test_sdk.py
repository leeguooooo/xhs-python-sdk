#!/usr/bin/env python3
"""Test script for XHS SDK - For demonstration purposes only."""

import asyncio
import os
import sys
from pathlib import Path

# Add SDK to path for testing
sys.path.insert(0, str(Path(__file__).parent))

from xhs_sdk import XhsClient, AsyncXhsClient
from xhs_sdk.exceptions import XhsAuthError, XhsAPIError


def test_sync_client():
    """Test synchronous client functionality."""
    print("=== Testing Synchronous Client ===")
    
    # Get cookie from environment variable
    cookie = os.getenv("XHS_COOKIE")
    if not cookie:
        print("Please set XHS_COOKIE environment variable")
        return
    
    try:
        # Initialize client
        client = XhsClient(cookie=cookie, debug=True)
        
        # Test 1: Get current user
        print("\n1. Getting current user...")
        user = client.get_current_user()
        print(f"   User: {user.nickname} (ID: {user.user_id})")
        print(f"   Followers: {user.followers}")
        
        # Test 2: Search notes
        print("\n2. Searching notes...")
        notes = client.search_notes("Python", limit=5)
        print(f"   Found {len(notes)} notes")
        for i, note in enumerate(notes, 1):
            print(f"   {i}. {note.title[:30]}... ({note.likes} likes)")
        
        # Test 3: Get home feed
        print("\n3. Getting home feed...")
        home_feed = client.get_home_feed()
        print(f"   Got {len(home_feed)} recommendations")
        
        # Close client
        client.close()
        print("\n✅ Synchronous client tests passed!")
        
    except XhsAuthError as e:
        print(f"❌ Authentication error: {e}")
    except XhsAPIError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


async def test_async_client():
    """Test asynchronous client functionality."""
    print("\n=== Testing Asynchronous Client ===")
    
    cookie = os.getenv("XHS_COOKIE")
    if not cookie:
        print("Please set XHS_COOKIE environment variable")
        return
    
    try:
        async with AsyncXhsClient(cookie=cookie, debug=True) as client:
            # Test concurrent requests
            print("\n1. Making concurrent requests...")
            
            user, notes, home_feed = await asyncio.gather(
                client.get_current_user(),
                client.search_notes("编程", limit=3),
                client.get_home_feed(),
            )
            
            print(f"   User: {user.nickname}")
            print(f"   Search results: {len(notes)} notes")
            print(f"   Home feed: {len(home_feed)} notes")
            
        print("\n✅ Asynchronous client tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("XHS Python SDK Test Suite")
    print("=" * 50)
    print("⚠️  This SDK is for learning purposes only!")
    print("⚠️  Do not use for commercial purposes!")
    print("=" * 50)
    
    # Test sync client
    test_sync_client()
    
    # Test async client
    asyncio.run(test_async_client())
    
    print("\n" + "=" * 50)
    print("Testing complete!")


if __name__ == "__main__":
    main()