"""
Token 刷新配置路由
"""

import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils.config_manager import ConfigManager
from utils.db_service import DatabaseService
import os

bp = Blueprint('token_refresh', __name__, url_prefix='/api/token-refresh')
config_manager = ConfigManager()
db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))
logger = logging.getLogger(__name__)


@bp.route('/config/<server_id>', methods=['GET'])
@login_required
def get_token_refresh_config(server_id):
    """获取 Token 刷新配置"""
    logger.info(f"用户 {current_user.username} 获取 Token 刷新配置: {server_id}")
    
    server = config_manager.get_server(server_id)
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        config = db_service.get_token_refresh_config(server_id)
        
        # 如果没有配置，返回默认值
        if not config:
            config = {
                'server_id': server_id,
                'enabled': False,
                'refresh_interval': 86400,  # 24小时
                'refresh_lead_time': 432000,  # 5天
                'max_retry_attempts': 3,
                'retry_interval': 300,  # 5分钟
                'auto_disable_on_failure': True
            }
        
        return jsonify({
            "success": True,
            "config": config
        })
    
    except Exception as e:
        logger.error(f"获取 Token 刷新配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/config/<server_id>', methods=['POST', 'PUT'])
@login_required
def save_token_refresh_config(server_id):
    """保存 Token 刷新配置"""
    logger.info(f"用户 {current_user.username} 保存 Token 刷新配置: {server_id}")
    
    server = config_manager.get_server(server_id)
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    data = request.get_json()
    
    try:
        enabled = data.get('enabled', False)
        refresh_interval = data.get('refresh_interval', 86400)
        refresh_lead_time = data.get('refresh_lead_time', 432000)
        max_retry_attempts = data.get('max_retry_attempts', 3)
        retry_interval = data.get('retry_interval', 300)
        auto_disable_on_failure = data.get('auto_disable_on_failure', True)
        
        # 验证刷新间隔（最小1小时）
        if refresh_interval < 3600:
            return jsonify({
                "success": False,
                "error": "刷新间隔不能小于1小时（3600秒）"
            }), 400
        
        # 验证提前刷新时间（最小1小时）
        if refresh_lead_time < 3600:
            return jsonify({
                "success": False,
                "error": "提前刷新时间不能小于1小时（3600秒）"
            }), 400
        
        # 验证重试次数（1-10）
        if max_retry_attempts < 1 or max_retry_attempts > 10:
            return jsonify({
                "success": False,
                "error": "重试次数必须在1-10之间"
            }), 400
        
        db_service.save_token_refresh_config(
            server_id=server_id,
            enabled=enabled,
            refresh_interval=refresh_interval,
            refresh_lead_time=refresh_lead_time,
            max_retry_attempts=max_retry_attempts,
            retry_interval=retry_interval,
            auto_disable_on_failure=auto_disable_on_failure
        )
        
        # 记录审计日志
        db_service.add_audit_log(
            user=current_user.username,
            action='update_token_refresh_config',
            resource_type='server',
            resource_id=server_id,
            details={
                'enabled': enabled,
                'refresh_interval': refresh_interval,
                'refresh_lead_time': refresh_lead_time,
                'max_retry_attempts': max_retry_attempts,
                'retry_interval': retry_interval,
                'auto_disable_on_failure': auto_disable_on_failure
            }
        )
        
        # 更新调度器任务
        try:
            from flask import current_app
            from utils.scheduler import update_token_refresh_task, remove_token_refresh_task
            
            if enabled:
                # 启用定时刷新
                update_token_refresh_task(
                    current_app._get_current_object(),
                    db_service,
                    config_manager,
                    server_id,
                    server['name'],
                    refresh_interval
                )
                logger.info(f"已更新 Token 刷新任务: {server['name']}, 间隔 {refresh_interval} 秒")
            else:
                # 禁用定时刷新，移除任务
                remove_token_refresh_task(server_id)
                logger.info(f"已移除 Token 刷新任务: {server['name']}")
        except Exception as e:
            logger.warning(f"更新调度器任务失败: {e}")
        
        logger.info(f"Token 刷新配置已保存: {server['name']}")
        
        return jsonify({
            "success": True,
            "message": "Token 刷新配置已保存"
        })
    
    except Exception as e:
        logger.error(f"保存 Token 刷新配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/logs/<server_id>', methods=['GET'])
@login_required
def get_token_refresh_logs(server_id):
    """获取 Token 刷新日志"""
    try:
        limit = int(request.args.get('limit', 100))
        
        logs = db_service.get_token_refresh_logs(server_id, limit)
        
        return jsonify({
            "success": True,
            "logs": logs
        })
    
    except Exception as e:
        logger.error(f"获取 Token 刷新日志失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/refresh/<server_id>/<filename>', methods=['POST'])
@login_required
def manual_refresh_token(server_id, filename):
    """手动刷新单个 Token"""
    logger.info(f"用户 {current_user.username} 手动刷新 Token: {server_id}/{filename}")
    
    server = config_manager.get_server(server_id)
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    data = request.get_json() or {}
    email = data.get('email', '')
    
    try:
        from utils.cpa_client import CPAClient
        import time
        
        start_time = time.time()
        
        client = CPAClient(server["base_url"], server["token"], server["name"])
        
        # 获取刷新配置
        refresh_config = db_service.get_token_refresh_config(server_id)
        max_attempts = refresh_config.get('max_retry_attempts', 3) if refresh_config else 3
        
        # 执行刷新
        success, message = client.refresh_token(email, filename, max_attempts)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 记录日志
        db_service.add_token_refresh_log(
            server_id=server_id,
            filename=filename,
            email=email,
            status='success' if success else 'failed',
            error_message=None if success else message,
            attempts=max_attempts if not success else 1,
            duration_ms=duration_ms
        )
        
        if success:
            # 刷新成功后同步账号数据
            try:
                ok, auth_data = client.download_auth_file(filename)
                if ok:
                    db_service.save_auth_file_backup(
                        server_id=server_id,
                        server_name=server['name'],
                        filename=filename,
                        email=email,
                        auth_data=auth_data,
                        disabled=False
                    )
            except Exception as e:
                logger.warning(f"刷新后同步数据失败: {e}")
            
            return jsonify({
                "success": True,
                "message": message
            })
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 400
    
    except Exception as e:
        logger.error(f"手动刷新 Token 失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
