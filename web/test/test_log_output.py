#!/usr/bin/env python3
"""
测试日志输出脚本
验证日志既能在终端显示，又能推送到 Web 界面
"""

import time
import logging
import requests
from threading import Thread

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_logger')

def test_console_logs():
    """测试控制台日志输出"""
    print("=" * 60)
    print("测试控制台日志输出")
    print("=" * 60)
    
    logger.info("这是一条 INFO 级别的测试日志")
    logger.warning("这是一条 WARNING 级别的测试日志")
    logger.error("这是一条 ERROR 级别的测试日志")
    
    print("如果你能在终端看到上面的日志，说明控制台输出正常")

def test_web_logs():
    """测试 Web 日志接口"""
    print("\n" + "=" * 60)
    print("测试 Web 日志接口")
    print("=" * 60)
    
    try:
        # 测试历史日志接口
        response = requests.get('http://localhost:5000/api/logs/history', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 历史日志接口正常，获取到 {data.get('total', 0)} 条日志")
        else:
            print(f"✗ 历史日志接口异常: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ 无法连接到 Web 服务: {e}")
        print("请确保 Web 应用正在运行 (python app.py)")

def simulate_user_actions():
    """模拟用户操作产生日志"""
    print("\n" + "=" * 60)
    print("模拟用户操作产生日志")
    print("=" * 60)
    
    actions = [
        "用户访问仪表板",
        "查看服务器列表", 
        "检查账号使用情况",
        "执行批量操作",
        "同步认证文件"
    ]
    
    for i, action in enumerate(actions, 1):
        logger.info(f"[{i}/{len(actions)}] {action}")
        time.sleep(1)
    
    logger.info("所有模拟操作完成")

def monitor_log_stream():
    """监控日志流"""
    print("\n" + "=" * 60)
    print("监控日志流 (5秒)")
    print("=" * 60)
    print("请在浏览器中打开 http://localhost:5000 -> 系统日志")
    print("你应该能看到实时的日志更新")
    
    # 持续产生日志
    for i in range(5):
        logger.info(f"实时日志测试 {i+1}/5")
        time.sleep(1)

def main():
    """主函数"""
    print("日志功能测试")
    print("请确保 Web 应用正在运行: python app.py")
    print()
    
    # 测试控制台输出
    test_console_logs()
    
    # 测试 Web 接口
    test_web_logs()
    
    # 模拟用户操作
    simulate_user_actions()
    
    # 监控日志流
    monitor_log_stream()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("检查要点:")
    print("1. 终端中应该能看到所有测试日志")
    print("2. Web 界面的系统日志页面应该显示相同的日志")
    print("3. 日志应该实时更新（无需刷新页面）")

if __name__ == '__main__':
    main()