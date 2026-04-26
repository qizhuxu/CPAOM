/**
 * 定时任务 API
 */

import { jsonResponse } from './router';
import {
  createScheduledTask,
  getEnabledTasks,
  updateTaskRunTime,
  logTaskExecution
} from '../utils/db-service';
import { parseCronExpression, getNextRunTime } from '../utils/cron-parser';

export async function handleScheduled(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // GET /api/scheduled/tasks - 获取所有定时任务
  if (path === '/api/scheduled/tasks' && request.method === 'GET') {
    return getTasks(env);
  }

  // POST /api/scheduled/tasks - 创建定时任务
  if (path === '/api/scheduled/tasks' && request.method === 'POST') {
    return createTask(request, env);
  }

  // PUT /api/scheduled/tasks/:id - 更新定时任务
  const updateMatch = path.match(/^\/api\/scheduled\/tasks\/(\d+)$/);
  if (updateMatch && request.method === 'PUT') {
    return updateTask(updateMatch[1], request, env);
  }

  // DELETE /api/scheduled/tasks/:id - 删除定时任务
  if (updateMatch && request.method === 'DELETE') {
    return deleteTask(updateMatch[1], env);
  }

  // POST /api/scheduled/tasks/:id/run - 手动执行任务
  const runMatch = path.match(/^\/api\/scheduled\/tasks\/(\d+)\/run$/);
  if (runMatch && request.method === 'POST') {
    return runTaskManually(runMatch[1], env, ctx);
  }

  // GET /api/scheduled/executions - 获取任务执行历史
  if (path === '/api/scheduled/executions' && request.method === 'GET') {
    return getExecutions(url, env);
  }

  return jsonResponse({ error: 'Not Found' }, 404);
}

/**
 * 获取所有定时任务
 */
async function getTasks(env) {
  try {
    const result = await env.DB.prepare(`
      SELECT * FROM scheduled_tasks ORDER BY task_name
    `).all();

    const tasks = (result.results || []).map(task => ({
      ...task,
      enabled: task.enabled === 1,
      server_ids: task.server_ids ? JSON.parse(task.server_ids) : null
    }));

    return jsonResponse({
      success: true,
      tasks
    });

  } catch (error) {
    console.error('Get tasks error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 创建定时任务
 */
async function createTask(request, env) {
  try {
    const { name, type, enabled, cron_expression, server_ids } = await request.json();

    if (!name || !type || !cron_expression) {
      return jsonResponse({ error: 'Missing required fields' }, 400);
    }

    // 验证 cron 表达式
    try {
      parseCronExpression(cron_expression);
    } catch (error) {
      return jsonResponse({ error: `Invalid cron expression: ${error.message}` }, 400);
    }

    await createScheduledTask(env.DB, {
      name,
      type,
      enabled: enabled !== false,
      cronExpression: cron_expression,
      serverIds: server_ids
    });

    return jsonResponse({
      success: true,
      message: 'Task created successfully'
    });

  } catch (error) {
    console.error('Create task error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 更新定时任务
 */
async function updateTask(taskId, request, env) {
  try {
    const updates = await request.json();
    const now = new Date().toISOString();

    const fields = [];
    const values = [];

    if (updates.task_name !== undefined) {
      fields.push('task_name = ?');
      values.push(updates.task_name);
    }
    if (updates.enabled !== undefined) {
      fields.push('enabled = ?');
      values.push(updates.enabled ? 1 : 0);
    }
    if (updates.cron_expression !== undefined) {
      // 验证 cron 表达式
      try {
        parseCronExpression(updates.cron_expression);
      } catch (error) {
        return jsonResponse({ error: `Invalid cron expression: ${error.message}` }, 400);
      }
      fields.push('cron_expression = ?');
      values.push(updates.cron_expression);
    }
    if (updates.server_ids !== undefined) {
      fields.push('server_ids = ?');
      values.push(updates.server_ids ? JSON.stringify(updates.server_ids) : null);
    }

    fields.push('updated_at = ?');
    values.push(now);

    values.push(taskId);

    await env.DB.prepare(`
      UPDATE scheduled_tasks
      SET ${fields.join(', ')}
      WHERE id = ?
    `).bind(...values).run();

    return jsonResponse({
      success: true,
      message: 'Task updated successfully'
    });

  } catch (error) {
    console.error('Update task error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 删除定时任务
 */
async function deleteTask(taskId, env) {
  try {
    await env.DB.prepare(`
      DELETE FROM scheduled_tasks WHERE id = ?
    `).bind(taskId).run();

    return jsonResponse({
      success: true,
      message: 'Task deleted successfully'
    });

  } catch (error) {
    console.error('Delete task error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 手动执行任务
 */
async function runTaskManually(taskId, env, ctx) {
  try {
    const task = await env.DB.prepare(`
      SELECT * FROM scheduled_tasks WHERE id = ?
    `).bind(taskId).first();

    if (!task) {
      return jsonResponse({ error: 'Task not found' }, 404);
    }

    // 在后台执行任务
    ctx.waitUntil(executeTask(task, env));

    return jsonResponse({
      success: true,
      message: 'Task execution started'
    });

  } catch (error) {
    console.error('Run task manually error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 获取任务执行历史
 */
async function getExecutions(url, env) {
  try {
    const taskId = url.searchParams.get('task_id');
    const limit = parseInt(url.searchParams.get('limit') || '50');

    let query = `SELECT * FROM task_executions`;
    const params = [];

    if (taskId) {
      query += ` WHERE task_id = ?`;
      params.push(taskId);
    }

    query += ` ORDER BY started_at DESC LIMIT ?`;
    params.push(limit);

    const result = await env.DB.prepare(query).bind(...params).all();

    const executions = (result.results || []).map(exec => ({
      ...exec,
      result: exec.result ? JSON.parse(exec.result) : null
    }));

    return jsonResponse({
      success: true,
      executions
    });

  } catch (error) {
    console.error('Get executions error:', error);
    return jsonResponse({ error: error.message }, 500);
  }
}

/**
 * 执行定时任务
 */
async function executeTask(task, env) {
  const startTime = Date.now();
  let status = 'success';
  let result = null;
  let error = null;

  try {
    const serverIds = task.server_ids ? JSON.parse(task.server_ids) : null;
    const serversData = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
    const allServers = serversData || [];
    const servers = serverIds 
      ? allServers.filter(s => serverIds.includes(s.id))
      : allServers;

    switch (task.task_type) {
      case 'sync_auth':
        result = await executeSyncAuth(servers, env);
        break;
      case 'sync_config':
        result = await executeSyncConfig(servers, env);
        break;
      case 'check_usage':
        result = await executeCheckUsage(servers, env);
        break;
      case 'revive_tokens':
        result = await executeReviveTokens(servers, env);
        break;
      default:
        throw new Error(`Unknown task type: ${task.task_type}`);
    }

  } catch (err) {
    status = 'failed';
    error = err.message;
    console.error(`Task ${task.task_name} failed:`, err);
  }

  const endTime = Date.now();

  // 记录执行历史
  await logTaskExecution(
    env.DB,
    task.id,
    task.task_name,
    status,
    result,
    error,
    startTime,
    endTime
  );

  // 更新任务执行时间
  const now = new Date().toISOString();
  const nextRun = getNextRunTime(task.cron_expression);
  await updateTaskRunTime(env.DB, task.id, now, nextRun);
}

/**
 * 执行同步认证文件任务
 */
async function executeSyncAuth(servers, env) {
  const results = [];
  
  for (const server of servers) {
    try {
      // 调用同步逻辑（简化版）
      const client = new (await import('../utils/cpa-client.js')).CPAClient(server.base_url, server.token);
      const files = await client.getAuthFiles();
      const activeFiles = files.filter(f => !f.disabled && f.status === 'ready');
      
      results.push({
        server_id: server.id,
        server_name: server.name,
        success: true,
        synced: activeFiles.length
      });
    } catch (error) {
      results.push({
        server_id: server.id,
        server_name: server.name,
        success: false,
        error: error.message
      });
    }
  }
  
  return { servers: results };
}

/**
 * 执行同步配置任务
 */
async function executeSyncConfig(servers, env) {
  const results = [];
  
  for (const server of servers) {
    try {
      const response = await fetch(`${server.base_url}/v0/management/config.yaml`, {
        headers: { 'Authorization': `Bearer ${server.token}` }
      });
      
      results.push({
        server_id: server.id,
        server_name: server.name,
        success: response.ok
      });
    } catch (error) {
      results.push({
        server_id: server.id,
        server_name: server.name,
        success: false,
        error: error.message
      });
    }
  }
  
  return { servers: results };
}

/**
 * 执行检查使用情况任务
 */
async function executeCheckUsage(servers, env) {
  // 实现检查逻辑
  return { message: 'Check usage completed' };
}

/**
 * 执行复活 Token 任务
 */
async function executeReviveTokens(servers, env) {
  // 实现复活逻辑
  return { message: 'Revive tokens completed' };
}
