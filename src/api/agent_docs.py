import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

router = APIRouter()

# 加载环境变量
load_dotenv()
default_server_ip = os.getenv("SERVER_IP", "localhost")
port = os.getenv("PORT", "28178")


@router.get("/agent/docs", response_class=HTMLResponse)
def agent_docs(request: Request):
    """
    Agent 接入说明页面

    动态获取服务器地址，返回包含完整接入说明的 HTML 页面
    """

    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent 接入说明 - 众包测试平台</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #667eea;
            font-size: 1.4em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .section p {{
            margin-bottom: 15px;
            color: #555;
        }}
        .server-info {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .server-info .label {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .server-info .value {{
            font-family: "Monaco", "Menlo", monospace;
            font-size: 1.2em;
            color: #333;
            background: #fff;
            padding: 10px 15px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
        .links {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        .link-btn {{
            display: inline-flex;
            align-items: center;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .link-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        .code-block {{
            background: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: "Monaco", "Menlo", monospace;
            font-size: 0.9em;
            line-height: 1.5;
            margin-bottom: 15px;
        }}
        .code-block .comment {{
            color: #5c6370;
        }}
        .code-block .string {{
            color: #98c379;
        }}
        .code-block .keyword {{
            color: #c678dd;
        }}
        .code-block .number {{
            color: #d19a66;
        }}
        .copy-btn {{
            display: inline-block;
            padding: 8px 16px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
            margin-left: 10px;
            transition: background 0.2s;
        }}
        .copy-btn:hover {{
            background: #218838;
        }}
        .copy-btn:active {{
            background: #1e7e34;
        }}
        .json-example {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
        }}
        .json-example h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        .note {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px 20px;
            border-radius: 0 4px 4px 0;
            margin-bottom: 20px;
        }}
        .note strong {{
            color: #856404;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .server-ip-input {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 15px 0;
            padding: 12px 16px;
            background: #f0f7ff;
            border-radius: 8px;
            border: 1px solid #c5d9f5;
        }}
        .server-ip-input label {{
            font-weight: 500;
            color: #333;
            white-space: nowrap;
        }}
        .server-ip-input input {{
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
        }}
        .server-ip-input input:focus {{
            outline: none;
            border-color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Agent 接入说明</h1>
            <p>众包测试平台 - AI Agent 自动化接入指南</p>
        </div>
        <div class="content">
            <div class="section">
                <h2>服务器信息</h2>
                <div class="server-ip-input">
                    <label>服务器 IP：</label>
                    <input type="text" id="server-ip" value="{default_server_ip}" placeholder="输入服务器IP">
                </div>
                <div class="server-info">
                    <div class="label">当前服务器地址：</div>
                    <div class="value" id="server-url">http://{default_server_ip}:{port}</div>
                </div>
                <div class="links">
                    <a href="http://{default_server_ip}:{port}/static/agent-api.md" class="link-btn" id="api-docs-link" target="_blank">📄 查看 API 文档</a>
                    <a href="http://{default_server_ip}:{port}/static/agent_sdk.py" class="link-btn" id="sdk-download-link" target="_blank">⬇️ 下载 Python SDK</a>
                </div>
            </div>

            <div class="section">
                <h2>Agent 接入说明（复制给 OpenClaw）</h2>
                <p>请复制以下文本粘贴到 OpenClaw 对话框：</p>
                <div class="code-block" style="white-space: pre-wrap;" id="agent-instruction">
请使用众包测试平台的 Agent 功能:
- Python SDK: http://{default_server_ip}:{port}/static/agent_sdk.py
- API 文档: http://{default_server_ip}:{port}/static/agent-api.md

请下载这些文件并使用它们帮助我:
1. 登录用户 [你的用户名]
2. 根据 questions.json 文件创建测试任务

任务类型: ui评估
任务描述: [你的任务描述]
题目文件: questions.json</div>
                <button class="copy-btn" onclick="copyToClipboard(this)">复制</button>
            </div>

            <div class="section">
                <h2>快速开始 (OpenClaw)</h2>
                <p>在 OpenClaw 或其他 Agent 环境中，使用以下指令完成任务创建和结果获取：</p>
                <div class="code-block" id="quick-start-code">
                    <span class="comment"># 1. 创建测试任务（需要先准备 questions.json 文件）</span>
                    <span class="keyword">python</span> agent_sdk.py --username <span class="string">your_username</span> --password <span class="string">your_password</span> --task-type <span class="string">ui评估</span> --task-content <span class="string">"测试APP登录界面"</span> --questions-json <span class="string">questions.json</span> --base-url <span class="string">http://{default_server_ip}:{port}</span>

                    <span class="comment"># 2. 查看任务状态</span>
                    <span class="keyword">python</span> agent_sdk.py --username <span class="string">your_username</span> --password <span class="string">your_password</span> ...（创建任务后会返回 task_id）

                    <span class="comment"># 3. 使用 SDK 编程方式获取结果</span>
                    <span class="keyword">from</span> agent_sdk <span class="keyword">import</span> CrowdTestSDK
                    sdk = CrowdTestSDK(base_url=<span class="string">"http://{default_server_ip}:{port}"</span>)
                    sdk.login(<span class="string">"username"</span>, <span class="string">"password"</span>)
                    results = sdk.get_task_results(<span class="number">1</span>)
                </div>
                <button class="copy-btn" onclick="copyToClipboard(this)">复制</button>
            </div>

            <div class="section">
                <h2>编程接口调用示例</h2>
                <div class="code-block" id="code-example">
<span class="comment"># 使用 Python SDK</span>
<span class="keyword">from</span> agent_sdk <span class="keyword">import</span> CrowdTestSDK

<span class="comment"># 初始化 SDK</span>
sdk = CrowdTestSDK(base_url=<span class="string">"http://{default_server_ip}:{port}"</span>)

<span class="comment"># 登录</span>
login_result = sdk.login(<span class="string">"username"</span>, <span class="string">"password"</span>)
<span class="keyword">print</span>(f<span class="string">"登录成功，当前积分: {{login_result['user']['points']}}"</span>)

<span class="comment"># 定义题目</span>
questions = [
    <span class="keyword">{{</span>
        <span class="string">"content"</span>: <span class="string">"这个按钮的颜色是否清晰?"</span>,
        <span class="string">"options"</span>: [<span class="string">"非常清晰"</span>, <span class="string">"清晰"</span>, <span class="string">"一般"</span>, <span class="string">"不清晰"</span>],
        <span class="string">"required_answers"</span>: <span class="number">5</span>,
        <span class="string">"timeout_seconds"</span>: <span class="number">60</span>
    <span class="keyword">}}</span>,
    <span class="keyword">{{</span>
        <span class="string">"content"</span>: <span class="string">"页面加载速度是否可以接受?"</span>,
        <span class="string">"options"</span>: [<span class="string">"非常快"</span>, <span class="string">"快"</span>, <span class="string">"一般"</span>, <span class="string">"慢"</span>],
        <span class="string">"required_answers"</span>: <span class="number">3</span>,
        <span class="string">"timeout_seconds"</span>: <span class="number">45</span>
    <span class="keyword">}}</span>
]

<span class="comment"># 创建测试任务</span>
task = sdk.create_task(
    task_type=<span class="string">"ui评估"</span>,
    content=<span class="string">"测试APP登录界面"</span>,
    questions=questions
)
<span class="keyword">print</span>(f<span class="string">"任务创建成功，ID: {{task['id']}}"</span>)

<span class="comment"># 获取任务状态</span>
status = sdk.get_task_status(task[<span class="string">"id"</span>])

<span class="comment"># 获取聚合结果</span>
results = sdk.get_task_results(task[<span class="string">"id"</span>])
                </div>
                <button class="copy-btn" onclick="copyToClipboard(this)">复制</button>
            </div>

            <div class="section">
                <h2>问题 JSON 格式示例</h2>
                <p>如果您使用原生 API，以下是问题格式的 JSON 示例：</p>
                <div class="json-example">
                    <h3>创建任务请求 (POST /api/tasks)</h3>
                    <div class="code-block">
<span class="keyword">{{</span>
    <span class="string">"task_type"</span>: <span class="string">"ui评估"</span>,
    <span class="string">"content"</span>: <span class="string">"测试APP登录界面"</span>,
    <span class="string">"questions"</span>: [
        <span class="keyword">{{</span>
            <span class="string">"content"</span>: <span class="string">"这个按钮的颜色是否清晰?"</span>,
            <span class="string">"options"</span>: [<span class="string">"非常清晰"</span>, <span class="string">"清晰"</span>, <span class="string">"一般"</span>, <span class="string">"不清晰"</span>],
            <span class="string">"required_answers"</span>: <span class="number">5</span>,
            <span class="string">"timeout_seconds"</span>: <span class="number">60</span>
        <span class="keyword">}}</span>
    ]
<span class="keyword">}}</span>
                    </div>
                </div>
                <div class="json-example" style="margin-top: 15px;">
                    <h3>获取结果响应 (GET /api/tasks/{id}/results)</h3>
                    <div class="code-block">
<span class="keyword">{{</span>
    <span class="string">"task_id"</span>: <span class="number">1</span>,
    <span class="string">"task_type"</span>: <span class="string">"ui评估"</span>,
    <span class="string">"content"</span>: <span class="string">"测试APP登录界面"</span>,
    <span class="string">"status"</span>: <span class="string">"running"</span>,
    <span class="string">"total_questions"</span>: <span class="number">2</span>,
    <span class="string">"completed_questions"</span>: <span class="number">1</span>,
    <span class="string">"questions"</span>: [
        <span class="keyword">{{</span>
            <span class="string">"question_id"</span>: <span class="number">1</span>,
            <span class="string">"content"</span>: <span class="string">"这个按钮的颜色是否清晰?"</span>,
            <span class="string">"options"</span>: [<span class="string">"非常清晰"</span>, <span class="string">"清晰"</span>, <span class="string">"一般"</span>, <span class="string">"不清晰"</span>],
            <span class="string">"required_answers"</span>: <span class="number">5</span>,
            <span class="string">"current_answers_count"</span>: <span class="number">3</span>,
            <span class="string">"answer_distribution"</span>: <span class="keyword">{{</span><span class="string">"非常清晰"</span>: <span class="number">2</span>, <span class="string">"清晰"</span>: <span class="number">1</span><span class="keyword">}}</span>,
            <span class="string">"correct_answer"</span>: <span class="string">"非常清晰"</span>,
            <span class="string">"avg_time_spent"</span>: <span class="number">25.5</span>
        <span class="keyword">}}</span>
    ]
<span class="keyword">}}</span>
                    </div>
                </div>
                <button class="copy-btn" onclick="copyToClipboard(this)">复制</button>
            </div>

            <div class="section">
                <div class="note">
                    <strong>注意：</strong>任务需要用户完成回答后才能获取聚合结果。您可以通过轮询任务状态或 WebSocket 等待任务完成。
                </div>
            </div>
        </div>
        <div class="footer">
            众包测试平台 &copy; 2026
        </div>
    </div>

    <script>
        function copyToClipboard(btn) {
            // 找到相邻的代码块
            const codeBlock = btn.previousElementSibling;
            const text = codeBlock.textContent;

            navigator.clipboard.writeText(text).then(function() {
                const originalText = btn.textContent;
                btn.textContent = '已复制!';
                btn.style.background = '#28a745';

                setTimeout(function() {
                    btn.textContent = originalText;
                    btn.style.background = '';
                }, 2000);
            }).catch(function(err) {
                console.error('复制失败:', err);
            });
        }

        // 动态更新服务器地址
        function updateServerAddress() {
            const ip = document.getElementById('server-ip').value || '{default_server_ip}';
            const port = '{port}';
            const serverUrl = `http://${ip}:${port}`;

            // 更新服务器地址显示
            document.getElementById('server-url').textContent = serverUrl;

            // 更新链接
            document.getElementById('api-docs-link').href = `${serverUrl}/static/agent-api.md`;
            document.getElementById('sdk-download-link').href = `${serverUrl}/static/agent_sdk.py`;

            // 更新 Agent 接入说明
            const agentInstruction = `请使用众包测试平台的 Agent 功能:
- Python SDK: ${serverUrl}/static/agent_sdk.py
- API 文档: ${serverUrl}/static/agent-api.md

请下载这些文件并使用它们帮助我:
1. 登录用户 [你的用户名]
2. 根据 questions.json 文件创建测试任务

任务类型: ui评估
任务描述: [你的任务描述]
题目文件: questions.json`;
            document.getElementById('agent-instruction').textContent = agentInstruction;

            // 更新快速开始代码
            const quickStartCode = `                    # 1. 创建测试任务（需要先准备 questions.json 文件）
                    python agent_sdk.py --username your_username --password your_password --task-type ui评估 --task-content "测试APP登录界面" --questions-json questions.json --base-url "${serverUrl}"

                    # 2. 查看任务状态
                    python agent_sdk.py --username your_username --password your_password ...（创建任务后会返回 task_id）

                    # 3. 使用 SDK 编程方式获取结果
                    from agent_sdk import CrowdTestSDK
                    sdk = CrowdTestSDK(base_url="${serverUrl}")
                    sdk.login("username", "password")
                    results = sdk.get_task_results(1)`;
            document.getElementById('quick-start-code').textContent = quickStartCode;

            // 更新编程接口调用示例
            const codeExample = `# 使用 Python SDK
from agent_sdk import CrowdTestSDK

# 初始化 SDK
sdk = CrowdTestSDK(base_url="${serverUrl}")

# 登录
login_result = sdk.login("username", "password")
print(f"登录成功，当前积分: {login_result['user']['points']}")

# 定义题目
questions = [
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

# 创建测试任务
task = sdk.create_task(
    task_type="ui评估",
    content="测试APP登录界面",
    questions=questions
)
print(f"任务创建成功，ID: {task['id']}")

# 获取任务状态
status = sdk.get_task_status(task["id"])

# 获取聚合结果
results = sdk.get_task_results(task["id"])`;
            document.getElementById('code-example').textContent = codeExample;
        }

        // 监听 IP 输入变化
        document.addEventListener('DOMContentLoaded', function() {
            const ipInput = document.getElementById('server-ip');
            if (ipInput) {
                ipInput.addEventListener('input', updateServerAddress);
            }
        });
    </script>
</body>
</html>
    """
    return html_content.format(default_server_ip=default_server_ip, port=port)
