#!/usr/bin/env python3
"""
生成测试日志脚本
在 Web 应用运行时产生各种测试日志，用于验证日志流功能
"""

import sys
import os
import time
import logging
import requests
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_web_app():
    """检查 Web 应用是否运行"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=3)
        return response.status_code == 200
    except:
        return False

def generate_app_logs():
    """通过应用模块生成日志"""
    try:
        from app import app
        
        print("通过应用模块生成日志...")
        
        # 各种级别的日志
        app.logger.debug("这是一条调试日志 - 通常在开发时使用")
        app.logger.info("用户执行了某个操作")
        app.logger.warning("检测到潜在问题，但不影响正常运行")
        app.logger.error("发生了错误，需要注意")
        
        # 模拟业务日志
        app.logger.info("用户登录成功: admin")
        app.logger.info("查看服务器列表")
        app.logger.info("添加新服务器: 测试服务器")
        app.logger.warning("服务器连接超时，正在重试...")
        app.logger.info("服务器连接成功")
        
        # 模拟错误场景
        app.logger.error("无法连接到 CPA 服务器: Connection refused")
        app.logger.warning("Token 即将过期，建议刷新")
        app.logger.info("Token 刷新成功")
        
        print("✓ 应用日志生成完成")
        
    except Exception as e:
        print(f"✗ 生成应用日志失败: {e}")

def generate_python_logs():
    """通过 Python logging 生成日志"""
    print("通过 Python logging 生成日志...")
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('test_generator')
    
    # 生成各种日志
    logger.info("开始批量操作...")
    
    for i in range(5):
        logger.info(f"处理账号 {i+1}/5: user{i+1}@example.com")
        time.sleep(0.5)
    
    logger.warning("发现 2 个账号使用率超过 80%")
    logger.info("批量操作完成")
    logger.error("某个操作失败，但不影响整体流程")
    
    print("✓ Python 日志生成完成")

def simulate_user_actions():
    """模拟用户操作产生日志"""
    if not check_web_app():
        print("✗ Web 应用未运行，跳过 API 测试")
        return
    
    print("模拟用户操作...")
    
    try:
        # 模拟 API 调用（这些会产生 werkzeug 日志）
        requests.get('http://localhost:5000/', timeout=3)
        requests.get('http://localhost:5000/api/stats/dashboard', timeout=3)
        requests.get('http://localhost:5000/api/servers/', timeout=3)
        
        print("✓ 用户操作模拟完成")
        
    except Exception as e:
        print(f"✗ 模拟用户操作失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("测试日志生成器")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if check_web_app():
        print("✓ Web 应用正在运行")
    else:
        print("⚠ Web 应用未运行，某些测试将跳过")
    
    print()
    
    # 生成各种类型的日志
    generate_app_logs()
    print()
    
    generate_python_logs()
    print()
    
    simulate_user_actions()
    print()
    
    print("=" * 60)
    print("日志生成完成！")
    print("=" * 60)
    print("请在 Web 界面的'系统日志'页面查看这些日志")
    print("你应该能看到：")
    print("- 不同颜色的日志级别")
    print("- 实时更新的日志流")
    print("- 完整的时间戳和模块信息")

if __name__ == '__main__':
    main()