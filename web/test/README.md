# 测试脚本

Web 版 CPA 管理系统的测试脚本集合。

## 测试脚本列表

### quick_test.py ⭐ 推荐

快速验证日志系统是否正常工作的脚本。

**功能:**
- 验证应用模块导入
- 测试日志系统初始化
- 发送测试日志消息

**使用方法:**

```bash
cd test
python quick_test.py
```

**预期结果:**
- 终端显示测试日志消息
- 无错误信息

### test_logs.py

测试日志功能的脚本，用于验证日志流是否正常工作。

**功能:**
- 测试不同日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 测试不同内容的日志
- 测试连续日志输出
- 测试多行日志
- 测试中文日志

**使用方法:**

```bash
# 1. 启动 Web 应用
cd ..
python app.py

# 2. 在另一个终端运行测试
cd test
python test_logs.py
```

### test_log_output.py

测试日志双输出功能的脚本，验证日志既能在终端显示，又能推送到 Web 界面。

**功能:**
- 验证控制台日志输出
- 测试 Web 日志接口
- 模拟用户操作产生日志
- 监控实时日志流

**使用方法:**

```bash
# 1. 启动 Web 应用
cd ..
python app.py

# 2. 在另一个终端运行测试
cd test
python test_log_output.py
```

**预期结果:**
- 终端中能看到所有测试日志
- Web 界面的"系统日志"页面显示相同日志
- 日志实时更新（无需刷新页面）

### generate_test_logs.py

生成各种测试日志的脚本，用于验证日志流的实时显示效果。

**功能:**
- 通过应用模块生成日志
- 通过 Python logging 生成日志
- 模拟用户操作产生 HTTP 请求日志
- 生成不同级别和类型的日志

**使用方法:**

```bash
# 1. 启动 Web 应用
cd ..
python app.py
# 或使用启动脚本
start_with_logs.bat  # Windows
./start_with_logs.sh # Linux/macOS

# 2. 在另一个终端生成测试日志
cd test
..\\.venv\\Scripts\\activate  # Windows
# 或 source ../.venv/bin/activate  # Linux/macOS
python generate_test_logs.py
```

**预期结果:**
- 终端显示各种测试日志
- Web 界面实时显示相同日志
- 不同级别显示不同颜色

## 运行所有测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
python -m pytest test/ -v

# 生成覆盖率报告
python -m pytest --cov=. test/
```

## 添加新测试

创建新的测试文件时，请遵循以下命名规范：

- 文件名：`test_<功能名>.py`
- 测试函数：`test_<具体功能>()`
- 测试类：`Test<功能名>`

示例：

```python
# test_api.py
import unittest
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
    
    def test_login_required(self):
        """测试需要登录的端点"""
        response = self.app.get('/api/servers/')
        self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()
```

## 测试环境

测试脚本使用独立的测试环境，不会影响生产数据：

- 测试数据库：`:memory:` (内存数据库)
- 测试配置：`test_config.json`
- 测试日志：输出到控制台

## 持续集成

项目使用 GitHub Actions 进行自动化测试：

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest test/ --cov=.
```

## 性能测试

使用 `locust` 进行性能测试：

```python
# test_performance.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # 登录
        self.client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
    
    @task
    def view_dashboard(self):
        self.client.get("/")
    
    @task
    def get_servers(self):
        self.client.get("/api/servers/")
    
    @task
    def get_stats(self):
        self.client.get("/api/stats/dashboard")
```

运行性能测试：

```bash
pip install locust
locust -f test/test_performance.py --host=http://localhost:5000
```

## 故障排除

### 测试失败常见原因

1. **端口占用**: 确保 5000 端口未被占用
2. **依赖缺失**: 运行 `pip install -r requirements.txt`
3. **权限问题**: 确保有写入 `data/` 目录的权限
4. **配置错误**: 检查 `config.json` 格式是否正确

### 调试测试

```python
# 在测试中添加调试信息
import logging
logging.basicConfig(level=logging.DEBUG)

# 或使用 pdb 调试器
import pdb; pdb.set_trace()
```

### 清理测试数据

```bash
# 清理测试生成的文件
rm -rf data/test_*.db
rm -rf pool/test_*.zip
```


### test_threaded_sse.py ⭐ 新增 - 并发测试

测试 SSE 日志流在多线程模式下的并发性能，验证日志流不会阻塞其他功能。

**功能:**
- 测试基本 SSE 连接
- 验证 SSE 连接期间其他 API 请求不被阻塞
- 测试多个并发 SSE 连接
- 确认多线程模式正常工作

**使用方法:**

```bash
# 1. 启动 Web 应用（必须启用 threaded=True）
cd ..
python app.py

# 2. 在另一个终端运行测试
cd test
..\\.venv\\Scripts\\activate  # Windows
# 或 source ../.venv/bin/activate  # Linux/macOS
python test_threaded_sse.py
```

**预期结果:**
- ✓ SSE 流测试完成，接收多条日志
- ✓ 并发测试通过，所有 API 请求成功
- ✓ 多连接测试通过，3个连接同时工作

**如果测试失败:**
- 检查 `app.py` 中是否使用 `app.run(threaded=True)`
- 确认没有其他进程占用 5000 端口
- 查看终端日志了解详细错误信息


### init_system.py ⭐ 系统初始化

系统初始化脚本，执行数据库迁移和配置初始化。

**功能:**
- 初始化数据库表结构
- 运行数据库迁移（扩展表以支持增强同步）
- 为所有服务器创建默认同步配置

**使用方法:**

```bash
cd test
python init_system.py
```

**预期结果:**
- ✓ 数据库初始化完成
- ✓ 迁移完成（或跳过已迁移的表）
- ✓ 为每个服务器创建默认同步配置


### test_accounts_fix.py

测试账号路由修复，验证 db_service 是否正确导入。

**功能:**
- 验证 db_service 已导入
- 验证 config_manager 已导入
- 验证账号路由已注册

**使用方法:**

```bash
cd test
python test_accounts_fix.py
```


### test_check_usage_fix.py ⭐ 新增

测试批量检查使用情况修复，验证 logger 作用域问题是否解决。

**功能:**
- 验证 logger 已导入
- 验证使用独立函数而不是闭包
- 验证没有使用 nonlocal（避免作用域问题）
- 验证所有变量通过参数传递

**使用方法:**

```bash
cd test
python test_check_usage_fix.py
```

**预期结果:**
- ✓ logger 已导入
- ✓ 使用独立函数（避免闭包问题）
- ✓ 没有使用 nonlocal（避免作用域问题）
- ✓ 通过参数传递所有变量


### test_scheduler.py ⭐ 调度器测试

测试定时任务调度器是否正常工作。

**功能:**
- 验证调度器启动
- 检查已加载的同步任务
- 显示任务下次运行时间

**使用方法:**

```bash
cd test
python test_scheduler.py
```

**预期结果:**
- ✓ 调度器已启动
- 显示所有已加载的同步任务
- 显示每个任务的下次运行时间

**注意:**
- 如果没有任务，请先添加服务器并配置同步
- 任务会根据配置的间隔自动执行


### migrate_db.py - 数据库迁移

扩展数据库表结构以支持增强同步功能。

**功能:**
- 扩展 `auth_files_backup` 表（添加使用量、禁用原因等字段）
- 创建 `server_sync_config` 表（同步配置）
- 创建 `server_stats` 表（服务器统计）
- 扩展 `sync_logs` 表（添加维护操作计数）

**使用方法:**

```bash
cd test
python migrate_db.py
```

**预期结果:**
- ✓ 所有表迁移完成
- 或显示"已存在，跳过"（如果已迁移）


## 重要说明：SSE 日志流与多线程

### 问题背景

Flask 开发服务器默认是**单线程**的，这意味着：
- 当建立 SSE 长连接时，会阻塞整个服务器
- 其他 API 请求无法处理
- 浏览器会卡死，Ctrl+C 无响应

### 解决方案

在 `app.py` 中启用多线程模式：

```python
# 错误的方式（会导致阻塞）
app.run(host='0.0.0.0', port=5000, debug=True)

# 正确的方式（支持并发）
app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
```

### 生产环境建议

开发服务器不适合生产环境，建议使用专业的 WSGI 服务器：

**使用 Gunicorn (推荐):**

```bash
# 安装
pip install gunicorn

# 运行（4个工作进程，每个2个线程）
gunicorn -w 4 --threads 2 -b 0.0.0.0:5000 app:app

# 带日志
gunicorn -w 4 --threads 2 -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
```

**使用 uWSGI:**

```bash
# 安装
pip install uwsgi

# 运行
uwsgi --http 0.0.0.0:5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

### 验证多线程是否生效

运行 `test_threaded_sse.py` 测试脚本：

```bash
python test/test_threaded_sse.py
```

如果看到以下输出，说明多线程工作正常：

```
✓ 登录成功
✓ SSE 流测试完成，共接收 X 条日志
  ✓ Health Check: 200 (0.05s)
  ✓ Get Servers: 200 (0.08s)
  ✓ Get Stats: 200 (0.12s)
  ✓ Get Log History: 200 (0.06s)
  并发测试结果: 4/4 成功
✓ 所有测试通过！
```

如果测试失败，检查：
1. `app.py` 是否使用 `threaded=True`
2. 是否有其他错误日志
3. 端口是否被占用
