# Skills 规格说明

## 概述

AIPool 部署框架提供 5 个 Claude Code Skills，用于管理 AI 服务池的部署和运维。

## Skills 清单

| Skill | 用途 | 优先级 |
|-------|------|--------|
| `/aipool:init` | 初始化项目配置 | P0 |
| `/aipool:deploy` | 部署到指定服务器 | P0 |
| `/aipool:status` | 检查所有服务器状态 | P0 |
| `/aipool:sync` | 同步有漂移的服务器 | P1 |
| `/aipool:verify` | 验证部署健康度 | P1 |
| `/aipool:rollback` | 回滚到上一版本 | P2 |

## /aipool:init

### 功能

初始化 AIPool 项目配置，创建必要的目录和配置文件。

### 用法

```
/aipool:init
```

### 行为

1. 检查是否已初始化（`.aipool/` 目录是否存在）
2. 创建目录结构：
   ```
   .aipool/
   ├── inventory.yaml
   └── state/
   ```
3. 引导用户填写 `inventory.yaml`：
   - 服务器列表
   - 每台服务器的 provider 和池子数量
4. 验证配置有效性
5. 输出初始化成功信息

### 输出示例

```
✓ 已创建 .aipool/ 目录
✓ 已创建 inventory.yaml 模板

请编辑 .aipool/inventory.yaml 添加服务器信息：

servers:
  dev-server-1:
    host: 192.168.1.10
    user: admin
    pools:
      - provider: claude-code
        count: 4

完成后运行: /aipool:deploy dev-server-1
```

### 错误处理

- 如果已初始化，提示用户并退出
- 如果无法创建目录，报告权限错误

## /aipool:deploy

### 功能

部署 AI 服务池到指定服务器，支持断点续传。

### 用法

```
/aipool:deploy <server-name>
```

### 参数

- `server-name` - 服务器名称（在 inventory.yaml 中定义）

### 行为

1. **读取配置**
   - 从 `inventory.yaml` 读取服务器信息
   - 确定 provider 类型
   - 读取对应的 `adapter.yaml`

2. **检查状态**
   - 读取 `.aipool/state/<server-name>.json`
   - 如果存在，询问是否断点续传

3. **前置检查**
   - 测试 SSH 连通性
   - 执行 adapter.yaml 中的 pre_checks

4. **执行部署步骤**
   - 按顺序执行 deploy_steps
   - 每步完成后更新 state.json
   - 遇到 `type: manual` 暂停等待用户输入

5. **计算文件 hash**
   - 根据 drift_detection.files 计算 hash
   - 保存到 state.json

6. **生成报告**
   - 输出部署摘要
   - 列出完成的步骤和待手动完成的步骤

### 输出示例

```
=== 部署到 dev-server-1 ===

Provider: claude-code
Pools: 4

[前置检查]
✓ SSH 连接成功
✓ 操作系统: Linux
✓ 磁盘空间: 120GB (需要 50GB)

[部署步骤]
✓ create_dirs - 创建共享目录
✓ sync_files - 同步文件到服务器
✓ run_setup - 执行 setup.sh

⏸ auth_login - 需要手动操作

请为 Pool 1 登录 Claude Code：
1. sudo su - claude-pool-1
2. claude auth login
3. 完成浏览器认证
4. 输入 'done' 继续

> _
```

### 错误处理

- SSH 连接失败 → 提示检查网络和权限
- 前置检查失败 → 显示具体失败项，停止部署
- 步骤执行失败 → 保存状态，提示用户修复后重试
- 验证失败 → 提示用户检查手动步骤是否正确完成

## /aipool:status

### 功能

检查所有服务器的部署状态和版本漂移情况。

### 用法

```
/aipool:status
```

### 行为

1. 读取 `inventory.yaml` 获取所有服务器
2. 对每台服务器：
   - SSH 连接
   - 读取 state.json
   - 计算当前文件 hash
   - 对比 state.json 中的 hash
3. 输出状态报告

### 输出示例

```
=== AIPool 服务器状态 ===

dev-server-1 (claude-code, 4 pools)
  状态: ✓ 已部署
  版本: adapter v1.0
  部署时间: 2026-04-02 10:30
  漂移: 无

dev-server-2 (claude-code, 2 pools)
  状态: ✓ 已部署
  版本: adapter v1.0
  部署时间: 2026-04-01 15:20
  漂移: ⚠ 检测到 1 个文件变更
    - scripts/setup.sh (本地已更新)

dev-server-3 (claude-code, 4 pools)
  状态: ⏸ 部署中断
  进度: 3/5 步骤完成
  待完成: auth_login (Pool 3, 4)

建议操作:
- dev-server-2: 运行 /aipool:sync dev-server-2
- dev-server-3: 运行 /aipool:deploy dev-server-3 (断点续传)
```

### 错误处理

- 服务器无法连接 → 标记为 "无法访问"
- state.json 不存在 → 标记为 "未部署"

## /aipool:sync

### 功能

同步有漂移的服务器到最新版本。

### 用法

```
/aipool:sync <server-name>
```

### 参数

- `server-name` - 服务器名称

### 行为

1. 检测漂移文件
2. 显示差异（diff）
3. 询问用户确认
4. 同步文件到服务器
5. 重新计算 hash 并更新 state.json
6. 运行 health_checks 验证

### 输出示例

```
=== 同步 dev-server-2 ===

检测到以下文件有变更:

scripts/setup.sh
  本地: abc123...
  远程: def456...

差异预览:
  + 新增了 claude-monitor 工具安装
  + 优化了日志目录权限设置

确认同步？(y/n) > y

✓ 同步 scripts/setup.sh
✓ 更新 state.json
✓ 健康检查通过

同步完成！
```

### 错误处理

- 无漂移 → 提示"已是最新版本"
- 同步失败 → 保留旧版本，报告错误

## /aipool:verify

### 功能

验证指定服务器的部署健康度。

### 用法

```
/aipool:verify <server-name>
```

### 参数

- `server-name` - 服务器名称

### 行为

1. 读取 adapter.yaml 的 health_checks
2. 逐项执行检查
3. 输出检查结果

### 输出示例

```
=== 验证 dev-server-1 ===

[健康检查]
✓ check_users - 用户账号存在
✓ check_tools - 管理工具已安装
✓ check_pools - 所有池子可用
✓ check_auth - 认证状态正常

健康度: 100% (4/4 通过)
```

### 错误处理

- 检查失败 → 显示具体失败项和建议修复方法

## /aipool:rollback

### 功能

回滚服务器到上一个版本。

### 用法

```
/aipool:rollback <server-name>
```

### 参数

- `server-name` - 服务器名称

### 行为

1. 检查是否有备份
2. 显示当前版本和备份版本信息
3. 询问用户确认
4. 执行 adapter.yaml 中的 rollback.steps
5. 恢复 state.json 到备份版本
6. 运行 health_checks 验证

### 输出示例

```
=== 回滚 dev-server-1 ===

当前版本: adapter v1.1 (2026-04-02 10:30)
备份版本: adapter v1.0 (2026-04-01 15:20)

确认回滚？(y/n) > y

✓ 恢复文件到 /opt/aipool-backup
✓ 恢复 state.json
✓ 健康检查通过

回滚完成！
```

### 错误处理

- 无备份 → 提示"无可用备份"
- 回滚失败 → 尝试恢复到当前版本，报告错误

## 通用规范

### 错误输出格式

```
❌ 错误: <错误描述>

原因: <具体原因>
建议: <修复建议>
```

### 成功输出格式

```
✓ <操作描述>
```

### 进度输出格式

```
[步骤 X/Y] <步骤名称>
  ✓ <子任务 1>
  ✓ <子任务 2>
  ⏳ <子任务 3> (进行中)
```

### 确认提示格式

```
<操作描述>

确认继续？(y/n) > _
```

## 状态码

Skills 应该返回适当的退出码：

- `0` - 成功
- `1` - 一般错误
- `2` - 配置错误
- `3` - 连接错误
- `4` - 验证失败

## 日志

所有 Skills 应该记录操作日志到：

```
.aipool/logs/<server-name>-<timestamp>.log
```

日志格式：

```
[2026-04-02 10:30:15] INFO: 开始部署 dev-server-1
[2026-04-02 10:30:16] INFO: SSH 连接成功
[2026-04-02 10:30:20] INFO: 前置检查通过
[2026-04-02 10:30:25] INFO: 执行步骤: create_dirs
[2026-04-02 10:30:26] INFO: 步骤完成: create_dirs
...
```
