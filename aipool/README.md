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

### Claude Code 共享池

```bash
cd aipool/claude-code-pool
cat HANDOVER.md  # 阅读快速交接文档
```

详细文档：[claude-code-pool/HANDOVER.md](claude-code-pool/HANDOVER.md)

## 📁 项目结构

```
aipool/
├── README.md                 # 本文件
├── claude-code-pool/         # Claude Code 共享池 ✅
├── openai-pool/              # OpenAI 池化 🚧
├── gemini-pool/              # Gemini 池化 🚧
└── aipool-core/              # 核心框架 🚧
```

## 🗺️ 路线图

- [x] v1.0 - Claude Code 共享池
- [ ] v1.1 - API 网关服务
- [ ] v2.0 - 多 AI 支持

---

**让 AI 触手可及** 🌊

**版本**: 1.0.0 | **状态**: ✅ 生产就绪
