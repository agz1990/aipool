# /aipool:status

检查所有服务器的部署状态和版本漂移情况。

## 用法

```
/aipool:status
```

## 实现指南

### 步骤 1：读取服务器清单

```python
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, ".aipool/lib")
from state_manager import load_inventory, load_state
from adapter_parser import load_adapter
from ssh_manager import get_connection, close_all_connections
from builtin_ops import compute_file_hash
from logger import print_section, print_success, print_warning, print_error

inventory = load_inventory()
servers = inventory.get("servers", {})

if not servers:
    print("⚠ 没有配置服务器。请编辑 .aipool/inventory.yaml")
    sys.exit(0)

print(f"\n=== AIPool 服务器状态 ===\n")
```

### 步骤 2：遍历每台服务器

```python
summary = []

for server_name, server_info in servers.items():
    host = server_info["host"]
    user = server_info["user"]
    port = server_info.get("port", 22)
    provider = server_info["pools"][0]["provider"]
    pool_count = server_info["pools"][0]["count"]

    print(f"{server_name} ({provider}, {pool_count} pools)")

    # 读取本地状态
    state = load_state(server_name)
    if not state:
        print(f"  状态: ✗ 未部署")
        summary.append({"server": server_name, "status": "undeployed"})
        print()
        continue

    # 检查是否部署完成
    adapter = load_adapter(Path(f"aipool/{provider}"))
    total_steps = len(adapter.get("deploy_steps", []))
    done_steps = sum(1 for v in state.get("steps", {}).values() if v == "done")

    if done_steps < total_steps:
        print(f"  状态: ⏸ 部署中断")
        print(f"  进度: {done_steps}/{total_steps} 步骤完成")
        summary.append({"server": server_name, "status": "interrupted", "done": done_steps, "total": total_steps})
        print()
        continue

    deployed_at = state.get("deployed_at", "未知")
    adapter_version = state.get("adapter_version", "未知")
    print(f"  状态: ✓ 已部署")
    print(f"  版本: adapter v{adapter_version}")
    print(f"  部署时间: {deployed_at[:16].replace('T', ' ') if deployed_at else '未知'}")
```

### 步骤 3：漂移检测

```python
    # SSH 连接检测漂移
    drift_files = adapter.get("drift_detection", {}).get("files", [])
    saved_hashes = state.get("script_hashes", {})
    drifted = []

    try:
        conn = get_connection(host, user, port)
        for f in drift_files:
            current_hash = compute_file_hash(f, conn.run)
            saved_hash = saved_hashes.get(f, "")
            if current_hash and saved_hash and current_hash != saved_hash:
                drifted.append(f)

        if drifted:
            print(f"  漂移: ⚠ 检测到 {len(drifted)} 个文件变更")
            for f in drifted:
                print(f"    - {f} (已变更)")
            summary.append({"server": server_name, "status": "drifted", "files": drifted})
        else:
            print(f"  漂移: 无")
            summary.append({"server": server_name, "status": "ok"})

    except Exception as e:
        print(f"  漂移: ⚠ 无法连接检测 ({e})")
        summary.append({"server": server_name, "status": "unreachable"})

    print()
```

### 步骤 4：输出建议操作

```python
close_all_connections()

# 建议操作
suggestions = []
for s in summary:
    if s["status"] == "undeployed":
        suggestions.append(f"- {s['server']}: 运行 /aipool:deploy {s['server']}")
    elif s["status"] == "interrupted":
        suggestions.append(f"- {s['server']}: 运行 /aipool:deploy {s['server']} (断点续传)")
    elif s["status"] == "drifted":
        suggestions.append(f"- {s['server']}: 运行 /aipool:sync {s['server']}")
    elif s["status"] == "unreachable":
        suggestions.append(f"- {s['server']}: 检查 SSH 连接")

if suggestions:
    print("建议操作:")
    for s in suggestions:
        print(s)
```

## 输出示例

```
=== AIPool 服务器状态 ===

dev-server-1 (claude-code, 4 pools)
  状态: ✓ 已部署
  版本: adapter v1.0
  部署时间: 2026-04-02 10:30
  漂移: 无

dev-server-2 (claude-code, 2 pools)
  状态: ✓ 已部署
  版本: adapter v1.0
  部署时间: 2026-04-01 15:20
  漂移: ⚠ 检测到 1 个文件变更
    - scripts/setup.sh (已变更)

建议操作:
- dev-server-2: 运行 /aipool:sync dev-server-2
```

## 错误处理

- 服务器无法连接 → 标记为"无法访问"，继续检查其他服务器
- state.json 不存在 → 标记为"未部署"
- adapter.yaml 不存在 → 显示警告，跳过该服务器
