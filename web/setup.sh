#!/bin/bash

echo "=========================================="
echo "  CPA 账号管理系统 - Web 版"
echo "  本地部署安装脚本"
echo "=========================================="
echo ""

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ 检测到 Python $PYTHON_VERSION"
echo ""

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p data
mkdir -p pool

# 复制配置文件
if [ ! -f "config.json" ]; then
    echo "📝 创建配置文件..."
    cp config.json.example config.json
    echo "⚠️  请编辑 config.json 添加您的 CPA 服务器配置"
fi

if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 修改管理员密码和密钥"
fi

echo ""
echo "=========================================="
echo "  ✅ 安装完成！"
echo "=========================================="
echo ""
echo "启动服务:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "或使用快捷脚本:"
echo "  ./run.sh"
echo ""
echo "访问地址: http://localhost:5000"
echo "默认账号: admin / admin123"
echo ""
echo "⚠️  首次使用前请:"
echo "  1. 编辑 config.json 添加 CPA 服务器"
echo "  2. 编辑 .env 修改管理员密码"
echo ""
