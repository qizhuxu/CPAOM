#!/usr/bin/env python3
"""
快速测试脚本
用于验证日志系统是否正常工作
"""

import sys
import os
import logging

# 添加父目录到路径，以便导入应用模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_logging_setup():
    """测试日志设置"""
    print("=" * 50)
    print("快速日志测试")
    print("=" * 50)
    
    # 导入应用
    try:
        from app import app
        from routes.logs import setup_logging
        
        print("✓ 成功导入应用模块")
        
        # 初始化日志系统
        setup_logging(app)
        print("✓ 日志系统初始化完成")
        
        # 测试日志输出
        app.logger.info("这是一条测试日志 - 应该同时在终端和 Web 界面显示")
        app.logger.warning("这是一条警告日志")
        app.logger.error("这是一条错误日志")
        
        print("✓ 测试日志已发送")
        print()
        print("如果你能在终端看到上面的日志消息，说明控制台输出正常")
        print("启动 Web 应用后，在'系统日志'页面应该能看到相同的日志")
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        print("请确保在 web 目录下运行此脚本")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

if __name__ == '__main__':
    test_logging_setup()