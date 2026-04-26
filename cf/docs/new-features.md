# 🎉 新功能：数据同步备份 + 定时自动维护

## ✨ 新增功能概述

### 1. 数据同步备份 💾
将 CPA 服务器的数据自动同步到 Cloudflare D1 数据库，实现数据持久化和版本管理。

**核心特性：**
- ✅ 认证文件自动备份
- ✅ Config.yaml 配置备份
- ✅ 版本历史管理
- ✅ 一键恢复功能
- ✅ 自动去重（相同内容不重复备份）

### 2. 定时自动维护 ⏰
支持配置定时任务，自动执行维护操作，无需人工干预。

**核心特性：**
- ✅ 定时同步数据
- ✅ 定时检查账号
- ✅ 定时复活 Token
- ✅ Cron 表达式配置
- ✅ 任务执行历史

## 📊 数据库设计

### 新增 8 张表

1. **auth_files_backup** - 认证文件备份
2. **config_backups** - 配置文件备份
3. **sync_logs** - 同步日志
4. **scheduled_tasks** - 定时任务配置
5. **task_executions** - 任务执行历史
6. **audit_logs** - 操作审计日志
7. **system_stats** - 系统统计
8. **索引** - 查询优化索引

## 🔄 同步功能

### 同步认证文件
```bash
POST /api/sync/auth-files
{
  "server_id": "uuid",
  "only_active": true  # 只同步活跃账号
}
```

**功能：**
- 从 CPA 服务器下载所有认证文件
- 批量保存到 D1 数据库
- 记录同步日志
- 支持增量同步

### 同步配置文件
```bash
POST /api/sync/config
{
  "server_id": "uuid"
}
```

**功能：**
- 下载 config.yaml 配置
- 计算 SHA-256 哈希
- 自动去重（相同内容不重复保存）
- 保留历史版本

### 完整同步
```bash
POST /api/sync/full
{
  "server_id": "uuid",
  "only_active": true
}
```

**功能：**
- 同时同步认证文件和配置
- 一次性完成所有备份
- 返回详细执行结果

## 📥 备份查询

### 查看认证文件备份
```bash
GET /api/sync/backups/auth-files?server_id=uuid&limit=100
```

**返回：**
- 所有备份的认证文件
- 包含完整的 auth_data
- 支持按状态过滤

### 查看配置备份历史
```bash
GET /api/sync/backups/config?server_id=uuid&limit=10
```

**返回：**
- 配置文件历史版本
- 每个版本的哈希值
- 备份时间

### 查看同步日志
```bash
GET /api/sync/logs?server_id=uuid&limit=50
```

**返回：**
- 同步操作历史
- 成功/失败统计
- 执行时间

## 🔄 数据恢复

### 恢复认证文件
```bash
POST /api/sync/restore/auth-file
{
  "server_id": "uuid",
  "filename": "account.json"
}
```

**功能：**
- 从 D1 备份恢复
- 自动上传到 CPA 服务器
- 支持误删除恢复

## ⏰ 定时任务

### 创建定时任务
```bash
POST /api/scheduled/tasks
{
  "name": "每小时同步认证文件",
  "type": "sync_auth",
  "enabled": true,
  "cron_expression": "0 * * * *",
  "server_ids": ["uuid1", "uuid2"]
}
```

**任务类型：**
- `sync_auth` - 同步认证文件
- `sync_config` - 同步配置文件
- `check_usage` - 检查使用情况
- `revive_tokens` - 复活 Token

### 管理定时任务
```bash
# 获取所有任务
GET /api/scheduled/tasks

# 更新任务
PUT /api/scheduled/tasks/:id
{
  "enabled": false,
  "cron_expression": "0 */2 * * *"
}

# 删除任务
DELETE /api/scheduled/tasks/:id

# 手动执行
POST /api/scheduled/tasks/:id/run
```

### 查看执行历史
```bash
GET /api/scheduled/executions?task_id=1&limit=50
```

**返回：**
- 任务执行记录
- 执行结果
- 执行时间
- 错误信息（如果失败）

## 📅 Cron 表达式

### 常用示例

| 表达式 | 说明 | 使用场景 |
|--------|------|----------|
| `0 * * * *` | 每小时 | 频繁维护 |
| `0 */2 * * *` | 每2小时 | 常规维护 |
| `0 */6 * * *` | 每6小时 | 定期检查 |
| `0 2 * * *` | 每天凌晨2点 | 每日备份 |
| `*/15 * * * *` | 每15分钟 | 实时监控 |
| `*/30 * * * *` | 每30分钟 | 高频检查 |

## 🎯 典型使用场景

### 场景 1：每日自动备份
**需求**：每天凌晨 2 点自动备份所有服务器数据

**配置：**
```json
{
  "name": "每日自动备份",
  "type": "sync_auth",
  "enabled": true,
  "cron_expression": "0 2 * * *",
  "server_ids": null  // 所有服务器
}
```

### 场景 2：每小时自动维护
**需求**：每小时检查账号并自动复活过期 Token

**配置：**
```json
{
  "name": "每小时自动维护",
  "type": "revive_tokens",
  "enabled": true,
  "cron_expression": "0 * * * *",
  "server_ids": null
}
```

### 场景 3：配置监控
**需求**：每6小时备份配置，监控配置变化

**配置：**
```json
{
  "name": "配置监控",
  "type": "sync_config",
  "enabled": true,
  "cron_expression": "0 */6 * * *",
  "server_ids": ["uuid1"]
}
```

### 场景 4：数据恢复
**需求**：误删除账号后从备份恢复

**步骤：**
1. 查看备份：`GET /api/sync/backups/auth-files?server_id=uuid`
2. 找到需要恢复的文件
3. 恢复：`POST /api/sync/restore/auth-file`

## 🚀 部署步骤

### 1. 创建 D1 数据库
```bash
wrangler d1 create cpa-manager-db
```

复制输出的 `database_id`，更新 `wrangler.toml`：
```toml
[[d1_databases]]
binding = "DB"
database_name = "cpa-manager-db"
database_id = "your-database-id"  # 替换这里
```

### 2. 运行数据库迁移
```bash
# 本地测试
wrangler d1 migrations apply cpa-manager-db --local

# 生产环境
wrangler d1 migrations apply cpa-manager-db --remote
```

### 3. 部署 Worker
```bash
npm run deploy
```

### 4. 验证功能
```bash
# 测试同步
curl -X POST https://your-worker.workers.dev/api/sync/auth-files \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"server_id":"uuid","only_active":true}'

# 查看备份
curl https://your-worker.workers.dev/api/sync/backups/auth-files?server_id=uuid \
  -H "Authorization: Bearer your-token"
```

## 💡 最佳实践

### 1. 备份策略
- **频率**：每天至少备份一次
- **时间**：选择服务器负载低的时间（凌晨）
- **范围**：只备份活跃账号可减少存储

### 2. 定时任务配置
- **避免冲突**：不同任务错开执行时间
- **合理频率**：根据实际需求设置
- **监控执行**：定期查看执行历史

### 3. 数据清理
- **定期清理**：删除 90 天前的旧日志
- **保留策略**：每个服务器保留最新 10 个配置备份
- **存储优化**：只备份必要的数据

### 4. 故障恢复
- **定期测试**：定期测试恢复流程
- **多重备份**：重要数据考虑额外备份
- **监控告警**：同步失败时及时通知

## 📊 性能影响

### D1 数据库
- **免费套餐**：5GB 存储，500万行读取/天
- **预估**：100 个账号 ≈ 1MB，可存储 5000+ 个账号
- **查询性能**：平均 <10ms

### Worker 执行时间
- **同步 100 个账号**：约 5-10 秒
- **同步配置**：约 1-2 秒
- **查询备份**：约 100-500ms

### 成本估算
- **D1 免费套餐**：完全够用
- **Worker 时间**：同步操作会消耗更多 CPU 时间
- **建议**：使用付费套餐（$5/月）以获得更多 CPU 时间

## 🔧 故障排查

### 同步失败
1. 查看同步日志：`GET /api/sync/logs`
2. 检查服务器连接
3. 查看错误信息
4. 手动重试

### 定时任务不执行
1. 检查任务状态（enabled = true）
2. 验证 Cron 表达式
3. 查看执行历史
4. 手动执行测试

### 数据库错误
1. 确认数据库已创建
2. 检查迁移是否已应用
3. 查看 Worker 日志
4. 验证 wrangler.toml 配置

## 📚 相关文档

- **[数据同步与备份](docs/sync-and-backup.md)** - 完整功能文档
- **[API 参考](docs/api.md)** - API 接口文档
- **[部署指南](docs/deployment.md)** - 部署步骤
- **[架构设计](docs/architecture.md)** - 数据库设计

## 🎉 总结

新增的数据同步备份和定时自动维护功能，让 CPA 账号管理系统更加完善：

✅ **数据安全** - 自动备份到 D1 数据库
✅ **版本管理** - 保留历史版本，支持恢复
✅ **自动维护** - 定时任务自动执行
✅ **操作审计** - 完整的操作日志
✅ **灵活配置** - Cron 表达式自定义时间

---

**版本**: v1.1.0  
**发布日期**: 2026-04-25  
**新增文件**: 5 个（数据库迁移、API、工具类、文档）
