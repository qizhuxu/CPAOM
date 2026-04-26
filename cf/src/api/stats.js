/**
 * 统计 API
 */

import { jsonResponse } from './router';
import { CPAClient } from '../utils/cpa-client';

export async function handleStats(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // GET /api/stats/overview - 总览统计
  if (path === '/api/stats/overview' && request.method === 'GET') {
    return getOverview(env);
  }

  // GET /api/stats/server/:id - 单个服务器统计
  const serverMatch = path.match(/^\/api\/stats\/server\/([^/]+)$/);
  if (serverMatch && request.method === 'GET') {
    return getServerStats(serverMatch[1], env);
  }

  return jsonResponse({ error: 'Not Found' }, 404);
}

/**
 * 获取总览统计
 */
async function getOverview(env) {
  try {
    const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
    const servers = serversData || [];

    let totalAccounts = 0;
    let totalActive = 0;
    let totalDisabled = 0;
    let totalError = 0;

    const serverStats = [];

    for (const server of servers) {
      try {
        const client = new CPAClient(server.base_url, server.token);
        const files = await client.getAuthFiles();

        const active = files.filter(f => !f.disabled && f.status === 'ready').length;
        const disabled = files.filter(f => f.disabled).length;
        const error = files.filter(f => f.status === 'error').length;

        totalAccounts += files.length;
        totalActive += active;
        totalDisabled += disabled;
        totalError += error;

        serverStats.push({
          server_id: server.id,
          server_name: server.name,
          total: files.length,
          active,
          disabled,
          error,
          status: 'online'
        });

      } catch (error) {
        serverStats.push({
          server_id: server.id,
          server_name: server.name,
          status: 'offline',
          error: error.message
        });
      }
    }

    return jsonResponse({
      success: true,
      overview: {
        total_servers: servers.length,
        total_accounts: totalAccounts,
        total_active: totalActive,
        total_disabled: totalDisabled,
        total_error: totalError
      },
      servers: serverStats
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 获取单个服务器统计
 */
async function getServerStats(serverId, env) {
  try {
    const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
    const servers = serversData || [];
    const server = servers.find(s => s.id === serverId);

    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    const files = await client.getAuthFiles();

    const stats = {
      total: files.length,
      active: files.filter(f => !f.disabled && f.status === 'ready').length,
      disabled: files.filter(f => f.disabled).length,
      error: files.filter(f => f.status === 'error').length,
      ready: files.filter(f => f.status === 'ready').length,
      by_status: {}
    };

    // 按状态分组
    files.forEach(file => {
      const status = file.status || 'unknown';
      stats.by_status[status] = (stats.by_status[status] || 0) + 1;
    });

    return jsonResponse({
      success: true,
      server: {
        id: server.id,
        name: server.name,
        base_url: server.base_url
      },
      stats
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}
