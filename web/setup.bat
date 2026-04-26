@echo off
chcp 65001 >nul
echo ==========================================
echo   CPA 账号管理系统 - Web 版
echo   本地部署安装脚本 (Windows)
echo ==========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo ✅ 检测到 Python
echo.

REM 创建虚拟环境
echo 📦 创建虚拟环境...
python -m venv venv

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖包...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 创建必要的目录
echo 📁 创建数据目录...
if not exist "data" mkdir data
if not exist "pool" mkdir pool

REM 复制配置文件
if not exist "config.json" (
    echo 📝 创建配置文件...
    copy config.json.example config.json
    echo ⚠️  请编辑 config.json 添加您的 CPA 服务器配置
)

if not exist ".env" (
    echo 📝 创建环境变量文件...
    copy .env.example .env
    echo ⚠️  请编辑 .env 修改管理员密码和密钥
)

echo.
echo ==========================================
echo   ✅ 安装完成！
echo ==========================================
echo.
echo 启动服务:
echo   run.bat
echo.
echo 访问地址: http://localhost:5000
echo 默认账号: admin / admin123
echo.
echo ⚠️  首次使用前请:
echo   1. 编辑 config.json 添加 CPA 服务器
echo   2. 编辑 .env 修改管理员密码
echo.
pause
