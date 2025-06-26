"""
小红书 SDK 详细使用教程
"""

# ===== 1. 安装和初始化 =====
"""
首先安装 SDK:
pip install xhs-sdk

或从源码安装:
git clone https://github.com/leeguooooo/xhs-python-sdk.git
cd xhs-python-sdk
pip install -e .
"""

# ===== 2. 获取 Cookie =====
"""
方法一：从浏览器手动获取
1. 打开 https://www.xiaohongshu.com
2. 登录账号
3. F12 打开开发者工具
4. Network 标签 -> 任意请求 -> Headers -> Cookie
5. 复制整个 Cookie 值

方法二：使用浏览器自动化工具
（注意：这只是示例，实际使用需遵守平台规则）
"""

# ===== 3. 初始化客户端 =====
from xhs_sdk import XhsClient

# 基础初始化
client = XhsClient(cookie="a1=xxx; web_session=xxx; ...")

# 完整配置
client = XhsClient(
    cookie="your_cookie",
    timeout=30,         # 超时时间
    max_retries=3,      # 重试次数
    retry_delay=1,      # 重试延迟
    debug=True,         # 调试模式
    proxy={            # 代理设置
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
)

# ===== 4. 用户操作 =====
# 获取当前登录用户信息
user = client.get_current_user()
print(f"""
用户信息:
- ID: {user.user_id}
- 昵称: {user.nickname}
- 简介: {user.description}
- 粉丝数: {user.followers}
- 关注数: {user.following}
- 笔记数: {user.notes_count}
""")

# ===== 5. 搜索功能 =====
# 基础搜索
notes = client.search_notes("咖啡")

# 高级搜索
notes = client.search_notes(
    keyword="咖啡",
    limit=50,              # 结果数量
    sort="hot",            # 排序方式: hot(热门), time(最新)
    note_type="normal",    # 笔记类型: normal(图文), video(视频)
    filter_options={
        "location": "上海",
        "min_likes": 1000,
        "max_likes": 10000
    }
)

# 处理搜索结果
for note in notes:
    print(f"""
    标题: {note.title}
    作者: {note.author.nickname}
    点赞: {note.likes} | 评论: {note.comments} | 收藏: {note.collects}
    标签: {', '.join(note.tags)}
    链接: https://www.xiaohongshu.com/explore/{note.note_id}
    """)

# ===== 6. 获取笔记详情 =====
"""
注意：获取笔记详情需要 xsec_token
获取方式：
1. 访问笔记页面 URL
2. URL 中包含 xsec_token 参数
例如: https://www.xiaohongshu.com/explore/123456?xsec_token=xxx
"""

# 获取单篇笔记
note_detail = client.get_note(
    note_id="123456",
    xsec_token="your_xsec_token"
)

print(f"""
笔记详情:
标题: {note_detail.title}
内容: {note_detail.content}
图片: {len(note_detail.images)} 张
视频: {'有' if note_detail.video else '无'}
发布时间: {note_detail.created_at}
最后更新: {note_detail.updated_at}
""")

# 下载笔记图片
for idx, img_url in enumerate(note_detail.images):
    # client.download_image(img_url, f"note_{note_id}_{idx}.jpg")
    print(f"图片 {idx + 1}: {img_url}")

# ===== 7. 评论操作 =====
# 获取评论列表
comments_result = client.get_note_comments(
    note_id="123456",
    xsec_token="your_xsec_token",
    cursor=""  # 分页游标，首次为空
)

# 遍历所有评论（分页）
all_comments = []
cursor = ""
while True:
    result = client.get_note_comments(
        note_id="123456",
        xsec_token="token",
        cursor=cursor
    )
    all_comments.extend(result.comments)
    
    if not result.has_more:
        break
    cursor = result.cursor

print(f"共获取 {len(all_comments)} 条评论")

# 发布评论
try:
    new_comment = client.post_comment(
        note_id="123456",
        content="这个笔记写得真棒！学到了很多 [赞]"
    )
    print(f"评论成功，ID: {new_comment.comment_id}")
except Exception as e:
    print(f"评论失败: {e}")

# ===== 8. 首页推荐 =====
# 获取个性化推荐
home_feed = client.get_home_feed()
print(f"获取到 {len(home_feed)} 篇推荐笔记")

# 处理推荐内容
for note in home_feed[:5]:
    print(f"- {note.title} by {note.author.nickname}")

# ===== 9. 批量操作（使用异步） =====
import asyncio
from xhs_sdk import AsyncXhsClient

async def batch_operations():
    async with AsyncXhsClient(cookie="your_cookie") as client:
        # 并发搜索多个关键词
        keywords = ["美食", "旅行", "穿搭", "护肤"]
        tasks = [client.search_notes(kw, limit=10) for kw in keywords]
        all_results = await asyncio.gather(*tasks)
        
        for keyword, results in zip(keywords, all_results):
            print(f"{keyword}: 找到 {len(results)} 篇笔记")
        
        # 批量获取笔记详情
        note_ids = ["id1", "id2", "id3"]
        detail_tasks = [
            client.get_note(nid, xsec_token="token") 
            for nid in note_ids
        ]
        details = await asyncio.gather(*detail_tasks, return_exceptions=True)
        
        for note_id, detail in zip(note_ids, details):
            if isinstance(detail, Exception):
                print(f"获取 {note_id} 失败: {detail}")
            else:
                print(f"获取 {note_id} 成功: {detail.title}")

# 运行异步任务
# asyncio.run(batch_operations())

# ===== 10. 错误处理最佳实践 =====
from xhs_sdk.exceptions import (
    XhsAuthError, 
    XhsAPIError, 
    XhsNetworkError,
    XhsRateLimitError
)
import time

def safe_request_with_retry():
    """带重试的安全请求"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # 尝试请求
            result = client.search_notes("test")
            return result
            
        except XhsAuthError:
            # Cookie 失效，无法重试
            print("认证失败，请更新 Cookie")
            raise
            
        except XhsRateLimitError:
            # 触发频率限制，延长等待时间
            wait_time = retry_delay * (attempt + 1)
            print(f"触发频率限制，等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
            
        except XhsAPIError as e:
            # API 错误，可能可以重试
            if e.code in [500, 502, 503]:
                print(f"服务器错误 {e.code}，第 {attempt + 1} 次重试")
                time.sleep(retry_delay)
            else:
                print(f"API 错误: {e.code} - {e.message}")
                raise
                
        except XhsNetworkError:
            # 网络错误，重试
            print(f"网络错误，第 {attempt + 1} 次重试")
            time.sleep(retry_delay)
            
        except Exception as e:
            # 未知错误
            print(f"未知错误: {e}")
            raise
    
    print("重试次数已达上限")
    return None

# ===== 11. 日志和调试 =====
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 启用 SDK 调试模式
debug_client = XhsClient(cookie="your_cookie", debug=True)

# ===== 12. 性能优化建议 =====
"""
1. 使用异步客户端进行批量操作
2. 合理设置超时时间和重试次数
3. 实现请求缓存机制
4. 控制并发数量
5. 使用连接池
"""

# 示例：带缓存的客户端封装
from functools import lru_cache
import hashlib

class CachedXhsClient(XhsClient):
    @lru_cache(maxsize=1000)
    def search_notes_cached(self, keyword, limit=20):
        """缓存搜索结果"""
        return self.search_notes(keyword, limit)
    
    def get_cache_key(self, *args, **kwargs):
        """生成缓存键"""
        key = f"{args}_{kwargs}"
        return hashlib.md5(key.encode()).hexdigest()

# ===== 13. 实际应用场景 =====

# 场景1：监控特定话题
def monitor_topic(topic, interval=300):
    """监控话题新内容"""
    seen_notes = set()
    
    while True:
        try:
            notes = client.search_notes(topic, sort="time", limit=20)
            new_notes = [n for n in notes if n.note_id not in seen_notes]
            
            for note in new_notes:
                print(f"新笔记: {note.title} - {note.author.nickname}")
                seen_notes.add(note.note_id)
            
            time.sleep(interval)
        except Exception as e:
            print(f"监控出错: {e}")
            time.sleep(60)

# 场景2：数据分析
def analyze_topic(keyword):
    """分析话题数据"""
    notes = client.search_notes(keyword, limit=100)
    
    total_likes = sum(n.likes for n in notes)
    avg_likes = total_likes / len(notes) if notes else 0
    
    print(f"""
    话题分析: {keyword}
    - 笔记总数: {len(notes)}
    - 总点赞数: {total_likes}
    - 平均点赞: {avg_likes:.1f}
    - 最高点赞: {max(n.likes for n in notes) if notes else 0}
    """)

# 场景3：内容聚合
async def aggregate_content(topics):
    """聚合多个话题内容"""
    async with AsyncXhsClient(cookie="your_cookie") as client:
        all_notes = []
        
        for topic in topics:
            notes = await client.search_notes(topic, limit=10)
            all_notes.extend(notes)
        
        # 按点赞数排序
        all_notes.sort(key=lambda x: x.likes, reverse=True)
        
        print("热门内容聚合:")
        for note in all_notes[:10]:
            print(f"- {note.title} ({note.likes} 赞)")

if __name__ == "__main__":
    print("请参考以上示例使用 SDK")