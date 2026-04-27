"""
测试下载认证文件功能
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.cpa_client import CPAClient
from utils.config_manager import ConfigManager
from dotenv import load_dotenv

load_dotenv()


def test_download():
    """测试下载功能"""
    print("测试下载认证文件功能")
    print("=" * 60)
    
    config_manager = ConfigManager()
    servers = config_manager.get_servers()
    
    if not servers:
        print("❌ 没有配置服务器")
        return
    
    server = servers[0]
    print(f"\n测试服务器: {server['name']}")
    print(f"URL: {server['base_url']}")
    
    client = CPAClient(server["base_url"], server["token"], server["name"])
    
    # 获取账号列表
    print("\n1. 获取账号列表...")
    files = client.get_auth_files()
    print(f"   找到 {len(files)} 个账号")
    
    if not files:
        print("❌ 没有账号可测试")
        return
    
    # 测试下载第一个账号
    test_file = files[0]
    filename = test_file.get('name')
    email = test_file.get('email', '')
    
    print(f"\n2. 测试下载账号: {email}")
    print(f"   文件名: {filename}")
    
    ok, auth_data = client.download_auth_file(filename)
    
    if ok:
        print(f"   ✓ 下载成功")
        print(f"   数据类型: {type(auth_data)}")
        if auth_data:
            print(f"   包含字段: {list(auth_data.keys())[:5]}...")
    else:
        print(f"   ✗ 下载失败")
    
    print("\n" + "=" * 60)
    print("测试完成")


if __name__ == '__main__':
    test_download()
