# 项目结构说明

```
CPAOM/web/
├── app.py                      # Flask 应用主入口
├── requirements.txt            # Python 依赖包
├── config.json.example         # 配置文件示例
├── .env.example               # 环境变量示例
├── Dockerfile                 # Docker 镜像构建文件
├── docker-compose.yml         # Docker Compose 配置
├── setup.sh                   # Linux/macOS 安装脚本
├── setup.bat                  # Windows 安装脚本
├── run.sh                     # Linux/macOS 启动脚本
├── run.bat                    # Windows 启动脚本
├── README.md                  # 项目说明文档
├── QUICKSTART.md              # 快速开始指南
├── .gitignore                 # Git 忽略文件
│
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── db_service.py         # 数据库服务
│   ├── cpa_client.py         # CPA API 客户端
│   ├── config_manager.py     # 配置管理器
│   └── scheduler.py          # 定时任务调度器
│
├── routes/                    # 路由蓝图
│   ├── __init__.py
│   ├── auth.py               # 认证路由
│   ├── servers.py            # 服务器管理
│   ├── accounts.py           # 账号管理
│   ├── operations.py         # 批量操作
│   ├── stats.py              # 统计信息
│   ├── sync.py               # 同步备份
│   └── tasks.py              # 定时任务
│
├── templates/                 # HTML 模板
│   ├── base.html             # 基础模板
│   ├── dashboard.html        # 仪表板
│   ├── 404.html              # 404 错误页
│   ├── 500.html              # 500 错误页
│   └── auth/
│       └── login.html        # 登录页面
│
├── data/                      # 数据目录（运行时创建）
│   └── cpa_manager.db        # SQLite 数据库
│
└── pool/                      # 临时文件目录（运行时创建）
    └── *.zip                 # 下载的账号包
```

## 核心模块说明

### app.py
Flask 应用主入口，负责：
- 初始化 Flask 应用
- 配置 Flask-Login
- 注册路由蓝图
- 启动定时任务调度器
- 错误处理

### utils/db_service.py
数据库服务模块，提供：
- 数据库初始化
- 认证文件备份
- 同步日志记录
- 审计日志记录
- 统计数据管理

### utils/cpa_client.py
CPA API 客户端，实现：
- 获取认证文件列表
- 下载/上传认证文件
- 启用/禁用账号
- 检查使用情况
- Token 复活功能

### utils/config_manager.py
配置管理器，负责：
- 加载/保存配置文件
- 服务器配置管理
- 系统设置管理

### utils/scheduler.py
定时任务调度器，支持：
- 自动同步任务
- 数据库清理任务
- 自定义定时任务

### routes/
路由蓝图模块，按功能划分：
- **auth.py**: 用户登录/登出
- **servers.py**: 服务器增删改查
- **accounts.py**: 账号管理操作
- **operations.py**: 批量下载/上传
- **stats.py**: 统计信息查询
- **sync.py**: 数据同步备份
- **tasks.py**: 定时任务管理

### templates/
HTML 模板文件：
- **base.html**: 基础布局（侧边栏、导航）
- **dashboard.html**: 仪表板页面
- **auth/login.html**: 登录页面
- **404.html / 500.html**: 错误页面

## 数据库表结构

### auth_files_backup
存储认证文件备份

### config_backups
存储配置文件备份

### sync_logs
记录同步操作日志

### scheduled_tasks
定时任务配置

### task_executions
任务执行历史

### audit_logs
操作审计日志

### system_stats
系统统计数据

## API 端点

### 认证
- `POST /auth/login` - 登录
- `GET /auth/logout` - 登出

### 服务器管理
- `GET /api/servers/` - 获取服务器列表
- `POST /api/servers/` - 添加服务器
- `PUT /api/servers/<id>` - 更新服务器
- `DELETE /api/servers/<id>` - 删除服务器
- `POST /api/servers/<id>/test` - 测试连接

### 账号管理
- `GET /api/accounts/<server_id>` - 获取账号列表
- `POST /api/accounts/<server_id>/check-usage` - 检查使用情况
- `POST /api/accounts/<server_id>/<filename>/disable` - 禁用账号
- `POST /api/accounts/<server_id>/<filename>/enable` - 启用账号
- `POST /api/accounts/<server_id>/<filename>/revive` - 复活 Token

### 批量操作
- `POST /api/operations/<server_id>/download` - 批量下载
- `POST /api/operations/<server_id>/upload` - 批量上传
- `POST /api/operations/<server_id>/batch-revive` - 批量复活

### 统计信息
- `GET /api/stats/dashboard` - 仪表板统计
- `GET /api/stats/server/<server_id>` - 服务器统计

### 同步备份
- `POST /api/sync/<server_id>/auth-files` - 同步认证文件
- `GET /api/sync/logs` - 获取同步日志

## 配置文件

### config.json
```json
{
  "cpa_servers": [
    {
      "id": "唯一标识",
      "name": "服务器名称",
      "base_url": "CPA 服务器地址",
      "token": "管理令牌",
      "enable_token_revive": true,
      "enabled": true
    }
  ],
  "settings": {
    "max_workers": 10,
    "auto_sync_interval": 3600,
    "token_revive_max_attempts": 3
  }
}
```

### .env
```env
FLASK_ENV=production
SECRET_KEY=随机密钥
ADMIN_USERNAME=admin
ADMIN_PASSWORD=密码
HOST=0.0.0.0
PORT=5000
DATABASE_PATH=data/cpa_manager.db
```

## 部署流程

### Docker 部署
1. 编辑 `config.json` 和 `.env`
2. 运行 `docker-compose up -d`
3. 访问 http://localhost:5000

### 本地部署
1. 运行 `setup.sh` 或 `setup.bat`
2. 编辑 `config.json` 和 `.env`
3. 运行 `run.sh` 或 `run.bat`
4. 访问 http://localhost:5000

## 开发建议

### 添加新功能
1. 在 `routes/` 创建新的蓝图
2. 在 `app.py` 注册蓝图
3. 在 `templates/` 添加对应模板
4. 更新 API 文档

### 数据库迁移
1. 修改 `utils/db_service.py` 中的表结构
2. 删除 `data/cpa_manager.db`
3. 重启应用自动创建新表

### 添加定时任务
1. 在 `utils/scheduler.py` 添加任务函数
2. 使用装饰器配置执行时间
3. 重启应用生效
