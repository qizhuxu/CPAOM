#!/usr/bin/env python3
"""
CPA 账号管理工具
- 批量检查账号使用情况
- 自动复活失效的 Token（401 错误）
- 自动禁用复活失败的账号
- 批量下载并打包认证文件
- 多 CPA 服务器管理
"""

import json
import os
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, Tuple, Optional, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# OpenAI OAuth 配置
OAUTH_TOKEN_URL = "https://auth.openai.com/oauth/token"
OAUTH_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
OAUTH_REDIRECT_URI = "http://localhost:1455/auth/callback"


class CPAManager:
    """CPA 管理器（检查、复活、下载、打包）"""
    
    def __init__(self, base_url: str, token: str, name: str = "默认", max_workers: int = 10, enable_revive: bool = True):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.name = name
        self.max_workers = max_workers
        self.enable_revive = enable_revive
        self.print_lock = Lock()
        self.revive_stats = {
            "attempted": 0,
            "succeeded": 0,
            "failed": 0
        }
    
    def get_auth_files(self) -> list:
        """获取所有认证文件列表"""
        url = f"{self.base_url}/v0/management/auth-files"
        
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        })
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get("files", [])
    
    def refresh_oauth_token(self, refresh_token: str) -> Tuple[bool, dict]:
        """使用 refresh_token 获取新的 access_token
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            (成功标志, 新token数据或错误信息)
        """
        if not refresh_token:
            return False, {"error": "无 refresh_token"}
        
        try:
            response = requests.post(
                OAUTH_TOKEN_URL,
                data={
                    "client_id": OAUTH_CLIENT_ID,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "redirect_uri": OAUTH_REDIRECT_URI,
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
            
            return False, {"error": f"HTTP {response.status_code}", "body": response.text[:200]}
        
        except Exception as e:
            return False, {"error": str(e)}
    
    def download_auth_file(self, filename: str) -> Optional[dict]:
        """下载完整的认证文件
        
        Args:
            filename: 文件名
            
        Returns:
            认证文件内容或 None
        """
        try:
            url = f"{self.base_url}/v0/management/auth-files/download"
            response = requests.get(
                url,
                params={"name": filename},
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30,
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                with self.print_lock:
                    print(f"   ⚠️  下载 {filename} 失败: HTTP {response.status_code}")
                return None
        
        except Exception as e:
            with self.print_lock:
                print(f"   ⚠️  下载 {filename} 异常: {e}")
            return None
    
    def upload_auth_file(self, auth_data: dict, filename: str) -> Tuple[bool, str]:
        """上传更新后的认证文件
        
        Args:
            auth_data: 认证文件数据
            filename: 文件名
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 修复：使用官方文档的正确路径
            url = f"{self.base_url}/v0/management/auth-files"
            
            # 准备 multipart/form-data
            files = {
                'file': (filename, json.dumps(auth_data), 'application/json')
            }
            
            response = requests.post(
                url,
                files=files,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30,
            )
            
            if response.status_code == 200:
                return True, "上传成功"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"异常: {str(e)}"
    
    def disable_auth_file(self, filename: str) -> Tuple[bool, str]:
        """禁用认证文件（使用 CPA API 的 status 接口）
        
        Args:
            filename: 文件名
            
        Returns:
            (成功标志, 消息)
        """
        try:
            url = f"{self.base_url}/v0/management/auth-files/status"
            
            response = requests.patch(
                url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": filename,
                    "disabled": True
                },
                timeout=15,
            )
            
            if response.status_code in (200, 204):
                return True, "禁用成功"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"异常: {str(e)}"
    
    def enable_auth_file(self, filename: str) -> Tuple[bool, str]:
        """启用认证文件（使用 CPA API 的 status 接口）
        
        Args:
            filename: 文件名
            
        Returns:
            (成功标志, 消息)
        """
        try:
            url = f"{self.base_url}/v0/management/auth-files/status"
            
            response = requests.patch(
                url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": filename,
                    "disabled": False
                },
                timeout=15,
            )
            
            if response.status_code in (200, 204):
                return True, "启用成功"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"异常: {str(e)}"
    
    def revive_token(self, email: str, filename: str, max_attempts: int = 3) -> Tuple[bool, str]:
        """尝试复活 Token
        
        Args:
            email: 邮箱地址
            filename: 文件名
            max_attempts: 最大尝试次数
            
        Returns:
            (成功标志, 消息)
        """
        with self.print_lock:
            print(f"   🔄 尝试复活 Token: {email}")
        
        self.revive_stats["attempted"] += 1
        
        # 1. 下载完整认证文件
        auth_data = self.download_auth_file(filename)
        if not auth_data:
            return False, "无法下载认证文件"
        
        refresh_token = auth_data.get("refresh_token")
        if not refresh_token:
            with self.print_lock:
                print(f"   ❌ {email}: 缺少 refresh_token，无法复活")
            return False, "缺少 refresh_token"
        
        # 2. 尝试刷新 Token（最多 max_attempts 次）
        for attempt in range(1, max_attempts + 1):
            with self.print_lock:
                print(f"   🔄 {email}: 第 {attempt}/{max_attempts} 次尝试刷新...")
            
            ok, result = self.refresh_oauth_token(refresh_token)
            
            if ok:
                # 3. 刷新成功，更新认证文件
                with self.print_lock:
                    print(f"   ✅ {email}: Token 刷新成功")
                
                auth_data.update(result)
                
                # 确保有 email 字段
                if "email" not in auth_data:
                    auth_data["email"] = email
                
                # 4. 上传更新后的文件
                upload_ok, upload_msg = self.upload_auth_file(auth_data, filename)
                
                if upload_ok:
                    with self.print_lock:
                        print(f"   ✅ {email}: 认证文件已更新")
                    
                    # 5. 等待一下再验证
                    time.sleep(2)
                    
                    # 6. 验证新 Token 是否可用
                    auth_index = auth_data.get("auth_index") or filename.replace("codex-account-", "").replace(".json", "")
                    test_result = self._test_new_token(auth_index, email)
                    
                    if test_result:
                        with self.print_lock:
                            print(f"   🎉 {email}: Token 复活成功！")
                        self.revive_stats["succeeded"] += 1
                        return True, "复活成功"
                    else:
                        with self.print_lock:
                            print(f"   ⚠️  {email}: 新 Token 验证失败")
                        # 继续尝试下一次
                else:
                    with self.print_lock:
                        print(f"   ❌ {email}: 上传失败 - {upload_msg}")
                    # 继续尝试下一次
            else:
                error_msg = result.get("error", "未知错误")
                with self.print_lock:
                    print(f"   ❌ {email}: 刷新失败 - {error_msg}")
                
                # 如果是 400 错误，说明 refresh_token 已失效，不再重试
                if "400" in str(error_msg):
                    break
            
            # 等待后重试
            if attempt < max_attempts:
                time.sleep(2)
        
        # 所有尝试都失败
        self.revive_stats["failed"] += 1
        return False, f"复活失败（尝试 {max_attempts} 次）"
    
    def _test_new_token(self, auth_index: str, email: str) -> bool:
        """测试新 Token 是否可用
        
        Args:
            auth_index: 认证索引
            email: 邮箱地址
            
        Returns:
            是否可用
        """
        try:
            api_url = f"{self.base_url}/v0/management/api-call"
            
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
            
            response = requests.post(api_url, json=payload, 
                                    headers={
                                        "Authorization": f"Bearer {self.token}",
                                        "Content-Type": "application/json"
                                    },
                                    timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("status_code") == 200
            
            return False
        
        except Exception:
            return False
    
    def check_usage(self, auth_index: str, email: str, filename: str) -> Tuple[str, Dict]:
        """检查单个账号的使用情况（带重试机制和 Token 复活）
        
        Returns:
            (email, usage_data) 或 (email, error_info) 如果失败
        """
        api_url = f"{self.base_url}/v0/management/api-call"
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔：1秒、2秒、4秒
            status_forcelist=[429, 500, 502, 503, 504],  # 这些状态码会重试
            allowed_methods=["POST"]  # 允许 POST 重试
        )
        
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })
        
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
        
        # 手动重试 SSL 错误
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = session.post(api_url, json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                status_code = result.get("status_code")
                
                if status_code == 200:
                    body = result.get("body", "{}")
                    usage_data = json.loads(body)
                    return (email, usage_data)
                elif status_code == 401:
                    # Token 失效，尝试复活
                    body = result.get("body", "")
                    with self.print_lock:
                        print(f"   ⚠️  [401] {email}: Token 已失效")
                    
                    if self.enable_revive:
                        # 尝试复活 Token
                        revive_ok, revive_msg = self.revive_token(email, filename, max_attempts=3)
                        
                        if revive_ok:
                            # 复活成功，重新检查使用情况
                            with self.print_lock:
                                print(f"   🔄 {email}: 复活成功，重新检查使用情况...")
                            
                            time.sleep(1)
                            # 递归调用自己（只递归一次，避免无限循环）
                            return self.check_usage(auth_index, email, filename)
                        else:
                            # 复活失败，禁用该文件
                            with self.print_lock:
                                print(f"   ❌ {email}: 复活失败，禁用该认证文件")
                            
                            disable_ok, disable_msg = self.disable_auth_file(filename)
                            if disable_ok:
                                with self.print_lock:
                                    print(f"   ✅ {email}: 已禁用")
                            else:
                                with self.print_lock:
                                    print(f"   ⚠️  {email}: 禁用失败 - {disable_msg}")
                            
                            return (email, {
                                "_error": True,
                                "status_code": 401,
                                "body": body[:200] if body else "",
                                "revive_failed": True
                            })
                    else:
                        # 未开启复活功能
                        return (email, {
                            "_error": True,
                            "status_code": status_code,
                            "body": body[:200] if body else ""
                        })
                else:
                    # 其他非200状态码，返回错误信息
                    body = result.get("body", "")
                    error_info = {
                        "_error": True,
                        "status_code": status_code,
                        "body": body[:200] if body else ""
                    }
                    with self.print_lock:
                        print(f"   ⚠️  [{status_code}] {email}: {body[:100] if body else 'No body'}")
                    return (email, error_info)
            
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                if attempt < max_attempts - 1:
                    # 等待后重试
                    time.sleep(1 * (attempt + 1))
                    continue
                else:
                    # 最后一次尝试失败
                    with self.print_lock:
                        print(f"   ⚠️  网络错误 (重试{max_attempts}次): {email} - {type(e).__name__}")
                    return (email, {"_error": True, "error_type": "network", "message": str(e)})
            
            except Exception as e:
                with self.print_lock:
                    print(f"   ⚠️  检查失败: {email} - {type(e).__name__}: {str(e)[:100]}")
                return (email, {"_error": True, "error_type": type(e).__name__, "message": str(e)[:200]})
        
        return (email, {"_error": True, "error_type": "unknown", "message": "Max retries exceeded"})
    
    def check_all(self):
        """批量检查所有账号"""
        # 获取文件列表
        print("📡 获取认证文件列表...")
        files = self.get_auth_files()
        print(f"✅ 找到 {len(files)} 个认证文件")
        print()
        
        if not files:
            print("⚠️  没有找到任何文件")
            return
        
        # 统计已禁用的账号
        disabled_files = [f for f in files if f.get("disabled")]
        active_files = [f for f in files if not f.get("disabled")]
        
        if disabled_files:
            print(f"ℹ️  跳过 {len(disabled_files)} 个已禁用的账号")
            print()
        
        if not active_files:
            print("⚠️  没有可用的活跃账号")
            return
        
        print(f"🔍 开始检查使用情况（{self.max_workers} 线程）...")
        print()
        
        results = []
        failed_results = []  # 存储失败的账号
        completed = 0
        total = len(active_files)
        
        # 并发检查
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务（只检查活跃账号）
            future_to_file = {}
            for file_info in active_files:
                file_name = file_info.get("name", "")
                email = file_info.get("email", "")
                
                # 使用文件元数据中的 auth_index 字段
                auth_index = file_info.get("auth_index", "")
                
                if not auth_index:
                    continue
                
                future = executor.submit(self.check_usage, auth_index, email, file_name)
                future_to_file[future] = email
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                completed += 1
                email, usage_data = future.result()
                
                if usage_data and not usage_data.get("_error"):
                    # 成功获取使用情况
                    results.append((email, usage_data))
                    
                    rate_limit = usage_data.get("rate_limit", {})
                    primary = rate_limit.get("primary_window", {})
                    used_percent = primary.get("used_percent", 0)
                    limit_reached = rate_limit.get("limit_reached", False)
                    
                    status = "🔴" if limit_reached else "🟢" if used_percent < 50 else "🟡"
                    
                    with self.print_lock:
                        print(f"   [{completed}/{total}] {status} {email}: {used_percent}%")
                elif usage_data and usage_data.get("_error"):
                    # 有错误信息（已在 check_usage 中打印）
                    failed_results.append((email, usage_data))
                else:
                    # 未知错误
                    failed_results.append((email, {"_error": True, "error_type": "unknown"}))
                    with self.print_lock:
                        print(f"   [{completed}/{total}] ❌ {email}: 未知错误")
        
        print()
        print("=" * 70)
        print("📊 统计结果")
        print("=" * 70)
        print()
        
        # 统计
        total_files = len(files)
        disabled_count = len(disabled_files)
        total_checked = len(results)
        failed_count = len(failed_results)
        available = sum(1 for _, data in results if not data.get("rate_limit", {}).get("limit_reached"))
        limited = total_checked - available
        
        print(f"总计: {total_files} 个认证文件")
        if disabled_count > 0:
            print(f"已禁用: {disabled_count} 个 🚫")
        print(f"活跃账号: {len(active_files)} 个")
        print(f"成功检查: {total_checked} 个")
        if failed_count > 0:
            print(f"检查失败: {failed_count} 个 ⚠️")
        print(f"可用: {available} 个 (🟢)")
        print(f"受限: {limited} 个 (🔴)")
        print()
        
        # 如果有失败的账号，显示详细信息
        if failed_results:
            print("=" * 70)
            print("❌ 检查失败的账号")
            print("=" * 70)
            print()
            
            # 按错误类型分组
            error_by_status = {}
            for email, error_data in failed_results:
                status_code = error_data.get("status_code", "unknown")
                if status_code not in error_by_status:
                    error_by_status[status_code] = []
                error_by_status[status_code].append((email, error_data))
            
            for status_code, items in sorted(error_by_status.items()):
                print(f"🔸 HTTP {status_code}: {len(items)} 个")
                for email, error_data in items[:5]:  # 最多显示5个
                    print(f"   • {email}")
                    if error_data.get("body"):
                        body_preview = error_data["body"][:150]
                        print(f"     {body_preview}")
                    elif error_data.get("message"):
                        print(f"     {error_data['message'][:150]}")
                if len(items) > 5:
                    print(f"   ... 还有 {len(items) - 5} 个")
                print()
            
            print("常见错误码说明:")
            print("  401 - Token 已失效" + (" (已尝试复活)" if self.enable_revive else " (未开启复活功能)"))
            print("  403 - 访问被拒绝，可能账号被封禁")
            print("  429 - 请求过于频繁，触发限流")
            print("  500/502/503 - 服务器错误")
            print()
        
        # 显示 Token 复活统计
        if self.enable_revive and self.revive_stats["attempted"] > 0:
            print("=" * 70)
            print("🔄 Token 复活统计")
            print("=" * 70)
            print()
            print(f"尝试复活: {self.revive_stats['attempted']} 个")
            print(f"复活成功: {self.revive_stats['succeeded']} 个 ✅")
            print(f"复活失败: {self.revive_stats['failed']} 个 ❌")
            if self.revive_stats["attempted"] > 0:
                success_rate = (self.revive_stats["succeeded"] / self.revive_stats["attempted"]) * 100
                print(f"成功率: {success_rate:.1f}%")
            print()
        
        # 按使用率排序
        results.sort(key=lambda x: x[1].get("rate_limit", {}).get("primary_window", {}).get("used_percent", 0))
        
        # 显示可用账号（使用率 < 80%）
        print("🟢 可用账号（使用率 < 80%）:")
        available_accounts = [
            (email, data) for email, data in results
            if data.get("rate_limit", {}).get("primary_window", {}).get("used_percent", 0) < 80
        ]
        
        if available_accounts:
            for email, data in available_accounts[:10]:  # 只显示前10个
                rate_limit = data.get("rate_limit", {})
                primary = rate_limit.get("primary_window", {})
                used_percent = primary.get("used_percent", 0)
                reset_seconds = primary.get("reset_after_seconds", 0)
                
                print(f"   • {email}")
                print(f"     使用率: {used_percent}%, 重置: {reset_seconds // 3600}小时后")
            
            if len(available_accounts) > 10:
                print(f"   ... 还有 {len(available_accounts) - 10} 个")
        else:
            print("   无")
        
        print()
        
        # 显示受限账号
        print("🔴 受限账号（使用率 >= 80%）:")
        limited_accounts = [
            (email, data) for email, data in results
            if data.get("rate_limit", {}).get("primary_window", {}).get("used_percent", 0) >= 80
        ]
        
        if limited_accounts:
            for email, data in limited_accounts[:10]:  # 只显示前10个
                rate_limit = data.get("rate_limit", {})
                primary = rate_limit.get("primary_window", {})
                used_percent = primary.get("used_percent", 0)
                reset_seconds = primary.get("reset_after_seconds", 0)
                
                print(f"   • {email}")
                print(f"     使用率: {used_percent}%, 重置: {reset_seconds // 3600}小时后")
            
            if len(limited_accounts) > 10:
                print(f"   ... 还有 {len(limited_accounts) - 10} 个")
        else:
            print("   无")
        
        print()
    
    def download_file(self, file_name: str) -> Tuple[str, bytes]:
        """下载单个认证文件（线程安全，带重试）
        
        Returns:
            (file_name, content) 或 (file_name, None) 如果失败
        """
        url = f"{self.base_url}/v0/management/auth-files/download"
        params = {"name": file_name}
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        # 每个线程使用独立的 session
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        })
        
        # 手动重试 SSL 错误
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return (file_name, response.content)
            
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                if attempt < max_attempts - 1:
                    time.sleep(1 * (attempt + 1))
                    continue
                else:
                    with self.print_lock:
                        print(f"   ⚠️  下载失败（重试{max_attempts}次）: {file_name}")
                    return (file_name, None)
            
            except requests.exceptions.RequestException as e:
                with self.print_lock:
                    print(f"   ⚠️  下载失败: {file_name} - {type(e).__name__}")
                return (file_name, None)
    
    def download_and_pack(self, output_dir: str = "pool") -> Tuple[str, int]:
        """并发下载所有文件并打包（跳过禁用的账号）
        
        Returns:
            (zip_path, file_count) 或 (None, 0) 如果失败
        """
        print()
        print("=" * 70)
        print(f"📦 批量下载并打包 - {self.name}")
        print("=" * 70)
        print()
        
        # 获取文件列表
        print("📡 获取认证文件列表...")
        files = self.get_auth_files()
        print(f"✅ 找到 {len(files)} 个认证文件")
        
        if not files:
            print("⚠️  没有找到任何文件")
            return None, 0
        
        # 过滤掉禁用的账号
        active_files = [f for f in files if not f.get("disabled")]
        disabled_count = len(files) - len(active_files)
        
        if disabled_count > 0:
            print(f"ℹ️  跳过 {disabled_count} 个已禁用的账号")
        
        if not active_files:
            print("⚠️  没有可用的活跃账号")
            return None, 0
        
        print(f"📥 准备下载 {len(active_files)} 个活跃账号")
        print()
        
        # 创建临时目录
        temp_dir = Path("auth_files_download")
        temp_dir.mkdir(exist_ok=True)
        
        print(f"📥 开始并发下载文件（{self.max_workers} 线程）...")
        
        success_count = 0
        failed_count = 0
        completed = 0
        total = len(active_files)
        
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有下载任务（只下载活跃账号）
            future_to_file = {
                executor.submit(self.download_file, file_info.get("name")): file_info
                for file_info in active_files
                if file_info.get("name")
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                completed += 1
                file_name, content = future.result()
                
                if content:
                    # 保存文件
                    file_path = temp_dir / file_name
                    with open(file_path, "wb") as f:
                        f.write(content)
                    
                    with self.print_lock:
                        print(f"   [{completed}/{total}] ✅ {file_name}")
                    success_count += 1
                else:
                    with self.print_lock:
                        print(f"   [{completed}/{total}] ❌ {file_name}")
                    failed_count += 1
        
        print()
        print(f"📊 下载完成: 成功 {success_count}, 失败 {failed_count}")
        
        if success_count == 0:
            print("⚠️  没有成功下载任何文件")
            # 清理临时目录
            if temp_dir.exists():
                temp_dir.rmdir()
            return None, 0
        
        # 创建 pool 目录
        pool_dir = Path(output_dir)
        pool_dir.mkdir(exist_ok=True)
        
        # 打包为 ZIP（格式：日期-文件数）
        date_str = datetime.now().strftime("%Y%m%d")
        zip_name = f"{date_str}-{success_count}.zip"
        zip_path = pool_dir / zip_name
        
        print(f"\n📦 正在打包为 {zip_path}...")
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.glob("*"):
                if file_path.is_file():
                    zipf.write(file_path, file_path.name)
        
        # 清理临时文件
        print(f"🧹 清理临时文件...")
        for file_path in temp_dir.glob("*"):
            file_path.unlink()
        temp_dir.rmdir()
        
        zip_size = os.path.getsize(zip_path) / 1024 / 1024
        print(f"✅ 打包完成: {zip_path} ({zip_size:.2f} MB)")
        print()
        
        return str(zip_path), success_count
    
    def upload_from_directory(self, source_dir: str = "pool") -> Tuple[int, int]:
        """从目录批量上传认证文件
        
        Args:
            source_dir: 源目录路径
            
        Returns:
            (成功数量, 失败数量)
        """
        print()
        print("=" * 70)
        print(f"📤 批量上传认证文件 - {self.name}")
        print("=" * 70)
        print()
        
        source_path = Path(source_dir)
        
        if not source_path.exists():
            print(f"❌ 目录不存在: {source_dir}")
            return 0, 0
        
        # 查找所有 JSON 文件
        json_files = list(source_path.glob("*.json"))
        
        if not json_files:
            print(f"⚠️  目录中没有 JSON 文件: {source_dir}")
            return 0, 0
        
        print(f"📁 找到 {len(json_files)} 个 JSON 文件")
        print()
        print(f"📤 开始并发上传（{self.max_workers} 线程）...")
        print()
        
        success_count = 0
        failed_count = 0
        completed = 0
        total = len(json_files)
        
        # 使用线程池并发上传
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有上传任务
            future_to_file = {}
            for file_path in json_files:
                future = executor.submit(self._upload_single_file, file_path)
                future_to_file[future] = file_path.name
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                completed += 1
                filename = future_to_file[future]
                success, message = future.result()
                
                if success:
                    with self.print_lock:
                        print(f"   [{completed}/{total}] ✅ {filename}")
                    success_count += 1
                else:
                    with self.print_lock:
                        print(f"   [{completed}/{total}] ❌ {filename}: {message}")
                    failed_count += 1
        
        print()
        print(f"📊 上传完成: 成功 {success_count}, 失败 {failed_count}")
        print()
        
        return success_count, failed_count
    
    def _upload_single_file(self, file_path: Path) -> Tuple[bool, str]:
        """上传单个文件（线程安全）
        
        Args:
            file_path: 文件路径
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                auth_data = json.load(f)
            
            # 上传
            return self.upload_auth_file(auth_data, file_path.name)
        
        except json.JSONDecodeError as e:
            return False, f"JSON 格式错误: {str(e)}"
        except Exception as e:
            return False, f"读取失败: {str(e)}"
    
    def upload_from_zip(self, zip_path: str) -> Tuple[int, int]:
        """从 ZIP 文件批量上传认证文件
        
        Args:
            zip_path: ZIP 文件路径
            
        Returns:
            (成功数量, 失败数量)
        """
        print()
        print("=" * 70)
        print(f"📤 从 ZIP 批量上传 - {self.name}")
        print("=" * 70)
        print()
        
        zip_file = Path(zip_path)
        
        if not zip_file.exists():
            print(f"❌ ZIP 文件不存在: {zip_path}")
            return 0, 0
        
        if not zip_file.suffix.lower() == '.zip':
            print(f"❌ 不是 ZIP 文件: {zip_path}")
            return 0, 0
        
        print(f"📦 解压 ZIP 文件: {zip_path}")
        
        # 创建临时目录
        temp_dir = Path("temp_upload_extract")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # 解压 ZIP
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                # 只提取 JSON 文件
                json_members = [m for m in zipf.namelist() if m.lower().endswith('.json')]
                
                if not json_members:
                    print("⚠️  ZIP 中没有 JSON 文件")
                    return 0, 0
                
                print(f"📄 找到 {len(json_members)} 个 JSON 文件")
                
                for member in json_members:
                    zipf.extract(member, temp_dir)
            
            print()
            
            # 批量上传
            success_count, failed_count = self.upload_from_directory(str(temp_dir))
            
            return success_count, failed_count
        
        finally:
            # 清理临时文件
            print("🧹 清理临时文件...")
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    file_path.unlink()
            
            # 删除所有空目录
            for dir_path in sorted(temp_dir.rglob("*"), reverse=True):
                if dir_path.is_dir():
                    try:
                        dir_path.rmdir()
                    except:
                        pass
            
            # 删除根临时目录
            try:
                temp_dir.rmdir()
            except:
                pass
            
            print()
    
    def download_config_yaml(self, output_path: str = "config.yaml") -> Tuple[bool, str]:
        """下载 CPA 服务器的 config.yaml 配置文件
        
        Args:
            output_path: 保存路径
            
        Returns:
            (成功标志, 消息)
        """
        try:
            url = f"{self.base_url}/v0/management/config.yaml"
            
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                # 保存文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                file_size = len(response.text) / 1024
                return True, f"下载成功: {output_path} ({file_size:.2f} KB)"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"下载失败: {str(e)}"
    
    def get_openai_compatibility(self) -> Tuple[bool, list]:
        """获取 OpenAI 兼容提供商列表
        
        Returns:
            (成功标志, 提供商列表或错误信息)
        """
        try:
            url = f"{self.base_url}/v0/management/openai-compatibility"
            
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get("openai-compatibility", [])
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"获取失败: {str(e)}"
    
    def add_openai_compatibility(self, provider: Dict) -> Tuple[bool, str]:
        """添加 OpenAI 兼容提供商
        
        Args:
            provider: 提供商配置字典
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 先获取现有列表
            ok, result = self.get_openai_compatibility()
            if not ok:
                return False, f"获取现有配置失败: {result}"
            
            providers = result if isinstance(result, list) else []
            
            # 添加新提供商
            providers.append(provider)
            
            # 更新整个列表
            url = f"{self.base_url}/v0/management/openai-compatibility"
            
            response = requests.put(
                url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=providers,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "添加成功"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def update_openai_compatibility(self, name: str, provider: Dict) -> Tuple[bool, str]:
        """更新 OpenAI 兼容提供商
        
        Args:
            name: 提供商名称
            provider: 新的提供商配置
            
        Returns:
            (成功标志, 消息)
        """
        try:
            url = f"{self.base_url}/v0/management/openai-compatibility"
            
            response = requests.patch(
                url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": name,
                    "value": provider
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "更新成功"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def delete_openai_compatibility(self, name: str) -> Tuple[bool, str]:
        """删除 OpenAI 兼容提供商
        
        Args:
            name: 提供商名称
            
        Returns:
            (成功标志, 消息)
        """
        try:
            url = f"{self.base_url}/v0/management/openai-compatibility"
            
            response = requests.delete(
                url,
                params={"name": name},
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "删除成功"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"删除失败: {str(e)}"


def load_config(config_path: str = "config.json") -> Dict:
    """加载配置文件（支持单个或多个 CPA）"""
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        print()
        print("请创建 config.json 文件，支持以下两种格式：")
        print()
        print("格式1 - 单个 CPA:")
        print(json.dumps({
            "max_workers": 10,
            "base_url": "https://your-cpa.example.com",
            "token": "your-management-token",
            "enable_token_revive": True
        }, indent=2, ensure_ascii=False))
        print()
        print("格式2 - 多个 CPA:")
        print(json.dumps({
            "max_workers": 10,
            "cpa_servers": [
                {
                    "name": "主服务器",
                    "base_url": "https://cpa1.example.com",
                    "token": "token1",
                    "enable_token_revive": True
                },
                {
                    "name": "备用服务器",
                    "base_url": "https://cpa2.example.com",
                    "token": "token2",
                    "enable_token_revive": False
                }
            ]
        }, indent=2, ensure_ascii=False))
        sys.exit(1)
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 兼容旧格式（单个 CPA）
        if "base_url" in config and "token" in config:
            return {
                "max_workers": config.get("max_workers", 10),
                "cpa_servers": [{
                    "name": "默认",
                    "base_url": config["base_url"],
                    "token": config["token"],
                    "enable_token_revive": config.get("enable_token_revive", True)
                }]
            }
        
        # 新格式（多个 CPA）
        if "cpa_servers" in config:
            # 确保有 max_workers 字段
            if "max_workers" not in config:
                config["max_workers"] = 10
            return config
        
        print("❌ 配置文件格式错误")
        sys.exit(1)
    
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        sys.exit(1)


def show_menu():
    """显示主菜单"""
    print()
    print("=" * 70)
    print("CPA 账号管理工具")
    print("=" * 70)
    print()
    print("功能菜单:")
    print("  1. 检查账号使用情况（自动复活 Token）")
    print("  2. 下载并打包认证文件（跳过禁用）")
    print("  3. 批量上传认证文件")
    print("  4. 下载 config.yaml 配置文件")
    print("  5. 管理 OpenAI 兼容提供商")
    print("  6. 查看 CPA 服务器列表")
    print("  0. 退出")
    print()


def select_cpa_servers(servers: List[Dict]) -> List[int]:
    """选择要操作的 CPA 服务器
    
    Returns:
        选中的服务器索引列表
    """
    print()
    print("=" * 70)
    print("选择 CPA 服务器")
    print("=" * 70)
    print()
    
    for i, server in enumerate(servers, 1):
        name = server.get("name", f"服务器{i}")
        url = server.get("base_url", "")
        print(f"  {i}. {name}")
        print(f"     {url}")
    
    print(f"  0. 全部服务器")
    print()
    
    while True:
        choice = input("请选择服务器（多个用逗号分隔，如 1,2,3）: ").strip()
        
        if not choice:
            continue
        
        if choice == "0":
            return list(range(len(servers)))
        
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            
            # 验证索引
            if all(0 <= i < len(servers) for i in indices):
                return indices
            else:
                print("❌ 无效的选择，请重新输入")
        except ValueError:
            print("❌ 输入格式错误，请输入数字（如 1,2,3）")


def check_usage_action(servers: List[Dict], selected_indices: List[int], max_workers: int = 10):
    """执行检查使用情况操作"""
    for idx in selected_indices:
        server = servers[idx]
        name = server.get("name", f"服务器{idx+1}")
        base_url = server.get("base_url")
        token = server.get("token")
        enable_revive = server.get("enable_token_revive", True)
        
        print()
        print("=" * 70)
        print(f"检查账号使用情况 - {name}")
        print("=" * 70)
        print()
        print(f"CPA 地址: {base_url}")
        print(f"Token 复活: {'✅ 已开启' if enable_revive else '❌ 已关闭'}")
        print(f"并发线程: {max_workers}")
        print()
        
        manager = CPAManager(base_url, token, name, max_workers=max_workers, enable_revive=enable_revive)
        manager.check_all()
        
        if idx < len(selected_indices) - 1:
            print()
            input("按 Enter 继续下一个服务器...")


def download_action(servers: List[Dict], selected_indices: List[int], max_workers: int = 10):
    """执行下载打包操作"""
    results = []
    
    for idx in selected_indices:
        server = servers[idx]
        name = server.get("name", f"服务器{idx+1}")
        base_url = server.get("base_url")
        token = server.get("token")
        
        manager = CPAManager(base_url, token, name, max_workers=max_workers)
        zip_path, file_count = manager.download_and_pack()
        
        if zip_path:
            results.append((name, zip_path, file_count))
        
        if idx < len(selected_indices) - 1:
            print()
            input("按 Enter 继续下一个服务器...")
    
    # 显示汇总
    if results:
        print()
        print("=" * 70)
        print("📊 下载汇总")
        print("=" * 70)
        print()
        for name, zip_path, file_count in results:
            print(f"✅ {name}: {zip_path} ({file_count} 个文件)")
        print()


def upload_action(servers: List[Dict], selected_indices: List[int], max_workers: int = 10):
    """执行批量上传操作"""
    print()
    print("=" * 70)
    print("选择上传方式")
    print("=" * 70)
    print()
    print("  1. 从目录上传（默认: pool）")
    print("  2. 从 ZIP 文件上传")
    print("  3. 自定义目录路径")
    print()
    
    choice = input("请选择上传方式 (1-3): ").strip()
    
    if choice == "1":
        # 从默认 pool 目录上传
        source = "pool"
        upload_type = "directory"
    elif choice == "2":
        # 从 ZIP 文件上传
        print()
        # 列出 pool 目录中的 ZIP 文件
        pool_dir = Path("pool")
        if pool_dir.exists():
            zip_files = list(pool_dir.glob("*.zip"))
            if zip_files:
                print("可用的 ZIP 文件:")
                for i, zf in enumerate(zip_files, 1):
                    size = zf.stat().st_size / 1024 / 1024
                    print(f"  {i}. {zf.name} ({size:.2f} MB)")
                print()
                
                zip_choice = input(f"请选择 ZIP 文件 (1-{len(zip_files)}) 或输入完整路径: ").strip()
                
                try:
                    idx = int(zip_choice) - 1
                    if 0 <= idx < len(zip_files):
                        source = str(zip_files[idx])
                    else:
                        print("❌ 无效的选择")
                        return
                except ValueError:
                    # 用户输入了路径
                    source = zip_choice
            else:
                source = input("请输入 ZIP 文件路径: ").strip()
        else:
            source = input("请输入 ZIP 文件路径: ").strip()
        
        upload_type = "zip"
    elif choice == "3":
        # 自定义目录
        source = input("请输入目录路径: ").strip()
        upload_type = "directory"
    else:
        print("❌ 无效的选择")
        return
    
    if not source:
        print("❌ 未指定路径")
        return
    
    # 执行上传
    results = []
    
    for idx in selected_indices:
        server = servers[idx]
        name = server.get("name", f"服务器{idx+1}")
        base_url = server.get("base_url")
        token = server.get("token")
        
        manager = CPAManager(base_url, token, name, max_workers=max_workers)
        
        if upload_type == "directory":
            success, failed = manager.upload_from_directory(source)
        else:  # zip
            success, failed = manager.upload_from_zip(source)
        
        if success > 0 or failed > 0:
            results.append((name, success, failed))
        
        if idx < len(selected_indices) - 1:
            print()
            input("按 Enter 继续下一个服务器...")
    
    # 显示汇总
    if results:
        print()
        print("=" * 70)
        print("📊 上传汇总")
        print("=" * 70)
        print()
        for name, success, failed in results:
            total = success + failed
            print(f"📤 {name}:")
            print(f"   总计: {total} 个文件")
            print(f"   成功: {success} 个 ✅")
            if failed > 0:
                print(f"   失败: {failed} 个 ❌")
        print()


def show_servers_action(servers: List[Dict]):
    """显示 CPA 服务器列表"""
    print()
    print("=" * 70)
    print("CPA 服务器列表")
    print("=" * 70)
    print()
    
    for i, server in enumerate(servers, 1):
        name = server.get("name", f"服务器{i}")
        url = server.get("base_url", "")
        token = server.get("token", "")
        enable_revive = server.get("enable_token_revive", True)
        
        token_display = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else token
        
        print(f"{i}. {name}")
        print(f"   URL: {url}")
        print(f"   Token: {token_display}")
        print(f"   Token 复活: {'✅ 已开启' if enable_revive else '❌ 已关闭'}")
        print()


def download_config_action(servers: List[Dict], selected_indices: List[int]):
    """执行下载 config.yaml 操作"""
    for idx in selected_indices:
        server = servers[idx]
        name = server.get("name", f"服务器{idx+1}")
        base_url = server.get("base_url")
        token = server.get("token")
        
        print()
        print("=" * 70)
        print(f"下载 config.yaml - {name}")
        print("=" * 70)
        print()
        
        # 生成文件名
        safe_name = name.replace(" ", "_").replace("/", "_")
        output_path = f"config_{safe_name}.yaml"
        
        manager = CPAManager(base_url, token, name)
        success, message = manager.download_config_yaml(output_path)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        if idx < len(selected_indices) - 1:
            print()
            input("按 Enter 继续下一个服务器...")


def manage_openai_compatibility_action(servers: List[Dict], selected_indices: List[int]):
    """管理 OpenAI 兼容提供商"""
    if len(selected_indices) != 1:
        print("❌ 请选择单个服务器进行配置管理")
        return
    
    idx = selected_indices[0]
    server = servers[idx]
    name = server.get("name", f"服务器{idx+1}")
    base_url = server.get("base_url")
    token = server.get("token")
    
    manager = CPAManager(base_url, token, name)
    
    while True:
        print()
        print("=" * 70)
        print(f"OpenAI 兼容提供商管理 - {name}")
        print("=" * 70)
        print()
        print("操作:")
        print("  1. 查看提供商列表")
        print("  2. 添加提供商")
        print("  3. 更新提供商")
        print("  4. 删除提供商")
        print("  0. 返回主菜单")
        print()
        
        choice = input("请选择操作: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            # 查看列表
            print()
            print("📋 获取提供商列表...")
            ok, result = manager.get_openai_compatibility()
            
            if ok:
                providers = result
                if not providers:
                    print("⚠️  没有配置任何提供商")
                else:
                    print(f"✅ 找到 {len(providers)} 个提供商:")
                    print()
                    for i, p in enumerate(providers, 1):
                        print(f"{i}. {p.get('name', '未命名')}")
                        print(f"   Base URL: {p.get('base-url', 'N/A')}")
                        
                        api_keys = p.get('api-key-entries', [])
                        print(f"   API Keys: {len(api_keys)} 个")
                        
                        models = p.get('models', [])
                        if models:
                            print(f"   Models: {len(models)} 个")
                            for m in models[:3]:
                                alias = m.get('alias', m.get('name'))
                                print(f"     - {alias}")
                            if len(models) > 3:
                                print(f"     ... 还有 {len(models) - 3} 个")
                        
                        headers = p.get('headers', {})
                        if headers:
                            print(f"   Headers: {len(headers)} 个")
                        
                        print()
            else:
                print(f"❌ {result}")
        
        elif choice == "2":
            # 添加提供商
            print()
            print("=" * 70)
            print("添加 OpenAI 兼容提供商")
            print("=" * 70)
            print()
            
            provider_name = input("提供商名称 (如 openrouter): ").strip()
            if not provider_name:
                print("❌ 名称不能为空")
                continue
            
            base_url = input("Base URL (如 https://openrouter.ai/api/v1): ").strip()
            if not base_url:
                print("❌ Base URL 不能为空")
                continue
            
            api_key = input("API Key: ").strip()
            if not api_key:
                print("❌ API Key 不能为空")
                continue
            
            proxy_url = input("Proxy URL (可选，直接回车跳过): ").strip()
            
            # 构建提供商配置
            provider = {
                "name": provider_name,
                "base-url": base_url,
                "api-key-entries": [
                    {
                        "api-key": api_key,
                        "proxy-url": proxy_url
                    }
                ],
                "models": []
            }
            
            # 询问是否添加模型映射
            add_models = input("是否添加模型映射? (y/n): ").strip().lower()
            if add_models == 'y':
                models = []
                while True:
                    model_name = input("  模型名称 (直接回车结束): ").strip()
                    if not model_name:
                        break
                    
                    model_alias = input("  模型别名 (可选): ").strip()
                    
                    model_entry = {"name": model_name}
                    if model_alias:
                        model_entry["alias"] = model_alias
                    
                    models.append(model_entry)
                
                if models:
                    provider["models"] = models
            
            print()
            print("📤 添加提供商...")
            ok, message = manager.add_openai_compatibility(provider)
            
            if ok:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        
        elif choice == "3":
            # 更新提供商
            print()
            print("📋 获取提供商列表...")
            ok, result = manager.get_openai_compatibility()
            
            if not ok:
                print(f"❌ {result}")
                continue
            
            providers = result
            if not providers:
                print("⚠️  没有可更新的提供商")
                continue
            
            print()
            print("现有提供商:")
            for i, p in enumerate(providers, 1):
                print(f"  {i}. {p.get('name', '未命名')}")
            print()
            
            try:
                idx = int(input("选择要更新的提供商 (序号): ").strip()) - 1
                if idx < 0 or idx >= len(providers):
                    print("❌ 无效的选择")
                    continue
            except ValueError:
                print("❌ 请输入数字")
                continue
            
            old_provider = providers[idx]
            provider_name = old_provider.get('name')
            
            print()
            print(f"更新提供商: {provider_name}")
            print("(直接回车保持原值)")
            print()
            
            new_base_url = input(f"Base URL [{old_provider.get('base-url')}]: ").strip()
            if not new_base_url:
                new_base_url = old_provider.get('base-url')
            
            # 简化更新：只更新 base-url
            updated_provider = old_provider.copy()
            updated_provider['base-url'] = new_base_url
            
            print()
            print("📤 更新提供商...")
            ok, message = manager.update_openai_compatibility(provider_name, updated_provider)
            
            if ok:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        
        elif choice == "4":
            # 删除提供商
            print()
            print("📋 获取提供商列表...")
            ok, result = manager.get_openai_compatibility()
            
            if not ok:
                print(f"❌ {result}")
                continue
            
            providers = result
            if not providers:
                print("⚠️  没有可删除的提供商")
                continue
            
            print()
            print("现有提供商:")
            for i, p in enumerate(providers, 1):
                print(f"  {i}. {p.get('name', '未命名')}")
            print()
            
            try:
                idx = int(input("选择要删除的提供商 (序号): ").strip()) - 1
                if idx < 0 or idx >= len(providers):
                    print("❌ 无效的选择")
                    continue
            except ValueError:
                print("❌ 请输入数字")
                continue
            
            provider_name = providers[idx].get('name')
            
            confirm = input(f"确认删除 '{provider_name}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                continue
            
            print()
            print("🗑️  删除提供商...")
            ok, message = manager.delete_openai_compatibility(provider_name)
            
            if ok:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        
        else:
            print("❌ 无效的选择")
        
        if choice in ["1", "2", "3", "4"]:
            input("\n按 Enter 继续...")


def main():
    """主函数（交互式菜单）"""
    # 加载配置
    config = load_config("config.json")
    servers = config.get("cpa_servers", [])
    max_workers = config.get("max_workers", 10)
    
    if not servers:
        print("❌ 配置文件中没有 CPA 服务器")
        sys.exit(1)
    
    # 主循环
    while True:
        show_menu()
        
        choice = input("请选择功能: ").strip()
        
        if choice == "0":
            print("\n👋 再见！")
            break
        
        elif choice == "1":
            # 检查账号使用情况
            selected = select_cpa_servers(servers)
            check_usage_action(servers, selected, max_workers)
            input("\n按 Enter 返回主菜单...")
        
        elif choice == "2":
            # 下载并打包
            selected = select_cpa_servers(servers)
            download_action(servers, selected, max_workers)
            input("\n按 Enter 返回主菜单...")
        
        elif choice == "3":
            # 批量上传
            selected = select_cpa_servers(servers)
            upload_action(servers, selected, max_workers)
            input("\n按 Enter 返回主菜单...")
        
        elif choice == "4":
            # 下载 config.yaml
            selected = select_cpa_servers(servers)
            download_config_action(servers, selected)
            input("\n按 Enter 返回主菜单...")
        
        elif choice == "5":
            # 管理 OpenAI 兼容提供商
            selected = select_cpa_servers(servers)
            manage_openai_compatibility_action(servers, selected)
            # 此函数内部已有返回提示
        
        elif choice == "6":
            # 查看服务器列表
            show_servers_action(servers)
            input("\n按 Enter 返回主菜单...")
        
        else:
            print("❌ 无效的选择，请重新输入")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
