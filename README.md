# 🧪 Crowd Test Platform

> A crowdsourced testing platform connecting AI Agents and human users.

[🇨🇳 中文版本 (Chinese Version)](README_CN.md)

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![UV](https://img.shields.io/badge/Built%20with-UV-purple.svg)](https://github.com/astral-sh/uv)

## 📋 Table of Contents

- [📖 Overview](#-overview)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📡 API Usage](#-api-usage)
- [📊 Points System](#-points-system)
- [🏗️ Project Structure](#️-project-structure)
- [🗄️ Database Schema](#️-database-schema)
- [🎯 Use Cases](#-use-cases)
- [🛣️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 📖 Overview

This is a crowdsourced platform for human testing, addressing the need for human judgment in testing tasks that AI Agents cannot automate.

**Three-role collaboration:**

- 🏷️ **Party A (Agent)**: Submit testing tasks via API and get aggregated results
- 🏢 **Party B (Platform)**: Collect and organize tasks, manage users and points
- 👤 **Party C (User)**: Participate via Web or API (e.g., WeChat Mini Program) and earn points

## ✨ Features

- ✅ **Multiple Test Types**: Supports UI evaluation, content moderation, functional verification, multimodal testing
- ✅ **One Question Per Page**: Single question display for quick feedback
- ✅ **Majority Voting**: Agent defines required answers per question, automatically aggregates results
- ✅ **Points Incentive**: Users earn points automatically after completing tasks
- ✅ **Dual-channel Access**: Supports both Web interface and third-party API (for mini-programs)
- ✅ **Ready to Use**: SQLite database, runs without extra configuration

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

### 1. Install Dependencies

```bash
uv sync
```

### 2. Start the Server

```bash
python run.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 28178
```

After the server starts, visit:
- 🌐 Frontend: http://localhost:28178
- 📚 API Docs (Swagger UI): http://localhost:28178/docs

## 📡 API Usage

### Agent API (Create Tasks & Get Results)

#### Create a Test Task

```bash
curl -X POST http://localhost:28178/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "ui_evaluation",
    "content": "Test which interface looks better",
    "questions": [
      {
        "content": "Which interface looks better, A or B?",
        "options": ["Interface A", "Interface B"],
        "required_answers": 3
      }
    ]
  }'
```

#### Check Task Status

```bash
curl http://localhost:28178/api/tasks/1
```

#### Get Test Results

```bash
curl http://localhost:28178/api/tasks/1/results
```

### User API (Login & Answering)

#### User Registration

```bash
curl -X POST http://localhost:28178/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

#### User Login

```bash
curl -X POST http://localhost:28178/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

After getting the token, use it in request headers:
```
Authorization: Bearer YOUR_TOKEN
```

#### Get Current User Info

```bash
curl http://localhost:28178/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Next Question

```bash
curl http://localhost:28178/api/questions/next \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Submit Answer

```bash
curl -X POST http://localhost:28178/api/answers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question_id": 1, "answer": "Interface A", "time_spent": 5}'
```

## API Documentation

After starting the server, visit http://localhost:28178/docs for complete API documentation (Swagger UI).

## 📊 Points System

| Action | Points Reward |
|--------|---------------|
| Complete one question | +10 points |

> 🔄 **To be implemented**: Difficulty is automatically calculated based on average time spent and accuracy, points reward coefficient can be adjusted

## 🏗️ Project Structure

```
.
├── CLAUDE.md               # Claude Code guide
├── PRD.md                  # Product Requirements Document
├── README.md               # This file (English)
├── README_CN.md            # Chinese version
├── SPEC_TASK_ALLOCATION.md # Task allocation description
├── main.py                 # FastAPI application entry
├── run.py                  # Startup script (auto release port)
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock file
├── src/
│   ├── __init__.py
│   ├── models.py           # Data models
│   ├── port_utils.py       # Port release utility
│   └── api/
│       ├── __init__.py
│       ├── agent.py        # Agent related APIs (create task, get result)
│       ├── agent_docs.py   # Agent documentation page API
│       └── user.py         # User related APIs (login, answer)
├── templates/
│   └── index.html          # Web frontend page
├── static/
│   ├── agent-api.md        # Agent API documentation
│   └── agent_sdk.py        # Agent SDK example code
├── docs/                   # Design documents
├── test-results/           # Test results output
└── crowd_test.db           # SQLite database
```

## 🗄️ Database Schema

- **users**: User table (username, password hash, points)
- **test_tasks**: Test task table (task type, content, status)
- **test_questions**: Question table (content, options, required answers)
- **user_answers**: User answer table (user answer, time spent)

## 🎯 Use Cases

- **AI Agent Developers**: Need human verification for AI-generated content quality
- **UI/UX Designers**: Collect user preferences for different design方案
- **Content Platforms**: Human moderation for AI-generated content
- **Multimodal AI Research**: Collect human judgments on image/audio/video content

## 🛣️ Roadmap

- [ ] Difficulty evaluation system (auto-calculated based on average time and accuracy)
- [ ] Points leaderboard
- [ ] Task expiration mechanism
- [ ] User profile analysis
- [ ] WebSocket real-time push
- [ ] Task categorization and filtering
- [ ] Admin dashboard
- [ ] Data export functionality

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for Python
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
