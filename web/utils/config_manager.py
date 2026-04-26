"""
配置管理器
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config = None
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            # 创建默认配置
            default_config = {
                "cpa_servers": [],
                "settings": {
                    "max_workers": 10,
                    "auto_sync_interval": 3600,
                    "token_revive_max_attempts": 3
                }
            }
            self.save_config(default_config)
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
        
        return self._config
    
    def save_config(self, config: Dict):
        """保存配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self._config = config
    
    def get_servers(self) -> List[Dict]:
        """获取所有服务器配置"""
        config = self.load_config()
        return config.get("cpa_servers", [])
    
    def get_server(self, server_id: str) -> Optional[Dict]:
        """获取指定服务器配置"""
        servers = self.get_servers()
        for server in servers:
            if server.get("id") == server_id:
                return server
        return None
    
    def add_server(self, server: Dict):
        """添加服务器"""
        config = self.load_config()
        if "cpa_servers" not in config:
            config["cpa_servers"] = []
        
        config["cpa_servers"].append(server)
        self.save_config(config)
    
    def update_server(self, server_id: str, server_data: Dict):
        """更新服务器配置"""
        config = self.load_config()
        servers = config.get("cpa_servers", [])
        
        for i, server in enumerate(servers):
            if server.get("id") == server_id:
                servers[i] = {**server, **server_data}
                break
        
        self.save_config(config)
    
    def delete_server(self, server_id: str):
        """删除服务器"""
        config = self.load_config()
        servers = config.get("cpa_servers", [])
        
        config["cpa_servers"] = [s for s in servers if s.get("id") != server_id]
        self.save_config(config)
    
    def get_settings(self) -> Dict:
        """获取系统设置"""
        config = self.load_config()
        return config.get("settings", {})
    
    def update_settings(self, settings: Dict):
        """更新系统设置"""
        config = self.load_config()
        if "settings" not in config:
            config["settings"] = {}
        
        config["settings"].update(settings)
        self.save_config(config)
