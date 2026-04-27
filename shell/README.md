# CPA 工具集 - Shell 版

Python 命令行工具，支持批量操作和多服务器管理。

## 快速开始

```bash
cd CPAOM/shell
python manage_accounts.py
```

## 主要功能

1. **检查账号使用情况** - 自动复活失效 Token
2. **批量下载** - 打包为 ZIP（跳过禁用账号）
3. **批量上传** - 支持目录和 ZIP 文件
4. **下载配置文件** - 备份 config.yaml
5. **管理 OpenAI 提供商** - 添加/更新/删除兼容提供商
6. **查看服务器列表** - 多服务器管理

## 配置文件

**config.json** - 支持单服务器或多服务器：

```json
{
  "cpa_servers": [
    {
      "name": "主服务器",
      "base_url": "https://cpa1.example.com",
      "token": "mgt-token1",
      "enable_token_revive": true
    }
  ]
}
```

## Token 复活机制

```
检测 401 错误 → 用 refresh_token 刷新（最多3次）
成功 → 更新并上传文件 ✅
失败 → 自动禁用账号 🚫
```

## 批量上传

支持三种方式：
1. 从 `pool/` 目录上传所有 JSON
2. 从 ZIP 文件解压并上传
3. 指定自定义目录路径

## OpenAI 兼容提供商

管理 OpenRouter、DeepSeek 等兼容提供商：
- 查看提供商列表
- 添加新提供商（Base URL + API Key）
- 更新/删除提供商配置

**常见提供商示例：**
- OpenRouter: `https://openrouter.ai/api/v1`
- DeepSeek: `https://api.deepseek.com/v1`
- SiliconFlow: `https://api.siliconflow.cn/v1`

## 常见问题

**Q: 下载的文件保存在哪？**  
A: `pool/` 目录，格式 `YYYYMMDD-count.zip`

**Q: 如何重新启用被禁用的账号？**  
A: 通过 CPA 管理界面或 API 手动启用

**Q: 上传会覆盖已存在的账号吗？**  
A: 是的，同名文件会被覆盖

## 更新日志

**v1.2.0** (2026-04-21)
- ✅ 新增下载 config.yaml 功能
- ✅ 新增 OpenAI 兼容提供商管理

**v1.1.0** (2026-04-21)
- ✅ 修复上传接口路径
- ✅ 新增批量上传功能

**v1.0.0**
- ✅ 初始版本

## 许可证

MIT License
