#!/usr/bin/env python3
"""Live API integration tests for XHS SDK - requires valid cookie"""

import asyncio
import os
import sys
from pathlib import Path

# Add SDK to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from xhs_sdk import XhsClient, AsyncXhsClient
from xhs_sdk.exceptions import XhsAuthError, XhsAPIError
from xhs_sdk.utils import get_cookie


def test_with_real_cookie():
    """Test with real cookie - from environment variable or local config"""
    cookie = get_cookie()
    if not cookie:
        print("⚠️  No cookie found! Please either:")
        print("   1. Set XHS_COOKIE environment variable")
        print("   2. Create config.local.json with your cookie")
        return False
    
    print("=== Live API Integration Tests ===")
    print("⚠️  This SDK is for learning purposes only!\n")
    
    try:
        # Initialize client
        client = XhsClient(cookie=cookie, debug=True)
        
        # Test 1: Get current user info
        print("1. Testing get_current_user...")
        try:
            user = client.get_current_user()
            print(f"✅ Success: User {user.nickname} (ID: {user.user_id})")
            print(f"   Followers: {user.followers}")
            print(f"   Following: {user.following}")
            print(f"   Notes: {user.notes_count}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Test 2: Search notes
        print("\n2. Testing search_notes...")
        try:
            notes = client.search_notes("Python编程", limit=5)
            print(f"✅ Success: Found {len(notes)} notes")
            for i, note in enumerate(notes, 1):
                print(f"   {i}. {note.title[:30]}...")
                print(f"      Author: {note.author.nickname}")
                print(f"      Likes: {note.likes} | Comments: {note.comments}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Test 3: Get home feed
        print("\n3. Testing get_home_feed...")
        try:
            home_feed = client.get_home_feed()
            print(f"✅ Success: Got {len(home_feed)} recommended notes")
            if home_feed:
                note = home_feed[0]
                print(f"   First note: {note.title[:30]}...")
                print(f"   Author: {note.author.nickname}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Close client
        client.close()
        return True
        
    except XhsAuthError as e:
        print(f"\n❌ Authentication failed: {e}")
        print("Possible reasons:")
        print("1. Cookie expired")
        print("2. Invalid cookie format")
        print("3. Account status issue")
        return False
    except Exception as e:
        print(f"\n❌ Unknown error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_async_client():
    """Test async client functionality"""
    cookie = get_cookie()
    if not cookie:
        print("⚠️  No cookie found! Please either:")
        print("   1. Set XHS_COOKIE environment variable")
        print("   2. Create config.local.json with your cookie")
        return False
    
    print("\n=== Async Client Integration Tests ===")
    
    try:
        async with AsyncXhsClient(cookie=cookie, debug=False) as client:
            print("Running concurrent requests...")
            
            # Concurrent requests
            results = await asyncio.gather(
                client.get_current_user(),
                client.search_notes("美食", limit=3),
                client.get_home_feed(),
                return_exceptions=True
            )
            
            user, search_results, home_feed = results
            
            if not isinstance(user, Exception):
                print(f"✅ User: {user.nickname}")
            else:
                print(f"❌ User fetch failed: {user}")
                
            if not isinstance(search_results, Exception):
                print(f"✅ Search results: {len(search_results)} notes")
            else:
                print(f"❌ Search failed: {search_results}")
                
            if not isinstance(home_feed, Exception):
                print(f"✅ Home feed: {len(home_feed)} notes")
            else:
                print(f"❌ Home feed failed: {home_feed}")
                
        return True
                
    except Exception as e:
        print(f"❌ Async client error: {e}")
        return False


if __name__ == "__main__":
    print("XHS Python SDK Live Integration Tests")
    print("=" * 50)
    
    # Test sync client
    sync_success = test_with_real_cookie()
    
    # Test async client
    async_success = asyncio.run(test_async_client())
    
    print("\n" + "=" * 50)
    print("Integration Test Results:")
    print(f"Sync Client: {'✅ PASS' if sync_success else '❌ FAIL'}")
    print(f"Async Client: {'✅ PASS' if async_success else '❌ FAIL'}")
    print("\nNote: Some failures may be due to account permissions or expired cookies.")