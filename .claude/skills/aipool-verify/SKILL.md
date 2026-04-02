# /aipool:verify

验证指定服务器的部署健康度。

## 用法

```
/aipool:verify <server-name>
```

## 参数

- `server-name` - 服务器名称

## 实现指南

### 步骤 1：读取配置

```python
import sys
from pathlib import Path

sys.path.insert(0, ".aipool/lib")
from state_manager import get_server_info, load_state
from adapter_parser import load_adapter
from ssh_manager import get_connection, close_all_connections
from builtin_ops import run_builtin
from logger import Logger, print_section, print_step, print_success, print_warning

server_name = sys.argv[1] if len(sys.argv) > 1 else None
if not server_name:
    print("❌ 错误: 请指定服务器名称")
    print("用法: /aipool:verify <server-name>")
    sys.exit(1)

logger = Logger(server_name)
logger.info(f"开始验证 {server_name}")

server_info = get_server_info(server_name)
state = load_state(server_name)
if not state:
    print(f"❌ 服务器 {server_name} 尚未部署")
    sys.exit(1)

provider = state["provider"]
adapter = load_adapter(Path(f"aipool/{provider}"))

print(f"\n=== 验证 {server_name} ===\n")

# SSH 连接
conn = get_connection(server_info["host"], server_info["user"], server_info.get("port", 22))
```

### 步骤 2：执行健康检查

```python
print_section("健康检查")
health_checks = adapter.get("health_checks", [])
if not health_checks:
    print("⚠ adapter.yaml 未定义健康检查")
    close_all_connections()
    sys.exit(0)

passed = 0
failed = 0
results = []

for check in health_checks:
    check_id = check["id"]
    print_step(check_id, check_id, "running")

    try:
        if check["type"] == "builtin":
            params = {k: v for k, v in check.items() if k not in ("id", "type", "action")}
            result = run_builtin(check["action"], params, conn.run)
        else:
            result = conn.run(check["script"])

        print_step(check_id, "通过", "done")
        passed += 1
        results.append({"id": check_id, "status": "pass"})
        logger.info(f"健康检查通过: {check_id}")

    except Exception as e:
        print_step(check_id, str(e), "failed")
        failed += 1
        results.append({"id": check_id, "status": "fail", "error": str(e)})
        logger.error(f"健康检查失败 {check_id}: {e}")
```

### 步骤 3：计算健康度

```python
total = passed + failed
health_score = int((passed / total) * 100) if total > 0 else 0

print(f"\n{'='*40}")
print(f"健康度: {health_score}% ({passed}/{total} 通过)")

if health_score == 100:
    print("✓ 所有检查通过，服务器状态良好")
elif health_score >= 80:
    print("⚠ 大部分检查通过，但有少量问题")
else:
    print("❌ 多项检查失败，建议排查问题")
```

### 步骤 4：输出修复建议

```python
if failed > 0:
    print("\n失败的检查项:")
    for r in results:
        if r["status"] == "fail":
            print(f"  - {r['id']}: {r.get('error', '未知错误')}")

    print("\n建议:")
    print("  1. 检查服务器日志: .aipool/logs/")
    print("  2. 手动验证失败的检查项")
    print("  3. 如需重新部署: /aipool:deploy", server_name)

close_all_connections()
logger.info(f"验证完成，健康度: {health_score}%")
```

## 输出示例

```
=== 验证 dev-server-1 ===

[健康检查]
  ✓ check_pool_users - 通过
  ✓ check_tools_installed - 通过
  ✓ check_shared_dirs - 通过

========================================
健康度: 100% (3/3 通过)
✓ 所有检查通过，服务器状态良好
```

## 错误处理

- 服务器未部署 → 提示先运行 /aipool:deploy
- SSH 连接失败 → 报告连接错误
- 检查失败 → 显示具体失败项和建议
