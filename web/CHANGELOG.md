# 更新日志

## [1.0.1] - 2026-04-26

### 🐛 Bug 修复

#### 前端修复
- ✅ 修复使用情况检查显示错误 - 现在正确显示使用百分比而非美元金额
- ✅ 使用正确的数据结构：`rate_limit.primary_window.used_percent`
- ✅ 添加状态图标：🟢 (< 50%), 🟡 (≥ 50%), 🔴 (已达限额)
- ✅ 移除调试 console.log 语句
- ✅ 移除侧边栏重复的"服务器管理"菜单项（已在仪表板中实现）

#### 数据显示改进
- ✅ 使用情况现在显示为百分比（如 "45.2%"）
- ✅ 详情栏显示状态图标和限额状态
- ✅ 与 Shell 版本保持一致的数据结构

## [1.0.0] - 2026-04-26

### 🎉 首次发布

完整的 Web 版 CPA 账号管理系统，支持 Docker 和本地部署。

### ✨ 核心功能

#### 服务器管理
- ✅ 添加/编辑/删除 CPA 服务器
- ✅ 测试服务器连接
- ✅ 多服务器支持
- ✅ 服务器启用/禁用

#### 账号管理
- ✅ 查看账号列表
- ✅ 批量检查使用情况
- ✅ 启用/禁用账号
- ✅ Token 自动复活
- ✅ 账号状态监控

#### 批量操作
- ✅ 批量下载账号（ZIP 打包）
- ✅ 批量上传账号（支持 ZIP）
- ✅ 批量复活 Token
- ✅ 并发处理（可配置线程数）

#### 数据同步
- ✅ 认证文件同步到数据库
- ✅ 同步日志记录
- ✅ 增量同步支持

#### 统计分析
- ✅ 仪表板统计
- ✅ 服务器统计
- ✅ 账号状态统计
- ✅ 操作日志审计

#### 系统功能
- ✅ 用户认证（Flask-Login）
- ✅ SQLite 数据库
- ✅ 定时任务调度（APScheduler）
- ✅ 操作审计日志
- ✅ 错误处理

### 🏗️ 技术实现

#### 后端
- Flask 3.0.0 - Web 框架
- Flask-Login 0.6.3 - 用户认证
- APScheduler 3.10.4 - 定时任务
- SQLite - 数据存储
- requests - HTTP 客户端

#### 前端
- Bootstrap 5 - UI 框架
- Font Awesome 6 - 图标库
- Vanilla JavaScript - 交互逻辑
- Axios - API 调用

#### 部署
- Docker - 容器化部署
- Docker Compose - 编排工具
- 支持 Windows/Linux/macOS 本地部署

### 📦 部署方式

#### Docker 部署
```bash
docker-compose up -d
```

#### 本地部署
**Windows:**
```bash
setup.bat
run.bat
```

**Linux/macOS:**
```bash
./setup.sh
./run.sh
```

### 🔧 配置

#### 环境变量（.env）
- `FLASK_ENV` - 运行环境
- `SECRET_KEY` - 会话密钥
- `ADMIN_USERNAME` - 管理员用户名
- `ADMIN_PASSWORD` - 管理员密码
- `HOST` - 监听地址
- `PORT` - 监听端口
- `DATABASE_PATH` - 数据库路径

#### 配置文件（config.json）
- `cpa_servers` - CPA 服务器列表
- `settings.max_workers` - 并发线程数
- `settings.auto_sync_interval` - 自动同步间隔
- `settings.token_revive_max_attempts` - Token 复活最大尝试次数

### 📊 数据库表

- `auth_files_backup` - 认证文件备份
- `config_backups` - 配置文件备份
- `sync_logs` - 同步日志
- `scheduled_tasks` - 定时任务配置
- `task_executions` - 任务执行历史
- `audit_logs` - 操作审计日志
- `system_stats` - 系统统计

### 🔒 安全特性

- ✅ 用户认证保护
- ✅ 会话管理
- ✅ 密码环境变量配置
- ✅ 操作审计日志
- ✅ 错误信息脱敏

### 📚 文档

- ✅ README.md - 项目说明
- ✅ QUICKSTART.md - 快速开始
- ✅ PROJECT_STRUCTURE.md - 项目结构
- ✅ CHANGELOG.md - 更新日志

### 🎯 已知限制

- 单用户系统（仅支持一个管理员）
- 定时任务功能待完善
- 暂无图表可视化
- 暂无邮件通知

### 🚀 未来计划

- [ ] 多用户支持
- [ ] 权限管理
- [ ] 图表可视化（Chart.js）
- [ ] 邮件通知
- [ ] WebSocket 实时更新
- [ ] 更多定时任务类型
- [ ] API 文档（Swagger）
- [ ] 单元测试

### 🐛 Bug 修复

无（首次发布）

### 📝 注意事项

1. 首次使用请修改默认管理员密码
2. 生产环境请配置 HTTPS
3. 定期备份 `data/` 目录
4. 建议使用 Docker 部署以获得最佳体验

---

**发布日期:** 2026-04-26  
**版本:** 1.0.0  
**状态:** 稳定版
