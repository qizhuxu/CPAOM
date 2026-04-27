"""
账号管理路由
"""

import logging
import os
import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils.config_manager import ConfigManager
from utils.cpa_client import CPAClient
from utils.db_service import DatabaseService
from concurrent.futures import ThreadPoolExecutor, as_completed

bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')
config_manager = ConfigManager()
db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))
logger = logging.getLogger(__name__)


@bp.route('/<server_id>', methods=['GET'])
@login_required
def list_accounts(server_id):
    """获取账号列表（从本地数据库读取）"""
    logger.info(f"用户 {current_user.username} 请求账号列表: {server_id}")
    
    server = config_manager.get_server(server_id)
    
    if not server:
        logger.warning(f"服务器不存在: {server_id}")
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        # 从本地数据库读取账号列表
        local_accounts = db_service.get_auth_files_by_server(server_id)
        
        # 转换为前端需要的格式
        accounts = []
        for account in local_accounts:
            accounts.append({
                'name': account['filename'],
                'filename': account['filename'],
                'email': account['email'],
                'disabled': bool(account['disabled']),
                'disable_reason': account.get('disable_reason'),
                'auth_index': account['email'],  # 使用email作为auth_index
                'usage_percent': account.get('usage_percent'),
                'usage_checked_at': account.get('usage_checked_at'),
                'is_401': bool(account.get('is_401')),
                'last_error': account.get('last_error'),
                'updated_at': account.get('updated_at')
            })
        
        logger.info(f"获取账号列表成功: {server['name']}, 共 {len(accounts)} 个账号（本地数据）")
        
        return jsonify({
            "success": True,
            "accounts": accounts,
            "total": len(accounts),
            "from_local": True
        })
    except Exception as e:
        logger.error(f"获取账号列表失败: {server['name']} - {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/check-usage', methods=['POST'])
@bp.route('/<server_id>/check-usage', methods=['POST'])
@login_required
def check_usage(server_id):
    """批量检查使用情况"""
    logger.info(f"用户 {current_user.username} 开始检查使用情况: {server_id}")
    
    server = config_manager.get_server(server_id)
    
    if not server:
        logger.warning(f"服务器不存在: {server_id}")
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        # 过滤活跃账号
        active_files = [f for f in files if not f.get("disabled")]
        
        logger.info(f"开始检查 {len(active_files)} 个活跃账号的使用情况")
        
        results = []
        settings = config_manager.get_settings()
        max_workers = settings.get("max_workers", 10)
        
        # 使用独立函数而不是闭包
        def check_single_account(file_info, cpa_client, total_count, index):
            """检查单个账号（独立函数，避免闭包问题）"""
            auth_index = file_info.get("auth_index", "")
            email = file_info.get("email", "")
            
            if not auth_index:
                return None
            
            try:
                ok, usage_data = cpa_client.check_usage(auth_index)
                
                if ok:
                    # 提取使用率信息
                    rate_limit = usage_data.get("rate_limit", {})
                    primary = rate_limit.get("primary_window", {})
                    used_percent = primary.get("used_percent", 0)
                    
                    logger.info(f"[{index}/{total_count}] {email}: {used_percent:.1f}%")
                    
                    return {
                        "email": email,
                        "auth_index": auth_index,
                        "usage": usage_data,
                        "status": "success"
                    }
                else:
                    logger.warning(f"[{index}/{total_count}] {email}: 检查失败")
                    return {
                        "email": email,
                        "auth_index": auth_index,
                        "error": usage_data,
                        "status": "error"
                    }
            except Exception as e:
                logger.error(f"[{index}/{total_count}] {email}: 检查异常 - {str(e)}")
                return {
                    "email": email,
                    "auth_index": auth_index,
                    "error": str(e),
                    "status": "error"
                }
        
        # 并发检查
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for idx, file_info in enumerate(active_files, 1):
                future = executor.submit(check_single_account, file_info, client, len(active_files), idx)
                futures.append(future)
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        
        success_count = len([r for r in results if r['status'] == 'success'])
        error_count = len([r for r in results if r['status'] == 'error'])
        
        logger.info(f"使用情况检查完成: 成功 {success_count}, 失败 {error_count}, 总计 {len(results)}")
        
        return jsonify({
            "success": True,
            "results": results,
            "total": len(results)
        })
    
    except Exception as e:
        logger.error(f"检查使用情况失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/check-usage-single', methods=['POST'])
@login_required
def check_usage_single(server_id):
    """检查单个账号的使用情况"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    data = request.get_json()
    auth_index = data.get("auth_index", "")
    email = data.get("email", "")
    progress = data.get("progress", "")  # 例如 "1/20"
    
    if not auth_index:
        return jsonify({"success": False, "error": "缺少 auth_index"}), 400
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        ok, usage_data = client.check_usage(auth_index)
        
        if ok:
            # 提取使用率信息用于日志
            rate_limit = usage_data.get("rate_limit", {})
            primary = rate_limit.get("primary_window", {})
            used_percent = primary.get("used_percent", 0)
            
            # 输出进度日志
            if progress:
                logger.info(f"[{progress}] {email}: {used_percent:.1f}%")
            else:
                logger.info(f"{email}: {used_percent:.1f}%")
            
            return jsonify({
                "success": True,
                "data": {
                    "email": email,
                    "auth_index": auth_index,
                    "usage": usage_data,
                    "status": "success"
                }
            })
        else:
            if progress:
                logger.warning(f"[{progress}] {email}: 检查失败")
            else:
                logger.warning(f"{email}: 检查失败")
            
            return jsonify({
                "success": False,
                "data": {
                    "email": email,
                    "auth_index": auth_index,
                    "error": usage_data,
                    "status": "error"
                }
            })
    
    except Exception as e:
        logger.error(f"{email}: 检查异常 - {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/<filename>/check-and-sync', methods=['POST'])
@login_required
def check_and_sync_account(server_id, filename):
    """检测单个账号使用情况并同步到本地"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        
        # 获取账号信息
        files = client.get_auth_files()
        account = next((f for f in files if f.get('name') == filename), None)
        
        if not account:
            return jsonify({
                "success": False,
                "error": "账号不存在"
            }), 404
        
        email = account.get('email', '')
        disabled = account.get('disabled', False)
        auth_index = account.get('auth_index', '')
        
        # 检查使用量（无论是否禁用都尝试检查）
        usage_percent = None
        is_401 = False
        last_error = None
        usage_data = None
        
        if auth_index:
            try:
                ok, result = client.check_usage(auth_index)
                if ok:
                    usage_data = result
                    rate_limit = result.get("rate_limit", {})
                    primary = rate_limit.get("primary_window", {})
                    usage_percent = primary.get("used_percent", 0)
                    logger.info(f"账号 {email} 使用率: {usage_percent:.1f}%")
                else:
                    if "401" in str(result) or "unauthorized" in str(result).lower():
                        is_401 = True
                        last_error = "401 Unauthorized"
                    else:
                        last_error = str(result)
                    logger.warning(f"账号 {email} 检查失败: {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"账号 {email} 检查异常: {e}")
        
        # 下载认证文件内容
        auth_data = {}
        try:
            ok, content = client.download_auth_file(filename)
            if ok:
                auth_data = json.loads(content) if isinstance(content, str) else content
        except Exception as e:
            logger.warning(f"下载文件内容失败: {e}")
        
        # 保存到本地
        db_service.save_auth_file_backup(
            server_id=server_id,
            server_name=server["name"],
            filename=filename,
            email=email,
            auth_data=auth_data,
            disabled=disabled,
            usage_percent=usage_percent,
            is_401=is_401,
            last_error=last_error
        )
        
        logger.info(f"账号检测同步完成: {email}")
        
        return jsonify({
            "success": True,
            "account": {
                "filename": filename,
                "email": email,
                "disabled": disabled,
                "usage_percent": usage_percent,
                "usage_data": usage_data,
                "is_401": is_401,
                "last_error": last_error
            }
        })
    
    except Exception as e:
        logger.error(f"账号检测同步失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/<filename>/disable', methods=['POST'])
@login_required
def disable_account(server_id, filename):
    """禁用账号（云端操作后同步到本地）"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        ok, message = client.disable_auth_file(filename)
        
        if ok:
            # 同步该账号到本地（手动禁用原因）
            sync_single_account(server_id, server, filename, manual_disable_reason="手动禁用")
        
        return jsonify({
            "success": ok,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/<filename>/enable', methods=['POST'])
@login_required
def enable_account(server_id, filename):
    """启用账号（云端操作后同步到本地）"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        ok, message = client.enable_auth_file(filename)
        
        if ok:
            # 同步该账号到本地（清除禁用原因）
            sync_single_account(server_id, server, filename, clear_disable_reason=True)
        
        return jsonify({
            "success": ok,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/<filename>/revive', methods=['POST'])
@login_required
def revive_token(server_id, filename):
    """复活 Token（云端操作后同步到本地）"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    data = request.get_json()
    email = data.get("email", "")
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        settings = config_manager.get_settings()
        max_attempts = settings.get("token_revive_max_attempts", 3)
        
        ok, message = client.revive_token(email, filename, max_attempts)
        
        if ok:
            # 同步该账号到本地
            sync_single_account(server_id, server, filename)
        
        return jsonify({
            "success": ok,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def sync_single_account(server_id, server, filename, manual_disable_reason=None, clear_disable_reason=False):
    """同步单个账号到本地数据库
    
    Args:
        server_id: 服务器ID
        server: 服务器配置
        filename: 文件名
        manual_disable_reason: 手动禁用原因（如"手动禁用"）
        clear_disable_reason: 是否清除禁用原因（启用时使用）
    """
    try:
        from utils.db_service import DatabaseService
        import os
        import json
        
        db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))
        client = CPAClient(server["base_url"], server["token"], server["name"])
        
        # 获取账号列表找到该账号
        files = client.get_auth_files()
        account = next((f for f in files if f.get('name') == filename), None)
        
        if not account:
            logger.warning(f"账号不存在: {filename}")
            return
        
        email = account.get('email', '')
        disabled = account.get('disabled', False)
        auth_index = account.get('auth_index', '')
        
        # 检查使用量（无论是否禁用都尝试检查）
        usage_percent = None
        is_401 = False
        last_error = None
        disable_reason = None
        
        if auth_index:
            try:
                ok, usage_data = client.check_usage(auth_index)
                if ok:
                    rate_limit = usage_data.get("rate_limit", {})
                    primary = rate_limit.get("primary_window", {})
                    usage_percent = primary.get("used_percent", 0)
                else:
                    if "401" in str(usage_data) or "unauthorized" in str(usage_data).lower():
                        is_401 = True
                        last_error = "401 Unauthorized"
                    else:
                        last_error = str(usage_data)
            except Exception as e:
                last_error = str(e)
        
        # 确定禁用原因
        if clear_disable_reason:
            # 启用账号时清除原因
            disable_reason = None
        elif manual_disable_reason and disabled:
            # 手动禁用时使用传入的原因
            disable_reason = manual_disable_reason
        elif disabled:
            # 已禁用但没有指定原因，尝试从错误推断
            if is_401:
                disable_reason = "401错误"
            elif usage_percent is not None and usage_percent >= 100:
                disable_reason = "100%使用量"
        
        # 下载认证文件内容
        auth_data = {}
        try:
            ok, content = client.download_auth_file(filename)
            if ok:
                auth_data = json.loads(content) if isinstance(content, str) else content
        except Exception as e:
            logger.warning(f"下载文件内容失败: {e}")
        
        # 保存到本地
        db_service.save_auth_file_backup(
            server_id=server_id,
            server_name=server["name"],
            filename=filename,
            email=email,
            auth_data=auth_data,
            disabled=disabled,
            disable_reason=disable_reason,
            usage_percent=usage_percent,
            is_401=is_401,
            last_error=last_error
        )
        
        logger.info(f"单个账号同步完成: {email} (禁用原因: {disable_reason})")
        
    except Exception as e:
        logger.error(f"单个账号同步失败: {e}")


@bp.route('/<server_id>/<filename>/download', methods=['GET'])
@login_required
def download_account(server_id, filename):
    """下载单个账号的认证文件"""
    logger.info(f"用户 {current_user.username} 下载账号文件: {server_id}/{filename}")
    
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        from flask import send_file
        import io
        
        client = CPAClient(server["base_url"], server["token"], server["name"])
        
        # 下载认证文件
        ok, content = client.download_auth_file(filename)
        
        if not ok:
            return jsonify({"error": "下载失败"}), 500
        
        # 返回文件
        return send_file(
            io.BytesIO(content.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"下载账号文件失败: {server['name']}/{filename} - {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/<filename>/auth-content', methods=['GET'])
@login_required
def get_auth_content(server_id, filename):
    """获取认证文件内容（从本地数据库）"""
    logger.info(f"用户 {current_user.username} 查看认证文件内容: {server_id}/{filename}")
    
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    try:
        # 从本地数据库获取
        auth_file = db_service.get_auth_file_by_filename(server_id, filename)
        
        if not auth_file:
            return jsonify({
                "success": False,
                "error": "认证文件不存在"
            }), 404
        
        auth_data = auth_file.get('auth_data')
        
        if not auth_data:
            return jsonify({
                "success": False,
                "error": "认证文件内容为空"
            }), 404
        
        return jsonify({
            "success": True,
            "auth_data": auth_data
        })
    except Exception as e:
        logger.error(f"获取认证文件内容失败: {server['name']}/{filename} - {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
