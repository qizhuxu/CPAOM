# 开发指南

CPA 账号管理系统 Web 版开发环境搭建和贡献指南。

## 开发环境搭建

### 系统要求

- Python 3.8+
- Git
- 文本编辑器 (VS Code 推荐)

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/qizhuxu/CPAOM.git
cd CPAOM/web

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 复制配置文件
cp config.json.example config.json
cp .env.example .env

# 6. 启动开发服务器
python app.py
```

### 验证安装

访问 http://localhost:5000，应该看到登录页面。

默认账号：`admin` / `admin123`

### 开发工具推荐

**VS Code 扩展：**
- Python
- Flask Snippets
- SQLite Viewer
- REST Client

**Chrome 扩展：**
- JSON Formatter
- React Developer Tools (用于调试)

## 项目结构

```
web/
├── app.py                 # Flask 应用入口
├── requirements.txt       # Python 依赖
├── config.json           # 服务器配置 (运行时)
├── .env                  # 环境变量 (运行时)
├── routes/               # API 路由模块
│   ├── __init__.py
│   ├── auth.py          # 用户认证
│   ├── servers.py       # 服务器管理
│   ├── accounts.py      # 账号管理
│   ├── operations.py    # 批量操作
│   ├── stats.py         # 统计信息
│   ├── sync.py          # 数据同步
│   ├── tasks.py         # 定时任务
│   ├── local_accounts.py # 本地账号
│   └── logs.py          # 系统日志
├── utils/                # 工具模块
│   ├── __init__.py
│   ├── config_manager.py # 配置管理
│   ├── cpa_client.py    # CPA API 客户端
│   ├── db_service.py    # 数据库服务
│   └── scheduler.py     # 任务调度
├── templates/            # HTML 模板
│   ├── base.html        # 基础模板
│   ├── dashboard.html   # 仪表板
│   ├── 404.html         # 404 页面
│   ├── 500.html         # 500 页面
│   └── auth/
│       └── login.html   # 登录页面
├── docs/                 # 项目文档
├── test/                 # 测试脚本
├── data/                 # 数据文件 (运行时创建)
│   └── cpa_manager.db   # SQLite 数据库
└── pool/                 # 临时文件 (运行时创建)
```

## 代码规范

### Python 代码风格

遵循 PEP 8 规范：

```python
# 好的示例
def get_server_by_id(server_id: str) -> dict:
    """根据 ID 获取服务器配置
    
    Args:
        server_id: 服务器唯一标识
        
    Returns:
        服务器配置字典，不存在时返回 None
    """
    servers = config_manager.get_servers()
    return next((s for s in servers if s['id'] == server_id), None)

# 避免的写法
def getServer(id):
    servers=config_manager.get_servers()
    for s in servers:
        if s['id']==id:
            return s
    return None
```

### JavaScript 代码风格

```javascript
// 好的示例
async function loadAccounts() {
    const serverId = document.getElementById('accountsServerSelect').value;
    if (!serverId) {
        showToast('请先选择服务器', 'warning');
        return;
    }
    
    try {
        const result = await apiCall('GET', `/api/accounts/${serverId}`);
        displayAccounts(result.accounts);
    } catch (error) {
        showToast(`加载失败: ${error.message}`, 'danger');
    }
}

// 避免的写法
function loadAccounts(){
    var serverId=document.getElementById('accountsServerSelect').value;
    if(!serverId){
        alert('请先选择服务器');
        return;
    }
    // 使用 XMLHttpRequest 而不是 fetch/axios
}
```

### 命名规范

**Python:**
- 函数和变量：`snake_case`
- 类名：`PascalCase`
- 常量：`UPPER_CASE`
- 私有方法：`_private_method`

**JavaScript:**
- 函数和变量：`camelCase`
- 类名：`PascalCase`
- 常量：`UPPER_CASE`

**文件名:**
- Python 模块：`snake_case.py`
- HTML 模板：`kebab-case.html`
- 文档：`kebab-case.md`

## 数据库操作

### 添加新表

1. 在 `utils/db_service.py` 中添加表结构：

```python
def init_db(self):
    """初始化数据库表"""
    # 现有表...
    
    # 新表
    self.execute_query('''
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
```

2. 添加相关操作方法：

```python
def add_new_record(self, name: str) -> int:
    """添加新记录"""
    return self.execute_query(
        'INSERT INTO new_table (name) VALUES (?)',
        (name,)
    )

def get_new_records(self) -> List[dict]:
    """获取所有记录"""
    return self.execute_query('SELECT * FROM new_table ORDER BY created_at DESC')
```

### 数据库迁移

当需要修改表结构时：

```python
def migrate_database(self):
    """数据库迁移"""
    # 检查版本
    version = self.get_db_version()
    
    if version < 2:
        # 添加新列
        self.execute_query('ALTER TABLE accounts ADD COLUMN last_used TIMESTAMP')
        self.set_db_version(2)
```

## API 开发

### 添加新的 API 端点

1. 在相应的路由文件中添加端点：

```python
# routes/new_feature.py
from flask import Blueprint, request, jsonify
from flask_login import login_required
import logging

bp = Blueprint('new_feature', __name__, url_prefix='/api/new-feature')
logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
@login_required
def list_items():
    """获取项目列表"""
    try:
        # 业务逻辑
        items = get_items_from_db()
        
        logger.info(f"获取到 {len(items)} 个项目")
        
        return jsonify({
            'success': True,
            'items': items
        })
    except Exception as e:
        logger.error(f"获取项目列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/', methods=['POST'])
@login_required
def create_item():
    """创建新项目"""
    data = request.get_json()
    
    # 输入验证
    if not data or not data.get('name'):
        return jsonify({
            'success': False,
            'error': '缺少必要参数'
        }), 400
    
    try:
        item_id = create_item_in_db(data)
        logger.info(f"创建项目成功: {data['name']}")
        
        return jsonify({
            'success': True,
            'item_id': item_id
        })
    except Exception as e:
        logger.error(f"创建项目失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

2. 在 `app.py` 中注册蓝图：

```python
from routes import new_feature
app.register_blueprint(new_feature.bp)
```

### API 设计原则

1. **RESTful 设计**
   - GET: 获取资源
   - POST: 创建资源
   - PUT: 更新整个资源
   - PATCH: 部分更新
   - DELETE: 删除资源

2. **统一响应格式**
   ```json
   {
     "success": true,
     "data": {...},
     "message": "操作成功"
   }
   ```

3. **错误处理**
   ```json
   {
     "success": false,
     "error": "错误描述",
     "code": "ERROR_CODE"
   }
   ```

## 前端开发

### 添加新页面

1. 在 `base.html` 中添加导航：

```html
<a class="nav-link" href="#" onclick="showNewPage(); return false;">
    <i class="fas fa-new-icon"></i> 新功能
</a>
```

2. 添加页面函数：

```javascript
function showNewPage() {
    if (currentPage === 'new-page') return;
    currentPage = 'new-page';
    
    const content = document.querySelector('.main-content');
    content.innerHTML = `
        <div class="container-fluid">
            <h1 class="mb-4"><i class="fas fa-new-icon"></i> 新功能</h1>
            
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">功能面板</h5>
                </div>
                <div class="card-body">
                    <button class="btn btn-primary" onclick="performAction()">
                        执行操作
                    </button>
                </div>
            </div>
        </div>
    `;
}

async function performAction() {
    try {
        const result = await apiCall('POST', '/api/new-feature/');
        if (result.success) {
            showToast('操作成功', 'success');
        }
    } catch (error) {
        showToast(`操作失败: ${error.message}`, 'danger');
    }
}
```

### 前端工具函数

```javascript
// API 调用封装
async function apiCall(method, url, data = null) {
    const config = {
        method: method,
        url: url,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        config.data = data;
    }
    
    const response = await axios(config);
    return response.data;
}

// 消息提示
function showToast(message, type = 'success') {
    // 实现消息提示逻辑
}

// 表格渲染
function renderTable(data, columns) {
    // 实现表格渲染逻辑
}
```

## 测试

### 单元测试

创建测试文件 `test/test_api.py`：

```python
import unittest
import json
from app import app

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
    
    def test_login_required(self):
        """测试需要登录的端点"""
        response = self.app.get('/api/servers/')
        self.assertEqual(response.status_code, 302)  # 重定向到登录页

if __name__ == '__main__':
    unittest.main()
```

### 运行测试

```bash
# 运行所有测试
python -m pytest test/

# 运行特定测试
python -m pytest test/test_api.py

# 生成覆盖率报告
python -m pytest --cov=. test/
```

### 手动测试

使用 `test/test_logs.py` 测试日志功能：

```bash
# 启动应用
python app.py

# 在另一个终端运行测试
cd test
python test_logs.py
```

## 调试

### 启用调试模式

```bash
# 设置环境变量
export FLASK_ENV=development
export FLASK_DEBUG=1

# 或在 .env 文件中设置
FLASK_ENV=development
FLASK_DEBUG=1
```

### 日志调试

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 在代码中添加调试信息
logger.debug(f"处理请求: {request.method} {request.path}")
logger.info(f"用户操作: {current_user.username}")
```

### 前端调试

```javascript
// 在浏览器控制台查看 API 调用
console.log('API 请求:', method, url, data);
console.log('API 响应:', response);

// 查看日志流连接状态
console.log('EventSource 状态:', logEventSource.readyState);
```

## 部署

### 开发环境部署

```bash
# 直接运行
python app.py

# 使用 gunicorn (生产环境推荐)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker 部署

```bash
# 构建镜像
docker build -t cpaom-web .

# 运行容器
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data cpaom-web
```

## 贡献指南

### 提交代码

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -m "Add new feature"`
4. 推送分支：`git push origin feature/new-feature`
5. 创建 Pull Request

### 提交信息规范

```
type(scope): description

feat(api): 添加新的日志流 API
fix(ui): 修复账号列表显示问题
docs(readme): 更新安装说明
test(logs): 添加日志功能测试
```

### 代码审查

- 确保代码符合规范
- 添加必要的测试
- 更新相关文档
- 检查性能影响

## 常见问题

### Q: 如何添加新的 CPA 服务器？

A: 编辑 `config.json` 文件，或通过 Web 界面添加。

### Q: 数据库文件在哪里？

A: `data/cpa_manager.db`，首次运行时自动创建。

### Q: 如何重置管理员密码？

A: 修改 `.env` 文件中的 `ADMIN_PASSWORD`，重启应用。

### Q: 日志文件在哪里？

A: 当前版本使用内存日志，可通过 Web 界面查看和下载。

### Q: 如何备份数据？

A: 复制 `data/` 目录和 `config.json` 文件即可。

## 性能优化

### 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_local_accounts_email ON local_accounts(email);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);

-- 定期清理旧数据
DELETE FROM operation_logs WHERE created_at < datetime('now', '-30 days');
```

### 前端优化

```javascript
// 使用防抖避免频繁请求
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 搜索输入防抖
const debouncedSearch = debounce(performSearch, 300);
```

### 内存优化

```python
# 限制日志缓冲区大小
log_buffer = deque(maxlen=1000)

# 使用生成器处理大量数据
def process_large_dataset():
    for item in get_items_generator():
        yield process_item(item)
```

## 扩展开发

### 添加新的存储后端

```python
class StorageBackend:
    """存储后端接口"""
    
    def save_account(self, account_data):
        raise NotImplementedError
    
    def get_accounts(self, server_id):
        raise NotImplementedError

class RedisStorage(StorageBackend):
    """Redis 存储实现"""
    
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
    
    def save_account(self, account_data):
        # Redis 实现
        pass
```

### 添加新的认证方式

```python
class AuthProvider:
    """认证提供者接口"""
    
    def authenticate(self, username, password):
        raise NotImplementedError

class LDAPAuth(AuthProvider):
    """LDAP 认证实现"""
    
    def authenticate(self, username, password):
        # LDAP 实现
        pass
```