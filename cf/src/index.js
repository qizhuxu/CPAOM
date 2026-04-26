/**
 * CPA Manager - Cloudflare Workers
 * 主入口文件
 */

import { handleAPI } from './api/router';
import { handleStatic } from './static';
import { corsHeaders } from './utils/cors';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 处理 CORS 预检请求
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: corsHeaders
      });
    }

    try {
      // API 路由
      if (url.pathname.startsWith('/api/')) {
        const response = await handleAPI(request, env, ctx);
        return addCorsHeaders(response);
      }

      // 静态文件（前端）
      return handleStatic(request, env, ctx);

    } catch (error) {
      console.error('Error:', error);
      return new Response(
        JSON.stringify({
          error: 'Internal Server Error',
          message: error.message
        }),
        {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        }
      );
    }
  }
};

/**
 * 添加 CORS 头
 */
function addCorsHeaders(response) {
  const newResponse = new Response(response.body, response);
  Object.entries(corsHeaders).forEach(([key, value]) => {
    newResponse.headers.set(key, value);
  });
  return newResponse;
}
