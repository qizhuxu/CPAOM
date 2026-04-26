# 数据同步与备份

本文档说明如何使用数据同步备份和定时自动维护功能。

## 🎯 功能概述

### 数据同步备份
- **认证文件备份** - 将 CPA 服务器的认证文件同步到 D1 数据库
- **配置文件备份** - 备份 config.yaml 配置文件
- **版本历史** - 保留历史版本，支持恢复
- **自动去重** - 相同内容不重复备份

### 定时自动维护
- **定时同步** - 按计划自动同步数据
- **定时检查** - 自动检查账号使用情况
- **定时复活** - 自动复活过期 Token
- **灵活配置** - 支持 Cron 表达式自定义时间

## 📊 数据库表结构

### auth_files_backup
存储认证文件备份

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| server_id | TEXT | 服务器 ID |
| filename | TEXT | 文件名 |
| email | TEXT | 账号邮箱 |
| auth_data | TEXT | 完整认证数据（JSON） |
| status | TEXT | 状态（active/disabled/error） |
| backup_time | TEXT | 备份时间 |

### config_backups
存储配置文件备份

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| server_id | TEXT | 服务器 ID |
| config_content | TEXT | YAML 内容 |
| config_hash | TEXT | SHA-256 哈希 |
| backup_time | TEXT | 备份时间 |

### scheduled_tasks
定时任务配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_name | TEXT | 任务名称 |
| task_type | TEXT | 任务类型 |
| enabled | INTEGER | 是否启用 |
| cron_expression | TEXT | Cron 表达式 |
| last_run | TEXT | 最后执行时间 |
| next_run | TEXT | 下次执行时间 |

## 🔄 同步 API

### POST /api/sync/auth-files
同步认证文件到 D1

**请求体:**
```json
{
  "server_id": "uuid",
  "only_active": true  // 只同步活跃账号
}
```

**响应:**
```json
{
  "success": true,
  "synced": 150,
  "total": 150,
  "duration_ms": 5000
}
```

### POST /api/sync/config
同步配置文件到 D1

**请求体:**
```json
{
  "server_id": "uuid"
}
```

**响应:**
```json
{
  "success": true,
  "hash": "abc123...",
  "duplicate": false,
  "size": 12345,
  "duration_ms": 1000
}
```

### POST /api/sync/full
完整同步（认证文件 + 配置）

**请求体:**
```json
{
  "server_id": "uuid",
  "only_active": true
}
```

**响应:**
```json
{
  "success": true,
  "status": "success",
  "results": {
    "auth_files": {
      "success": true,
      "synced": 150,
      "total": 150
    },
    "config": {
      "success": true,
      "hash": "abc123..."
    }
  },
  "duration_ms": 6000
}
```

### GET /api/sync/backups/auth-files
获取认证文件备份

**查询参数:**
- `server_id` (必需) - 服务器 ID
- `status` (可选) - 过滤状态
- `disabled` (可选) - 过滤禁用状态
- `limit` (可选) - 限制数量，默认 100

**响应:**
```json
{
  "success": true,
  "backups": [
    {
      "id": 1,
      "server_id": "uuid",
      "filename": "account.json",
      "email": "user@example.com",
      "auth_data": {...},
      "status": "active",
      "backup_time": "2026-04-25T10:00:00Z"
    }
  ],
  "total": 150
}
```

### GET /api/sync/backups/config
获取配置备份历史

**查询参数:**
- `server_id` (必需) - 服务器 ID
- `limit` (可选) - 限制数量，默认 10

**响应:**
```json
{
  "success": true,
  "backups": [
    {
      "id": 1,
      "server_id": "uuid",
      "config_content": "...",
      "config_hash": "abc123...",
      "backup_time": "2026-04-25T10:00:00Z"
    }
  ],
  "total": 5
}
```

### GET /api/sync/logs
获取同步日志

**查询参数:**
- `server_id` (可选) - 过滤服务器
- `limit` (可选) - 限制数量，默认 50

**响应:**
```json
{
  "success": true,
  "logs": [
    {
      "id": 1,
      "server_id": "uuid",
      "sync_type": "auth_files",
      "status": "success",
      "files_synced": 150,
      "files_failed": 0,
      "duration_ms": 5000,
      "created_at": "2026-04-25T10:00:00Z"
    }
  ],
  "total": 20
}
```

### POST /api/sync/restore/auth-file
从备份恢复认证文件

**请求体:**
```json
{
  "server_id": "uuid",
  "filename": "account.json"
}
```

**响应:**
```json
{
  "success": true,
  "message": "Auth file restored successfully",
  "filename": "account.json"
}
```

## ⏰ 定时任务 API

### GET /api/scheduled/tasks
获取所有定时任务

**响应:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": 1,
      "task_name": "每小时同步认证文件",
      "task_type": "sync_auth",
      "enabled": true,
      "cron_expression": "0 * * * *",
      "server_ids": ["uuid1", "uuid2"],
      "last_run": "2026-04-25T10:00:00Z",
      "next_run": "2026-04-25T11:00:00Z",
      "run_count": 100
    }
  ]
}
```

### POST /api/scheduled/tasks
创建定时任务

**请求体:**
```json
{
  "name": "每小时同步认证文件",
  "type": "sync_auth",
  "enabled": true,
  "cron_expression": "0 * * * *",
  "server_ids": ["uuid1", "uuid2"]  // null 表示所有服务器
}
```

**任务类型:**
- `sync_auth` - 同步认证文件
- `sync_config` - 同步配置文件
- `check_usage` - 检查使用情况
- `revive_tokens` - 复活 Token

### PUT /api/scheduled/tasks/:id
更新定时任务

**请求体:**
```json
{
  "task_name": "新名称",
  "enabled": false,
  "cron_expression": "0 */2 * * *"
}
```

### DELETE /api/scheduled/tasks/:id
删除定时任务

### POST /api/scheduled/tasks/:id/run
手动执行任务

**响应:**
```json
{
  "success": true,
  "message": "Task execution started"
}
```

### GET /api/scheduled/executions
获取任务执行历史

**查询参数:**
- `task_id` (可选) - 过滤任务
- `limit` (可选) - 限制数量，默认 50

**响应:**
```json
{
  "success": true,
  "executions": [
    {
      "id": 1,
      "task_id": 1,
      "task_name": "每小时同步认证文件",
      "status": "success",
      "result": {...},
      "started_at": "2026-04-25T10:00:00Z",
      "completed_at": "2026-04-25T10:05:00Z",
      "duration_ms": 300000
    }
  ]
}
```

## 📅 Cron 表达式

### 格式
```
分 时 日 月 周
```

### 常用示例

| 表达式 | 说明 |
|--------|------|
| `0 * * * *` | 每小时执行 |
| `0 */2 * * *` | 每2小时执行 |
| `0 */6 * * *` | 每6小时执行 |
| `0 2 * * *` | 每天凌晨2点执行 |
| `0 0 * * *` | 每天午夜执行 |
| `*/15 * * * *` | 每15分钟执行 |
| `*/30 * * * *` | 每30分钟执行 |

### 字段说明

- **分钟** (0-59)
- **小时** (0-23)
- **日** (1-31)
- **月** (1-12)
- **周** (0-6, 0=周日)

特殊字符：
- `*` - 任意值
- `*/n` - 每 n 个单位
- `n` - 具体值

## 🎯 使用场景

### 场景 1：定时备份
每天凌晨 2 点自动备份所有服务器的数据

```json
{
  "name": "每日自动备份",
  "type": "sync_auth",
  "enabled": true,
  "cron_expression": "0 2 * * *",
  "server_ids": null
}
```

### 场景 2：定时维护
每小时检查账号并自动复活过期 Token

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
每6小时备份配置文件，监控配置变化

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
从备份恢复误删除的认证文件

```bash
# 1. 查看备份
GET /api/sync/backups/auth-files?server_id=uuid

# 2. 恢复文件
POST /api/sync/restore/auth-file
{
  "server_id": "uuid",
  "filename": "account.json"
}
```

## 💡 最佳实践

### 1. 备份策略
- **频率**：每天至少备份一次
- **时间**：选择服务器负载低的时间（如凌晨）
- **范围**：只备份活跃账号可减少存储

### 2. 定时任务配置
- **避免冲突**：不同任务错开执行时间
- **合理频率**：根据实际需求设置，避免过于频繁
- **监控执行**：定期查看执行历史，确保任务正常

### 3. 数据清理
- **定期清理**：删除 90 天前的旧日志
- **保留策略**：每个服务器保留最新 10 个配置备份
- **存储优化**：只备份必要的数据

### 4. 故障恢复
- **定期测试**：定期测试恢复流程
- **多重备份**：重要数据考虑额外备份
- **监控告警**：同步失败时及时通知

## 🔧 故障排查

### 同步失败
**问题**：同步任务失败

**排查步骤**：
1. 查看同步日志：`GET /api/sync/logs`
2. 检查服务器连接：测试服务器连接
3. 查看错误信息：检查 error_message 字段
4. 手动重试：调用同步 API 手动执行

### 定时任务不执行
**问题**：定时任务没有按时执行

**排查步骤**：
1. 检查任务状态：确认 enabled = true
2. 验证 Cron 表达式：确保格式正确
3. 查看执行历史：`GET /api/scheduled/executions`
4. 手动执行测试：`POST /api/scheduled/tasks/:id/run`

### 数据库错误
**问题**：D1 数据库操作失败

**排查步骤**：
1. 确认数据库已创建
2. 检查迁移是否已应用
3. 查看 Worker 日志：`wrangler tail`
4. 验证 wrangler.toml 配置

## 📊 监控指标

### 关键指标
- **同步成功率** - 成功同步次数 / 总同步次数
- **备份数据量** - 备份的认证文件数量
- **任务执行率** - 按时执行的任务比例
- **平均执行时间** - 任务平均耗时

### 查看方式
```bash
# 查看同步日志
GET /api/sync/logs?limit=100

# 查看任务执行历史
GET /api/scheduled/executions?limit=100

# 查看备份统计
SELECT COUNT(*) FROM auth_files_backup WHERE server_id = 'uuid';
```

## 相关文档

- [API 参考](api.md) - 完整 API 文档
- [架构设计](architecture.md) - 数据库设计
- [部署指南](deployment.md) - D1 数据库配置
