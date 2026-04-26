"""
CPA 客户端
"""

import requests
import json
import time
from typing import Dict, List, Tuple, Optional


class CPAClient:
    """CPA API 客户端"""
    
    # OAuth 配置
    OAUTH_TOKEN_URL = "https://auth.openai.com/oauth/token"
    OAUTH_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
    OAUTH_REDIRECT_URI = "http://localhost:1455/auth/callback"
    
    def __init__(self, base_url: str, token: str, name: str = "默认"):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        })
    
    def get_auth_files(self) -> List[Dict]:
        """获取认证文件列表"""
        url = f"{self.base_url}/v0/management/auth-files"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get("files", [])
    
    def download_auth_file(self, filename: str) -> Optional[Dict]:
        """下载认证文件"""
        url = f"{self.base_url}/v0/management/auth-files/download"
        response = self.session.get(url, params={"name": filename}, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def upload_auth_file(self, auth_data: Dict, filename: str) -> Tuple[bool, str]:
        """上传认证文件"""
        try:
            url = f"{self.base_url}/v0/management/auth-files"
            
            files = {
                'file': (filename, json.dumps(auth_data), 'application/json')
            }
            
            response = self.session.post(url, files=files, timeout=30)
            
            if response.status_code == 200:
                return True, "上传成功"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def disable_auth_file(self, filename: str) -> Tuple[bool, str]:
        """禁用认证文件"""
        try:
            url = f"{self.base_url}/v0/management/auth-files/status"
            
            response = self.session.patch(
                url,
                json={"name": filename, "disabled": True},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code in (200, 204):
                return True, "禁用成功"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def enable_auth_file(self, filename: str) -> Tuple[bool, str]:
        """启用认证文件"""
        try:
            url = f"{self.base_url}/v0/management/auth-files/status"
            
            response = self.session.patch(
                url,
                json={"name": filename, "disabled": False},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code in (200, 204):
                return True, "启用成功"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_usage(self, auth_index: str) -> Tuple[bool, Dict]:
        """检查账号使用情况"""
        try:
            url = f"{self.base_url}/v0/management/api-call"
            
            payload = {
                "authIndex": auth_index,
                "method": "GET",
                "url": "https://chatgpt.com/backend-api/wham/usage",
                "header": {
                    "Authorization": "Bearer $TOKEN$",
                    "Content-Type": "application/json",
                    "User-Agent": "codex_cli_rs/0.76.0"
                }
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            status_code = result.get("status_code")
            
            if status_code == 200:
                body = result.get("body", "{}")
                usage_data = json.loads(body)
                return True, usage_data
            else:
                return False, {"status_code": status_code, "body": result.get("body", "")}
        
        except Exception as e:
            return False, {"error": str(e)}
    
    def refresh_oauth_token(self, refresh_token: str) -> Tuple[bool, Dict]:
        """刷新 OAuth Token"""
        if not refresh_token:
            return False, {"error": "无 refresh_token"}
        
        try:
            response = requests.post(
                self.OAUTH_TOKEN_URL,
                data={
                    "client_id": self.OAUTH_CLIENT_ID,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "redirect_uri": self.OAUTH_REDIRECT_URI,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                now = int(time.time())
                expires_in = int(data.get("expires_in", 3600))
                
                return True, {
                    "access_token": data.get("access_token"),
                    "refresh_token": data.get("refresh_token", refresh_token),
                    "id_token": data.get("id_token"),
                    "last_refresh": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
                    "expired": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + expires_in)),
                }
            
            return False, {"error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            return False, {"error": str(e)}
    
    def revive_token(self, email: str, filename: str, max_attempts: int = 3) -> Tuple[bool, str]:
        """复活 Token"""
        # 下载完整认证文件
        auth_data = self.download_auth_file(filename)
        if not auth_data:
            return False, "无法下载认证文件"
        
        refresh_token = auth_data.get("refresh_token")
        if not refresh_token:
            return False, "缺少 refresh_token"
        
        # 尝试刷新 Token
        for attempt in range(1, max_attempts + 1):
            ok, result = self.refresh_oauth_token(refresh_token)
            
            if ok:
                # 更新认证文件
                auth_data.update(result)
                
                if "email" not in auth_data:
                    auth_data["email"] = email
                
                # 上传更新后的文件
                upload_ok, upload_msg = self.upload_auth_file(auth_data, filename)
                
                if upload_ok:
                    return True, "复活成功"
                else:
                    return False, f"上传失败: {upload_msg}"
            else:
                error_msg = result.get("error", "未知错误")
                if "400" in str(error_msg):
                    break
            
            if attempt < max_attempts:
                time.sleep(2)
        
        return False, f"复活失败（尝试 {max_attempts} 次）"
    
    def download_config_yaml(self) -> Tuple[bool, str]:
        """下载 config.yaml"""
        try:
            url = f"{self.base_url}/v0/management/config.yaml"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return True, response.text
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
