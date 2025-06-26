# XHS Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-google-blue)](https://google.github.io/styleguide/pyguide.html)

[English](README_EN.md) | 简体中文

小红书 Web API 的 Python SDK

## ⚠️ 免责声明

**本 SDK 仅供学习和研究使用。**

- 本项目与小红书官方**无任何关联**
- **严禁用于商业用途**
- 使用者必须遵守小红书的服务条款
- 开发者不对 SDK 的滥用承担任何责任
- 使用本 SDK 的风险由使用者自行承担

## 📚 项目用途

本 SDK 仅适用于：
- 学术研究和教育学习
- 了解 Web API 的工作原理
- 学习 SDK 设计模式
- 个人技术研究

## 🚫 禁止用途

严禁将本 SDK 用于：
- 任何商业目的
- 大规模数据采集
- 侵犯他人隐私
- 违反小红书服务条款的行为
- 任何非法用途

## 🛠 安装

### 环境要求
- Python 3.8+
- Node.js 14+（用于签名生成）

### 从 PyPI 安装（即将发布）
```bash
pip install xhs-sdk
```

### 从源码安装
```bash
git clone https://github.com/leeguooooo/xhs-python-sdk.git
cd xhs-python-sdk
pip install -e .
```

## 🚀 快速开始

### 获取 Cookie
首先需要从小红书网页版获取 Cookie：
1. 访问 https://www.xiaohongshu.com 并登录
2. 打开开发者工具（F12）→ Network 标签页
3. 刷新页面，找到任意请求，复制 `Cookie` 请求头的值

### 基础使用

```python
from xhs_sdk import XhsClient
from xhs_sdk.exceptions import XhsAuthError

# 初始化客户端
client = XhsClient(cookie="你的Cookie")

try:
    # 获取当前用户信息
    user = client.get_current_user()
    print(f"用户名: {user.nickname} (ID: {user.user_id})")
    
    # 搜索笔记
    notes = client.search_notes("Python编程", limit=10)
    for note in notes:
        print(f"- {note.title} ({note.likes} 赞)")
        
except XhsAuthError:
    print("认证失败，请更新 Cookie")
```

### 异步支持

```python
import asyncio
from xhs_sdk import AsyncXhsClient

async def main():
    async with AsyncXhsClient(cookie="你的Cookie") as client:
        # 并发请求
        user, notes = await asyncio.gather(
            client.get_current_user(),
            client.search_notes("编程")
        )
        print(f"{user.nickname} 搜索到 {len(notes)} 篇笔记")

asyncio.run(main())
```

## 📖 API 参考

### 客户端配置

```python
client = XhsClient(
    cookie: str,              # 必需：认证 Cookie
    timeout: int = 30,        # 请求超时时间（秒）
    max_retries: int = 3,     # 最大重试次数
    retry_delay: float = 1.0, # 重试延迟（秒）
    debug: bool = False,      # 调试模式
    proxy: dict = None        # 代理设置
)
```

### 主要功能

#### 用户相关
- `get_current_user()` - 获取当前用户信息
- `get_user_profile(user_id: str)` - 获取指定用户资料

#### 笔记相关  
- `search_notes(keyword: str, limit: int = 20, sort: str = "general")` - 搜索笔记
- `get_home_feed()` - 获取首页推荐
- `get_note(note_id: str, xsec_token: str)` - 获取笔记详情

#### 评论相关
- `get_note_comments(note_id: str, xsec_token: str, cursor: str = "")` - 获取评论
- `post_comment(note_id: str, content: str)` - 发布评论

### 数据模型

#### User 用户信息
```python
user_id: str          # 用户ID
nickname: str         # 昵称
avatar: str          # 头像URL
description: str     # 个人简介
followers: int       # 粉丝数
following: int       # 关注数
notes_count: int     # 笔记数
```

#### Note 笔记信息
```python
note_id: str         # 笔记ID
title: str           # 标题
description: str     # 描述
author: User         # 作者信息
images: List[str]    # 图片列表
video: dict         # 视频信息
likes: int          # 点赞数
comments: int       # 评论数
collects: int       # 收藏数
created_at: datetime # 创建时间
```

#### Comment 评论信息
```python
comment_id: str      # 评论ID
content: str         # 评论内容
user: User          # 评论者
created_at: datetime # 创建时间
likes: int          # 点赞数
```

## 🔧 高级使用

### 错误处理

```python
from xhs_sdk.exceptions import (
    XhsAuthError,      # 认证错误
    XhsAPIError,       # API 错误
    XhsNetworkError,   # 网络错误
    XhsRateLimitError  # 频率限制
)

try:
    notes = client.search_notes("test")
except XhsAuthError:
    print("Cookie 已失效")
except XhsRateLimitError:
    print("请求过于频繁")
except XhsAPIError as e:
    print(f"API 错误: {e.code} - {e.message}")
```

### 分页获取评论

```python
all_comments = []
cursor = ""

while True:
    page = client.get_note_comments(
        note_id="笔记ID",
        xsec_token="token",
        cursor=cursor
    )
    all_comments.extend(page.comments)
    
    if not page.has_more:
        break
    cursor = page.cursor
    
print(f"总共获取 {len(all_comments)} 条评论")
```

### 批量操作（异步）

```python
async def batch_search():
    async with AsyncXhsClient(cookie="cookie") as client:
        keywords = ["Python", "机器学习", "数据分析"]
        
        # 并发搜索
        results = await asyncio.gather(*[
            client.search_notes(kw, limit=5) 
            for kw in keywords
        ])
        
        for keyword, notes in zip(keywords, results):
            print(f"{keyword}: {len(notes)} 篇笔记")
```

## 🏗 项目架构

```
xhs_sdk/
├── client.py          # 客户端实现
├── models/            # 数据模型
├── api/               # API 处理
├── core/              # 核心功能
├── exceptions.py      # 异常定义
└── constants.py       # 常量配置
```

## 🧪 测试

运行测试：
```bash
# 设置环境变量
export XHS_COOKIE="你的Cookie"

# 运行测试脚本
python test_sdk.py
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

贡献前请注意：
1. 遵循 [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
2. 添加必要的测试
3. 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## ⚖️ 法律声明

使用本 SDK 即表示您同意：
1. 仅将其用于学习和研究目的
2. 不会用于任何商业活动
3. 自行承担使用风险
4. 遵守所有适用的法律法规

## 🙏 致谢

- 感谢开源社区的支持
- 本项目仅供学习交流使用
- 请尊重他人的知识产权

---

**重要提醒：本 SDK 仅供学习使用，请勿用于商业用途！**