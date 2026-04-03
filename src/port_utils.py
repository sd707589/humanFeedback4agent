"""
端口占用释放工具
用于解除指定端口的占用
"""
import subprocess
import signal
import os
import sys


def kill_port(port: int) -> bool:
    """
    释放指定端口的占用

    Args:
        port: 端口号

    Returns:
        bool: 是否成功释放端口
    """
    try:
        # 查找占用端口的进程
        if sys.platform == "win32":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split("\n")
            for line in lines:
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                        print(f"已终止占用端口 {port} 的进程 (PID: {pid})")
                        return True
        else:
            # Linux/Mac 使用 lsof 或 ss
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"已终止占用端口 {port} 的进程 (PID: {pid})")
                    except ProcessLookupError:
                        pass
                return True
            else:
                # 尝试使用 ss 命令
                result = subprocess.run(
                    ["ss", "-tlnp"],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split("\n"):
                    if f":{port}" in line and "LISTEN" in line:
                        # 尝试提取 PID
                        import re
                        match = re.search(r'pid=(\d+)', line)
                        if match:
                            pid = match.group(1)
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                                print(f"已终止占用端口 {port} 的进程 (PID: {pid})")
                            except ProcessLookupError:
                                pass
                        return True

        print(f"端口 {port} 未被占用")
        return True

    except Exception as e:
        print(f"释放端口 {port} 失败: {e}")
        return False


def kill_port_uvicorn(port: int = 28178) -> bool:
    """
    专门用于释放 uvicorn 服务的端口

    Args:
        port: 端口号，默认 28178

    Returns:
        bool: 是否成功释放端口
    """
    return kill_port(port)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 28178
    kill_port(port)