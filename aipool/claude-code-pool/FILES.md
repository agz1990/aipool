# AIPool - Claude Code 共享池方案 - 文件清单

## 📁 完整文件列表

### 核心文件

```
aipool/claude-code-pool/
├── README.md                    # 方案概述和快速开始
├── SUMMARY.md                   # 完整总结文档
├── QUICK-REFERENCE.md           # 快速参考卡片
└── FILES.md                     # 本文件（文件清单）
```

### 脚本目录 (scripts/)

```
scripts/
└── setup.sh                     # 一键部署脚本
    - 创建池子账号
    - 配置共享目录
    - 安装协调脚本
    - 生成使用文档
    - 创建监控工具
```

### 文档目录 (docs/)

```
docs/
├── user-guide.md                # 用户使用指南（团队成员必读）
│   - 新手入门
│   - 日常使用
│   - 最佳实践
│   - 常见问题
│   - 故障排查
│
├── admin-guide.md               # 管理员手册（管理员必读）
│   - 部署指南
│   - 日常维护
│   - 监控统计
│   - 故障处理
│   - 扩展优化
│   - 安全合规
│
└── cost-analysis.md             # 成本分析（决策参考）
    - 方案对比
    - ROI 分析
    - 案例研究
    - 优化建议
```

### 监控目录 (monitoring/)

```
monitoring/
└── (预留，用于未来的监控脚本和工具)
```

## 📊 文件用途说明

### 给决策者

1. **README.md** - 了解方案概述
2. **docs/cost-analysis.md** - 评估成本效益
3. **SUMMARY.md** - 查看完整总结

### 给管理员

1. **scripts/setup.sh** - 执行部署
2. **docs/admin-guide.md** - 学习管理和维护
3. **SUMMARY.md** - 了解整体方案

### 给团队成员

1. **QUICK-REFERENCE.md** - 快速查阅常用命令
2. **docs/user-guide.md** - 详细学习使用方法
3. **README.md** - 快速开始

## 🚀 使用流程

### 第一次部署

```
1. 阅读 README.md
   ↓
2. 阅读 docs/admin-guide.md（部署指南部分）
   ↓
3. 执行 scripts/setup.sh
   ↓
4. 为每个池子登录 Claude Code
   ↓
5. 分发 docs/user-guide.md 给团队成员
   ↓
6. 打印 QUICK-REFERENCE.md 给团队成员
```

### 日常使用

```
团队成员:
- 参考 QUICK-REFERENCE.md 使用
- 遇到问题查看 docs/user-guide.md

管理员:
- 参考 docs/admin-guide.md 维护
- 定期查看监控和日志
```

## 📝 部署后生成的文件

部署脚本会在服务器上生成以下文件：

### 系统命令

```
/usr/local/bin/
├── claude-status              # 查看池子状态
├── claude-claim               # 占用池子
├── claude-release             # 释放池子
├── claude-auto                # 自动分配池子
├── claude-force-release       # 强制释放所有池子
├── claude-monitor             # 监控信息
├── claude-monthly-report      # 月度报告
├── claude-dashboard           # 实时仪表板
├── claude-alert               # 告警检查
├── claude-backup              # 数据备份
└── claude-cleanup             # 数据清理
```

### 共享目录

```
/shared/
├── repos/                     # 共享代码目录
├── claude-status/             # 池子状态文件
│   ├── pool-1.lock
│   ├── pool-2.lock
│   ├── pool-3.lock
│   └── pool-4.lock
├── claude-logs/               # 日志目录
│   └── usage.log
└── claude-pool-guide.md       # 使用文档（自动生成）
```

### 用户目录

```
/home/
├── claude-pool-1/             # 池子 1
│   ├── repos -> /shared/repos
│   └── .claude/
├── claude-pool-2/             # 池子 2
│   ├── repos -> /shared/repos
│   └── .claude/
├── claude-pool-3/             # 池子 3
│   ├── repos -> /shared/repos
│   └── .claude/
└── claude-pool-4/             # 池子 4
    ├── repos -> /shared/repos
    └── .claude/
```

## 📦 打包和分发

### 打包方案

```bash
# 创建压缩包
cd /path/to/
tar -czf aipool/claude-code-pool.tar.gz aipool/claude-code-pool/

# 或创建 zip 包
zip -r aipool/claude-code-pool.zip aipool/claude-code-pool/
```

### 分发给团队

```
1. 将压缩包上传到服务器
2. 解压
3. 执行部署脚本
4. 分发文档给团队成员
```

## 🔄 版本管理

### 当前版本

```
版本: 1.0
发布日期: 2026-04-02
```

### 版本历史

```
v1.0 (2026-04-02)
- 初始版本发布
- 完整的部署脚本
- 用户和管理员文档
- 成本分析和方案对比
```

### 未来计划

```
v1.1 (计划中)
- Web 管理界面
- 自动化告警
- 使用配额管理
- 更详细的统计报表

v2.0 (未来)
- API 服务封装
- 多服务器支持
- 高级调度算法
- 集成其他 AI 工具
```

## 📞 支持

如有问题，请：
1. 查看相关文档
2. 在团队群里询问
3. 联系管理员

---

**最后更新**: 2026-04-02
