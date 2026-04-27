#!/usr/bin/env python3
"""
测试新的快速API
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import json


def test_servers_overview_api():
    """测试服务器概览API"""
    print("测试服务器概览API...")
    
    with app.test_client() as client:
        # 登录
        response = client.post('/auth/login', data={
            'username': os.getenv('ADMIN_USERNAME', 'admin'),
            'password': os.getenv('ADMIN_PASSWORD', 'admin123')
        }, follow_redirects=False)
        
        # 测试新API
        response = client.get('/api/stats/servers-overview')
        assert response.status_code == 200, f"API返回错误: {response.status_code}"
        
        data = json.loads(response.data)
        assert data['success'] == True, "API返回失败"
        assert 'servers' in data, "缺少servers字段"
        
        print(f"✓ API正常，返回 {len(data['servers'])} 个服务器")
        
        # 检查服务器数据结构
        if data['servers']:
            server = data['servers'][0]
            required_fields = ['id', 'name', 'base_url', 'stats', 'status', 
                             'last_sync', 'local_backup_count', 'token_revive_enabled', 'online']
            
            for field in required_fields:
                assert field in server, f"服务器数据缺少字段: {field}"
            
            print("✓ 服务器数据结构正确")
            print(f"\n示例服务器数据:")
            print(f"  名称: {server['name']}")
            print(f"  状态: {server['status']}")
            print(f"  在线: {server['online']}")
            print(f"  总账号: {server['stats']['total']}")
            print(f"  活跃: {server['stats']['active']}")
            print(f"  禁用: {server['stats']['disabled']}")
            print(f"  最后同步: {server['last_sync']}")
            print(f"  本地备份: {server['local_backup_count']}")
            print(f"  Token复活: {server['token_revive_enabled']}")
        
        print("\n✓ 所有测试通过！")


if __name__ == '__main__':
    print("=" * 60)
    print("测试新的快速API")
    print("=" * 60)
    print()
    
    try:
        test_servers_overview_api()
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
