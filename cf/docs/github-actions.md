# GitHub Actions 自动部署

本文档说明如何使用 GitHub Actions 自动部署 CPA 管理系统到 Cloudflare Workers。

## 🎯 工作流概述

我们提供了 4 个 GitHub Actions 工作流：

1. **deploy.yml** - 自动部署到生产环境
2. **test.yml** - 运行测试和代码检查
3. **preview.yml** - 为 PR 创建预览环境
4. **cleanup.yml** - 定期清理旧数据

## 📋 前置要求

### 1. GitHub 仓库
确保代码已推送到 GitHub 仓库。

### 2. Cloudflare 凭证
需要以下信息：
- **API Token** - Cloudflare API 令牌
- **Account ID** - Cloudflare 账户 ID

### 3. 管理员凭证
- **ADMIN_USERNAME** - 管理员用户名
- **ADMIN_PASSWORD** - 管理员密码

## 🔑 配置 Secrets

### 步骤 1：获取 Cloudflare API Token

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 进入 **My Profile** → **API Tokens**
3. 点击 **Create Token**
4. 选择 **Edit Cloudflare Workers** 模板
5. 或创建自定义 Token，需要以下权限：
   - Account - Workers Scripts: Edit
   - Account - Workers KV Storage: Edit
   - Account - D1: Edit
6. 复制生成的 Token

### 步骤 2：获取 Account ID

1. 在 Cloudflare Dashboard 中
2. 进入 **Workers & Pages**
3. 右侧可以看到 **Account ID**
4. 复制 Account ID

### 步骤 3：在 GitHub 设置 Secrets

1. 进入 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下 Secrets：

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `CLOUDFLARE_API_TOKEN` | 你的 API Token | Cloudflare API 令牌 |
| `CLOUDFLARE_ACCOUNT_ID` | 你的 Account ID | Cloudflare 账户 ID |
| `ADMIN_USERNAME` | admin | 管理员用户名 |
| `ADMIN_PASSWORD` | your-password | 管理员密码 |

## 🚀 工作流详解

### 1. deploy.yml - 自动部署

**触发条件：**
- 推送到 `main` 或 `master` 分支
- 手动触发

**执行步骤：**
1. ✅ 检出代码
2. ✅ 安装 Node.js 和依赖
3. ✅ 运行数据库迁移
4. ✅ 部署到 Cloudflare Workers
5. ✅ 设置环境变量（Secrets）

**使用方法：**
```bash
# 自动触发
git push origin main

# 手动触发
# 在 GitHub 仓库页面：Actions → Deploy to Cloudflare Workers → Run workflow
```

### 2. test.yml - 测试和检查

**触发条件：**
- 推送到任何分支
- Pull Request

**执行步骤：**
1. ✅ 检出代码
2. ✅ 安装依赖
3. ✅ 检查 wrangler.toml 语法
4. ✅ 验证数据库迁移
5. ✅ 检查 JavaScript 语法

**使用方法：**
```bash
# 自动触发
git push origin develop

# 或创建 Pull Request
```

### 3. preview.yml - 预览部署

**触发条件：**
- Pull Request 到 `main` 或 `master`

**执行步骤：**
1. ✅ 检出代码
2. ✅ 安装依赖
3. ✅ 部署到预览环境
4. ✅ 在 PR 中评论预览 URL

**使用方法：**
```bash
# 创建 Pull Request
git checkout -b feature/new-feature
git push origin feature/new-feature
# 在 GitHub 创建 PR
```

**预览环境配置：**

在 `wrangler.toml` 中添加：
```toml
[env.preview]
name = "cpa-manager-preview"
vars = { ENVIRONMENT = "preview" }
```

### 4. cleanup.yml - 定期清理

**触发条件：**
- 每周日凌晨 3 点（Cron）
- 手动触发

**执行步骤：**
1. ✅ 删除 90 天前的同步日志
2. ✅ 删除 90 天前的任务执行记录
3. ✅ 删除 90 天前的审计日志
4. ✅ 保留每个服务器最新 10 个配置备份

**使用方法：**
```bash
# 自动触发（每周日）
# 或手动触发：Actions → Cleanup Old Data → Run workflow
```

## 📝 工作流文件结构

```
.github/
└── workflows/
    ├── deploy.yml      # 生产部署
    ├── test.yml        # 测试检查
    ├── preview.yml     # 预览部署
    └── cleanup.yml     # 数据清理
```

## 🔧 自定义配置

### 修改部署分支

编辑 `deploy.yml`：
```yaml
on:
  push:
    branches:
      - main
      - production  # 添加其他分支
```

### 修改 Node.js 版本

编辑任何工作流文件：
```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'  # 改为 20
```

### 修改清理周期

编辑 `cleanup.yml`：
```yaml
on:
  schedule:
    - cron: '0 3 * * 0'  # 每周日 3:00
    # 改为每天：'0 3 * * *'
    # 改为每月：'0 3 1 * *'
```

### 添加通知

在工作流中添加通知步骤：

**Slack 通知：**
```yaml
- name: Notify Slack
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "✅ Deployment successful!"
      }
```

**Email 通知：**
```yaml
- name: Send email
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Deployment Failed
    body: Check GitHub Actions for details
    to: admin@example.com
```

## 🎯 完整部署流程

### 首次设置

1. **Fork 或克隆仓库**
   ```bash
   git clone https://github.com/your-username/cpa-manager.git
   cd cpa-manager/L/CPAD/cf
   ```

2. **配置 GitHub Secrets**
   - 添加 `CLOUDFLARE_API_TOKEN`
   - 添加 `CLOUDFLARE_ACCOUNT_ID`
   - 添加 `ADMIN_USERNAME`
   - 添加 `ADMIN_PASSWORD`

3. **更新 wrangler.toml**
   ```toml
   # 确保配置正确
   name = "cpa-manager"
   
   [[kv_namespaces]]
   binding = "ACCOUNTS"
   id = "your-kv-id"
   
   [[d1_databases]]
   binding = "DB"
   database_name = "cpa-manager-db"
   database_id = "your-db-id"
   ```

4. **推送代码触发部署**
   ```bash
   git add .
   git commit -m "Initial deployment setup"
   git push origin main
   ```

5. **查看部署状态**
   - 进入 GitHub 仓库
   - 点击 **Actions** 标签
   - 查看工作流执行状态

### 日常开发流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **开发和测试**
   ```bash
   # 本地开发
   npm run dev
   
   # 提交代码
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

3. **创建 Pull Request**
   - 在 GitHub 创建 PR
   - 自动触发测试和预览部署
   - 查看预览环境

4. **合并到主分支**
   - PR 审核通过后合并
   - 自动触发生产部署

## 📊 监控和日志

### 查看部署日志

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择工作流运行
4. 查看详细日志

### 查看 Cloudflare 日志

```bash
# 实时日志
wrangler tail

# 或在 Cloudflare Dashboard 查看
```

### 部署状态徽章

在 README.md 中添加：
```markdown
![Deploy Status](https://github.com/your-username/cpa-manager/actions/workflows/deploy.yml/badge.svg)
```

## 🐛 故障排查

### 部署失败

**问题**：部署失败，显示认证错误

**解决**：
1. 检查 `CLOUDFLARE_API_TOKEN` 是否正确
2. 确认 Token 有足够的权限
3. 验证 `CLOUDFLARE_ACCOUNT_ID` 是否正确

### 数据库迁移失败

**问题**：D1 迁移失败

**解决**：
1. 确认数据库已创建
2. 检查 `wrangler.toml` 中的 `database_id`
3. 手动运行迁移：
   ```bash
   wrangler d1 migrations apply cpa-manager-db --remote
   ```

### Secrets 未生效

**问题**：环境变量未设置

**解决**：
1. 确认 Secrets 名称拼写正确
2. 检查工作流中的 `secrets` 配置
3. 重新运行工作流

### 预览部署失败

**问题**：预览环境部署失败

**解决**：
1. 确认 `wrangler.toml` 中有 `[env.preview]` 配置
2. 检查预览环境的资源配置
3. 查看详细错误日志

## 🔒 安全最佳实践

### 1. 保护 Secrets
- ✅ 永远不要在代码中硬编码 Secrets
- ✅ 使用 GitHub Secrets 存储敏感信息
- ✅ 定期轮换 API Token

### 2. 限制权限
- ✅ API Token 只授予必要的权限
- ✅ 使用最小权限原则

### 3. 审计日志
- ✅ 定期查看部署日志
- ✅ 监控异常部署活动

### 4. 分支保护
- ✅ 启用分支保护规则
- ✅ 要求 PR 审核
- ✅ 要求状态检查通过

## 📚 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
- [Wrangler Action](https://github.com/cloudflare/wrangler-action)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## 🎉 总结

使用 GitHub Actions 自动部署的优势：

✅ **自动化** - 推送代码自动部署
✅ **预览环境** - PR 自动创建预览
✅ **测试保障** - 部署前自动测试
✅ **定期维护** - 自动清理旧数据
✅ **版本控制** - 完整的部署历史

---

**下一步**：配置 GitHub Secrets 并推送代码触发首次部署！
