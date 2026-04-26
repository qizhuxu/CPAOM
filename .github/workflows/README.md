# GitHub Actions 工作流说明

本项目包含多个自动化工作流，用于 CI/CD 和维护任务。

## 📋 工作流列表

### Cloudflare 版本

| 工作流 | 文件 | 触发条件 | 作用 |
|--------|------|----------|------|
| 🚀 部署生产 | `deploy-cloudflare.yml` | 推送到 main/master | 自动部署到 Cloudflare Workers |
| 👀 预览部署 | `preview-cloudflare.yml` | 创建/更新 PR | 部署预览环境并在 PR 中评论链接 |
| ✅ 代码测试 | `test-cloudflare.yml` | 推送/PR | 检查语法和配置 |
| 🗑️ 数据清理 | `cleanup-cloudflare.yml` | 每周日 3:00 AM | 清理 90 天前的旧数据 |

### Web 版本

| 工作流 | 文件 | 触发条件 | 作用 |
|--------|------|----------|------|
| 🐳 构建镜像 | `build-web-docker.yml` | 推送到 main/master 或版本标签 | 构建并推送 Docker 镜像 |

---

## 🔧 配置要求

### Cloudflare 工作流需要的 Secrets

在 GitHub 仓库设置中配置以下 Secrets：

**必需：**
- `CLOUDFLARE_API_TOKEN` - Cloudflare API 令牌
  - 获取方式：Cloudflare Dashboard → My Profile → API Tokens → Create Token
  - 权限：Account.Cloudflare Workers Scripts (Edit)
- `CLOUDFLARE_ACCOUNT_ID` - Cloudflare 账户 ID
  - 获取方式：Cloudflare Dashboard → Workers & Pages → 右侧栏
- `ADMIN_USERNAME` - 管理员用户名（自定义）
- `ADMIN_PASSWORD` - 管理员密码（自定义，建议使用强密码）

### Web Docker 工作流需要的 Secrets

**GitHub Container Registry（自动配置）：**
- 使用 `GITHUB_TOKEN`（自动提供，无需配置）
- 镜像推送到：`ghcr.io/你的用户名/仓库名/cpaom-web`

**Docker Hub（可选）：**
如果要同时推送到 Docker Hub，需要配置：
- `DOCKERHUB_USERNAME` - Docker Hub 用户名
- `DOCKERHUB_TOKEN` - Docker Hub 访问令牌
  - 获取方式：Docker Hub → Account Settings → Security → New Access Token

---

## 📦 Web Docker 镜像使用

### 拉取镜像

**从 GitHub Container Registry：**
```bash
docker pull ghcr.io/qizhuxu/cpaom/cpaom-web:latest
```

**从 Docker Hub（如果配置了）：**
```bash
docker pull qizhuxu/cpaom-web:latest
```

### 运行容器

```bash
docker run -d \
  --name cpaom-web \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.json:/app/config.json \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=your-password \
  ghcr.io/qizhuxu/cpaom/cpaom-web:latest
```

### 使用 Docker Compose

```yaml
version: '3.8'
services:
  cpaom-web:
    image: ghcr.io/qizhuxu/cpaom/cpaom-web:latest
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./config.json:/app/config.json
    environment:
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=your-password
    restart: unless-stopped
```

---

## 🏷️ 版本标签策略

### 自动生成的标签

工作流会根据不同情况自动生成标签：

| 触发方式 | 生成的标签 | 示例 |
|---------|-----------|------|
| 推送到 main | `latest` | `latest` |
| 推送到分支 | `分支名` | `develop` |
| 创建 PR | `pr-编号` | `pr-123` |
| 推送版本标签 | `版本号` | `v1.0.0`, `1.0`, `1` |
| Git commit | `分支名-SHA` | `main-abc1234` |

### 发布新版本

创建版本标签并推送：

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

这会触发构建并生成以下镜像标签：
- `v1.0.0`
- `1.0`
- `1`
- `latest`

---

## 🔒 安全扫描

Web Docker 工作流包含自动安全扫描：

- 使用 **Trivy** 扫描镜像漏洞
- 结果上传到 GitHub Security 标签
- 每次推送镜像后自动执行

**查看扫描结果：**
仓库 → Security → Code scanning alerts

---

## 🚀 手动触发工作流

所有工作流都支持手动触发：

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择要运行的工作流
4. 点击 **Run workflow** 按钮
5. 选择分支并确认

---

## 📊 工作流状态徽章

在 README.md 中添加状态徽章：

```markdown
![Deploy Cloudflare](https://github.com/qizhuxu/CPAOM/actions/workflows/deploy-cloudflare.yml/badge.svg)
![Build Docker](https://github.com/qizhuxu/CPAOM/actions/workflows/build-web-docker.yml/badge.svg)
```

---

## 🛠️ 故障排查

### Cloudflare 部署失败

**常见问题：**
1. API Token 权限不足
   - 解决：确保 Token 有 Workers Scripts Edit 权限
2. Account ID 错误
   - 解决：检查 Cloudflare Dashboard 中的 Account ID
3. wrangler.toml 配置错误
   - 解决：运行 `npx wrangler deploy --dry-run` 本地测试

### Docker 构建失败

**常见问题：**
1. 依赖安装失败
   - 解决：检查 `requirements.txt` 是否正确
2. 权限问题
   - 解决：确保 GitHub Actions 有 `packages: write` 权限
3. 多平台构建超时
   - 解决：移除 `platforms` 参数，只构建 `linux/amd64`

### 推送到 Docker Hub 失败

**常见问题：**
1. 认证失败
   - 解决：检查 `DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN` 是否正确
2. 仓库不存在
   - 解决：先在 Docker Hub 创建仓库

---

## 📝 自定义工作流

### 修改触发条件

编辑工作流文件的 `on` 部分：

```yaml
on:
  push:
    branches:
      - main
      - develop  # 添加其他分支
    paths:
      - 'web/**'
      - '!web/docs/**'  # 排除文档目录
```

### 修改构建平台

编辑 `build-web-docker.yml` 中的 `platforms`：

```yaml
platforms: linux/amd64  # 仅构建 amd64
# 或
platforms: linux/amd64,linux/arm64,linux/arm/v7  # 多平台
```

### 添加构建参数

```yaml
build-args: |
  PYTHON_VERSION=3.11
  APP_VERSION=${{ github.ref_name }}
```

---

## 📚 相关文档

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
- [Docker 文档](https://docs.docker.com/)
- [Wrangler CLI 文档](https://developers.cloudflare.com/workers/wrangler/)

---

**需要帮助？** 提交 [Issue](../../issues) 或查看项目文档。
