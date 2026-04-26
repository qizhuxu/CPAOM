# GitHub Actions 快速设置指南

5 分钟配置自动部署到 Cloudflare Workers。

## 📋 准备工作

需要以下信息：
- ✅ GitHub 账号
- ✅ Cloudflare 账号
- ✅ 代码已推送到 GitHub

## 🚀 快速设置（5 步）

### 步骤 1：获取 Cloudflare API Token

1. 访问 https://dash.cloudflare.com/profile/api-tokens
2. 点击 **Create Token**
3. 选择 **Edit Cloudflare Workers** 模板
4. 点击 **Continue to summary** → **Create Token**
5. **复制 Token**（只显示一次！）

### 步骤 2：获取 Account ID

1. 访问 https://dash.cloudflare.com/
2. 进入 **Workers & Pages**
3. 右侧找到 **Account ID**
4. **复制 Account ID**

### 步骤 3：配置 GitHub Secrets

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加 4 个 Secrets：

```
名称: CLOUDFLARE_API_TOKEN
值: [粘贴步骤1的Token]

名称: CLOUDFLARE_ACCOUNT_ID
值: [粘贴步骤2的Account ID]

名称: ADMIN_USERNAME
值: admin

名称: ADMIN_PASSWORD
值: [设置一个强密码]
```

### 步骤 4：更新 wrangler.toml

确保 `wrangler.toml` 配置正确：

```toml
name = "cpa-manager"
main = "src/index.js"
compatibility_date = "2024-01-01"

[[kv_namespaces]]
binding = "ACCOUNTS"
id = "your-kv-namespace-id"  # 替换为实际ID

[[d1_databases]]
binding = "DB"
database_name = "cpa-manager-db"
database_id = "your-database-id"  # 替换为实际ID
```

### 步骤 5：推送代码触发部署

```bash
git add .
git commit -m "Setup GitHub Actions"
git push origin main
```

## ✅ 验证部署

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 查看 **Deploy to Cloudflare Workers** 工作流
4. 等待部署完成（约 2-3 分钟）
5. 看到绿色 ✅ 表示成功！

## 🎯 部署成功后

访问你的 Worker URL：
```
https://cpa-manager.your-subdomain.workers.dev
```

使用设置的用户名和密码登录。

## 🔄 工作流说明

### 自动触发
- ✅ 推送到 `main` 分支 → 自动部署
- ✅ 创建 Pull Request → 自动测试 + 预览
- ✅ 每周日凌晨 → 自动清理旧数据

### 手动触发
1. 进入 **Actions** 标签
2. 选择工作流
3. 点击 **Run workflow**

## 📊 查看部署状态

### 方法 1：GitHub Actions
1. 进入仓库 **Actions** 标签
2. 查看最新的工作流运行
3. 点击查看详细日志

### 方法 2：Cloudflare Dashboard
1. 访问 https://dash.cloudflare.com/
2. 进入 **Workers & Pages**
3. 选择 `cpa-manager`
4. 查看部署历史和日志

### 方法 3：命令行
```bash
wrangler tail
```

## 🐛 常见问题

### Q: 部署失败，显示 "Authentication error"

**A:** 检查 Secrets 配置
1. 确认 `CLOUDFLARE_API_TOKEN` 正确
2. 确认 Token 有 Workers 编辑权限
3. 确认 `CLOUDFLARE_ACCOUNT_ID` 正确

### Q: 数据库迁移失败

**A:** 手动运行迁移
```bash
wrangler d1 migrations apply cpa-manager-db --remote
```

### Q: Secrets 未生效

**A:** 重新设置 Secrets
1. 删除旧的 Secrets
2. 重新添加
3. 重新运行工作流

### Q: 如何回滚部署？

**A:** 两种方法
1. **Git 回滚**：
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Cloudflare Dashboard**：
   - 进入 Workers & Pages
   - 选择之前的部署版本
   - 点击 Rollback

## 🎨 添加部署徽章

在 `README.md` 中添加：

```markdown
![Deploy Status](https://github.com/your-username/cpa-manager/actions/workflows/deploy.yml/badge.svg)
```

效果：
![Deploy Status](https://github.com/your-username/cpa-manager/actions/workflows/deploy.yml/badge.svg)

## 📝 下一步

- [ ] 配置自定义域名
- [ ] 设置分支保护规则
- [ ] 配置通知（Slack/Email）
- [ ] 添加更多测试

## 📚 详细文档

查看完整文档：[docs/github-actions.md](docs/github-actions.md)

---

**设置完成！** 🎉

现在每次推送代码都会自动部署到 Cloudflare Workers。
