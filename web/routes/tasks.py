"""
定时任务路由
"""

from flask import Blueprint, jsonify
from flask_login import login_required

bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


@bp.route('/', methods=['GET'])
@login_required
def list_tasks():
    """获取定时任务列表"""
    # TODO: 实现定时任务列表
    return jsonify({
        "success": True,
        "tasks": []
    })


@bp.route('/', methods=['POST'])
@login_required
def create_task():
    """创建定时任务"""
    # TODO: 实现创建定时任务
    return jsonify({
        "success": True,
        "message": "功能开发中"
    })
