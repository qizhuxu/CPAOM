# 新增功能说明

## 更新内容 (2026-04-21)

### 1. 下载 config.yaml 配置文件 📥

**菜单选项**: 4. 下载 config.yaml 配置文件

**功能**:
- 从 CPA 服务器下载完整的 YAML 配置文件
- 保留原始格式和注释
- 支持多服务器批量下载
- 自动命名：`config_服务器名称.yaml`

**使用场景**:
- 备份 CPA 服务器配置
- 在多个服务器间同步配置
- 查看当前运行时配置
- 配置迁移和版本管理

**示例**:
```
选择功能: 4
选择服务器: 1
✅ 下载成功: config_主服务器.yaml (12.34 KB)
```

---

### 2. OpenAI 兼容提供商管理 🔧

**菜单选项**: 5. 管理 OpenAI 兼容提供商

**功能**:
- 查看已配置的 OpenAI 兼容提供商列表
- 添加新的兼容提供商（如 OpenRouter、DeepSeek 等）
- 更新现有提供商配置
- 删除不需要的提供商

**子菜单**:
```
1. 查看提供商列表
2. 添加提供商
3. 更新提供商
4. 删除提供商
0. 返回主菜单
```

#### 2.1 查看提供商列表

显示所有已配置的提供商及其详细信息：
- 提供商名称
- Base URL
- API Keys 数量
- 模型映射数量
- 自定义 Headers

**示例输出**:
```
✅ 找到 2 个提供商:

1. openrouter
   Base URL: https://openrouter.ai/api/v1
   API Keys: 1 个
   Models: 3 个
     - kimi-k2
     - claude-sonnet
     - gpt-4o
   Headers: 1 个

2. deepseek
   Base URL: https://api.deepseek.com/v1
   API Keys: 2 个
```

#### 2.2 添加提供商

交互式添加新的 OpenAI 兼容提供商。

**输入项**:
- 提供商名称（必填）
- Base URL（必填）
- API Key（必填）
- Proxy URL（可选）
- 模型映射（可选）

**示例流程**:
```
提供商名称: openrouter
Base URL: https://openrouter.ai/api/v1
API Key: sk-or-v1-xxxxx
Proxy URL: (直接回车跳过)
是否添加模型映射? (y/n): y
  模型名称: anthropic/claude-3.5-sonnet
  模型别名: claude-sonnet
  模型名称: (直接回车结束)

✅ 添加成功
```

#### 2.3 更新提供商

更新现有提供商的配置（目前支持更新 Base URL）。

**示例**:
```
现有提供商:
  1. openrouter
  2. deepseek

选择要更新的提供商: 1
更新提供商: openrouter
Base URL [https://openrouter.ai/api/v1]: https://openrouter.ai/api/v2

✅ 更新成功
```

#### 2.4 删除提供商

删除不再需要的提供商配置。

**示例**:
```
现有提供商:
  1. openrouter
  2. deepseek

选择要删除的提供商: 2
确认删除 'deepseek'? (y/n): y

✅ 删除成功
```

---

## 技术实现

### CPAManager 类新增方法

```python
# 下载配置文件
def download_config_yaml(self, output_path: str) -> Tuple[bool, str]

# OpenAI 兼容提供商管理
def get_openai_compatibility(self) -> Tuple[bool, list]
def add_openai_compatibility(self, provider: Dict) -> Tuple[bool, str]
def update_openai_compatibility(self, name: str, provider: Dict) -> Tuple[bool, str]
def delete_openai_compatibility(self, name: str) -> Tuple[bool, str]
```

### API 端点

**下载配置**:
```
GET /v0/management/config.yaml
```

**OpenAI 兼容提供商**:
```
GET    /v0/management/openai-compatibility  # 获取列表
PUT    /v0/management/openai-compatibility  # 完整替换
PATCH  /v0/management/openai-compatibility  # 更新单个
DELETE /v0/management/openai-compatibility  # 删除单个
```

---

## 使用建议

### 配置备份流程

1. 定期下载 config.yaml 备份
2. 使用版本控制管理配置文件
3. 在修改配置前先备份

```bash
# 建议的备份命名
config_主服务器_20260421.yaml
config_备用服务器1_20260421.yaml
```

### OpenAI 兼容提供商配置

**常见提供商配置示例**:

**OpenRouter**:
```
名称: openrouter
Base URL: https://openrouter.ai/api/v1
API Key: sk-or-v1-xxxxx
```

**DeepSeek**:
```
名称: deepseek
Base URL: https://api.deepseek.com/v1
API Key: sk-xxxxx
```

**SiliconFlow**:
```
名称: siliconflow
Base URL: https://api.siliconflow.cn/v1
API Key: sk-xxxxx
```

---

## 注意事项

1. **单服务器操作**: OpenAI 兼容提供商管理只能选择单个服务器
2. **配置持久化**: 所有修改会自动写入 YAML 配置文件并热重载
3. **API Key 安全**: 添加的 API Key 会明文存储在配置文件中，注意保护
4. **Base URL 验证**: 确保 Base URL 格式正确（以 http:// 或 https:// 开头）
5. **模型映射**: 模型别名用于简化模型名称，可选配置

---

## 更新日志

### v1.2.0 (2026-04-21)
- ✅ 新增下载 config.yaml 功能
- ✅ 新增 OpenAI 兼容提供商管理功能
  - 查看提供商列表
  - 添加新提供商
  - 更新提供商配置
  - 删除提供商
- 📊 优化菜单结构
- 🔧 改进交互式配置流程

### v1.1.0 (2026-04-21)
- ✅ 修复上传接口路径
- 🆕 新增批量上传功能
- 🆕 支持多 CPA 服务器
- 📊 上传统计显示

### v1.0.0
- 初始版本
- 批量检查账号使用情况
- 自动 Token 复活
- 批量下载并打包
- 多 CPA 服务器管理
