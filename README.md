# 众包测试平台

连接AI Agent与普通用户的众包测试平台。

## 概述

这是一个用于人工测试的众包平台，解决AI Agent无法自动化执行的人工判断测试需求。

- **甲方 (Agent)**: 通过API提交测试任务，获取测试结果
- **乙方 (平台)**: 收集、组织测试任务，管理用户和积分
- **丙方 (用户)**: 通过Web或API（如微信小程序）参与测试，获得积分奖励

## 功能特性

- 支持多种测试类型：UI评估、内容审核、功能验证、多模态测试
- 每次只展示一道题目，快速反馈
- Agent定义每题需要多少人回答，采用多数投票确定正确答案
- 用户完成答题自动获得积分
- 双通道接入：Web端 + 用户API（供小程序调用）

## 技术栈

- **后端**: Python FastAPI
- **数据库**: SQLite
- **前端**: HTML/JS

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 启动服务

```bash
python run.py
```

或使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 28178
```

服务启动后访问: http://localhost:28178

### 3. Agent API 使用

#### 创建测试任务

```bash
curl -X POST http://localhost:28178/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "ui评估",
    "content": "测试两个界面哪个更好看",
    "questions": [
      {
        "content": "A和B哪个界面更好看？",
        "options": ["A界面", "B界面"],
        "required_answers": 3
      }
    ]
  }'
```

#### 查询任务状态

```bash
curl http://localhost:28178/api/tasks/1
```

#### 获取测试结果

```bash
curl http://localhost:28178/api/tasks/1/results
```

### 4. 用户API使用

#### 用户注册

```bash
curl -X POST http://localhost:28178/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

#### 用户登录

```bash
curl -X POST http://localhost:28178/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

获取Token后，在请求头中使用：
```
Authorization: Bearer YOUR_TOKEN
```

#### 获取当前用户信息

```bash
curl http://localhost:28178/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 领取下一道题目

```bash
curl http://localhost:28178/api/questions/next \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 提交答案

```bash
curl -X POST http://localhost:28178/api/answers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question_id": 1, "answer": "A界面", "time_spent": 5}'
```

## API 文档

启动服务后访问 http://localhost:28178/docs 查看完整API文档（Swagger UI）。

## 项目结构

```
.
├── CLAUDE.md               # Claude Code 指引文档
├── PRD.md                  # 产品需求文档
├── README.md               # 项目说明文档（本文件）
├── SPEC_TASK_ALLOCATION.md # 任务分配说明
├── main.py                 # FastAPI 应用入口
├── run.py                  # 启动脚本（自动释放端口）
├── pyproject.toml          # 项目配置
├── uv.lock                 # 依赖锁定
├── src/
│   ├── __init__.py
│   ├── models.py           # 数据模型
│   ├── port_utils.py       # 端口释放工具
│   └── api/
│       ├── __init__.py
│       ├── agent.py        # Agent 相关 API（创建任务、查询结果）
│       ├── agent_docs.py   # Agent 接入说明页面 API
│       └── user.py         # 用户相关 API（登录、答题）
├── templates/
│   └── index.html          # Web 前端页面
├── static/
│   ├── agent-api.md        # Agent API 文档
│   └── agent_sdk.py        # Agent SDK 示例代码
├── docs/                   # 设计文档
├── test-results/           # 测试结果输出
└── crowd_test.db           # SQLite 数据库
```

## 数据库表

- **users**: 用户表（用户名、密码哈希、积分）
- **test_tasks**: 测试任务表（任务类型、内容、状态）
- **test_questions**: 题目表（内容、选项、需回答人数）
- **user_answers**: 用户答案表（用户答案、耗时）

## 积分规则

- 用户每完成一道题目可获得10积分
- 难度根据平均耗时和正确率自动计算（待实现）