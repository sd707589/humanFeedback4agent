#!/usr/bin/env python
"""
启动脚本 - 自动释放端口后启动服务

使用方法:
    python run.py
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

from src.port_utils import kill_port

# 加载环境变量
load_dotenv()
PORT = int(os.getenv("PORT", "28178"))

if __name__ == "__main__":
    # 释放端口
    print(f"正在释放端口 {PORT}...")
    if kill_port(PORT):
        print(f"端口 {PORT} 已释放，启动服务...")
    else:
        print("警告: 端口释放遇到问题，继续尝试启动...")

    # 启动 uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )