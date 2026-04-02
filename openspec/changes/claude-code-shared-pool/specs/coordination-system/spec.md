## ADDED Requirements

### Requirement: 池子状态管理
系统 SHALL 使用文件锁机制管理池子的占用和释放状态。

#### Scenario: 占用空闲池子
- **WHEN** 用户占用一个空闲池子
- **THEN** 系统创建状态文件记录用户信息和时间戳

#### Scenario: 尝试占用已被占用的池子
- **WHEN** 用户尝试占用已被占用的池子
- **THEN** 系统拒绝并显示当前占用者信息

#### Scenario: 释放池子
- **WHEN** 用户释放池子
- **THEN** 系统删除对应的状态文件

### Requirement: 状态文件格式
系统 SHALL 使用标准化的状态文件格式存储池子占用信息。

#### Scenario: 状态文件内容
- **WHEN** 池子被占用
- **THEN** 状态文件包含用户名和时间戳（格式：用户名 @ YYYY-MM-DD HH:MM:SS）

#### Scenario: 状态文件位置
- **WHEN** 系统管理池子状态
- **THEN** 状态文件存储在 /shared/claude-status/pool-N.lock

### Requirement: 并发安全
系统 SHALL 确保池子占用操作的原子性，避免竞态条件。

#### Scenario: 同时占用同一池子
- **WHEN** 两个用户同时尝试占用同一池子
- **THEN** 只有一个用户成功占用，另一个收到已被占用的提示

### Requirement: 使用日志记录
系统 SHALL 记录所有池子占用和释放操作的日志。

#### Scenario: 记录占用操作
- **WHEN** 用户占用池子
- **THEN** 系统在日志文件追加占用记录

#### Scenario: 记录释放操作
- **WHEN** 用户释放池子
- **THEN** 系统在日志文件追加释放记录

#### Scenario: 日志格式
- **WHEN** 系统记录日志
- **THEN** 日志包含时间戳、操作类型、池子编号和用户信息
