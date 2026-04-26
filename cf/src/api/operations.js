/**
 * 批量操作 API
 */

import { jsonResponse } from './router';
import { CPAClient } from '../utils/cpa-client';
import { refreshOAuthToken } from '../utils/oauth';

export async function handleOperations(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // POST /api/operations/check-usage - 批量检查账号使用情况
  if (path === '/api/operations/check-usage' && request.method === 'POST') {
    return checkUsage(request, env, ctx);
  }

  // POST /api/operations/revive-tokens - 批量复活 Token
  if (path === '/api/operations/revive-tokens' && request.method === 'POST') {
    return reviveTokens(request, env, ctx);
  }

  // POST /api/operations/download-pack - 下载并打包
  if (path === '/api/operations/download-pack' && request.method === 'POST') {
    return downloadPack(request, env, ctx);
  }

  // POST /api/operations/batch-upload - 批量上传
  if (path === '/api/operations/batch-upload' && request.method === 'POST') {
    return batchUpload(request, env, ctx);
  }

  return jsonResponse({ error: 'Not Found' }, 404);
}

/**
 * 批量检查账号使用情况
 */
async function checkUsage(request, env, ctx) {
  try {
    const { server_id } = await request.json();

    if (!server_id) {
      return jsonResponse({ error: 'Missing server_id' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    const files = await client.getAuthFiles();

    const results = [];
    let successCount = 0;
    let errorCount = 0;
    let disabledCount = 0;

    for (const file of files) {
      if (file.disabled) {
        disabledCount++;
        continue;
      }

      try {
        const usage = await client.checkUsage(file.auth_index, file.email);
        
        if (usage.status_code === 200) {
          successCount++;
          results.push({
            filename: file.name,
            email: file.email,
            status: 'success',
            usage: usage.body
          });
        } else if (usage.status_code === 401) {
          errorCount++;
          results.push({
            filename: file.name,
            email: file.email,
            status: 'token_expired',
            needs_revive: true
          });
        } else {
          errorCount++;
          results.push({
            filename: file.name,
            email: file.email,
            status: 'error',
            error: `HTTP ${usage.status_code}`
          });
        }
      } catch (error) {
        errorCount++;
        results.push({
          filename: file.name,
          email: file.email,
          status: 'error',
          error: error.message
        });
      }
    }

    return jsonResponse({
      success: true,
      summary: {
        total: files.length,
        checked: results.length,
        success: successCount,
        error: errorCount,
        disabled: disabledCount
      },
      results
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 批量复活 Token
 */
async function reviveTokens(request, env, ctx) {
  try {
    const { server_id, filenames } = await request.json();

    if (!server_id || !filenames || !Array.isArray(filenames)) {
      return jsonResponse({ error: 'Missing or invalid parameters' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    if (!server.enable_token_revive) {
      return jsonResponse({ error: 'Token revive is disabled for this server' }, 400);
    }

    const client = new CPAClient(server.base_url, server.token);
    const results = [];

    for (const filename of filenames) {
      try {
        // 下载认证文件
        const authData = await client.downloadAuthFile(filename);
        
        if (!authData.refresh_token) {
          results.push({
            filename,
            status: 'error',
            error: 'No refresh_token found'
          });
          continue;
        }

        // 尝试刷新 Token
        let success = false;
        let lastError = null;

        for (let attempt = 1; attempt <= 3; attempt++) {
          try {
            const newTokens = await refreshOAuthToken(authData.refresh_token);
            
            // 更新认证数据
            authData.access_token = newTokens.access_token;
            authData.refresh_token = newTokens.refresh_token;
            if (newTokens.id_token) {
              authData.id_token = newTokens.id_token;
            }

            // 上传更新后的文件
            await client.uploadAuthFile(authData, filename);

            // 验证新 Token
            const testResult = await client.checkUsage(authData.auth_index || authData.email, authData.email);
            
            if (testResult.status_code === 200) {
              success = true;
              results.push({
                filename,
                status: 'success',
                attempts: attempt
              });
              break;
            }
          } catch (error) {
            lastError = error.message;
          }
        }

        if (!success) {
          // 3次尝试都失败，禁用账号
          await client.disableAuthFile(filename);
          results.push({
            filename,
            status: 'failed',
            error: lastError,
            disabled: true
          });
        }

      } catch (error) {
        results.push({
          filename,
          status: 'error',
          error: error.message
        });
      }
    }

    const successCount = results.filter(r => r.status === 'success').length;
    const failedCount = results.filter(r => r.status === 'failed').length;

    return jsonResponse({
      success: true,
      summary: {
        total: filenames.length,
        success: successCount,
        failed: failedCount
      },
      results
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 下载并打包（返回下载链接）
 */
async function downloadPack(request, env, ctx) {
  try {
    const { server_id } = await request.json();

    if (!server_id) {
      return jsonResponse({ error: 'Missing server_id' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    const files = await client.getAuthFiles();

    // 过滤掉禁用的账号
    const activeFiles = files.filter(f => !f.disabled);

    // 下载所有文件
    const accounts = [];
    for (const file of activeFiles) {
      try {
        const authData = await client.downloadAuthFile(file.name);
        accounts.push({
          filename: file.name,
          data: authData
        });
      } catch (error) {
        console.error(`Failed to download ${file.name}:`, error);
      }
    }

    // 生成唯一 ID 并存储到 KV
    const packId = crypto.randomUUID();
    const packData = {
      server_id,
      server_name: server.name,
      created_at: Date.now(),
      count: accounts.length,
      accounts
    };

    // 存储 1 小时
    await env.ACCOUNTS.put(`pack:${packId}`, JSON.stringify(packData), {
      expirationTtl: 3600
    });

    return jsonResponse({
      success: true,
      pack_id: packId,
      download_url: `/api/operations/download-pack/${packId}`,
      count: accounts.length,
      expires_in: 3600
    });

  } catch (error) {
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 批量上传
 */
async function batchUpload(request, env, ctx) {
  try {
    const { server_id, accounts } = await request.json();

    if (!server_id || !accounts || !Array.isArray(accounts)) {
      return jsonResponse({ error: 'Missing or invalid parameters' }, 400);
    }

    const server = await getServerById(server_id, env);
    if (!server) {
      return jsonResponse({ error: 'Server not found' }, 404);
    }

    const client = new CPAClient(server.base_url, server.token);
    const results = [];

    for (const account of accounts) {
      try {
        await client.uploadAuthFile(account.data, account.filename);
        results.push({
          filename: account.filename,
          status: 'success'
        });
      } catch (error) {
        results.push({
          filename: account.filename,
          status: 'error',
          error: error.message
        });
      }
    }

    const successCount = results.filter(r => r.status === 'success').length;

    return jsonResponse({
      success: true,
      summary: {
        total: accounts.length,
        success: successCount,
        failed: accounts.length - successCount
      },
      results
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
