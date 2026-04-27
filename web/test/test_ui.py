#!/usr/bin/env python3
"""
UI 功能测试脚本
测试新UI的基本功能是否正常
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import json


def test_routes():
    """测试路由是否正常"""
    print("测试路由...")
    
    with app.test_client() as client:
        # 测试登录页面
        response = client.get('/auth/login')
        assert response.status_code == 200, "登录页面加载失败"
        print("✓ 登录页面正常")
        
        # 测试健康检查
        response = client.get('/health')
        assert response.status_code == 200, "健康检查失败"
        data = json.loads(response.data)
        assert data['status'] == 'ok', "健康检查状态异常"
        print("✓ 健康检查正常")
        
        # 测试404页面
        response = client.get('/nonexistent')
        assert response.status_code == 404, "404页面状态码错误"
        print("✓ 404页面正常")
        
        print("\n所有路由测试通过！")


def test_api_endpoints():
    """测试API端点是否存在"""
    print("\n测试API端点...")
    
    with app.test_client() as client:
        # 登录
        response = client.post('/auth/login', data={
            'username': os.getenv('ADMIN_USERNAME', 'admin'),
            'password': os.getenv('ADMIN_PASSWORD', 'admin123')
        }, follow_redirects=False)
        
        # 测试服务器列表API
        response = client.get('/api/servers/')
        assert response.status_code == 200, "服务器列表API失败"
        print("✓ 服务器列表API正常")
        
        # 测试统计API
        response = client.get('/api/stats/dashboard')
        assert response.status_code == 200, "统计API失败"
        print("✓ 统计API正常")
        
        # 测试本地账号API
        response = client.get('/api/local-accounts/')
        assert response.status_code == 200, "本地账号API失败"
        print("✓ 本地账号API正常")
        
        print("\n所有API端点测试通过！")


def test_templates():
    """测试模板是否存在"""
    print("\n测试模板文件...")
    
    templates = [
        'base.html',
        'dashboard.html',
        'server_detail.html',
        'auth/login.html',
        '404.html',
        '500.html'
    ]
    
    for template in templates:
        path = os.path.join('templates', template)
        assert os.path.exists(path), f"模板文件不存在: {template}"
        print(f"✓ {template}")
    
    print("\n所有模板文件存在！")


if __name__ == '__main__':
    print("=" * 60)
    print("CPA 账号管理系统 - UI 功能测试")
    print("=" * 60)
    
    try:
        test_templates()
        test_routes()
        test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
