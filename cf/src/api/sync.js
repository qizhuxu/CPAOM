/**
 * 数据同步 API
 */

import { jsonResponse } from './router';
import { CPAClient } from '../utils/cpa-client';
import {
  batchBackupAuthFiles,
  backupConfig,
  logSync,
  getBackupAuthFiles,
  getConfigBackups,
  getSyncLogs
} from '../utils/db-service';

export async function handleSync(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // POST /api/sync/auth-files - 同步认证文件
  if (path === '/api/sync/auth-files' && request.method === 'POST') {
    return syncAuthFiles(request, env);
  }

  // POST /api/sync/config - 同步配置文件
  if (path === '/api/sync/config' && request.method === 'POST') {
    return syncConfig(request, env);
  }

  // POST /api/sync/full - 完整同步
  if (path === '/api/sync/full' && request.method === 'POST') {
    return fullSync(request, env);
  }

  // GET /api/sync/backups/auth-files - 获取认证文件备份
  if (path === '/api/sync/backups/auth-files' && request.method === 'GET') {
    return getAuthFileBackups(url, env);
  }

  // GET /api/sync/backups/config - 获取配置备份
  if (path === '/api/sync/backups/config' && request.method === 'GET') {
    return getConfigBackupHistory(url, env);
  }

  // GET /api/sync/logs - 获取同步日志
  if (path === '/api/sync/logs' && request.method === 'GET') {
    return getSyncLogsAPI(url, env);
  }

  // POST /api/sync/restore/auth-file - 从备份恢复认证文件
  if (path === '/api/sync/restore/auth-file' && request.method === 'POST') {
    return restoreAuthFile(request, env);
  }

  return jsonResponse({ error: 'Not Found' }, 404);
}

/**
 * 同步认证文件到 D1
 */
async function syncAuthFiles(request, env) {
  const startTime = Date.now();
  
  try {
    const { server_id, only_active } = await request.json();

    if (!server_id) {
      return jsonResponse({ error: 'Missing server_id' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    const files = await client.getAuthFiles();

    // 过滤：只同步活跃账号（如果指定）
    const filesToSync = only_active 
      ? files.filter(f => !f.disabled && f.status === 'ready')
      : files;

    // 下载所有认证文件
    const authDataMap = {};
    const downloadPromises = filesToSync.map(async (file) => {
      try {
        const authData = await client.downloadAuthFile(file.name);
        authDataMap[file.name] = authData;
      } catch (error) {
        console.error(`Failed to download ${file.name}:`, error);
      }
    });

    await Promise.all(downloadPromises);

    // 批量备份到 D1
    const syncedCount = await batchBackupAuthFiles(
      env.DB,
      server,
      filesToSync,
      authDataMap
    );

    const duration = Date.now() - startTime;

    // 记录同步日志
    await logSync(
      env.DB,
      server,
      'auth_files',
      'success',
      { synced: syncedCount, failed: filesToSync.length - syncedCount },
      null,
      duration
    );

    return jsonResponse({
      success: true,
      synced: syncedCount,
      total: filesToSync.length,
      duration_ms: duration
    });

  } catch (error) {
    const duration = Date.now() - startTime;
    console.error('Sync auth files error:', error);
    
    return jsonResponse({
      error: error.message,
      duration_ms: duration
    }, 500);
  }
}

/**
 * 同步配置文件到 D1
 */
async function syncConfig(request, env) {
  const startTime = Date.now();
  
  try {
    const { server_id } = await request.json();

    if (!server_id) {
      return jsonResponse({ error: 'Missing server_id' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    // 下载 config.yaml
    const response = await fetch(`${server.base_url}/v0/management/config.yaml`, {
      headers: {
        'Authorization': `Bearer ${server.token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to download config: ${response.status}`);
    }

    const configContent = await response.text();

    // 备份到 D1
    const result = await backupConfig(env.DB, server, configContent);

    const duration = Date.now() - startTime;

    // 记录同步日志
    await logSync(
      env.DB,
      server,
      'config',
      'success',
      { synced: 1, failed: 0 },
      null,
      duration
    );

    return jsonResponse({
      success: true,
      hash: result.hash,
      duplicate: result.duplicate || false,
      size: configContent.length,
      duration_ms: duration
    });

  } catch (error) {
    const duration = Date.now() - startTime;
    console.error('Sync config error:', error);
    
    return jsonResponse({
      error: error.message,
      duration_ms: duration
    }, 500);
  }
}

/**
 * 完整同步（认证文件 + 配置）
 */
async function fullSync(request, env) {
  const startTime = Date.now();
  
  try {
    const { server_id, only_active } = await request.json();

    if (!server_id) {
      return jsonResponse({ error: 'Missing server_id' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const results = {
      auth_files: { success: false },
      config: { success: false }
    };

    // 同步认证文件
    try {
      const client = new CPAClient(server.base_url, server.token);
      const files = await client.getAuthFiles();
      const filesToSync = only_active 
        ? files.filter(f => !f.disabled && f.status === 'ready')
        : files;

      const authDataMap = {};
      await Promise.all(filesToSync.map(async (file) => {
        try {
          const authData = await client.downloadAuthFile(file.name);
          authDataMap[file.name] = authData;
        } catch (error) {
          console.error(`Failed to download ${file.name}:`, error);
        }
      }));

      const syncedCount = await batchBackupAuthFiles(
        env.DB,
        server,
        filesToSync,
        authDataMap
      );

      results.auth_files = {
        success: true,
        synced: syncedCount,
        total: filesToSync.length
      };
    } catch (error) {
      results.auth_files = {
        success: false,
        error: error.message
      };
    }

    // 同步配置
    try {
      const response = await fetch(`${server.base_url}/v0/management/config.yaml`, {
        headers: {
          'Authorization': `Bearer ${server.token}`
        }
      });

      if (response.ok) {
        const configContent = await response.text();
        const result = await backupConfig(env.DB, server, configContent);
        
        results.config = {
          success: true,
          hash: result.hash,
          duplicate: result.duplicate || false
        };
      } else {
        results.config = {
          success: false,
          error: `HTTP ${response.status}`
        };
      }
    } catch (error) {
      results.config = {
        success: false,
        error: error.message
      };
    }

    const duration = Date.now() - startTime;

    // 记录同步日志
    const status = results.auth_files.success && results.config.success 
      ? 'success' 
      : (results.auth_files.success || results.config.success ? 'partial' : 'failed');

    await logSync(
      env.DB,
      server,
      'full',
      status,
      {
        synced: (results.auth_files.synced || 0) + (results.config.success ? 1 : 0),
        failed: 0
      },
      null,
      duration
    );

    return jsonResponse({
      success: status !== 'failed',
      status,
      results,
      duration_ms: duration
    });

  } catch (error) {
    const duration = Date.now() - startTime;
    console.error('Full sync error:', error);
    
    return jsonResponse({
      error: error.message,
      duration_ms: duration
    }, 500);
  }
}

/**
 * 获取认证文件备份
 */
async function getAuthFileBackups(url, env) {
  try {
    const serverId = url.searchParams.get('server_id');
    const status = url.searchParams.get('status');
    const disabled = url.searchParams.get('disabled');
    const limit = parseInt(url.searchParams.get('limit') || '100');

    if (!serverId) {
      return jsonResponse({ error: 'Missing server_id' }, 400);
    }

    const options = { limit };
    if (status) options.status = status;
    if (disabled !== null) options.disabled = disabled === 'true';

    const backups = await getBackupAuthFiles(env.DB, serverId, options);

    // 解析 auth_data JSON
    const parsedBackups = backups.map(backup => ({
      ...backup,
      auth_data: JSON.parse(backup.auth_data),
      disabled: backup.disabled === 1
    }));

    return jsonResponse({
      success: true,
      backups: parsedBackups,
      total: parsedBackups.length
    });

  } catch (error) {
    console.error('Get auth file backups error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 获取配置备份历史
 */
async function getConfigBackupHistory(url, env) {
  try {
    const serverId = url.searchParams.get('server_id');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    if (!serverId) {
      return jsonResponse({ error: 'Missing server_id' }, 400);
    }

    const backups = await getConfigBackups(env.DB, serverId, limit);

    return jsonResponse({
      success: true,
      backups,
      total: backups.length
    });

  } catch (error) {
    console.error('Get config backups error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 获取同步日志
 */
async function getSyncLogsAPI(url, env) {
  try {
    const serverId = url.searchParams.get('server_id');
    const limit = parseInt(url.searchParams.get('limit') || '50');

    const logs = await getSyncLogs(env.DB, serverId, limit);

    return jsonResponse({
      success: true,
      logs,
      total: logs.length
    });

  } catch (error) {
    console.error('Get sync logs error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 从备份恢复认证文件
 */
async function restoreAuthFile(request, env) {
  try {
    const { server_id, filename } = await request.json();

    if (!server_id || !filename) {
      return jsonResponse({ error: 'Missing required fields' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    // 从 D1 获取备份
    const backups = await getBackupAuthFiles(env.DB, server_id, { limit: 1 });
    const backup = backups.find(b => b.filename === filename);

    if (!backup) {
      return jsonResponse({ error: 'Backup not found' }, 404);
    }

    // 恢复到 CPA 服务器
    const authData = JSON.parse(backup.auth_data);
    const client = new CPAClient(server.base_url, server.token);
    await client.uploadAuthFile(authData, filename);

    return jsonResponse({
      success: true,
      message: 'Auth file restored successfully',
      filename
    });

  } catch (error) {
    console.error('Restore auth file error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 辅助函数：根据 ID 获取服务器
 */
async function getServerById(id, env) {
  const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
  const servers = serversData || [];
  return servers.find(s => s.id === id);
}
