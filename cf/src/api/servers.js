/**
 * CPA 服务器管理 API
 */

import { jsonResponse } from './router';

export async function handleServers(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // GET /api/servers - 获取服务器列表
  if (path === '/api/servers' && request.method === 'GET') {
    return getServers(env);
  }

  // POST /api/servers - 添加服务器
  if (path === '/api/servers' && request.method === 'POST') {
    return addServer(request, env);
  }

  // PUT /api/servers/:id - 更新服务器
  const updateMatch = path.match(/^\/api\/servers\/([^/]+)$/);
  if (updateMatch && request.method === 'PUT') {
    return updateServer(updateMatch[1], request, env);
  }

  // DELETE /api/servers/:id - 删除服务器
  if (updateMatch && request.method === 'DELETE') {
    return deleteServer(updateMatch[1], env);
  }

  // POST /api/servers/:id/test - 测试服务器连接
  const testMatch = path.match(/^\/api\/servers\/([^/]+)\/test$/);
  if (testMatch && request.method === 'POST') {
    return testServer(testMatch[1], env);
  }

  return jsonResponse({ error: 'Not Found' }, 404);
}

/**
 * 获取服务器列表
 */
async function getServers(env) {
  const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
  const servers = serversData || [];

  return jsonResponse({
    success: true,
    servers
  });
}

/**
 * 添加服务器
 */
async function addServer(request, env) {
  try {
    const { name, base_url, token, enable_token_revive } = await request.json();

    if (!name || !base_url || !token) {
      return jsonResponse({ error: 'Missing required fields' }, 400);
    }

    const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
    const servers = serversData || [];

    const newServer = {
      id: crypto.randomUUID(),
      name,
      base_url,
      token,
      enable_token_revive: enable_token_revive !== false,
      created_at: Date.now()
    };

    servers.push(newServer);
    await env.ACCOUNTS.put('cpa_servers', JSON.stringify(servers));

    return jsonResponse({
      success: true,
      server: newServer
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 400);
  }
}

/**
 * 更新服务器
 */
async function updateServer(id, request, env) {
  try {
    const updates = await request.json();
    const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
    const servers = serversData || [];

    const index = servers.findIndex(s => s.id === id);
    if (index === -1) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    servers[index] = {
      ...servers[index],
      ...updates,
      id, // 保持 ID 不变
      updated_at: Date.now()
    };

    await env.ACCOUNTS.put('cpa_servers', JSON.stringify(servers));

    return jsonResponse({
      success: true,
      server: servers[index]
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 400);
  }
}

/**
 * 删除服务器
 */
async function deleteServer(id, env) {
  const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
  const servers = serversData || [];

  const filtered = servers.filter(s => s.id !== id);
  if (filtered.length === servers.length) {
    return jsonResponse({ error: 'Server not found' }, 404);
  }

  await env.ACCOUNTS.put('cpa_servers', JSON.stringify(filtered));

  return jsonResponse({ success: true });
}

/**
 * 测试服务器连接
 */
async function testServer(id, env) {
  const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
  const servers = serversData || [];

  const server = servers.find(s => s.id === id);
  if (!server) {
    return jsonResponse({ error: 'Server not found' }, 404);
  }

  try {
    const response = await fetch(`${server.base_url}/v0/management/auth-files`, {
      headers: {
        'Authorization': `Bearer ${server.token}`
      },
      signal: AbortSignal.timeout(10000) // 10秒超时
    });

    if (response.ok) {
      const data = await response.json();
      return jsonResponse({
        success: true,
        status: 'connected',
        accounts_count: data.files?.length || 0
      });
    } else {
      return jsonResponse({
        success: false,
        status: 'error',
        error: `HTTP ${response.status}`
      });
    }

  } catch (error) {
    return jsonResponse({
      success: false,
      status: 'error',
      error: error.message
    });
  }
}
