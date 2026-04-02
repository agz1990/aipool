# Changelog

All notable changes to AIPool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-02

### Added

#### 通用部署框架
- ✅ 6 个 Claude Code Skills
  - `/aipool:init` - 初始化项目配置
  - `/aipool:deploy` - 部署到指定服务器（含断点续传）
  - `/aipool:status` - 检查所有服务器状态和漂移
  - `/aipool:sync` - 同步有漂移的服务器
  - `/aipool:verify` - 验证部署健康度
  - `/aipool:rollback` - 回滚到上一版本
- ✅ 框架核心库（`.aipool/lib/`）
  - `state_manager.py` - inventory.yaml 读取、state.json 读写、断点续传、自动备份
  - `adapter_parser.py` - adapter.yaml 解析、schema 验证、模板变量替换、for_each 展开
  - `builtin_ops.py` - 6 个内置操作（mkdir/rsync/check_os/check_disk/check_user_exists/restore_backup）
  - `ssh_manager.py` - SSH 连接封装、连接池复用、重试机制、文件上传下载
  - `logger.py` - 统一日志系统、错误码定义、修复建议
- ✅ Claude Code Pool Adapter（`aipool/claude-code-pool/adapter.yaml`）
- ✅ 通用文档（`aipool/docs/`）
  - 快速开始指南
  - Adapter 编写指南
  - 故障排查指南
- ✅ 31 个单元测试全部通过

### Features

- **断点续传**: 部署中断后可从上次位置继续
- **漂移检测**: 基于文件 hash 自动检测版本漂移
- **Adapter 模式**: 新增 provider 只需编写 adapter.yaml
- **手动步骤**: 支持需要人工介入的步骤（如 claude auth login）

---

## [1.0.0] - 2026-04-02

### Added

#### Claude Code 共享池方案
- ✅ 完整的池子管理系统
- ✅ 协调机制（占用/释放）
- ✅ 11 个用户和管理工具
- ✅ 一键部署脚本
- ✅ 完整的中文文档（30,000+ 字）
  - 用户使用指南
  - 管理员手册
  - 成本分析
  - 快速参考卡片
- ✅ OpenSpec 项目提案
  - 提案文档
  - 技术设计
  - 详细规格（6 个能力）
  - 任务清单

#### 文档
- README.md - 项目主页
- HANDOVER.md - 快速交接
- PROJECT-COMPLETE.md - 项目完结总结
- CHANGELOG.md - 更新日志（本文件）

#### 进阶设计
- API 网关架构设计文档

### Features

- **成本节省**: 相比独立订阅节省 73%
- **快速部署**: 10 分钟完成部署
- **易于使用**: 简单的命令行工具
- **完整监控**: 实时状态、使用统计、告警

### Technical Details

- 支持 2-10 个池子配置
- 基于文件锁的协调机制
- SQLite 数据存储（规划中）
- Bash 脚本实现

---

## [Unreleased]

### Planned for v1.1 - API 网关服务

- [ ] HTTP API 封装
- [ ] API Key 认证系统
- [ ] 配额管理
- [ ] 客户端 SDK（Python/JavaScript）
- [ ] CLI 工具
- [ ] 流式输出支持

### Planned for v2.0 - 多 AI 支持

- [ ] OpenAI 池化支持
- [ ] Gemini 池化支持
- [ ] 统一 API 接口
- [ ] Web 管理界面
- [ ] 企业级功能
  - 多租户支持
  - 细粒度权限控制
  - 详细的审计日志

---

## Version History

- **1.1.0** (2026-04-02) - 通用部署框架，6 个 Skills，Adapter 模式
- **1.0.0** (2026-04-02) - 初始版本，Claude Code 共享池
- **0.1.0** (2026-04-02) - 项目启动，架构设计

---

## Notes

### 合规性提醒

当前的 Claude Code 共享池方案可能违反 Anthropic 服务条款。建议：
- 先小规模测试
- 监控警告信号
- 准备备选方案

### 贡献

欢迎贡献代码和建议！请查看 CONTRIBUTING.md（待创建）

---

**项目**: AIPool
**维护者**: Your Team
**许可**: MIT License
