#!/usr/bin/env python3
"""
众包测试平台 Agent SDK
用于 OpenClaw 自动完成任务创建
"""

import os
import sys
import json
import argparse
import requests
from typing import List, Dict, Any, Optional


# 默认 BASE_URL，可通过环境变量 CROWD_TEST_BASE_URL 覆盖
DEFAULT_BASE_URL = os.environ.get("CROWD_TEST_BASE_URL", "http://localhost:28178")


class CrowdTestSDK:
    """众包测试平台 SDK"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or DEFAULT_BASE_URL
        self.token = None
        self.username = None

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username: str, password: str) -> dict:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            包含 access_token 和用户信息的字典

        Raises:
            requests.HTTPError: 登录失败时抛出
        """
        url = f"{self.base_url}/api/users/login"
        data = {"username": username, "password": password}

        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        self.token = result.get("access_token")
        self.username = username
        return result

    def create_task(
        self,
        task_type: str,
        content: str,
        questions: List[Dict[str, Any]],
        answer_key: Optional[str] = None
    ) -> dict:
        """
        创建测试任务

        Args:
            task_type: 任务类型，如 "ui评估"
            content: 任务描述
            questions: 题目列表，每个题目包含 content, options, required_answers, timeout_seconds
            answer_key: 可选的答案密钥

        Returns:
            任务信息字典

        Raises:
            requests.HTTPError: 创建失败时抛出
        """
        if not self.token:
            raise ValueError("请先调用 login() 登录")

        url = f"{self.base_url}/api/tasks"
        data = {
            "task_type": task_type,
            "content": content,
            "answer_key": answer_key,
            "questions": questions
        }

        response = requests.post(url, json=data, headers=self._get_headers(), timeout=30)
        response.raise_for_status()

        return response.json()

    def get_task_status(self, task_id: int) -> dict:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息字典

        Raises:
            requests.HTTPError: 获取失败时抛出
        """
        if not self.token:
            raise ValueError("请先调用 login() 登录")

        url = f"{self.base_url}/api/tasks/{task_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()

        return response.json()

    def get_task_results(self, task_id: int) -> dict:
        """
        获取任务结果

        Args:
            task_id: 任务ID

        Returns:
            任务结果字典，包含各题目的统计数据

        Raises:
            requests.HTTPError: 获取失败时抛出
        """
        if not self.token:
            raise ValueError("请先调用 login() 登录")

        url = f"{self.base_url}/api/tasks/{task_id}/results"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()

        return response.json()


def main():
    """OpenClaw 入口函数"""
    parser = argparse.ArgumentParser(
        description="众包测试平台 Agent SDK - 用于自动创建测试任务"
    )
    parser.add_argument(
        "--username", "-u",
        required=True,
        help="用户名"
    )
    parser.add_argument(
        "--password", "-p",
        required=True,
        help="密码"
    )
    parser.add_argument(
        "--task-type", "-t",
        required=True,
        help="任务类型，如 ui评估"
    )
    parser.add_argument(
        "--task-content", "-c",
        required=True,
        help="任务描述"
    )
    parser.add_argument(
        "--questions-json", "-q",
        required=True,
        help="题目 JSON 文件路径或 JSON 字符串"
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API 基础 URL (默认: {DEFAULT_BASE_URL})"
    )

    args = parser.parse_args()

    # 初始化 SDK
    sdk = CrowdTestSDK(base_url=args.base_url)

    # 登录
    print(f"正在登录用户: {args.username}")
    try:
        login_result = sdk.login(args.username, args.password)
        print(f"登录成功! 用户ID: {login_result['user']['id']}")
    except requests.HTTPError as e:
        print(f"登录失败: {e}")
        sys.exit(1)

    # 解析题目
    questions_path = args.questions_json
    try:
        # 尝试作为文件路径读取
        if os.path.isfile(questions_path):
            with open(questions_path, "r", encoding="utf-8") as f:
                questions = json.load(f)
        else:
            # 尝试作为 JSON 字符串解析
            questions = json.loads(questions_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"解析题目失败: {e}")
        sys.exit(1)

    # 创建任务
    print(f"正在创建任务: {args.task_type}")
    try:
        task_result = sdk.create_task(
            task_type=args.task_type,
            content=args.task_content,
            questions=questions
        )
        print(f"任务创建成功! 任务ID: {task_result['id']}")
        print(f"任务状态: {task_result['status']}")
    except requests.HTTPError as e:
        print(f"创建任务失败: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

    # 获取任务结果
    task_id = task_result["id"]
    print(f"\n获取任务结果 (任务ID: {task_id})...")
    try:
        results = sdk.get_task_results(task_id)
        print(f"任务状态: {results['status']}")
        print(f"总题目数: {results['total_questions']}")
        print(f"已完成题目数: {results['completed_questions']}")
    except requests.HTTPError as e:
        print(f"获取结果失败: {e}")


if __name__ == "__main__":
    main()