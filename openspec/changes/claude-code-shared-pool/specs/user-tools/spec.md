## ADDED Requirements

### Requirement: 查看池子状态
系统 SHALL 提供命令查看所有池子的当前状态。

#### Scenario: 显示所有池子状态
- **WHEN** 用户运行 claude-status 命令
- **THEN** 系统显示所有池子的状态（空闲/使用中）和占用者信息

#### Scenario: 格式化输出
- **WHEN** 显示池子状态
- **THEN** 输出使用表格格式，包含池子编号、状态图标和使用信息

### Requirement: 手动占用池子
系统 SHALL 提供命令手动占用指定的池子。

#### Scenario: 成功占用池子
- **WHEN** 用户运行 claude-claim N 用户名
- **THEN** 系统占用池子 N 并显示成功消息和使用提示

#### Scenario: 池子已被占用
- **WHEN** 用户尝试占用已被占用的池子
- **THEN** 系统显示错误消息和当前占用者信息，并建议查看其他空闲池子

#### Scenario: 池子不存在
- **WHEN** 用户尝试占用不存在的池子
- **THEN** 系统显示错误消息

### Requirement: 释放池子
系统 SHALL 提供命令释放指定的池子。

#### Scenario: 成功释放池子
- **WHEN** 用户运行 claude-release N
- **THEN** 系统释放池子 N 并显示成功消息

#### Scenario: 池子本来就空闲
- **WHEN** 用户尝试释放空闲的池子
- **THEN** 系统显示提示信息

### Requirement: 自动分配池子
系统 SHALL 提供命令自动分配一个空闲池子并切换到该池子账号。

#### Scenario: 成功自动分配
- **WHEN** 用户运行 claude-auto 用户名
- **THEN** 系统找到空闲池子、占用它、并自动切换到该池子账号

#### Scenario: 所有池子都被占用
- **WHEN** 用户运行 claude-auto 但所有池子都被占用
- **THEN** 系统显示错误消息和当前池子状态

#### Scenario: 退出时自动释放
- **WHEN** 用户通过 claude-auto 进入池子并退出
- **THEN** 系统自动释放该池子
