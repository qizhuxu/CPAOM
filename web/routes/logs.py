"""
日志查看路由
提供实时日志流和历史日志查看
"""

import os
import time
from flask import Blueprint, Response, jsonify, stream_with_context, request
from flask_login import login_required
from collections import deque
from threading import Lock

bp = Blueprint('logs', __name__, url_prefix='/api/logs')

# 日志缓冲区（保存最近的日志）
log_buffer = deque(maxlen=1000)
log_lock = Lock()


class LogHandler:
    """自定义日志处理器，用于捕获日志到缓冲区"""
    
    def __init__(self):
        self.subscribers = []
        self.lock = Lock()
    
    def emit(self, record):
        """发送日志记录"""
        log_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage()
        }
        
        # 添加到缓冲区
        with log_lock:
            log_buffer.append(log_entry)
        
        # 通知所有订阅者
        with self.lock:
            for subscriber in self.subscribers:
                try:
                    subscriber.put(log_entry)
                except:
                    pass
    
    def subscribe(self, queue):
        """订阅日志"""
        with self.lock:
            self.subscribers.append(queue)
    
    def unsubscribe(self, queue):
        """取消订阅"""
        with self.lock:
            if queue in self.subscribers:
                self.subscribers.remove(queue)


# 全局日志处理器
log_handler = LogHandler()


@bp.route('/stream')
@login_required
def stream_logs():
    """实时日志流 (Server-Sent Events)"""
    
    def generate():
        """生成日志流"""
        import queue
        
        # 创建订阅队列
        q = queue.Queue(maxsize=100)
        log_handler.subscribe(q)
        
        try:
            # 首先发送缓冲区中的历史日志
            with log_lock:
                for log_entry in log_buffer:
                    yield f"data: {format_log_entry(log_entry)}\n\n"
            
            # 然后持续发送新日志
            while True:
                try:
                    log_entry = q.get(timeout=30)  # 30秒超时，用于保持连接
                    yield f"data: {format_log_entry(log_entry)}\n\n"
                except queue.Empty:
                    # 发送心跳保持连接
                    yield f": heartbeat\n\n"
        except GeneratorExit:
            pass
        finally:
            log_handler.unsubscribe(q)
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@bp.route('/history')
@login_required
def get_history():
    """获取历史日志"""
    limit = int(request.args.get('limit', 100))
    level = request.args.get('level', None)
    
    with log_lock:
        logs = list(log_buffer)
    
    # 过滤日志级别
    if level:
        logs = [log for log in logs if log['level'] == level]
    
    # 限制数量
    logs = logs[-limit:]
    
    return jsonify({
        'success': True,
        'logs': logs,
        'total': len(logs)
    })


@bp.route('/clear', methods=['POST'])
@login_required
def clear_logs():
    """清空日志缓冲区"""
    with log_lock:
        log_buffer.clear()
    
    return jsonify({
        'success': True,
        'message': '日志已清空'
    })


def format_log_entry(log_entry):
    """格式化日志条目为 JSON 字符串"""
    import json
    return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(app):
    """设置日志系统"""
    import logging
    
    # 创建自定义处理器
    class FlaskLogHandler(logging.Handler):
        def emit(self, record):
            log_handler.emit(record)
    
    # 添加处理器到 Flask 应用日志
    flask_handler = FlaskLogHandler()
    flask_handler.setLevel(logging.INFO)
    
    # 设置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    flask_handler.setFormatter(formatter)
    
    # 添加到 Flask 日志
    app.logger.addHandler(flask_handler)
    app.logger.setLevel(logging.INFO)
    
    # 同时添加到根日志记录器，捕获所有日志
    logging.getLogger().addHandler(flask_handler)
    logging.getLogger().setLevel(logging.INFO)
    
    app.logger.info('日志系统已初始化')
