# CPA 工具集

## 工具列表

### 1. manage_accounts.py - 账号管理工具（推荐）⭐
**功能：**
- ✅ 批量检查账号使用情况
- 🔄 自动复活失效的 Token（检测到 401 时）
- 🚫 自动禁用复活失败的账号（3次尝试后）
- 📦 批量下载并打包认证文件（跳过禁用账号）
- � 批量上传认证文件（支持目录和 ZIP）
- �🖥️  交互式菜单界面
- 🌐 支持多 CPA 服务器管理
- 📊 显示详细统计报告

**使用：**
```bash
python manage_accounts.py
```

**交互式菜单：**
```
功能菜单:
  1. 检查账号使用情况（自动复活 Token）
  2. 下载并打包认证文件（跳过禁用）
  3. 批量上传认证文件
  4. 查看 CPA 服务器列表
  0. 退出
```

**配置：** `config.json`

**格式1 - 单个 CPA（兼容旧版）:**
```json
{
  "base_url": "https://your-cpa-server.com",
  "token": "your-management-token",
  "enable_token_revive": true
}
```

**格式2 - 多个 CPA（推荐）:**
```json
{
  "cpa_servers": [
    {
      "name": "主服务器",
      "base_url": "https://cpa1.example.com",
      "token": "token1",
      "enable_token_revive": true
    },
    {
      "name": "备用服务器",
      "base_url": "https://cpa2.example.com",
      "token": "token2",
      "enable_token_revive": false
    }
  ]
}
```

---

### 2. cpa_downloader.py - 批量下载工具（独立版）
**功能：**
- 批量下载所有认证文件
- 自动打包为 ZIP（按日期命名）
- 并发下载（默认10线程）
- **注意：** 不会跳过禁用账号，下载所有文件

**使用：**
```bash
python cpa_downloader.py
```

**推荐：** 使用 `manage_accounts.py` 的下载功能，可以自动跳过禁用账号。

---

### 3. check_error_accounts.py - 错误账号分析
**功能：**
- 查看处于 error 状态的账号
- 分析错误原因和恢复时间
- 按错误类型分组统计

**使用：**
```bash
python check_error_accounts.py
```

---

### 4. test_token_revive.py - Token 刷新测试
**功能：**
- 测试单个 refresh_token 是否有效
- 验证 Token 刷新功能

**使用：**
```bash
python test_token_revive.py "your-refresh-token"
```

---

## 工作流程

### 多 CPA 管理

`manage_accounts.py` 支持同时管理多个 CPA 服务器：

1. **配置多个服务器**：在 `config.json` 中添加多个 CPA 配置
2. **选择服务器**：执行操作时可以选择单个、多个或全部服务器
3. **批量操作**：一次性检查、下载或上传多个 CPA 的账号

**示例流程：**
```
1. 启动程序 → 显示主菜单
2. 选择功能 → 选择要操作的 CPA 服务器
3. 执行操作 → 依次处理选中的服务器
4. 查看结果 → 返回主菜单
```

### 批量上传功能 🆕

**支持的上传方式：**
1. **从目录上传**：上传指定目录中的所有 JSON 文件
2. **从 ZIP 上传**：自动解压 ZIP 并上传其中的 JSON 文件
3. **自定义路径**：指定任意目录路径进行上传

**特点：**
- 并发上传（10线程）
- 自动验证 JSON 格式
- 实时显示上传进度
- 详细的成功/失败统计
- 支持从 `pool/` 目录选择 ZIP 文件

**使用场景：**
- 从备份恢复账号
- 在多个 CPA 服务器间同步账号
- 批量导入新注册的账号
- 从其他工具迁移账号数据

**流程：**
```
1. 选择上传方式（目录/ZIP/自定义）
2. 选择目标 CPA 服务器
3. 并发上传所有 JSON 文件
4. 显示上传统计（成功/失败）
```

**示例：**
```bash
# 从 pool 目录上传
选择: 1 → 从目录上传 → 使用默认 pool 目录

# 从 ZIP 文件上传
选择: 2 → 从 ZIP 文件上传 → 选择 pool/20260421-150.zip

# 从自定义目录上传
选择: 3 → 自定义目录路径 → 输入 /path/to/accounts
```

### 下载打包功能

**特点：**
- 自动跳过已禁用的账号
- 并发下载（10线程）
- 自动打包为 ZIP 文件
- 文件命名：`YYYYMMDD-count.zip`（日期-文件数）
- 保存位置：`pool/` 目录

**流程：**
```
1. 获取文件列表
2. 过滤禁用账号
3. 并发下载活跃账号
4. 打包为 ZIP
5. 清理临时文件
```

### Token 复活机制

```
检测到 401 错误
    ↓
尝试用 refresh_token 刷新（最多3次）
    ↓
成功 → 更新文件 → 上传到 CPA → 继续使用 ✅
失败 → 禁用账号 🚫
```

**重要更新：** Token 复活功能已修复上传接口路径，现在使用官方 API：
- ✅ 正确路径：`POST /v0/management/auth-files`
- ❌ 旧路径：`POST /v0/management/auth-files/upload`（已修复）

### 禁用账号处理

**禁用方式：**
- 使用 CPA API 的 `/v0/management/auth-files/status` 接口
- PATCH 请求，设置 `{"disabled": true}`

**后续处理：**
- 已禁用的账号会被自动跳过，不再检查
- 可以手动重新启用后再次尝试复活

**启用账号：**
```python
# 使用 manage_accounts.py 中的 enable_auth_file 方法
# 或通过 CPA 管理界面手动启用
```

---

## 配置文件

### config.json

**单个 CPA（兼容旧版）：**
```json
{
  "base_url": "https://your-cpa-server.com",
  "token": "mgt-xxx",
  "enable_token_revive": true
}
```

**多个 CPA（推荐）：**
```json
{
  "cpa_servers": [
    {
      "name": "主服务器",
      "base_url": "https://cpa1.example.com",
      "token": "mgt-token1",
      "enable_token_revive": true
    },
    {
      "name": "备用服务器",
      "base_url": "https://cpa2.example.com",
      "token": "mgt-token2",
      "enable_token_revive": false
    }
  ]
}
```

**参数说明：**
- `name`: 服务器名称（仅多 CPA 模式）
- `base_url`: CPA 服务器地址
- `token`: 管理 Token
- `enable_token_revive`: 是否开启 Token 复活（默认 true）

---

## 常见问题

### Q: 如何管理多个 CPA 服务器？
A: 在 `config.json` 中使用 `cpa_servers` 数组格式，添加多个服务器配置。运行 `manage_accounts.py` 时可以选择要操作的服务器。

### Q: 如何批量上传账号？
A: 使用 `manage_accounts.py` 的功能 3（批量上传认证文件），支持三种方式：
1. 从 `pool/` 目录上传所有 JSON 文件
2. 从 ZIP 文件解压并上传
3. 指定自定义目录路径上传

### Q: 上传功能支持什么格式？
A: 只支持 `.json` 格式的认证文件。文件必须是有效的 JSON 格式，包含完整的认证信息（access_token、refresh_token 等）。

### Q: 可以在多个 CPA 服务器间同步账号吗？
A: 可以！流程如下：
1. 从服务器 A 下载账号（功能 2）
2. 选择服务器 B 上传账号（功能 3）
3. 选择刚才下载的 ZIP 文件上传

### Q: 下载功能会下载禁用的账号吗？
A: 不会。`manage_accounts.py` 的下载功能会自动跳过已禁用的账号，只下载活跃账号。如果需要下载所有文件（包括禁用），请使用 `cpa_downloader.py`。

### Q: 为什么有些账号被跳过？
A: 这些账号已被禁用（disabled=true），通常是因为：
- Token 复活失败（3次尝试）
- 手动禁用
- 账号被封禁

### Q: 如何重新启用被禁用的账号？
A: 两种方式：
1. 通过 CPA 管理界面手动启用
2. 使用 API：`PATCH /v0/management/auth-files/status` 设置 `{"disabled": false}`

### Q: Token 复活成功率低怎么办？
A: 可能原因：
- Refresh Token 已过期（通常几个月有效期）
- 账号密码被修改
- 账号被封禁
- 网络问题

### Q: 下载的文件保存在哪里？
A: 打包后的 ZIP 文件保存在 `pool/` 目录，文件名格式为 `YYYYMMDD-count.zip`（例如：`20260419-153.zip` 表示 2026年4月19日下载的153个文件）。

### Q: 禁用的账号会被删除吗？
A: 不会。禁用只是标记为不可用，文件仍然保留在 CPA 服务器上。

### Q: 上传会覆盖已存在的账号吗？
A: 是的。如果上传的文件名与服务器上已有文件同名，会覆盖原文件。建议上传前先备份。

---

## 最佳实践

1. **定期运行**：建议每小时运行一次 `manage_accounts.py` 检查功能
2. **监控成功率**：关注 Token 复活成功率，低于 50% 需要检查
3. **及时清理**：定期清理长期禁用的账号
4. **备份数据**：定期使用下载功能备份认证文件到 `pool/` 目录
5. **多 CPA 管理**：使用多 CPA 配置分散风险，避免单点故障
6. **选择性操作**：根据需要选择特定的 CPA 服务器进行操作，提高效率
7. **账号同步**：使用下载+上传功能在多个 CPA 服务器间同步账号
8. **批量导入**：新注册的账号可以批量放入 `pool/` 目录，然后使用上传功能导入

---

## 更新日志

### v1.1.0 (2026-04-21)
- ✅ 修复上传接口路径（使用官方 API）
- 🆕 新增批量上传功能（支持目录和 ZIP）
- 🆕 支持从 `pool/` 目录选择 ZIP 文件上传
- 🆕 上传功能支持多 CPA 服务器
- 📊 上传完成后显示详细统计
- 🧹 自动清理上传临时文件

### v1.0.0
- 初始版本
- 支持批量检查账号使用情况
- 支持自动 Token 复活
- 支持批量下载并打包
- 支持多 CPA 服务器管理
