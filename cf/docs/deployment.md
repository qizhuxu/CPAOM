# 部署指南

## 快速开始

### 1. 前置要求

- Node.js 16.13.0 或更高版本
- npm 或 yarn
- Cloudflare 账号

### 2. 安装 Wrangler CLI

```bash
npm install -g wrangler

# 或使用 npx（推荐）
npx wrangler --version
```

### 3. 登录 Cloudflare

```bash
wrangler login
```

这会打开浏览器，登录你的 Cloudflare 账号并授权。

## 详细部署步骤

### 步骤 1：克隆并安装

```bash
cd L/CPAD/cf
npm install
```

### 步骤 2：创建 KV 命名空间

```bash
# 创建生产环境 KV
wrangler kv:namespace create "ACCOUNTS"

# 输出示例：
# 🌀 Creating namespace with title "cpa-manager-ACCOUNTS"
# ✨ Success!
# Add the following to your configuration file in your kv_namespaces array:
# { binding = "ACCOUNTS", id = "abc123..." }
```

复制输出的 ID，更新 `wrangler.toml`：

```toml
[[kv_namespaces]]
binding = "ACCOUNTS"
id = "abc123..."  # 替换为你的 ID
```

### 步骤 3：配置环境变量

#### 方法 1：使用 Secret（推荐）

```bash
# 设置管理员用户名
wrangler secret put ADMIN_USERNAME
# 提示输入时输入: admin

# 设置管理员密码
wrangler secret put ADMIN_PASSWORD
# 提示输入时输入: your-secure-password
```

#### 方法 2：使用 .dev.vars（仅本地开发）

创建 `.dev.vars` 文件：

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password
```

**注意**：`.dev.vars` 仅用于本地开发，不会部署到生产环境。

### 步骤 4：本地测试

```bash
npm run dev
```

访问 `http://localhost:8787`，测试功能：

1. 登录（使用配置的用户名密码）
2. 添加一个测试服务器
3. 测试连接
4. 查看账号列表

### 步骤 5：部署到生产环境

```bash
npm run deploy
```

部署成功后，你会看到：

```
✨ Success! Uploaded 1 files (x.xx sec)
Published cpa-manager (x.xx sec)
  https://cpa-manager.your-subdomain.workers.dev
```

### 步骤 6：验证部署

访问部署的 URL，确认：

- ✅ 可以正常访问登录页面
- ✅ 可以成功登录
- ✅ 可以添加服务器
- ✅ 可以查看账号列表

## 高级配置

### 自定义域名

1. 在 Cloudflare Dashboard 中进入 Workers & Pages
2. 选择你的 Worker
3. 点击 "Triggers" 标签
4. 点击 "Add Custom Domain"
5. 输入你的域名（例如：`cpa.yourdomain.com`）
6. 等待 DNS 配置生效

或者在 `wrangler.toml` 中配置：

```toml
routes = [
  { pattern = "cpa.yourdomain.com", zone_name = "yourdomain.com" }
]
```

### 多环境部署

#### 开发环境

```bash
wrangler deploy --env dev
```

#### 生产环境

```bash
wrangler deploy --env production
```

配置示例（`wrangler.toml`）：

```toml
[env.dev]
name = "cpa-manager-dev"
vars = { ENVIRONMENT = "development" }

[env.production]
name = "cpa-manager"
vars = { ENVIRONMENT = "production" }
```

### 使用 D1 数据库（可选）

如果需要使用 D1 数据库存储操作日志：

```bash
# 创建数据库
wrangler d1 create cpa-manager-db

# 更新 wrangler.toml 中的 database_id

# 创建迁移
wrangler d1 migrations create cpa-manager-db create_logs_table

# 应用迁移
wrangler d1 migrations apply cpa-manager-db --remote
```

## 监控和日志

### 查看实时日志

```bash
npm run tail

# 或指定环境
wrangler tail --env production
```

### 查看 Cloudflare Dashboard

1. 登录 Cloudflare Dashboard
2. 进入 Workers & Pages
3. 选择你的 Worker
4. 查看：
   - 请求统计
   - 错误日志
   - 性能指标

## 故障排查

### 问题 1：KV 命名空间未找到

**错误**：`Error: KV namespace not found`

**解决**：
1. 确认已创建 KV 命名空间
2. 检查 `wrangler.toml` 中的 ID 是否正确
3. 重新部署：`npm run deploy`

### 问题 2：认证失败

**错误**：`401 Unauthorized`

**解决**：
1. 确认已设置 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD`
2. 检查 Secret 是否正确：`wrangler secret list`
3. 重新设置 Secret：`wrangler secret put ADMIN_PASSWORD`

### 问题 3：CORS 错误

**错误**：`CORS policy: No 'Access-Control-Allow-Origin' header`

**解决**：
1. 检查 `src/utils/cors.js` 配置
2. 确认 API 响应包含 CORS 头
3. 如果使用自定义域名，更新 CORS 配置

### 问题 4：部署失败

**错误**：`Error: Failed to publish`

**解决**：
1. 确认已登录：`wrangler whoami`
2. 检查网络连接
3. 查看详细错误：`wrangler deploy --verbose`
4. 尝试重新登录：`wrangler logout && wrangler login`

## 性能优化

### 1. 启用缓存

在 `wrangler.toml` 中配置：

```toml
[build]
command = ""

[site]
bucket = ""
```

### 2. 优化 KV 读取

- 使用 `cacheTtl` 参数缓存 KV 读取
- 批量操作时使用并发请求

### 3. 减少 API 调用

- 在前端缓存服务器列表
- 使用 WebSocket 实现实时更新（可选）

## 安全加固

### 1. 限制访问

使用 Cloudflare Access：

```bash
# 在 Cloudflare Dashboard 中配置 Access 策略
# 限制只有特定 IP 或邮箱可以访问
```

### 2. 启用 WAF

在 Cloudflare Dashboard 中：
1. 进入 Security > WAF
2. 启用 Managed Rules
3. 配置自定义规则

### 3. 速率限制

在 `wrangler.toml` 中配置：

```toml
[limits]
cpu_ms = 50
```

或使用 Cloudflare Rate Limiting 规则。

## 备份和恢复

### 备份 KV 数据

```bash
# 导出服务器配置
wrangler kv:key get --binding=ACCOUNTS "cpa_servers" > backup-servers.json

# 导出所有 keys
wrangler kv:key list --binding=ACCOUNTS > backup-keys.json
```

### 恢复数据

```bash
# 导入服务器配置
wrangler kv:key put --binding=ACCOUNTS "cpa_servers" --path=backup-servers.json
```

## 更新和维护

### 更新依赖

```bash
npm update
npm audit fix
```

### 更新 Wrangler

```bash
npm install -g wrangler@latest
```

### 回滚部署

```bash
# 查看部署历史
wrangler deployments list

# 回滚到指定版本
wrangler rollback [deployment-id]
```

## 成本估算

Cloudflare Workers 免费套餐：
- ✅ 100,000 请求/天
- ✅ 10ms CPU 时间/请求
- ✅ 1GB KV 存储
- ✅ 1,000 KV 写入/天
- ✅ 100,000 KV 读取/天

付费套餐（$5/月）：
- ✅ 10,000,000 请求/月
- ✅ 50ms CPU 时间/请求
- ✅ 无限 KV 存储
- ✅ 无限 KV 操作

**预估**：对于中小规模使用（<100 个账号），免费套餐足够。

## 下一步

- [ ] 配置自定义域名
- [ ] 启用 Cloudflare Access
- [ ] 设置监控告警
- [ ] 定期备份 KV 数据
- [ ] 优化前端性能

## 支持

如有问题，请：
1. 查看 [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
2. 查看 [Wrangler 文档](https://developers.cloudflare.com/workers/wrangler/)
3. 提交 Issue

---

**祝部署顺利！** 🚀
