# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

**AIPool** - AI 资源池化平台

这是一个 AI 资源池化平台，通过共享和池化技术，让中国开发者能够以更低的成本使用全球领先的 AI 服务。

### 当前项目

- ✅ **Claude Code 共享池** (`aipool/claude-code-pool/`) - 已完成
- ✅ **通用部署框架** (`.aipool/lib/` + `.claude/skills/`) - 已完成
- 🚧 **OpenAI 池化** - 规划中
- 🚧 **Gemini 池化** - 规划中

## 语言要求

**重要：本项目所有内容必须使用中文**
- 所有文档、注释、提交信息使用中文
- 变量名、函数名可使用英文，但相关说明必须用中文
- 规格说明、任务描述、设计文档等全部使用中文

## 项目结构

### 主要目录

- `aipool/` - AIPool 主项目目录
  - `claude-code-pool/` - Claude Code 共享池方案（已完成）
    - `scripts/setup.sh` - 一键部署脚本
    - `adapter.yaml` - 通用部署框架配置
    - `docs/` - 完整文档（30,000+ 字）
  - `docs/` - 通用文档
    - `quick-start.md` - 快速开始指南
    - `adapter-guide.md` - Adapter 编写指南
    - `troubleshooting.md` - 故障排查
  - `openai-pool/` - OpenAI 池化（规划中）
  - `gemini-pool/` - Gemini 池化（规划中）

- `.aipool/` - 部署框架运行时目录（本地，不提交 git）
  - `inventory.yaml` - 服务器清单
  - `state/` - 部署状态（自动管理）
  - `lib/` - 框架核心库
    - `state_manager.py` - 状态管理
    - `adapter_parser.py` - Adapter 解释器
    - `builtin_ops.py` - 内置操作库
    - `ssh_manager.py` - SSH 连接管理
    - `logger.py` - 日志系统
  - `tests/` - 单元测试

- `.claude/skills/` - Claude Code Skills（项目级）
  - `aipool-init/` - `/aipool:init` 初始化
  - `aipool-deploy/` - `/aipool:deploy` 部署
  - `aipool-status/` - `/aipool:status` 状态检查
  - `aipool-sync/` - `/aipool:sync` 同步漂移
  - `aipool-verify/` - `/aipool:verify` 健康验证
  - `aipool-rollback/` - `/aipool:rollback` 版本回滚

- `openspec/` - OpenSpec 工作流目录
  - `config.yaml` - OpenSpec 配置（schema: spec-driven）
  - `changes/` - 活跃变更
    - `claude-code-shared-pool/` - Claude Code 共享池提案（进行中）
    - `claude-code-api-gateway/` - API 网关提案
    - `archive/` - 已完成的变更
      - `2026-04-02-aipool-deploy-framework/` - 通用部署框架（已归档）
  - `specs/` - 规格文件
    - `aipool-deploy-framework/` - 部署框架规格

## OpenSpec 工作流

本项目使用 OpenSpec 进行结构化功能开发。可用命令：

- `/opsx:propose` - 提出新变更，包含设计、规格和任务
- `/opsx:explore` - 进入探索模式，思考想法和需求
- `/opsx:apply` - 实施 OpenSpec 变更中的任务
- `/opsx:archive` - 归档已完成的变更

## 开发说明

### 已完成的工作

1. **Claude Code 共享池方案** (v1.0)
   - 完整的部署脚本
   - 11 个管理和用户工具
   - 30,000+ 字中文文档
   - OpenSpec 完整提案

2. **通用部署框架** (v1.1)
   - 6 个 Claude Code Skills（init/deploy/status/sync/verify/rollback）
   - Adapter 模式支持多 provider 扩展
   - 状态持久化和断点续传
   - SSH 连接管理和连接池复用
   - 漂移检测（文件 hash 对比）
   - 31 个单元测试全部通过
   - claude-code-pool adapter.yaml 已完成

3. **API 网关架构设计**
   - 完整的架构设计文档
   - 待实施

### 快速开始

```bash
# 查看项目主页
cat aipool/README.md

# 初始化部署框架
/aipool:init

# 查看 Claude Code 共享池（手动部署）
cd aipool/claude-code-pool
cat HANDOVER.md

# 运行测试
python3 -m pytest .aipool/tests/ -v
```

## 核心理念

- **池化共享**: 通过资源池化降低使用成本（节省 60-75%）
- **按需使用**: 灵活的配额和计费管理
- **全球连接**: 连接海外 AI 服务，服务中国开发者
- **易于扩展**: 支持多种 AI 服务提供商
