/**
 * D1 数据库服务
 * 处理所有数据库操作
 */

/**
 * 备份认证文件到 D1
 */
export async function backupAuthFile(db, serverInfo, fileInfo, authData) {
  const now = new Date().toISOString();
  
  await db.prepare(`
    INSERT INTO auth_files_backup (
      server_id, server_name, filename, email, auth_data,
      status, disabled, last_refresh, backup_time, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(server_id, filename) DO UPDATE SET
      email = excluded.email,
      auth_data = excluded.auth_data,
      status = excluded.status,
      disabled = excluded.disabled,
      last_refresh = excluded.last_refresh,
      backup_time = excluded.backup_time,
      updated_at = excluded.updated_at
  `).bind(
    serverInfo.id,
    serverInfo.name,
    fileInfo.name,
    fileInfo.email || authData.email,
    JSON.stringify(authData),
    fileInfo.status || 'active',
    fileInfo.disabled ? 1 : 0,
    fileInfo.last_refresh || null,
    now,
    now
  ).run();
}

/**
 * 批量备份认证文件
 */
export async function batchBackupAuthFiles(db, serverInfo, files, authDataMap) {
  const statements = [];
  const now = new Date().toISOString();
  
  for (const file of files) {
    const authData = authDataMap[file.name];
    if (!authData) continue;
    
    statements.push(
      db.prepare(`
        INSERT INTO auth_files_backup (
          server_id, server_name, filename, email, auth_data,
          status, disabled, last_refresh, backup_time, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(server_id, filename) DO UPDATE SET
          email = excluded.email,
          auth_data = excluded.auth_data,
          status = excluded.status,
          disabled = excluded.disabled,
          last_refresh = excluded.last_refresh,
          backup_time = excluded.backup_time,
          updated_at = excluded.updated_at
      `).bind(
        serverInfo.id,
        serverInfo.name,
        file.name,
        file.email || authData.email,
        JSON.stringify(authData),
        file.status || 'active',
        file.disabled ? 1 : 0,
        file.last_refresh || null,
        now,
        now
      )
    );
  }
  
  if (statements.length > 0) {
    await db.batch(statements);
  }
  
  return statements.length;
}

/**
 * 备份 Config.yml
 */
export async function backupConfig(db, serverInfo, configContent) {
  const now = new Date().toISOString();
  
  // 计算配置内容的哈希
  const encoder = new TextEncoder();
  const data = encoder.encode(configContent);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const configHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  
  try {
    await db.prepare(`
      INSERT INTO config_backups (
        server_id, server_name, config_content, config_hash, backup_time
      ) VALUES (?, ?, ?, ?, ?)
    `).bind(
      serverInfo.id,
      serverInfo.name,
      configContent,
      configHash,
      now
    ).run();
    
    return { success: true, hash: configHash };
  } catch (error) {
    // 如果是重复（相同哈希），忽略错误
    if (error.message.includes('UNIQUE constraint')) {
      return { success: true, hash: configHash, duplicate: true };
    }
    throw error;
  }
}

/**
 * 记录同步日志
 */
export async function logSync(db, serverInfo, syncType, status, stats, error = null, durationMs = 0) {
  await db.prepare(`
    INSERT INTO sync_logs (
      server_id, server_name, sync_type, status,
      files_synced, files_failed, error_message, duration_ms
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    serverInfo.id,
    serverInfo.name,
    syncType,
    status,
    stats.synced || 0,
    stats.failed || 0,
    error,
    durationMs
  ).run();
}

/**
 * 获取备份的认证文件
 */
export async function getBackupAuthFiles(db, serverId, options = {}) {
  let query = `
    SELECT * FROM auth_files_backup
    WHERE server_id = ?
  `;
  const params = [serverId];
  
  if (options.status) {
    query += ` AND status = ?`;
    params.push(options.status);
  }
  
  if (options.disabled !== undefined) {
    query += ` AND disabled = ?`;
    params.push(options.disabled ? 1 : 0);
  }
  
  query += ` ORDER BY backup_time DESC`;
  
  if (options.limit) {
    query += ` LIMIT ?`;
    params.push(options.limit);
  }
  
  const result = await db.prepare(query).bind(...params).all();
  return result.results || [];
}

/**
 * 获取配置备份历史
 */
export async function getConfigBackups(db, serverId, limit = 10) {
  const result = await db.prepare(`
    SELECT * FROM config_backups
    WHERE server_id = ?
    ORDER BY backup_time DESC
    LIMIT ?
  `).bind(serverId, limit).all();
  
  return result.results || [];
}

/**
 * 获取同步日志
 */
export async function getSyncLogs(db, serverId = null, limit = 50) {
  let query = `SELECT * FROM sync_logs`;
  const params = [];
  
  if (serverId) {
    query += ` WHERE server_id = ?`;
    params.push(serverId);
  }
  
  query += ` ORDER BY created_at DESC LIMIT ?`;
  params.push(limit);
  
  const result = await db.prepare(query).bind(...params).all();
  return result.results || [];
}

/**
 * 创建定时任务
 */
export async function createScheduledTask(db, task) {
  const now = new Date().toISOString();
  
  await db.prepare(`
    INSERT INTO scheduled_tasks (
      task_name, task_type, enabled, cron_expression,
      server_ids, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    task.name,
    task.type,
    task.enabled ? 1 : 0,
    task.cronExpression,
    task.serverIds ? JSON.stringify(task.serverIds) : null,
    now,
    now
  ).run();
}

/**
 * 获取所有启用的定时任务
 */
export async function getEnabledTasks(db) {
  const result = await db.prepare(`
    SELECT * FROM scheduled_tasks
    WHERE enabled = 1
    ORDER BY task_name
  `).all();
  
  return result.results || [];
}

/**
 * 更新任务执行时间
 */
export async function updateTaskRunTime(db, taskId, lastRun, nextRun) {
  await db.prepare(`
    UPDATE scheduled_tasks
    SET last_run = ?, next_run = ?, run_count = run_count + 1, updated_at = ?
    WHERE id = ?
  `).bind(lastRun, nextRun, new Date().toISOString(), taskId).run();
}

/**
 * 记录任务执行
 */
export async function logTaskExecution(db, taskId, taskName, status, result = null, error = null, startTime, endTime) {
  const durationMs = endTime - startTime;
  
  await db.prepare(`
    INSERT INTO task_executions (
      task_id, task_name, status, result, error_message,
      started_at, completed_at, duration_ms
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    taskId,
    taskName,
    status,
    result ? JSON.stringify(result) : null,
    error,
    new Date(startTime).toISOString(),
    new Date(endTime).toISOString(),
    durationMs
  ).run();
}

/**
 * 记录审计日志
 */
export async function logAudit(db, user, action, resourceType = null, resourceId = null, details = null, request = null) {
  const ipAddress = request?.headers.get('cf-connecting-ip') || 
                    request?.headers.get('x-forwarded-for') || 
                    'unknown';
  const userAgent = request?.headers.get('user-agent') || 'unknown';
  
  await db.prepare(`
    INSERT INTO audit_logs (
      user, action, resource_type, resource_id, details,
      ip_address, user_agent
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    user,
    action,
    resourceType,
    resourceId,
    details ? JSON.stringify(details) : null,
    ipAddress,
    userAgent
  ).run();
}

/**
 * 更新系统统计
 */
export async function updateSystemStats(db, stats) {
  const today = new Date().toISOString().split('T')[0];
  const now = new Date().toISOString();
  
  await db.prepare(`
    INSERT INTO system_stats (
      stat_date, total_servers, total_accounts, active_accounts,
      disabled_accounts, error_accounts, syncs_performed,
      tokens_revived, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(stat_date) DO UPDATE SET
      total_servers = excluded.total_servers,
      total_accounts = excluded.total_accounts,
      active_accounts = excluded.active_accounts,
      disabled_accounts = excluded.disabled_accounts,
      error_accounts = excluded.error_accounts,
      syncs_performed = syncs_performed + excluded.syncs_performed,
      tokens_revived = tokens_revived + excluded.tokens_revived,
      updated_at = excluded.updated_at
  `).bind(
    today,
    stats.totalServers || 0,
    stats.totalAccounts || 0,
    stats.activeAccounts || 0,
    stats.disabledAccounts || 0,
    stats.errorAccounts || 0,
    stats.syncsPerformed || 0,
    stats.tokensRevived || 0,
    now
  ).run();
}

/**
 * 获取系统统计（最近 N 天）
 */
export async function getSystemStats(db, days = 30) {
  const result = await db.prepare(`
    SELECT * FROM system_stats
    ORDER BY stat_date DESC
    LIMIT ?
  `).bind(days).all();
  
  return result.results || [];
}

/**
 * 清理旧数据
 */
export async function cleanupOldData(db, daysToKeep = 90) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
  const cutoff = cutoffDate.toISOString();
  
  // 清理旧的同步日志
  await db.prepare(`
    DELETE FROM sync_logs WHERE created_at < ?
  `).bind(cutoff).run();
  
  // 清理旧的任务执行记录
  await db.prepare(`
    DELETE FROM task_executions WHERE started_at < ?
  `).bind(cutoff).run();
  
  // 清理旧的审计日志
  await db.prepare(`
    DELETE FROM audit_logs WHERE created_at < ?
  `).bind(cutoff).run();
  
  // 保留每个服务器最新的 10 个配置备份
  await db.prepare(`
    DELETE FROM config_backups
    WHERE id NOT IN (
      SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY server_id ORDER BY backup_time DESC) as rn
        FROM config_backups
      ) WHERE rn <= 10
    )
  `).run();
}
