# Agent 任务接入 API 设计

## 概述

为众包测试平台(乙方)提供 Agent (OpenClaw) 接入能力，使甲方可以通过自然语言指令让 Agent 自动完成登录和题目上传。

## 需求背景

- 乙方平台部署在内网，甲方的 OpenClaw 也部署在同局域网
- 甲方已有题目 JSON 数据，需要批量上传到平台
- 甲方希望复制一段说明文本给 OpenClaw，Agent 即可自动完成登录和出题

## 技术方案

### 1. 文件结构

在 `static/` 目录下新增两个文件：

```
static/
├── agent-api.md      # API 文档（供 OpenClaw 读取并组成 skill）
└── agent_sdk.py      # Python SDK（封装登录和创建任务的函数）
```

### 2. 添加 /api/agent/docs 端点

创建新的 API 端点 `/api/agent/docs`，返回 Agent 接入说明的 HTML 页面，显示：
- 服务器局域网地址（动态获取请求的 Host）
- skill 文件下载链接
- 复制按钮，一键复制说明文本

该端点可直接在浏览器访问，供甲方复制说明文本。

### 3. agent-api.md 内容

```markdown
# 众包测试平台 Agent API

## 概述

本 skill 用于通过 OpenClaw 自动向众包测试平台上传测试题目。

## 文件

- Python SDK: `http://<SERVER>/static/agent_sdk.py`

## API 端点

### 登录

```
POST /api/users/login
Body: {"username": "xxx", "password": "xxx"}
Response: {
  "access_token": "xxx",
  "token_type": "bearer",
  "user": {"id": 1, "username": "xxx", "points": 0}
}
```

### 创建任务

```
POST /api/tasks
Headers: Authorization: Bearer <token>
Body: {
  "task_type": "ui评估",
  "content": "任务描述",
  "questions": [
    {
      "content": "题目内容",
      "options": ["选项A", "选项B", "选项C"],
      "required_answers": 5,
      "timeout_seconds": 60
    }
  ]
}
Response: {
  "id": 1,
  "task_type": "ui评估",
  "content": "任务描述",
  "status": "running",
  "created_at": "2026-04-03T12:00:00"
}
```

### 错误响应

- 401 Unauthorized: {"detail": "无效的用户名或密码"}
- 400 Bad Request: {"detail": "具体错误信息"}

## 使用方法

1. 使用 Python SDK 的 `login(username, password)` 登录
2. 使用 `create_task(task_type, content, questions)` 创建任务并添加题目
```

### 4. agent_sdk.py 结构

SDK 需要支持 BASE_URL 动态配置，优先级：
1. 构造函数传入 `base_url` 参数
2. 环境变量 `CROWD_TEST_BASE_URL`
3. 默认 `http://localhost:28178`（本地调试用）

```python
#!/usr/bin/env python3
"""
众包测试平台 Agent SDK
用于 OpenClaw 自动完成任务创建
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional

# 默认 BASE_URL，可通过环境变量 CROWD_TEST_BASE_URL 覆盖
DEFAULT_BASE_URL = os.environ.get("CROWD_TEST_BASE_URL", "http://localhost:28178")

class CrowdTestSDK:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or DEFAULT_BASE_URL
        self.token = None

    def login(self, username: str, password: str) -> dict:
        """登录并获取 token"""
        # 实现...

    def create_task(self, task_type: str, content: str, questions: List[Dict]) -> dict:
        """创建测试任务"""
        # 实现...

# 供 OpenClaw 调用的入口函数
def main():
    """OpenClaw 入口函数，支持命令行参数或环境变量传入题目数据"""
    import argparse

    parser = argparse.ArgumentParser(description="众包测试平台 Agent")
    parser.add_argument("--username", required=True, help="用户名")
    parser.add_argument("--password", required=True, help="密码")
    parser.add_argument("--task-type", default="ui评估", help="任务类型")
    parser.add_argument("--task-content", required=True, help="任务描述")
    parser.add_argument("--questions-json", required=True, help="题目 JSON 文件路径")
    parser.add_argument("--base-url", default=None, help="服务器地址")

    args = parser.parse_args()

    # 初始化 SDK
    sdk = CrowdTestSDK(base_url=args.base_url)

    # 登录
    print(f"正在登录用户: {args.username}")
    login_result = sdk.login(args.username, args.password)
    print(f"登录成功，Token: {login_result.get('access_token', '')[:20]}...")

    # 读取题目文件
    with open(args.questions_json, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # 创建任务
    print(f"正在创建任务: {args.task_content}")
    result = sdk.create_task(args.task_type, args.task_content, questions)
    print(f"任务创建成功，ID: {result.get('id')}, 题目数: {len(questions)}")

    return result
```

## 实现步骤

1. **创建 static/agent-api.md** - API 文档
2. **创建 static/agent_sdk.py** - Python SDK（支持 base_url 动态配置）
3. **创建 src/api/agent_docs.py** - 实现 `/api/agent/docs` 端点，返回 Agent 接入说明 HTML 页面
4. **在 main.py 注册新路由**

## 验收标准

- [ ] `/api/agent/docs` 端点可访问，显示 Agent 接入说明
- [ ] 说明文本包含动态获取的服务器地址
- [ ] 包含 static/agent_sdk.py 和 static/agent-api.md 下载链接
- [ ] 复制按钮可一键复制说明文本
- [ ] agent_sdk.py 包含 login 和 create_task 函数，支持 base_url 配置
- [ ] agent-api.md 包含完整的 API 文档（请求/响应格式、错误响应）
- [ ] OpenClaw 读取 skill 后可正常调用 API