"""
小红书 Python SDK 基础使用示例
"""
import asyncio
from xhs_sdk import XhsClient, AsyncXhsClient
from xhs_sdk.exceptions import XhsAuthError, XhsAPIError

# 1. 同步客户端使用示例
def sync_example():
    """同步方式使用 SDK"""
    # 初始化客户端（需要从浏览器获取 cookie）
    client = XhsClient(cookie="your_xhs_cookie_here")
    
    try:
        # 获取当前用户信息
        user = client.get_current_user()
        print(f"当前用户: {user.nickname} (ID: {user.user_id})")
        
        # 搜索笔记
        notes = client.search_notes("美食", limit=10)
        for note in notes:
            print(f"笔记: {note.title} - 点赞数: {note.likes}")
        
        # 获取首页推荐
        home_feed = client.get_home_feed()
        print(f"首页推荐 {len(home_feed)} 篇笔记")
        
        # 获取笔记详情（需要从笔记URL中提取 xsec_token）
        # URL 示例: https://www.xiaohongshu.com/explore/123456?xsec_token=xxx
        note_detail = client.get_note(
            note_id="123456",
            xsec_token="your_xsec_token"
        )
        print(f"笔记内容: {note_detail.content[:100]}...")
        
        # 获取笔记评论
        comments = client.get_note_comments(
            note_id="123456",
            xsec_token="your_xsec_token"
        )
        for comment in comments[:5]:
            print(f"评论: {comment.content} - {comment.user.nickname}")
        
        # 发布评论
        new_comment = client.post_comment(
            note_id="123456",
            content="这个笔记写得真好！"
        )
        print(f"评论发布成功: {new_comment.comment_id}")
        
    except XhsAuthError:
        print("认证失败，请检查 cookie 是否有效")
    except XhsAPIError as e:
        print(f"API 调用失败: {e}")

# 2. 异步客户端使用示例
async def async_example():
    """异步方式使用 SDK"""
    async with AsyncXhsClient(cookie="your_xhs_cookie_here") as client:
        try:
            # 并发获取多个信息
            user, home_feed, search_results = await asyncio.gather(
                client.get_current_user(),
                client.get_home_feed(),
                client.search_notes("旅行", limit=20)
            )
            
            print(f"用户: {user.nickname}")
            print(f"首页推荐: {len(home_feed)} 篇")
            print(f"搜索结果: {len(search_results)} 篇")
            
            # 批量获取笔记详情
            note_ids = [note.note_id for note in search_results[:3]]
            tasks = [
                client.get_note(note_id, xsec_token="token")
                for note_id in note_ids
            ]
            note_details = await asyncio.gather(*tasks)
            
            for detail in note_details:
                print(f"笔记标题: {detail.title}")
                
        except Exception as e:
            print(f"错误: {e}")

# 3. 高级功能示例
def advanced_example():
    """高级功能使用示例"""
    # 配置客户端
    client = XhsClient(
        cookie="your_cookie",
        timeout=30,  # 请求超时时间
        max_retries=3,  # 最大重试次数
        debug=True  # 开启调试日志
    )
    
    # 使用过滤器搜索
    notes = client.search_notes(
        keyword="咖啡",
        limit=20,
        sort="hot",  # 按热度排序
        note_type="video"  # 只搜索视频笔记
    )
    
    # 分页获取评论
    all_comments = []
    cursor = ""
    while True:
        page = client.get_note_comments(
            note_id="123456",
            xsec_token="token",
            cursor=cursor
        )
        all_comments.extend(page.comments)
        if not page.has_more:
            break
        cursor = page.cursor
    
    print(f"总共获取 {len(all_comments)} 条评论")

# 4. 错误处理示例
def error_handling_example():
    """错误处理最佳实践"""
    client = XhsClient(cookie="your_cookie")
    
    try:
        notes = client.search_notes("test")
    except XhsAuthError:
        # Cookie 失效，需要重新登录
        print("Cookie 已失效，请重新获取")
    except XhsAPIError as e:
        # API 错误，可能是参数错误或服务端问题
        print(f"API 错误: {e.code} - {e.message}")
    except Exception as e:
        # 其他未知错误
        print(f"未知错误: {e}")

if __name__ == "__main__":
    # 运行同步示例
    sync_example()
    
    # 运行异步示例
    # asyncio.run(async_example())