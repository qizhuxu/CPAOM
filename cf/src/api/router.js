/**
 * API 路由处理
 */

import { handleAuth } from './auth';
import { handleServers } from './servers';
import { handleAccounts } from './accounts';
import { handleOperations } from './operations';
import { handleStats } from './stats';
import { handleSync } from './sync';
import { handleScheduled } from './scheduled';

export async function handleAPI(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // 认证检查（除了登录接口）
  if (!path.startsWith('/api/auth/login')) {
    const authResult = await checkAuth(request, env);
    if (!authResult.success) {
      return jsonResponse({ error: authResult.error }, 401);
    }
  }

  // 路由分发
  if (path.startsWith('/api/auth')) {
    return handleAuth(request, env, ctx);
  }

  if (path.startsWith('/api/servers')) {
    return handleServers(request, env, ctx);
  }

  if (path.startsWith('/api/accounts')) {
    return handleAccounts(request, env, ctx);
  }

  if (path.startsWith('/api/operations')) {
    return handleOperations(request, env, ctx);
  }

  if (path.startsWith('/api/stats')) {
    return handleStats(request, env, ctx);
  }

  if (path.startsWith('/api/sync')) {
    return handleSync(request, env, ctx);
  }

  if (path.startsWith('/api/scheduled')) {
    return handleScheduled(request, env, ctx);
  }

  return jsonResponse({ error: 'Not Found' }, 404);
}

/**
 * 认证检查
 */
async function checkAuth(request, env) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return { success: false, error: 'Missing authorization token' };
  }

  const token = authHeader.substring(7);
  const session = await env.ACCOUNTS.get(`session:${token}`, { type: 'json' });

  if (!session) {
    return { success: false, error: 'Invalid or expired token' };
  }

  return { success: true, session };
}

/**
 * JSON 响应辅助函数
 */
export function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}
