/**
 * 认证 API
 */

import { jsonResponse } from './router';

export async function handleAuth(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // POST /api/auth/login
  if (path === '/api/auth/login' && request.method === 'POST') {
    return handleLogin(request, env);
  }

  // POST /api/auth/logout
  if (path === '/api/auth/logout' && request.method === 'POST') {
    return handleLogout(request, env);
  }

  // GET /api/auth/me
  if (path === '/api/auth/me' && request.method === 'GET') {
    return handleMe(request, env);
  }

  return jsonResponse({ error: 'Not Found' }, 404);
}

/**
 * 登录
 */
async function handleLogin(request, env) {
  try {
    const { username, password } = await request.json();

    // 从环境变量或 KV 获取管理员凭证
    const adminUsername = env.ADMIN_USERNAME || 'admin';
    const adminPassword = env.ADMIN_PASSWORD || 'admin123';

    if (username !== adminUsername || password !== adminPassword) {
      return jsonResponse({ error: 'Invalid credentials' }, 401);
    }

    // 生成会话 token
    const token = crypto.randomUUID();
    const session = {
      username,
      createdAt: Date.now(),
      expiresAt: Date.now() + 24 * 60 * 60 * 1000 // 24小时
    };

    // 存储会话（24小时过期）
    await env.ACCOUNTS.put(`session:${token}`, JSON.stringify(session), {
      expirationTtl: 24 * 60 * 60
    });

    return jsonResponse({
      success: true,
      token,
      user: { username }
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 400);
  }
}

/**
 * 登出
 */
async function handleLogout(request, env) {
  const authHeader = request.headers.get('Authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    await env.ACCOUNTS.delete(`session:${token}`);
  }

  return jsonResponse({ success: true });
}

/**
 * 获取当前用户信息
 */
async function handleMe(request, env) {
  const authHeader = request.headers.get('Authorization');
  const token = authHeader.substring(7);
  const session = await env.ACCOUNTS.get(`session:${token}`, { type: 'json' });

  if (!session) {
    return jsonResponse({ error: 'Unauthorized' }, 401);
  }

  return jsonResponse({
    user: {
      username: session.username,
      loginAt: session.createdAt
    }
  });
}
