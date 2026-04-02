#!/usr/bin/env python3
"""
AIPool 日志系统
统一的日志记录、格式化和轮转
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path


LOGS_DIR = Path(".aipool/logs")

# 错误码定义
ERROR_CODES = {
    "E001": "配置文件错误",
    "E002": "SSH 连接失败",
    "E003": "前置检查失败",
    "E004": "部署步骤失败",
    "E005": "验证检查失败",
    "E006": "文件同步失败",
    "E007": "状态文件损坏",
    "E008": "备份不存在",
    "E009": "权限不足",
    "E010": "磁盘空间不足",
}

FIX_SUGGESTIONS = {
    "E001": "请检查 .aipool/inventory.yaml 和 adapter.yaml 格式是否正确",
    "E002": "请检查：1) 服务器 IP 是否正确 2) SSH 密钥是否配置 3) 防火墙是否开放 22 端口",
    "E003": "请根据检查失败的具体项目修复后重试",
    "E004": "请查看日志了解详情，修复后运行 /aipool:deploy 断点续传",
    "E005": "请手动检查服务器状态，确认部署是否正确完成",
    "E006": "请检查网络连接和目标目录权限",
    "E007": "请运行 /aipool:repair 重建状态文件",
    "E008": "无法回滚：没有可用的备份版本",
    "E009": "请确认服务器用户有 sudo 权限",
    "E010": "请清理磁盘空间后重试",
}


class Logger:
    """操作日志记录器"""

    def __init__(self, server_name: str):
        self.server_name = server_name
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        self.log_file = LOGS_DIR / f"{server_name}-{ts}.log"
        self._rotate_old_logs(server_name)

    def _rotate_old_logs(self, server_name: str, keep: int = 10) -> None:
        """保留最近 keep 个日志文件，删除旧的"""
        logs = sorted(LOGS_DIR.glob(f"{server_name}-*.log"))
        for old in logs[:-keep]:
            old.unlink(missing_ok=True)

    def _write(self, level: str, message: str) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {level}: {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def info(self, message: str) -> None:
        self._write("INFO", message)

    def warn(self, message: str) -> None:
        self._write("WARN", message)

    def error(self, message: str) -> None:
        self._write("ERROR", message)


def format_error(code: str, detail: str = "") -> str:
    """格式化错误信息"""
    desc = ERROR_CODES.get(code, "未知错误")
    suggestion = FIX_SUGGESTIONS.get(code, "请查看日志了解详情")
    lines = [f"❌ 错误 [{code}]: {desc}"]
    if detail:
        lines.append(f"   原因: {detail}")
    lines.append(f"   建议: {suggestion}")
    return "\n".join(lines)


def print_step(step_id: str, description: str, status: str = "running") -> None:
    """打印步骤状态"""
    icons = {"running": "⏳", "done": "✓", "failed": "❌", "skip": "⏭"}
    icon = icons.get(status, "•")
    print(f"  {icon} {step_id} - {description}")


def print_section(title: str) -> None:
    print(f"\n[{title}]")


def print_success(message: str) -> None:
    print(f"✓ {message}")


def print_warning(message: str) -> None:
    print(f"⚠ {message}")


def print_error(message: str) -> None:
    print(f"❌ {message}", file=sys.stderr)
