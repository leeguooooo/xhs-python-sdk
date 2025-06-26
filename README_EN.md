# XHS Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-google-blue)](https://google.github.io/styleguide/pyguide.html)

English | [简体中文](README.md)

A Python SDK for XiaoHongShu (Little Red Book) Web API

## ⚠️ Legal Disclaimer

**This SDK is developed for LEARNING and RESEARCH purposes only.**

- This project is **NOT** affiliated with, authorized by, or endorsed by XiaoHongShu
- **Commercial use is strictly prohibited**
- Users must comply with XiaoHongShu's Terms of Service
- The developers assume no liability for misuse of this SDK
- Use at your own risk and responsibility

## 📚 Purpose

This SDK is intended for:
- Academic research on social media platforms
- Learning web scraping and API reverse engineering
- Understanding modern web application architectures
- Educational demonstrations of SDK design patterns

## 🚫 Prohibited Uses

This SDK must NOT be used for:
- Commercial purposes of any kind
- Automated content scraping at scale
- Creating derivative commercial products
- Violating XiaoHongShu's Terms of Service
- Any illegal or unethical activities

## 🛠 Installation

### Requirements
- Python 3.8+
- Node.js 14+ (for signature generation)

### Install from PyPI (Coming Soon)
```bash
pip install xhs-sdk
```

### Install from Source
```bash
git clone https://github.com/leeguooooo/xhs-python-sdk.git
cd xhs-python-sdk
pip install -e .
```

## 🚀 Quick Start

### Authentication
First, obtain your cookie from XiaoHongShu web:
1. Visit https://www.xiaohongshu.com and log in
2. Open DevTools (F12) → Network tab
3. Refresh the page, find any request, copy the `Cookie` header value

### Basic Usage

```python
from xhs_sdk import XhsClient
from xhs_sdk.exceptions import XhsAuthError

# Initialize client
client = XhsClient(cookie="your_cookie_here")

try:
    # Get current user info
    user = client.get_current_user()
    print(f"User: {user.nickname} (ID: {user.user_id})")
    
    # Search notes
    notes = client.search_notes("Python programming", limit=10)
    for note in notes:
        print(f"- {note.title} ({note.likes} likes)")
        
except XhsAuthError:
    print("Authentication failed. Please update your cookie.")
```

### Async Support

```python
import asyncio
from xhs_sdk import AsyncXhsClient

async def main():
    async with AsyncXhsClient(cookie="your_cookie") as client:
        # Concurrent requests
        user, notes = await asyncio.gather(
            client.get_current_user(),
            client.search_notes("programming")
        )
        print(f"{user.nickname} found {len(notes)} notes")

asyncio.run(main())
```

## 📖 API Reference

### Client Configuration

```python
client = XhsClient(
    cookie: str,              # Required: authentication cookie
    timeout: int = 30,        # Request timeout in seconds
    max_retries: int = 3,     # Maximum retry attempts
    retry_delay: float = 1.0, # Delay between retries
    debug: bool = False,      # Enable debug logging
    proxy: dict = None        # HTTP/HTTPS proxy settings
)
```

### Available Methods

#### User Operations
- `get_current_user()` - Get authenticated user info
- `get_user_profile(user_id: str)` - Get user profile by ID

#### Note Operations  
- `search_notes(keyword: str, limit: int = 20, sort: str = "general")` - Search notes
- `get_home_feed()` - Get personalized home feed
- `get_note(note_id: str, xsec_token: str)` - Get note details

#### Comment Operations
- `get_note_comments(note_id: str, xsec_token: str, cursor: str = "")` - Get comments
- `post_comment(note_id: str, content: str)` - Post a comment

### Data Models

#### User
```python
user_id: str          # User ID
nickname: str         # Nickname
avatar: str          # Avatar URL
description: str     # Bio description
followers: int       # Followers count
following: int       # Following count
notes_count: int     # Notes count
```

#### Note
```python
note_id: str         # Note ID
title: str           # Title
description: str     # Description
author: User         # Author info
images: List[str]    # Image URLs
video: dict         # Video info
likes: int          # Likes count
comments: int       # Comments count
collects: int       # Collections count
created_at: datetime # Creation time
```

#### Comment
```python
comment_id: str      # Comment ID
content: str         # Comment content
user: User          # Commenter info
created_at: datetime # Creation time
likes: int          # Likes count
```

## 🔧 Advanced Usage

### Error Handling

```python
from xhs_sdk.exceptions import (
    XhsAuthError,      # Authentication errors
    XhsAPIError,       # API errors
    XhsNetworkError,   # Network errors
    XhsRateLimitError  # Rate limit errors
)

try:
    notes = client.search_notes("test")
except XhsAuthError:
    print("Cookie expired")
except XhsRateLimitError:
    print("Too many requests")
except XhsAPIError as e:
    print(f"API error: {e.code} - {e.message}")
```

### Pagination for Comments

```python
all_comments = []
cursor = ""

while True:
    page = client.get_note_comments(
        note_id="note_id",
        xsec_token="token",
        cursor=cursor
    )
    all_comments.extend(page.comments)
    
    if not page.has_more:
        break
    cursor = page.cursor
    
print(f"Total comments: {len(all_comments)}")
```

### Batch Operations (Async)

```python
async def batch_search():
    async with AsyncXhsClient(cookie="cookie") as client:
        keywords = ["Python", "Machine Learning", "Data Science"]
        
        # Concurrent searches
        results = await asyncio.gather(*[
            client.search_notes(kw, limit=5) 
            for kw in keywords
        ])
        
        for keyword, notes in zip(keywords, results):
            print(f"{keyword}: {len(notes)} notes")
```

## 🏗 Architecture

```
xhs_sdk/
├── client.py          # Main client implementation
├── models/            # Pydantic data models
├── api/               # API endpoint handlers
├── core/              # Core utilities (HTTP, auth)
├── exceptions.py      # Custom exception classes
└── constants.py       # Constants and configurations
```

## 🧪 Testing

Run tests:
```bash
# Set environment variable
export XHS_COOKIE="your_cookie"

# Run test script
python test_sdk.py
```

## 🤝 Contributing

We welcome contributions that improve the SDK for educational purposes!

Before contributing:
1. Follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
2. Add tests for new functionality
3. Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Notice

By using this SDK, you acknowledge that:
1. You will use it only for learning and research purposes
2. You will not use it for any commercial activities
3. You understand the risks and take full responsibility
4. You will comply with all applicable laws and regulations

## 🙏 Acknowledgments

- Inspired by modern SDK design patterns
- Built for educational purposes
- Thanks to the open-source community

---

**Remember: This SDK is for LEARNING ONLY. Please use responsibly and ethically.**