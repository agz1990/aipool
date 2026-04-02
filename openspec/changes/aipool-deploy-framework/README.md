# AIPool 通用部署框架

> 通过 Claude Code Skills 实现 AI 服务池的标准作业流程（SOP）自动化

## 📋 概述

AIPool 通用部署框架是一个基于 Claude Code 的部署自动化系统，通过 Provider + Adapter 架构支持多种 AI 服务池（Claude Code、Gemini、Codex 等）的统一部署和管理。

### 核心特性

- ✅ **SOP 自动化** - Claude Code 驱动整个部署流程，减少人工操作
- ✅ **状态持久化** - 支持断点续传，部署中断后可继续
- ✅ **多服务器管理** - 自动检测版本漂移，批量同步更新
- ✅ **Provider 抽象** - 新增 AI 服务池只需编写配置文件
- ✅ **可观测性** - 清晰展示所有服务器的部署状态和健康度

### 解决的问题

- 部署流程依赖人工，容易出错或遗漏
- 无状态持久化，中断后必须从头开始
- 多服务器管理困难，版本容易漂移
- 每个新服务池都要重写部署流程

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│              用户交互层 (Claude Code Skills)             │
│  /aipool:deploy  /aipool:status  /aipool:sync           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              通用框架层                                  │
│  • Adapter 解释器    • 状态管理                         │
│  • SSH 连接管理      • 漂移检测                         │
│  • Builtin 操作库    • 断点续传                         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Provider 层 (可扩展)                        │
│  claude-code/adapter.yaml                               │
│  gemini/adapter.yaml (未来)                             │
│  codex/adapter.yaml (未来)                              │
└─────────────────────────────────────────────────────────┘
```

### 核心概念

**Adapter 模式**：每个 AI 服务池提供一个 `adapter.yaml` 配置文件，定义部署步骤、验证方式、漂移检测等行为。框架读取配置并驱动执行。

**混合式步骤**：
- `type: builtin` - 框架内置的常见操作（mkdir、rsync、check_disk）
- `type: script` - 自定义 bash 脚本（灵活处理特殊需求）
- `type: manual` - 手动介入点（如交互式登录）

**状态管理**：
- `inventory.yaml` - 服务器清单（手动维护）
- `.aipool/state/*.json` - 部署状态（自动生成，支持断点续传）

## 📚 文档结构

| 文档 | 说明 |
|------|------|
| [proposal.md](./proposal.md) | 问题定义、目标、价值主张、范围界定 |
| [design.md](./design.md) | 技术架构、关键决策、实施细节、风险分析 |
| [specs/adapter-spec.md](./specs/adapter-spec.md) | adapter.yaml 完整规格说明 |
| [specs/skills-spec.md](./specs/skills-spec.md) | 6 个 Skills 的详细规格 |
| [tasks.md](./tasks.md) | 实施任务清单（7 个阶段，70+ 任务） |

## 🚀 快速开始

### 1. 初始化项目

```bash
/aipool:init
```

创建 `.aipool/` 目录和 `inventory.yaml` 配置文件。

### 2. 配置服务器清单

编辑 `.aipool/inventory.yaml`：

```yaml
servers:
  dev-server-1:
    host: 192.168.1.10
    user: admin
    pools:
      - provider: claude-code
        count: 4
```

### 3. 部署到服务器

```bash
/aipool:deploy dev-server-1
```

框架会：
- 执行前置检查（OS、磁盘空间等）
- 同步文件到服务器
- 执行部署步骤
- 在手动步骤暂停等待（如 `claude auth login`）
- 保存部署状态

### 4. 检查服务器状态

```bash
/aipool:status
```

显示所有服务器的部署状态和版本漂移情况。

### 5. 同步有漂移的服务器

```bash
/aipool:sync dev-server-2
```

增量更新有变更的文件。

## 🛠️ Skills 清单

| Skill | 用途 | 优先级 |
|-------|------|--------|
| `/aipool:init` | 初始化项目配置 | P0 |
| `/aipool:deploy` | 部署到指定服务器 | P0 |
| `/aipool:status` | 检查所有服务器状态 | P0 |
| `/aipool:sync` | 同步有漂移的服务器 | P1 |
| `/aipool:verify` | 验证部署健康度 | P1 |
| `/aipool:rollback` | 回滚到上一版本 | P2 |

## 📝 adapter.yaml 示例

```yaml
provider: claude-code
version: "1.0"
auth_type: interactive

pre_checks:
  - id: check_disk
    type: builtin
    action: check_disk
    path: /shared
    min_gb: 50

deploy_steps:
  - id: create_dirs
    type: builtin
    action: mkdir
    paths: [/shared/repos, /shared/status]

  - id: run_setup
    type: script
    script: |
      cd /opt/aipool
      sudo ./scripts/setup.sh -n {{ pools }}

  - id: auth_login
    type: manual
    for_each: pool
    instruction: |
      请为 Pool {{ index }} 登录：
      1. sudo su - claude-pool-{{ index }}
      2. claude auth login
      3. 输入 'done' 继续
    verify_script: |
      sudo su - claude-pool-{{ index }} -c 'claude "test"'

drift_detection:
  method: file_hash
  files:
    - scripts/setup.sh
    - /usr/local/bin/claude-status
```

## 📊 实施计划

### 里程碑

- **M1: 核心框架完成** (Week 1-2) - 能解析 adapter.yaml 并执行基本步骤
- **M2: 基础部署可用** (Week 2-3) - 能完整部署 claude-code-pool
- **M3: 功能完善** (Week 3-4) - 所有 Skills 可用
- **M4: 生产就绪** (Week 4-5) - 文档完整，测试通过，生产验证完成

### 时间估算

- 阶段 1: 核心框架 (3-5 天)
- 阶段 2: 核心 Skills (5-7 天)
- 阶段 3: Claude Code Adapter (2-3 天)
- 阶段 4: 扩展 Skills (3-4 天)
- 阶段 5: 高级功能 (3-4 天)
- 阶段 6: 文档和测试 (3-5 天)
- 阶段 7: 生产验证 (5-7 天)

**总计**: 24-35 天（约 5-7 周）

## 🎯 成功指标

- 部署成功率：从 ~70% 提升到 95%+
- 部署时间：从 30 分钟降低到 10 分钟（自动化部分）
- 扩展性：新增 Provider 只需 1 天（编写 adapter.yaml + 测试）
- 用户反馈：至少 3 个团队成员能独立完成部署

## 🔧 技术栈

- **语言**: Bash (脚本)、YAML (配置)
- **工具**: Claude Code、SSH、rsync、jq
- **平台**: Linux、macOS
- **依赖**: 免密 SSH、sudo 权限

## 📖 扩展指南

### 新增一个 Provider

1. 创建 `aipool/<provider-name>/adapter.yaml`
2. 定义 provider 信息和部署步骤
3. 测试部署流程
4. 更新文档

示例：添加 Gemini Pool

```yaml
# aipool/gemini-pool/adapter.yaml
provider: gemini
version: "1.0"
auth_type: api-key

deploy_steps:
  - id: install_proxy
    type: script
    script: |
      sudo ./scripts/setup-proxy.sh

  - id: configure_keys
    type: config
    template: config/gemini.conf.j2
    vars:
      api_key: "{{ env.GEMINI_API_KEY }}"
```

### 新增一个 Builtin 操作

1. 在框架中实现操作逻辑
2. 添加到 builtin 操作库
3. 更新 adapter-spec.md 文档
4. 编写单元测试

## ⚠️ 风险和缓解

| 风险 | 缓解措施 |
|------|----------|
| SSH 连接不稳定 | 状态持久化支持断点续传 |
| 自定义脚本执行失败 | 每步都有 verify 检查，失败立即停止 |
| 状态文件损坏 | 每次写入前备份，提供修复命令 |

## 🤝 贡献

欢迎贡献代码、文档或反馈！

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 发起 Pull Request

## 📄 许可

MIT License

## 🔗 相关链接

- [AIPool 主项目](../../README.md)
- [Claude Code 共享池方案](../../aipool/claude-code-pool/)
- [OpenSpec 工作流](../../openspec/)

---

**状态**: 📝 设计阶段
**创建日期**: 2026-04-02
**预计完成**: 2026-05 月中旬
