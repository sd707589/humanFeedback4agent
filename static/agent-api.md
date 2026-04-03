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