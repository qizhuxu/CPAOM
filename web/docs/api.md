# API 参考文档

CPA 账号管理系统 Web 版 REST API 接口文档。

## 认证

所有 API 端点都需要用户登录。使用 Flask-Login 进行会话管理。

### 登录
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**响应 (302 重定向)**
```http
Location: /
Set-Cookie: session=...
```

### 登出
```http
GET /auth/logout
```

## 服务器管理

### 获取服务器列表
```http
GET /api/servers/
```

**响应 (200 OK)**
```json
{
  "servers": [
    {
      "id": "abc123",
      "name": "主服务器",
      "base_url": "https://cpa.example.com",
      "token": "mgt-xxx",
      "enable_token_revive": true,
      "enabled": true
    }
  ]
}
```

### 添加服务器
```http
POST /api/servers/
Content-Type: application/json

{
  "name": "新服务器",
  "base_url": "https://cpa.example.com",
  "token": "mgt-xxx",
  "enable_token_revive": true
}
```

**响应 (200 OK)**
```json
{
  "success": true,
  "message": "服务器添加成功",
  "server_id": "def456"
}
```

### 测试服务器连接
```http
POST /api/servers/{server_id}/test
```

**响应 (200 OK)**
```json
{
  "success": true,
  "message": "连接成功",
  "file_count": 25
}
```

### 删除服务器
```http
DELETE /api/servers/{server_id}
```

## 账号管理

### 获取账号列表
```http
GET /api/accounts/{server_id}
```

**响应 (200 OK)**
```json
{
  "success": true,
  "accounts": [
    {
      "name": "user1@example.com.json",
      "email": "user1@example.com",
      "auth_index": "abc123",
      "disabled": false,
      "created_at": "2026-04-26T10:00:00Z"
    }
  ]
}
```

### 检查使用情况
```http
POST /api/accounts/{server_id}/check-usage
```

**响应 (200 OK)**
```json
{
  "success": true,
  "results": [
    {
      "email": "user1@example.com",
      "auth_index": "abc123",
      "status": "success",
      "usage": {
        "rate_limit": {
          "primary_window": {
            "used_percent": 45.2
          },
          "limit_reached": false
        }
      }
    }
  ],
  "total": 1
}
```

### 禁用账号
```http
POST /api/accounts/{server_id}/{filename}/disable
```

### 启用账号
```http
POST /api/accounts/{server_id}/{filename}/enable
```

## 批量操作

### 批量下载
```http
POST /api/operations/{server_id}/download
```

**响应 (200 OK)**
```json
{
  "success": true,
  "message": "下载完成",
  "filename": "20260426-25.zip",
  "count": 25
}
```

### 批量上传
```http
POST /api/operations/{server_id}/upload
Content-Type: multipart/form-data

file: [ZIP文件]
```

### 批量复活 Token
```http
POST /api/operations/{server_id}/revive
```

## 统计信息

### 仪表板统计
```http
GET /api/stats/dashboard
```

**响应 (200 OK)**
```json
{
  "success": true,
  "stats": {
    "total_servers": 2,
    "total_accounts": 50,
    "active_accounts": 45,
    "disabled_accounts": 5
  }
}
```

## 数据同步

### 同步认证文件
```http
POST /api/sync/{server_id}/auth-files
```

### 获取同步日志
```http
GET /api/sync/logs?limit=50
```

## 本地账号

### 获取本地账号统计
```http
GET /api/local-accounts/stats
```

### 获取本地账号列表
```http
GET /api/local-accounts/?server_id={server_id}&search={keyword}
```

### 删除本地账号
```http
DELETE /api/local-accounts/{account_id}
```

## 系统日志

### 实时日志流 (SSE)
```http
GET /api/logs/stream
Accept: text/event-stream
```

**响应 (200 OK)**
```
Content-Type: text/event-stream

data: {"timestamp":"2026-04-26 17:15:30","level":"INFO","name":"app","message":"用户登录成功"}

data: {"timestamp":"2026-04-26 17:15:31","level":"INFO","name":"servers","message":"服务器添加成功: 测试服务器"}
```

### 历史日志
```http
GET /api/logs/history?limit=100&level=ERROR
```

### 清空日志
```http
POST /api/logs/clear
```

## 错误响应

所有 API 在出错时返回统一格式：

```json
{
  "success": false,
  "error": "错误描述",
  "code": "ERROR_CODE"
}
```

### 常见错误码

- `400` - 请求参数错误
- `401` - 未登录或登录过期
- `403` - 权限不足
- `404` - 资源不存在
- `500` - 服务器内部错误

### 错误示例

**未登录 (401)**
```json
{
  "success": false,
  "error": "请先登录",
  "code": "UNAUTHORIZED"
}
```

**服务器不存在 (404)**
```json
{
  "success": false,
  "error": "服务器不存在",
  "code": "SERVER_NOT_FOUND"
}
```

## 速率限制

- 登录接口：每分钟 5 次尝试
- 其他接口：每分钟 100 次请求
- 批量操作：每分钟 10 次请求

超出限制返回 `429 Too Many Requests`。

## 数据格式

### 时间格式
所有时间使用 ISO 8601 格式：`2026-04-26T17:15:30Z`

### 文件名格式
- 认证文件：`email@domain.com.json`
- 下载包：`YYYYMMDD-count.zip`
- 日志文件：`cpa-logs-YYYY-MM-DD-HH-MM-SS.txt`

### 服务器 ID
8 位随机字符串，如：`abc12345`

### 账号 Auth Index
CPA 服务器返回的唯一标识符，用于 API 调用。