# 设计文档：AIPool 通用部署框架

## Context

### 背景

AIPool 项目当前有 claude-code-pool 方案已完成，未来计划支持 gemini-pool、codex-pool 等多种 AI 服务池。每个池子都需要：
- 部署到多台服务器
- 管理部署状态
- 处理版本更新
- 验证健康度

当前的 `setup.sh` 脚本只能处理单次部署，缺乏状态管理和抽象能力。

### 当前状态

```
aipool/claude-code-pool/
├── scripts/setup.sh          ← 一次性部署脚本
├── docs/admin-guide.md       ← 人工操作手册
└── ...

部署方式：
1. 手动 scp 上传文件
2. 手动 ssh 执行 setup.sh
3. 手动逐个池子 claude auth login
4. 手动验证
```

### 约束

- 必须兼容现有的 setup.sh 脚本（不能破坏已部署环境）
- 服务器需要免密 SSH + sudo 权限
- 仅支持 Linux/macOS 服务器
- Skills 放在项目 `.claude/skills/` 目录（项目级别）

## Goals / Non-Goals

### Goals

1. 提供通用的部署框架，支持多种 AI 服务池
2. 通过 adapter.yaml 配置驱动部署流程
3. 状态持久化支持断点续传
4. 多服务器版本漂移检测和同步

### Non-Goals

- 不提供 Web UI（仅 CLI）
- 不支持并发部署多台服务器（初期按顺序执行）
- 不处理网络层高可用（负载均衡、故障转移）

## Decisions

### 决策 1：Adapter 模式 vs 硬编码

**选择**：使用 Adapter 模式，每个 provider 提供 `adapter.yaml` 配置文件

**理由**：
- 扩展性：新增 provider 只需编写配置，无需修改 skill 代码
- 可维护性：配置和逻辑分离，修改部署流程不需要改代码
- 可测试性：可以独立验证 adapter 配置的正确性

**替代方案**：
- 为每个 provider 写独立的 skill → 代码重复，难以维护
- 纯脚本方案 → 缺乏抽象，难以复用

### 决策 2：混合式步骤定义（builtin + script）

**选择**：支持两种步骤类型
- `type: builtin` - 框架内置的常见操作（mkdir、rsync、check_disk）
- `type: script` - 自定义 bash 脚本片段

**理由**：
- 80% 的常见操作用 builtin（简洁、安全、易读）
- 20% 的特殊需求用 script（灵活性）
- 平衡了安全性和灵活性

**替代方案**：
- 纯声明式（只有 builtin）→ 无法处理复杂场景
- 纯脚本式 → 安全性差，难以标准化

### 决策 3：状态存储格式

**选择**：
- `inventory.yaml` - 服务器清单（手动维护）
- `.aipool/state/*.json` - 部署状态（自动生成）

**理由**：
- YAML 适合人工编辑（inventory）
- JSON 适合程序读写（state）
- 分离关注点：清单 vs 状态

**状态包含**：
- 部署时间、版本号
- 脚本文件 hash（用于漂移检测）
- 每个步骤的完成状态（支持断点续传）

### 决策 4：手动介入点的处理

**选择**：`type: manual` 步骤会暂停执行，显示指引，等待用户输入 'done' 继续

**理由**：
- `claude auth login` 需要浏览器交互，无法自动化
- 保持流程连贯性，不需要用户记住"下一步做什么"
- 验证机制确保手动步骤真正完成

**流程**：
```
1. Skill 执行到 manual 步骤
2. 显示详细指引（如何操作）
3. 等待用户输入 'done'
4. 运行 verify_script 验证
5. 验证通过 → 继续；失败 → 提示重试
```

### 决策 5：漂移检测方式

**选择**：基于文件 hash 对比

**理由**：
- 简单可靠：MD5/SHA256 hash 能准确检测文件变化
- 无需版本号：不依赖人工维护版本号
- 支持多文件：可以检测脚本、配置、工具等多个文件

**检测逻辑**：
```
1. adapter.yaml 定义需要监控的文件列表
2. 部署时计算并保存 hash 到 state.json
3. /aipool:status 时重新计算 hash 并对比
4. 不一致 → 标记为 "drifted"
```

## Architecture

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                  用户交互层                              │
│  /aipool:deploy  /aipool:status  /aipool:sync           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Skills 层 (.claude/skills/)                │
│  • aipool-deploy/SKILL.md                               │
│  • aipool-status/SKILL.md                               │
│  • aipool-sync/SKILL.md                                 │
│  • aipool-verify/SKILL.md                               │
│  • aipool-rollback/SKILL.md                             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│           Adapter 解释器 (Skill 内部逻辑)               │
│  • 读取 adapter.yaml                                    │
│  • 执行 builtin 操作                                    │
│  • 执行 script 片段                                     │
│  • 管理状态持久化                                       │
│  • SSH 连接管理                                         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Provider 层                                │
│  aipool/claude-code-pool/adapter.yaml                   │
│  aipool/gemini-pool/adapter.yaml (未来)                 │
│  aipool/codex-pool/adapter.yaml (未来)                  │
└─────────────────────────────────────────────────────────┘
```

### 数据流

```
部署流程:
1. 用户: /aipool:deploy dev-server-1
2. Skill 读取 inventory.yaml → 知道部署什么 provider
3. Skill 读取 adapter.yaml → 知道部署步骤
4. Skill 读取 state.json → 知道从哪里继续（断点续传）
5. 逐步执行 deploy_steps
6. 每步完成后更新 state.json
7. 遇到 type:manual 暂停等待
8. 全部完成后生成部署报告

漂移检测流程:
1. 用户: /aipool:status
2. Skill 遍历 inventory.yaml 所有服务器
3. 对每台服务器:
   - SSH 连接
   - 读取 adapter.yaml 的 drift_detection.files
   - 计算当前 hash
   - 对比 state.json 中的 hash
4. 输出漂移报告
```

### 目录结构

```
aipool/
├── claude-code-pool/
│   ├── adapter.yaml          ← 新增：provider 配置
│   ├── scripts/setup.sh      ← 已有
│   └── docs/
├── gemini-pool/              ← 未来
│   └── adapter.yaml
└── codex-pool/               ← 未来
    └── adapter.yaml

.aipool/                      ← 新增：状态管理目录
├── inventory.yaml            ← 服务器清单
└── state/                    ← 部署状态
    ├── dev-server-1.json
    └── dev-server-2.json

.claude/skills/               ← 新增：Skills
├── aipool-deploy/
│   └── SKILL.md
├── aipool-status/
│   └── SKILL.md
├── aipool-sync/
│   └── SKILL.md
├── aipool-verify/
│   └── SKILL.md
└── aipool-rollback/
    └── SKILL.md
```

## Implementation Details

### adapter.yaml 规范

```yaml
provider: string              # provider 名称
version: string               # adapter 版本
auth_type: interactive|api-key  # 认证方式

pre_checks:                   # 前置检查
  - id: string
    type: builtin|script
    action: string (if builtin)
    script: string (if script)

deploy_steps:                 # 部署步骤
  - id: string
    type: builtin|script|manual
    # builtin 类型
    action: mkdir|rsync|check_disk|...
    # script 类型
    script: string
    verify: string (可选)
    # manual 类型
    for_each: pool (可选)
    instruction: string
    verify_script: string

drift_detection:              # 漂移检测
  method: file_hash
  files: [string]

health_checks:                # 健康检查
  - id: string
    type: builtin|script
    ...

rollback:                     # 回滚配置
  backup_path: string
  steps: [...]
```

### state.json 格式

```json
{
  "provider": "claude-code",
  "adapter_version": "1.0",
  "deployed_at": "2026-04-02T10:30:00Z",
  "script_hashes": {
    "scripts/setup.sh": "abc123...",
    "/usr/local/bin/claude-status": "def456..."
  },
  "pools": {
    "1": { "auth": "done" },
    "2": { "auth": "pending" }
  },
  "steps": {
    "create_dirs": "done",
    "sync_files": "done",
    "run_setup": "done",
    "auth_login": "in_progress"
  }
}
```

### Builtin 操作清单

| 操作 | 参数 | 说明 |
|------|------|------|
| `mkdir` | paths, mode | 创建目录 |
| `rsync` | source, dest, exclude | 同步文件 |
| `check_os` | allowed | 检查操作系统 |
| `check_disk` | path, min_gb | 检查磁盘空间 |
| `check_user_exists` | users | 检查用户是否存在 |
| `restore_backup` | from, to | 恢复备份 |

## Risks / Trade-offs

### 风险 1：SSH 连接不稳定

**风险**：长时间部署过程中 SSH 可能断开

**缓解措施**：
- 状态持久化支持断点续传
- 每个步骤独立，失败后可以从该步骤重试
- 建议使用 tmux/screen 保持会话

### 风险 2：自定义脚本执行失败

**风险**：adapter.yaml 中的 script 可能有 bug

**缓解措施**：
- 每个 script 步骤都有 verify 检查
- 失败立即停止，不继续执行后续步骤
- 提供详细的错误日志

### 风险 3：状态文件损坏

**风险**：state.json 被意外修改或删除

**缓解措施**：
- 每次写入前备份旧版本
- 提供 `/aipool:repair` 命令重建状态
- 状态文件使用 JSON schema 验证

### Trade-off 1：灵活性 vs 复杂度

**选择**：支持 builtin + script 混合模式

**代价**：
- adapter.yaml 可能变得复杂
- 用户需要学习两种语法

**收益**：
- 常见操作简洁（builtin）
- 特殊需求灵活（script）

### Trade-off 2：自动化 vs 控制

**选择**：关键步骤（如 auth login）需要手动确认

**代价**：
- 无法完全无人值守
- 部署时间取决于人的响应速度

**收益**：
- 避免自动化出错导致的严重后果
- 用户保持对关键操作的控制权

## Migration Plan

### 阶段 1：框架开发（1-2 周）

1. 实现 adapter 解释器核心逻辑
2. 实现 builtin 操作库
3. 实现状态管理系统
4. 编写 aipool:deploy skill

### 阶段 2：Claude Code 适配（3-5 天）

1. 编写 claude-code-pool/adapter.yaml
2. 在测试服务器验证完整流程
3. 修复发现的问题

### 阶段 3：完善功能（1 周）

1. 实现 aipool:status、aipool:sync
2. 实现 aipool:verify、aipool:rollback
3. 编写文档和示例

### 阶段 4：生产验证（1-2 周）

1. 在真实环境部署 2-3 台服务器
2. 收集用户反馈
3. 优化体验

### 回滚策略

如果新框架有问题，可以回退到手动部署方式：
1. 删除 `.aipool/` 目录
2. 继续使用 `setup.sh` 手动部署
3. 不影响已部署的服务器

## Open Questions

1. **并发部署**：未来是否需要支持同时部署多台服务器？
   - 当前设计按顺序执行，如需并发需要考虑锁机制

2. **Adapter 版本升级**：adapter.yaml 从 v1.0 升级到 v1.1 时，如何处理已部署的服务器？
   - 可能需要 migration_scripts 机制

3. **权限管理**：是否需要支持不同用户有不同的操作权限？
   - 当前假设所有用户都有完整权限

4. **日志聚合**：是否需要将所有服务器的部署日志集中存储？
   - 当前每台服务器独立记录，未来可考虑集中式日志
