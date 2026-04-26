-- CPA Manager Database Schema
-- 初始化数据库表结构

-- 认证文件备份表
CREATE TABLE IF NOT EXISTS auth_files_backup (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  server_id TEXT NOT NULL,
  server_name TEXT NOT NULL,
  filename TEXT NOT NULL,
  email TEXT,
  auth_data TEXT NOT NULL,  -- JSON 格式的完整认证数据
  status TEXT DEFAULT 'active',  -- active, disabled, error
  disabled INTEGER DEFAULT 0,  -- 0=启用, 1=禁用
  last_refresh TEXT,
  backup_time TEXT NOT NULL,  -- ISO 8601 格式
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(server_id, filename)
);

-- 为查询优化创建索引
CREATE INDEX IF NOT EXISTS idx_auth_files_server ON auth_files_backup(server_id);
CREATE INDEX IF NOT EXISTS idx_auth_files_email ON auth_files_backup(email);
CREATE INDEX IF NOT EXISTS idx_auth_files_status ON auth_files_backup(status);
CREATE INDEX IF NOT EXISTS idx_auth_files_backup_time ON auth_files_backup(backup_time);

-- Config.yml 备份表
CREATE TABLE IF NOT EXISTS config_backups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  server_id TEXT NOT NULL,
  server_name TEXT NOT NULL,
  config_content TEXT NOT NULL,  -- YAML 内容
  config_hash TEXT NOT NULL,  -- SHA-256 哈希，用于检测变化
  backup_time TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(server_id, config_hash)
);

CREATE INDEX IF NOT EXISTS idx_config_server ON config_backups(server_id);
CREATE INDEX IF NOT EXISTS idx_config_backup_time ON config_backups(backup_time);

-- 同步任务日志表
CREATE TABLE IF NOT EXISTS sync_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  server_id TEXT NOT NULL,
  server_name TEXT NOT NULL,
  sync_type TEXT NOT NULL,  -- auth_files, config, full
  status TEXT NOT NULL,  -- success, failed, partial
  files_synced INTEGER DEFAULT 0,
  files_failed INTEGER DEFAULT 0,
  error_message TEXT,
  duration_ms INTEGER,  -- 执行时间（毫秒）
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sync_logs_server ON sync_logs(server_id);
CREATE INDEX IF NOT EXISTS idx_sync_logs_type ON sync_logs(sync_type);
CREATE INDEX IF NOT EXISTS idx_sync_logs_created ON sync_logs(created_at);

-- 定时任务配置表
CREATE TABLE IF NOT EXISTS scheduled_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_name TEXT NOT NULL UNIQUE,
  task_type TEXT NOT NULL,  -- sync_auth, sync_config, check_usage, revive_tokens
  enabled INTEGER DEFAULT 1,  -- 0=禁用, 1=启用
  cron_expression TEXT NOT NULL,  -- Cron 表达式
  server_ids TEXT,  -- JSON 数组，null 表示所有服务器
  last_run TEXT,
  next_run TEXT,
  run_count INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 定时任务执行历史表
CREATE TABLE IF NOT EXISTS task_executions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  task_name TEXT NOT NULL,
  status TEXT NOT NULL,  -- success, failed, running
  result TEXT,  -- JSON 格式的执行结果
  error_message TEXT,
  started_at TEXT NOT NULL,
  completed_at TEXT,
  duration_ms INTEGER,
  FOREIGN KEY (task_id) REFERENCES scheduled_tasks(id)
);

CREATE INDEX IF NOT EXISTS idx_task_executions_task ON task_executions(task_id);
CREATE INDEX IF NOT EXISTS idx_task_executions_started ON task_executions(started_at);

-- 操作审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user TEXT NOT NULL,
  action TEXT NOT NULL,  -- login, logout, add_server, delete_server, sync, etc.
  resource_type TEXT,  -- server, account, config
  resource_id TEXT,
  details TEXT,  -- JSON 格式的详细信息
  ip_address TEXT,
  user_agent TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);

-- 系统统计表（用于仪表板）
CREATE TABLE IF NOT EXISTS system_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stat_date TEXT NOT NULL UNIQUE,  -- YYYY-MM-DD
  total_servers INTEGER DEFAULT 0,
  total_accounts INTEGER DEFAULT 0,
  active_accounts INTEGER DEFAULT 0,
  disabled_accounts INTEGER DEFAULT 0,
  error_accounts INTEGER DEFAULT 0,
  syncs_performed INTEGER DEFAULT 0,
  tokens_revived INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_system_stats_date ON system_stats(stat_date);
