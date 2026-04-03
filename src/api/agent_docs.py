from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/agent/docs", response_class=HTMLResponse)
def agent_docs(request: Request):
    """
    Agent 接入说明页面

    动态获取服务器地址，返回包含完整接入说明的 HTML 页面
    """
    # 获取服务器地址
    server_url = str(request.base_url).rstrip("/")

    html_content = f"""<!DOCTYPE html>
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
                <div class="server-info">
                    <div class="label">当前服务器地址：</div>
                    <div class="value">{server_url}</div>
                </div>
            </div>

            <div class="section">
                <h2>下载 SDK 和文档</h2>
                <div class="links">
                    <a href="/static/agent_sdk.py" class="link-btn" download>Python SDK</a>
                    <a href="/static/agent-api.md" class="link-btn">API 文档</a>
                </div>
                <p>点击上方链接下载 Python SDK 或查看 API 文档。SDK 提供了简洁的 Python API 用于与平台交互。</p>
            </div>

            <div class="section">
                <h2>快速开始 (OpenClaw)</h2>
                <p>在 OpenClaw 或其他 Agent 环境中，使用以下指令完成任务创建和结果获取：</p>
                <div class="code-block">
                    <span class="comment"># 1. 创建测试任务</span>
                    <span class="keyword">python</span> agent_sdk.py create-task --questions <span class="string">"问题1|问题2|问题3"</span> --answers <span class="string">"答案1|答案2|答案3"</span> --base-url <span class="string">{server_url}</span>

                    <span class="comment"># 2. 查看任务状态</span>
                    <span class="keyword">python</span> agent_sdk.py get-task --task-id <span class="string">&lt;task_id&gt;</span> --base-url <span class="string">{server_url}</span>

                    <span class="comment"># 3. 获取聚合结果</span>
                    <span class="keyword">python</span> agent_sdk.py get-results --task-id <span class="string">&lt;task_id&gt;</span> --base-url <span class="string">{server_url}</span>
                </div>
                <button class="copy-btn" onclick="copyToClipboard(this)">复制</button>
            </div>

            <div class="section">
                <h2>编程接口调用示例</h2>
                <div class="code-block">
<span class="comment"># 使用 Python SDK</span>
<span class="keyword">from</span> agent_sdk <span class="keyword">import</span> CrowdTestSDK

<span class="comment"># 初始化 SDK</span>
sdk = CrowdTestSDK(base_url=<span class="string">"{server_url}"</span>)

<span class="comment"># 创建测试任务</span>
task = sdk.create_task(
    questions=[<span class="string">"问题1"</span>, <span class="string">"问题2"</span>, <span class="string">"问题3"</span>],
    answers=[<span class="string">"答案1"</span>, <span class="string">"答案2"</span>, <span class="string">"答案3"</span>]
)
<span class="keyword">print</span>(f<span class="string">"Task ID: {{task['task_id']}}"</span>)

<span class="comment"># 获取任务状态</span>
status = sdk.get_task_status(task[<span class="string">"task_id"</span>])

<span class="comment"># 获取聚合结果</span>
results = sdk.get_results(task[<span class="string">"task_id"</span>])
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
    <span class="string">"title"</span>: <span class="string">"测试任务标题"</span>,
    <span class="string">"questions"</span>: [
        <span class="string">"问题1: 请问这个功能是否正常工作？"</span>,
        <span class="string">"问题2: 页面加载速度是否满意？"</span>,
        <span class="string">"问题3: 界面设计是否符合您的预期？"</span>
    ],
    <span class="string">"answers"</span>: [
        <span class="string">"正常工作"</span>,
        <span class="string">"满意"</span>,
        <span class="string">"符合"</span>
    ],
    <span class="string">"question_timeout"</span>: <span class="number">60</span>,
    <span class="string">"description"</span>: <span class="string">"可选的任务描述"</span>
<span class="keyword">}}</span>
                    </div>
                </div>
                <div class="json-example" style="margin-top: 15px;">
                    <h3>获取结果响应 (GET /api/tasks/{{id}}/results)</h3>
                    <div class="code-block">
<span class="keyword">{{</span>
    <span class="string">"task_id"</span>: <span class="string">"xxx"</span>,
    <span class="string">"status"</span>: <span class="string">"completed"</span>,
    <span class="string">"results"</span>: [
        <span class="keyword">{{</span>
            <span class="string">"question"</span>: <span class="string">"问题1"</span>,
            <span class="string">"expected_answer"</span>: <span class="string">"答案1"</span>,
            <span class="string">"user_answers"</span>: [<span class="string">"答案1"</span>, <span class="string">"答案1"</span>, <span class="string">"答案2"</span>],
            <span class="string">"answer_count"</span>: <span class="number">3</span>
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
        function copyToClipboard(btn) {{
            // 找到相邻的代码块
            const codeBlock = btn.previousElementSibling;
            const text = codeBlock.textContent;

            navigator.clipboard.writeText(text).then(function() {{
                const originalText = btn.textContent;
                btn.textContent = '已复制!';
                btn.style.background = '#28a745';

                setTimeout(function() {{
                    btn.textContent = originalText;
                    btn.style.background = '';
                }}, 2000);
            }}).catch(function(err) {{
                console.error('复制失败:', err);
            }});
        }}
    </script>
</body>
</html>
    """
    return html_content