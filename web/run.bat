@echo off
chcp 65001 >nul
echo 启动 CPA 账号管理系统...
echo.

REM 激活虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ❌ 虚拟环境不存在，请先运行 setup.bat
    pause
    exit /b 1
)

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
python app.py
