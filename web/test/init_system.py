"""
系统初始化脚本
1. 运行数据库迁移
2. 为所有服务器创建默认同步配置
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.db_service import DatabaseService
from utils.config_manager import ConfigManager
from dotenv import load_dotenv

load_dotenv()


def init_system():
    """初始化系统"""
    print("=" * 60)
    print("CPA 账号管理系统 - 系统初始化")
    print("=" * 60)
    
    # 1. 初始化数据库
    print("\n1. 初始化数据库...")
    db_path = os.getenv('DATABASE_PATH', 'data/cpa_manager.db')
    db_service = DatabaseService(db_path)
    db_service.init_db()
    print("   ✓ 数据库初始化完成")
    
    # 2. 运行迁移
    print("\n2. 运行数据库迁移...")
    try:
        from migrate_db import migrate_database
        migrate_database(db_path)
    except Exception as e:
        print(f"   ⚠ 迁移警告: {e}")
    
    # 3. 为所有服务器创建默认同步配置
    print("\n3. 创建默认同步配置...")
    config_manager = ConfigManager()
    servers = config_manager.get_servers()
    
    if not servers:
        print("   - 没有配置服务器")
    else:
        for server in servers:
            server_id = server['id']
            server_name = server['name']
            
            # 检查是否已有配置
            existing_config = db_service.get_sync_config(server_id)
            
            if existing_config:
                print(f"   - {server_name}: 已有配置，跳过")
            else:
                # 创建默认配置
                db_service.save_sync_config(
                    server_id=server_id,
                    sync_interval=3600,  # 1小时
                    auto_disable_100_percent=False,
                    auto_disable_401=True,
                    auto_delete_401_files=False,
                    auto_enable_reset_accounts=False,
                    fetch_auth_content=True,
                    max_workers=10
                )
                print(f"   ✓ {server_name}: 已创建默认配置")
    
    print("\n" + "=" * 60)
    print("✅ 系统初始化完成！")
    print("=" * 60)
    print("\n提示：")
    print("  - 运行 'python app.py' 启动系统")
    print("  - 访问 http://localhost:5000")
    print("  - 默认账号: admin / admin")
    print()


if __name__ == '__main__':
    init_system()
