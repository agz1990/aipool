# AIPool 部署框架 - 快速开始指南

## 前提条件

- 已安装 Claude Code CLI
- 服务器支持免密 SSH 登录（`ssh-copy-id`）
- 服务器用户有 `sudo` 权限
- 服务器已安装：`bash`、`rsync`、`jq`

## 5 分钟快速部署

### 第一步：初始化

在项目根目录运行：

```
/aipool:init
```

这会创建 `.aipool/` 目录和 `inventory.yaml` 模板。

### 第二步：配置服务器

编辑 `.aipool/inventory.yaml`：

```yaml
servers:
  my-server:
    host: 192.168.1.10    # 你的服务器 IP
    user: admin           # SSH 用户名
    pools:
      - provider: claude-code
        count: 4          # 池子数量
```

### 第三步：部署

```
/aipool:deploy my-server
```

框架会自动：
1. 检查服务器环境（OS、磁盘空间）
2. 上传部署文件
3. 执行 setup.sh 创建池子账号
4. 暂停等待你完成每个池子的 Claude 认证
5. 保存部署状态

### 第四步：验证

```
/aipool:status
```

查看所有服务器的部署状态和健康度。

## 常用命令

| 命令 | 说明 |
|------|------|
| `/aipool:init` | 初始化项目配置 |
| `/aipool:deploy <server>` | 部署到指定服务器 |
| `/aipool:status` | 查看所有服务器状态 |
| `/aipool:sync <server>` | 同步有漂移的服务器 |
| `/aipool:verify <server>` | 验证部署健康度 |
| `/aipool:rollback <server>` | 回滚到上一版本 |

## 断点续传

部署中断后，直接重新运行：

```
/aipool:deploy my-server
```

框架会检测到未完成的部署，询问是否继续，跳过已完成的步骤。

## 多服务器管理

在 `inventory.yaml` 中添加多台服务器：

```yaml
servers:
  server-1:
    host: 192.168.1.10
    user: admin
    pools:
      - provider: claude-code
        count: 4

  server-2:
    host: 192.168.1.11
    user: admin
    pools:
      - provider: claude-code
        count: 2
```

然后分别部署：

```
/aipool:deploy server-1
/aipool:deploy server-2
```

运行 `/aipool:status` 查看所有服务器的统一状态。
