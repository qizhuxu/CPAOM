"""
数据库迁移脚本 - 同步日志扩展
添加新的同步日志字段和账号同步记录表
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
    
    # 1. 扩展 sync_logs 表
    print("1. 扩展 sync_logs 表...")
    
    new_columns = [
        ("sync_mode", "TEXT NOT NULL DEFAULT 'auto'"),
        ("accounts_total", "INTEGER DEFAULT 0"),
        ("accounts_active", "INTEGER DEFAULT 0"),
        ("accounts_disabled", "INTEGER DEFAULT 0"),
        ("accounts_401", "INTEGER DEFAULT 0"),
        ("accounts_100_percent", "INTEGER DEFAULT 0"),
        ("avg_usage_percent", "REAL DEFAULT 0"),
    ]
    
    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE sync_logs ADD COLUMN {col_name} {col_type}")
            print(f"   ✓ 添加 {col_name} 列")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"   - {col_name} 列已存在")
            else:
                print(f"   ✗ 添加 {col_name} 列失败: {e}")
    
    print()
    
    # 2. 创建 account_sync_logs 表
    print("2. 创建 account_sync_logs 表...")
    try:
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
        print("   ✓ 创建 account_sync_logs 表")
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_sync_logs_sync_log ON account_sync_logs(sync_log_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_sync_logs_server ON account_sync_logs(server_id)')
        print("   ✓ 创建索引")
        
    except sqlite3.OperationalError as e:
        print(f"   - account_sync_logs 表已存在或创建失败: {e}")
    
    print()
    
    # 3. 扩展 server_sync_config 表
    print("3. 扩展 server_sync_config 表...")
    try:
        cursor.execute("ALTER TABLE server_sync_config ADD COLUMN keep_sync_logs INTEGER DEFAULT 100")
        print("   ✓ 添加 keep_sync_logs 列")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("   - keep_sync_logs 列已存在")
        else:
            print(f"   ✗ 添加 keep_sync_logs 列失败: {e}")
    
    print()
    
    # 4. 创建额外索引
    print("4. 创建额外索引...")
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_logs_server ON sync_logs(server_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_logs_created ON sync_logs(created_at)')
        print("   ✓ 创建索引")
    except sqlite3.OperationalError as e:
        print(f"   - 索引已存在: {e}")
    
    print()
    
    conn.commit()
    conn.close()
    
    print("✅ 数据库迁移完成！")
    print()
    print("新增功能:")
    print("  - 同步日志现在记录更详细的统计信息")
    print("  - 新增账号级别的同步记录表")
    print("  - 支持配置保留同步日志数量")
    print()

if __name__ == '__main__':
    migrate_database()
