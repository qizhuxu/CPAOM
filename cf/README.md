# CPA 账号管理系统 - Cloudflare 版

Cloudflare Workers + D1 + KV 实现的零运维云端部署方案。

## 快速开始

**三种部署方式：**

1. **GitHub Actions**（推荐）- Fork 仓库，配置 Secrets，自动部署
2. **自动脚本** - 运行 `setup.bat` (Windows) 或 `setup.sh` (Linux/macOS)
3. **手动部署** - 使用 Wrangler CLI 逐步配置

详见 [快速开始文档](docs/quickstart.md)

## 核心功能

- **Web 界面**：现代化响应式 UI
- **多服务器**：管理多个 CPA 服务器
- **Token 复活**：自动刷新过期 OAuth Token
- **批量操作**：批量检查、下载、上传
- **数据备份**：D1 数据库自动备份
- **定时任务**：Cron 触发器自动维护
- **边缘计算**：全球 CDN 低延迟

## 技术栈

Cloudflare Workers + D1 Database + KV Storage + Wrangler CLI

## 成本

- **免费版**：100,000 请求/天，1GB KV 存储
- **付费版**：$5/月，10M 请求/月，无限 KV

## 文档

- [快速开始](docs/quickstart.md) - 详细部署步骤
- [API 参考](docs/api.md) - REST API 文档
- [开发指南](docs/development.md) - 本地开发

## 许可证

MIT License
