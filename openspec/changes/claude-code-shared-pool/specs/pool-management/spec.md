## ADDED Requirements

### Requirement: 创建池子账号
系统 SHALL 能够创建独立的 Linux 用户账号作为 Claude Code 池子。

#### Scenario: 成功创建池子账号
- **WHEN** 管理员运行部署脚本指定池子数量
- **THEN** 系统创建对应数量的 claude-pool-N 账号（N 从 1 开始）

#### Scenario: 池子账号已存在
- **WHEN** 部署脚本检测到池子账号已存在
- **THEN** 系统跳过创建并显示提示信息

### Requirement: 配置共享目录
系统 SHALL 为每个池子配置访问共享代码目录的能力。

#### Scenario: 创建共享目录软链接
- **WHEN** 池子账号创建完成
- **THEN** 系统在池子 home 目录创建指向 /shared/repos 的软链接

#### Scenario: 共享目录权限设置
- **WHEN** 创建共享目录
- **THEN** 系统设置适当的权限（755）允许所有池子读写

### Requirement: 池子环境配置
系统 SHALL 为每个池子配置必要的环境和目录结构。

#### Scenario: 创建日志目录
- **WHEN** 池子账号创建完成
- **THEN** 系统在池子 home 目录创建 .claude-logs 目录

#### Scenario: 设置 shell 环境
- **WHEN** 池子账号创建完成
- **THEN** 系统设置 bash 作为默认 shell
