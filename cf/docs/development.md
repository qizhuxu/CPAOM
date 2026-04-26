# 开发指南

本文档面向希望在本地开发、测试或贡献代码的开发者。

## 开发环境设置

### 前置要求

- Node.js 16.13.0+
- npm 或 yarn
- Git
- Cloudflare 账号（用于部署测试）

### 首次设置

```bash
# 1. 克隆项目
cd L/CPAD/cf

# 2. 安装依赖
npm install

# 3. 安装 Wrangler CLI（如果未安装）
npm install -g wrangler

# 4. 登录 Cloudflare
wrangler login

# 5. 创建本地环境变量文件
cat > .dev.vars << EOF
ADMIN_USERNAME=admin
ADMIN_PASSWORD=dev123
EOF

# 6. 创建 KV 命名空间（开发环境）
wrangler kv:namespace create "ACCOUNTS" --preview

# 7. 更新 wrangler.toml 中的 preview_id
```

### 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:8787`

## 项目结构

```
cf/
├── src/
│   ├── index.js              # Worker 主入口
│   ├── static.js             # 静态文件处理
│   ├── api/                  # API 层
│   │   ├── router.js         # 路由分发和认证中间件
│   │   ├── auth.js           # 认证 API
│   │   ├── servers.js        # 服务器管理
│   │   ├── accounts.js       # 账号管理
│   │   ├── operations.js     # 批量操作
│   │   └── stats.js          # 统计分析
│   ├── utils/                # 工具类
│   │   ├── cors.js           # CORS 配置
│   │   ├── cpa-client.js     # CPA API 客户端
│   │   └── oauth.js          # OAuth Token 刷新
│   └── frontend/             # 前端
│       └── index.html.js     # 单页应用（内嵌）
├── docs/                     # 文档
├── wrangler.toml             # Wrangler 配置
└── package.json              # 项目配置
```

### 关键文件说明

**src/index.js**
- Worker 主入口
- 处理所有传入请求
- 路由分发到 API 或静态文件

**src/api/router.js**
- API 路由分发
- 认证中间件
- 统一错误处理

**src/utils/cpa-client.js**
- CPA API 客户端封装
- 处理所有与 CPA 服务器的通信
- 包含错误处理和重试逻辑

**src/frontend/index.html.js**
- 完整的前端应用
- 内嵌在 Worker 中，无需构建步骤
- 纯 HTML/CSS/JavaScript

## 开发工作流

### 1. 添加新功能

#### 后端 API

```javascript
// 1. 在 src/api/ 创建新文件或修改现有文件
// src/api/new-feature.js
export async function handleNewFeature(request, env, ctx) {
  const url = new URL(request.url);
  
  if (request.method === 'GET') {
    // 实现 GET 逻辑
    return jsonResponse({ data: 'result' });
  }
  
  return jsonResponse({ error: 'Method not allowed' }, 405);
}

// 2. 在 src/api/router.js 注册路由
import { handleNewFeature } from './new-feature';

if (path.startsWith('/api/new-feature')) {
  return handleNewFeature(request, env, ctx);
}
```

#### 前端功能

```javascript
// 在 src/frontend/index.html.js 中添加
// 1. 添加 HTML 结构
<div id="new-feature">
  <button onclick="callNewFeature()">New Feature</button>
</div>

// 2. 添加 JavaScript 函数
async function callNewFeature() {
  const res = await fetch('/api/new-feature', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await res.json();
  console.log(data);
}
```

### 2. 测试

#### 本地测试

```bash
# 启动开发服务器
npm run dev

# 在另一个终端测试 API
curl http://localhost:8787/api/stats/overview \
  -H "Authorization: Bearer test-token"
```

#### 使用 Wrangler Tail 查看日志

```bash
# 在开发服务器运行时
wrangler tail --local
```

### 3. 调试

#### 使用 console.log

```javascript
export default {
  async fetch(request, env, ctx) {
    console.log('Request:', request.url);
    console.log('Method:', request.method);
    
    const response = await handleRequest(request, env);
    
    console.log('Response status:', response.status);
    return response;
  }
};
```

#### 查看日志

```bash
# 本地开发
wrangler tail --local

# 生产环境
wrangler tail
```

### 4. 部署测试

```bash
# 部署到开发环境
wrangler deploy --env dev

# 测试
curl https://cpa-manager-dev.your-subdomain.workers.dev/api/stats/overview
```

## 代码规范

### JavaScript 风格

- 使用 ES6+ 语法
- 使用 `async/await` 而非 Promise 链
- 使用 `const` 和 `let`，避免 `var`
- 函数命名使用驼峰命名法
- 常量使用大写下划线命名

```javascript
// ✅ Good
const API_BASE_URL = 'https://api.example.com';

async function getUserData(userId) {
  const response = await fetch(`${API_BASE_URL}/users/${userId}`);
  return await response.json();
}

// ❌ Bad
var apiUrl = 'https://api.example.com';

function get_user_data(userId) {
  return fetch(apiUrl + '/users/' + userId)
    .then(res => res.json());
}
```

### 错误处理

```javascript
// ✅ Good - 统一错误处理
export async function handleAPI(request, env, ctx) {
  try {
    const result = await processRequest(request, env);
    return jsonResponse(result);
  } catch (error) {
    console.error('API Error:', error);
    return jsonResponse(
      { error: error.message },
      error.status || 500
    );
  }
}

// ❌ Bad - 忽略错误
export async function handleAPI(request, env, ctx) {
  const result = await processRequest(request, env);
  return jsonResponse(result);
}
```

### 注释规范

```javascript
/**
 * 刷新 OAuth Token
 * 
 * @param {string} refreshToken - Refresh Token
 * @returns {Promise<Object>} 新的 Token 对象
 * @throws {Error} 刷新失败时抛出错误
 */
export async function refreshOAuthToken(refreshToken) {
  // 实现
}
```

## 测试策略

### 手动测试清单

部署前确保测试以下功能：

- [ ] 登录/登出
- [ ] 添加服务器
- [ ] 测试服务器连接
- [ ] 查看账号列表
- [ ] 启用/禁用账号
- [ ] 批量检查使用情况
- [ ] 下载打包
- [ ] 查看统计数据

### API 测试脚本

```bash
#!/bin/bash
# test-api.sh

BASE_URL="http://localhost:8787"

# 1. 登录
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"dev123"}' \
  | jq -r '.token')

echo "Token: $TOKEN"

# 2. 获取服务器列表
curl -s "$BASE_URL/api/servers" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'

# 3. 获取统计
curl -s "$BASE_URL/api/stats/overview" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

## 常见开发问题

### Q: 本地开发时 KV 数据丢失？

**A:** 本地开发使用内存 KV，重启后数据会丢失。使用 `--remote` 标志连接到远程 KV：

```bash
wrangler dev --remote
```

### Q: CORS 错误？

**A:** 检查 `src/utils/cors.js` 配置，确保允许你的来源：

```javascript
export const corsHeaders = {
  'Access-Control-Allow-Origin': '*', // 或指定域名
  ...
};
```

### Q: 如何调试 Worker 代码？

**A:** 使用 `console.log` 和 `wrangler tail`：

```bash
# 终端 1
npm run dev

# 终端 2
wrangler tail --local
```

### Q: 修改代码后没有生效？

**A:** Wrangler dev 支持热重载，但有时需要手动重启：

```bash
# Ctrl+C 停止
npm run dev
```

## 贡献指南

### 提交 Pull Request

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/new-feature`
3. 提交变更：`git commit -am 'Add new feature'`
4. 推送到分支：`git push origin feature/new-feature`
5. 创建 Pull Request

### Commit 消息规范

```
<type>: <subject>

<body>

<footer>
```

**Type:**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具变动

**示例:**
```
feat: 添加批量删除账号功能

- 添加 DELETE /api/accounts/batch 端点
- 前端添加批量选择和删除按钮
- 更新 API 文档

Closes #123
```

## 性能优化建议

### 1. 减少 KV 读取

```javascript
// ❌ Bad - 每次请求都读取
async function getServers(env) {
  return await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
}

// ✅ Good - 缓存在内存中（适用于不常变化的数据）
let serversCache = null;
let cacheTime = 0;

async function getServers(env) {
  const now = Date.now();
  if (!serversCache || now - cacheTime > 60000) {
    serversCache = await env.ACCOUNTS.get('cpa_servers', { type: 'json' });
    cacheTime = now;
  }
  return serversCache;
}
```

### 2. 并发请求

```javascript
// ❌ Bad - 串行请求
for (const file of files) {
  await processFile(file);
}

// ✅ Good - 并发请求
await Promise.all(files.map(file => processFile(file)));
```

### 3. 减少响应大小

```javascript
// ❌ Bad - 返回完整数据
return jsonResponse({ accounts: allAccounts });

// ✅ Good - 只返回必要字段
return jsonResponse({
  accounts: allAccounts.map(acc => ({
    id: acc.id,
    email: acc.email,
    status: acc.status
  }))
});
```

## 相关资源

- [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
- [Wrangler CLI 文档](https://developers.cloudflare.com/workers/wrangler/)
- [Workers KV 文档](https://developers.cloudflare.com/workers/runtime-apis/kv/)
- [Web API 标准](https://developer.mozilla.org/en-US/docs/Web/API)

## 下一步

- 查看 [API 参考](api.md) 了解所有端点
- 查看 [架构设计](architecture.md) 了解系统设计
- 查看 [部署指南](deployment.md) 了解生产部署
