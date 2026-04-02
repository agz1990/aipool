# Claude Code API 网关 - 架构设计

## 概述

将共享的 Claude Code CLI 池子封装成 HTTP API 服务，团队成员通过 API Key 访问，无需 SSH 到服务器。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        完整架构图                                 │
│                                                                   │
│  中国开发者 A (本地)                                              │
│      │                                                            │
│      │ ① HTTPS 请求                                              │
│      │    POST /api/v1/chat                                      │
│      │    Authorization: Bearer <api-key-a>                      │
│      │    Body: { "message": "帮我实现登录功能" }                 │
│      ▼                                                            │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  美国服务器 - API 网关服务                            │       │
│  │                                                        │       │
│  │  ┌────────────────────────────────────────────┐      │       │
│  │  │  API Gateway (Node.js/Express)             │      │       │
│  │  │                                             │      │       │
│  │  │  ┌──────────────────────────────────┐     │      │       │
│  │  │  │  认证层                           │     │      │       │
│  │  │  │  - 验证 API Key                   │     │      │       │
│  │  │  │  - 检查配额                       │     │      │       │
│  │  │  │  - 记录请求                       │     │      │       │
│  │  │  └──────────────────────────────────┘     │      │       │
│  │  │           │                                │      │       │
│  │  │           ▼                                │      │       │
│  │  │  ┌──────────────────────────────────┐     │      │       │
│  │  │  │  请求队列管理                     │     │      │       │
│  │  │  │  - 分配空闲池子                   │     │      │       │
│  │  │  │  - 排队等待                       │     │      │       │
│  │  │  │  - 超时处理                       │     │      │       │
│  │  │  └──────────────────────────────────┘     │      │       │
│  │  │           │                                │      │       │
│  │  │           ▼                                │      │       │
│  │  │  ┌──────────────────────────────────┐     │      │       │
│  │  │  │  Claude Code 执行器               │     │      │       │
│  │  │  │  - 调用 CLI                       │     │      │       │
│  │  │  │  - 流式输出                       │     │      │       │
│  │  │  │  - 错误处理                       │     │      │       │
│  │  │  └──────────────────────────────────┘     │      │       │
│  │  │           │                                │      │       │
│  │  └───────────┼────────────────────────────────┘      │       │
│  │              │                                        │       │
│  │              ▼                                        │       │
│  │  ┌────────────────────────────────────────────┐      │       │
│  │  │  Claude Code 池子                          │      │       │
│  │  │                                             │      │       │
│  │  │  Pool 1: 🟢 空闲                           │      │       │
│  │  │  Pool 2: 🔴 处理中 (用户 A 的请求)         │      │       │
│  │  │  Pool 3: 🟢 空闲                           │      │       │
│  │  │  Pool 4: 🔴 处理中 (用户 B 的请求)         │      │       │
│  │  │                                             │      │       │
│  │  └────────────────────────────────────────────┘      │       │
│  │                                                        │       │
│  │  ┌────────────────────────────────────────────┐      │       │
│  │  │  数据存储 (SQLite)                         │      │       │
│  │  │  - API Keys                                │      │       │
│  │  │  - 用户配额                                │      │       │
│  │  │  - 使用统计                                │      │       │
│  │  │  - 请求日志                                │      │       │
│  │  └────────────────────────────────────────────┘      │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 核心优势

### vs 直接 SSH 方案

| 维度 | SSH 方案 | API 网关方案 |
|------|---------|-------------|
| **用户体验** | 需要 SSH 连接 | HTTP API，本地使用 |
| **学习成本** | 需要学习 Linux 命令 | 简单的 API 调用 |
| **IDE 集成** | 困难 | 容易（VS Code 插件） |
| **权限管理** | 需要 SSH 权限 | API Key 即可 |
| **使用追踪** | 基于日志 | 精确的使用统计 |
| **配额控制** | 手动协调 | 自动化配额管理 |
| **商业化** | 不可行 | 可对外提供服务 |

## API 设计

### 1. 发送消息

```http
POST /api/v1/chat
Authorization: Bearer ck_live_1234567890abcdef
Content-Type: application/json

{
  "message": "帮我实现用户登录功能",
  "context": {
    "project": "my-app",
    "files": ["/src/auth.js"]
  }
}
```

**响应**:
```json
{
  "id": "req_abc123",
  "status": "completed",
  "response": "我来帮你实现用户登录功能...",
  "usage": {
    "tokens_input": 150,
    "tokens_output": 500
  },
  "pool_id": 2,
  "duration_ms": 3500
}
```

### 2. 流式对话

```http
POST /api/v1/chat/stream
Authorization: Bearer ck_live_1234567890abcdef
Content-Type: application/json

{
  "message": "帮我实现用户登录功能"
}
```

**响应** (Server-Sent Events):
```
data: {"type":"start","request_id":"req_abc123"}

data: {"type":"chunk","content":"我来"}

data: {"type":"chunk","content":"帮你"}

data: {"type":"done","usage":{"tokens":650}}
```

### 3. 查看使用量

```http
GET /api/v1/usage
Authorization: Bearer ck_live_1234567890abcdef
```

**响应**:
```json
{
  "quota": {
    "daily": {
      "limit": 100,
      "used": 45,
      "remaining": 55
    },
    "monthly": {
      "limit": 3000,
      "used": 1250,
      "remaining": 1750
    }
  }
}
```

## 客户端使用

### Python SDK

```python
from claude_code_client import ClaudeCodeClient

client = ClaudeCodeClient(api_key="ck_live_xxx")

# 发送消息
response = client.chat("帮我实现用户登录功能")
print(response.content)

# 流式对话
for chunk in client.chat_stream("帮我实现用户登录功能"):
    print(chunk, end='', flush=True)
```

### JavaScript SDK

```javascript
import { ClaudeCodeClient } from 'claude-code-client';

const client = new ClaudeCodeClient({ apiKey: 'ck_live_xxx' });

// 发送消息
const response = await client.chat('帮我实现用户登录功能');
console.log(response.content);

// 流式对话
const stream = await client.chatStream('帮我实现用户登录功能');
for await (const chunk of stream) {
  process.stdout.write(chunk);
}
```

### CLI 工具

```bash
# 配置
claude-code config set-key ck_live_xxx

# 使用
claude-code chat "帮我实现用户登录功能"

# 流式输出
claude-code chat --stream "帮我实现用户登录功能"

# 查看使用量
claude-code usage
```

## 技术实现

### 核心组件

1. **API Gateway** (Node.js + Express)
   - HTTP 服务器
   - 路由管理
   - WebSocket 支持

2. **认证层**
   - API Key 验证
   - 配额检查
   - 请求限流

3. **队列管理器**
   - 池子分配
   - 请求排队
   - 负载均衡

4. **Claude Code 执行器**
   - CLI 调用
   - 输出捕获
   - 流式传输

5. **数据存储** (SQLite)
   - API Keys
   - 使用记录
   - 池子状态

### 数据库设计

```sql
-- API Keys
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    quota_daily INTEGER DEFAULT 100,
    quota_monthly INTEGER DEFAULT 3000,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- 使用记录
CREATE TABLE usage_logs (
    id INTEGER PRIMARY KEY,
    api_key_id INTEGER,
    request_id TEXT,
    message TEXT,
    tokens_input INTEGER,
    tokens_output INTEGER,
    pool_id INTEGER,
    duration_ms INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 池子状态
CREATE TABLE pool_status (
    pool_id INTEGER PRIMARY KEY,
    status TEXT CHECK(status IN ('idle', 'busy', 'error')),
    current_user TEXT,
    started_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 部署方案

### Docker 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  api-gateway:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=/data/claude-code.db
      - POOL_COUNT=4
    volumes:
      - ./data:/data
      - /shared:/shared
    restart: unless-stopped
```

### 系统要求

- Node.js 18+
- 4GB RAM
- 20GB 磁盘空间
- 已部署的 Claude Code 池子

## 成本分析

### 开发成本

```
初期开发: 14-22 天
- API Gateway: 3-5 天
- 认证和配额: 2-3 天
- 队列管理: 2-3 天
- Claude Code 集成: 3-5 天
- 客户端 SDK: 2-3 天
- 文档和测试: 2-3 天

维护成本: 每月 2-4 小时
```

### 运营成本

```
月成本: $80 (4个池子订阅)
vs 独立订阅: $300 (15人)
节省: 73%

如果对外提供服务:
- 可以收费覆盖成本
- 甚至产生利润
```

## 风险和缓解

### 风险 1: Claude Code CLI 交互复杂

**缓解**:
- 使用 `pty` 库处理交互
- 预先测试各种场景
- 实现重试机制

### 风险 2: 并发限制

**缓解**:
- 实现请求队列
- 提供队列位置反馈
- 动态调整池子数量

### 风险 3: 合规性

**缓解**:
- 明确告知用户风险
- 准备备选方案（Claude API）
- 监控警告信号

## 下一步

1. **实现 API Gateway 核心功能**
2. **开发客户端 SDK**
3. **编写部署文档**
4. **测试和优化**

---

**更新**: 2026-04-02
