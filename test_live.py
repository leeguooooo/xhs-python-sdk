#!/usr/bin/env python3
"""实时测试 XHS SDK"""

import asyncio
import os
import sys
from pathlib import Path

# Add SDK to path for testing
sys.path.insert(0, str(Path(__file__).parent))

from xhs_sdk import XhsClient, AsyncXhsClient
from xhs_sdk.exceptions import XhsAuthError, XhsAPIError


def test_with_real_cookie():
    """使用真实 cookie 测试"""
    cookie = "galaxy.creator.beaker.session.id=1750815815418083460892; galaxy_creator_session_id=z4V75Ldqlt236Za1hElYMkRsyqdxXOcFna2h; customerClientId=889584813827385; websectiga=a9bdcaed0af874f3a1431e94fbea410e8f738542fbb02df4e8e30c29ef3d91ac; access-token-creator.xiaohongshu.com=customer.creator.AT-68c5175196966671623120916vlvygaovxreosgo; webId=4519a429a6c0954977fb09af1e0b241d; customer-sso-sid=68c517519696667162312089x6rgsy1a2kjcdpo3; gid=yjW04S8f8238yjW04S8DdE3DSdv8lAKK2qk2Kf4U1KVM4dq8vky6uI888qYqj2q8dJ040iJK; x-user-id-creator.xiaohongshu.com=5bfcdc756b58b74712fb8910; a1=197a4c0becey0oq6653g5pl6js4yg1mziw6enibd430000383953; sec_poison_id=57c108c4-0aa9-46b3-8d46-fe61f1294483; xsecappid=ugc; acw_tc=0a0d0e0317508157841747092e7ea91546812a582bee36df27745f02e085d9"
    
    print("=== 测试 XHS SDK ===")
    print("注意：本 SDK 仅供学习使用！\n")
    
    try:
        # 初始化客户端
        client = XhsClient(cookie=cookie, debug=True)
        
        # 测试 1: 获取当前用户信息
        print("1. 正在获取当前用户信息...")
        try:
            user = client.get_current_user()
            print(f"✅ 成功获取用户信息:")
            print(f"   - 昵称: {user.nickname}")
            print(f"   - ID: {user.user_id}")
            print(f"   - 粉丝数: {user.followers}")
            print(f"   - 关注数: {user.following}")
            print(f"   - 笔记数: {user.notes_count}")
        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}")
        
        # 测试 2: 搜索笔记
        print("\n2. 正在搜索笔记...")
        try:
            notes = client.search_notes("Python编程", limit=5)
            print(f"✅ 搜索成功，找到 {len(notes)} 篇笔记:")
            for i, note in enumerate(notes, 1):
                print(f"   {i}. {note.title[:30]}...")
                print(f"      作者: {note.author.nickname}")
                print(f"      点赞: {note.likes} | 评论: {note.comments} | 收藏: {note.collects}")
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
        
        # 测试 3: 获取首页推荐
        print("\n3. 正在获取首页推荐...")
        try:
            home_feed = client.get_home_feed()
            print(f"✅ 成功获取 {len(home_feed)} 篇推荐笔记")
            if home_feed:
                note = home_feed[0]
                print(f"   第一篇: {note.title[:30]}...")
                print(f"   作者: {note.author.nickname}")
        except Exception as e:
            print(f"❌ 获取推荐失败: {e}")
        
        # 关闭客户端
        client.close()
        
    except XhsAuthError as e:
        print(f"\n❌ 认证失败: {e}")
        print("可能原因：")
        print("1. Cookie 已过期")
        print("2. Cookie 格式不正确")
        print("3. 账号状态异常")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()


async def test_async_client(cookie):
    """测试异步客户端"""
    print("\n\n=== 测试异步客户端 ===")
    
    try:
        async with AsyncXhsClient(cookie=cookie, debug=False) as client:
            print("正在并发执行多个请求...")
            
            # 并发获取多个数据
            results = await asyncio.gather(
                client.get_current_user(),
                client.search_notes("美食", limit=3),
                client.get_home_feed(),
                return_exceptions=True
            )
            
            user, search_results, home_feed = results
            
            if not isinstance(user, Exception):
                print(f"✅ 用户: {user.nickname}")
            else:
                print(f"❌ 获取用户失败: {user}")
                
            if not isinstance(search_results, Exception):
                print(f"✅ 搜索结果: {len(search_results)} 篇")
            else:
                print(f"❌ 搜索失败: {search_results}")
                
            if not isinstance(home_feed, Exception):
                print(f"✅ 首页推荐: {len(home_feed)} 篇")
            else:
                print(f"❌ 获取推荐失败: {home_feed}")
                
    except Exception as e:
        print(f"❌ 异步客户端错误: {e}")


if __name__ == "__main__":
    # 测试同步客户端
    test_with_real_cookie()
    
    # 测试异步客户端
    cookie = "galaxy.creator.beaker.session.id=1750815815418083460892; galaxy_creator_session_id=z4V75Ldqlt236Za1hElYMkRsyqdxXOcFna2h; customerClientId=889584813827385; websectiga=a9bdcaed0af874f3a1431e94fbea410e8f738542fbb02df4e8e30c29ef3d91ac; access-token-creator.xiaohongshu.com=customer.creator.AT-68c5175196966671623120916vlvygaovxreosgo; webId=4519a429a6c0954977fb09af1e0b241d; customer-sso-sid=68c517519696667162312089x6rgsy1a2kjcdpo3; gid=yjW04S8f8238yjW04S8DdE3DSdv8lAKK2qk2Kf4U1KVM4dq8vky6uI888qYqj2q8dJ040iJK; x-user-id-creator.xiaohongshu.com=5bfcdc756b58b74712fb8910; a1=197a4c0becey0oq6653g5pl6js4yg1mziw6enibd430000383953; sec_poison_id=57c108c4-0aa9-46b3-8d46-fe61f1294483; xsecappid=ugc; acw_tc=0a0d0e0317508157841747092e7ea91546812a582bee36df27745f02e085d9"
    asyncio.run(test_async_client(cookie))