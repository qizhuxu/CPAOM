# 🚀 快速开始

5 分钟部署你的 CPA 账号管理系统到 Cloudflare！

## 📋 前置要求

- ✅ Node.js 16.13.0+
- ✅ Cloudflare 账号（免费）
- ✅ 一个或多个 CPA 服务器

## 🎯 三步部署

### 方法 1：自动化脚本（推荐）

#### Windows

```bash
cd L/CPAD/cf
setup.bat
```

#### Linux/macOS

```bash
cd L/CPAD/cf
chmod +x setup.sh
./setup.sh
```

脚本会自动完成：
1. ✅ 安装依赖
2. ✅ 登录 Cloudflare
3. ✅ 创建 KV 命名空间
4. ✅ 设置管理员凭证
5. ✅ 部署到生产环境

### 方法 2：手动部署

#### 步骤 1：安装和登录

```bash
cd L/CPAD/cf
npm install
wrangler login
```

#### 步骤 2：创建 KV 并配置

```bash
# 创建 KV
wrangler kv:namespace create "ACCOUNTS"

# 复制输出的 ID，更新 wrangler.toml
# 将 your-kv-namespace-id 替换为实际 ID
```

#### 步骤 3：设置凭证并部署

```bash
# 设置管理员凭证
wrangler secret put ADMIN_USERNAME  # 输入: admin
wrangler secret put ADMIN_PASSWORD  # 输入: your-password

# 部署
npm run deploy
```

## 🎉 完成！

部署成功后，你会看到：

```
✨ Success! Published cpa-manager
  https://cpa-manager.your-subdomain.workers.dev
```

## 🔧 首次使用

### 1. 登录系统

访问部署的 URL，使用设置的用户名和密码登录。

### 2. 添加 CPA 服务器

1. 点击 "服务器管理" 标签
2. 点击 "➕ 添加服务器"
3. 填写信息：
   ```
   服务器名称: 主服务器
   Base URL: https://your-cpa-server.com
   管理 Token: mgt-xxx
   ✅ 启用 Token 自动复活
   ```
4. 点击 "添加"
5. 点击 "测试连接" 验证

### 3. 查看账号

1. 点击 "账号管理" 标签
2. 选择服务器
3. 查看所有账号列表

### 4. 批量操作

1. 点击 "批量操作" 标签
2. 选择服务器
3. 执行操作：
   - **检查使用情况**：查看所有账号状态
   - **下载打包**：备份所有活跃账号
   - **批量上传**：导入账号文件

## 📊 功能概览

| 功能 | 说明 |
|------|------|
| 🖥️ Web 界面 | 现代化响应式 UI |
| 🔐 安全认证 | Token 身份验证 |
| 🌐 多服务器 | 管理多个 CPA 服务器 |
| 📊 实时统计 | 账号状态监控 |
| 🔄 Token 复活 | 自动刷新过期 Token |
| 📦 批量操作 | 批量检查/下载/上传 |
| ⚡ 边缘计算 | 全球 CDN 加速 |
| 💾 KV 存储 | 配置和会话存储 |

## 🔒 安全建议

1. **立即修改密码**
   ```bash
   wrangler secret put ADMIN_PASSWORD
   ```

2. **使用强密码**
   - 至少 12 位
   - 包含大小写字母、数字、特殊字符

3. **限制访问**（可选）
   - 使用 Cloudflare Access
   - 配置 IP 白名单

4. **定期备份**
   ```bash
   wrangler kv:key get --binding=ACCOUNTS "cpa_servers" > backup.json
   ```

## 🐛 常见问题

### Q: 登录失败？

**A:** 检查是否正确设置了 Secret：
```bash
wrangler secret list
```

### Q: 服务器连接失败？

**A:** 确认：
- CPA 服务器 URL 正确
- 管理 Token 有效
- CPA 服务器允许远程管理

### Q: KV 错误？

**A:** 确认：
- KV 命名空间已创建
- `wrangler.toml` 中的 ID 正确
- 重新部署：`npm run deploy`

### Q: 如何查看日志？

**A:** 
```bash
npm run tail
```

## 📚 更多资源

- 📖 [完整文档](README.md)
- 🚀 [部署指南](DEPLOY.md)
- 🔧 [API 文档](README.md#-api-文档)
- 💬 [提交 Issue](https://github.com/your-repo/issues)

## 🎯 下一步

- [ ] 配置自定义域名
- [ ] 添加更多 CPA 服务器
- [ ] 设置定时任务（自动检查）
- [ ] 启用 Cloudflare Access
- [ ] 配置监控告警

## 💡 提示

- 免费套餐支持 100,000 请求/天
- 适合管理 100+ 账号
- 全球边缘节点，访问速度快
- 无需服务器，零运维成本

---

**开始使用吧！** 🚀

有问题？查看 [完整文档](README.md) 或 [提交 Issue](https://github.com/your-repo/issues)
