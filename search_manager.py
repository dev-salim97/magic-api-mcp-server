#!/usr/bin/env python3
"""Magic-API 搜索客户端 CLI。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

import requests

# Ensure magicapi_tools can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from magicapi_tools.utils.http_client import MagicAPIHTTPClient, MagicAPISettings

class MagicAPISearchClient:
    """Magic-API 搜索客户端。"""

    def __init__(self, settings: MagicAPISettings) -> None:
        self.settings = settings
        self.http_client = MagicAPIHTTPClient(settings)
        self.session = self.http_client.session
        # Update headers if needed, though MagicAPIHTTPClient sets basic ones
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "magicapi-search-manager/1.0",
        })
        # No manual login needed, handled by MagicAPIHTTPClient


    def search(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """在所有 API 脚本中搜索关键词。

        Args:
            keyword: 搜索关键词

        Returns:
            搜索结果列表，每个结果包含 id、text、line 字段
        """
        if not keyword.strip():
            print("❌ 搜索关键词不能为空")
            return []

        url = f"{self.settings.base_url}/search"
        data = {'keyword': keyword}

        try:
            response = self.session.post(url, data=data, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            result = response.json()
            if result.get("code") == 1:
                results = result.get("data", [])
                # 应用 limit 限制
                if limit > 0:
                    results = results[:limit]
                return results
            else:
                print(f"❌ API 返回错误: {result.get('message', '未知错误')}")
                return []
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return []

    def search_todo(self, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索所有 TODO 注释。

        Returns:
            TODO 注释列表，每个结果包含 id、text、line 字段
        """
        url = f"{self.settings.base_url}/todo"

        try:
            response = self.session.get(url, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            result = response.json()
            if result.get("code") == 1:
                results = result.get("data", [])
                # 应用 limit 限制
                if limit > 0:
                    results = results[:limit]
                return results
            else:
                print(f"❌ API 返回错误: {result.get('message', '未知错误')}")
                return []
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return []


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="Magic-API 搜索客户端")
    parser.add_argument("--search", help="在所有API脚本中搜索关键词")
    parser.add_argument("--todo", action="store_true", help="搜索所有TODO注释")
    parser.add_argument("--limit", type=int, default=5, help="返回结果的最大数量（默认5条）")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")
    return parser.parse_args()


def build_client(settings: MagicAPISettings) -> MagicAPISearchClient:
    """构建搜索客户端。"""
    return MagicAPISearchClient(settings)


def perform_search(client: MagicAPISearchClient, keyword: str, limit: int, json_output: bool) -> None:
    """执行关键词搜索。"""
    print(f"🔍 搜索关键词: '{keyword}' (限制 {limit} 条)")
    results = client.search(keyword, limit)

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("📭 没有找到匹配的结果")
            return

        print(f"📋 找到 {len(results)} 个匹配结果:")
        for i, result in enumerate(results, 1):
            print(f"{i}. 文件ID: {result.get('id', 'N/A')}")
            print(f"   行号: {result.get('line', 'N/A')}")
            print(f"   内容: {result.get('text', 'N/A')}")
            print()


def perform_todo_search(client: MagicAPISearchClient, limit: int, json_output: bool) -> None:
    """执行TODO搜索。"""
    print(f"📝 搜索TODO注释... (限制 {limit} 条)")
    results = client.search_todo(limit)

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("📭 没有找到TODO注释")
            return

        print(f"📋 找到 {len(results)} 个TODO注释:")
        for i, result in enumerate(results, 1):
            print(f"{i}. 文件ID: {result.get('id', 'N/A')}")
            print(f"   行号: {result.get('line', 'N/A')}")
            print(f"   内容: {result.get('text', 'N/A')}")
            print()


def main() -> None:
    """主函数。"""
    args = parse_args()

    # 验证参数组合
    operations = [bool(args.search), args.todo]
    if sum(operations) != 1:
        print("❌ 必须且只能指定一个操作: --search 或 --todo")
        sys.exit(1)

    settings = MagicAPISettings.from_env()
    client = build_client(settings)

    try:
        if args.search:
            perform_search(client, args.search, args.limit, args.json)
        elif args.todo:
            perform_todo_search(client, args.limit, args.json)
    except KeyboardInterrupt:
        print("\n⏹️ 操作已取消")
        sys.exit(1)


if __name__ == "__main__":
    main()
