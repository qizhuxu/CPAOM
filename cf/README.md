# CPA 账号管理系统 - Cloudflare 版

基于 Cloudflare Workers 的 CPA 账号管理系统，提供 Web 界面进行账号管理、批量操作和统计分析。

## 快速开始

### 方式 1：GitHub Actions 自动部署（推荐）⭐

使用 GitHub Actions 实现自动化部署：

1. **Fork 仓库到 GitHub**
2. **配置 Secrets**（5 分钟）
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
3. **推送代码自动部署**

📖 [查看详细设置指南](docs/github-actions-setup.md)

### 方式 2：自动部署脚本

**Windows:**
```bash
cd L/CPAD/cf
setup.bat
```

**Linux/macOS:**
```bash
cd L/CPAD/cf
chmod +x setup.sh
./setup.sh
```

### 方式 3：手动部署

```bash
# 1. 安装依赖
npm install

# 2. 登录 Cloudflare
wrangler login

# 3. 创建 KV 命名空间
wrangler kv:namespace create "ACCOUNTS"
# 复制输出的 ID，更新 wrangler.toml

# 4. 创建 D1 数据库
wrangler d1 create cpa-manager-db
# 复制输出的 database_id，更新 wrangler.toml

# 5. 运行数据库迁移
wrangler d1 migrations apply cpa-manager-db --remote

# 6. 设置管理员凭证
wrangler secret put ADMIN_USERNAME  # 输入: admin
wrangler secret put ADMIN_PASSWORD  # 输入: your-password

# 7. 部署
npm run deploy
```

访问部署的 URL，使用设置的凭证登录。

## 核心功能

- 🌐 **Web 管理界面** - 现代化响应式 UI
- 🔐 **安全认证** - Token 身份验证
- 🌍 **多服务器管理** - 支持管理多个 CPA 服务器
- 📊 **实时统计** - 账号状态、服务器状态监控
- 🔄 **Token 自动复活** - 自动刷新过期的 OAuth Token
- 📦 **批量操作** - 批量检查、下载、上传账号
- 💾 **数据同步备份** - 认证文件和配置自动备份到 D1 数据库
- ⏰ **定时自动维护** - 支持定时任务自动执行维护操作
- ⚡ **边缘计算** - 部署在 Cloudflare 全球网络
- 💾 **双重存储** - KV 存储配置，D1 数据库备份数据

## 文档

- **[快速开始](docs/quickstart.md)** - 5分钟部署指南
- **[部署指南](docs/deployment.md)** - 详细部署步骤和故障排查
- **[数据同步与备份](docs/sync-and-backup.md)** - 🆕 数据备份和定时维护
- **[架构设计](docs/architecture.md)** - 系统架构和技术选型
- **[API 参考](docs/api.md)** - API 端点和使用说明
- **[开发指南](docs/development.md)** - 本地开发和贡献指南
- **[更新日志](docs/changelog.md)** - 版本历史
- **[项目总结](docs/project-summary.md)** - 完整交付说明

📖 [查看所有文档](docs/)

## 技术栈

- **前端**: HTML/CSS/JavaScript（内嵌在 Worker）
- **后端**: Cloudflare Workers（边缘计算）
- **存储**: Cloudflare KV（键值存储）
- **部署**: Wrangler CLI

## 为什么选择 Cloudflare？

- ✅ **零运维** - 无需管理服务器
- ✅ **全球分布** - 自动部署到全球边缘节点
- ✅ **自动扩展** - 根据流量自动扩展
- ✅ **低成本** - 免费套餐支持 100,000 请求/天
- ✅ **高性能** - 边缘计算，低延迟

## 成本

**免费套餐**（适合个人和小团队）:
- 100,000 请求/天
- 1GB KV 存储
- 全球 CDN

**付费套餐**（$5/月）:
- 10,000,000 请求/月
- 无限 KV 存储

## 安全建议

⚠️ **部署后立即修改默认密码**:
```bash
wrangler secret put ADMIN_PASSWORD
```

更多安全建议请查看 [部署指南](docs/deployment.md#安全配置)。

## 许可证

MIT License

## 相关项目

- [Python 版本](../manage_accounts.py) - 命令行版本的 CPA 管理工具
- [CPA 服务器](https://github.com/your-repo/cpa-server) - CPA 服务器实现

---

**需要帮助？** 查看 [文档](docs/) 或提交 [Issue](https://github.com/your-repo/issues)
