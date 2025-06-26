"""Test fixtures and mock data for XHS SDK tests"""

# Mock user data for testing
MOCK_USER_DATA = {
    "user_id": "test_user_123",
    "nickname": "Test User",
    "description": "This is a test user",
    "followers": 100,
    "following": 50,
    "notes_count": 25
}

# Mock note data for testing
MOCK_NOTE_DATA = {
    "note_id": "test_note_123",
    "title": "Test Note Title",
    "content": "This is test content",
    "likes": 10,
    "comments": 5,
    "collects": 3,
    "author": {
        "user_id": "test_author_123",
        "nickname": "Test Author"
    }
}

# Test cookies (expired/invalid for safety)
TEST_COOKIES = {
    "expired": "expired_cookie_for_testing",
    "invalid": "invalid_cookie_format",
    "demo": "abRequestId=demo; webBuild=4.68.0; web_session=demo_session"
}

# API response mocks
MOCK_RESPONSES = {
    "user_info": {
        "success": True,
        "data": MOCK_USER_DATA
    },
    "search_notes": {
        "success": True,
        "data": [MOCK_NOTE_DATA] * 3
    },
    "home_feed": {
        "success": True,  
        "data": [MOCK_NOTE_DATA] * 5
    }
}