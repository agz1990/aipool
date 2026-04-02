# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 语言要求

**重要：本项目所有内容必须使用中文**
- 所有文档、注释、提交信息使用中文
- 变量名、函数名可使用英文，但相关说明必须用中文
- 规格说明、任务描述、设计文档等全部使用中文

## 项目结构

这是一个基于 OpenSpec 的项目目录，使用规格驱动的开发工作流。

### 目录布局

- `openspec/` - OpenSpec 工作流目录
  - `config.yaml` - OpenSpec 配置（schema: spec-driven）
  - `changes/` - 活跃和已归档的变更
    - `archive/` - 已完成的变更
  - `specs/` - 规格文件

## OpenSpec 工作流

本项目使用 OpenSpec 进行结构化功能开发。可用命令：

- `/opsx:propose` - 提出新变更，包含设计、规格和任务
- `/opsx:explore` - 进入探索模式，思考想法和需求
- `/opsx:apply` - 实施 OpenSpec 变更中的任务
- `/opsx:archive` - 归档已完成的变更

## 开发说明

项目当前处于初始设置阶段，代码结构较少。
