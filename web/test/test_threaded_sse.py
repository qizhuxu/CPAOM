#!/usr/bin/env python3
"""
测试 SSE 日志流在多线程模式下的并发性能
验证日志流不会阻塞其他 API 请求
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = 'http://localhost:5000'
USERNAME = 'admin'
PASSWORD = 'admin123'

def login():
    """登录并获取 session"""
    session = requests.Session()
    response = session.post(
        f'{BASE_URL}/auth/login',
        data={'username': USERNAME, 'password': PASSWORD},
        allow_redirects=False
    )
    if response.status_code in [200, 302]:
        print("✓ 登录成功")
        return session
    else:
        print(f"✗ 登录失败: {response.status_code}")
        return None

def test_sse_stream(session, duration=10):
    """测试 SSE 日志流连接"""
    print(f"\n[SSE 测试] 开始连接日志流，持续 {duration} 秒...")
    
    try:
        response = session.get(
            f'{BASE_URL}/api/logs/stream',
            stream=True,
            timeout=duration + 5
        )
        
        log_count = 0
        start_time = time.time()
        
        for line in response.iter_lines():
            if time.time() - start_time > duration:
                break
                
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    log_count += 1
                    if log_count <= 3:
                        print(f"  收到日志: {decoded_line[:80]}...")
        
        print(f"✓ SSE 流测试完成，共接收 {log_count} 条日志")
        return True
        
    except Exception as e:
        print(f"✗ SSE 流测试失败: {e}")
        return False

def test_api_request(session, endpoint, name):
    """测试普通 API 请求"""
    try:
        start = time.time()
        response = session.get(f'{BASE_URL}{endpoint}')
        elapsed = time.time() - start
        
        if response.status_code == 200:
            print(f"  ✓ {name}: {response.status_code} ({elapsed:.2f}s)")
            return True
        else:
            print(f"  ✗ {name}: {response.status_code} ({elapsed:.2f}s)")
            return False
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return False

def test_concurrent_requests(session):
    """在 SSE 连接期间测试并发 API 请求"""
    print("\n[并发测试] 在 SSE 连接期间发送多个 API 请求...")
    
    # 启动 SSE 流（在后台线程）
    sse_thread = threading.Thread(target=test_sse_stream, args=(session, 15))
    sse_thread.daemon = True
    sse_thread.start()
    
    # 等待 SSE 连接建立
    time.sleep(2)
    
    # 测试多个并发请求
    endpoints = [
        ('/health', 'Health Check'),
        ('/api/servers/', 'Get Servers'),
        ('/api/stats/overview', 'Get Stats'),
        ('/api/logs/history?limit=10', 'Get Log History'),
    ]
    
    success_count = 0
    total_count = 0
    
    print("\n  发送并发请求（SSE 流正在运行）...")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for endpoint, name in endpoints:
            future = executor.submit(test_api_request, session, endpoint, name)
            futures.append(future)
        
        for future in as_completed(futures):
            total_count += 1
            if future.result():
                success_count += 1
    
    print(f"\n  并发测试结果: {success_count}/{total_count} 成功")
    
    # 等待 SSE 线程完成
    sse_thread.join(timeout=20)
    
    return success_count == total_count

def test_multiple_sse_connections(session):
    """测试多个 SSE 连接"""
    print("\n[多连接测试] 同时建立多个 SSE 连接...")
    
    def connect_sse(session_id):
        try:
            response = session.get(
                f'{BASE_URL}/api/logs/stream',
                stream=True,
                timeout=8
            )
            
            log_count = 0
            start_time = time.time()
            
            for line in response.iter_lines():
                if time.time() - start_time > 5:
                    break
                if line and line.decode('utf-8').startswith('data:'):
                    log_count += 1
            
            print(f"  ✓ 连接 {session_id}: 接收 {log_count} 条日志")
            return True
        except Exception as e:
            print(f"  ✗ 连接 {session_id}: {e}")
            return False
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(connect_sse, i) for i in range(3)]
        results = [f.result() for f in as_completed(futures)]
    
    success = all(results)
    print(f"\n  多连接测试: {'✓ 通过' if success else '✗ 失败'}")
    return success

def main():
    """主测试流程"""
    print("=" * 60)
    print("SSE 日志流多线程并发测试")
    print("=" * 60)
    
    # 登录
    session = login()
    if not session:
        print("\n✗ 测试失败：无法登录")
        return
    
    # 测试 1: 基本 SSE 连接
    test_sse_stream(session, duration=5)
    
    # 测试 2: SSE 期间的并发请求
    concurrent_ok = test_concurrent_requests(session)
    
    # 测试 3: 多个 SSE 连接
    multiple_ok = test_multiple_sse_connections(session)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if concurrent_ok and multiple_ok:
        print("✓ 所有测试通过！")
        print("  - SSE 日志流工作正常")
        print("  - 不会阻塞其他 API 请求")
        print("  - 支持多个并发连接")
    else:
        print("✗ 部分测试失败")
        if not concurrent_ok:
            print("  - 并发请求测试失败（可能是单线程阻塞）")
        if not multiple_ok:
            print("  - 多连接测试失败")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
