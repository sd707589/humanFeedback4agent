#!/usr/bin/env python3
"""
端口工具 - 杀死占用指定端口的进程
"""

import os
import signal
import subprocess
from typing import List, Optional


def get_pids_by_port(port: int) -> List[int]:
    """获取占用指定端口的所有 PID"""
    pids = []
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-t"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        pids.append(int(line.strip()))
                    except ValueError:
                        pass
    except Exception:
        pass
    return pids


def kill_port(port: int) -> bool:
    """杀死占用指定端口的所有进程

    Returns:
        True - 至少杀死一个进程
        False - 没有找到占用端口的进程
    """
    pids = get_pids_by_port(port)
    if not pids:
        return False

    killed = False
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            killed = True
        except ProcessLookupError:
            pass
        except PermissionError:
            try:
                os.kill(pid, signal.SIGKILL)
                killed = True
            except Exception:
                pass
        except Exception:
            pass

    return killed
