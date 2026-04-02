# AIPool - Claude Code 共享池 - 快速参考卡

> 打印或保存此文件，方便随时查阅

## 🚀 快速使用（3 步）

```bash
# 1. 自动分配池子
claude-auto 你的名字

# 2. 进入项目
cd ~/repos/your-project

# 3. 使用 Claude Code
claude "帮我实现功能"

# 完成后退出（自动释放）
exit
```

## 📋 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `claude-status` | 查看池子状态 | `claude-status` |
| `claude-auto 名字` | 自动分配 | `claude-auto 张三` |
| `claude-claim N 名字` | 占用池子 N | `claude-claim 1 张三` |
| `claude-release N` | 释放池子 N | `claude-release 1` |

## ✅ 使用规范

### 必须做
- ✅ 使用完立即释放
- ✅ 下班前检查并释放
- ✅ 长时间使用（>2h）在群里说明

### 不要做
- ❌ 长时间占用不使用
- ❌ 同时占用多个池子
- ❌ 忘记释放

## 🆘 常见问题

### 所有池子都被占用？
```bash
# 1. 查看状态
claude-status

# 2. 在群里询问
"Pool 2 显示是张三在用，还在用吗？"

# 3. 等待或强制释放
claude-release 2  # 确认无人使用后
```

### 忘记释放了？
```bash
# 其他人可以帮你释放
claude-release <pool-number>
```

### 命令不存在？
```bash
# 确保在池子账号中
whoami  # 应该显示 claude-pool-N

# 检查是否安装
which claude
```

## 📞 获取帮助

- **使用文档**: `cat /shared/claude-pool-guide.md`
- **团队群**: 在群里询问
- **管理员**: 联系团队管理员

## 🎯 最佳实践

### 高效使用
```bash
# 使用别名简化命令
alias cs='claude-status'
alias ca='claude-auto'
alias cr='claude-release'
```

### 项目管理
```bash
# 代码放在共享目录
cd ~/repos/your-project

# 定期提交
git add . && git commit -m "完成功能" && git push
```

### 团队协作
```
- 使用前先看状态
- 使用中保持专注
- 使用后立即释放
- 遇到问题及时沟通
```

## 📊 池子状态图例

```
🟢 空闲    - 可以使用
🔴 使用中  - 已被占用
```

## ⚡ 快捷操作

### 查看今日使用记录
```bash
grep "$(date '+%Y-%m-%d')" /shared/claude-logs/usage.log | grep "你的名字"
```

### 查看我占用的池子
```bash
grep "你的名字" /shared/claude-status/*.lock
```

### 释放所有我占用的池子
```bash
# 需要记住占用了哪些
claude-release 1
claude-release 2
```

---

**提示**: 将此文件保存到桌面或打印出来，方便随时查阅！

**更新**: 2026-04-02
