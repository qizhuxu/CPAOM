/**
 * 静态文件处理（前端）
 */

import { html } from './frontend/index.html';

export async function handleStatic(request, env, ctx) {
  const url = new URL(request.url);
  
  // 根路径返回前端页面
  if (url.pathname === '/' || url.pathname === '/index.html') {
    return new Response(html, {
      headers: {
        'Content-Type': 'text/html;charset=UTF-8'
      }
    });
  }

  return new Response('Not Found', { status: 404 });
}
