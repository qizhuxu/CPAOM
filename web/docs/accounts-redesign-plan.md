# 账号管理界面重新设计方案

## 设计目标
支持300+账号的高效管理，提供快速筛选、批量操作和清晰的视觉反馈。

## 核心改进

### 1. 紧凑列表视图
- **行高**：40px（vs 当前的60px+）
- **信息密度**：每行显示核心信息
- **虚拟滚动**：只渲染可见区域（性能优化）

### 2. 强大筛选系统
```
[搜索框] [全部|活跃|禁用|离线] [使用率: <50%|50-80%|>80%|未检查] [排序▼]
```

### 3. 批量操作栏
选中账号后底部浮动显示：
```
已选 N 个  [批量下载] [批量启用] [批量禁用] [批量复活] [取消]
```

### 4. 列表项设计
```
[☐] [●] user@example.com                    [85.2%] [详情] [下载]
     ↑   ↑                                      ↑       ↑
   状态  邮箱（主要信息）                    使用率   快速操作
```

### 5. 快捷键支持
- `Cmd/Ctrl + K` - 命令面板
- `Cmd/Ctrl + F` - 搜索
- `Cmd/Ctrl + A` - 全选
- `Space` - 切换选中
- `R` - 刷新

## 技术实现

### 前端组件
- `AccountsManager.jsx` - 主组件
- `AccountsList.jsx` - 列表组件
- `FilterBar.jsx` - 筛选栏
- `BatchActions.jsx` - 批量操作栏
- `CommandPalette.jsx` - 命令面板

### 数据流
1. 从API加载账号列表
2. 前端内存筛选（300条数据很小）
3. 虚拟滚动渲染可见行
4. 批量操作使用Promise.all并发

### API需求
- `GET /api/accounts/<server_id>` - 获取账号列表（已有）
- `POST /api/accounts/<server_id>/batch-download` - 批量下载（新增）
- `POST /api/accounts/<server_id>/batch-toggle` - 批量启用/禁用（新增）
- `POST /api/accounts/<server_id>/batch-revive` - 批量复活（已有）

## 视觉设计

### 色彩系统（保持一致）
- 主色：#0A5F5F
- Accent：#D97706
- 成功：#059669（<50%使用率）
- 警告：#D97706（50-80%）
- 危险：#DC2626（>80%）

### 状态指示
- 在线：绿色脉动圆点
- 离线：灰色圆点
- 禁用：红色圆点

### 使用率徽章（120%细节）
```css
background: linear-gradient(135deg, color1, color2);
border-radius: 12px;
padding: 4px 10px;
font-family: var(--font-mono);
font-weight: 600;
```

## 实现计划

### Phase 1 - 核心列表（优先）
- [x] 设计方案
- [ ] 创建新模板文件
- [ ] 实现筛选栏
- [ ] 实现紧凑列表
- [ ] 实现搜索功能

### Phase 2 - 批量操作
- [ ] 多选功能
- [ ] 浮动操作栏
- [ ] 批量API

### Phase 3 - 增强功能
- [ ] 命令面板
- [ ] 快捷键
- [ ] 虚拟滚动
- [ ] 导出功能

## 下一步
创建新的模板文件并实现Phase 1功能。
