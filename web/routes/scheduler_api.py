"""
调度器管理 API
"""

import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from utils.scheduler import get_all_jobs, add_sync_task, remove_sync_task
from utils.config_manager import ConfigManager
from utils.db_service import DatabaseService
import os

bp = Blueprint('scheduler_api', __name__, url_prefix='/api/scheduler')
config_manager = ConfigManager()
db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))
logger = logging.getLogger(__name__)


@bp.route('/jobs', methods=['GET'])
@login_required
def list_jobs():
    """获取所有定时任务"""
    try:
        jobs = get_all_jobs()
        
        return jsonify({
            "success": True,
            "jobs": jobs,
            "total": len(jobs)
        })
    
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/reload', methods=['POST'])
@login_required
def reload_tasks():
    """重新加载所有任务"""
    try:
        from flask import current_app
        from utils.scheduler import load_sync_tasks
        
        load_sync_tasks(
            current_app._get_current_object(),
            db_service,
            config_manager
        )
        
        logger.info(f"用户 {current_user.username} 重新加载了所有任务")
        
        return jsonify({
            "success": True,
            "message": "任务已重新加载"
        })
    
    except Exception as e:
        logger.error(f"重新加载任务失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
