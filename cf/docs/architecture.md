# 架构设计

本文档说明系统的技术架构、设计决策和实现细节。

## 为什么选择 Cloudflare Workers？

### 技术决策

我们选择 Cloudflare Workers 而非传统服务器部署，原因如下：

1. **零运维成本**
   - 无需管理服务器
   - 自动扩展和负载均衡
   - 全球 CDN 自动分发

2. **边缘计算优势**
   - 请求在离用户最近的节点处理
   - 平均响应时间 <50ms
   - 全球 200+ 数据中心

3. **成本效益**
   - 免费套餐：100,000 请求/天
   - 付费套餐：$5/月 = 10M 请求/月
   - 比传统 VPS 便宜 70%+

4. **开发体验**
   - 标准 Web API
   - 本地开发环境
   - 一键部署

### 替代方案对比

| 方案 | 优点 | 缺点 | 成本 |
|------|------|------|------|
| **Cloudflare Workers** | 零运维、全球分布、自动扩展 | CPU 时间限制 | $0-5/月 |
| VPS (Nginx + Node.js) | 完全控制、无限制 | 需要运维、单点故障 | $5-20/月 |
| AWS Lambda | 成熟生态、灵活 | 冷启动、复杂配置 | $10-50/月 |
| Vercel/Netlify | 简单易用 | 功能限制、价格高 | $20+/月 |

**结论**：对于 CPA 管理系统，Cloudflare Workers 提供最佳的性价比和用户体验。

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────┐
│                   用户浏览器                      │
│            (HTML/CSS/JavaScript)                │
└────────────────┬────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────┐
│          Cloudflare Edge Network                │
│         (全球 200+ 数据中心)                      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│            Cloudflare Worker                    │
│  ┌──────────────────────────────────────────┐  │
│  │  src/index.js (主入口)                    │  │
│  │    ├─ API 路由 (/api/*)                  │  │
│  │    └─ 静态文件 (/)                        │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  API 层                                   │  │
│  │    ├─ auth.js (认证)                     │  │
│  │    ├─ servers.js (服务器管理)            │  │
│  │    ├─ accounts.js (账号管理)             │  │
│  │    ├─ operations.js (批量操作)           │  │
│  │    └─ stats.js (统计)                    │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  工具层                                   │  │
│  │    ├─ cpa-client.js (CPA API 客户端)     │  │
│  │    ├─ oauth.js (Token 刷新)              │  │
│  │    └─ cors.js (CORS 配置)                │  │
│  └──────────────────────────────────────────┘  │
└────────┬───────────────────────┬────────────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Cloudflare KV    │    │  CPA 服务器       │
│  (配置存储)       │    │  (账号数据)       │
│                  │    │                  │
│ - cpa_servers    │    │ - 认证文件        │
│ - session:*      │    │ - 使用统计        │
│ - pack:*         │    │ - API 调用        │
└──────────────────┘    └──────────────────┘
```

### 数据流示例

**用户登录流程：**
```
1. 用户输入用户名密码
   ↓
2. POST /api/auth/login
   ↓
3. Worker 验证凭证（env.ADMIN_USERNAME/PASSWORD）
   ↓
4. 生成 UUID Token
   ↓
5. 存储到 KV: session:{token} (24h TTL)
   ↓
6. 返回 Token 给前端
   ↓
7. 前端存储到 localStorage
   ↓
8. 后续请求携带 Token
```

**批量检查账号流程：**
```
1. 用户选择服务器，点击"检查使用情况"
   ↓
2. POST /api/operations/check-usage
   ↓
3. Worker 从 KV 获取服务器配置
   ↓
4. 调用 CPA API 获取账号列表
   ↓
5. 并发检查每个账号（Promise.all）
   ↓
6. 对于 401 错误，标记需要复活
   ↓
7. 返回汇总结果给前端
   ↓
8. 前端显示统计和详情
```

## 📁 项目结构

```
L/CPAD/cf/
├── src/                          # 源代码
│   ├── index.js                  # Worker 主入口
│   ├── static.js                 # 静态文件处理
│   ├── api/                      # API 层
│   │   ├── router.js             # 路由分发和认证
│   │   ├── auth.js               # 认证 API（登录/登出）
│   │   ├── servers.js            # 服务器管理 API
│   │   ├── accounts.js           # 账号管理 API
│   │   ├── operations.js         # 批量操作 API
│   │   └── stats.js              # 统计 API
│   ├── utils/                    # 工具类
│   │   ├── cors.js               # CORS 配置
│   │   ├── cpa-client.js         # CPA 客户端封装
│   │   └── oauth.js              # OAuth Token 刷新
│   └── frontend/                 # 前端
│       └── index.html.js         # 单页应用（内嵌）
├── wrangler.toml                 # Wrangler 配置
├── package.json                  # 依赖配置
├── README.md                     # 完整文档
├── DEPLOY.md                     # 部署指南
├── QUICKSTART.md                 # 快速开始
├── setup.sh                      # Linux/macOS 部署脚本
├── setup.bat                     # Windows 部署脚本
└── .gitignore                    # Git 忽略文件
```

## 🏗️ 技术架构

### 前端

- **纯 HTML/CSS/JavaScript**
  - 无构建步骤
  - 内嵌在 Worker 中
  - 响应式设计
  - 现代化 UI

### 后端

- **Cloudflare Workers**
  - 边缘计算
  - 全球分布
  - 自动扩展
  - 零运维

### 存储

- **Cloudflare KV**
  - 服务器配置
  - 用户会话
  - 临时数据

### API 设计

- **RESTful API**
  - 标准 HTTP 方法
  - JSON 数据格式
  - Token 认证
  - CORS 支持

## 🔄 数据流

### 1. 用户登录

```
用户 → POST /api/auth/login
     → 验证凭证
     → 生成 Token
     → 存储到 KV (session:token)
     → 返回 Token
```

### 2. 添加服务器

```
用户 → POST /api/servers
     → 验证 Token
     → 测试连接
     → 存储到 KV (cpa_servers)
     → 返回成功
```

### 3. 查看账号

```
用户 → GET /api/accounts?server_id=xxx
     → 验证 Token
     → 从 KV 获取服务器配置
     → 调用 CPA API
     → 返回账号列表
```

### 4. Token 复活

```
用户 → POST /api/operations/revive-tokens
     → 验证 Token
     → 下载认证文件
     → 调用 OAuth API 刷新
     → 上传更新后的文件
     → 验证新 Token
     → 返回结果
```

## 🔐 安全机制

### 认证流程

1. **登录**
   - 用户名密码验证
   - 生成随机 UUID Token
   - 存储到 KV（24小时过期）

2. **请求验证**
   - 检查 Authorization Header
   - 从 KV 验证 Token
   - 检查过期时间

3. **登出**
   - 删除 KV 中的 Session

### 数据保护

- **Secret 存储**：敏感信息使用 Wrangler Secret
- **HTTPS Only**：强制 HTTPS 访问
- **CORS 限制**：可配置允许的来源
- **Token 过期**：会话自动过期

## 📊 性能优化

### 1. 边缘缓存

- 静态资源缓存在边缘节点
- KV 数据全球分布
- 就近访问，低延迟

### 2. 并发处理

- 批量操作使用并发请求
- Promise.all 并行处理
- 提高吞吐量

### 3. 数据压缩

- JSON 数据自动压缩
- 减少传输大小
- 加快响应速度

## 🔧 扩展性

### 添加新功能

1. **新增 API 端点**
   ```javascript
   // src/api/new-feature.js
   export async function handleNewFeature(request, env, ctx) {
     // 实现逻辑
   }
   
   // src/api/router.js
   if (path.startsWith('/api/new-feature')) {
     return handleNewFeature(request, env, ctx);
   }
   ```

2. **新增前端页面**
   ```javascript
   // src/frontend/index.html.js
   // 添加新的 tab 和功能
   ```

3. **新增工具类**
   ```javascript
   // src/utils/new-util.js
   export function newUtility() {
     // 实现逻辑
   }
   ```

### 集成其他服务

- **D1 数据库**：存储操作日志
- **R2 存储**：存储大文件
- **Durable Objects**：实时通信
- **Queues**：异步任务处理

## 📈 监控指标

### 关键指标

- **请求数**：每日/每月请求量
- **错误率**：4xx/5xx 错误比例
- **响应时间**：P50/P95/P99
- **KV 操作**：读写次数

### 查看方式

1. **Cloudflare Dashboard**
   - Workers & Pages
   - Analytics 标签
   - 实时图表

2. **Wrangler CLI**
   ```bash
   npm run tail
   ```

3. **日志分析**
   - 错误日志
   - 访问日志
   - 性能日志

## 🧪 测试

### 本地测试

```bash
# 启动开发服务器
npm run dev

# 测试 API
curl http://localhost:8787/api/stats/overview \
  -H "Authorization: Bearer test-token"
```

### 集成测试

```bash
# 部署到测试环境
wrangler deploy --env dev

# 运行测试脚本
node test/integration.js
```

## 🚀 部署流程

### 开发环境

```bash
npm run dev          # 本地开发
wrangler tail        # 查看日志
```

### 测试环境

```bash
wrangler deploy --env dev
```

### 生产环境

```bash
npm run deploy       # 部署到生产
wrangler tail        # 监控日志
```

## 💰 成本分析

### 免费套餐

- ✅ 100,000 请求/天
- ✅ 1GB KV 存储
- ✅ 1,000 KV 写入/天
- ✅ 100,000 KV 读取/天

**适用场景**：
- 个人使用
- 小团队（<10人）
- 账号数 <100

### 付费套餐（$5/月）

- ✅ 10,000,000 请求/月
- ✅ 无限 KV 存储
- ✅ 无限 KV 操作

**适用场景**：
- 中大型团队
- 账号数 >100
- 高频操作

### 预估成本

| 使用场景 | 账号数 | 请求/天 | 月成本 |
|---------|--------|---------|--------|
| 个人 | <50 | <1,000 | $0 |
| 小团队 | 50-100 | 1,000-10,000 | $0 |
| 中型团队 | 100-500 | 10,000-50,000 | $5 |
| 大型团队 | >500 | >50,000 | $5+ |

## 🔄 维护计划

### 日常维护

- [ ] 监控错误日志
- [ ] 检查性能指标
- [ ] 备份 KV 数据

### 每周维护

- [ ] 更新依赖包
- [ ] 检查安全漏洞
- [ ] 优化性能

### 每月维护

- [ ] 审查访问日志
- [ ] 更新文档
- [ ] 收集用户反馈

## 📝 开发规范

### 代码风格

- 使用 ES6+ 语法
- 异步操作使用 async/await
- 错误处理使用 try-catch
- 函数命名清晰明确

### 注释规范

```javascript
/**
 * 函数说明
 * @param {Type} param - 参数说明
 * @returns {Type} 返回值说明
 */
function example(param) {
  // 实现
}
```

### Git 提交

```bash
# 格式：<type>: <subject>
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
style: 代码格式
refactor: 重构代码
test: 添加测试
chore: 构建/工具变动
```

## 🎯 路线图

### v1.0（当前）

- ✅ Web 管理界面
- ✅ 服务器管理
- ✅ 账号管理
- ✅ 批量操作
- ✅ Token 复活
- ✅ 统计分析

### v1.1（计划中）

- [ ] 定时任务（自动检查）
- [ ] WebSocket 实时更新
- [ ] 操作日志（D1）
- [ ] 文件上传（R2）
- [ ] 邮件通知

### v2.0（未来）

- [ ] 多用户支持
- [ ] 权限管理
- [ ] API 限流
- [ ] 高级统计
- [ ] 移动端适配

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

---

**项目维护者**：[Your Name]  
**最后更新**：2026-04-25  
**版本**：v1.0.0
