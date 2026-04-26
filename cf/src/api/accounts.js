/**
 * 账号管理 API
 */

import { jsonResponse } from './router';
import { CPAClient } from '../utils/cpa-client';

export async function handleAccounts(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // GET /api/accounts - 获取所有账号
  if (path === '/api/accounts' && request.method === 'GET') {
    return getAccounts(url, env);
  }

  // GET /api/accounts/:filename - 获取单个账号详情
  const detailMatch = path.match(/^\/api\/accounts\/([^/]+)$/);
  if (detailMatch && request.method === 'GET') {
    return getAccountDetail(detailMatch[1], url, env);
  }

  // POST /api/accounts/upload - 上传账号
  if (path === '/api/accounts/upload' && request.method === 'POST') {
    return uploadAccount(request, env);
  }

  // DELETE /api/accounts/:filename - 删除账号
  if (detailMatch && request.method === 'DELETE') {
    return deleteAccount(detailMatch[1], url, env);
  }

  // PATCH /api/accounts/:filename/status - 更新账号状态
  const statusMatch = path.match(/^\/api\/accounts\/([^/]+)\/status$/);
  if (statusMatch && request.method === 'PATCH') {
    return updateAccountStatus(statusMatch[1], request, env);
  }

  return jsonResponse({ error: 'Not Found' }, 404);
}

/**
 * 获取所有账号
 */
async function getAccounts(url, env) {
  try {
    const serverId = url.searchParams.get('server_id');
    if (!serverId) {
      return jsonResponse({ error: 'Missing server_id parameter' }, 400);
    }

    const server = await getServerById(serverId, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    const files = await client.getAuthFiles();

    return jsonResponse({
      success: true,
      accounts: files,
      total: files.length
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 获取账号详情
 */
async function getAccountDetail(filename, url, env) {
  try {
    const serverId = url.searchParams.get('server_id');
    if (!serverId) {
      return jsonResponse({ error: 'Missing server_id parameter' }, 400);
    }

    const server = await getServerById(serverId, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    const authData = await client.downloadAuthFile(filename);

    return jsonResponse({
      success: true,
      account: authData
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 上传账号
 */
async function uploadAccount(request, env) {
  try {
    const { server_id, auth_data, filename } = await request.json();

    if (!server_id || !auth_data || !filename) {
      return jsonResponse({ error: 'Missing required fields' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    await client.uploadAuthFile(auth_data, filename);

    return jsonResponse({
      success: true,
      message: 'Account uploaded successfully'
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 删除账号
 */
async function deleteAccount(filename, url, env) {
  try {
    const serverId = url.searchParams.get('server_id');
    if (!serverId) {
      return jsonResponse({ error: 'Missing server_id parameter' }, 400);
    }

    const server = await getServerById(serverId, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    await client.deleteAuthFile(filename);

    return jsonResponse({
      success: true,
      message: 'Account deleted successfully'
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 更新账号状态
 */
async function updateAccountStatus(filename, request, env) {
  try {
    const { server_id, disabled } = await request.json();

    if (!server_id || disabled === undefined) {
      return jsonResponse({ error: 'Missing required fields' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    
    if (disabled) {
      await client.disableAuthFile(filename);
    } else {
      await client.enableAuthFile(filename);
    }

    return jsonResponse({
      success: true,
      message: `Account ${disabled ? 'disabled' : 'enabled'} successfully`
    });

  } catch (error) {
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
