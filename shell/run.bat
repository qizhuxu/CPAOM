@echo off
chcp 65001 >nul
echo 正在激活虚拟环境...
call .venv\Scripts\activate.bat
echo.
python manage_accounts.py
echo.
echo 按任意键退出...
pause >nul
