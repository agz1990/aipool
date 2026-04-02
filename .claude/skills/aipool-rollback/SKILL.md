# /aipool:rollback

回滚服务器到上一个版本。

## 用法

```
/aipool:rollback <server-name>
```

## 参数

- `server-name` - 服务器名称

## 实现指南

### 步骤 1：检查备份

```python
import sys
import json
from pathlib import Path

sys.path.insert(0, ".aipool/lib")
from state_manager import get_server_info, load_state, save_state, BACKUPS_DIR
from adapter_parser import load_adapter
from ssh_manager import get_connection, close_all_connections
from builtin_ops import run_builtin
from logger import Logger, print_section, print_step, print_success, print_error

server_name = sys.argv[1] if len(sys.argv) > 1 else None
if not server_name:
    print("❌ 错误: 请指定服务器名称")
    print("用法: /aipool:rollback <server-name>")
    sys.exit(1)

logger = Logger(server_name)
logger.info(f"开始回滚 {server_name}")

server_info = get_server_info(server_name)
current_state = load_state(server_name)
if not current_state:
    print(f"❌ 服务器 {server_name} 尚未部署，无法回滚")
    sys.exit(1)

# 查找最近的备份
backups = sorted(BACKUPS_DIR.glob(f"{server_name}-*.json"), reverse=True)
if not backups:
    print(f"❌ 没有可用的备份版本")
    print("建议: 备份在每次部署时自动创建")
    sys.exit(8)

backup_file = backups[0]
with open(backup_file) as f:
    backup_state = json.load(f)
```

### 步骤 2：显示版本信息

```python
current_version = current_state.get("adapter_version", "未知")
current_time = current_state.get("deployed_at", "未知")[:16].replace("T", " ")

backup_version = backup_state.get("adapter_version", "未知")
backup_time = backup_file.stem.split("-", 1)[1] if "-" in backup_file.stem else "未知"

print(f"\n=== 回滚 {server_name} ===\n")
print(f"当前版本: adapter v{current_version} ({current_time})")
print(f"备份版本: adapter v{backup_version} ({backup_time})")
print()

answer = input("确认回滚到备份版本？(y/n) > ").strip().lower()
if answer != "y":
    print("回滚已取消")
    sys.exit(0)
```

### 步骤 3：执行回滚步骤

```python
provider = current_state["provider"]
adapter = load_adapter(Path(f"aipool/{provider}"))
rollback_config = adapter.get("rollback", {})

if not rollback_config:
    print("⚠ adapter.yaml 未定义回滚策略")
    sys.exit(0)

print_section("执行回滚")
conn = get_connection(server_info["host"], server_info["user"], server_info.get("port", 22))

for step in rollback_config.get("steps", []):
    step_type = step.get("type")
    print_step(step.get("action", "rollback"), "执行中", "running")
    try:
        if step_type == "builtin":
            params = {k: v for k, v in step.items() if k not in ("type",)}
            result = run_builtin(step.get("action"), params, conn.run)
        else:
            conn.run(step.get("script", ""))
        print_step(step.get("action", "rollback"), "完成", "done")
        logger.info(f"回滚步骤完成: {step}")
    except Exception as e:
        print_step(step.get("action", "rollback"), str(e), "failed")
        print_error(f"回滚失败: {e}")
        logger.error(f"回滚失败: {e}")
        sys.exit(4)
```

### 步骤 4：恢复状态文件

```python
print_section("恢复状态")
save_state(server_name, backup_state)
print_step("restore_state", "状态文件已恢复", "done")
logger.info("状态文件已恢复到备份版本")
```

### 步骤 5：验证回滚结果

```python
print_section("健康检查")
for check in adapter.get("health_checks", []):
    check_id = check["id"]
    print_step(check_id, check_id, "running")
    try:
        if check["type"] == "builtin":
            params = {k: v for k, v in check.items() if k not in ("id", "type", "action")}
            run_builtin(check["action"], params, conn.run)
        else:
            conn.run(check["script"])
        print_step(check_id, "通过", "done")
    except Exception as e:
        print_step(check_id, str(e), "failed")
        print(f"⚠ 健康检查失败: {e}")

close_all_connections()
logger.info("回滚完成")

print(f"\n✓ 回滚完成！")
print(f"  服务器: {server_name}")
print(f"  已恢复到: adapter v{backup_version}")
```

## 错误处理

- 服务器未部署 → 提示无法回滚
- 无备份 → 提示"无可用备份"
- 回滚步骤失败 → 报告错误，不继续
- 健康检查失败 → 显示警告，建议手动检查
