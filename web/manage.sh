#!/bin/bash

set -e

COMMAND="${1:-}"

show_help() {
    cat << EOF
==========================================
  CPA 账号管理系统 - Web 版
==========================================

用法: ./manage.sh [命令]

命令:
  setup    初始化环境（首次使用）
  start    启动服务
  help     显示帮助

示例:
  ./manage.sh setup    # 首次安装
  ./manage.sh start    # 启动服务

EOF
}

setup() {
    echo "=========================================="
    echo "  初始化环境"
    echo "=========================================="
    echo ""

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ 未找到 Python 3，请先安装 Python 3.8+"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ 检测到 Python $PYTHON_VERSION"
    echo ""

    # 创建虚拟环境
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv

    # 激活虚拟环境
    source .venv/bin/activate

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
    fi

    if [ ! -f ".env" ]; then
        echo "📝 创建环境变量文件..."
        cp .env.example .env
    fi

    echo ""
    echo "=========================================="
    echo "  ✅ 安装完成！"
    echo "=========================================="
    echo ""
    echo "下一步:"
    echo "  1. 编辑 config.json 添加 CPA 服务器"
    echo "  2. 编辑 .env 修改管理员密码"
    echo "  3. 运行: ./manage.sh start"
    echo ""
    echo "访问地址: http://localhost:5000"
    echo "默认账号: admin / admin123"
    echo ""
}

start() {
    echo "=========================================="
    echo "  启动服务"
    echo "=========================================="
    echo ""

    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo "❌ 虚拟环境不存在，请先运行: ./manage.sh setup"
        exit 1
    fi

    # 激活虚拟环境
    source .venv/bin/activate

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
    echo "🚀 启动中..."
    echo ""
    echo "访问地址: http://localhost:5000"
    echo "默认账号: admin / admin123"
    echo ""
    echo "按 Ctrl+C 停止服务"
    echo ""
    python app.py
}

case "$COMMAND" in
    setup)
        setup
        ;;
    start)
        start
        ;;
    help|"")
        show_help
        ;;
    *)
        echo "❌ 未知命令: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac
