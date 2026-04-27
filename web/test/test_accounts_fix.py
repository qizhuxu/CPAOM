"""
测试账号路由修复
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_login import LoginManager
from routes import accounts
from utils.db_service import DatabaseService
from utils.config_manager import ConfigManager
from dotenv import load_dotenv

load_dotenv()


def test_accounts_route():
    """测试账号路由"""
    print("=" * 60)
    print("测试账号路由修复")
    print("=" * 60)
    
    # 创建 Flask 应用
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'data/cpa_manager.db')
    app.config['TESTING'] = True
    
    # 初始化 Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(accounts.bp)
    
    print("\n1. 检查 db_service 是否正确导入...")
    if hasattr(accounts, 'db_service'):
        print("   ✓ db_service 已导入")
        print(f"   数据库路径: {accounts.db_service.db_path}")
    else:
        print("   ✗ db_service 未导入")
        return False
    
    print("\n2. 检查 config_manager 是否正确导入...")
    if hasattr(accounts, 'config_manager'):
        print("   ✓ config_manager 已导入")
    else:
        print("   ✗ config_manager 未导入")
        return False
    
    print("\n3. 检查路由是否注册...")
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    account_routes = [r for r in routes if '/api/accounts' in r]
    
    if account_routes:
        print(f"   ✓ 已注册 {len(account_routes)} 个账号路由")
        for route in account_routes:
            print(f"     - {route}")
    else:
        print("   ✗ 没有注册账号路由")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 所有检查通过！")
    print("=" * 60)
    print("\n提示：")
    print("  - db_service 已正确导入到 accounts.py")
    print("  - 可以启动应用测试账号列表功能")
    print()
    
    return True


if __name__ == '__main__':
    success = test_accounts_route()
    sys.exit(0 if success else 1)
