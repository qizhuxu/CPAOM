"""
数据库迁移脚本 - 添加同步配置和统计功能
"""

import sqlite3
import os
from pathlib import Path

def migrate_database(db_path='data/cpa_manager.db'):
    """迁移数据库到新版本"""
    
    # 确保数据目录存在
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("开始数据库迁移...")
    
    # 1. 扩展 auth_files_backup 表
    print("1. 扩展 auth_files_backup 表...")
    try:
        cursor.execute("ALTER TABLE auth_files_backup ADD COLUMN disable_reason TEXT")
        print("   ✓ 添加 disable_reason 列")
    except sqlite3.OperationalError:
        print("   - disable_reason 列已存在")
    
    try:
        cursor.execute("ALTER TABLE auth_files_backup ADD COLUMN usage_percent REAL")
        print("   ✓ 添加 usage_percent 列")
    except sqlite3.OperationalError:
        print("   - usage_percent 列已存在")
    
    try:
        cursor.execute("ALTER TABLE auth_files_backup ADD COLUMN usage_checked_at TEXT")
        print("   ✓ 添加 usage_checked_at 列")
    except sqlite3.OperationalError:
        print("   - usage_checked_at 列已存在")
    
    try:
        cursor.execute("ALTER TABLE auth_files_backup ADD COLUMN last_error TEXT")
        print("   ✓ 添加 last_error 列")
    except sqlite3.OperationalError:
        print("   - last_error 列已存在")
    
    try:
        cursor.execute("ALTER TABLE auth_files_backup ADD COLUMN is_401 INTEGER DEFAULT 0")
        print("   ✓ 添加 is_401 列")
    except sqlite3.OperationalError:
        print("   - is_401 列已存在")
    
    # 2. 扩展 sync_logs 表
    print("2. 扩展 sync_logs 表...")
    try:
        cursor.execute("ALTER TABLE sync_logs ADD COLUMN accounts_disabled INTEGER DEFAULT 0")
        print("   ✓ 添加 accounts_disabled 列")
    except sqlite3.OperationalError:
        print("   - accounts_disabled 列已存在")
    
    try:
        cursor.execute("ALTER TABLE sync_logs ADD COLUMN accounts_enabled INTEGER DEFAULT 0")
        print("   ✓ 添加 accounts_enabled 列")
    except sqlite3.OperationalError:
        print("   - accounts_enabled 列已存在")
    
    try:
        cursor.execute("ALTER TABLE sync_logs ADD COLUMN accounts_deleted INTEGER DEFAULT 0")
        print("   ✓ 添加 accounts_deleted 列")
    except sqlite3.OperationalError:
        print("   - accounts_deleted 列已存在")
    
    # 3. 创建 server_sync_config 表
    print("3. 创建 server_sync_config 表...")
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
            last_sync_at TEXT,
            next_sync_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')
    print("   ✓ server_sync_config 表已创建")
    
    # 3.1 添加 max_workers 列（如果表已存在）
    try:
        cursor.execute("ALTER TABLE server_sync_config ADD COLUMN max_workers INTEGER DEFAULT 10")
        print("   ✓ 添加 max_workers 列")
    except sqlite3.OperationalError:
        print("   - max_workers 列已存在")
    
    # 4. 创建 server_stats 表
    print("4. 创建 server_stats 表...")
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
    print("   ✓ server_stats 表已创建")
    
    # 5. 创建索引
    print("5. 创建索引...")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_auth_files_disabled ON auth_files_backup(disabled)")
        print("   ✓ 创建 idx_auth_files_disabled 索引")
    except:
        print("   - 索引已存在")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 数据库迁移完成！")
    print("\n新增功能：")
    print("  - 账号使用量跟踪")
    print("  - 401错误标记")
    print("  - 禁用原因记录")
    print("  - 服务器同步配置")
    print("  - 服务器统计数据")
    print("  - 自动维护功能（禁用/启用/删除）")

if __name__ == '__main__':
    db_path = os.getenv('DATABASE_PATH', 'data/cpa_manager.db')
    migrate_database(db_path)
