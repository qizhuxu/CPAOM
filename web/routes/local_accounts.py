"""
本地账号数据路由
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from utils.db_service import DatabaseService
from utils.config_manager import ConfigManager
import json

bp = Blueprint('local_accounts', __name__, url_prefix='/api/local-accounts')

# 初始化服务
config_manager = ConfigManager()


def get_db_service():
    """获取数据库服务实例"""
    import os
    db_path = os.getenv('DATABASE_PATH', 'data/cpa_manager.db')
    return DatabaseService(db_path)


@bp.route('/', methods=['GET'])
@login_required
def list_local_accounts():
    """获取所有本地账号"""
    try:
        db = get_db_service()
        accounts = db.get_all_auth_files()
        
        # 解析 auth_data JSON
        for account in accounts:
            if account.get('auth_data'):
                try:
                    account['auth_data_parsed'] = json.loads(account['auth_data'])
                except:
                    account['auth_data_parsed'] = None
        
        return jsonify({
            "success": True,
            "accounts": accounts,
            "total": len(accounts)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/server/<server_id>', methods=['GET'])
@login_required
def list_local_accounts_by_server(server_id):
    """获取指定服务器的本地账号"""
    try:
        db = get_db_service()
        accounts = db.get_auth_files_by_server(server_id)
        
        # 解析 auth_data JSON
        for account in accounts:
            if account.get('auth_data'):
                try:
                    account['auth_data_parsed'] = json.loads(account['auth_data'])
                except:
                    account['auth_data_parsed'] = None
        
        return jsonify({
            "success": True,
            "accounts": accounts,
            "total": len(accounts)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/stats', methods=['GET'])
@login_required
def get_local_stats():
    """获取本地账号统计"""
    try:
        db = get_db_service()
        accounts = db.get_all_auth_files()
        
        # 按服务器分组统计
        server_stats = {}
        total_active = 0
        total_disabled = 0
        
        for account in accounts:
            server_id = account['server_id']
            server_name = account['server_name']
            
            if server_id not in server_stats:
                server_stats[server_id] = {
                    'server_id': server_id,
                    'server_name': server_name,
                    'total': 0,
                    'active': 0,
                    'disabled': 0
                }
            
            server_stats[server_id]['total'] += 1
            
            if account['disabled']:
                server_stats[server_id]['disabled'] += 1
                total_disabled += 1
            else:
                server_stats[server_id]['active'] += 1
                total_active += 1
        
        return jsonify({
            "success": True,
            "total_accounts": len(accounts),
            "total_active": total_active,
            "total_disabled": total_disabled,
            "total_servers": len(server_stats),
            "server_stats": list(server_stats.values())
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<int:account_id>', methods=['GET'])
@login_required
def get_local_account_detail(account_id):
    """获取本地账号详情"""
    try:
        db = get_db_service()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM auth_files_backup WHERE id = ?', (account_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"error": "账号不存在"}), 404
        
        account = dict(row)
        
        # 解析 auth_data
        if account.get('auth_data'):
            try:
                account['auth_data_parsed'] = json.loads(account['auth_data'])
            except:
                account['auth_data_parsed'] = None
        
        return jsonify({
            "success": True,
            "account": account
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<int:account_id>', methods=['DELETE'])
@login_required
def delete_local_account(account_id):
    """删除本地账号"""
    try:
        db = get_db_service()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM auth_files_backup WHERE id = ?', (account_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "账号不存在"}), 404
        
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "账号已删除"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/search', methods=['POST'])
@login_required
def search_local_accounts():
    """搜索本地账号"""
    data = request.get_json()
    keyword = data.get('keyword', '').strip()
    server_id = data.get('server_id')
    
    try:
        db = get_db_service()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM auth_files_backup WHERE 1=1'
        params = []
        
        if server_id:
            query += ' AND server_id = ?'
            params.append(server_id)
        
        if keyword:
            query += ' AND (email LIKE ? OR filename LIKE ?)'
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        query += ' ORDER BY server_name, email'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        accounts = [dict(row) for row in rows]
        
        # 解析 auth_data
        for account in accounts:
            if account.get('auth_data'):
                try:
                    account['auth_data_parsed'] = json.loads(account['auth_data'])
                except:
                    account['auth_data_parsed'] = None
        
        return jsonify({
            "success": True,
            "accounts": accounts,
            "total": len(accounts)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
