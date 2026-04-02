# Claude Code 共享池子 - 管理员手册

## 📋 目录

1. [部署指南](#部署指南)
2. [日常维护](#日常维护)
3. [监控和统计](#监控和统计)
4. [故障处理](#故障处理)
5. [扩展和优化](#扩展和优化)
6. [安全和合规](#安全和合规)

---

## 🚀 部署指南

### 系统要求

```
操作系统: Linux (Ubuntu/Debian/CentOS) 或 macOS
权限: root 或 sudo 权限
磁盘空间: 至少 50GB（用于共享代码）
内存: 建议 16GB+（支持多个并发用户）
网络: 稳定的美国网络连接
```

### 快速部署

#### 步骤 1: 下载部署脚本

```bash
# 假设脚本已经在 claude-pool-solution/scripts/setup.sh

# 添加执行权限
chmod +x claude-pool-solution/scripts/setup.sh
```

#### 步骤 2: 运行部署脚本

```bash
# 默认创建 4 个池子
sudo ./claude-pool-solution/scripts/setup.sh

# 或指定池子数量
sudo ./claude-pool-solution/scripts/setup.sh -n 3  # 创建 3 个池子
```

#### 步骤 3: 为每个池子登录 Claude Code

```bash
# 对每个池子重复以下操作

# 切换到池子账号
sudo su - claude-pool-1

# 登录 Claude Code
claude auth login
# 按照提示完成登录（使用不同的 Claude Code 订阅）

# 测试
claude "hello"

# 退出
exit

# 对 pool-2, pool-3, pool-4 重复上述操作
```

#### 步骤 4: 验证部署

```bash
# 查看池子状态
claude-status

# 应该看到所有池子都是空闲状态
# Pool 1: 🟢 空闲
# Pool 2: 🟢 空闲
# Pool 3: 🟢 空闲
# Pool 4: 🟢 空闲
```

### 详细配置

#### 自定义共享目录位置

编辑部署脚本中的配置：

```bash
# 在 setup.sh 中修改
SHARED_REPOS="/your/custom/path/repos"
STATUS_DIR="/your/custom/path/status"
LOG_DIR="/your/custom/path/logs"
```

#### 配置用户权限

```bash
# 允许特定用户使用 sudo 切换到池子账号
# 编辑 /etc/sudoers.d/claude-pool

# 创建配置文件
sudo visudo -f /etc/sudoers.d/claude-pool

# 添加以下内容
%developers ALL=(claude-pool-1,claude-pool-2,claude-pool-3,claude-pool-4) NOPASSWD: ALL

# 将用户添加到 developers 组
sudo usermod -aG developers username
```

---

## 🔧 日常维护

### 每日检查清单

```bash
# 1. 查看池子状态
claude-status

# 2. 查看监控信息
claude-monitor

# 3. 检查日志
tail -50 /shared/claude-logs/usage.log

# 4. 检查磁盘空间
df -h /shared/repos

# 5. 检查系统负载
top
htop  # 如果安装了
```

### 每周维护任务

#### 1. 清理日志

```bash
# 归档旧日志
cd /shared/claude-logs
sudo gzip usage.log.$(date -d '7 days ago' '+%Y%m%d')

# 删除 30 天前的日志
find /shared/claude-logs -name "*.gz" -mtime +30 -delete
```

#### 2. 检查订阅状态

```bash
# 在每个池子中检查 Claude Code 状态
for i in 1 2 3 4; do
    echo "检查 Pool $i..."
    sudo su - claude-pool-$i -c "claude --version"
done
```

#### 3. 清理临时文件

```bash
# 清理共享目录中的临时文件
find /shared/repos -name "*.tmp" -delete
find /shared/repos -name ".DS_Store" -delete
find /shared/repos -name "__pycache__" -type d -exec rm -rf {} +
```

### 每月维护任务

#### 1. 生成使用报告

```bash
# 创建月度报告脚本
cat > /usr/local/bin/claude-monthly-report << 'EOF'
#!/bin/bash

MONTH=$(date '+%Y-%m')
LOG_FILE="/shared/claude-logs/usage.log"

echo "=== Claude Code 月度使用报告 ($MONTH) ==="
echo ""

# 总使用次数
TOTAL=$(grep "$MONTH" "$LOG_FILE" | grep "占用" | wc -l)
echo "总使用次数: $TOTAL"

# 按用户统计
echo ""
echo "用户使用统计:"
grep "$MONTH" "$LOG_FILE" | grep "占用" | awk '{print $4}' | sort | uniq -c | sort -rn

# 按池子统计
echo ""
echo "池子使用统计:"
grep "$MONTH" "$LOG_FILE" | grep "占用" | grep -oP 'Pool \d+' | sort | uniq -c | sort -rn

# 高峰时段
echo ""
echo "使用高峰时段:"
grep "$MONTH" "$LOG_FILE" | grep "占用" | awk '{print $2}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -5
EOF

chmod +x /usr/local/bin/claude-monthly-report

# 运行报告
claude-monthly-report
```

#### 2. 更新系统和软件

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# 或
sudo yum update -y  # CentOS

# 更新 Claude Code（在每个池子中）
for i in 1 2 3 4; do
    echo "更新 Pool $i..."
    sudo su - claude-pool-$i -c "claude update"
done
```

---

## 📊 监控和统计

### 实时监控

#### 创建监控仪表板

```bash
# 创建实时监控脚本
cat > /usr/local/bin/claude-dashboard << 'EOF'
#!/bin/bash

while true; do
    clear
    echo "=== Claude Code 实时监控 ==="
    echo "更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    # 池子状态
    claude-status
    echo ""

    # 系统资源
    echo "【系统资源】"
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
    echo "内存: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "磁盘: $(df -h /shared/repos | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
    echo ""

    # 今日统计
    echo "【今日统计】"
    TODAY=$(date '+%Y-%m-%d')
    USAGE_COUNT=$(grep "$TODAY" /shared/claude-logs/usage.log 2>/dev/null | grep "占用" | wc -l)
    echo "使用次数: $USAGE_COUNT"

    sleep 5
done
EOF

chmod +x /usr/local/bin/claude-dashboard

# 运行监控
claude-dashboard
```

### 使用统计分析

#### 1. 用户活跃度分析

```bash
# 最活跃用户（本周）
grep "$(date '+%Y-%m')" /shared/claude-logs/usage.log | \
    grep "占用" | \
    awk '{print $4}' | \
    sort | uniq -c | sort -rn | head -10
```

#### 2. 池子利用率分析

```bash
# 各池子使用频率
grep "$(date '+%Y-%m')" /shared/claude-logs/usage.log | \
    grep "占用" | \
    grep -oP 'Pool \d+' | \
    sort | uniq -c | sort -rn
```

#### 3. 高峰时段分析

```bash
# 每小时使用量
grep "$(date '+%Y-%m-%d')" /shared/claude-logs/usage.log | \
    grep "占用" | \
    awk '{print $2}' | \
    cut -d: -f1 | \
    sort | uniq -c
```

### 告警设置

#### 创建告警脚本

```bash
cat > /usr/local/bin/claude-alert << 'EOF'
#!/bin/bash

# 配置
ALERT_EMAIL="admin@example.com"  # 修改为实际邮箱
DISK_THRESHOLD=80  # 磁盘使用率阈值

# 检查磁盘空间
DISK_USAGE=$(df /shared/repos | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
    echo "警告: 磁盘使用率 ${DISK_USAGE}% 超过阈值 ${DISK_THRESHOLD}%" | \
        mail -s "Claude Pool 磁盘告警" "$ALERT_EMAIL"
fi

# 检查长时间占用
for i in 1 2 3 4; do
    STATUS_FILE="/shared/claude-status/pool-${i}.lock"
    if [ -f "$STATUS_FILE" ]; then
        # 检查文件修改时间
        MTIME=$(stat -c %Y "$STATUS_FILE" 2>/dev/null || stat -f %m "$STATUS_FILE")
        NOW=$(date +%s)
        DIFF=$((NOW - MTIME))

        # 如果超过 4 小时（14400 秒）
        if [ "$DIFF" -gt 14400 ]; then
            USER_INFO=$(cat "$STATUS_FILE")
            echo "警告: Pool $i 已被占用超过 4 小时 - $USER_INFO" | \
                mail -s "Claude Pool 长时间占用告警" "$ALERT_EMAIL"
        fi
    fi
done
EOF

chmod +x /usr/local/bin/claude-alert

# 添加到 crontab（每小时检查一次）
(crontab -l 2>/dev/null; echo "0 * * * * /usr/local/bin/claude-alert") | crontab -
```

---

## 🔥 故障处理

### 常见问题处理

#### 问题 1: 池子账号无法登录

**诊断**：
```bash
# 检查账号是否存在
id claude-pool-1

# 检查账号状态
sudo passwd -S claude-pool-1

# 检查 home 目录
ls -la /home/claude-pool-1
```

**解决**：
```bash
# 重新创建账号
sudo userdel -r claude-pool-1
sudo useradd -m -s /bin/bash claude-pool-1
sudo ln -sf /shared/repos /home/claude-pool-1/repos
```

#### 问题 2: Claude Code 认证失败

**诊断**：
```bash
# 切换到池子账号
sudo su - claude-pool-1

# 检查认证状态
claude auth status

# 查看配置
cat ~/.claude/config
```

**解决**：
```bash
# 重新登录
claude auth logout
claude auth login

# 如果仍然失败，检查网络
ping claude.ai
curl -I https://claude.ai
```

#### 问题 3: 共享目录权限问题

**诊断**：
```bash
# 检查目录权限
ls -la /shared/repos

# 检查软链接
ls -la /home/claude-pool-1/repos
```

**解决**：
```bash
# 修复权限
sudo chmod 755 /shared/repos
sudo chown -R root:root /shared/repos

# 重新创建软链接
for i in 1 2 3 4; do
    sudo ln -sf /shared/repos /home/claude-pool-$i/repos
done
```

#### 问题 4: 状态文件损坏

**诊断**：
```bash
# 检查状态文件
ls -la /shared/claude-status/

# 查看文件内容
cat /shared/claude-status/pool-*.lock
```

**解决**：
```bash
# 清理所有状态文件
sudo rm -f /shared/claude-status/*.lock

# 重新初始化
sudo mkdir -p /shared/claude-status
sudo chmod 777 /shared/claude-status
```

### 紧急恢复程序

#### 完全重置

```bash
# ⚠️ 警告：这会清除所有状态和日志

# 1. 强制释放所有池子
claude-force-release

# 2. 清理状态文件
sudo rm -f /shared/claude-status/*.lock

# 3. 备份日志
sudo cp /shared/claude-logs/usage.log /shared/claude-logs/usage.log.backup.$(date +%Y%m%d)

# 4. 重启相关服务（如果有）
# sudo systemctl restart <service-name>

# 5. 验证
claude-status
```

---

## 📈 扩展和优化

### 添加新池子

```bash
# 创建新池子账号
POOL_NUM=5
sudo useradd -m -s /bin/bash claude-pool-${POOL_NUM}
sudo ln -sf /shared/repos /home/claude-pool-${POOL_NUM}/repos

# 登录 Claude Code
sudo su - claude-pool-${POOL_NUM}
claude auth login
exit

# 验证
claude-status
```

### 升级池子订阅

```bash
# 如果某个池子需要更高的配额
# 在该池子账号中重新登录更高级别的订阅

sudo su - claude-pool-1
claude auth logout
claude auth login  # 使用 Max 订阅登录
exit
```

### 性能优化

#### 1. 磁盘 I/O 优化

```bash
# 使用 SSD 存储共享代码
# 如果有多个磁盘，将共享目录移到 SSD

# 检查磁盘性能
sudo hdparm -Tt /dev/sda

# 启用 noatime 挂载选项
# 编辑 /etc/fstab
/dev/sdb1 /shared/repos ext4 defaults,noatime 0 2
```

#### 2. 网络优化

```bash
# 优化 TCP 参数
sudo sysctl -w net.ipv4.tcp_fin_timeout=30
sudo sysctl -w net.ipv4.tcp_keepalive_time=1200
sudo sysctl -w net.core.netdev_max_backlog=5000

# 持久化配置
sudo tee -a /etc/sysctl.conf << EOF
net.ipv4.tcp_fin_timeout=30
net.ipv4.tcp_keepalive_time=1200
net.core.netdev_max_backlog=5000
EOF
```

#### 3. 内存优化

```bash
# 增加 swap 空间（如果内存不足）
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 持久化
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 横向扩展（多台服务器）

如果需要为其他团队提供服务：

```
架构设计：

┌─────────────────────────────────────────┐
│  团队 A                                  │
│  Mac Studio 1                           │
│  - 4 个池子                              │
│  - 服务 10-15 人                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  团队 B                                  │
│  Mac Studio 2                           │
│  - 4 个池子                              │
│  - 服务 10-15 人                         │
└─────────────────────────────────────────┘

每台服务器独立部署，互不干扰
```

---

## 🔒 安全和合规

### 安全最佳实践

#### 1. 访问控制

```bash
# 限制 SSH 访问
# 编辑 /etc/ssh/sshd_config
AllowUsers your-admin-user developer1 developer2

# 禁用密码登录，只允许密钥
PasswordAuthentication no
PubkeyAuthentication yes

# 重启 SSH 服务
sudo systemctl restart sshd
```

#### 2. 审计日志

```bash
# 启用详细的审计日志
sudo apt install auditd  # Ubuntu/Debian

# 监控池子账号的活动
sudo auditctl -w /home/claude-pool-1 -p wa -k claude-pool-1
sudo auditctl -w /home/claude-pool-2 -p wa -k claude-pool-2
sudo auditctl -w /home/claude-pool-3 -p wa -k claude-pool-3
sudo auditctl -w /home/claude-pool-4 -p wa -k claude-pool-4

# 查看审计日志
sudo ausearch -k claude-pool-1
```

#### 3. 定期备份

```bash
# 创建备份脚本
cat > /usr/local/bin/claude-backup << 'EOF'
#!/bin/bash

BACKUP_DIR="/backup/claude-pool"
DATE=$(date +%Y%m%d)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份共享代码
tar -czf "$BACKUP_DIR/repos-$DATE.tar.gz" /shared/repos

# 备份日志
tar -czf "$BACKUP_DIR/logs-$DATE.tar.gz" /shared/claude-logs

# 备份配置
tar -czf "$BACKUP_DIR/config-$DATE.tar.gz" /usr/local/bin/claude-*

# 删除 30 天前的备份
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: $DATE"
EOF

chmod +x /usr/local/bin/claude-backup

# 添加到 crontab（每天凌晨 2 点备份）
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/claude-backup") | crontab -
```

### 合规性考虑

#### Anthropic 服务条款

```
⚠️ 重要提醒：

1. 账号共享可能违反 Anthropic 服务条款
2. 建议定期检查服务条款更新
3. 准备好转向合规方案的备选计划

风险缓解：
- 不要在多个地理位置同时登录
- 使用量保持在合理范围
- 避免 24/7 连续使用
- 准备好 Teams 计划或 API 方案作为备选
```

#### 数据隐私

```bash
# 定期清理敏感数据
# 创建清理脚本
cat > /usr/local/bin/claude-cleanup << 'EOF'
#!/bin/bash

# 清理临时文件
find /shared/repos -name "*.tmp" -delete
find /shared/repos -name ".env" -delete
find /shared/repos -name "*.key" -delete
find /shared/repos -name "*.pem" -delete

# 清理 Claude Code 缓存
for i in 1 2 3 4; do
    rm -rf /home/claude-pool-$i/.claude/cache/*
done

echo "清理完成"
EOF

chmod +x /usr/local/bin/claude-cleanup

# 每周运行一次
(crontab -l 2>/dev/null; echo "0 0 * * 0 /usr/local/bin/claude-cleanup") | crontab -
```

---

## 📞 支持和联系

### 获取帮助

- **Anthropic 支持**: https://support.anthropic.com
- **Claude Code 文档**: https://docs.anthropic.com/claude-code
- **社区论坛**: https://community.anthropic.com

### 报告问题

如果遇到无法解决的问题：

1. 收集诊断信息
2. 查看日志文件
3. 联系 Anthropic 支持

---

## 📝 附录

### 完整命令参考

| 命令 | 说明 | 权限 |
|------|------|------|
| `claude-status` | 查看池子状态 | 所有用户 |
| `claude-claim N 名字` | 占用池子 | 所有用户 |
| `claude-release N` | 释放池子 | 所有用户 |
| `claude-auto 名字` | 自动分配池子 | 所有用户 |
| `claude-monitor` | 查看监控信息 | 所有用户 |
| `claude-force-release` | 强制释放所有池子 | 管理员 |
| `claude-monthly-report` | 生成月度报告 | 管理员 |
| `claude-dashboard` | 实时监控仪表板 | 管理员 |
| `claude-alert` | 告警检查 | 管理员 |
| `claude-backup` | 备份数据 | 管理员 |
| `claude-cleanup` | 清理数据 | 管理员 |

### 目录结构

```
/shared/
├── repos/              # 共享代码目录
├── claude-status/      # 池子状态文件
│   ├── pool-1.lock
│   ├── pool-2.lock
│   └── ...
├── claude-logs/        # 日志目录
│   └── usage.log
└── claude-pool-guide.md  # 使用文档

/home/
├── claude-pool-1/      # 池子 1 账号
│   ├── repos -> /shared/repos
│   └── .claude/
├── claude-pool-2/      # 池子 2 账号
└── ...

/usr/local/bin/
├── claude-status       # 状态查看
├── claude-claim        # 占用池子
├── claude-release      # 释放池子
├── claude-auto         # 自动分配
├── claude-monitor      # 监控
└── ...                 # 其他管理脚本
```

---

**最后更新**: 2026-04-02
