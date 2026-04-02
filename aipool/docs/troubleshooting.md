# 故障排查指南

## 常见问题

### SSH 连接失败

**症状**：`❌ 错误 [E002]: SSH 连接失败`

**排查步骤**：
1. 测试手动 SSH 连接：`ssh admin@192.168.1.10`
2. 检查 SSH 密钥：`ssh-copy-id admin@192.168.1.10`
3. 检查防火墙：`telnet 192.168.1.10 22`
4. 检查 inventory.yaml 中的 host/user/port 是否正确

### 前置检查失败

**症状**：`❌ 错误 [E003]: 前置检查失败`

**磁盘空间不足**：
```bash
# 在服务器上检查
df -h /
# 清理空间
sudo apt-get clean
sudo journalctl --vacuum-size=1G
```

**操作系统不支持**：
- 当前仅支持 Linux 服务器
- 检查 adapter.yaml 中的 `check_os.allowed` 配置

### 部署步骤失败

**症状**：`❌ 错误 [E004]: 部署步骤失败`

1. 查看详细日志：`.aipool/logs/<server>-<timestamp>.log`
2. 手动 SSH 到服务器排查
3. 修复问题后运行 `/aipool:deploy <server>` 断点续传

### 手动步骤验证失败

**症状**：`⚠ 验证失败: ...`

对于 Claude Code 认证：
1. 确认已在池子账号下完成 `claude auth login`
2. 测试认证：`sudo su - claude-pool-1 -c 'claude "test"'`
3. 如果认证过期，重新运行 `claude auth login`

### 漂移检测误报

**症状**：`/aipool:status` 显示漂移，但文件实际未变

可能原因：
- 文件权限变化（不影响内容但影响 hash）
- 文件被系统更新

解决方法：
```
/aipool:sync <server>
```
重新同步并更新 hash 记录。

### 状态文件损坏

**症状**：JSON 解析错误

恢复方法：
1. 查看备份：`.aipool/backups/<server>-*.json`
2. 手动恢复：`cp .aipool/backups/<server>-<timestamp>.json .aipool/state/<server>.json`
3. 或重新部署：删除状态文件后运行 `/aipool:deploy <server>`

## 日志位置

- 操作日志：`.aipool/logs/<server>-<timestamp>.log`
- 状态文件：`.aipool/state/<server>.json`
- 状态备份：`.aipool/backups/<server>-<timestamp>.json`

## 获取帮助

如果以上方法无法解决问题：
1. 查看完整日志文件
2. 检查服务器系统日志：`sudo journalctl -xe`
3. 在项目 Issues 中提交问题，附上日志内容
