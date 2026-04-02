# /aipool:sync

同步有漂移的服务器到最新版本。

## 用法

```
/aipool:sync <server-name>
```

## 参数

- `server-name` - 服务器名称

## 实现指南

### 步骤 1：检测漂移

```python
import sys
from pathlib import Path

sys.path.insert(0, ".aipool/lib")
from state_manager import get_server_info, load_state, save_state
from adapter_parser import load_adapter
from ssh_manager import get_connection, close_all_connections
from builtin_ops import compute_file_hash, compute_local_file_hash
from logger import Logger, print_section, print_step, print_success, print_error

server_name = sys.argv[1] if len(sys.argv) > 1 else None
if not server_name:
    print("❌ 错误: 请指定服务器名称")
    print("用法: /aipool:sync <server-name>")
    sys.exit(1)

logger = Logger(server_name)
logger.info(f"开始同步 {server_name}")

server_info = get_server_info(server_name)
state = load_state(server_name)
if not state:
    print(f"❌ 服务器 {server_name} 尚未部署")
    sys.exit(1)

provider = state["provider"]
adapter = load_adapter(Path(f"aipool/{provider}"))
drift_files = adapter.get("drift_detection", {}).get("files", [])

print(f"\n=== 同步 {server_name} ===\n")

# SSH 连接
conn = get_connection(server_info["host"], server_info["user"], server_info.get("port", 22))

# 检测漂移
drifted = []
for f in drift_files:
    local_hash = compute_local_file_hash(f)
    remote_hash = compute_file_hash(f, conn.run)
    saved_hash = state.get("script_hashes", {}).get(f, "")

    if local_hash != remote_hash:
        drifted.append({"file": f, "local": local_hash, "remote": remote_hash})

if not drifted:
    print("✓ 服务器已是最新版本，无需同步")
    close_all_connections()
    sys.exit(0)
```

### 步骤 2：显示差异

```python
print("检测到以下文件有变更:\n")
for d in drifted:
    print(f"  {d['file']}")
    print(f"    本地: {d['local'][:8]}...")
    print(f"    远程: {d['remote'][:8]}...")
    print()
```

### 步骤 3：确认同步

```python
answer = input("确认同步这些文件到服务器？(y/n) > ").strip().lower()
if answer != "y":
    print("同步已取消")
    sys.exit(0)
```

### 步骤 4：同步文件

```python
print_section("同步文件")
for d in drifted:
    f = d["file"]
    print_step(f, f, "running")
    try:
        # 上传文件
        conn.upload(f, f)
        print_step(f, f"已同步", "done")
        logger.info(f"同步文件: {f}")
    except Exception as e:
        print_step(f, str(e), "failed")
        logger.error(f"同步失败 {f}: {e}")
        print_error(f"同步失败: {e}")
        sys.exit(6)
```

### 步骤 5：更新 hash

```python
print_section("更新 Hash")
for f in drift_files:
    new_hash = compute_file_hash(f, conn.run)
    state["script_hashes"][f] = new_hash
    print_step(f"hash_{f}", f"{f}: {new_hash[:8]}...", "done")

save_state(server_name, state)
```

### 步骤 6：运行健康检查

```python
print_section("健康检查")
for check in adapter.get("health_checks", []):
    check_id = check["id"]
    print_step(check_id, check_id, "running")
    try:
        if check["type"] == "builtin":
            from builtin_ops import run_builtin
            params = {k: v for k, v in check.items() if k not in ("id", "type", "action")}
            result = run_builtin(check["action"], params, conn.run)
        else:
            conn.run(check["script"])
        print_step(check_id, "通过", "done")
    except Exception as e:
        print_step(check_id, str(e), "failed")
        print(f"⚠ 健康检查失败: {e}")

close_all_connections()
logger.info("同步完成")

print("\n✓ 同步完成！")
```

## 错误处理

- 服务器未部署 → 提示先运行 /aipool:deploy
- 无漂移 → 提示已是最新版本
- 同步失败 → 保留旧版本，报告错误
- 健康检查失败 → 显示警告，但不回滚
