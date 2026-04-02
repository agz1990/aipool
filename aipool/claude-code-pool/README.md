# AIPool

> AI 资源池化平台 - 让 AI 触手可及

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](CHANGELOG.md)

## 🌊 项目简介

**AIPool** 是一个 AI 资源池化平台，通过共享和池化技术，让中国开发者能够以更低的成本使用全球领先的 AI 服务。

### 核心理念

- **池化共享**: 通过资源池化降低使用成本
- **按需使用**: 灵活的配额和计费管理
- **全球连接**: 连接海外 AI 服务，服务中国开发者
- **易于扩展**: 支持多种 AI 服务提供商

### 当前支持

- ✅ **Claude Code** - Anthropic 的 AI 编程助手
- 🚧 **OpenAI** - GPT 系列（规划中）
- 🚧 **Gemini** - Google AI（规划中）

---

## 📊 成本对比

以 15 人团队使用 Claude Code 为例：

| 方案 | 月成本 | 年成本 | 节省 |
|------|--------|--------|------|
| **AIPool 共享池** | **$80** | **$960** | **73%** |
| 每人独立订阅 | $300 | $3,600 | - |
| 混合方案 | $120 | $1,440 | 60% |

---

## 🚀 快速开始

### Claude Code 共享池（已完成）

适合：中小型团队，预算有限，可接受一定合规风险

```bash
# 1. 进入 Claude Code 池子目录
cd aipool/claude-code-pool

# 2. 阅读快速交接文档
cat HANDOVER.md

# 3. 部署到服务器
sudo ./scripts/setup.sh -n 4

# 4. 开始使用
claude-status
claude-auto 你的名字
```

详细文档：[快速交接](claude-code-pool/HANDOVER.md) | [完整总结](claude-code-pool/PROJECT-COMPLETE.md)

---

## 📁 项目结构

```
aipool/
├── README.md                      # 本文件
├── claude-code-pool/              # Claude Code 共享池方案 ✅
│   ├── HANDOVER.md                # 快速交接
│   ├── PROJECT-COMPLETE.md        # 完整总结
│   ├── scripts/setup.sh           # 一键部署
│   └── docs/                      # 详细文档
│
├── openai-pool/                   # OpenAI 池化（规划中）🚧
├── gemini-pool/                   # Gemini 池化（规划中）🚧
└── aipool-core/                   # 核心框架（规划中）🚧
```

---

## 🎯 核心功能

### Claude Code 共享池

**用户工具**:
- `claude-status` - 查看池子状态
- `claude-auto` - 自动分配空闲池子
- `claude-claim` - 手动占用池子
- `claude-release` - 释放池子

**管理工具**:
- `claude-monitor` - 监控信息
- `claude-monthly-report` - 月度报告
- `claude-dashboard` - 实时仪表板
- `claude-backup` - 数据备份

---

## 📚 文档

### 快速开始
- [快速交接](claude-code-pool/HANDOVER.md) - 3 步开始
- [完整总结](claude-code-pool/PROJECT-COMPLETE.md) - 项目完结文档

### 用户文档
- [用户使用指南](claude-code-pool/docs/user-guide.md) - 8,000+ 字
- [快速参考卡片](claude-code-pool/QUICK-REFERENCE.md) - 常用命令

### 管理员文档
- [管理员手册](claude-code-pool/docs/admin-guide.md) - 12,000+ 字
- [成本分析](claude-code-pool/docs/cost-analysis.md) - 5,000+ 字

### 进阶方案
- [API 网关架构](claude-code-pool/docs/api-gateway-design.md) - 进阶设计

---

## 🗺️ 发展路线图

### v1.0 - Claude Code 共享池 ✅ 已完成

- [x] 池子管理系统
- [x] 协调机制
- [x] 用户和管理工具
- [x] 完整文档
- [x] 一键部署脚本

### v1.1 - API 网关服务 🚧 规划中

- [ ] HTTP API 封装
- [ ] API Key 认证
- [ ] 配额管理
- [ ] 客户端 SDK
- [ ] CLI 工具

### v2.0 - 多 AI 支持 🔮 未来

- [ ] OpenAI 池化支持
- [ ] Gemini 池化支持
- [ ] 统一 API 接口
- [ ] Web 管理界面

---

## ⚠️ 重要提醒

### 合规性

当前的 Claude Code 共享池方案可能违反 Anthropic 服务条款，存在一定风险。

**风险等级**: 中等

**缓解措施**:
- 先小规模测试
- 监控警告信号
- 准备备选方案

详见：[成本分析 - 风险管理](claude-code-pool/docs/cost-analysis.md)

---

## 📈 统计

- **文件数量**: 20+
- **代码行数**: 3,489+
- **文档字数**: 30,000+
- **支持的 AI**: 1 (Claude Code)
- **节省成本**: 高达 73%

---

**让 AI 触手可及** 🌊

---

**版本**: 1.0.0
**更新日期**: 2026-04-02
**状态**: ✅ 生产就绪
