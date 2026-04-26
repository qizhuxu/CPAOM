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
        
        # 认证文件备份表
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
        
        # 同步日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                server_name TEXT NOT NULL,
                sync_type TEXT NOT NULL,
                status TEXT NOT NULL,
                files_synced INTEGER DEFAULT 0,
                files_failed INTEGER DEFAULT 0,
                error_message TEXT,
                duration_ms INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        
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
                             email: str, auth_data: dict, disabled: bool = False):
        """保存认证文件备份"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO auth_files_backup 
            (server_id, server_name, filename, email, auth_data, disabled, backup_time, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, server_name, filename, email, json.dumps(auth_data), 
              1 if disabled else 0, now, now))
        
        conn.commit()
        conn.close()
    
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
                    status: str, files_synced: int = 0, files_failed: int = 0,
                    error_message: str = None, duration_ms: int = None):
        """添加同步日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_logs 
            (server_id, server_name, sync_type, status, files_synced, files_failed, 
             error_message, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, server_name, sync_type, status, files_synced, files_failed,
              error_message, duration_ms))
        
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
