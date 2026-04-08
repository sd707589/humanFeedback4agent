# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

众包测试平台 (Crowd Test Platform) - 连接AI Agent与普通用户的众包测试平台。AI Agent通过API提交测试任务，用户完成人工测试并获取积分奖励。支持UI评估、内容审核、功能验证、多模态测试等多种测试类型。

## Project Structure (标准工程结构)

```
freelance/
├── CLAUDE.md               # Claude Code 指引文档（自动读取）
├── PRD.md                  # 产品需求文档
├── README.md               # 项目说明文档（随功能完成更新）
├── docs/                   # 其他所有的.md文件目录
├── main.py                 # FastAPI 应用入口
├── run.py                  # 前端程序启动脚本（自动释放端口）
├── pyproject.toml          # 项目配置文件
├── uv.lock                 # 依赖锁定文件
├── .claude/                # Claude 配置目录
├── .env                    # 环境变量配置文件
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── models.py           # 数据模型
│   ├── port_utils.py       # 端口释放工具
│   └── api/                # API 模块
│       ├── __init__.py
│       ├── agent.py        # Agent 相关 API（创建任务、查询结果）
│       ├── agent_docs.py   # Agent 接入说明页面 API
│       └── user.py         # 用户相关 API（登录、答题）
├── templates/              # HTML 模板目录
│   └── index.html          # 用户前端主页面
├── static/                 # 静态文件目录
│   ├── agent-api.md        # Agent API 文档
│   └── agent_sdk.py        # Agent SDK 示例代码
├── test-results/           # 测试结果输出目录
├── crowd_test.db           # SQLite 数据库文件（在 .gitignore 中）
```

### 新会话开始时的阅读顺序
1. `CLAUDE.md` - 当前文件，已经自动读取
2. `PRD.md` - 产品需求文档，了解功能验收标准
3. `README.md` - 项目概况，查看已完成和待完成的功能
4. `progress.md` - 开发决策记录和未决问题（如有）

## Commands

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv sync

# 使用uv add安装新的python库
uv add <package-name>

# 启动服务（推荐，自动释放端口）
python run.py

# 直接使用uvicorn运行
uvicorn main:app --host 0.0.0.0 --port 28178

# 开发模式（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 28178
```
## 测试原则
- 所有的功能完成后都要写测试文件。测试通过后才算成功。
- 不允许使用**硬编码**的测试数据。
- 每个模块最多只能有一个测试脚本。

## 代码规范
- 所有的敏感变量都要从环境变量（.env）中获取，不能直接写在代码中。
- 脚本尽量模块化，每个模块负责一个功能。每个模块都要有自己的测试脚本。
- 不要让一个脚本太长，每个脚本的行数不要超过 800 行。
- 新增新功能后，在新功能脚本测试通过后，所有模块的测试脚本都要测试一遍，都没问题才算成功。