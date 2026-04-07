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

### 获取任务结果

```
GET /api/tasks/{task_id}/results
Headers:
  Authorization: Bearer {access_token}

Response (200 OK):
{
  "task_id": 1,
  "task_type": "ui评估",
  "content": "任务描述",
  "status": "running",
  "total_questions": 5,
  "completed_questions": 3,
  "questions": [
    {
      "question_id": 1,
      "content": "题目内容",
      "options": ["选项A", "选项B", "选项C"],
      "required_answers": 5,
      "current_answers_count": 3,
      "answer_distribution": {"选项A": 2, "选项B": 1},
      "correct_answer": "选项A",
      "avg_time_spent": 25.5
    }
  ]
}
```
```

## 错误响应

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误，如题目格式不正确、缺少必要字段等 |
| 401 | 未授权，如 token 无效、过期或未提供 |
| 404 | 资源不存在，如任务ID或题目ID不存在 |
| 422 | 请求体格式错误 |

示例错误响应：

```json
{
  "detail": "用户名或密码错误"
}
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
    "content": "![截图](https://example.com/screenshot.png)\n\n页面加载速度是否可以接受?",
    "options": ["非常快", "快", "一般", "慢"],
    "required_answers": 3,
    "timeout_seconds": 45
  }
]
```

**说明**：`content` 字段支持 **Markdown 格式**，可以插入图片和超链接：
- `![描述](图片URL)` - 插入图片
- `[链接文字](URL)` - 插入超链接
- `**粗体**` - 粗体
- `*斜体*` - 斜体

## Markdown 支持

题目内容 (`content`) 支持基础 Markdown 语法：

- **图片**：`![描述](图片URL)` - 可以是外部 URL 或上传到本服务器的图片
- **链接**：`[链接文字](URL)` - 超链接会在新标签页打开
- **粗体**：`**粗体文字**`
- **斜体**：`*斜体文字*`
- **行内代码**：`` `代码` ``
- 换行：直接换行即可

## 上传图片 API

### 上传图片

```
POST /api/images
Headers:
  Authorization: Bearer {access_token}
Content-Type: multipart/form-data

Form 字段：
  file: 图片文件 (支持格式: jpg, jpeg, png, gif, webp)

Response (200 OK):
{
  "success": true,
  "image_url": "/api/images/abc123.png",
  "image_id": "abc123.png"
}
```

### 获取图片

```
GET /api/images/{image_id}

Response: 图片文件
```

### 存储说明

- 图片存储在服务器 `/tmp/crowd_test_images` 目录
- 超过 **2 天** 的图片会自动清理
- 返回的完整 URL 可以直接用在 Markdown `![alt](url)` 中

## Python SDK 使用示例（含图片上传）

```python
from agent_sdk import CrowdTestClient

# 初始化客户端
client = CrowdTestClient(base_url="http://localhost:28178")
client.login("username", "password")

# 上传本地图片
image_url = client.upload_image("screenshot.png")

# 创建带图片的题目（使用 Markdown）
questions = [
    {
        "content": f"![截图]({image_url})\n\n请评价这个界面：",
        "options": ["非常清晰", "清晰", "一般", "不清晰"],
        "required_answers": 5,
        "timeout_seconds": 60
    }
]

# 创建任务
task = client.create_task(
    task_type="ui评估",
    content="UI 界面评价",
    questions=questions
)

print(f"任务创建成功: {task['id']}")
```

## 批量获取问题结果

```
POST /api/questions/results
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Request Body:
{
  "question_ids": [1, 2, 3, 4, 5],
  "task_id_min": 1,
  "task_id_max": 100,
  "created_after": "2026-04-01",
  "created_before": "2026-04-07"
}
```

**筛选说明**：可以任意组合筛选条件，至少提供一个筛选条件

- `question_ids`: 指定问题ID列表
- `task_id_min` / `task_id_max`: 按任务ID范围筛选
- `created_after` / `created_before`: 按创建时间范围筛选 (ISO 格式)

Response:
```json
{
  "total": 5,
  "questions": [
    {
      "question_id": 1,
      "content": "![截图](url)\n\n题目内容",
      "options": ["非常清晰", "清晰", "一般", "不清晰"],
      "required_answers": 5,
      "current_answers_count": 3,
      "answer_distribution": {"非常清晰": 2, "清晰": 1},
      "correct_answer": "非常清晰",
      "avg_time_spent": 25.5
    }
  ]
}
```

## 列出任务（按条件筛选）

```
POST /api/tasks/list
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Request Body:
{
  "task_id_min": 1,
  "task_id_max": 100,
  "created_after": "2026-04-01",
  "created_before": "2026-04-07",
  "status": "completed"
}
```

Response:
```json
{
  "total": 10,
  "tasks": [
    {
      "id": 1,
      "task_type": "ui评估",
      "content": "任务描述",
      "status": "completed",
      "created_at": "2026-04-03T12:00:00",
      "total_questions": 5,
      "completed_questions": 5
    }
  ]
}
```

## Python SDK 批量获取示例

```python
from agent_sdk import CrowdTestClient

client = CrowdTestClient(base_url="http://localhost:28178")
client.login("username", "password")

# 方式1: 获取指定ID列表的问题结果
results = client.get_questions_results(
    question_ids=[1, 2, 3, 4, 5]
)
print(f"获取到 {results['total']} 个问题")
for q in results['questions']:
    print(f"问题 {q['question_id']}: {q['correct_answer']} - {q['answer_distribution']}")

# 方式2: 获取最近一周创建的所有已完成任务中的问题
results = client.get_questions_results(
    created_after="2026-04-01"
)

# 方式3: 获取ID范围 1-100 内的问题
results = client.get_questions_results(
    task_id_min=1,
    task_id_max=100
)

# 列出 4月份 所有已完成的任务
tasks = client.list_tasks(
    created_after="2026-04-01",
    created_before="2026-04-30",
    status="completed"
)
print(f"找到 {tasks['total']} 个已完成任务")
```