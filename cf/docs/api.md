# API 参考

所有 API 请求（除登录外）都需要在 Header 中携带 Token：

```
Authorization: Bearer <your-token>
```

## 认证 API

### POST /api/auth/login

用户登录，获取访问 Token。

**请求体:**
```json
{
  "username": "admin",
  "password": "your-password"
}
```

**响应 (200 OK):**
```json
{
  "success": true,
  "token": "uuid-token",
  "user": {
    "username": "admin"
  }
}
```

**错误响应:**
- `401` - 用户名或密码错误

### POST /api/auth/logout

登出当前用户。

**响应 (200 OK):**
```json
{
  "success": true
}
```

### GET /api/auth/me

获取当前登录用户信息。

**响应 (200 OK):**
```json
{
  "user": {
    "username": "admin",
    "loginAt": 1234567890
  }
}
```

## 服务器管理 API

### GET /api/servers

获取所有 CPA 服务器列表。

**响应 (200 OK):**
```json
{
  "success": true,
  "servers": [
    {
      "id": "uuid",
      "name": "主服务器",
      "base_url": "https://example.com",
      "token": "mgt-xxx",
      "enable_token_revive": true,
      "created_at": 1234567890
    }
  ]
}
```

### POST /api/servers

添加新的 CPA 服务器。

**请求体:**
```json
{
  "name": "主服务器",
  "base_url": "https://example.com",
  "token": "mgt-xxx",
  "enable_token_revive": true
}
```

**响应 (200 OK):**
```json
{
  "success": true,
  "server": {
    "id": "uuid",
    "name": "主服务器",
    ...
  }
}
```

### PUT /api/servers/:id

更新服务器配置。

**请求体:**
```json
{
  "name": "新名称",
  "base_url": "https://new-url.com"
}
```

### DELETE /api/servers/:id

删除服务器。

**响应 (200 OK):**
```json
{
  "success": true
}
```

### POST /api/servers/:id/test

测试服务器连接。

**响应 (200 OK):**
```json
{
  "success": true,
  "status": "connected",
  "accounts_count": 150
}
```

## 账号管理 API

### GET /api/accounts?server_id=xxx

获取指定服务器的所有账号。

**查询参数:**
- `server_id` (必需) - 服务器 ID

**响应 (200 OK):**
```json
{
  "success": true,
  "accounts": [
    {
      "id": "codex-account-123",
      "name": "codex-account-123.json",
      "email": "user@example.com",
      "status": "ready",
      "disabled": false,
      "auth_index": "123",
      "last_refresh": "2025-08-31T01:23:45Z"
    }
  ],
  "total": 150
}
```

### GET /api/accounts/:filename?server_id=xxx

获取单个账号的详细信息。

**查询参数:**
- `server_id` (必需) - 服务器 ID

**响应 (200 OK):**
```json
{
  "success": true,
  "account": {
    "email": "user@example.com",
    "access_token": "eyJhbG...",
    "refresh_token": "ey...",
    ...
  }
}
```

### POST /api/accounts/upload

上传账号文件。

**请求体:**
```json
{
  "server_id": "uuid",
  "filename": "account.json",
  "auth_data": {
    "email": "user@example.com",
    "access_token": "...",
    "refresh_token": "..."
  }
}
```

### DELETE /api/accounts/:filename?server_id=xxx

删除账号。

**查询参数:**
- `server_id` (必需) - 服务器 ID

### PATCH /api/accounts/:filename/status

更新账号状态（启用/禁用）。

**请求体:**
```json
{
  "server_id": "uuid",
  "disabled": true
}
```

## 批量操作 API

### POST /api/operations/check-usage

批量检查账号使用情况。

**请求体:**
```json
{
  "server_id": "uuid"
}
```

**响应 (200 OK):**
```json
{
  "success": true,
  "summary": {
    "total": 150,
    "checked": 145,
    "success": 140,
    "error": 5,
    "disabled": 5
  },
  "results": [
    {
      "filename": "account.json",
      "email": "user@example.com",
      "status": "success",
      "usage": {...}
    }
  ]
}
```

### POST /api/operations/revive-tokens

批量复活过期的 Token。

**请求体:**
```json
{
  "server_id": "uuid",
  "filenames": ["account1.json", "account2.json"]
}
```

**响应 (200 OK):**
```json
{
  "success": true,
  "summary": {
    "total": 2,
    "success": 1,
    "failed": 1
  },
  "results": [
    {
      "filename": "account1.json",
      "status": "success",
      "attempts": 1
    },
    {
      "filename": "account2.json",
      "status": "failed",
      "error": "Refresh token expired",
      "disabled": true
    }
  ]
}
```

### POST /api/operations/download-pack

下载并打包所有活跃账号。

**请求体:**
```json
{
  "server_id": "uuid"
}
```

**响应 (200 OK):**
```json
{
  "success": true,
  "pack_id": "uuid",
  "download_url": "/api/operations/download-pack/uuid",
  "count": 145,
  "expires_in": 3600
}
```

### POST /api/operations/batch-upload

批量上传账号。

**请求体:**
```json
{
  "server_id": "uuid",
  "accounts": [
    {
      "filename": "account1.json",
      "data": {...}
    }
  ]
}
```

## 统计 API

### GET /api/stats/overview

获取总览统计。

**响应 (200 OK):**
```json
{
  "success": true,
  "overview": {
    "total_servers": 2,
    "total_accounts": 300,
    "total_active": 280,
    "total_disabled": 15,
    "total_error": 5
  },
  "servers": [
    {
      "server_id": "uuid",
      "server_name": "主服务器",
      "total": 150,
      "active": 140,
      "disabled": 8,
      "error": 2,
      "status": "online"
    }
  ]
}
```

### GET /api/stats/server/:id

获取单个服务器的详细统计。

**响应 (200 OK):**
```json
{
  "success": true,
  "server": {
    "id": "uuid",
    "name": "主服务器",
    "base_url": "https://example.com"
  },
  "stats": {
    "total": 150,
    "active": 140,
    "disabled": 8,
    "error": 2,
    "ready": 140,
    "by_status": {
      "ready": 140,
      "error": 2
    }
  }
}
```

## 错误响应

所有 API 在出错时返回统一格式：

```json
{
  "error": "错误描述",
  "message": "详细错误信息"
}
```

**常见错误码:**
- `400` - 请求参数错误
- `401` - 未授权（Token 无效或过期）
- `404` - 资源不存在
- `500` - 服务器内部错误

## 速率限制

目前没有实施速率限制，但建议：
- 批量操作使用适当的间隔
- 避免在短时间内大量请求

## 认证流程

1. 调用 `POST /api/auth/login` 获取 Token
2. 在后续请求的 Header 中携带 Token
3. Token 有效期 24 小时
4. Token 过期后需要重新登录

## 示例：完整工作流

```javascript
// 1. 登录
const loginRes = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'password'
  })
});
const { token } = await loginRes.json();

// 2. 获取服务器列表
const serversRes = await fetch('/api/servers', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { servers } = await serversRes.json();

// 3. 获取账号列表
const accountsRes = await fetch(`/api/accounts?server_id=${servers[0].id}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { accounts } = await accountsRes.json();

// 4. 批量检查使用情况
const checkRes = await fetch('/api/operations/check-usage', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    server_id: servers[0].id
  })
});
const { summary, results } = await checkRes.json();
```

## 相关文档

- [快速开始](quickstart.md) - 部署和首次使用
- [架构设计](architecture.md) - API 实现细节
- [开发指南](development.md) - 本地开发和测试
