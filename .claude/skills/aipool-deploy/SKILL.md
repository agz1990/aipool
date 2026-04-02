# /aipool:deploy

部署 AI 服务池到指定服务器，支持断点续传。

## 用法

```
/aipool:deploy <server-name>
```

## 参数

- `server-name` - 服务器名称（在 `.aipool/inventory.yaml` 中定义）

## 实现指南

运行此 skill 时，按以下步骤执行：

### 步骤 1：读取配置

```python
import sys
import json
import yaml
from pathlib import Path

# 解析参数
args = sys.argv[1:]
if not args:
    print("❌ 错误: 请指定服务器名称")
    print("用法: /aipool:deploy <server-name>")
    sys.exit(1)

server_name = args[0]

# 读取 inventory.yaml
sys.path.insert(0, ".aipool/lib")
from state_manager import get_server_info, load_state, save_state, init_state, update_step_status, is_step_done, mark_deployed
from adapter_parser import load_adapter, validate_adapter, render_template, get_template_variables, expand_for_each_steps
from ssh_manager import get_connection, close_all_connections
from builtin_ops import run_builtin, compute_file_hash
from logger import Logger, format_error, print_section, print_step, print_success, print_error

logger = Logger(server_name)
logger.info(f"开始部署 {server_name}")

server_info = get_server_info(server_name)
host = server_info["host"]
user = server_info["user"]
port = server_info.get("port", 22)
pools_config = server_info["pools"]
provider = pools_config[0]["provider"]
pool_count = pools_config[0]["count"]

print(f"\n=== 部署到 {server_name} ===\n")
print(f"Provider: {provider}")
print(f"Pools: {pool_count}")
print(f"服务器: {user}@{host}:{port}")
```

### 步骤 2：加载 adapter.yaml

```python
# adapter.yaml 位于 aipool/<provider>/adapter.yaml
adapter_path = Path(f"aipool/{provider}")
adapter = load_adapter(adapter_path)
adapter_version = adapter["version"]
```

### 步骤 3：检查断点续传

```python
state = load_state(server_name)
resume = False

if state:
    completed_steps = sum(1 for v in state.get("steps", {}).values() if v == "done")
    total_steps = len(adapter.get("deploy_steps", []))
    print(f"\n⚠ 发现未完成的部署（{completed_steps}/{total_steps} 步骤已完成）")
    answer = input("是否从上次位置继续？(y/n) > ").strip().lower()
    if answer == "y":
        resume = True
        print("✓ 将从上次位置继续")
    else:
        state = None

if not state:
    state = init_state(server_name, provider, adapter_version, pool_count)
    save_state(server_name, state)
```

### 步骤 4：SSH 连接和前置检查

```python
print_section("SSH 连接")
try:
    conn = get_connection(host, user, port)
    print_step("ssh_connect", f"连接到 {user}@{host}", "done")
    logger.info(f"SSH 连接成功: {user}@{host}")
except Exception as e:
    print_error(format_error("E002", str(e)))
    logger.error(f"SSH 连接失败: {e}")
    sys.exit(3)

ssh_runner = conn.run

print_section("前置检查")
for check in adapter.get("pre_checks", []):
    check_id = check["id"]
    if is_step_done(state, f"pre_{check_id}"):
        print_step(check_id, check_id, "skip")
        continue

    print_step(check_id, check_id, "running")
    try:
        if check["type"] == "builtin":
            params = {k: v for k, v in check.items() if k not in ("id", "type", "action")}
            result = run_builtin(check["action"], params, ssh_runner)
        else:
            result = ssh_runner(check["script"])

        print_step(check_id, result, "done")
        state = update_step_status(state, f"pre_{check_id}", "done")
        save_state(server_name, state)
        logger.info(f"前置检查通过: {check_id}")
    except Exception as e:
        print_step(check_id, str(e), "failed")
        print_error(format_error("E003", str(e)))
        logger.error(f"前置检查失败 {check_id}: {e}")
        sys.exit(3)
```

### 步骤 5：执行部署步骤

```python
print_section("部署步骤")
tmpl_vars = get_template_variables(server_name, provider, pool_count)
deploy_steps = expand_for_each_steps(adapter.get("deploy_steps", []), pool_count)

for step in deploy_steps:
    step_id = step["id"]
    pool_index = step.get("_pool_index")

    if is_step_done(state, step_id):
        print_step(step_id, step_id, "skip")
        continue

    state = update_step_status(state, step_id, "in_progress")
    save_state(server_name, state)

    if pool_index:
        tmpl_vars["index"] = pool_index

    step_type = step["type"]

    try:
        if step_type == "builtin":
            params = {k: v for k, v in step.items() if k not in ("id", "type", "action", "_pool_index")}
            # 注入 SSH 信息给 rsync
            params["_host"] = host
            params["_user"] = user
            print_step(step_id, step["action"], "running")
            result = run_builtin(step["action"], params, ssh_runner)
            print_step(step_id, result, "done")

        elif step_type == "script":
            script = render_template(step["script"], tmpl_vars)
            print_step(step_id, step_id, "running")
            ssh_runner(script)

            # 执行 verify
            if "verify" in step:
                verify_script = render_template(step["verify"], tmpl_vars)
                ssh_runner(verify_script)

            print_step(step_id, step_id, "done")

        elif step_type == "manual":
            instruction = render_template(step["instruction"], tmpl_vars)
            print(f"\n⏸ 手动步骤: {step_id}")
            print("-" * 40)
            print(instruction)
            print("-" * 40)

            while True:
                answer = input("\n完成后输入 'done' 继续，输入 'skip' 跳过: ").strip().lower()
                if answer == "skip":
                    print_step(step_id, "已跳过", "skip")
                    break
                elif answer == "done":
                    # 执行验证
                    if "verify_script" in step:
                        verify = render_template(step["verify_script"], tmpl_vars)
                        try:
                            ssh_runner(verify)
                            print_step(step_id, "验证通过", "done")
                        except Exception as ve:
                            print(f"⚠ 验证失败: {ve}")
                            print("请重新完成手动步骤后再输入 'done'")
                            continue
                    else:
                        print_step(step_id, "已完成", "done")
                    break

        state = update_step_status(state, step_id, "done")
        save_state(server_name, state)
        logger.info(f"步骤完成: {step_id}")

    except Exception as e:
        state = update_step_status(state, step_id, "failed")
        save_state(server_name, state)
        print_step(step_id, str(e), "failed")
        print_error(format_error("E004", str(e)))
        logger.error(f"步骤失败 {step_id}: {e}")
        print(f"\n部署已暂停。修复问题后运行 /aipool:deploy {server_name} 断点续传")
        sys.exit(4)
```

### 步骤 6：计算文件 hash 并保存

```python
print_section("计算文件 Hash")
drift_files = adapter.get("drift_detection", {}).get("files", [])
hashes = {}
for f in drift_files:
    try:
        h = compute_file_hash(f, ssh_runner)
        hashes[f] = h
        print_step(f"hash_{f}", f"{f}: {h[:8]}...", "done")
    except Exception:
        hashes[f] = ""

state["script_hashes"] = hashes
state = mark_deployed(state)
save_state(server_name, state)
```

### 步骤 7：生成部署报告

```python
close_all_connections()
logger.info("部署完成")

completed = sum(1 for v in state.get("steps", {}).values() if v == "done")
total = len(deploy_steps) + len(adapter.get("pre_checks", []))

print(f"\n{'='*40}")
print(f"✓ 部署完成！")
print(f"  服务器: {server_name}")
print(f"  Provider: {provider} v{adapter_version}")
print(f"  Pools: {pool_count}")
print(f"  完成步骤: {completed}/{total}")
print(f"  部署时间: {state['deployed_at']}")
print(f"\n运行 /aipool:status 查看所有服务器状态")
```

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| 服务器不在 inventory.yaml | 显示可用服务器列表 |
| adapter.yaml 不存在 | 提示检查 provider 名称 |
| SSH 连接失败 | 显示连接信息，提示检查网络 |
| 前置检查失败 | 显示具体失败项，停止部署 |
| 步骤执行失败 | 保存状态，提示断点续传 |
| 手动步骤验证失败 | 提示重新完成，不继续 |

## 断点续传

部署中断后，重新运行 `/aipool:deploy <server-name>` 会：
1. 检测到未完成的部署状态
2. 询问是否继续
3. 跳过已完成的步骤
4. 从中断处继续执行
