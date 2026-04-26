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