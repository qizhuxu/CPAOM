"""
认证路由
"""

import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, UserMixin

bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)


class User(UserMixin):
    """用户模型"""
    def __init__(self, username):
        self.id = username
        self.username = username


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.info(f"用户尝试登录: {username}")
        
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_username and password == admin_password:
            user = User(username)
            login_user(user, remember=True)
            
            logger.info(f"用户登录成功: {username}")
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            logger.warning(f"用户登录失败: {username} - 用户名或密码错误")
            flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """登出"""
    username = request.user.username if hasattr(request, 'user') else 'unknown'
    logger.info(f"用户登出: {username}")
    
    logout_user()
    flash('已成功登出', 'success')
    return redirect(url_for('auth.login'))
