#!/usr/bin/env python3
"""
日志功能测试脚本
用于测试日志流是否正常工作
"""

import logging
import time
import sys

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('test_logs')

def test_log_levels():
    """测试不同日志级别"""
    print("开始测试日志级别...")
    
    logger.debug("这是一条 DEBUG 级别的日志")
    time.sleep(0.5)
    
    logger.info("这是一条 INFO 级别的日志")
    time.sleep(0.5)
    
    logger.warning("这是一条 WARNING 级别的日志")
    time.sleep(0.5)
    
    logger.error("这是一条 ERROR 级别的日志")
    time.sleep(0.5)
    
    logger.critical("这是一条 CRITICAL 级别的日志")
    time.sleep(0.5)

def test_log_content():
    """测试不同内容的日志"""
    print("开始测试日志内容...")
    
    logger.info("用户登录成功: admin")
    time.sleep(0.5)
    
    logger.info("服务器添加成功: test-server (ID: abc123)")
    time.sleep(0.5)
    
    logger.warning("Token 即将过期，建议刷新")
    time.sleep(0.5)
    
    logger.error("连接服务器失败: Connection timeout")
    time.sleep(0.5)
    
    logger.info("批量下载完成: 10 个账号")
    time.sleep(0.5)

def test_continuous_logs():
    """测试连续日志"""
    print("开始测试连续日志...")
    
    for i in range(10):
        logger.info(f"处理任务 {i+1}/10")
        time.sleep(0.3)
    
    logger.info("所有任务处理完成")

def test_multiline_logs():
    """测试多行日志"""
    print("开始测试多行日志...")
    
    error_message = """
    发生错误:
    - 错误类型: ConnectionError
    - 错误信息: Failed to connect to server
    - 服务器地址: https://example.com
    - 重试次数: 3
    """
    
    logger.error(error_message.strip())
    time.sleep(1)

def test_chinese_logs():
    """测试中文日志"""
    print("开始测试中文日志...")
    
    logger.info("系统启动成功 ✓")
    time.sleep(0.5)
    
    logger.info("正在检查账号使用情况...")
    time.sleep(0.5)
    
    logger.info("找到 5 个活跃账号，2 个已禁用账号")
    time.sleep(0.5)
    
    logger.warning("账号 user@example.com 使用率已达 85%")
    time.sleep(0.5)

def main():
    """主函数"""
    print("=" * 60)
    print("日志功能测试")
    print("=" * 60)
    print()
    
    try:
        test_log_levels()
        print()
        
        test_log_content()
        print()
        
        test_continuous_logs()
        print()
        
        test_multiline_logs()
        print()
        
        test_chinese_logs()
        print()
        
        print("=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n测试被中断")
        sys.exit(0)

if __name__ == '__main__':
    main()
