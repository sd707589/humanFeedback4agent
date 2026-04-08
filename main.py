from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

from src.models import init_db

# 加载环境变量
load_dotenv()
SERVER_IP = os.getenv("SERVER_IP", "localhost")
PORT = os.getenv("PORT", "28178")

app = FastAPI(title="众包测试平台", version="0.1.0")

# 初始化数据库
init_db()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    # 读取模板并替换环境变量
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # 替换占位符（只替换我们定义的两个，避免和 CSS/JS 中的 {} 冲突）
    html_content = html_content.replace("{default_server_ip}", SERVER_IP)
    html_content = html_content.replace("{port}", str(PORT))
    return HTMLResponse(content=html_content)


# 路由导入
from src.api import agent, user, agent_docs
app.include_router(agent.router, prefix="/api", tags=["Agent"])
app.include_router(user.router, prefix="/api", tags=["User"])
app.include_router(agent_docs.router, prefix="/api")