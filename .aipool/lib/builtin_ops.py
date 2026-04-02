#!/usr/bin/env python3
"""
AIPool Builtin 操作库
实现 adapter.yaml 中 type: builtin 的所有内置操作
"""

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Callable


class BuiltinError(Exception):
    """Builtin 操作执行失败"""
    pass


def run_builtin(action: str, params: dict, ssh_runner: Callable | None = None) -> str:
    """
    执行 builtin 操作
    ssh_runner: 可选的远程执行函数，签名为 (cmd: str) -> str
    返回操作结果描述
    """
    handlers = {
        "mkdir": _mkdir,
        "rsync": _rsync,
        "check_os": _check_os,
        "check_disk": _check_disk,
        "check_user_exists": _check_user_exists,
        "restore_backup": _restore_backup,
    }
    if action not in handlers:
        raise BuiltinError(f"未知的 builtin 操作: {action}")
    return handlers[action](params, ssh_runner)


def _mkdir(params: dict, ssh_runner: Callable | None) -> str:
    """创建目录"""
    paths = params.get("paths", [])
    mode = params.get("mode", "755")
    if not paths:
        raise BuiltinError("mkdir 操作缺少 paths 参数")

    paths_str = " ".join(f'"{p}"' for p in paths)
    cmd = f"mkdir -p {paths_str} && chmod {mode} {paths_str}"

    if ssh_runner:
        ssh_runner(cmd)
    else:
        for p in paths:
            Path(p).mkdir(parents=True, exist_ok=True)
            os.chmod(p, int(mode, 8))

    return f"已创建目录: {', '.join(paths)}"


def _rsync(params: dict, ssh_runner: Callable | None) -> str:
    """同步文件"""
    source = params.get("source")
    dest = params.get("dest")
    exclude = params.get("exclude", [])

    if not source or not dest:
        raise BuiltinError("rsync 操作缺少 source 或 dest 参数")

    exclude_args = " ".join(f'--exclude="{e}"' for e in exclude)
    # rsync 需要在本地执行（上传到远程）
    host = params.get("_host")
    user = params.get("_user")

    if host and user:
        cmd = f"rsync -avz {exclude_args} {source} {user}@{host}:{dest}"
    else:
        cmd = f"rsync -avz {exclude_args} {source} {dest}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise BuiltinError(f"rsync 失败: {result.stderr}")

    return f"已同步 {source} → {dest}"


def _check_os(params: dict, ssh_runner: Callable | None) -> str:
    """检查操作系统"""
    allowed = params.get("allowed", ["linux", "darwin"])

    cmd = "uname -s | tr '[:upper:]' '[:lower:]'"
    if ssh_runner:
        os_name = ssh_runner(cmd).strip().lower()
    else:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        os_name = result.stdout.strip().lower()

    # 标准化：linux 系统 uname 返回 "linux"，macOS 返回 "darwin"
    allowed_lower = [a.lower() for a in allowed]
    if os_name not in allowed_lower:
        raise BuiltinError(f"操作系统不支持: {os_name}。允许的系统: {allowed}")

    return f"操作系统检查通过: {os_name}"


def _check_disk(params: dict, ssh_runner: Callable | None) -> str:
    """检查磁盘空间"""
    path = params.get("path", "/")
    min_gb = params.get("min_gb", 10)

    # 使用 python3 跨平台获取磁盘空间（本地和远程都支持）
    cmd = f"python3 -c \"import shutil; s=shutil.disk_usage('{path}'); print(s.free // 1024**3)\""
    if ssh_runner:
        available_str = ssh_runner(cmd).strip()
    else:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        available_str = result.stdout.strip()

    try:
        available_gb = int(available_str)
    except ValueError:
        raise BuiltinError(f"无法解析磁盘空间: {available_str}")

    if available_gb < min_gb:
        raise BuiltinError(f"磁盘空间不足: {path} 可用 {available_gb}GB，需要 {min_gb}GB")

    return f"磁盘空间检查通过: {path} 可用 {available_gb}GB"


def _check_user_exists(params: dict, ssh_runner: Callable | None) -> str:
    """检查用户是否存在"""
    users = params.get("users", [])
    if not users:
        raise BuiltinError("check_user_exists 操作缺少 users 参数")

    missing = []
    for user in users:
        cmd = f"id {user} &>/dev/null && echo ok || echo missing"
        if ssh_runner:
            result = ssh_runner(cmd).strip()
        else:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            result = proc.stdout.strip()

        if result != "ok":
            missing.append(user)

    if missing:
        raise BuiltinError(f"以下用户不存在: {', '.join(missing)}")

    return f"用户检查通过: {', '.join(users)}"


def _restore_backup(params: dict, ssh_runner: Callable | None) -> str:
    """恢复备份"""
    from_path = params.get("from")
    to_path = params.get("to")

    if not from_path or not to_path:
        raise BuiltinError("restore_backup 操作缺少 from 或 to 参数")

    cmd = f"test -d {from_path} && rsync -av {from_path}/ {to_path}/"
    if ssh_runner:
        ssh_runner(cmd)
    else:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise BuiltinError(f"恢复备份失败: {result.stderr}")

    return f"已恢复备份: {from_path} → {to_path}"


def compute_file_hash(file_path: str, ssh_runner: Callable | None = None) -> str:
    """计算文件 MD5 hash"""
    cmd = f"md5sum {file_path} 2>/dev/null | awk '{{print $1}}' || md5 -q {file_path} 2>/dev/null"
    if ssh_runner:
        return ssh_runner(cmd).strip()
    else:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()


def compute_local_file_hash(file_path: str) -> str:
    """计算本地文件 MD5 hash"""
    path = Path(file_path)
    if not path.exists():
        return ""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
