# CPA 账号管理系统 (CPAOM)

CPA 账号管理系统提供三种部署方式，满足不同场景需求。

## 📦 三种部署方式

### 1. Shell 版 - 命令行工具

**适用场景:** 个人使用、快速操作、脚本自动化

**特点:**
- ✅ 纯命令行界面
- ✅ 无需安装依赖服务
- ✅ 支持批量操作
- ✅ 轻量级，启动快

**快速开始:**
```bash
cd CPAOM/shell
python manage_accounts.py
```

[查看详细文档](shell/README.md)

---

### 2. Cloudflare 版 - 云端部署

**适用场景:** 零运维、全球访问、团队协作

**特点:**
- ✅ 完整 Web 界面
- ✅ 零服务器运维
- ✅ 全球 CDN 加速
- ✅ D1 数据库持久化
- ✅ 定时任务支持

**快速开始:**
```bash
cd CPAOM/cf
npm install
npx wrangler deploy
```

[查看详细文档](cf/README.md)

---

### 3. Web 版 - Docker/本地部署

**适用场景:** 本地部署、数据私有、完全控制

**特点:**
- ✅ 完整 Web 界面
- ✅ Docker 一键部署
- ✅ SQLite 数据库
- ✅ 支持 Windows/Linux/macOS
- ✅ 数据完全私有

**快速开始:**
```bash
cd CPAOM/web
docker pull ghcr.io/qizhuxu/cpaom/cpaom-web:latest
docker-compose up -d
```

[查看详细文档](web/README.md)

---

## 🆚 版本对比

| 特性 | Shell 版 | Cloudflare 版 | Web 版 |
|------|---------|---------------|--------|
| **界面** | 命令行 | Web | Web |
| **部署难度** | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐ 中等 |
| **运维成本** | 需手动运行 | 零运维 | 需维护服务器 |
| **数据存储** | 无持久化 | D1 数据库 | SQLite |
| **定时任务** | 手动/Cron | 内置 Cron | APScheduler |
| **访问方式** | 本地 | 全球访问 | 局域网/公网 |
| **成本** | 免费 | $0-5/月 | 免费（自托管） |
| **适用规模** | 小型 | 中大型 | 中型 |

## 🎯 选择建议

### 选择 Shell 版，如果你：
- 只需要偶尔管理账号
- 喜欢命令行操作
- 不需要 Web 界面
- 想要最简单的部署

### 选择 Cloudflare 版，如果你：
- 需要团队协作
- 想要零运维
- 需要全球访问
- 可以接受少量成本

### 选择 Web 版，如果你：
- 需要本地部署
- 数据必须私有
- 有服务器资源
- 想要完全控制

## 🚀 核心功能

所有版本都支持以下核心功能：

- ✅ 多服务器管理
- ✅ 账号列表查看
- ✅ 批量检查使用情况
- ✅ Token 自动复活
- ✅ 批量下载/上传
- ✅ 认证文件管理

## 📚 文档

- [Shell 版文档](shell/README.md)
- [Cloudflare 版文档](cf/README.md)
- [Web 版文档](web/README.md)

## 🔧 技术栈

**Shell 版:**
- Python 3.8+
- requests, concurrent.futures

**Cloudflare 版:**
- Cloudflare Workers
- D1 Database
- KV Storage

**Web 版:**
- Flask (Python)
- SQLite
- Bootstrap 5
- Docker

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**快速开始:** 选择适合你的版本，查看对应文档开始使用 🚀
