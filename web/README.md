# CPA 账号管理系统 - Web 版

现代化的 Web 界面 CPA 账号管理系统，支持 Docker 和本地部署。

## 🚀 快速开始

### 使用 Docker（推荐）

```bash
# 下载配置文件
curl -O https://raw.githubusercontent.com/qizhuxu/CPAOM/main/web/docker-compose.yml
curl -O https://raw.githubusercontent.com/qizhuxu/CPAOM/main/web/.env.example

# 配置环境变量
cp .env.example .env
nano .env

# 启动服务
docker-compose up -d
```

访问 http://localhost:5000，默认账号：`admin` / `admin123`

### 本地部署

**Windows:**
```bash
git clone https://github.com/qizhuxu/CPAOM.git
cd CPAOM/web
setup.bat && run.bat
```

**Linux/macOS:**
```bash
git clone https://github.com/qizhuxu/CPAOM.git
cd CPAOM/web
chmod +x setup.sh run.sh && ./setup.sh && ./run.sh
```

## ✨ 核心功能

### 服务器管理
- 多服务器配置和管理
- 连接测试和状态监控
- 服务器启用/禁用控制

### 账号管理
- 账号列表查看和搜索
- 批量使用情况检查（显示百分比和状态图标）
- Token 自动复活机制
- 账号启用/禁用操作

### 批量操作
- 批量下载账号（ZIP 打包）
- 批量上传账号文件
- 批量 Token 复活处理

### 数据管理
- 认证文件同步到本地数据库
- 本地账号数据查看和管理
- 操作历史和审计日志

### 系统监控
- **实时日志流** - Server-Sent Events 推送
- **日志过滤** - 按级别和内容过滤
- **彩色显示** - 不同级别不同颜色
- **日志下载** - 导出为文本文件

## 🏗️ 技术栈

- **后端**: Flask + SQLite + APScheduler
- **前端**: Bootstrap 5 + Vanilla JavaScript
- **部署**: Docker + Docker Compose

## 📚 文档

- [API 参考](docs/api.md) - REST API 接口文档
- [系统架构](docs/architecture.md) - 技术架构和设计决策
- [开发指南](docs/development.md) - 开发环境搭建和贡献指南
- [部署指南](docs/deployment.md) - 生产环境部署配置
- [日志功能](docs/log-stream.md) - 实时日志流功能详解
- [更新日志](docs/changelog.md) - 版本更新记录

## ⚙️ 配置

### 服务器配置 (config.json)

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

### 环境变量 (.env)

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

## 🔧 开发

```bash
# 克隆仓库
git clone https://github.com/qizhuxu/CPAOM.git
cd CPAOM/web

# 安装依赖
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 配置文件
cp config.json.example config.json
cp .env.example .env

# 启动开发服务器
python app.py
```

详见 [开发指南](docs/development.md)

## 🐳 Docker 镜像

- **GitHub Container Registry**: `ghcr.io/qizhuxu/cpaom/cpaom-web:latest`
- **多架构支持**: amd64, arm64
- **安全扫描**: 集成 Trivy 安全扫描

## 📝 许可证

MIT License - 详见 [LICENSE](../LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

详见 [开发指南](docs/development.md#贡献指南)
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
