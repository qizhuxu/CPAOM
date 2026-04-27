"""
日志查看路由
提供实时日志流和历史日志查看
"""

import os
import time
from flask import Blueprint, Response, jsonify, request
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
    import logging
    import queue
    
    stream_logger = logging.getLogger(__name__)
    stream_logger.info("新的日志流连接请求")
    
    def generate():
        """生成日志流"""
        q = queue.Queue(maxsize=100)
        log_handler.subscribe(q)
        
        try:
            # 发送连接成功消息（不发送历史日志，避免阻塞）
            yield "data: {\"message\": \"connected\"}\n\n"
            stream_logger.info("日志流连接建立")
            
            # 持续发送新日志
            while True:
                try:
                    log_entry = q.get(timeout=1)
                    yield f"data: {format_log_entry(log_entry)}\n\n"
                except queue.Empty:
                    yield ": heartbeat\n\n"
                except:
                    break
                    
        except GeneratorExit:
            stream_logger.info("客户端断开连接")
        finally:
            log_handler.unsubscribe(q)
            stream_logger.info("日志流已关闭")
    
    return Response(
        generate(),
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
    import sys
    
    # 创建自定义处理器用于 Web 日志流
    class WebLogHandler(logging.Handler):
        def emit(self, record):
            log_handler.emit(record)
    
    # 创建 Web 日志处理器
    web_handler = WebLogHandler()
    web_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器（保留原有的终端输出）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    web_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 清除现有的处理器（避免重复）
    app.logger.handlers.clear()
    logging.getLogger().handlers.clear()
    
    # 添加处理器到 Flask 应用日志
    app.logger.addHandler(web_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # 添加到根日志记录器，捕获所有模块的日志
    root_logger = logging.getLogger()
    root_logger.addHandler(web_handler)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # 防止日志重复（禁用传播到父记录器）
    app.logger.propagate = False
    
    app.logger.info('日志系统已初始化 - 支持控制台和 Web 界面双输出')
