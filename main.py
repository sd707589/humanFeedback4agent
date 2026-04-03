from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from src.models import init_db

app = FastAPI(title="众包测试平台", version="0.1.0")

# 初始化数据库
init_db()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("templates/index.html")


# 路由导入
from src.api import agent, user, agent_docs
app.include_router(agent.router, prefix="/api", tags=["Agent"])
app.include_router(user.router, prefix="/api", tags=["User"])
app.include_router(agent_docs.router, prefix="/api")