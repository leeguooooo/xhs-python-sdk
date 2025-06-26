#!/usr/bin/env python3
"""Debug tool to test individual API endpoints and identify issues"""

import sys
from pathlib import Path
import os

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from xhs_sdk import XhsClient
from xhs_sdk.constants import Endpoints, API_BASE_URL
from xhs_sdk.utils import get_cookie

def test_api_endpoints():
    """Test individual API endpoints to identify which ones work"""
    
    # Get cookie from various sources
    cookie = get_cookie()
    
    print("🔍 XHS API Endpoints Debug Tool")
    print("=" * 50)
    print(f"📍 Base URL: {API_BASE_URL}")
    
    if cookie:
        if os.getenv('XHS_COOKIE'):
            print(f"🍪 Cookie: ✅ Loaded from environment variable")
        else:
            print(f"🍪 Cookie: ✅ Loaded from config.local.json")
    else:
        print(f"🍪 Cookie: ❌ No cookie found!")
        print("   Please set XHS_COOKIE env var or create config.local.json")
        cookie = "demo_cookie_for_testing"
        print("   Using demo cookie for testing...")
    
    print()
    
    client = XhsClient(cookie=cookie, debug=True)
    
    # Test endpoints one by one
    endpoints_to_test = [
        {
            "name": "User Profile",
            "endpoint": Endpoints.USER_ME,
            "method": "GET",
            "test_func": lambda: client.get_current_user(),
            "description": "获取当前用户信息"
        },
        {
            "name": "Search Notes", 
            "endpoint": Endpoints.SEARCH_NOTES,
            "method": "POST",
            "test_func": lambda: client.search_notes("Python", limit=3),
            "description": "搜索笔记功能"
        },
        {
            "name": "Home Feed",
            "endpoint": Endpoints.HOME_FEED, 
            "method": "POST",
            "test_func": lambda: client.get_home_feed(),
            "description": "获取首页推荐"
        }
    ]
    
    results = []
    
    for endpoint_info in endpoints_to_test:
        print(f"🧪 Testing: {endpoint_info['name']}")
        print(f"   📍 Endpoint: {endpoint_info['endpoint']}")
        print(f"   🔧 Method: {endpoint_info['method']}")
        print(f"   📝 Description: {endpoint_info['description']}")
        
        try:
            result = endpoint_info['test_func']()
            print(f"   ✅ Success!")
            if hasattr(result, '__len__'):
                print(f"   📊 Returned {len(result)} items")
            results.append((endpoint_info['name'], "✅ Success", None))
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Failed: {error_msg}")
            
            # Categorize the error
            if "权限" in error_msg or "permission" in error_msg.lower():
                category = "🚫 Permission Denied"
            elif "认证" in error_msg or "auth" in error_msg.lower():
                category = "🔐 Authentication Failed"
            elif "cookie" in error_msg.lower():
                category = "🍪 Cookie Issue"
            elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                category = "⏱️ Rate Limited"
            else:
                category = "❓ Other Error"
                
            print(f"   🔍 Category: {category}")
            results.append((endpoint_info['name'], category, error_msg))
            
        print()
    
    # Summary
    print("📋 Test Results Summary")
    print("=" * 50)
    
    for name, status, error in results:
        print(f"{status} {name}")
        if error and len(error) > 100:
            print(f"    └─ {error[:100]}...")
        elif error:
            print(f"    └─ {error}")
    
    print()
    print("💡 Common Issues:")
    print("   🚫 Permission Denied: Account lacks specific API access")
    print("   🔐 Authentication Failed: Invalid or expired cookie")
    print("   🍪 Cookie Issue: Cookie format or content problems")
    print("   ⏱️ Rate Limited: Too many requests, wait and retry")
    
    print()
    print("🔧 API Endpoint Reference:")
    print(f"   User Profile: {API_BASE_URL}{Endpoints.USER_ME}")
    print(f"   Search Notes: {API_BASE_URL}{Endpoints.SEARCH_NOTES}")
    print(f"   Home Feed: {API_BASE_URL}{Endpoints.HOME_FEED}")
    print(f"   Note Detail: {API_BASE_URL}{Endpoints.NOTE_FEED}")
    print(f"   Comments: {API_BASE_URL}{Endpoints.COMMENT_PAGE}")

if __name__ == "__main__":
    test_api_endpoints()