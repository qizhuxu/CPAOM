"""
账号管理路由
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from utils.config_manager import ConfigManager
from utils.cpa_client import CPAClient
from concurrent.futures import ThreadPoolExecutor, as_completed

bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')
config_manager = ConfigManager()


@bp.route('/<server_id>', methods=['GET'])
@login_required
def list_accounts(server_id):
    """获取账号列表"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        return jsonify({
            "success": True,
            "accounts": files,
            "total": len(files)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/check-usage', methods=['POST'])
@login_required
def check_usage(server_id):
    """批量检查使用情况"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        # 过滤活跃账号
        active_files = [f for f in files if not f.get("disabled")]
        
        results = []
        settings = config_manager.get_settings()
        max_workers = settings.get("max_workers", 10)
        
        def check_single(file_info):
            auth_index = file_info.get("auth_index", "")
            email = file_info.get("email", "")
            
            if not auth_index:
                return None
            
            ok, usage_data = client.check_usage(auth_index)
            
            if ok:
                return {
                    "email": email,
                    "auth_index": auth_index,
                    "usage": usage_data,
                    "status": "success"
                }
            else:
                return {
                    "email": email,
                    "auth_index": auth_index,
                    "error": usage_data,
                    "status": "error"
                }
        
        # 并发检查
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(check_single, f): f for f in active_files}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        
        return jsonify({
            "success": True,
            "results": results,
            "total": len(results)
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/<filename>/disable', methods=['POST'])
@login_required
def disable_account(server_id, filename):
    """禁用账号"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        ok, message = client.disable_auth_file(filename)
        
        return jsonify({
            "success": ok,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/<filename>/enable', methods=['POST'])
@login_required
def enable_account(server_id, filename):
    """启用账号"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        ok, message = client.enable_auth_file(filename)
        
        return jsonify({
            "success": ok,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/<filename>/revive', methods=['POST'])
@login_required
def revive_token(server_id, filename):
    """复活 Token"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    data = request.get_json()
    email = data.get("email", "")
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        settings = config_manager.get_settings()
        max_attempts = settings.get("token_revive_max_attempts", 3)
        
        ok, message = client.revive_token(email, filename, max_attempts)
        
        return jsonify({
            "success": ok,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
