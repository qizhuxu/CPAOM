#!/bin/bash

# CPA Manager - Cloudflare 部署脚本

echo "🚀 CPA Manager - Cloudflare 部署向导"
echo "===================================="
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js 16.13.0 或更高版本"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ 未找到 npm"
    exit 1
fi

echo "✅ npm 版本: $(npm --version)"
echo ""

# 安装依赖
echo "📦 安装依赖..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装成功"
echo ""

# 检查 Wrangler
if ! command -v wrangler &> /dev/null; then
    echo "📥 安装 Wrangler CLI..."
    npm install -g wrangler
fi

echo "✅ Wrangler 版本: $(wrangler --version)"
echo ""

# 登录 Cloudflare
echo "🔐 登录 Cloudflare..."
echo "提示：这将打开浏览器，请登录你的 Cloudflare 账号"
read -p "按 Enter 继续..."

wrangler login

if [ $? -ne 0 ]; then
    echo "❌ 登录失败"
    exit 1
fi

echo "✅ 登录成功"
echo ""

# 创建 KV 命名空间
echo "📦 创建 KV 命名空间..."
echo "正在创建 ACCOUNTS 命名空间..."

KV_OUTPUT=$(wrangler kv:namespace create "ACCOUNTS" 2>&1)
echo "$KV_OUTPUT"

# 提取 KV ID
KV_ID=$(echo "$KV_OUTPUT" | grep -oP 'id = "\K[^"]+')

if [ -z "$KV_ID" ]; then
    echo "⚠️  无法自动提取 KV ID，请手动更新 wrangler.toml"
    echo "请将输出中的 ID 复制到 wrangler.toml 的 kv_namespaces 部分"
else
    echo "✅ KV 命名空间创建成功: $KV_ID"
    
    # 更新 wrangler.toml
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/id = \"your-kv-namespace-id\"/id = \"$KV_ID\"/" wrangler.toml
    else
        # Linux
        sed -i "s/id = \"your-kv-namespace-id\"/id = \"$KV_ID\"/" wrangler.toml
    fi
    
    echo "✅ wrangler.toml 已更新"
fi

echo ""

# 设置管理员凭证
echo "🔑 设置管理员凭证..."
echo ""

read -p "请输入管理员用户名 (默认: admin): " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-admin}

read -sp "请输入管理员密码: " ADMIN_PASS
echo ""

if [ -z "$ADMIN_PASS" ]; then
    echo "❌ 密码不能为空"
    exit 1
fi

# 设置 Secret
echo "$ADMIN_USER" | wrangler secret put ADMIN_USERNAME
echo "$ADMIN_PASS" | wrangler secret put ADMIN_PASSWORD

echo "✅ 管理员凭证设置成功"
echo ""

# 询问是否部署
echo "📋 配置完成！"
echo ""
echo "下一步："
echo "  1. 本地测试: npm run dev"
echo "  2. 部署到生产: npm run deploy"
echo ""

read -p "是否现在部署到生产环境？(y/n): " DEPLOY_NOW

if [ "$DEPLOY_NOW" = "y" ] || [ "$DEPLOY_NOW" = "Y" ]; then
    echo ""
    echo "🚀 开始部署..."
    npm run deploy
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 部署成功！"
        echo ""
        echo "🎉 你的 CPA Manager 已经部署完成！"
        echo ""
        echo "访问你的应用："
        echo "  https://cpa-manager.your-subdomain.workers.dev"
        echo ""
        echo "登录凭证："
        echo "  用户名: $ADMIN_USER"
        echo "  密码: ********"
        echo ""
        echo "下一步："
        echo "  - 配置自定义域名（可选）"
        echo "  - 添加 CPA 服务器"
        echo "  - 开始管理账号"
        echo ""
    else
        echo "❌ 部署失败，请查看错误信息"
        exit 1
    fi
else
    echo ""
    echo "✅ 配置完成！"
    echo ""
    echo "本地测试："
    echo "  npm run dev"
    echo ""
    echo "部署到生产："
    echo "  npm run deploy"
    echo ""
fi

echo "📚 更多信息请查看 README.md 和 DEPLOY.md"
echo ""
echo "祝使用愉快！ 🎉"
