"""
统计信息路由
"""

import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from utils.config_manager import ConfigManager
from utils.cpa_client import CPAClient
from utils.db_service import DatabaseService
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os

bp = Blueprint('stats', __name__, url_prefix='/api/stats')
config_manager = ConfigManager()
db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))
logger = logging.getLogger(__name__)


@bp.route('/servers-quick', methods=['GET'])
@login_required
def servers_quick():
    """快速获取服务器列表（从本地数据库读取）"""
    logger.debug(f"用户 {current_user.username} 请求快速服务器列表")
    
    try:
        servers = config_manager.get_servers()
        
        if not servers:
            return jsonify({
                "success": True,
                "servers": []
            })
        
        servers_info = []
        for server in servers:
            server_id = server['id']
            server_name = server['name']
            
            # 从本地数据库获取统计信息
            try:
                stats = db_service.get_server_stats(server_id)
                sync_config = db_service.get_sync_config(server_id)
                
                if stats:
                    # 使用本地统计数据
                    servers_info.append({
                        'id': server_id,
                        'name': server_name,
                        'base_url': server['base_url'],
                        'enabled': server.get('enabled', True),
                        'stats': {
                            'total': stats['total_accounts'],
                            'active': stats['active_accounts'],
                            'disabled': stats['disabled_accounts'],
                            'avg_usage_percent': stats['avg_usage_percent'],
                            'usage_checked_count': stats['usage_checked_count']
                        },
                        'status': 'healthy' if stats['disabled_accounts'] == 0 else 'warning',
                        'last_sync': sync_config['last_sync_at'] if sync_config else None,
                        'next_sync': sync_config['next_sync_at'] if sync_config else None,
                        'local_backup_count': stats['total_accounts'],
                        'token_revive_enabled': server.get('enable_token_revive', False),
                        'from_cache': True
                    })
                else:
                    # 没有统计数据，返回空数据
                    servers_info.append({
                        'id': server_id,
                        'name': server_name,
                        'base_url': server['base_url'],
                        'enabled': server.get('enabled', True),
                        'stats': {
                            'total': 0,
                            'active': 0,
                            'disabled': 0,
                            'avg_usage_percent': 0,
                            'usage_checked_count': 0
                        },
                        'status': 'warning',
                        'last_sync': None,
                        'next_sync': None,
                        'local_backup_count': 0,
                        'token_revive_enabled': server.get('enable_token_revive', False),
                        'from_cache': True
                    })
            except Exception as e:
                logger.warning(f"获取服务器 {server_name} 本地数据失败: {e}")
                servers_info.append({
                    'id': server_id,
                    'name': server_name,
                    'base_url': server['base_url'],
                    'enabled': server.get('enabled', True),
                    'stats': {
                        'total': 0,
                        'active': 0,
                        'disabled': 0,
                        'avg_usage_percent': 0,
                        'usage_checked_count': 0
                    },
                    'status': 'warning',
                    'last_sync': None,
                    'next_sync': None,
                    'local_backup_count': 0,
                    'token_revive_enabled': server.get('enable_token_revive', False),
                    'from_cache': True
                })
        
        # 按名称排序
        servers_info.sort(key=lambda x: x['name'])
        
        logger.info(f"快速服务器列表获取完成: {len(servers_info)} 个服务器（本地数据）")
        
        return jsonify({
            "success": True,
            "servers": servers_info,
            "from_cache": True
        })
    
    except Exception as e:
        logger.error(f"获取快速服务器列表失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/server-live/<server_id>', methods=['GET'])
@login_required
def server_live_stats(server_id):
    """获取单个服务器的实时统计（异步调用）"""
    logger.debug(f"用户 {current_user.username} 请求服务器 {server_id} 实时统计")
    
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        total = len(files)
        active = sum(1 for f in files if not f.get("disabled"))
        disabled = total - active
        
        # 计算总使用率（仅活跃账号）
        total_usage_percent = 0
        usage_checked_count = 0
        
        active_files = [f for f in files if not f.get("disabled")]
        
        for file_info in active_files[:10]:  # 只检查前10个账号以提高速度
            auth_index = file_info.get("auth_index", "")
            if not auth_index:
                continue
            
            try:
                ok, usage_data = client.check_usage(auth_index)
                if ok:
                    rate_limit = usage_data.get("rate_limit", {})
                    primary = rate_limit.get("primary_window", {})
                    used_percent = primary.get("used_percent", 0)
                    total_usage_percent += used_percent
                    usage_checked_count += 1
            except:
                continue
        
        # 计算平均使用率
        avg_usage_percent = 0
        if usage_checked_count > 0:
            avg_usage_percent = total_usage_percent / usage_checked_count
        
        # 获取最近同步时间
        sync_logs = db_service.get_sync_logs_by_server(server_id, limit=1)
        last_sync = None
        if sync_logs:
            last_sync = sync_logs[0].get('created_at')
        
        # 获取本地备份数量
        local_accounts = db_service.get_auth_files_by_server(server_id)
        local_count = len(local_accounts)
        
        # 确定状态
        status = 'healthy'
        if disabled > 0:
            status = 'warning' if disabled / total <= 0.3 else 'error'
        
        return jsonify({
            "success": True,
            "server_id": server_id,
            "stats": {
                "total": total,
                "active": active,
                "disabled": disabled,
                "avg_usage_percent": round(avg_usage_percent, 1),
                "usage_checked_count": usage_checked_count
            },
            "status": status,
            "last_sync": last_sync,
            "local_backup_count": local_count,
            "online": True,
            "from_cache": False
        })
    
    except Exception as e:
        logger.warning(f"获取服务器 {server['name']} 实时统计失败: {e}")
        return jsonify({
            "success": False,
            "server_id": server_id,
            "online": False,
            "error": str(e)
        }), 200  # 返回200但标记为失败，避免前端报错
@login_required
def servers_overview():
    """快速获取所有服务器概览（并行）"""
    logger.debug(f"用户 {current_user.username} 请求服务器概览")
    
    try:
        servers = config_manager.get_servers()
        
        if not servers:
            return jsonify({
                "success": True,
                "servers": []
            })
        
        def get_server_info(server):
            """获取单个服务器信息"""
            server_id = server['id']
            server_name = server['name']
            
            try:
                client = CPAClient(server["base_url"], server["token"], server_name)
                files = client.get_auth_files()
                
                total = len(files)
                active = sum(1 for f in files if not f.get("disabled"))
                disabled = total - active
                
                # 获取最近同步时间
                sync_logs = db_service.get_sync_logs_by_server(server_id, limit=1)
                last_sync = None
                if sync_logs:
                    last_sync = sync_logs[0].get('created_at')
                
                # 获取本地备份数量
                local_accounts = db_service.get_auth_files_by_server(server_id)
                local_count = len(local_accounts)
                
                # 确定状态
                status = 'healthy'
                if disabled > 0:
                    status = 'warning' if disabled / total <= 0.3 else 'error'
                
                return {
                    'id': server_id,
                    'name': server_name,
                    'base_url': server['base_url'],
                    'enabled': server.get('enabled', True),
                    'stats': {
                        'total': total,
                        'active': active,
                        'disabled': disabled
                    },
                    'status': status,
                    'last_sync': last_sync,
                    'local_backup_count': local_count,
                    'token_revive_enabled': server.get('enable_token_revive', False),
                    'online': True
                }
            except Exception as e:
                logger.warning(f"获取服务器 {server_name} 信息失败: {e}")
                return {
                    'id': server_id,
                    'name': server_name,
                    'base_url': server['base_url'],
                    'enabled': server.get('enabled', True),
                    'stats': {
                        'total': 0,
                        'active': 0,
                        'disabled': 0
                    },
                    'status': 'error',
                    'last_sync': None,
                    'local_backup_count': 0,
                    'token_revive_enabled': server.get('enable_token_revive', False),
                    'online': False,
                    'error': str(e)
                }
        
        # 并行获取所有服务器信息
        settings = config_manager.get_settings()
        max_workers = min(len(servers), settings.get("max_workers", 10))
        
        servers_info = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(get_server_info, s): s for s in servers}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    servers_info.append(result)
        
        # 按名称排序
        servers_info.sort(key=lambda x: x['name'])
        
        logger.info(f"服务器概览获取完成: {len(servers_info)} 个服务器")
        
        return jsonify({
            "success": True,
            "servers": servers_info
        })
    
    except Exception as e:
        logger.error(f"获取服务器概览失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_stats():
    """仪表板统计"""
    logger.debug(f"用户 {current_user.username} 请求仪表板统计")
    
    try:
        servers = config_manager.get_servers()
        
        total_servers = len(servers)
        enabled_servers = sum(1 for s in servers if s.get("enabled", True))
        
        total_accounts = 0
        active_accounts = 0
        disabled_accounts = 0
        
        # 统计所有服务器的账号
        for server in servers:
            if not server.get("enabled", True):
                continue
            
            try:
                client = CPAClient(server["base_url"], server["token"], server["name"])
                files = client.get_auth_files()
                
                total_accounts += len(files)
                active_accounts += sum(1 for f in files if not f.get("disabled"))
                disabled_accounts += sum(1 for f in files if f.get("disabled"))
            except Exception as e:
                logger.warning(f"获取服务器 {server['name']} 统计失败: {e}")
                continue
        
        logger.info(f"仪表板统计: {total_servers} 个服务器, {total_accounts} 个账号")
        
        # 获取同步日志统计
        sync_logs = db_service.get_sync_logs(limit=10)
        recent_syncs = len([log for log in sync_logs if log.get("status") == "success"])
        
        # 获取审计日志统计
        audit_logs = db_service.get_audit_logs(limit=100)
        
        return jsonify({
            "success": True,
            "stats": {
                "total_servers": total_servers,
                "enabled_servers": enabled_servers,
                "total_accounts": total_accounts,
                "active_accounts": active_accounts,
                "disabled_accounts": disabled_accounts,
                "recent_syncs": recent_syncs,
                "recent_operations": len(audit_logs)
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/server/<server_id>', methods=['GET'])
@login_required
def server_stats(server_id):
    """服务器统计"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        total = len(files)
        active = sum(1 for f in files if not f.get("disabled"))
        disabled = sum(1 for f in files if f.get("disabled"))
        
        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "active": active,
                "disabled": disabled,
                "server_name": server["name"]
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
