# 快速开始

5 分钟部署 CPA 账号管理系统到 Cloudflare。

## 前置要求

- Node.js 16.13.0+
- Cloudflare 账号（免费）
- CPA 服务器地址和管理 Token

## 部署方式

### 方式 1：GitHub Actions 自动部署（推荐）

**适合场景**：团队协作、持续部署、自动化运维

**步骤：**

1. **Fork 仓库到 GitHub**

2. **配置 GitHub Secrets**（Settings → Secrets and variables → Actions）：
   ```
   CLOUDFLARE_API_TOKEN      # Cloudflare API Token
   CLOUDFLARE_ACCOUNT_ID     # Cloudflare Account ID
   ADMIN_USERNAME            # 管理员用户名（如 admin）
   ADMIN_PASSWORD            # 管理员密码（强密码）
   ```

3. **获取 Cloudflare 凭证**：
   - 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
   - Account ID：右侧边栏可见
   - API Token：My Profile → API Tokens → Create Token
     - 使用模板：Edit Cloudflare Workers
     - 权限：Account.Cloudflare Workers Scripts (Edit)
     - 复制生成的 Token

4. **触发部署**：
   - 推送代码到 `main` 分支
   - 或手动触发：Actions → Deploy to Cloudflare → Run workflow

5. **查看部署结果**：
   - Actions 标签页查看部署日志
   - 成功后会显示部署的 URL

**优势**：
- ✅ 自动化部署，推送即上线
- ✅ 版本控制，易于回滚
- ✅ 团队协作，统一管理
- ✅ 无需本地配置 Wrangler

### 方式 2：自动化脚本

**适合场景**：个人使用、快速部署

#### Windows

```bash
cd CPAOM/cf
setup.bat
```

#### Linux/macOS

```bash
cd CPAOM/cf
chmod +x setup.sh && ./setup.sh
```

脚本自动完成：安装依赖 → 登录 Cloudflare → 创建资源 → 设置凭证 → 部署

### 方式 3：手动部署

**适合场景**：自定义配置、学习流程

```bash
# 1. 安装依赖
npm install

# 2. 登录 Cloudflare
wrangler login

# 3. 创建 KV 命名空间
wrangler kv:namespace create "ACCOUNTS"
# 复制输出的 ID，更新 wrangler.toml 中的 kv_namespaces.id

# 4. 创建 D1 数据库
wrangler d1 create cpa-manager-db
# 复制输出的 database_id，更新 wrangler.toml 中的 d1_databases.database_id

# 5. 运行数据库迁移
wrangler d1 migrations apply cpa-manager-db --remote

# 6. 设置管理员凭证
wrangler secret put ADMIN_USERNAME  # 输入: admin
wrangler secret put ADMIN_PASSWORD  # 输入: your-password

# 7. 部署
npm run deploy
```

## 部署成功

部署成功后，你会看到：

```
✨ Success! Published cpa-manager
  https://cpa-manager.your-subdomain.workers.dev
```

## 首次使用

1. **登录**：访问部署 URL，使用设置的用户名密码登录
2. **添加服务器**：服务器管理 → 添加服务器 → 填写 Base URL 和 Token → 测试连接
3. **查看账号**：账号管理 → 选择服务器 → 查看列表
4. **批量操作**：批量操作 → 检查使用情况 / 下载打包 / 批量上传

## 功能概览

- Web 界面、多服务器管理、Token 自动复活
- 批量检查/下载/上传、实时统计
- 边缘计算（全球 CDN）、KV + D1 存储

## 安全建议

- **修改密码**：`wrangler secret put ADMIN_PASSWORD`（使用强密码）
- **限制访问**：配置 Cloudflare Access 或 IP 白名单
- **定期备份**：`wrangler kv:key get --binding=ACCOUNTS "cpa_servers" > backup.json`

## 常见问题

**登录失败？** 检查 Secret：`wrangler secret list`

**服务器连接失败？** 确认 URL、Token 正确，CPA 服务器允许远程管理

**KV 错误？** 确认 KV 已创建，`wrangler.toml` ID 正确，重新部署

**查看日志？** `npm run tail`

## 更多资源

- [API 文档](api.md) - REST API 参考
- [开发指南](development.md) - 本地开发和贡献

## 下一步

配置自定义域名、添加更多服务器、启用 Cloudflare Access、配置监控告警

---

免费套餐支持 100,000 请求/天，适合管理 100+ 账号，全球边缘节点零延迟。
