"""
测试定时任务调度器
"""

import os
import sys
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from utils.db_service import DatabaseService
from utils.config_manager import ConfigManager
from utils.scheduler import init_scheduler, get_all_jobs
from dotenv import load_dotenv

load_dotenv()


def test_scheduler():
    """测试调度器"""
    print("=" * 60)
    print("测试定时任务调度器")
    print("=" * 60)
    
    # 创建 Flask 应用
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'data/cpa_manager.db')
    
    # 初始化服务
    db_service = DatabaseService(app.config['DATABASE_PATH'])
    config_manager = ConfigManager()
    
    print("\n1. 初始化调度器...")
    scheduler = init_scheduler(app, db_service, config_manager)
    print("   ✓ 调度器已启动")
    
    print("\n2. 查看已加载的任务...")
    jobs = get_all_jobs()
    
    if not jobs:
        print("   - 没有任务（可能没有配置服务器或同步配置）")
    else:
        for job in jobs:
            print(f"   - {job['name']} (ID: {job['id']})")
            print(f"     下次运行: {job['next_run_time']}")
    
    print("\n3. 等待 5 秒观察日志...")
    time.sleep(5)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("\n提示：")
    print("  - 如果没有任务，请先添加服务器并配置同步")
    print("  - 查看日志确认任务是否正常执行")
    print()


if __name__ == '__main__':
    test_scheduler()
