#!/usr/bin/env python3
"""Simple test for XHS SDK"""

import sys
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent))

from xhs_sdk import XhsClient

# Test cookie
cookie = "abRequestId=2ce60926-e78a-5087-b280-d70826758bfa; webBuild=4.68.0; loadts=1750900933976; unread={%22ub%22:%2263ede7e8000000001300adc7%22%2C%22ue%22:%22642282ed00000000130302ee%22%2C%22uc%22:16}; web_session=030037af6ff4b30fcbd38be6242f4ac5ece92c; galaxy.creator.beaker.session.id=1750815815418083460892; galaxy_creator_session_id=z4V75Ldqlt236Za1hElYMkRsyqdxXOcFna2h; customerClientId=889584813827385; access-token-creator.xiaohongshu.com=customer.creator.AT-68c5175196966671623120916vlvygaovxreosgo; webId=4519a429a6c0954977fb09af1e0b241d; customer-sso-sid=68c517519696667162312089x6rgsy1a2kjcdpo3; gid=yjW04S8f8238yjW04S8DdE3DSdv8lAKK2qk2Kf4U1KVM4dq8vky6uI888qYqj2q8dJ040iJK; x-user-id-creator.xiaohongshu.com=5bfcdc756b58b74712fb8910; a1=197a4c0becey0oq6653g5pl6js4yg1mziw6enibd430000383953; xsecappid=ugc; acw_tc=0a00073f17509009383876930e044e0a30a37e86f6f677c610a7dfb8e2281f; websectiga=a9bdcaed0af874f3a1431e94fbea410e8f738542fbb02df4e8e30c29ef3d91ac; sec_poison_id=3f7228d3-8c89-4369-b1d1-8dcd462af083"

try:
    # Initialize client without debug
    client = XhsClient(cookie=cookie, debug=False)
    
    # Test 1: User info (may fail if cookie is invalid)
    print("1. Testing get_current_user...")
    try:
        user = client.get_current_user()
        print(f"✅ Success! User: {user.nickname} (ID: {user.user_id})")
    except Exception as e:
        print(f"❌ User info failed: {e}")
        print("   This is expected if the cookie is invalid/expired")
    
    # Test 2: Search (should work even without valid cookie)
    print("\n2. Testing search_notes...")
    try:
        notes = client.search_notes("Python", limit=3)
        print(f"✅ Success! Found {len(notes)} notes:")
        for i, note in enumerate(notes, 1):
            print(f"   {i}. {note.title[:40]}...")
            print(f"      Author: {note.author.nickname}")
            print(f"      Likes: {note.likes}")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ Initialization error: {e}")
    import traceback
    traceback.print_exc()