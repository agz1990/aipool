# Adapter 规格说明

## 概述

adapter.yaml 是每个 AI 服务池 provider 的配置文件，定义了部署步骤、验证方式、漂移检测等行为。

## 文件位置

```
aipool/<provider-name>/adapter.yaml
```

例如：
- `aipool/claude-code-pool/adapter.yaml`
- `aipool/gemini-pool/adapter.yaml`

## 完整 Schema

```yaml
# 必填字段
provider: string              # provider 唯一标识，如 "claude-code"
version: string               # adapter 版本，如 "1.0"
auth_type: string             # 认证方式: "interactive" 或 "api-key"

# 可选：前置检查
pre_checks:
  - id: string                # 检查项唯一 ID
    type: string              # "builtin" 或 "script"
    # type=builtin 时
    action: string            # builtin 操作名
    [action_params]: any      # 操作参数（根据 action 不同）
    # type=script 时
    script: string            # bash 脚本内容

# 必填：部署步骤
deploy_steps:
  - id: string                # 步骤唯一 ID
    type: string              # "builtin" | "script" | "manual"
    # type=builtin 时
    action: string
    [action_params]: any
    # type=script 时
    script: string
    verify: string            # 可选：验证命令
    # type=manual 时
    for_each: string          # 可选："pool" 表示每个池子重复
    instruction: string       # 给用户的操作指引
    verify_script: string     # 验证脚本

# 必填：漂移检测
drift_detection:
  method: string              # 当前仅支持 "file_hash"
  files: [string]             # 要监控的文件路径列表

# 可选：健康检查
health_checks:
  - id: string
    type: string              # "builtin" 或 "script"
    # 同 pre_checks 格式

# 可选：回滚配置
rollback:
  backup_path: string         # 备份目录路径
  steps:
    - type: string
      [params]: any
```

## 字段详细说明

### provider

- **类型**：string
- **必填**：是
- **说明**：provider 的唯一标识符，用于在 inventory.yaml 中引用
- **示例**：`"claude-code"`, `"gemini"`, `"codex"`

### version

- **类型**：string
- **必填**：是
- **说明**：adapter 配置的版本号，用于追踪配置变更
- **格式**：建议使用语义化版本 "major.minor"
- **示例**：`"1.0"`, `"1.1"`, `"2.0"`

### auth_type

- **类型**：string
- **必填**：是
- **可选值**：
  - `"interactive"` - 需要交互式登录（如浏览器认证）
  - `"api-key"` - 使用 API Key 认证
- **说明**：决定了部署流程中如何处理认证步骤

### pre_checks

- **类型**：array
- **必填**：否
- **说明**：部署前的前置检查，任何一项失败都会阻止部署
- **用途**：检查操作系统、磁盘空间、网络连通性等

#### pre_checks 项格式

```yaml
- id: check_disk              # 唯一 ID
  type: builtin               # builtin 或 script
  action: check_disk          # builtin 操作名
  path: /shared               # 操作参数
  min_gb: 50
```

### deploy_steps

- **类型**：array
- **必填**：是
- **说明**：部署的具体步骤，按顺序执行
- **执行逻辑**：
  - 顺序执行每个步骤
  - 任何步骤失败则停止
  - 支持断点续传（从失败步骤重新开始）

#### deploy_steps 项格式

**type: builtin**

```yaml
- id: create_dirs
  type: builtin
  action: mkdir               # builtin 操作名
  paths:                      # 操作参数
    - /shared/repos
    - /shared/status
  mode: "755"
```

**type: script**

```yaml
- id: run_setup
  type: script
  script: |                   # bash 脚本
    cd /opt/aipool
    sudo ./scripts/setup.sh -n {{ pools }}
  verify: |                   # 可选：验证命令
    id claude-pool-1 &>/dev/null
```

**type: manual**

```yaml
- id: auth_login
  type: manual
  for_each: pool              # 可选：为每个池子重复
  instruction: |              # 给用户的指引
    请执行以下步骤：
    1. sudo su - claude-pool-{{ index }}
    2. claude auth login
    3. 完成后输入 'done'
  verify_script: |            # 验证脚本
    sudo su - claude-pool-{{ index }} -c 'claude "test"'
```

### drift_detection

- **类型**：object
- **必填**：是
- **说明**：定义如何检测服务器配置漂移

#### drift_detection 格式

```yaml
drift_detection:
  method: file_hash           # 当前仅支持 file_hash
  files:                      # 要监控的文件列表
    - scripts/setup.sh
    - /usr/local/bin/claude-status
```

**工作原理**：
1. 部署时计算这些文件的 hash 并保存到 state.json
2. `/aipool:status` 时重新计算 hash 并对比
3. 不一致则标记为 "drifted"

### health_checks

- **类型**：array
- **必填**：否
- **说明**：用于 `/aipool:verify` 命令的健康检查项
- **格式**：同 pre_checks

### rollback

- **类型**：object
- **必填**：否
- **说明**：定义回滚策略

#### rollback 格式

```yaml
rollback:
  backup_path: /opt/aipool-backup
  steps:
    - type: builtin
      action: restore_backup
      from: /opt/aipool-backup
      to: /opt/aipool
```

## Builtin 操作参考

### mkdir

创建目录

```yaml
action: mkdir
paths: [string]               # 目录路径列表
mode: string                  # 可选：权限，如 "755"
```

### rsync

同步文件

```yaml
action: rsync
source: string                # 源路径
dest: string                  # 目标路径
exclude: [string]             # 可选：排除模式
```

### check_os

检查操作系统

```yaml
action: check_os
allowed: [string]             # 允许的 OS 列表：linux, darwin
```

### check_disk

检查磁盘空间

```yaml
action: check_disk
path: string                  # 检查路径
min_gb: number                # 最小空间（GB）
```

### check_user_exists

检查用户是否存在

```yaml
action: check_user_exists
users: [string]               # 用户名列表
```

### restore_backup

恢复备份

```yaml
action: restore_backup
from: string                  # 备份路径
to: string                    # 恢复路径
```

## 模板变量

在 script 和 instruction 中可以使用以下变量：

- `{{ pools }}` - 池子数量（来自 inventory.yaml）
- `{{ index }}` - 当前池子索引（在 for_each: pool 时可用）
- `{{ provider }}` - provider 名称
- `{{ server }}` - 服务器主机名

## 完整示例

```yaml
provider: claude-code
version: "1.0"
auth_type: interactive

pre_checks:
  - id: check_os
    type: builtin
    action: check_os
    allowed: [linux, darwin]

  - id: check_disk
    type: builtin
    action: check_disk
    path: /shared
    min_gb: 50

deploy_steps:
  - id: create_dirs
    type: builtin
    action: mkdir
    paths:
      - /shared/repos
      - /shared/claude-status
      - /shared/claude-logs
    mode: "755"

  - id: sync_files
    type: builtin
    action: rsync
    source: ./
    dest: /opt/aipool/
    exclude: [".git", "*.md"]

  - id: run_setup
    type: script
    script: |
      cd /opt/aipool/claude-code-pool
      sudo ./scripts/setup.sh -n {{ pools }}
    verify: |
      id claude-pool-1 &>/dev/null

  - id: auth_login
    type: manual
    for_each: pool
    instruction: |
      请为 Pool {{ index }} 登录 Claude Code：

      1. sudo su - claude-pool-{{ index }}
      2. claude auth login
      3. 完成浏览器认证
      4. 输入 'done' 继续
    verify_script: |
      sudo su - claude-pool-{{ index }} -c 'claude "test" 2>&1' | grep -qv "error"

drift_detection:
  method: file_hash
  files:
    - scripts/setup.sh
    - /usr/local/bin/claude-status
    - /usr/local/bin/claude-auto

health_checks:
  - id: check_users
    type: builtin
    action: check_user_exists
    users: ["claude-pool-1", "claude-pool-2"]

  - id: check_tools
    type: script
    script: |
      for cmd in claude-status claude-auto claude-claim; do
        which $cmd || exit 1
      done

rollback:
  backup_path: /opt/aipool-backup
  steps:
    - type: builtin
      action: restore_backup
      from: /opt/aipool-backup
      to: /opt/aipool
```

## 验证

adapter.yaml 应该能通过以下验证：

1. **语法验证**：符合 YAML 格式
2. **Schema 验证**：所有必填字段存在，类型正确
3. **引用验证**：builtin action 名称有效
4. **逻辑验证**：步骤 ID 唯一，依赖关系合理

## 最佳实践

1. **步骤粒度**：每个步骤做一件事，便于调试和重试
2. **验证充分**：关键步骤都要有 verify 检查
3. **错误提示**：script 失败时输出清晰的错误信息
4. **幂等性**：步骤应该支持重复执行（如 mkdir -p）
5. **文档化**：在 instruction 中提供详细的操作指引
