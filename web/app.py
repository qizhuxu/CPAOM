#!/usr/bin/env python3
"""
CPA 账号管理系统 - Web 版
Flask 应用主入口
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from utils.db_service import DatabaseService
from utils.cpa_client import CPAClient
from utils.scheduler import init_scheduler
from routes import auth, servers, accounts, operations, stats, sync, tasks

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'data/cpa_manager.db')

# 初始化数据库服务
db_service = DatabaseService(app.config['DATABASE_PATH'])
db_service.init_db()

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'


class User(UserMixin):
    """用户模型"""
    def __init__(self, username):
        self.id = username
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    # 简单实现：只有一个管理员用户
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    if user_id == admin_username:
        return User(user_id)
    return None


# 注册蓝图
app.register_blueprint(auth.bp)
app.register_blueprint(servers.bp)
app.register_blueprint(accounts.bp)
app.register_blueprint(operations.bp)
app.register_blueprint(stats.bp)
app.register_blueprint(sync.bp)
app.register_blueprint(tasks.bp)


@app.route('/')
@login_required
def index():
    """首页 - 仪表板"""
    return render_template('dashboard.html')


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


@app.context_processor
def inject_globals():
    """注入全局变量到模板"""
    return {
        'app_name': 'CPA 账号管理系统',
        'current_year': datetime.now().year
    }


# 初始化定时任务调度器
if os.getenv('FLASK_ENV') != 'development' or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
    init_scheduler(app, db_service)


if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)
    
    # 运行应用
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           CPA 账号管理系统 - Web 版                          ║
║                                                              ║
║  访问地址: http://{host}:{port}                        ║
║  管理员账号: {os.getenv('ADMIN_USERNAME', 'admin')}                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)
