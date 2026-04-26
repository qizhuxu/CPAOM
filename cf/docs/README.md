# 文档索引

欢迎查阅 CPA 账号管理系统文档。

## 📚 文档导航

### 新手入门

- **[快速开始](quickstart.md)** ⭐
  - 5 分钟部署指南
  - 自动化脚本使用
  - 首次登录和配置

- **[GitHub Actions 部署](github-actions.md)** 🆕
  - 自动化 CI/CD 配置
  - GitHub Secrets 设置
  - 工作流详解
  - 快速设置指南：[github-actions-setup.md](github-actions-setup.md)
  - 故障排查

### 部署和运维

- **[部署指南](deployment.md)**
  - 详细部署步骤
  - 环境配置
  - 故障排查
  - 安全加固
  - 监控和日志

### 开发相关

- **[开发指南](development.md)**
  - 本地开发环境设置
  - 项目结构说明
  - 代码规范
  - 测试策略
  - 贡献指南

- **[API 参考](api.md)**
  - 所有 API 端点
  - 请求/响应格式
  - 认证方式
  - 错误处理
  - 使用示例

- **[数据同步与备份](sync-and-backup.md)** 🆕
  - 数据同步备份功能
  - 定时自动维护
  - Cron 表达式配置
  - 备份恢复流程

- **[架构设计](architecture.md)**
  - 系统架构图
  - 技术选型理由
  - 数据流说明
  - 性能优化
  - 扩展性设计

### 项目信息

- **[更新日志](changelog.md)**
  - 版本历史
  - 功能变更
  - Bug 修复

- **[项目总结](project-summary.md)**
  - 完整交付说明
  - 功能清单
  - 技术亮点

- **[新功能说明](new-features.md)** 🆕
  - 数据同步备份功能
  - 定时自动维护
  - 使用场景和示例

- **[文件清单](file-manifest.md)**
  - 所有文件列表
  - 文件说明
  - 代码统计

## 🎯 按场景查找

### 我想部署系统

1. 阅读 [快速开始](quickstart.md)
2. 运行自动化脚本或按照 [部署指南](deployment.md) 手动部署
3. 参考 [部署指南 - 安全配置](deployment.md#安全配置) 加固系统

### 我想开发新功能

1. 阅读 [开发指南](development.md) 设置本地环境
2. 查看 [架构设计](architecture.md) 了解系统结构
3. 参考 [API 参考](api.md) 了解现有接口
4. 按照 [开发指南 - 代码规范](development.md#代码规范) 编写代码

### 我想集成 API

1. 查看 [API 参考](api.md) 了解所有端点
2. 参考 [API 参考 - 认证流程](api.md#认证流程)
3. 使用 [API 参考 - 示例代码](api.md#示例完整工作流)

### 我遇到了问题

1. 查看 [部署指南 - 故障排查](deployment.md#故障排查)
2. 查看 [开发指南 - 常见问题](development.md#常见开发问题)
3. 查看 [GitHub Issues](https://github.com/your-repo/issues)

## 📖 文档约定

### 代码块

```bash
# Shell 命令
npm install
```

```javascript
// JavaScript 代码
const result = await fetch('/api/endpoint');
```

```json
// JSON 数据
{
  "key": "value"
}
```

### 标注说明

- ⭐ - 推荐阅读
- ✅ - 最佳实践
- ❌ - 不推荐
- ⚠️ - 重要提示
- 💡 - 提示
- 🐛 - 已知问题

### 链接约定

- `[文档名](filename.md)` - 文档内部链接
- `[章节](#anchor)` - 同文档内锚点
- `[外部](https://example.com)` - 外部链接

## 🔄 文档更新

文档与代码同步更新。如果发现文档过时或错误：

1. 提交 [Issue](https://github.com/your-repo/issues)
2. 或直接提交 Pull Request 修复

## 📝 贡献文档

欢迎改进文档！请遵循以下原则：

1. **简洁明了** - 避免冗长描述
2. **实用为主** - 提供可操作的步骤
3. **解释原因** - 说明"为什么"而不只是"怎么做"
4. **保持更新** - 代码变更时同步更新文档
5. **避免重复** - 一个主题只在一个地方详细说明

详见 [开发指南 - 贡献指南](development.md#贡献指南)

## 🌐 其他资源

### 官方文档

- [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
- [Wrangler CLI 文档](https://developers.cloudflare.com/workers/wrangler/)
- [Cloudflare KV 文档](https://developers.cloudflare.com/workers/runtime-apis/kv/)

### 相关项目

- [Python 版本](../../manage_accounts.py) - 命令行版本
- [CPA API 文档](../../test_docs/CPA_API_Reference.md)
- [Token 复活机制](../../test_docs/TOKEN_REVIVE_EXPLAINED.md)

---

**文档版本**: v1.0.0  
**最后更新**: 2026-04-25  
**维护者**: [Your Name]
