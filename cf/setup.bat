@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 CPA Manager - Cloudflare 部署向导
echo ====================================
echo.

REM 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 未找到 Node.js，请先安装 Node.js 16.13.0 或更高版本
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js 版本: %NODE_VERSION%

REM 检查 npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 未找到 npm
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo ✅ npm 版本: %NPM_VERSION%
echo.

REM 安装依赖
echo 📦 安装依赖...
call npm install

if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装成功
echo.

REM 检查 Wrangler
where wrangler >nul 2>nul
if %errorlevel% neq 0 (
    echo 📥 安装 Wrangler CLI...
    call npm install -g wrangler
)

for /f "tokens=*" %%i in ('wrangler --version') do set WRANGLER_VERSION=%%i
echo ✅ Wrangler 版本: %WRANGLER_VERSION%
echo.

REM 登录 Cloudflare
echo 🔐 登录 Cloudflare...
echo 提示：这将打开浏览器，请登录你的 Cloudflare 账号
pause

call wrangler login

if %errorlevel% neq 0 (
    echo ❌ 登录失败
    pause
    exit /b 1
)

echo ✅ 登录成功
echo.

REM 创建 KV 命名空间
echo 📦 创建 KV 命名空间...
echo 正在创建 ACCOUNTS 命名空间...

call wrangler kv:namespace create "ACCOUNTS" > kv_output.txt 2>&1
type kv_output.txt

REM 提取 KV ID（简化版，可能需要手动）
echo.
echo ⚠️  请手动复制上面输出中的 KV ID
echo 并更新 wrangler.toml 文件中的 your-kv-namespace-id
echo.
pause

del kv_output.txt

REM 设置管理员凭证
echo 🔑 设置管理员凭证...
echo.

set /p ADMIN_USER="请输入管理员用户名 (默认: admin): "
if "%ADMIN_USER%"=="" set ADMIN_USER=admin

set /p ADMIN_PASS="请输入管理员密码: "

if "%ADMIN_PASS%"=="" (
    echo ❌ 密码不能为空
    pause
    exit /b 1
)

REM 设置 Secret
echo %ADMIN_USER% | wrangler secret put ADMIN_USERNAME
echo %ADMIN_PASS% | wrangler secret put ADMIN_PASSWORD

echo ✅ 管理员凭证设置成功
echo.

REM 询问是否部署
echo 📋 配置完成！
echo.
echo 下一步：
echo   1. 本地测试: npm run dev
echo   2. 部署到生产: npm run deploy
echo.

set /p DEPLOY_NOW="是否现在部署到生产环境？(y/n): "

if /i "%DEPLOY_NOW%"=="y" (
    echo.
    echo 🚀 开始部署...
    call npm run deploy
    
    if %errorlevel% equ 0 (
        echo.
        echo ✅ 部署成功！
        echo.
        echo 🎉 你的 CPA Manager 已经部署完成！
        echo.
        echo 访问你的应用：
        echo   https://cpa-manager.your-subdomain.workers.dev
        echo.
        echo 登录凭证：
        echo   用户名: %ADMIN_USER%
        echo   密码: ********
        echo.
        echo 下一步：
        echo   - 配置自定义域名（可选）
        echo   - 添加 CPA 服务器
        echo   - 开始管理账号
        echo.
    ) else (
        echo ❌ 部署失败，请查看错误信息
        pause
        exit /b 1
    )
) else (
    echo.
    echo ✅ 配置完成！
    echo.
    echo 本地测试：
    echo   npm run dev
    echo.
    echo 部署到生产：
    echo   npm run deploy
    echo.
)

echo 📚 更多信息请查看 README.md 和 DEPLOY.md
echo.
echo 祝使用愉快！ 🎉
pause
