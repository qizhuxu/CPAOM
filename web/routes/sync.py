"""
同步备份路由
"""

import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from utils.config_manager import ConfigManager
from utils.cpa_client import CPAClient
from utils.db_service import DatabaseService
from datetime import datetime, timedelta
import os
import time
import json

bp = Blueprint('sync', __name__, url_prefix='/api/sync')
config_manager = ConfigManager()
db_service = DatabaseService(os.getenv('DATABASE_PATH', 'data/cpa_manager.db'))
logger = logging.getLogger(__name__)


@bp.route('/<server_id>/auth-files', methods=['POST'])
@login_required
def sync_auth_files(server_id):
    """同步认证文件"""
    server = config_manager.get_server(server_id)
    
    if not server:
        return jsonify({"error": "服务器不存在"}), 404
    
    start_time = time.time()
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        synced = 0
        failed = 0
        
        for file_info in files:
            filename = file_info.get("name")
            email = file_info.get("email", "")
            disabled = file_info.get("disabled", False)
            
            if not filename:
                failed += 1
                continue
            
            # 下载完整文件
            ok, auth_data = client.download_auth_file(filename)
            
            if ok and auth_data:
                # 保存到数据库
                db_service.save_auth_file_backup(
                    server_id=server_id,
                    server_name=server["name"],
                    filename=filename,
                    email=email,
                    auth_data=auth_data,
                    disabled=disabled
                )
                synced += 1
            else:
                failed += 1
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 记录同步日志
        db_service.add_sync_log(
            server_id=server_id,
            server_name=server["name"],
            sync_type="auth_files",
            status="success" if failed == 0 else "partial",
            files_synced=synced,
            files_failed=failed,
            duration_ms=duration_ms
        )
        
        return jsonify({
            "success": True,
            "synced": synced,
            "failed": failed,
            "total": len(files),
            "duration_ms": duration_ms
        })
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        
        db_service.add_sync_log(
            server_id=server_id,
            server_name=server["name"],
            sync_type="auth_files",
            status="failed",
            error_message=str(e),
            duration_ms=duration_ms
        )
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/<server_id>/enhanced', methods=['POST'])
@login_required
def enhanced_sync(server_id):
    """增强同步：巡检 + 维护 + 记录"""
    logger.info(f"用户 {current_user.username} 开始增强同步: {server_id}")
    
    result = perform_enhanced_sync(server_id, db_service, config_manager)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500


def perform_enhanced_sync(server_id, db_service, config_manager):
    """执行增强同步（可被调度器调用）"""
    server = config_manager.get_server(server_id)
    if not server:
        return {"success": False, "error": "服务器不存在"}
    
    # 获取同步配置
    sync_config = db_service.get_sync_config(server_id)
    if not sync_config:
        # 使用默认配置
        sync_config = {
            'fetch_auth_content': True,
            'auto_disable_401': True,
            'auto_disable_100_percent': False,
            'auto_enable_reset_accounts': False,
            'auto_delete_401_files': False,
            'max_workers': 10
        }
    
    # 获取并发线程数
    max_workers = sync_config.get('max_workers', 10)
    
    start_time = time.time()
    
    try:
        client = CPAClient(server["base_url"], server["token"], server["name"])
        files = client.get_auth_files()
        
        synced = 0
        failed = 0
        accounts_disabled = 0
        accounts_enabled = 0
        accounts_deleted = 0
        
        usage_stats = []
        
        logger.info(f"开始处理 {len(files)} 个账号")
        
        for i, file_info in enumerate(files, 1):
            filename = file_info.get("name")
            email = file_info.get("email", "")
            disabled = file_info.get("disabled", False)
            auth_index = file_info.get("auth_index", "")
            
            if not filename:
                failed += 1
                continue
            
            logger.info(f"[{i}/{len(files)}] 处理账号: {email}")
            
            # 1. 检查使用量
            usage_percent = None
            is_401 = False
            last_error = None
            
            if auth_index and not disabled:
                try:
                    ok, usage_data = client.check_usage(auth_index)
                    if ok:
                        rate_limit = usage_data.get("rate_limit", {})
                        primary = rate_limit.get("primary_window", {})
                        usage_percent = primary.get("used_percent", 0)
                        usage_stats.append(usage_percent)
                        logger.info(f"  使用率: {usage_percent:.1f}%")
                    else:
                        # 检查是否是401错误
                        if "401" in str(usage_data) or "unauthorized" in str(usage_data).lower():
                            is_401 = True
                            last_error = "401 Unauthorized"
                            logger.warning(f"  401错误: {usage_data}")
                        else:
                            last_error = str(usage_data)
                            logger.warning(f"  检查失败: {usage_data}")
                except Exception as e:
                    last_error = str(e)
                    logger.error(f"  检查异常: {e}")
            
            # 2. 自动维护逻辑
            should_disable = False
            should_enable = False
            should_delete = False
            disable_reason = None
            
            # 获取本地记录以比较状态变化
            local_record = db_service.get_auth_file_by_filename(server_id, filename)
            
            if not disabled:  # 当前活跃账号
                # 检查是否需要禁用
                if is_401 and sync_config.get('auto_disable_401'):
                    should_disable = True
                    disable_reason = "401错误"
                    logger.info(f"  → 自动禁用（401错误）")
                elif usage_percent is not None and usage_percent >= 100 and sync_config.get('auto_disable_100_percent'):
                    should_disable = True
                    disable_reason = "100%使用量"
                    logger.info(f"  → 自动禁用（100%使用量）")
            else:  # 当前禁用账号
                # 检查是否需要重新启用（仅针对100%使用量禁用的账号）
                if (sync_config.get('auto_enable_reset_accounts') and 
                    local_record and 
                    local_record.get('disable_reason') == '100%使用量' and
                    usage_percent is not None and usage_percent < 100):
                    should_enable = True
                    logger.info(f"  → 自动启用（使用量已重置: {usage_percent:.1f}%）")
            
            # 检查是否需要删除401文件
            if is_401 and sync_config.get('auto_delete_401_files'):
                should_delete = True
                logger.warning(f"  → 自动删除（401文件）")
            
            # 3. 执行维护操作
            if should_delete:
                try:
                    ok, message = client.delete_auth_file(filename)
                    if ok:
                        db_service.delete_auth_file(server_id, filename)
                        accounts_deleted += 1
                        logger.info(f"  ✓ 已删除文件")
                        continue  # 跳过后续处理
                    else:
                        logger.error(f"  ✗ 删除失败: {message}")
                except Exception as e:
                    logger.error(f"  ✗ 删除异常: {e}")
            
            if should_disable:
                try:
                    ok, message = client.disable_auth_file(filename)
                    if ok:
                        disabled = True
                        accounts_disabled += 1
                        logger.info(f"  ✓ 已禁用")
                    else:
                        logger.error(f"  ✗ 禁用失败: {message}")
                except Exception as e:
                    logger.error(f"  ✗ 禁用异常: {e}")
            
            if should_enable:
                try:
                    ok, message = client.enable_auth_file(filename)
                    if ok:
                        disabled = False
                        disable_reason = None
                        accounts_enabled += 1
                        logger.info(f"  ✓ 已启用")
                    else:
                        logger.error(f"  ✗ 启用失败: {message}")
                except Exception as e:
                    logger.error(f"  ✗ 启用异常: {e}")
            
            # 4. 拉取认证文件内容（可选）
            auth_data = {}
            if sync_config.get('fetch_auth_content'):
                try:
                    ok, content = client.download_auth_file(filename)
                    if ok:
                        auth_data = json.loads(content) if isinstance(content, str) else content
                except Exception as e:
                    logger.warning(f"  下载文件内容失败: {e}")
            
            # 5. 保存到本地数据库
            try:
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
                synced += 1
            except Exception as e:
                logger.error(f"  保存失败: {e}")
                failed += 1
        
        # 6. 计算并保存服务器统计
        total_accounts = len(files)
        active_accounts = sum(1 for f in files if not f.get("disabled"))
        disabled_accounts = total_accounts - active_accounts
        
        # 计算使用量统计
        avg_usage = sum(usage_stats) / len(usage_stats) if usage_stats else 0
        max_usage = max(usage_stats) if usage_stats else 0
        min_usage = min(usage_stats) if usage_stats else 0
        
        # 统计禁用原因
        local_accounts = db_service.get_auth_files_by_server(server_id)
        disabled_401_count = sum(1 for a in local_accounts if a.get('disable_reason') == '401错误')
        disabled_100_count = sum(1 for a in local_accounts if a.get('disable_reason') == '100%使用量')
        
        db_service.save_server_stats(
            server_id=server_id,
            total_accounts=total_accounts,
            active_accounts=active_accounts,
            disabled_accounts=disabled_accounts,
            disabled_401_accounts=disabled_401_count,
            disabled_100_percent_accounts=disabled_100_count,
            avg_usage_percent=avg_usage,
            max_usage_percent=max_usage,
            min_usage_percent=min_usage,
            usage_checked_count=len(usage_stats)
        )
        
        # 7. 更新同步时间
        now = datetime.utcnow().isoformat()
        next_sync = None
        if sync_config.get('sync_interval'):
            next_sync_time = datetime.utcnow() + timedelta(seconds=sync_config['sync_interval'])
            next_sync = next_sync_time.isoformat()
        
        db_service.update_sync_time(server_id, now, next_sync)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 8. 记录同步日志
        status = "success"
        if failed > 0:
            status = "partial"
        
        db_service.add_sync_log(
            server_id=server_id,
            server_name=server["name"],
            sync_type="enhanced",
            status=status,
            files_synced=synced,
            files_failed=failed,
            accounts_disabled=accounts_disabled,
            accounts_enabled=accounts_enabled,
            accounts_deleted=accounts_deleted,
            duration_ms=duration_ms
        )
        
        logger.info(f"增强同步完成: 处理{total_accounts}个账号, 禁用{accounts_disabled}个, 启用{accounts_enabled}个, 删除{accounts_deleted}个")
        
        return {
            "success": True,
            "total_processed": total_accounts,
            "synced": synced,
            "failed": failed,
            "accounts_disabled": accounts_disabled,
            "accounts_enabled": accounts_enabled,
            "accounts_deleted": accounts_deleted,
            "avg_usage_percent": round(avg_usage, 1),
            "duration_ms": duration_ms
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        
        db_service.add_sync_log(
            server_id=server_id,
            server_name=server["name"],
            sync_type="enhanced",
            status="failed",
            error_message=str(e),
            duration_ms=duration_ms
        )
        
        logger.error(f"增强同步失败: {e}")
        
        return {
            "success": False,
            "error": str(e)
        }


@bp.route('/logs', methods=['GET'])
@login_required
def get_sync_logs():
    """获取同步日志"""
    try:
        logs = db_service.get_sync_logs(limit=50)
        
        return jsonify({
            "success": True,
            "logs": logs
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route('/log-account', methods=['POST'])
@login_required
def log_account_sync():
    """记录单账号同步日志"""
    from flask import request
    
    data = request.get_json()
    server_id = data.get('server_id')
    filename = data.get('filename')
    email = data.get('email', '')
    sync_mode = data.get('sync_mode', 'manual_single')
    status = data.get('status', 'success')
    is_active = data.get('is_active', True)
    is_401 = data.get('is_401', False)
    usage_percent = data.get('usage_percent')
    disable_reason = data.get('disable_reason')
    error_message = data.get('error_message')
    duration_ms = data.get('duration_ms')
    
    try:
        server = config_manager.get_server(server_id)
        if not server:
            return jsonify({"error": "服务器不存在"}), 404
        
        # 创建一个简单的同步日志（单账号）
        log_id = db_service.add_sync_log(
            server_id=server_id,
            server_name=server['name'],
            sync_type='account',
            sync_mode=sync_mode,
            status=status,
            files_synced=1 if status == 'success' else 0,
            files_failed=1 if status == 'failed' else 0,
            duration_ms=duration_ms
        )
        
        # 添加账号详细记录
        db_service.add_account_sync_log(
            sync_log_id=log_id,
            server_id=server_id,
            filename=filename,
            email=email,
            sync_mode=sync_mode,
            status=status,
            is_active=is_active,
            is_401=is_401,
            usage_percent=usage_percent,
            disable_reason=disable_reason,
            error_message=error_message,
            duration_ms=duration_ms
        )
        
        return jsonify({"success": True, "log_id": log_id})
    
    except Exception as e:
        logger.error(f"记录账号同步日志失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/log-batch', methods=['POST'])
@login_required
def log_batch_sync():
    """记录批量同步日志"""
    from flask import request
    
    data = request.get_json()
    server_id = data.get('server_id')
    sync_mode = data.get('sync_mode', 'manual_batch')
    status = data.get('status', 'success')
    files_synced = data.get('files_synced', 0)
    files_failed = data.get('files_failed', 0)
    accounts_total = data.get('accounts_total', 0)
    accounts_active = data.get('accounts_active', 0)
    accounts_disabled = data.get('accounts_disabled', 0)
    accounts_401 = data.get('accounts_401', 0)
    accounts_100_percent = data.get('accounts_100_percent', 0)
    avg_usage_percent = data.get('avg_usage_percent', 0)
    duration_ms = data.get('duration_ms')
    account_logs = data.get('account_logs', [])
    
    try:
        server = config_manager.get_server(server_id)
        if not server:
            return jsonify({"error": "服务器不存在"}), 404
        
        # 创建批量同步日志
        log_id = db_service.add_sync_log(
            server_id=server_id,
            server_name=server['name'],
            sync_type='batch',
            sync_mode=sync_mode,
            status=status,
            files_synced=files_synced,
            files_failed=files_failed,
            accounts_total=accounts_total,
            accounts_active=accounts_active,
            accounts_disabled=accounts_disabled,
            accounts_401=accounts_401,
            accounts_100_percent=accounts_100_percent,
            avg_usage_percent=avg_usage_percent,
            duration_ms=duration_ms
        )
        
        # 添加每个账号的详细记录
        for acc_log in account_logs:
            db_service.add_account_sync_log(
                sync_log_id=log_id,
                server_id=server_id,
                filename=acc_log.get('filename', ''),
                email=acc_log.get('email', ''),
                sync_mode=sync_mode,
                status=acc_log.get('status', 'success'),
                is_active=acc_log.get('is_active', True),
                is_401=acc_log.get('is_401', False),
                usage_percent=acc_log.get('usage_percent'),
                disable_reason=acc_log.get('disable_reason'),
                error_message=acc_log.get('error_message'),
                duration_ms=acc_log.get('duration_ms')
            )
        
        # 清理旧日志
        sync_config = db_service.get_sync_config(server_id)
        if sync_config:
            keep_count = sync_config.get('keep_sync_logs', 100)
            db_service.cleanup_old_sync_logs(server_id, keep_count)
        
        return jsonify({"success": True, "log_id": log_id})
    
    except Exception as e:
        logger.error(f"记录批量同步日志失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/logs/<server_id>', methods=['GET'])
@login_required
def get_sync_logs_by_server(server_id):
    """获取指定服务器的同步日志"""
    try:
        from flask import request
        limit = int(request.args.get('limit', 100))
        
        logs = db_service.get_sync_logs_by_server(server_id, limit)
        
        return jsonify({
            "success": True,
            "logs": logs
        })
    
    except Exception as e:
        logger.error(f"获取同步日志失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/logs/<int:log_id>/accounts', methods=['GET'])
@login_required
def get_account_sync_logs(log_id):
    """获取单次同步的账号详细记录"""
    try:
        account_logs = db_service.get_account_sync_logs(log_id)
        
        return jsonify({
            "success": True,
            "account_logs": account_logs
        })
    
    except Exception as e:
        logger.error(f"获取账号同步记录失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
