# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

**AIPool** - AI 资源池化平台

这是一个 AI 资源池化平台，通过共享和池化技术，让中国开发者能够以更低的成本使用全球领先的 AI 服务。

### 当前项目

- ✅ **Claude Code 共享池** (`aipool/claude-code-pool/`) - 已完成
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
    - `docs/` - 完整文档（30,000+ 字）
  - `openai-pool/` - OpenAI 池化（规划中）
  - `gemini-pool/` - Gemini 池化（规划中）

- `openspec/` - OpenSpec 工作流目录
  - `config.yaml` - OpenSpec 配置（schema: spec-driven）
  - `changes/` - 活跃和已归档的变更
    - `claude-code-shared-pool/` - Claude Code 共享池提案
    - `claude-code-api-gateway/` - API 网关提案
    - `archive/` - 已完成的变更
  - `specs/` - 规格文件

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

2. **API 网关架构设计**
   - 完整的架构设计文档
   - 待实施

### 快速开始

```bash
# 查看项目主页
cat aipool/README.md

# 查看 Claude Code 共享池
cd aipool/claude-code-pool
cat HANDOVER.md
```

## 核心理念

- **池化共享**: 通过资源池化降低使用成本（节省 60-75%）
- **按需使用**: 灵活的配额和计费管理
- **全球连接**: 连接海外 AI 服务，服务中国开发者
- **易于扩展**: 支持多种 AI 服务提供商
