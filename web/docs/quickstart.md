# 快速开始指南

## 方式 1：Docker 部署（推荐）⭐

### 使用预构建镜像

1. 确保已安装 Docker 和 Docker Compose

2. 拉取最新镜像：
```bash
cd CPAOM/web
docker pull ghcr.io/qizhuxu/cpaom/cpaom-web:latest
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问 http://localhost:5000

5. 使用默认账号登录：
   - 用户名: `admin`
   - 密码: `admin123`

6. 在仪表板中添加 CPA 服务器

### 本地构建镜像

如果需要自定义修改：

1. 编辑 `docker-compose.yml`，注释 `image` 行，取消注释 `build` 行

2. 构建并启动：
```bash
docker-compose up -d --build
```

## 方式 2：本地部署

### Windows

```bash
cd CPAOM\web
manage.bat setup
manage.bat start
```

### Linux/macOS

```bash
cd CPAOM/web
chmod +x manage.sh
./manage.sh setup
./manage.sh start
```

访问 http://localhost:5000

## 首次配置

1. 登录后，点击"添加服务器"

2. 填写 CPA 服务器信息：
   - 服务器名称: 自定义名称
   - Base URL: CPA 服务器地址
   - Token: 管理令牌（mgt-xxx）

3. 点击"测试连接"验证配置

4. 开始使用！

## 常见问题

**Q: 如何修改管理员密码？**  
A: 编辑 `.env` 文件，修改 `ADMIN_PASSWORD` 的值

**Q: 端口被占用怎么办？**  
A: 编辑 `.env` 文件，修改 `PORT` 的值

**Q: 如何停止服务？**  
A: Docker: `docker-compose down`  
   本地: 按 Ctrl+C

**Q: 数据存储在哪里？**  
A: `data/cpa_manager.db` 文件中

## 下一步

- 配置定时任务实现自动维护
- 设置 HTTPS 提高安全性
