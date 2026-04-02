## ADDED Requirements

### Requirement: 一键部署脚本
系统 SHALL 提供一键部署脚本完成整个系统的安装和配置。

#### Scenario: 执行部署
- **WHEN** 管理员运行 setup.sh 脚本
- **THEN** 系统自动完成所有配置步骤并显示进度

#### Scenario: 指定池子数量
- **WHEN** 管理员运行 setup.sh -n N
- **THEN** 系统创建 N 个池子

#### Scenario: 显示帮助信息
- **WHEN** 管理员运行 setup.sh --help
- **THEN** 系统显示使用说明和参数选项

### Requirement: 创建共享目录
脚本 SHALL 自动创建所有必需的共享目录。

#### Scenario: 创建目录结构
- **WHEN** 执行部署脚本
- **THEN** 系统创建 /shared/repos、/shared/claude-status 和 /shared/claude-logs 目录

#### Scenario: 设置目录权限
- **WHEN** 创建共享目录
- **THEN** 系统设置适当的权限（755 或 777）

### Requirement: 安装协调脚本
脚本 SHALL 自动安装所有用户和管理员工具。

#### Scenario: 安装用户工具
- **WHEN** 执行部署脚本
- **THEN** 系统安装 claude-status、claude-claim、claude-release、claude-auto 到 /usr/local/bin

#### Scenario: 安装管理工具
- **WHEN** 执行部署脚本
- **THEN** 系统安装 claude-monitor、claude-force-release 等管理工具到 /usr/local/bin

#### Scenario: 设置执行权限
- **WHEN** 安装脚本
- **THEN** 系统为所有脚本添加执行权限

### Requirement: 生成使用文档
脚本 SHALL 自动生成服务器上的使用文档。

#### Scenario: 创建使用指南
- **WHEN** 执行部署脚本
- **THEN** 系统在 /shared 目录生成 claude-pool-guide.md 文档

### Requirement: 部署验证
脚本 SHALL 在部署完成后提供验证和后续步骤指引。

#### Scenario: 显示完成信息
- **WHEN** 部署完成
- **THEN** 系统显示成功消息和后续操作步骤

#### Scenario: 提供登录指引
- **WHEN** 部署完成
- **THEN** 系统显示如何为每个池子登录 Claude Code 的命令

### Requirement: 错误处理
脚本 SHALL 在遇到错误时提供清晰的错误信息。

#### Scenario: 权限不足
- **WHEN** 脚本检测到没有 sudo 权限
- **THEN** 系统显示错误消息并退出

#### Scenario: 参数错误
- **WHEN** 用户提供无效参数
- **THEN** 系统显示错误消息和帮助信息
