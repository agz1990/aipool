# Adapter 编写指南

## 概述

每个 AI 服务池 provider 需要提供一个 `adapter.yaml` 文件，定义部署步骤、健康检查和漂移检测规则。

## 文件位置

```
aipool/<provider-name>/adapter.yaml
```

## 最小示例

```yaml
provider: my-provider
version: "1.0"
auth_type: api-key

pre_checks:
  - id: check_os
    type: builtin
    action: check_os
    allowed: [linux]

deploy_steps:
  - id: install
    type: script
    script: |
      sudo apt-get install -y my-tool
    verify: |
      which my-tool

drift_detection:
  method: file_hash
  files:
    - /usr/local/bin/my-tool
```

## 完整字段说明

### 顶层字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `provider` | 是 | provider 唯一标识 |
| `version` | 是 | adapter 版本号 |
| `auth_type` | 是 | `interactive` 或 `api-key` |
| `pre_checks` | 否 | 部署前检查 |
| `deploy_steps` | 是 | 部署步骤 |
| `drift_detection` | 是 | 漂移检测配置 |
| `health_checks` | 否 | 健康检查 |
| `rollback` | 否 | 回滚配置 |

### 步骤类型

**type: builtin** - 使用内置操作

```yaml
- id: create_dirs
  type: builtin
  action: mkdir
  paths: [/opt/myapp]
  mode: "755"
```

**type: script** - 执行 bash 脚本

```yaml
- id: install_app
  type: script
  script: |
    sudo ./install.sh
  verify: |
    which myapp
```

**type: manual** - 需要人工操作

```yaml
- id: auth_setup
  type: manual
  for_each: pool          # 可选：为每个池子重复
  instruction: |
    请完成以下操作：
    1. 登录账号
    2. 完成认证
    输入 'done' 继续
  verify_script: |
    myapp auth status | grep -q "authenticated"
```

### 内置操作（builtin actions）

| 操作 | 参数 | 说明 |
|------|------|------|
| `mkdir` | `paths`, `mode` | 创建目录 |
| `rsync` | `source`, `dest`, `exclude` | 同步文件 |
| `check_os` | `allowed` | 检查操作系统 |
| `check_disk` | `path`, `min_gb` | 检查磁盘空间 |
| `check_user_exists` | `users` | 检查用户存在 |
| `restore_backup` | `from`, `to` | 恢复备份 |

### 模板变量

在 `script`、`instruction`、`verify_script` 中可用：

| 变量 | 说明 |
|------|------|
| `{{ pools }}` | 池子总数 |
| `{{ index }}` | 当前池子索引（for_each 时） |
| `{{ provider }}` | provider 名称 |
| `{{ server }}` | 服务器名称 |

## 最佳实践

1. **步骤幂等性**：步骤应支持重复执行（如 `mkdir -p`）
2. **充分验证**：关键步骤加 `verify` 检查
3. **清晰指引**：manual 步骤提供详细的操作说明
4. **合理粒度**：每个步骤做一件事，便于调试
5. **监控关键文件**：在 `drift_detection.files` 中列出所有重要文件
