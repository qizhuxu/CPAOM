# CPA 账号管理系统 - Web 版

支持 Docker 和本地部署的 Web 管理界面版本。

## 🎯 特点

- 🌐 完整的 Web 界面 - 现代化响应式设计
- 🐳 Docker 支持 - 一键部署，开箱即用
- 💻 本地部署 - 支持 Windows/Linux/macOS
- 🔐 用户认证 - 安全的登录系统
- 📊 实时统计 - 账号状态监控
- 🔄 自动维护 - Token 自动复活
- 💾 SQLite 数据库 - 数据持久化
- 📦 批量操作 - 高效管理大量账号

## 🚀 快速开始

### 方式 1：使用预构建镜像（推荐）⭐

直接使用 GitHub Container Registry 的预构建镜像：

```bash
cd CPAOM/web

# 拉取最新镜像
docker pull ghcr.io/qizhuxu/cpaom/cpaom-web:latest

# 启动容器
docker-compose up -d
```

访问 http://localhost:5000，默认账号：`admin` / `admin123`

### 方式 2：本地构建镜像

如果需要自定义修改，可以本地构建：

```bash
cd CPAOM/web

# 编辑 docker-compose.yml，注释 image 行，取消注释 build 行
# 然后构建并启动
docker-compose up -d --build
```

### 方式 3：本地部署（不使用 Docker）

**Windows:**
```bash
setup.bat
run.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

## 📋 核心功能

- 多服务器管理
- 账号列表查看
- 批量检查使用情况
- Token 自动复活
- 批量下载/上传
- 数据同步备份
- 操作日志审计

## 🏗️ 技术栈

**后端:** Flask + SQLite + APScheduler  
**前端:** Bootstrap 5 + Vanilla JS

## 🔧 配置

编辑 `config.json` 添加 CPA 服务器：

```json
{
  "cpa_servers": [
    {
      "id": "server1",
      "name": "主服务器",
      "base_url": "https://your-cpa-server.com",
      "token": "mgt-xxx",
      "enable_token_revive": true
    }
  ],
  "settings": {
    "max_workers": 10
  }
}
```

编辑 `.env` 修改管理员密码：

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
SECRET_KEY=your-random-secret-key
```

## 🆚 版本对比

| 特性 | Shell 版 | Cloudflare 版 | Web 版 |
|------|---------|---------------|--------|
| 界面 | 命令行 | Web | Web ✅ |
| 部署 | 本地 | 云端 | Docker/本地 ✅ |
| 数据库 | 无 | D1 | SQLite ✅ |
| 成本 | 免费 | $0-5/月 | 免费 ✅ |

## 📚 相关项目

- [Shell 版本](../shell/) - 命令行版本
- [Cloudflare 版本](../cf/) - 云端部署版本

## 📄 许可证

MIT License
