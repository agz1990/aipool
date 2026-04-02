#!/usr/bin/env python3
"""
AIPool SSH 连接管理
封装 SSH 连接、远程命令执行、文件上传/下载
"""

import subprocess
import time
from pathlib import Path


class SSHError(Exception):
    """SSH 操作失败"""
    pass


class SSHConnection:
    """SSH 连接封装，支持连接复用和重试"""

    def __init__(self, host: str, user: str, port: int = 22, max_retries: int = 3):
        self.host = host
        self.user = user
        self.port = port
        self.max_retries = max_retries
        self._control_path = f"/tmp/aipool-ssh-{user}-{host}-{port}.sock"
        self._connected = False

    def _ssh_base_args(self) -> list[str]:
        return [
            "ssh",
            "-o", "ControlMaster=auto",
            "-o", f"ControlPath={self._control_path}",
            "-o", "ControlPersist=60",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            "-p", str(self.port),
        ]

    def connect(self) -> None:
        """建立 SSH 连接（测试连通性）"""
        for attempt in range(1, self.max_retries + 1):
            try:
                result = subprocess.run(
                    self._ssh_base_args() + [f"{self.user}@{self.host}", "echo ok"],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0 and result.stdout.strip() == "ok":
                    self._connected = True
                    return
                raise SSHError(f"SSH 连接失败: {result.stderr.strip()}")
            except subprocess.TimeoutExpired:
                if attempt == self.max_retries:
                    raise SSHError(f"SSH 连接超时（已重试 {self.max_retries} 次）")
                time.sleep(2 ** attempt)

    def run(self, cmd: str, timeout: int = 120) -> str:
        """执行远程命令，返回 stdout"""
        if not self._connected:
            self.connect()

        for attempt in range(1, self.max_retries + 1):
            try:
                result = subprocess.run(
                    self._ssh_base_args() + [f"{self.user}@{self.host}", cmd],
                    capture_output=True, text=True, timeout=timeout
                )
                if result.returncode != 0:
                    raise SSHError(f"远程命令失败 (exit {result.returncode}): {result.stderr.strip()}")
                return result.stdout
            except subprocess.TimeoutExpired:
                if attempt == self.max_retries:
                    raise SSHError(f"远程命令超时: {cmd[:80]}")
                time.sleep(2)
            except SSHError:
                if attempt == self.max_retries:
                    raise
                self._connected = False
                time.sleep(2 ** attempt)
                self.connect()

    def upload(self, local_path: str, remote_path: str, exclude: list[str] | None = None) -> None:
        """上传文件或目录到远程服务器"""
        exclude_args = []
        for e in (exclude or []):
            exclude_args += ["--exclude", e]

        cmd = [
            "rsync", "-avz",
            "-e", f"ssh -o ControlPath={self._control_path} -o StrictHostKeyChecking=no -p {self.port}",
        ] + exclude_args + [
            local_path,
            f"{self.user}@{self.host}:{remote_path}",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise SSHError(f"文件上传失败: {result.stderr.strip()}")

    def download(self, remote_path: str, local_path: str) -> None:
        """从远程服务器下载文件"""
        cmd = [
            "rsync", "-avz",
            "-e", f"ssh -o ControlPath={self._control_path} -o StrictHostKeyChecking=no -p {self.port}",
            f"{self.user}@{self.host}:{remote_path}",
            local_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise SSHError(f"文件下载失败: {result.stderr.strip()}")

    def close(self) -> None:
        """关闭 SSH 连接"""
        if self._connected:
            subprocess.run(
                self._ssh_base_args() + ["-O", "exit", f"{self.user}@{self.host}"],
                capture_output=True
            )
            self._connected = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()


# 连接池：复用已有连接
_connection_pool: dict[str, SSHConnection] = {}


def get_connection(host: str, user: str, port: int = 22) -> SSHConnection:
    """从连接池获取或创建 SSH 连接"""
    key = f"{user}@{host}:{port}"
    if key not in _connection_pool or not _connection_pool[key]._connected:
        conn = SSHConnection(host, user, port)
        conn.connect()
        _connection_pool[key] = conn
    return _connection_pool[key]


def close_all_connections() -> None:
    """关闭所有连接池中的连接"""
    for conn in _connection_pool.values():
        conn.close()
    _connection_pool.clear()
