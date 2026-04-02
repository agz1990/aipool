# Claude Code 共享池子 - 团队成员使用指南

## 📖 目录

1. [新手入门](#新手入门)
2. [日常使用](#日常使用)
3. [最佳实践](#最佳实践)
4. [常见问题](#常见问题)
5. [故障排查](#故障排查)

---

## 🚀 新手入门

### 第一次使用（完整流程）

#### 步骤 1: 连接到开发主机

```bash
# 从你的虚拟机（通过 ToDesk 连接的那台）
# 使用 VS Code 的 Remote SSH 连接到开发主机

# 或者直接 SSH 连接
ssh your-username@dev-server
```

#### 步骤 2: 查看池子状态

```bash
claude-status
```

你会看到类似这样的输出：

```
=== Claude Code 池子状态 ===

池子       状态            使用信息
--------------------------------------------------------
Pool 1     🟢 空闲         -
Pool 2     🔴 使用中       张三 @ 2026-04-02 10:30:15
Pool 3     🟢 空闲         -
Pool 4     🟢 空闲         -

提示: 使用 'claude-auto 你的名字' 自动分配空闲池子
```

#### 步骤 3: 占用一个池子

**方式 A: 自动分配（推荐）**

```bash
claude-auto 你的名字

# 示例
claude-auto 李四
```

系统会自动：
1. 找到一个空闲的池子
2. 标记为你占用
3. 切换到池子账号
4. 退出时自动释放

**方式 B: 手动选择**

```bash
# 1. 占用池子 1
claude-claim 1 你的名字

# 2. 切换到池子账号
sudo su - claude-pool-1
```

#### 步骤 4: 开始工作

```bash
# 进入项目目录
cd ~/repos/your-project

# 或者创建新项目
cd ~/repos
mkdir my-new-project
cd my-new-project

# 使用 Claude Code
claude "帮我创建一个 Python 项目结构"
```

#### 步骤 5: 完成工作

```bash
# 退出池子账号
exit

# 释放池子（如果使用手动方式）
claude-release 1
```

**注意**：如果使用 `claude-auto`，退出时会自动释放，无需手动运行 `claude-release`。

---

## 💼 日常使用

### 快速使用流程

```bash
# 1. 查看状态（可选）
claude-status

# 2. 自动分配池子
claude-auto 你的名字

# 3. 进入项目
cd ~/repos/your-project

# 4. 使用 Claude Code
claude "帮我实现登录功能"

# 5. 完成后退出
exit
# （自动释放）
```

### 在 VS Code 中使用

如果你通过 VS Code Remote SSH 连接到开发主机：

```bash
# 在 VS Code 的终端中

# 1. 占用池子
claude-auto 你的名字

# 2. 在新终端中使用 Claude Code
# （因为 claude-auto 会切换账号，所以需要在新终端操作）
```

**更好的方式**：

```bash
# 1. 先占用池子
claude-claim 1 你的名字

# 2. 在 VS Code 中打开新的 Remote SSH 连接
# Host: claude-pool-1@localhost

# 3. 在新连接中使用 Claude Code
```

---

## ✨ 最佳实践

### 使用时长建议

```
✅ 推荐：
- 单次使用 30 分钟 - 2 小时
- 使用完立即释放
- 需要长时间使用时，在群里说明

❌ 避免：
- 占用超过 3 小时不使用
- 下班忘记释放
- 同时占用多个池子
```

### 团队协作礼仪

#### 1. 使用前

```bash
# 查看状态，选择空闲池子
claude-status

# 如果所有池子都被占用
# 在团队群里询问：
"大家好，所有池子都在使用中，有人可以释放一下吗？"
```

#### 2. 使用中

```bash
# 如果需要长时间使用（> 2 小时）
# 在群里说明：
"我需要用 Pool 1 大概 3 小时，做一个大功能"

# 如果临时离开（> 30 分钟）
# 先释放池子：
exit
claude-release 1
```

#### 3. 使用后

```bash
# 务必释放池子
claude-release 1

# 或者使用 claude-auto 会自动释放
```

### 代码管理

```bash
# ✅ 推荐：代码放在共享目录
cd ~/repos/your-project
git clone https://github.com/your-org/your-repo.git

# ✅ 推荐：定期提交代码
git add .
git commit -m "完成登录功能"
git push

# ❌ 避免：在池子账号的 home 目录存储重要文件
# 因为多人共享，可能会被覆盖
```

---

## ❓ 常见问题

### Q1: 所有池子都被占用怎么办？

**方案 1: 等待**
```bash
# 每隔几分钟查看一次
watch -n 60 claude-status
```

**方案 2: 团队协调**
```
在群里询问：
"Pool 2 显示是张三在用，但已经 2 小时了，还在用吗？"
```

**方案 3: 检查是否有人忘记释放**
```bash
# 查看使用日志
cat /shared/claude-logs/usage.log | tail -20

# 如果发现有池子长时间无活动，可以强制释放
claude-release 2
```

### Q2: 忘记释放池子怎么办？

**如果你忘记了：**
```bash
# 其他人可以帮你释放
claude-release <pool-number>

# 或者你自己远程释放
ssh dev-server
claude-release 1
```

**如果别人忘记了：**
```bash
# 先在群里询问
"Pool 1 显示是李四在用，还在用吗？"

# 如果确认不用了，可以释放
claude-release 1
```

### Q3: Claude Code 命令不存在？

```bash
# 检查是否在池子账号中
whoami
# 应该显示: claude-pool-1

# 检查 Claude Code 是否安装
which claude

# 如果未安装，需要安装
# 按照官方文档安装 Claude Code CLI
```

### Q4: 如何查看我的使用历史？

```bash
# 查看今天的使用记录
grep "$(date '+%Y-%m-%d')" /shared/claude-logs/usage.log | grep "你的名字"

# 查看所有使用记录
grep "你的名字" /shared/claude-logs/usage.log
```

### Q5: 可以在池子里安装软件吗？

```bash
# 可以，但建议只安装必要的开发工具
sudo apt install <package>  # Ubuntu/Debian
brew install <package>      # macOS

# 注意：所有池子共享同一台机器
# 安装的软件对所有池子可见
```

### Q6: 代码会被其他人看到吗？

```
是的，因为代码在共享目录 /shared/repos/

建议：
✅ 团队项目放在共享目录
❌ 个人敏感项目不要放在共享目录

如果需要隐私：
- 在自己的虚拟机上开发
- 或者使用独立的开发环境
```

---

## 🔧 故障排查

### 问题 1: 无法切换到池子账号

**症状**：
```bash
sudo su - claude-pool-1
# 提示: su: user claude-pool-1 does not exist
```

**解决**：
```bash
# 检查账号是否存在
id claude-pool-1

# 如果不存在，联系管理员
# 管理员需要运行部署脚本
```

### 问题 2: 提示权限不足

**症状**：
```bash
su - claude-pool-1
# 提示: Permission denied
```

**解决**：
```bash
# 使用 sudo
sudo su - claude-pool-1

# 如果仍然失败，联系管理员
# 管理员需要将你添加到 sudo 组
```

### 问题 3: Claude Code 登录失败

**症状**：
```bash
claude auth login
# 提示: Authentication failed
```

**解决**：
```bash
# 1. 检查网络连接
ping claude.ai

# 2. 检查是否在正确的账号中
whoami

# 3. 重新登录
claude auth logout
claude auth login

# 4. 如果仍然失败，联系管理员
# 可能是订阅过期或账号问题
```

### 问题 4: 池子状态显示异常

**症状**：
```bash
claude-status
# 显示所有池子都被占用，但实际没人在用
```

**解决**：
```bash
# 查看详细日志
cat /shared/claude-logs/usage.log | tail -20

# 如果确认没人在用，强制释放
claude-force-release

# 注意：这会释放所有池子，谨慎使用
```

### 问题 5: 找不到项目代码

**症状**：
```bash
cd ~/repos/my-project
# 提示: No such file or directory
```

**解决**：
```bash
# 检查软链接是否存在
ls -la ~/repos

# 如果不存在，创建软链接
ln -s /shared/repos ~/repos

# 检查共享目录
ls -la /shared/repos/
```

---

## 📞 获取帮助

### 自助排查

1. **查看使用文档**
   ```bash
   cat /shared/claude-pool-guide.md
   ```

2. **查看监控信息**
   ```bash
   claude-monitor
   ```

3. **查看日志**
   ```bash
   cat /shared/claude-logs/usage.log
   ```

### 联系支持

- **团队群**：在群里询问
- **管理员**：联系团队管理员
- **紧急情况**：直接联系管理员

---

## 📊 使用技巧

### 技巧 1: 使用别名简化命令

```bash
# 在你的 ~/.bashrc 或 ~/.zshrc 中添加
alias cs='claude-status'
alias ca='claude-auto'
alias cr='claude-release'

# 重新加载配置
source ~/.bashrc
```

### 技巧 2: 创建项目快捷方式

```bash
# 在你的 home 目录创建项目软链接
ln -s /shared/repos/my-project ~/my-project

# 快速进入项目
cd ~/my-project
```

### 技巧 3: 使用 tmux 保持会话

```bash
# 在池子账号中启动 tmux
tmux new -s work

# 即使断开连接，会话仍然保持
# 重新连接时
tmux attach -t work
```

### 技巧 4: 批量操作

```bash
# 查看所有空闲池子
claude-status | grep "空闲"

# 释放所有自己占用的池子
# （需要记住占用了哪些）
for i in 1 2 3; do claude-release $i; done
```

---

## 📝 更新日志

- **2026-04-02**: 初始版本
- 后续更新将在此记录

---

**祝使用愉快！** 🎉
