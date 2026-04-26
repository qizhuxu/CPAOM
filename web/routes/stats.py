"""
统计信息路由
"""

import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from utils.config_manager import ConfigManager
from utils.cpa_client import CPAClient
from utils.db_service import DatabaseService
import os

bp = Blueprint('stats', __name__, url_prefix='/api/stats')
config_manager = ConfigManager()
db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))
logger = logging.getLogger(__name__)


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
