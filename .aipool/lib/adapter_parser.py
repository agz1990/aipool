#!/usr/bin/env python3
"""
AIPool Adapter 解释器
负责解析 adapter.yaml 并执行部署步骤
"""

import re
from pathlib import Path
from typing import Any

import yaml


VALID_BUILTIN_ACTIONS = {
    "mkdir", "rsync", "check_os", "check_disk", "check_user_exists", "restore_backup"
}

VALID_STEP_TYPES = {"builtin", "script", "manual"}


def load_adapter(provider_dir: str | Path) -> dict:
    """加载并验证 adapter.yaml"""
    adapter_path = Path(provider_dir) / "adapter.yaml"
    if not adapter_path.exists():
        raise FileNotFoundError(f"未找到 adapter.yaml: {adapter_path}")

    with open(adapter_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    validate_adapter(data)
    return data


def validate_adapter(data: dict) -> None:
    """验证 adapter.yaml schema"""
    if not isinstance(data, dict):
        raise ValueError("adapter.yaml 必须是字典格式")

    # 必填字段
    for field in ["provider", "version", "auth_type", "deploy_steps", "drift_detection"]:
        if field not in data:
            raise ValueError(f"adapter.yaml 缺少必填字段: {field}")

    if data["auth_type"] not in ("interactive", "api-key"):
        raise ValueError(f"auth_type 必须是 'interactive' 或 'api-key'")

    # 验证步骤
    step_ids = set()
    for step in data.get("deploy_steps", []):
        _validate_step(step, step_ids)

    for step in data.get("pre_checks", []):
        _validate_step(step, set())

    for step in data.get("health_checks", []):
        _validate_step(step, set())

    # 验证漂移检测
    dd = data["drift_detection"]
    if dd.get("method") != "file_hash":
        raise ValueError("drift_detection.method 目前仅支持 'file_hash'")
    if not isinstance(dd.get("files"), list):
        raise ValueError("drift_detection.files 必须是列表")


def _validate_step(step: dict, seen_ids: set) -> None:
    """验证单个步骤"""
    if "id" not in step:
        raise ValueError(f"步骤缺少 id 字段: {step}")
    if step["id"] in seen_ids:
        raise ValueError(f"步骤 ID 重复: {step['id']}")
    seen_ids.add(step["id"])

    step_type = step.get("type")
    if step_type not in VALID_STEP_TYPES:
        raise ValueError(f"步骤 {step['id']} 的 type 无效: {step_type}")

    if step_type == "builtin":
        action = step.get("action")
        if action not in VALID_BUILTIN_ACTIONS:
            raise ValueError(f"步骤 {step['id']} 的 action 无效: {action}。有效值: {VALID_BUILTIN_ACTIONS}")
    elif step_type == "script":
        if "script" not in step:
            raise ValueError(f"步骤 {step['id']} 缺少 script 字段")
    elif step_type == "manual":
        if "instruction" not in step:
            raise ValueError(f"步骤 {step['id']} 缺少 instruction 字段")


def render_template(text: str, variables: dict) -> str:
    """替换模板变量 {{ var_name }}"""
    def replace(match):
        key = match.group(1).strip()
        if key not in variables:
            raise ValueError(f"未定义的模板变量: {key}")
        return str(variables[key])

    return re.sub(r"\{\{\s*(\w+)\s*\}\}", replace, text)


def get_template_variables(server_name: str, provider: str, pool_count: int, pool_index: int | None = None) -> dict:
    """构建模板变量字典"""
    variables = {
        "pools": pool_count,
        "provider": provider,
        "server": server_name,
    }
    if pool_index is not None:
        variables["index"] = pool_index
    return variables


def get_pending_steps(adapter: dict, state: dict, section: str = "deploy_steps") -> list[dict]:
    """获取尚未完成的步骤列表"""
    steps = adapter.get(section, [])
    completed = state.get("steps", {})
    return [s for s in steps if completed.get(s["id"]) != "done"]


def expand_for_each_steps(steps: list[dict], pool_count: int) -> list[dict]:
    """展开 for_each: pool 步骤为多个步骤（每个池子一个）"""
    expanded = []
    for step in steps:
        if step.get("for_each") == "pool":
            for i in range(1, pool_count + 1):
                expanded.append({**step, "_pool_index": i, "id": f"{step['id']}_pool_{i}"})
        else:
            expanded.append(step)
    return expanded
