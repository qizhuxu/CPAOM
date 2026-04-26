# 系统架构

CPA 账号管理系统 Web 版的技术架构和设计决策。

## 系统概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Flask App     │    │  CPA Servers    │
│                 │    │                 │    │                 │
│  - Bootstrap UI │◄──►│  - REST API     │◄──►│  - Auth Files   │
│  - JavaScript   │    │  - SQLite DB    │    │  - Usage API    │
│  - EventSource  │    │  - APScheduler  │    │  - Management   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   File System   │
                       │                 │
                       │  - Config JSON  │
                       │  - Log Files    │
                       │  - Pool Files   │
                       └─────────────────┘
```

## 技术栈选择

### 后端：Flask + SQLite

**为什么选择 Flask？**
- **轻量级**：相比 Django，Flask 更适合中小型项目
- **灵活性**：可以自由选择组件，不强制 ORM
- **快速开发**：简单的 API 开发，学习成本低
- **生态丰富**：Flask-Login、APScheduler 等扩展成熟

**为什么选择 SQLite？**
- **零配置**：无需单独安装数据库服务器
- **文件存储**：便于备份和迁移
- **性能足够**：对于中小规模数据完全够用
- **ACID 支持**：保证数据一致性

**替代方案考虑：**
- ❌ Django：过于重量级，ORM 复杂
- ❌ FastAPI：异步特性对此项目意义不大
- ❌ PostgreSQL：增加部署复杂度
- ❌ MySQL：配置复杂，SQLite 已足够

### 前端：Bootstrap + Vanilla JS

**为什么不用前端框架？**
- **简单性**：避免构建工具和复杂依赖
- **性能**：无需打包，直接加载
- **维护性**：减少技术栈复杂度
- **兼容性**：支持更多浏览器

**为什么选择 Bootstrap？**
- **响应式**：自动适配移动端
- **组件丰富**：表格、模态框、表单等
- **主题一致**：专业的视觉效果
- **文档完善**：易于使用和定制

## 核心组件

### 1. 配置管理 (ConfigManager)

```python
class ConfigManager:
    """统一配置管理"""
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def get_servers(self):
        """获取所有服务器配置"""
        return self.config.get("cpa_servers", [])
    
    def add_server(self, server):
        """添加服务器配置"""
        # 原子性写入，避免并发问题
```

**设计决策：**
- 使用 JSON 文件而非数据库存储配置
- 支持热重载配置
- 提供配置验证和默认值

### 2. CPA 客户端 (CPAClient)

```python
class CPAClient:
    """CPA 服务器 API 客户端"""
    
    def __init__(self, base_url, token, name):
        self.base_url = base_url
        self.token = token
        self.name = name
        self.session = requests.Session()
    
    def get_auth_files(self):
        """获取认证文件列表"""
        # 统一错误处理和重试机制
    
    def check_usage(self, auth_index):
        """检查账号使用情况"""
        # 返回标准化的使用数据
```

**设计决策：**
- 使用 requests.Session 复用连接
- 统一的错误处理和日志记录
- 支持超时和重试机制

### 3. 数据库服务 (DatabaseService)

```python
class DatabaseService:
    """SQLite 数据库操作"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def execute_query(self, query, params=None):
        """执行查询，自动处理连接"""
        # 连接池管理
        # 事务支持
        # 错误处理
```

**数据库设计：**
```sql
-- 本地账号备份表
CREATE TABLE local_accounts (
    id INTEGER PRIMARY KEY,
    server_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    email TEXT,
    auth_data TEXT,  -- JSON 格式存储
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 操作日志表
CREATE TABLE operation_logs (
    id INTEGER PRIMARY KEY,
    operation_type TEXT NOT NULL,
    server_id TEXT,
    details TEXT,  -- JSON 格式
    status TEXT,   -- success/error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 同步日志表
CREATE TABLE sync_logs (
    id INTEGER PRIMARY KEY,
    server_id TEXT NOT NULL,
    sync_type TEXT NOT NULL,
    file_count INTEGER,
    status TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. 任务调度 (APScheduler)

```python
def init_scheduler(app, db_service):
    """初始化定时任务"""
    scheduler = BackgroundScheduler()
    
    # 每小时检查 Token 状态
    scheduler.add_job(
        func=check_token_status,
        trigger="interval",
        hours=1,
        id='token_check'
    )
    
    # 每天凌晨 2 点备份数据
    scheduler.add_job(
        func=backup_data,
        trigger="cron",
        hour=2,
        id='daily_backup'
    )
```

**任务类型：**
- Token 自动复活
- 数据定期备份
- 清理过期日志
- 健康检查

### 5. 实时日志系统

```python
class LogHandler:
    """实时日志处理器"""
    
    def __init__(self):
        self.subscribers = []  # SSE 订阅者
        self.log_buffer = deque(maxlen=1000)  # 日志缓冲区
    
    def emit(self, record):
        """发送日志到所有订阅者"""
        # 格式化日志
        # 添加到缓冲区
        # 通知订阅者
```

**技术选择：Server-Sent Events (SSE)**
- **为什么不用 WebSocket？**
  - SSE 更简单，单向推送足够
  - 自动重连机制
  - 更好的防火墙兼容性
- **为什么不用轮询？**
  - 实时性更好
  - 减少服务器负载
  - 更好的用户体验

## 数据流

### 1. 用户操作流程

```
用户操作 → 前端 JS → Flask API → CPA 服务器
    ↓
前端更新 ← JSON 响应 ← 业务逻辑 ← API 响应
```

### 2. 批量操作流程

```
用户触发 → API 端点 → 创建后台任务
    ↓
ThreadPoolExecutor → 并发调用 CPA API
    ↓
结果汇总 → 更新数据库 → 返回前端
```

### 3. 日志流程

```
应用日志 → LogHandler → 日志缓冲区
    ↓
SSE 推送 → EventSource → 前端显示
```

## 安全考虑

### 1. 认证和授权
- Flask-Login 会话管理
- 密码哈希存储 (werkzeug.security)
- CSRF 保护 (Flask-WTF)

### 2. 数据保护
- 敏感配置环境变量存储
- Token 不记录到日志
- 数据库文件权限控制

### 3. API 安全
- 输入验证和清理
- SQL 注入防护 (参数化查询)
- 文件上传类型检查

## 性能优化

### 1. 并发处理
```python
# 使用线程池处理批量操作
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_account, acc) for acc in accounts]
    results = [future.result() for future in as_completed(futures)]
```

### 2. 缓存策略
- 服务器配置内存缓存
- 静态文件浏览器缓存
- API 响应适当缓存

### 3. 数据库优化
```sql
-- 关键字段索引
CREATE INDEX idx_local_accounts_server_id ON local_accounts(server_id);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);
```

## 部署架构

### Docker 部署
```dockerfile
FROM python:3.11-slim

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . /app
WORKDIR /app

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python", "app.py"]
```

### 目录结构
```
web/
├── app.py              # 应用入口
├── requirements.txt    # Python 依赖
├── config.json         # 服务器配置
├── .env               # 环境变量
├── routes/            # API 路由
├── utils/             # 工具模块
├── templates/         # HTML 模板
├── data/              # 数据文件 (运行时创建)
└── pool/              # 临时文件 (运行时创建)
```

## 扩展性考虑

### 1. 水平扩展
- 无状态设计，支持多实例
- 共享存储 (NFS/云存储)
- 负载均衡器分发请求

### 2. 功能扩展
- 插件化架构
- 事件驱动设计
- API 版本控制

### 3. 监控和运维
- 健康检查端点
- 指标收集 (Prometheus)
- 日志聚合 (ELK Stack)

## 已知限制

1. **单机部署**：当前版本不支持分布式部署
2. **SQLite 限制**：并发写入性能有限
3. **内存缓存**：重启后缓存丢失
4. **文件存储**：大文件可能影响性能

## 未来改进

- [ ] 支持 Redis 缓存
- [ ] 支持 PostgreSQL
- [ ] 添加 API 限流
- [ ] 实现插件系统
- [ ] 支持集群部署