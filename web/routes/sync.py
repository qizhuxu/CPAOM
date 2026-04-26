"""
同步备份路由
"""

from flask import Blueprint, jsonify
from flask_login import login_required
from utils.config_manager import ConfigManager
from utils.cpa_client import CPAClient
from utils.db_service import DatabaseService
import os
import time

bp = Blueprint('sync', __name__, url_prefix='/api/sync')
config_manager = ConfigManager()
db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))


@bp.route('/<server_id>/auth-files', methods=['POST'])
@login_required
def sync_auth_files(server_id):
    """同步认证文件"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    start_time = time.time()
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        synced = 0
        failed = 0
        
        for file_info in files:
            filename = file_info.get("name")
            email = file_info.get("email", "")
            disabled = file_info.get("disabled", False)
            
            if not filename:
                failed += 1
                continue
            
            # 下载完整文件
            auth_data = client.download_auth_file(filename)
            
            if auth_data:
                # 保存到数据库
                db_service.save_auth_file_backup(
                    server_id=server_id,
                    server_name=server["name"],
                    filename=filename,
                    email=email,
                    auth_data=auth_data,
                    disabled=disabled
                )
                synced += 1
            else:
                failed += 1
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 记录同步日志
        db_service.add_sync_log(
            server_id=server_id,
            server_name=server["name"],
            sync_type="auth_files",
            status="success" if failed == 0 else "partial",
            files_synced=synced,
            files_failed=failed,
            duration_ms=duration_ms
        )
        
        return jsonify({
            "success": True,
            "synced": synced,
            "failed": failed,
            "total": len(files),
            "duration_ms": duration_ms
        })
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        
        db_service.add_sync_log(
            server_id=server_id,
            server_name=server["name"],
            sync_type="auth_files",
            status="failed",
            error_message=str(e),
            duration_ms=duration_ms
        )
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/logs', methods=['GET'])
@login_required
def get_sync_logs():
    """获取同步日志"""
    try:
        logs = db_service.get_sync_logs(limit=50)
        
        return jsonify({
            "success": True,
            "logs": logs
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
