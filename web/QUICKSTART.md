# 快速开始指南

## Docker 部署（最简单）

1. 确保已安装 Docker 和 Docker Compose

2. 启动服务：
```bash
cd CPAOM/web
docker-compose up -d
```

3. 访问 http://localhost:5000

4. 使用默认账号登录：
   - 用户名: `admin`
   - 密码: `admin123`

5. 在仪表板中添加 CPA 服务器

## Windows 本地部署

1. 确保已安装 Python 3.8+

2. 运行安装脚本：
```bash
cd CPAOM\web
setup.bat
```

3. 启动服务：
```bash
run.bat
```

4. 访问 http://localhost:5000

## Linux/macOS 本地部署

1. 确保已安装 Python 3.8+

2. 运行安装脚本：
```bash
cd CPAOM/web
chmod +x setup.sh run.sh
./setup.sh
```

3. 启动服务：
```bash
./run.sh
```

4. 访问 http://localhost:5000

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

- 查看 [README.md](README.md) 了解完整功能
- 配置定时任务实现自动维护
- 设置 HTTPS 提高安全性
