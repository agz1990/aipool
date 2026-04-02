# /aipool:init

初始化 AIPool 项目配置，创建必要的目录和配置文件。

## 用法

```
/aipool:init
```

## 行为

执行以下步骤：

1. **检查是否已初始化**
   - 检查 `.aipool/` 目录是否存在
   - 如果已存在，询问用户是否重新初始化

2. **创建目录结构**
   ```
   .aipool/
   ├── inventory.yaml    ← 服务器清单
   ├── state/            ← 部署状态（自动生成）
   ├── logs/             ← 操作日志（自动生成）
   └── backups/          ← 状态备份（自动生成）
   ```

3. **生成 inventory.yaml 模板**
   - 创建包含示例配置的模板文件
   - 提示用户编辑填写真实服务器信息

4. **验证配置**
   - 如果用户已填写服务器信息，验证格式是否正确
   - 检查 provider 对应的 adapter.yaml 是否存在

5. **输出初始化结果**
   - 显示创建的文件和目录
   - 提示下一步操作

## 实现指南

运行此 skill 时，你需要：

### 步骤 1：检查现有状态

```python
import os
from pathlib import Path

aipool_dir = Path(".aipool")
inventory_file = aipool_dir / "inventory.yaml"

if aipool_dir.exists() and inventory_file.exists():
    # 读取现有配置
    import yaml
    with open(inventory_file) as f:
        existing = yaml.safe_load(f) or {}

    servers = existing.get("servers", {})
    if servers:
        print(f"⚠ AIPool 已初始化，当前有 {len(servers)} 台服务器")
        print("如需重新初始化，请先备份并删除 .aipool/ 目录")
        # 显示现有服务器列表
        for name, info in servers.items():
            print(f"  - {name}: {info.get('host')} ({info.get('pools', [{}])[0].get('provider', '未知')})")
        exit(0)
```

### 步骤 2：创建目录结构

```python
for d in [".aipool", ".aipool/state", ".aipool/logs", ".aipool/backups"]:
    Path(d).mkdir(parents=True, exist_ok=True)
    print(f"✓ 已创建 {d}/")
```

### 步骤 3：生成 inventory.yaml 模板

创建 `.aipool/inventory.yaml`，内容如下：

```yaml
# AIPool 服务器清单
# 每台服务器需要：
#   - 免密 SSH 登录（ssh-copy-id）
#   - sudo 权限
#   - 已安装：bash, rsync, jq

servers:
  # 示例：将 my-server 替换为你的服务器名称
  my-server:
    host: 192.168.1.10      # 服务器 IP 或域名
    user: admin             # SSH 用户名
    port: 22                # SSH 端口（默认 22）
    pools:
      - provider: claude-code  # provider 名称（对应 aipool/<provider>/adapter.yaml）
        count: 4               # 池子数量
```

### 步骤 4：输出完成信息

```
✓ AIPool 初始化完成！

已创建：
  .aipool/inventory.yaml  ← 请编辑此文件添加服务器信息
  .aipool/state/          ← 部署状态（自动管理）
  .aipool/logs/           ← 操作日志（自动管理）
  .aipool/backups/        ← 状态备份（自动管理）

下一步：
  1. 编辑 .aipool/inventory.yaml，添加你的服务器信息
  2. 确认服务器可以免密 SSH 登录：ssh admin@192.168.1.10
  3. 运行 /aipool:deploy <server-name> 开始部署
```

## 错误处理

- 无法创建目录（权限问题）→ 显示错误并提示检查权限
- inventory.yaml 格式错误 → 显示具体错误位置和修复建议

## 注意事项

- 此命令是幂等的：重复运行不会破坏已有配置
- `.aipool/` 目录应该加入 `.gitignore`（包含服务器信息）
- `state/` 目录中的文件由框架自动管理，不要手动修改
