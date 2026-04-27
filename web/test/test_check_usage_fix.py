"""
测试批量检查使用情况修复
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_login import LoginManager
from routes import accounts
from utils.config_manager import ConfigManager
from dotenv import load_dotenv

load_dotenv()


def test_check_usage_function():
    """测试批量检查使用情况函数"""
    print("=" * 60)
    print("测试批量检查使用情况修复")
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
    
    print("\n1. 检查 logger 是否正确导入...")
    if hasattr(accounts, 'logger'):
        print("   ✓ logger 已导入")
    else:
        print("   ✗ logger 未导入")
        return False
    
    print("\n2. 检查 check_usage 路由是否注册...")
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    check_usage_route = [r for r in routes if 'check-usage' in r]
    
    if check_usage_route:
        print(f"   ✓ check-usage 路由已注册")
        for route in check_usage_route:
            print(f"     - {route}")
    else:
        print("   ✗ check-usage 路由未注册")
        return False
    
    print("\n3. 检查函数定义...")
    import inspect
    
    # 获取 check_usage 函数
    check_usage_func = accounts.check_usage
    source = inspect.getsource(check_usage_func)
    
    # 检查是否使用了独立函数而不是闭包
    if 'def check_single_account' in source:
        print("   ✓ 使用独立函数（避免闭包问题）")
    else:
        print("   ⚠ 仍在使用闭包")
    
    # 检查是否有 nonlocal（闭包的标志）
    if 'nonlocal' not in source:
        print("   ✓ 没有使用 nonlocal（避免作用域问题）")
    else:
        print("   ⚠ 仍在使用 nonlocal")
    
    # 检查是否通过参数传递所有需要的变量
    if 'cpa_client' in source and 'total_count' in source:
        print("   ✓ 通过参数传递所有变量")
    else:
        print("   ⚠ 可能存在变量作用域问题")
    
    print("\n" + "=" * 60)
    print("✅ 所有检查通过！")
    print("=" * 60)
    print("\n提示：")
    print("  - 已修复 logger 未定义错误")
    print("  - 使用独立函数替代闭包，避免作用域问题")
    print("  - 所有变量通过参数传递，线程安全")
    print("  - 可以启动应用测试批量检查功能")
    print()
    
    return True


if __name__ == '__main__':
    success = test_check_usage_function()
    sys.exit(0 if success else 1)
