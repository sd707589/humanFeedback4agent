# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

众包测试平台 (Crowd Test Platform) - A platform connecting AI Agents with regular users for manual testing tasks. Agents submit test tasks via API, users complete tests and earn points.

## Commands

```bash
# Install dependencies
source .venv/bin/activate

# 使用uv add 来安装新的python库
uv add uvicorn

python run.py

# Run the server
uvicorn main:app --host 0.0.0.0 --port 28178

# Development with auto-reload
uvicorn main:app --reload
```

## Architecture

- **main.py** - FastAPI application entry point
- **src/models.py** - SQLAlchemy data models (User, TestTask, TestQuestion, UserAnswer)
- **src/api/agent.py** - Agent API endpoints (create tasks, get results)
- **src/api/user.py** - User API endpoints (register, login, get question, submit answer)
- **templates/index.html** - Web frontend for users
- **Database**: SQLite (crowd_test.db)

### Key Design Patterns

- Token-based authentication (simple in-memory tokens, not JWT)
- Round-robin question allocation with global pointer
- Question locking mechanism with timeout
- Points system: 10 points per completed answer

## API Endpoints

### Agent API
- `POST /api/tasks` - Create test task
- `GET /api/tasks/{id}` - Get task status
- `GET /api/tasks/{id}/results` - Get aggregated results

### User API
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login, returns token
- `GET /api/users/me` - Get current user info
- `GET /api/questions/next` - Get next available question
- `POST /api/answers` - Submit answer

## Important Notes

- The database file (crowd_test.db) is in .gitignore
- Token auth uses simple in-memory dict (tokens = {}) - not suitable for production
- Question timeout defaults to 60 seconds, configurable per question
- Multiple users can work on the same question simultaneously (no strict locking)