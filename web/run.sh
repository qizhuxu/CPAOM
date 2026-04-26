#!/bin/bash

echo "启动 CPA 账号管理系统..."
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行 setup.sh"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "⚠️  配置文件不存在，使用示例配置"
    cp config.json.example config.json
fi

if [ ! -f ".env" ]; then
    echo "⚠️  环境变量文件不存在，使用示例配置"
    cp .env.example .env
fi

# 启动应用
python app.py
