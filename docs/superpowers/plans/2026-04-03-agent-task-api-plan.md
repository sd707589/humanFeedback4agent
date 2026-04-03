# Agent 任务接入 API 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为众包测试平台添加 Agent (OpenClaw) 接入能力，使甲方可以通过自然语言指令让 Agent 自动完成登录和题目上传。

**Architecture:** 在 static 目录提供 Python SDK 和 API 文档，在后端添加 `/api/agent/docs` 端点返回包含动态服务器地址的接入说明页面。

**Tech Stack:** FastAPI, Python, HTML/CSS

---

## 文件结构

```
static/
├── agent-api.md      # 新建: API 文档（供 OpenClaw 读取）
└── agent_sdk.py      # 新建: Python SDK（封装登录和创建任务）

src/
├── api/
│   ├── __init__.py   # 修改: 导出新模块
│   ├── agent_docs.py # 新建: /api/agent/docs 端点
│   ├── agent.py      # 现有: Agent API
│   └── user.py       # 现有: User API
└── models.py         # 现有: 数据模型

main.py               # 修改: 注册新路由

templates/
└── index.html        # 现有: 前端页面（无需修改）
```

---

## 实现任务

### Task 1: 创建 static/agent-api.md (API 文档)

**Files:**
- Create: `static/agent-api.md`

- [ ] **Step 1: 编写 API 文档**

```markdown
# 众包测试平台 Agent API

## 概述

本 skill 用于通过 OpenClaw 自动向众包测试平台上传测试题目。

## 文件

- Python SDK: `http://{server}/static/agent_sdk.py`

## API 端点

### 登录

```
POST /api/users/login
Content-Type: application/json

Request Body:
{
  "username": "your_username",
  "password": "your_password"
}

Response (200 OK):
{
  "access_token": "xxx",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "xxx",
    "points": 0,
    "created_at": "2026-04-03T12:00:00"
  }
}

Error Response (401 Unauthorized):
{
  "detail": "用户名或密码错误"
}
```

### 创建任务

```
POST /api/tasks
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Request Body:
{
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

Response (200 OK):
{
  "id": 1,
  "task_type": "ui评估",
  "content": "任务描述",
  "status": "running",
  "created_at": "2026-04-03T12:00:00"
}

Error Response:
- 401: {"detail": "无效的token"}
- 400: {"detail": "具体错误信息"}
```

## 使用方法

1. 使用 Python SDK 的 `login(username, password)` 登录
2. 使用 `create_task(task_type, content, questions)` 创建任务并添加题目
3. SDK 支持通过命令行参数传入题目 JSON 文件路径

## 题目 JSON 格式示例

```json
[
  {
    "content": "这个按钮的颜色是否清晰?",
    "options": ["非常清晰", "清晰", "一般", "不清晰"],
    "required_answers": 5,
    "timeout_seconds": 60
  },
  {
    "content": "页面加载速度是否可以接受?",
    "options": ["非常快", "快", "一般", "慢"],
    "required_answers": 3,
    "timeout_seconds": 45
  }
]
```
```

- [ ] **Step 2: 提交**

```bash
git add static/agent-api.md
git commit -m "docs: add agent API documentation for OpenClaw"
```

---

### Task 2: 创建 static/agent_sdk.py (Python SDK)

**Files:**
- Create: `static/agent_sdk.py`

- [ ] **Step 1: 编写 Python SDK**

```python
#!/usr/bin/env python3
"""
众包测试平台 Agent SDK
用于 OpenClaw 自动完成任务创建

Usage:
    python agent_sdk.py --username USER --password PASS \
        --task-type ui评估 \
        --task-content "这是一个测试任务" \
        --questions-json questions.json
"""

import os
import sys
import json
import argparse
import requests
from typing import List, Dict, Any, Optional


# 默认 BASE_URL，可通过环境变量 CROWD_TEST_BASE_URL 覆盖
DEFAULT_BASE_URL = os.environ.get("CROWD_TEST_BASE_URL", "http://localhost:28178")


class CrowdTestSDK:
    """众包测试平台 SDK"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        初始化 SDK
        
        Args:
            base_url: 服务器地址，如 http://192.168.1.100:28178
        """
        self.base_url = base_url or DEFAULT_BASE_URL
        self.token = None
        self.username = None
    
    def login(self, username: str, password: str) -> dict:
        """
        登录并获取 token
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            包含 access_token 和 user 信息的字典
        """
        url = f"{self.base_url}/api/users/login"
        data = {"username": username, "password": password}
        
        response = requests.post(url, json=data)
        if response.status_code != 200:
            error_detail = response.json().get("detail", "登录失败")
            raise Exception(f"登录失败: {error_detail}")
        
        result = response.json()
        self.token = result["access_token"]
        self.username = username
        return result
    
    def create_task(self, task_type: str, content: str, questions: List[Dict[str, Any]]) -> dict:
        """
        创建测试任务
        
        Args:
            task_type: 任务类型，如 "ui评估", "内容审核", "功能验证", "多模态"
            content: 任务描述
            questions: 题目列表，每题包含:
                - content: 题目内容
                - options: 选项列表
                - required_answers: 需要多少人回答（默认5）
                - timeout_seconds: 超时秒数（默认60）
                
        Returns:
            包含任务信息的字典
        """
        if not self.token:
            raise Exception("请先调用 login() 登录")
        
        url = f"{self.base_url}/api/tasks"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "task_type": task_type,
            "content": content,
            "questions": questions
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            error_detail = response.json().get("detail", "创建任务失败")
            raise Exception(f"创建任务失败: {error_detail}")
        
        return response.json()
    
    def get_task_status(self, task_id: int) -> dict:
        """获取任务状态"""
        if not self.token:
            raise Exception("请先调用 login() 登录")
        
        url = f"{self.base_url}/api/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"获取任务状态失败: {response.json().get('detail')}")
        
        return response.json()
    
    def get_task_results(self, task_id: int) -> dict:
        """获取任务结果"""
        if not self.token:
            raise Exception("请先调用 login() 登录")
        
        url = f"{self.base_url}/api/tasks/{task_id}/results"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"获取任务结果失败: {response.json().get('detail')}")
        
        return response.json()


def main():
    """OpenClaw 入口函数"""
    parser = argparse.ArgumentParser(
        description="众包测试平台 Agent - 自动创建测试任务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python agent_sdk.py --username testuser --password 123456 \\
        --task-type ui评估 \\
        --task-content "测试APP的登录界面" \\
        --questions-json questions.json

题目JSON文件格式:
    [
        {
            "content": "题目内容",
            "options": ["选项A", "选项B", "选项C"],
            "required_answers": 5,
            "timeout_seconds": 60
        }
    ]
        """
    )
    parser.add_argument("--username", required=True, help="用户名")
    parser.add_argument("--password", required=True, help="密码")
    parser.add_argument("--task-type", default="ui评估", help="任务类型 (default: ui评估)")
    parser.add_argument("--task-content", required=True, help="任务描述")
    parser.add_argument("--questions-json", required=True, help="题目JSON文件路径")
    parser.add_argument("--base-url", default=None, help="服务器地址，如 http://192.168.1.100:28178")
    
    args = parser.parse_args()
    
    # 初始化 SDK
    sdk = CrowdTestSDK(base_url=args.base_url)
    
    # 登录
    print(f"[1/3] 正在登录用户: {args.username}")
    login_result = sdk.login(args.username, args.password)
    print(f"      登录成功，当前积分: {login_result['user']['points']}")
    
    # 读取题目文件
    print(f"[2/3] 读取题目文件: {args.questions_json}")
    try:
        with open(args.questions_json, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        print(f"      错误: 文件不存在: {args.questions_json}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"      错误: JSON 格式错误: {e}")
        sys.exit(1)
    
    if not isinstance(questions, list):
        print("      错误: JSON 根元素必须是数组")
        sys.exit(1)
    
    print(f"      成功读取 {len(questions)} 道题目")
    
    # 创建任务
    print(f"[3/3] 创建任务: {args.task_content}")
    result = sdk.create_task(args.task_type, args.task_content, questions)
    print(f"      任务创建成功!")
    print(f"      - 任务ID: {result['id']}")
    print(f"      - 任务类型: {result['task_type']}")
    print(f"      - 状态: {result['status']}")
    print(f"      - 题目数: {len(questions)}")
    
    return result


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 提交**

```bash
git add static/agent_sdk.py
git commit -m "feat: add Python SDK for OpenClaw agent integration"
```

---

### Task 3: 创建 src/api/agent_docs.py (Agent 接入说明页面)

**Files:**
- Create: `src/api/agent_docs.py`

- [ ] **Step 1: 编写 agent_docs.py**

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/agent/docs", response_class=HTMLResponse)
def agent_docs(request: Request):
    """
    Agent 接入说明页面
    
    动态获取服务器地址，返回包含完整接入说明的 HTML 页面
    """
    # 获取服务器地址
    server_url = str(request.base_url).rstrip("/")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent 接入说明 - 众包测试平台</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .content {{ padding: 30px; }}
        .section {{
            margin-bottom: 24px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .section h2 {{
            font-size: 18px;
            color: #333;
            margin-bottom: 12px;
        }}
        .section p, .section li {{
            color: #666;
            line-height: 1.6;
        }}
        .code-block {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            margin: 12px 0;
        }}
        .copy-btn {{
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }}
        .copy-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        .copy-btn:active {{
            transform: translateY(0);
        }}
        .copy-btn.copied {{
            background: #27ae60;
        }}
        .links {{
            display: flex;
            gap: 16px;
            margin-top: 12px;
        }}
        .links a {{
            color: #667eea;
            text-decoration: none;
        }}
        .links a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Agent 接入说明</h1>
            <p>使用 OpenClaw 自动创建测试任务</p>
        </div>
        <div class="content">
            <div class="section">
                <h2>服务器信息</h2>
                <p>本平台服务器地址: <strong>{server_url}</strong></p>
                <div class="links">
                    <a href="{server_url}/static/agent_sdk.py" target="_blank">下载 Python SDK</a>
                    <a href="{server_url}/static/agent-api.md" target="_blank">查看 API 文档</a>
                </div>
            </div>
            
            <div class="section">
                <h2>使用方法</h2>
                <ol style="margin-left: 20px; color: #666; line-height: 2;">
                    <li>将下方文本复制到 OpenClaw 对话框</li>
                    <li>OpenClaw 会自动下载 Python SDK 和 API 文档</li>
                    <li>根据你的题目数据执行任务创建</li>
                </ol>
            </div>
            
            <div class="section">
                <h2>复制下面的文本给 OpenClaw</h2>
                <div class="code-block" id="instruction-text">请使用众包测试平台的 Agent 功能:
- Python SDK: {server_url}/static/agent_sdk.py
- API 文档: {server_url}/static/agent-api.md

请下载这些文件并使用它们帮助我:
1. 登录用户 [你的用户名]
2. 根据 questions.json 文件创建测试任务

任务类型: ui评估
任务描述: [你的任务描述]
题目文件: questions.json</div>
                <button class="copy-btn" onclick="copyInstructions()">复制说明文本</button>
            </div>
            
            <div class="section">
                <h2>题目 JSON 格式</h2>
                <div class="code-block">[
  {{
    "content": "题目内容",
    "options": ["选项A", "选项B", "选项C"],
    "required_answers": 5,
    "timeout_seconds": 60
  }}
]</div>
            </div>
        </div>
    </div>
    
    <script>
        function copyInstructions() {{
            const text = document.getElementById('instruction-text').textContent;
            navigator.clipboard.writeText(text).then(function() {{
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '已复制!';
                btn.classList.add('copied');
                setTimeout(function() {{
                    btn.textContent = '复制说明文本';
                    btn.classList.remove('copied');
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>
    """
    return html_content
```

- [ ] **Step 2: 提交**

```bash
git add src/api/agent_docs.py
git commit -m "feat: add /api/agent/docs endpoint for agent integration guide"
```

---

### Task 4: 注册新路由

**Files:**
- Modify: `src/api/__init__.py`
- Modify: `main.py`

- [ ] **Step 1: 修改 src/api/__init__.py**

在文件末尾添加新模块导出:

```python
from src.api import agent_docs
```

- [ ] **Step 2: 修改 main.py**

在路由导入部分添加 agent_docs:

```python
from src.api import agent, user, agent_docs
app.include_router(agent_docs.router, prefix="/api", tags=["Agent Docs"])
```

- [ ] **Step 3: 测试端点**

```bash
# 启动服务器
uvicorn main:app --host 0.0.0.0 --port 28178

# 测试访问
curl http://localhost:28178/api/agent/docs
```

预期: 返回包含服务器地址的 HTML 页面

- [ ] **Step 4: 提交**

```bash
git add src/api/__init__.py main.py
git commit -m "feat: register agent_docs router"
```

---

## 验收测试

- [ ] 访问 `/api/agent/docs` 返回包含动态服务器地址的 HTML
- [ ] HTML 包含 Python SDK 和 API 文档的下载链接
- [ ] 复制按钮功能正常
- [ ] `static/agent_sdk.py` 可以独立运行
- [ ] `python agent_sdk.py --help` 显示帮助信息
- [ ] `static/agent-api.md` 包含完整的 API 文档

---

## 相关文件参考

- `src/api/user.py` - 用户登录 API (line 137-156)
- `src/api/agent.py` - 任务创建 API (line 62-95)
- `main.py` - FastAPI 应用入口