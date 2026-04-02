# AIPool

> AI 资源池化平台 - 让 AI 触手可及

## 🌊 项目简介

**AIPool** 是一个 AI 资源池化平台，通过共享和池化技术，让中国开发者能够以更低的成本使用全球领先的 AI 服务。

### 当前支持

- ✅ **Claude Code** - Anthropic 的 AI 编程助手（已完成）
- 🚧 **OpenAI** - GPT 系列（规划中）
- 🚧 **Gemini** - Google AI（规划中）

## 📊 成本对比

以 15 人团队使用 Claude Code 为例：

| 方案 | 月成本 | 节省 |
|------|--------|------|
| **AIPool 共享池** | **$80** | **73%** |
| 每人独立订阅 | $300 | - |

## 🚀 快速开始

### 使用通用部署框架（推荐）

```bash
# 1. 初始化配置
/aipool:init

# 2. 编辑服务器清单
vim .aipool/inventory.yaml

# 3. 一键部署
/aipool:deploy <server-name>
```

详细文档：[docs/quick-start.md](docs/quick-start.md)

### 手动部署 Claude Code 共享池

```bash
cd aipool/claude-code-pool
cat HANDOVER.md  # 阅读快速交接文档
```

## 📁 项目结构

```
aipool/
├── README.md                 # 本文件
├── docs/                     # 通用文档 ✅
│   ├── quick-start.md        # 快速开始指南
│   ├── adapter-guide.md      # Adapter 编写指南
│   └── troubleshooting.md    # 故障排查
├── claude-code-pool/         # Claude Code 共享池 ✅
│   ├── adapter.yaml          # 部署框架配置
│   └── scripts/setup.sh      # 部署脚本
├── openai-pool/              # OpenAI 池化 🚧
└── gemini-pool/              # Gemini 池化 🚧

.aipool/                      # 部署状态（本地，不提交）
├── inventory.yaml            # 服务器清单
├── state/                    # 部署状态
└── lib/                      # 框架核心库

.claude/skills/               # Claude Code Skills
├── aipool-init/              # /aipool:init
├── aipool-deploy/            # /aipool:deploy
├── aipool-status/            # /aipool:status
├── aipool-sync/              # /aipool:sync
├── aipool-verify/            # /aipool:verify
└── aipool-rollback/          # /aipool:rollback
```

## 🗺️ 路线图

- [x] v1.0 - Claude Code 共享池（手动部署）
- [x] v1.1 - 通用部署框架（Skills + Adapter 模式）
- [ ] v1.2 - API 网关服务
- [ ] v2.0 - 多 AI 支持（OpenAI、Gemini）

---

**让 AI 触手可及** 🌊

**版本**: 1.1.0 | **状态**: ✅ 生产就绪
