# CPA 账号管理系统 - Web 版

Flask + SQLite 实现的 Web 管理界面，支持 Docker 和本地部署。

## 快速开始

### Docker 部署（推荐）

```bash
cd CPAOM/web
docker-compose up -d
```

访问 http://localhost:5000，默认账号 `admin` / `admin123`

### 本地部署

```bash
# Windows
manage.bat setup
manage.bat start

# Linux/macOS
chmod +x manage.sh
./manage.sh setup
./manage.sh start
```

## 核心功能

- **服务器管理**：多服务器配置、连接测试、状态监控
- **账号管理**：列表查看、使用情况检查、Token 自动复活、启用/禁用
- **批量操作**：批量下载（ZIP）、批量上传、批量 Token 复活
- **数据同步**：认证文件同步到本地数据库、操作审计日志
- **实时日志**：SSE 推送、按级别过滤、彩色显示、日志下载

## 配置

**config.json**
```json
{
  "cpa_servers": [{
    "id": "server1",
    "name": "主服务器",
    "base_url": "https://your-cpa-server.com",
    "token": "mgt-xxx",
    "enable_token_revive": true
  }],
  "settings": {"max_workers": 10}
}
```

**.env**
```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
SECRET_KEY=your-secret-key
```

## 技术栈

Flask 3.0 + SQLite + APScheduler + Bootstrap 5

## 文档

- [快速开始](docs/quickstart.md) - 详细部署步骤
- [API 参考](docs/api.md) - REST API 文档
- [开发指南](docs/development.md) - 开发环境和贡献

## 更新日志

**v1.0.0** (2026-04-26)
- ✅ 完整 Web 界面
- ✅ 多服务器管理
- ✅ Token 自动复活
- ✅ 批量操作
- ✅ 实时日志流
- ✅ Docker 支持

## 许可证

MIT License
