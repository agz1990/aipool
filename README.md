# AIPool

> AI 资源池化平台 - 让中国开发者以更低成本使用全球领先的 AI 服务

## 简介

AIPool 通过共享和池化技术，将昂贵的 AI 订阅成本分摊到团队，节省 60-75%。

以 15 人团队使用 Claude Code 为例：

| 方案 | 月成本 | 节省 |
|------|--------|------|
| AIPool 共享池 | $80 | 73% |
| 每人独立订阅 | $300 | - |

## 快速开始

```bash
# 1. 初始化部署配置
/aipool:init

# 2. 编辑服务器清单
vim .aipool/inventory.yaml

# 3. 一键部署
/aipool:deploy <server-name>
```

详细文档见 [aipool/docs/quick-start.md](aipool/docs/quick-start.md)

## 项目结构

```
aipool/                       # 各 AI 服务池实现
├── claude-code-pool/         # Claude Code 共享池 ✅
├── openai-pool/              # OpenAI 池化 🚧
└── gemini-pool/              # Gemini 池化 🚧

.claude/skills/               # 部署管理 Skills
├── aipool-deploy/            # /aipool:deploy
├── aipool-status/            # /aipool:status
├── aipool-sync/              # /aipool:sync
└── ...

.aipool/                      # 运行时状态（本地，不提交）
├── inventory.yaml            # 服务器清单
└── lib/                      # 框架核心库
```

## 支持的 AI 服务

| 服务 | 状态 | 说明 |
|------|------|------|
| Claude Code | ✅ 已完成 | Anthropic AI 编程助手 |
| OpenAI | 🚧 规划中 | GPT 系列 |
| Gemini | 🚧 规划中 | Google AI |

## 路线图

- [x] v1.0 - Claude Code 共享池
- [x] v1.1 - 通用部署框架（Skills + Adapter 模式）
- [ ] v1.2 - API 网关服务
- [ ] v2.0 - 多 AI 支持

## 许可

MIT License
