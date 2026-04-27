"""
数据库服务
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class DatabaseService:
    """SQLite 数据库服务"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        # 确保数据目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 认证文件备份表（扩展）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_files_backup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                server_name TEXT NOT NULL,
                filename TEXT NOT NULL,
                email TEXT,
                auth_data TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                disabled INTEGER DEFAULT 0,
                disable_reason TEXT,
                usage_percent REAL,
                usage_checked_at TEXT,
                last_error TEXT,
                is_401 INTEGER DEFAULT 0,
                last_refresh TEXT,
                backup_time TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(server_id, filename)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_auth_files_server ON auth_files_backup(server_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_auth_files_email ON auth_files_backup(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_auth_files_status ON auth_files_backup(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_auth_files_disabled ON auth_files_backup(disabled)')
        
        # 服务器同步配置表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_sync_config (
                server_id TEXT PRIMARY KEY,
                sync_interval INTEGER DEFAULT 3600,
                auto_disable_100_percent INTEGER DEFAULT 0,
                auto_disable_401 INTEGER DEFAULT 1,
                auto_delete_401_files INTEGER DEFAULT 0,
                auto_enable_reset_accounts INTEGER DEFAULT 0,
                fetch_auth_content INTEGER DEFAULT 1,
                max_workers INTEGER DEFAULT 10,
                keep_sync_logs INTEGER DEFAULT 100,
                last_sync_at TEXT,
                next_sync_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        
        # 服务器统计表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_stats (
                server_id TEXT PRIMARY KEY,
                total_accounts INTEGER DEFAULT 0,
                active_accounts INTEGER DEFAULT 0,
                disabled_accounts INTEGER DEFAULT 0,
                disabled_401_accounts INTEGER DEFAULT 0,
                disabled_100_percent_accounts INTEGER DEFAULT 0,
                avg_usage_percent REAL DEFAULT 0,
                max_usage_percent REAL DEFAULT 0,
                min_usage_percent REAL DEFAULT 0,
                usage_checked_count INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        
        # Config 备份表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config_backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                server_name TEXT NOT NULL,
                config_content TEXT NOT NULL,
                config_hash TEXT NOT NULL,
                backup_time TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(server_id, config_hash)
            )
        ''')
        
        # 同步日志表（扩展版）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                server_name TEXT NOT NULL,
                sync_type TEXT NOT NULL,
                sync_mode TEXT NOT NULL,
                status TEXT NOT NULL,
                files_synced INTEGER DEFAULT 0,
                files_failed INTEGER DEFAULT 0,
                accounts_total INTEGER DEFAULT 0,
                accounts_active INTEGER DEFAULT 0,
                accounts_disabled INTEGER DEFAULT 0,
                accounts_401 INTEGER DEFAULT 0,
                accounts_100_percent INTEGER DEFAULT 0,
                accounts_enabled INTEGER DEFAULT 0,
                accounts_deleted INTEGER DEFAULT 0,
                avg_usage_percent REAL DEFAULT 0,
                error_message TEXT,
                duration_ms INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        
        # 单账号同步记录表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_log_id INTEGER,
                server_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                email TEXT,
                sync_mode TEXT NOT NULL,
                status TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                is_401 INTEGER DEFAULT 0,
                usage_percent REAL,
                disable_reason TEXT,
                error_message TEXT,
                duration_ms INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (sync_log_id) REFERENCES sync_logs(id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_sync_logs_sync_log ON account_sync_logs(sync_log_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_sync_logs_server ON account_sync_logs(server_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_logs_server ON sync_logs(server_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_logs_created ON sync_logs(created_at)')
        # 定时任务配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL UNIQUE,
                task_type TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                cron_expression TEXT NOT NULL,
                server_ids TEXT,
                last_run TEXT,
                next_run TEXT,
                run_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        
        # 任务执行历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                task_name TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                error_message TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_ms INTEGER,
                FOREIGN KEY (task_id) REFERENCES scheduled_tasks(id)
            )
        ''')
        
        # 操作审计日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        
        # 系统统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_date TEXT NOT NULL UNIQUE,
                total_servers INTEGER DEFAULT 0,
                total_accounts INTEGER DEFAULT 0,
                active_accounts INTEGER DEFAULT 0,
                disabled_accounts INTEGER DEFAULT 0,
                error_accounts INTEGER DEFAULT 0,
                syncs_performed INTEGER DEFAULT 0,
                tokens_revived INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # 认证文件备份相关方法
    def save_auth_file_backup(self, server_id: str, server_name: str, filename: str, 
                             email: str, auth_data: dict, disabled: bool = False,
                             disable_reason: str = None, usage_percent: float = None,
                             is_401: bool = False, last_error: str = None):
        """保存认证文件备份（扩展版）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO auth_files_backup 
            (server_id, server_name, filename, email, auth_data, disabled, disable_reason,
             usage_percent, usage_checked_at, is_401, last_error, backup_time, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, server_name, filename, email, json.dumps(auth_data), 
              1 if disabled else 0, disable_reason, usage_percent, 
              now if usage_percent is not None else None,
              1 if is_401 else 0, last_error, now, now))
        
        conn.commit()
        conn.close()
    
    def update_auth_file_usage(self, server_id: str, filename: str, 
                               usage_percent: float, last_error: str = None):
        """更新认证文件使用量"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            UPDATE auth_files_backup 
            SET usage_percent = ?, usage_checked_at = ?, last_error = ?, updated_at = ?
            WHERE server_id = ? AND filename = ?
        ''', (usage_percent, now, last_error, now, server_id, filename))
        
        conn.commit()
        conn.close()
    
    def update_auth_file_status(self, server_id: str, filename: str, 
                               disabled: bool, disable_reason: str = None,
                               is_401: bool = False):
        """更新认证文件状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            UPDATE auth_files_backup 
            SET disabled = ?, disable_reason = ?, is_401 = ?, updated_at = ?
            WHERE server_id = ? AND filename = ?
        ''', (1 if disabled else 0, disable_reason, 1 if is_401 else 0, now, 
              server_id, filename))
        
        conn.commit()
        conn.close()
    
    def delete_auth_file(self, server_id: str, filename: str):
        """删除认证文件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM auth_files_backup 
            WHERE server_id = ? AND filename = ?
        ''', (server_id, filename))
        
        conn.commit()
        conn.close()
    
    def get_auth_file_by_filename(self, server_id: str, filename: str) -> Optional[Dict]:
        """根据文件名获取认证文件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM auth_files_backup 
            WHERE server_id = ? AND filename = ?
        ''', (server_id, filename))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        result = dict(row)
        # 解析 JSON 字符串
        if result.get('auth_data'):
            try:
                result['auth_data'] = json.loads(result['auth_data'])
            except:
                pass
        
        return result
    
    def get_auth_files_by_server(self, server_id: str) -> List[Dict]:
        """获取指定服务器的认证文件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM auth_files_backup 
            WHERE server_id = ? 
            ORDER BY email
        ''', (server_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_auth_files(self) -> List[Dict]:
        """获取所有认证文件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM auth_files_backup ORDER BY server_name, email')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # 同步日志相关方法
    def add_sync_log(self, server_id: str, server_name: str, sync_type: str, 
                    sync_mode: str, status: str, files_synced: int = 0, 
                    files_failed: int = 0, accounts_total: int = 0,
                    accounts_active: int = 0, accounts_disabled: int = 0,
                    accounts_401: int = 0, accounts_100_percent: int = 0,
                    accounts_enabled: int = 0, accounts_deleted: int = 0,
                    avg_usage_percent: float = 0, error_message: str = None, 
                    duration_ms: int = None) -> int:
        """添加同步日志（扩展版），返回日志ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_logs 
            (server_id, server_name, sync_type, sync_mode, status, files_synced, 
             files_failed, accounts_total, accounts_active, accounts_disabled,
             accounts_401, accounts_100_percent, accounts_enabled, accounts_deleted,
             avg_usage_percent, error_message, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, server_name, sync_type, sync_mode, status, files_synced, 
              files_failed, accounts_total, accounts_active, accounts_disabled,
              accounts_401, accounts_100_percent, accounts_enabled, accounts_deleted,
              avg_usage_percent, error_message, duration_ms))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def add_account_sync_log(self, sync_log_id: int, server_id: str, 
                            filename: str, email: str, sync_mode: str,
                            status: str, is_active: bool = True,
                            is_401: bool = False, usage_percent: float = None,
                            disable_reason: str = None, error_message: str = None,
                            duration_ms: int = None):
        """添加单账号同步记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO account_sync_logs 
            (sync_log_id, server_id, filename, email, sync_mode, status,
             is_active, is_401, usage_percent, disable_reason, error_message, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (sync_log_id, server_id, filename, email, sync_mode, status,
              1 if is_active else 0, 1 if is_401 else 0, usage_percent,
              disable_reason, error_message, duration_ms))
        
        conn.commit()
        conn.close()
    
    def get_sync_logs(self, limit: int = 100) -> List[Dict]:
        """获取同步日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sync_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_sync_logs_by_server(self, server_id: str, limit: int = 100) -> List[Dict]:
        """获取指定服务器的同步日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sync_logs 
            WHERE server_id = ?
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (server_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_account_sync_logs(self, sync_log_id: int) -> List[Dict]:
        """获取单次同步的账号详细记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM account_sync_logs 
            WHERE sync_log_id = ?
            ORDER BY created_at
        ''', (sync_log_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def cleanup_old_sync_logs(self, server_id: str, keep_count: int = 100):
        """清理旧的同步日志，保留最新的 keep_count 条"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取要保留的日志ID
        cursor.execute('''
            SELECT id FROM sync_logs 
            WHERE server_id = ?
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (server_id, keep_count))
        
        keep_ids = [row[0] for row in cursor.fetchall()]
        
        if keep_ids:
            placeholders = ','.join('?' * len(keep_ids))
            
            # 删除旧的账号同步记录
            cursor.execute(f'''
                DELETE FROM account_sync_logs 
                WHERE server_id = ? AND sync_log_id NOT IN ({placeholders})
            ''', [server_id] + keep_ids)
            
            # 删除旧的同步日志
            cursor.execute(f'''
                DELETE FROM sync_logs 
                WHERE server_id = ? AND id NOT IN ({placeholders})
            ''', [server_id] + keep_ids)
        
        conn.commit()
        conn.close()
    
    # 审计日志相关方法
    def add_audit_log(self, user: str, action: str, resource_type: str = None,
                     resource_id: str = None, details: dict = None,
                     ip_address: str = None, user_agent: str = None):
        """添加审计日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_logs 
            (user, action, resource_type, resource_id, details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user, action, resource_type, resource_id, 
              json.dumps(details) if details else None, ip_address, user_agent))
        
        conn.commit()
        conn.close()
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM audit_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # 统计相关方法
    def update_daily_stats(self, total_servers: int, total_accounts: int,
                          active_accounts: int, disabled_accounts: int,
                          error_accounts: int):
        """更新每日统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.utcnow().date().isoformat()
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO system_stats 
            (stat_date, total_servers, total_accounts, active_accounts, 
             disabled_accounts, error_accounts, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (today, total_servers, total_accounts, active_accounts,
              disabled_accounts, error_accounts, now))
        
        conn.commit()
        conn.close()
    
    def get_daily_stats(self, days: int = 30) -> List[Dict]:
        """获取每日统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM system_stats 
            ORDER BY stat_date DESC 
            LIMIT ?
        ''', (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # 服务器同步配置相关方法
    def save_sync_config(self, server_id: str, sync_interval: int = 3600,
                        auto_disable_100_percent: bool = False,
                        auto_disable_401: bool = True,
                        auto_delete_401_files: bool = False,
                        auto_enable_reset_accounts: bool = False,
                        fetch_auth_content: bool = True,
                        max_workers: int = 10,
                        keep_sync_logs: int = 100):
        """保存服务器同步配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO server_sync_config 
            (server_id, sync_interval, auto_disable_100_percent, auto_disable_401,
             auto_delete_401_files, auto_enable_reset_accounts, fetch_auth_content, 
             max_workers, keep_sync_logs, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, sync_interval, 
              1 if auto_disable_100_percent else 0,
              1 if auto_disable_401 else 0,
              1 if auto_delete_401_files else 0,
              1 if auto_enable_reset_accounts else 0,
              1 if fetch_auth_content else 0,
              max_workers,
              keep_sync_logs,
              now))
        
        conn.commit()
        conn.close()
    
    def get_sync_config(self, server_id: str) -> Optional[Dict]:
        """获取服务器同步配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM server_sync_config 
            WHERE server_id = ?
        ''', (server_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_sync_time(self, server_id: str, last_sync_at: str = None, 
                        next_sync_at: str = None):
        """更新同步时间"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        if last_sync_at and next_sync_at:
            cursor.execute('''
                UPDATE server_sync_config 
                SET last_sync_at = ?, next_sync_at = ?, updated_at = ?
                WHERE server_id = ?
            ''', (last_sync_at, next_sync_at, now, server_id))
        elif last_sync_at:
            cursor.execute('''
                UPDATE server_sync_config 
                SET last_sync_at = ?, updated_at = ?
                WHERE server_id = ?
            ''', (last_sync_at, now, server_id))
        
        conn.commit()
        conn.close()
    
    # 服务器统计相关方法
    def save_server_stats(self, server_id: str, total_accounts: int,
                         active_accounts: int, disabled_accounts: int,
                         disabled_401_accounts: int = 0,
                         disabled_100_percent_accounts: int = 0,
                         avg_usage_percent: float = 0,
                         max_usage_percent: float = 0,
                         min_usage_percent: float = 0,
                         usage_checked_count: int = 0):
        """保存服务器统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO server_stats 
            (server_id, total_accounts, active_accounts, disabled_accounts,
             disabled_401_accounts, disabled_100_percent_accounts,
             avg_usage_percent, max_usage_percent, min_usage_percent,
             usage_checked_count, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, total_accounts, active_accounts, disabled_accounts,
              disabled_401_accounts, disabled_100_percent_accounts,
              avg_usage_percent, max_usage_percent, min_usage_percent,
              usage_checked_count, now))
        
        conn.commit()
        conn.close()
    
    def get_server_stats(self, server_id: str) -> Optional[Dict]:
        """获取服务器统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM server_stats 
            WHERE server_id = ?
        ''', (server_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_server_stats(self) -> List[Dict]:
        """获取所有服务器统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM server_stats')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Token 刷新配置相关方法
    def save_token_refresh_config(self, server_id: str, enabled: bool = False,
                                  refresh_interval: int = 86400,
                                  refresh_lead_time: int = 432000,
                                  max_retry_attempts: int = 3,
                                  retry_interval: int = 300,
                                  auto_disable_on_failure: bool = True):
        """保存 Token 刷新配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO token_refresh_config 
            (server_id, enabled, refresh_interval, refresh_lead_time,
             max_retry_attempts, retry_interval, auto_disable_on_failure, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, 1 if enabled else 0, refresh_interval, refresh_lead_time,
              max_retry_attempts, retry_interval, 1 if auto_disable_on_failure else 0, now))
        
        conn.commit()
        conn.close()
    
    def get_token_refresh_config(self, server_id: str) -> Optional[Dict]:
        """获取 Token 刷新配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM token_refresh_config 
            WHERE server_id = ?
        ''', (server_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def add_token_refresh_log(self, server_id: str, filename: str, email: str,
                             status: str, old_token_expiry: str = None,
                             new_token_expiry: str = None, error_message: str = None,
                             attempts: int = 1, duration_ms: int = None):
        """添加 Token 刷新日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO token_refresh_logs 
            (server_id, filename, email, status, old_token_expiry, new_token_expiry,
             error_message, attempts, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, filename, email, status, old_token_expiry, new_token_expiry,
              error_message, attempts, duration_ms))
        
        conn.commit()
        conn.close()
    
    def get_token_refresh_logs(self, server_id: str, limit: int = 100) -> List[Dict]:
        """获取 Token 刷新日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM token_refresh_logs 
            WHERE server_id = ?
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (server_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
