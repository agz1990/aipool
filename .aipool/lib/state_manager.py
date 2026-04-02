#!/usr/bin/env python3
"""
AIPool 状态管理系统
负责 inventory.yaml 读取验证和 state.json 读写
"""

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


AIPOOL_DIR = Path(".aipool")
STATE_DIR = AIPOOL_DIR / "state"
LOGS_DIR = AIPOOL_DIR / "logs"
BACKUPS_DIR = AIPOOL_DIR / "backups"
INVENTORY_FILE = AIPOOL_DIR / "inventory.yaml"


def load_inventory() -> dict:
    """读取并验证 inventory.yaml"""
    if not INVENTORY_FILE.exists():
        raise FileNotFoundError(f"未找到 {INVENTORY_FILE}，请先运行 /aipool:init")

    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    servers = data.get("servers", {})
    if not isinstance(servers, dict):
        raise ValueError("inventory.yaml 格式错误：servers 必须是字典")

    for name, info in servers.items():
        _validate_server(name, info)

    return data


def _validate_server(name: str, info: dict) -> None:
    """验证单个服务器配置"""
    if not isinstance(info, dict):
        raise ValueError(f"服务器 {name} 配置格式错误")
    required = ["host", "user", "pools"]
    for field in required:
        if field not in info:
            raise ValueError(f"服务器 {name} 缺少必填字段: {field}")
    if not isinstance(info["pools"], list) or len(info["pools"]) == 0:
        raise ValueError(f"服务器 {name} 的 pools 必须是非空列表")
    for pool in info["pools"]:
        if "provider" not in pool or "count" not in pool:
            raise ValueError(f"服务器 {name} 的 pool 缺少 provider 或 count")


def get_server_info(server_name: str) -> dict:
    """获取指定服务器信息"""
    inventory = load_inventory()
    servers = inventory.get("servers", {})
    if server_name not in servers:
        available = list(servers.keys())
        raise ValueError(f"服务器 '{server_name}' 不存在。可用服务器: {available}")
    return servers[server_name]


def state_file_path(server_name: str) -> Path:
    return STATE_DIR / f"{server_name}.json"


def load_state(server_name: str) -> dict | None:
    """读取服务器部署状态，不存在返回 None"""
    path = state_file_path(server_name)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(server_name: str, state: dict) -> None:
    """保存服务器部署状态（先备份旧版本）"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = state_file_path(server_name)

    # 备份旧状态
    if path.exists():
        _backup_state(server_name, path)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _backup_state(server_name: str, path: Path) -> None:
    """备份状态文件"""
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup_path = BACKUPS_DIR / f"{server_name}-{ts}.json"
    shutil.copy2(path, backup_path)


def init_state(server_name: str, provider: str, adapter_version: str, pool_count: int) -> dict:
    """初始化新的部署状态"""
    return {
        "provider": provider,
        "adapter_version": adapter_version,
        "pool_count": pool_count,
        "deployed_at": None,
        "script_hashes": {},
        "pools": {str(i): {"auth": "pending"} for i in range(1, pool_count + 1)},
        "steps": {},
    }


def update_step_status(state: dict, step_id: str, status: str) -> dict:
    """更新步骤状态：pending / in_progress / done / failed"""
    state["steps"][step_id] = status
    return state


def mark_deployed(state: dict) -> dict:
    """标记部署完成时间"""
    state["deployed_at"] = datetime.now(timezone.utc).isoformat()
    return state


def get_step_status(state: dict, step_id: str) -> str:
    """获取步骤状态，默认 pending"""
    return state.get("steps", {}).get(step_id, "pending")


def is_step_done(state: dict, step_id: str) -> bool:
    return get_step_status(state, step_id) == "done"
