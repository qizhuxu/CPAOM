@echo off
echo 启动 CPA Web 管理系统...
echo.

REM 激活虚拟环境
call .venv\Scripts\activate

REM 启动应用
echo 应用启动中，请在浏览器中访问 http://localhost:5000
echo 要测试日志功能，请：
echo 1. 登录系统（admin/admin123）
echo 2. 点击侧边栏的"系统日志"
echo 3. 观察实时日志更新
echo.

python app.py