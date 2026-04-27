@echo off
chcp 65001 >nul
setlocal

set "COMMAND=%~1"

if "%COMMAND%"=="" (
    call :show_help
    exit /b 0
)

if /i "%COMMAND%"=="setup" (
    call :setup
    exit /b %errorlevel%
)

if /i "%COMMAND%"=="start" (
    call :start
    exit /b %errorlevel%
)

if /i "%COMMAND%"=="help" (
    call :show_help
    exit /b 0
)

echo ❌ 未知命令: %COMMAND%
echo.
call :show_help
exit /b 1

:show_help
echo ==========================================
echo   CPA 账号管理系统 - Web 版
echo ==========================================
echo.
echo 用法: manage.bat [命令]
echo.
echo 命令:
echo   setup    初始化环境（首次使用）
echo   start    启动服务
echo   help     显示帮助
echo.
echo 示例:
echo   manage.bat setup    # 首次安装
echo   manage.bat start    # 启动服务
echo.
exit /b 0

:setup
echo ==========================================
echo   初始化环境
echo ==========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.8+
    exit /b 1
)
echo ✅ 检测到 Python
echo.

REM 创建虚拟环境
echo 📦 创建虚拟环境...
python -m venv .venv

REM 激活虚拟环境
call .venv\Scripts\activate.bat

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
)

if not exist ".env" (
    echo 📝 创建环境变量文件...
    copy .env.example .env
)

echo.
echo ==========================================
echo   ✅ 安装完成！
echo ==========================================
echo.
echo 下一步:
echo   1. 编辑 config.json 添加 CPA 服务器
echo   2. 编辑 .env 修改管理员密码
echo   3. 运行: manage.bat start
echo.
echo 访问地址: http://localhost:5000
echo 默认账号: admin / admin123
echo.
exit /b 0

:start
echo ==========================================
echo   启动服务
echo ==========================================
echo.

REM 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ 虚拟环境不存在，请先运行: manage.bat setup
    exit /b 1
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 检查配置文件
if not exist "config.json" (
    echo ⚠️  配置文件不存在，使用示例配置
    copy config.json.example config.json
)

if not exist ".env" (
    echo ⚠️  环境变量文件不存在，使用示例配置
    copy .env.example .env
)

REM 启动应用
echo 🚀 启动中...
echo.
echo 访问地址: http://localhost:5000
echo 默认账号: admin / admin123
echo.
echo 按 Ctrl+C 停止服务
echo.
python app.py
exit /b %errorlevel%
