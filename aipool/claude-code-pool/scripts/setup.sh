#!/bin/bash
# Claude Code 共享池子部署脚本
# 版本: 1.0
# 用途: 在开发主机上部署 Claude Code 共享池子环境

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
POOL_COUNT=4  # 默认 4 个池子，可以通过参数修改
SHARED_REPOS="/shared/repos"
STATUS_DIR="/shared/claude-status"
LOG_DIR="/shared/claude-logs"

# 显示帮助
show_help() {
    cat << EOF
用法: $0 [选项]

选项:
    -n, --pools NUMBER    池子数量 (默认: 4)
    -h, --help           显示此帮助信息

示例:
    $0                   # 创建 4 个池子
    $0 -n 3              # 创建 3 个池子
    $0 --pools 2         # 创建 2 个池子
EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--pools)
            POOL_COUNT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}错误: 未知参数 $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 检查是否为 root 或有 sudo 权限
if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
    echo -e "${RED}错误: 此脚本需要 root 权限或 sudo 权限${NC}"
    exit 1
fi

echo -e "${GREEN}=== Claude Code 共享池子部署脚本 ===${NC}"
echo ""
echo "配置信息："
echo "  池子数量: ${POOL_COUNT}"
echo "  共享代码目录: ${SHARED_REPOS}"
echo "  状态目录: ${STATUS_DIR}"
echo "  日志目录: ${LOG_DIR}"
echo ""

read -p "确认开始部署？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "部署已取消"
    exit 1
fi

# 1. 创建共享目录
echo -e "${YELLOW}>>> 步骤 1/5: 创建共享目录...${NC}"
sudo mkdir -p ${SHARED_REPOS}
sudo mkdir -p ${STATUS_DIR}
sudo mkdir -p ${LOG_DIR}
sudo chmod 755 ${SHARED_REPOS}
sudo chmod 777 ${STATUS_DIR}
sudo chmod 777 ${LOG_DIR}
echo -e "${GREEN}  ✓ 共享目录创建完成${NC}"

# 2. 创建池子账号
echo -e "${YELLOW}>>> 步骤 2/5: 创建池子账号...${NC}"
for i in $(seq 1 ${POOL_COUNT}); do
    POOL_USER="claude-pool-${i}"

    if id "${POOL_USER}" &>/dev/null; then
        echo "  账号 ${POOL_USER} 已存在，跳过"
    else
        sudo useradd -m -s /bin/bash ${POOL_USER}
        echo "  创建账号: ${POOL_USER}"
    fi

    # 创建软链接到共享代码目录
    sudo ln -sf ${SHARED_REPOS} /home/${POOL_USER}/repos

    # 创建个人日志目录
    sudo mkdir -p /home/${POOL_USER}/.claude-logs
    sudo chown ${POOL_USER}:${POOL_USER} /home/${POOL_USER}/.claude-logs

    echo -e "${GREEN}  ✓ ${POOL_USER} 配置完成${NC}"
done

# 3. 安装协调脚本
echo -e "${YELLOW}>>> 步骤 3/5: 安装协调脚本...${NC}"

# claude-status 脚本
sudo tee /usr/local/bin/claude-status > /dev/null << 'EOFSTATUS'
#!/bin/bash
# 显示所有池子的状态

echo "=== Claude Code 池子状态 ==="
echo ""
printf "%-10s %-15s %-30s\n" "池子" "状态" "使用信息"
echo "--------------------------------------------------------"

for i in $(seq 1 10); do
    STATUS_FILE="/shared/claude-status/pool-${i}.lock"
    if [ -f "$STATUS_FILE" ]; then
        CONTENT=$(cat "$STATUS_FILE")
        printf "%-10s %-15s %-30s\n" "Pool ${i}" "🔴 使用中" "${CONTENT}"
    elif id "claude-pool-${i}" &>/dev/null; then
        printf "%-10s %-15s %-30s\n" "Pool ${i}" "🟢 空闲" "-"
    fi
done

echo ""
echo "提示: 使用 'claude-auto 你的名字' 自动分配空闲池子"
EOFSTATUS

# claude-claim 脚本
sudo tee /usr/local/bin/claude-claim > /dev/null << 'EOFCLAIM'
#!/bin/bash
# 手动占用指定的池子

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "用法: claude-claim <pool-number> <your-name>"
    echo "示例: claude-claim 1 张三"
    echo ""
    echo "当前状态："
    claude-status
    exit 1
fi

POOL=$1
USER_NAME=$2
STATUS_FILE="/shared/claude-status/pool-${POOL}.lock"

# 检查池子是否存在
if ! id "claude-pool-${POOL}" &>/dev/null; then
    echo "❌ Pool ${POOL} 不存在"
    exit 1
fi

if [ -f "$STATUS_FILE" ]; then
    echo "❌ Pool ${POOL} 正在被使用："
    cat "$STATUS_FILE"
    echo ""
    echo "请选择其他空闲的池子："
    claude-status
    exit 1
else
    echo "${USER_NAME} @ $(date '+%Y-%m-%d %H:%M:%S')" > "$STATUS_FILE"

    # 记录日志
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${USER_NAME} 占用了 Pool ${POOL}" >> /shared/claude-logs/usage.log

    echo "✅ Pool ${POOL} 已被你占用"
    echo ""
    echo "现在可以连接到池子："
    echo "  ssh claude-pool-${POOL}@localhost"
    echo "  或: sudo su - claude-pool-${POOL}"
    echo ""
    echo "使用完毕后请运行: claude-release ${POOL}"
fi
EOFCLAIM

# claude-release 脚本
sudo tee /usr/local/bin/claude-release > /dev/null << 'EOFRELEASE'
#!/bin/bash
# 释放池子

if [ -z "$1" ]; then
    echo "用法: claude-release <pool-number>"
    exit 1
fi

POOL=$1
STATUS_FILE="/shared/claude-status/pool-${POOL}.lock"

if [ -f "$STATUS_FILE" ]; then
    USER_INFO=$(cat "$STATUS_FILE")
    rm "$STATUS_FILE"

    # 记录日志
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pool ${POOL} 被释放 (之前: ${USER_INFO})" >> /shared/claude-logs/usage.log

    echo "✅ Pool ${POOL} 已释放"
else
    echo "ℹ️  Pool ${POOL} 本来就是空闲的"
fi
EOFRELEASE

# claude-auto 脚本
sudo tee /usr/local/bin/claude-auto > /dev/null << 'EOFAUTO'
#!/bin/bash
# 自动分配空闲池子

if [ -z "$1" ]; then
    echo "用法: claude-auto <your-name>"
    echo "示例: claude-auto 张三"
    exit 1
fi

USER_NAME=$1

# 查找空闲池子
for i in $(seq 1 10); do
    STATUS_FILE="/shared/claude-status/pool-${i}.lock"
    if [ ! -f "$STATUS_FILE" ] && id "claude-pool-${i}" &>/dev/null; then
        POOL=$i
        break
    fi
done

if [ -z "$POOL" ]; then
    echo "❌ 所有池子都在使用中"
    echo ""
    claude-status
    exit 1
fi

# 占用池子
echo "${USER_NAME} @ $(date '+%Y-%m-%d %H:%M:%S')" > "/shared/claude-status/pool-${POOL}.lock"

# 记录日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${USER_NAME} 自动分配到 Pool ${POOL}" >> /shared/claude-logs/usage.log

echo "✅ 自动为你分配了 Pool ${POOL}"
echo ""
echo "正在切换到池子账号..."
echo "退出时会自动释放池子"
echo ""

# 切换到池子账号，退出时自动释放
trap "claude-release ${POOL}" EXIT
sudo su - claude-pool-${POOL}
EOFAUTO

# claude-force-release 脚本（管理员用）
sudo tee /usr/local/bin/claude-force-release > /dev/null << 'EOFFORCE'
#!/bin/bash
# 强制释放所有池子（管理员用）

echo "⚠️  即将强制释放所有池子"
read -p "确认继续？(y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 1
fi

COUNT=0
for i in $(seq 1 10); do
    STATUS_FILE="/shared/claude-status/pool-${i}.lock"
    if [ -f "$STATUS_FILE" ]; then
        USER_INFO=$(cat "$STATUS_FILE")
        rm "$STATUS_FILE"
        echo "释放 Pool ${i} (之前: ${USER_INFO})"

        # 记录日志
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pool ${i} 被强制释放 (之前: ${USER_INFO})" >> /shared/claude-logs/usage.log

        COUNT=$((COUNT + 1))
    fi
done

echo ""
echo "✅ 已释放 ${COUNT} 个池子"
EOFFORCE

# 设置执行权限
sudo chmod +x /usr/local/bin/claude-{status,claim,release,auto,force-release}

echo -e "${GREEN}  ✓ 协调脚本安装完成${NC}"

# 4. 创建使用文档
echo -e "${YELLOW}>>> 步骤 4/5: 创建使用文档...${NC}"
sudo tee /shared/claude-pool-guide.md > /dev/null << 'EOFDOC'
# Claude Code 共享池子使用指南

## 快速开始

### 方式 1: 自动分配（推荐新手）

```bash
# 自动分配一个空闲池子
claude-auto 你的名字

# 系统会自动切换到池子账号
# 退出时自动释放
```

### 方式 2: 手动选择（推荐熟练用户）

```bash
# 1. 查看池子状态
claude-status

# 2. 占用一个空闲池子
claude-claim 1 你的名字

# 3. 切换到池子账号
sudo su - claude-pool-1

# 4. 进入项目目录
cd ~/repos/your-project

# 5. 使用 Claude Code
claude "帮我实现功能"

# 6. 工作完成后退出
exit

# 7. 释放池子
claude-release 1
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `claude-status` | 查看所有池子的状态 |
| `claude-auto 名字` | 自动分配空闲池子 |
| `claude-claim N 名字` | 占用指定池子 |
| `claude-release N` | 释放指定池子 |
| `claude-force-release` | 强制释放所有池子（管理员） |

## 使用规范

### ✅ 良好习惯

1. **使用完立即释放**：不用时立即运行 `claude-release`
2. **下班前检查**：确保释放了所有占用的池子
3. **合理使用时长**：单次使用建议不超过 2-3 小时
4. **团队沟通**：如需长时间使用，在群里提前说明

### ❌ 避免行为

1. **不要长时间占用**：超过 3 小时不使用请释放
2. **不要同时占用多个池子**：一人一个池子
3. **不要忘记释放**：这会阻塞其他人使用
4. **不要在池子里存储重要文件**：使用共享代码目录

## 常见问题

### Q: 忘记释放池子怎么办？
A: 其他人可以运行 `claude-release <pool-number>` 强制释放，或联系管理员

### Q: 所有池子都被占用怎么办？
A:
1. 运行 `claude-status` 查看占用情况
2. 在团队群里询问是否有人可以释放
3. 如果有池子长时间无人使用，可以强制释放

### Q: 如何查看使用历史？
A: 查看日志文件 `cat /shared/claude-logs/usage.log`

### Q: 池子账号的密码是什么？
A: 不需要密码，使用 `sudo su - claude-pool-N` 切换

### Q: 可以在池子里安装软件吗？
A: 可以，但建议只安装必要的开发工具

### Q: 代码应该放在哪里？
A: 放在 `~/repos/` 目录（这是指向 `/shared/repos` 的软链接）

## 故障排查

### 问题：无法切换到池子账号
```bash
# 检查账号是否存在
id claude-pool-1

# 如果不存在，联系管理员
```

### 问题：Claude Code 命令不存在
```bash
# 检查是否已安装
which claude

# 如果未安装，需要在池子账号中安装
sudo su - claude-pool-1
# 按照官方文档安装 Claude Code
```

### 问题：提示权限不足
```bash
# 确保使用 sudo
sudo su - claude-pool-1

# 或者联系管理员添加你到 sudo 组
```

## 管理员操作

### 查看使用统计
```bash
# 查看使用日志
cat /shared/claude-logs/usage.log

# 统计今天的使用次数
grep "$(date '+%Y-%m-%d')" /shared/claude-logs/usage.log | wc -l

# 查看当前占用情况
claude-status
```

### 强制释放所有池子
```bash
# 谨慎使用！会释放所有正在使用的池子
claude-force-release
```

### 添加新池子
```bash
# 创建新账号
sudo useradd -m -s /bin/bash claude-pool-5
sudo ln -sf /shared/repos /home/claude-pool-5/repos

# 登录 Claude Code
sudo su - claude-pool-5
claude auth login
```

## 技术支持

如有问题，请联系：
- 团队管理员
- 或在团队群里询问

---

最后更新: $(date '+%Y-%m-%d')
EOFDOC

sudo chmod 644 /shared/claude-pool-guide.md
echo -e "${GREEN}  ✓ 使用文档: /shared/claude-pool-guide.md${NC}"

# 5. 创建监控脚本
echo -e "${YELLOW}>>> 步骤 5/5: 创建监控脚本...${NC}"
sudo tee /usr/local/bin/claude-monitor > /dev/null << 'EOFMONITOR'
#!/bin/bash
# 监控池子使用情况

echo "=== Claude Code 池子监控 ==="
echo ""

# 当前状态
echo "【当前状态】"
claude-status
echo ""

# 今日使用统计
echo "【今日使用统计】"
TODAY=$(date '+%Y-%m-%d')
if [ -f /shared/claude-logs/usage.log ]; then
    USAGE_COUNT=$(grep "$TODAY" /shared/claude-logs/usage.log | grep "占用" | wc -l)
    echo "今日使用次数: ${USAGE_COUNT}"
    echo ""
    echo "今日使用记录:"
    grep "$TODAY" /shared/claude-logs/usage.log | tail -10
else
    echo "暂无使用记录"
fi
EOFMONITOR

sudo chmod +x /usr/local/bin/claude-monitor

echo -e "${GREEN}  ✓ 监控脚本安装完成${NC}"

# 完成
echo ""
echo -e "${GREEN}=== 部署完成 ===${NC}"
echo ""
echo -e "${YELLOW}下一步操作：${NC}"
echo ""
echo "1. 在每个池子账号中登录 Claude Code："
for i in $(seq 1 ${POOL_COUNT}); do
    echo -e "   ${GREEN}sudo su - claude-pool-${i}${NC}"
    echo "   claude auth login"
    echo "   exit"
    echo ""
done
echo "2. 查看使用文档:"
echo -e "   ${GREEN}cat /shared/claude-pool-guide.md${NC}"
echo ""
echo "3. 测试命令:"
echo -e "   ${GREEN}claude-status${NC}        # 查看池子状态"
echo -e "   ${GREEN}claude-monitor${NC}       # 查看监控信息"
echo ""
echo "4. 开始使用:"
echo -e "   ${GREEN}claude-auto 你的名字${NC}  # 自动分配池子"
echo ""
