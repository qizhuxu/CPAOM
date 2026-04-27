"""
同步配置路由
"""

import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils.config_manager import ConfigManager
from utils.db_service import DatabaseService
import os

bp = Blueprint('sync_config', __name__, url_prefix='/api/sync-config')
config_manager = ConfigManager()
db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))
logger = logging.getLogger(__name__)


@bp.route('/<server_id>', methods=['GET'])
@login_required
def get_sync_config(server_id):
    """获取服务器同步配置"""
    logger.info(f"用户 {current_user.username} 获取同步配置: {server_id}")
    
    server = config_manager.get_server(server_id)
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        config = db_service.get_sync_config(server_id)
        
        # 如果没有配置，返回默认值
        if not config:
            config = {
                'server_id': server_id,
                'sync_interval': 3600,  # 1小时
                'auto_disable_100_percent': False,
                'auto_disable_401': True,
                'auto_delete_401_files': False,
                'auto_enable_reset_accounts': False,
                'fetch_auth_content': True,
                'max_workers': 10,
                'keep_sync_logs': 100,
                'last_sync_at': None,
                'next_sync_at': None
            }
        
        return jsonify({
            "success": True,
            "config": config
        })
    
    except Exception as e:
        logger.error(f"获取同步配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>', methods=['POST', 'PUT'])
@login_required
def save_sync_config(server_id):
    """保存服务器同步配置"""
    logger.info(f"用户 {current_user.username} 保存同步配置: {server_id}")
    
    server = config_manager.get_server(server_id)
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    data = request.get_json()
    
    try:
        sync_interval = data.get('sync_interval', 3600)
        auto_disable_100_percent = data.get('auto_disable_100_percent', False)
        auto_disable_401 = data.get('auto_disable_401', True)
        auto_delete_401_files = data.get('auto_delete_401_files', False)
        auto_enable_reset_accounts = data.get('auto_enable_reset_accounts', False)
        fetch_auth_content = data.get('fetch_auth_content', True)
        max_workers = data.get('max_workers', 10)
        keep_sync_logs = data.get('keep_sync_logs', 100)
        
        # 验证同步间隔（0表示禁用，或最小5分钟）
        if sync_interval > 0 and sync_interval < 300:
            return jsonify({
                "success": False,
                "error": "同步间隔不能小于5分钟（300秒）"
            }), 400
        
        # 验证并发线程数（1-50）
        if max_workers < 1 or max_workers > 50:
            return jsonify({
                "success": False,
                "error": "并发线程数必须在1-50之间"
            }), 400
        
        # 验证保留日志数量（10-1000）
        if keep_sync_logs < 10 or keep_sync_logs > 1000:
            return jsonify({
                "success": False,
                "error": "保留日志数量必须在10-1000之间"
            }), 400
        
        db_service.save_sync_config(
            server_id=server_id,
            sync_interval=sync_interval,
            auto_disable_100_percent=auto_disable_100_percent,
            auto_disable_401=auto_disable_401,
            auto_delete_401_files=auto_delete_401_files,
            auto_enable_reset_accounts=auto_enable_reset_accounts,
            fetch_auth_content=fetch_auth_content,
            max_workers=max_workers,
            keep_sync_logs=keep_sync_logs
        )
        
        # 记录审计日志
        db_service.add_audit_log(
            user=current_user.username,
            action='update_sync_config',
            resource_type='server',
            resource_id=server_id,
            details={
                'sync_interval': sync_interval,
                'auto_disable_100_percent': auto_disable_100_percent,
                'auto_disable_401': auto_disable_401,
                'auto_delete_401_files': auto_delete_401_files,
                'auto_enable_reset_accounts': auto_enable_reset_accounts,
                'fetch_auth_content': fetch_auth_content,
                'max_workers': max_workers
            }
        )
        
        # 更新调度器任务
        try:
            from flask import current_app
            from utils.scheduler import update_sync_task, remove_sync_task
            
            if sync_interval > 0:
                # 启用定时同步
                update_sync_task(
                    current_app._get_current_object(),
                    db_service,
                    config_manager,
                    server_id,
                    server['name'],
                    sync_interval
                )
                logger.info(f"已更新调度器任务: {server['name']}, 间隔 {sync_interval} 秒")
            else:
                # 禁用定时同步，移除任务
                remove_sync_task(server_id)
                logger.info(f"已移除调度器任务: {server['name']}")
        except Exception as e:
            logger.warning(f"更新调度器任务失败: {e}")
        
        logger.info(f"同步配置已保存: {server['name']}")
        
        return jsonify({
            "success": True,
            "message": "同步配置已保存"
        })
    
    except Exception as e:
        logger.error(f"保存同步配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/batch', methods=['POST'])
@login_required
def batch_save_sync_config():
    """批量保存同步配置（用于添加服务器时）"""
    logger.info(f"用户 {current_user.username} 批量保存同步配置")
    
    data = request.get_json()
    configs = data.get('configs', [])
    
    try:
        for config in configs:
            server_id = config.get('server_id')
            
            if not server_id:
                continue
            
            db_service.save_sync_config(
                server_id=server_id,
                sync_interval=config.get('sync_interval', 3600),
                auto_disable_100_percent=config.get('auto_disable_100_percent', False),
                auto_disable_401=config.get('auto_disable_401', True),
                auto_delete_401_files=config.get('auto_delete_401_files', False),
                auto_enable_reset_accounts=config.get('auto_enable_reset_accounts', False),
                fetch_auth_content=config.get('fetch_auth_content', True),
                max_workers=config.get('max_workers', 10)
            )
        
        return jsonify({
            "success": True,
            "message": f"已保存 {len(configs)} 个同步配置"
        })
    
    except Exception as e:
        logger.error(f"批量保存同步配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
