# 🧪 众包测试平台

> 反馈是agent自动化迭代循环中关键的一环，人类反馈有时也不可或缺。本项目就是人类快速反馈agent的一个工具。

[🇺🇸 English Version (英文版本)](README.md)

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![UV](https://img.shields.io/badge/Built%20with-UV-purple.svg)](https://github.com/astral-sh/uv)

## 📋 目录

- [📖 概述](#-概述)
- [✨ 功能特性](#-功能特性)
- [🚀 快速开始](#-快速开始)
- [📡 API 使用](#-api-使用)
- [📊 积分规则](#-积分规则)
- [🏗️ 项目结构](#️-项目结构)
- [🗄️ 数据库表](#️-数据库表)
- [🎯 使用场景](#-使用场景)
- [🛣️ 开发路线图](#️-开发路线图)
- [🤝 贡献](#-贡献)
- [📄 许可证](#-许可证)

## 📖 概述

这是一个用于人工测试的众包平台，解决AI Agent无法自动化执行的人工判断测试需求。

**三种角色协同：**

- 🏷️ **甲方 (Agent)**：通过API提交测试任务，获取聚合测试结果
- 🏢 **乙方 (平台)**：收集、组织测试任务，管理用户和积分
- 👤 **丙方 (用户)**：通过Web或API（如微信小程序）参与测试，获得积分奖励

## ✨ 功能特性

- ✅ **多种测试类型**：支持UI评估、内容审核、功能验证、多模态测试
- ✅ **一题一页体验**：每次只展示一道题目，快速反馈
- ✅ **多数投票机制**：Agent定义每题需要多少人回答，自动统计聚合结果
- ✅ **积分激励系统**：用户完成答题自动获得积分奖励
- ✅ **双通道接入**：同时支持Web端直接访问和第三方API（供小程序调用）
- ✅ **开箱即用**：SQLite数据库，无需额外配置即可运行

## 🚀 快速开始

### 前置要求

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)（推荐用于依赖管理）

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

服务启动后访问:
- 🌐 前端页面：http://localhost:28178
- 📚 API文档（Swagger UI）：http://localhost:28178/docs

## 📡 API 使用
启动网页后，输入服务器（局域网）IP地址，即可获得Agent API的接入说明。
### Agent API（创建任务和获取结果）
以openClaw agent为例，直接在对话框中输入
```bash
根据 http://<服务器IP地址>/static/agent-api.md 接入 API，下载 http://<服务器IP地址>/static/agent_sdk.py 获取 Python SDK。

如果之前已经下载过 agent_sdk.py，请重新下载新版本来获取图片上传功能：
wget -O agent_sdk.py http://<服务器IP地址>/static/agent_sdk.py
```

## API 文档

启动服务后访问 http://localhost:28178/docs 查看完整API文档（Swagger UI）。

## 📊 积分规则

| 操作 | 积分奖励 |
|------|---------|
| 完成一道题目 | +10 积分 |

> 🔄 **待实现**：难度根据平均耗时和正确率自动计算，可调整积分奖励系数

## 🏗️ 项目结构

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

## 🗄️ 数据库表

- **users**: 用户表（用户名、密码哈希、积分）
- **test_tasks**: 测试任务表（任务类型、内容、状态）
- **test_questions**: 题目表（内容、选项、需回答人数）
- **user_answers**: 用户答案表（用户答案、耗时）

## 🎯 使用场景

- **AI Agent开发者**：需要人工验证AI生成内容的质量
- **UI/UX设计师**：收集用户对不同设计方案的偏好
- **内容平台**：进行AI生成内容的人工审核
- **多模态AI研究**：收集人类对图像/音频/视频的判断数据

## 🛣️ 开发路线图

- [ ] 难度评估系统（根据平均耗时和正确率自动计算）
- [ ] 积分排行榜
- [ ] 任务过期机制
- [ ] 用户画像分析
- [ ] WebSocket实时推送
- [ ] 任务分类筛选
- [ ] 管理员后台
- [ ] 数据导出功能

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 快速Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL工具包
- [uv](https://github.com/astral-sh/uv) - 极速Python包管理器
