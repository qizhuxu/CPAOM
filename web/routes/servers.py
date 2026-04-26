"""
服务器管理路由
"""

import logging
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from utils.config_manager import ConfigManager
from utils.cpa_client import CPAClient
import uuid

bp = Blueprint('servers', __name__, url_prefix='/api/servers')
config_manager = ConfigManager()
logger = logging.getLogger(__name__)


@bp.route('/', methods=['GET'])
@login_required
def list_servers():
    """获取服务器列表"""
    logger.debug(f"用户 {current_user.username} 请求服务器列表")
    servers = config_manager.get_servers()
    logger.info(f"返回 {len(servers)} 个服务器配置")
    return jsonify({"servers": servers})


@bp.route('/', methods=['POST'])
@login_required
def add_server():
    """添加服务器"""
    data = request.get_json()
    
    logger.info(f"用户 {current_user.username} 尝试添加服务器: {data.get('name')}")
    
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
        
        logger.info(f"服务器添加成功: {server['name']} (ID: {server_id}), 找到 {len(files)} 个认证文件")
        
        return jsonify({
            "success": True,
            "message": "服务器添加成功",
            "server": server,
            "file_count": len(files)
        })
    except Exception as e:
        logger.error(f"添加服务器失败: {server.get('name', 'Unknown')} - {str(e)}")
        return jsonify({
            "success": False,
            "message": f"连接失败: {str(e)}"
        }), 400


@bp.route('/<server_id>', methods=['PUT'])
@login_required
def update_server(server_id):
    """更新服务器"""
    data = request.get_json()
    
    logger.info(f"用户 {current_user.username} 更新服务器: {server_id}")
    
    try:
        config_manager.update_server(server_id, data)
        logger.info(f"服务器更新成功: {server_id}")
        return jsonify({
            "success": True,
            "message": "服务器更新成功"
        })
    except Exception as e:
        logger.error(f"更新服务器失败: {server_id} - {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@bp.route('/<server_id>', methods=['DELETE'])
@login_required
def delete_server(server_id):
    """删除服务器"""
    logger.info(f"用户 {current_user.username} 删除服务器: {server_id}")
    
    try:
        config_manager.delete_server(server_id)
        logger.info(f"服务器删除成功: {server_id}")
        return jsonify({
            "success": True,
            "message": "服务器删除成功"
        })
    except Exception as e:
        logger.error(f"删除服务器失败: {server_id} - {str(e)}")
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
