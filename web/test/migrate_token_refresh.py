"""
数据库迁移脚本 - Token 刷新配置
添加 Token 定时刷新配置表
"""

import sqlite3
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_database():
    db_path = 'data/cpa_manager.db'
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("开始迁移数据库...")
    print()
    
    # 1. 创建 token_refresh_config 表
    print("1. 创建 token_refresh_config 表...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_refresh_config (
                server_id TEXT PRIMARY KEY,
                enabled INTEGER DEFAULT 0,
                refresh_interval INTEGER DEFAULT 86400,
                refresh_lead_time INTEGER DEFAULT 432000,
                max_retry_attempts INTEGER DEFAULT 3,
                retry_interval INTEGER DEFAULT 300,
                auto_disable_on_failure INTEGER DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        print("   ✓ 创建 token_refresh_config 表")
    except sqlite3.OperationalError as e:
        print(f"   - token_refresh_config 表已存在或创建失败: {e}")
    
    print()
    
    # 2. 创建 token_refresh_logs 表
    print("2. 创建 token_refresh_logs 表...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_refresh_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                email TEXT,
                status TEXT NOT NULL,
                old_token_expiry TEXT,
                new_token_expiry TEXT,
                error_message TEXT,
                attempts INTEGER DEFAULT 1,
                duration_ms INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        ''')
        print("   ✓ 创建 token_refresh_logs 表")
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_token_refresh_logs_server ON token_refresh_logs(server_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_token_refresh_logs_created ON token_refresh_logs(created_at)')
        print("   ✓ 创建索引")
        
    except sqlite3.OperationalError as e:
        print(f"   - token_refresh_logs 表已存在或创建失败: {e}")
    
    print()
    
    conn.commit()
    conn.close()
    
    print("✅ 数据库迁移完成！")
    print()
    print("新增功能:")
    print("  - Token 定时刷新配置表")
    print("  - Token 刷新日志记录表")
    print()

if __name__ == '__main__':
    migrate_database()
