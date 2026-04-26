"""
服务器管理路由
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from utils.config_manager import ConfigManager
from utils.cpa_client import CPAClient
import uuid

bp = Blueprint('servers', __name__, url_prefix='/api/servers')
config_manager = ConfigManager()


@bp.route('/', methods=['GET'])
@login_required
def list_servers():
    """获取服务器列表"""
    servers = config_manager.get_servers()
    return jsonify({"servers": servers})


@bp.route('/', methods=['POST'])
@login_required
def add_server():
    """添加服务器"""
    data = request.get_json()
    
    # 生成唯一 ID
    server_id = str(uuid.uuid4())[:8]
    
    server = {
        "id": server_id,
        "name": data.get("name"),
        "base_url": data.get("base_url"),
        "token": data.get("token"),
        "enable_token_revive": data.get("enable_token_revive", True),
        "enabled": data.get("enabled", True)
    }
    
    # 验证连接
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        config_manager.add_server(server)
        
        return jsonify({
            "success": True,
            "message": "服务器添加成功",
            "server": server,
            "file_count": len(files)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"连接失败: {str(e)}"
        }), 400


@bp.route('/<server_id>', methods=['PUT'])
@login_required
def update_server(server_id):
    """更新服务器"""
    data = request.get_json()
    
    try:
        config_manager.update_server(server_id, data)
        return jsonify({
            "success": True,
            "message": "服务器更新成功"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@bp.route('/<server_id>', methods=['DELETE'])
@login_required
def delete_server(server_id):
    """删除服务器"""
    try:
        config_manager.delete_server(server_id)
        return jsonify({
            "success": True,
            "message": "服务器删除成功"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@bp.route('/<server_id>/test', methods=['POST'])
@login_required
def test_connection(server_id):
    """测试服务器连接"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({
            "success": False,
            "message": "服务器不存在"
        }), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        return jsonify({
            "success": True,
            "message": "连接成功",
            "file_count": len(files)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"连接失败: {str(e)}"
        }), 400
