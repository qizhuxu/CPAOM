# 部署指南

CPA 账号管理系统 Web 版的生产环境部署指南。

## 部署方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Docker Compose | 简单快速，一键部署 | 单机限制 | 个人/小团队 |
| 本地部署 | 完全控制，易调试 | 环境依赖多 | 开发测试 |
| Kubernetes | 高可用，自动扩缩容 | 复杂度高 | 企业生产 |
| 云服务 | 托管服务，免运维 | 成本较高 | 快速上线 |

## Docker 部署（推荐）

### 使用预构建镜像

最简单的部署方式，使用 GitHub Container Registry 的预构建镜像：

```bash
# 1. 下载配置文件
wget https://raw.githubusercontent.com/qizhuxu/CPAOM/main/web/docker-compose.yml
wget https://raw.githubusercontent.com/qizhuxu/CPAOM/main/web/.env.example

# 2. 配置环境变量
cp .env.example .env
nano .env

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

### 自定义构建

如果需要修改代码：

```bash
# 1. 克隆仓库
git clone https://github.com/qizhuxu/CPAOM.git
cd CPAOM/web

# 2. 修改 docker-compose.yml
# 注释 image 行，取消注释 build 行

# 3. 构建并启动
docker-compose up -d --build
```

### Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  cpaom-web:
    # 使用预构建镜像
    image: ghcr.io/qizhuxu/cpaom/cpaom-web:latest
    
    # 或本地构建
    # build: .
    
    ports:
      - "5000:5000"
    
    volumes:
      - ./data:/app/data          # 数据持久化
      - ./config.json:/app/config.json  # 配置文件
      - ./pool:/app/pool          # 临时文件
    
    environment:
      - FLASK_ENV=production
      - HOST=0.0.0.0
      - PORT=5000
    
    env_file:
      - .env
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

# 可选：添加反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - cpaom-web
    restart: unless-stopped
```

## 本地部署

### 系统要求

- **操作系统**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Python**: 3.8 或更高版本
- **内存**: 最少 512MB，推荐 1GB+
- **存储**: 最少 100MB 可用空间
- **网络**: 能访问 CPA 服务器

### Windows 部署

```batch
REM 1. 安装 Python 3.8+
REM 从 https://python.org 下载安装

REM 2. 克隆仓库
git clone https://github.com/qizhuxu/CPAOM.git
cd CPAOM\web

REM 3. 运行安装脚本
setup.bat

REM 4. 启动服务
run.bat
```

### Linux/macOS 部署

```bash
# 1. 安装依赖
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install python3 python3-pip git

# macOS (使用 Homebrew)
brew install python3 git

# 2. 克隆仓库
git clone https://github.com/qizhuxu/CPAOM.git
cd CPAOM/web

# 3. 运行安装脚本
chmod +x setup.sh run.sh
./setup.sh

# 4. 启动服务
./run.sh
```

### 手动部署

```bash
# 1. 创建虚拟环境
python3 -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境
cp config.json.example config.json
cp .env.example .env

# 5. 启动应用
python app.py
```

## 生产环境配置

### 环境变量配置

```bash
# .env 文件
# 基础配置
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000

# 安全配置
SECRET_KEY=your-very-secure-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password

# 数据库配置
DATABASE_PATH=data/cpa_manager.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 性能配置
MAX_WORKERS=10
REQUEST_TIMEOUT=30
```

### 生成安全密钥

```python
# 生成随机密钥
import secrets
print(secrets.token_urlsafe(32))
```

### 服务器配置

```json
{
  "cpa_servers": [
    {
      "id": "prod-server-1",
      "name": "生产服务器 1",
      "base_url": "https://cpa1.example.com",
      "token": "mgt-production-token-1",
      "enable_token_revive": true,
      "enabled": true
    },
    {
      "id": "prod-server-2", 
      "name": "生产服务器 2",
      "base_url": "https://cpa2.example.com",
      "token": "mgt-production-token-2",
      "enable_token_revive": true,
      "enabled": true
    }
  ],
  "settings": {
    "max_workers": 20,
    "request_timeout": 30,
    "retry_attempts": 3,
    "log_level": "INFO"
  }
}
```

## 反向代理配置

### Nginx 配置

```nginx
# /etc/nginx/sites-available/cpaom
server {
    listen 80;
    server_name cpaom.example.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cpaom.example.com;
    
    # SSL 证书
    ssl_certificate /etc/nginx/ssl/cpaom.crt;
    ssl_certificate_key /etc/nginx/ssl/cpaom.key;
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # 代理配置
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持 (用于日志流)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件缓存
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 日志流特殊配置
    location /api/logs/stream {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE 特殊配置
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

### Apache 配置

```apache
# /etc/apache2/sites-available/cpaom.conf
<VirtualHost *:80>
    ServerName cpaom.example.com
    Redirect permanent / https://cpaom.example.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName cpaom.example.com
    
    # SSL 配置
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/cpaom.crt
    SSLCertificateKeyFile /etc/ssl/private/cpaom.key
    
    # 代理配置
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # 安全头
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
</VirtualHost>
```

## 系统服务配置

### Systemd 服务 (Linux)

```ini
# /etc/systemd/system/cpaom-web.service
[Unit]
Description=CPA Account Management Web Service
After=network.target

[Service]
Type=simple
User=cpaom
Group=cpaom
WorkingDirectory=/opt/cpaom/web
Environment=PATH=/opt/cpaom/web/.venv/bin
ExecStart=/opt/cpaom/web/.venv/bin/python app.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# 安全配置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/cpaom/web/data /opt/cpaom/web/pool

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
# 重载配置
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable cpaom-web

# 启动服务
sudo systemctl start cpaom-web

# 查看状态
sudo systemctl status cpaom-web

# 查看日志
sudo journalctl -u cpaom-web -f
```

### Windows 服务

使用 NSSM (Non-Sucking Service Manager)：

```batch
REM 1. 下载 NSSM
REM https://nssm.cc/download

REM 2. 安装服务
nssm install CpaomWeb "C:\path\to\CPAOM\web\.venv\Scripts\python.exe"
nssm set CpaomWeb Arguments "C:\path\to\CPAOM\web\app.py"
nssm set CpaomWeb AppDirectory "C:\path\to\CPAOM\web"

REM 3. 启动服务
nssm start CpaomWeb
```

## 监控和日志

### 健康检查

```bash
# 检查服务状态
curl -f http://localhost:5000/health

# 预期响应
{
  "status": "ok",
  "timestamp": "2026-04-26T17:15:30Z"
}
```

### 日志配置

```python
# 在 app.py 中配置日志
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    # 文件日志
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('CPA Web 启动')
```

### 监控脚本

```bash
#!/bin/bash
# monitor.sh - 服务监控脚本

SERVICE_URL="http://localhost:5000/health"
LOG_FILE="/var/log/cpaom-monitor.log"

check_service() {
    if curl -f -s "$SERVICE_URL" > /dev/null; then
        echo "$(date): 服务正常" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): 服务异常，尝试重启" >> "$LOG_FILE"
        systemctl restart cpaom-web
        return 1
    fi
}

# 每分钟检查一次
while true; do
    check_service
    sleep 60
done
```

## 备份和恢复

### 数据备份

```bash
#!/bin/bash
# backup.sh - 数据备份脚本

BACKUP_DIR="/backup/cpaom"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cpaom_backup_$DATE.tar.gz"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 停止服务 (可选)
# systemctl stop cpaom-web

# 备份数据
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    -C /opt/cpaom/web \
    data/ \
    config.json \
    .env

# 启动服务 (如果之前停止了)
# systemctl start cpaom-web

# 清理旧备份 (保留 30 天)
find "$BACKUP_DIR" -name "cpaom_backup_*.tar.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR/$BACKUP_FILE"
```

### 数据恢复

```bash
#!/bin/bash
# restore.sh - 数据恢复脚本

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <备份文件>"
    exit 1
fi

# 停止服务
systemctl stop cpaom-web

# 备份当前数据
mv /opt/cpaom/web/data /opt/cpaom/web/data.bak.$(date +%Y%m%d_%H%M%S)

# 恢复数据
tar -xzf "$BACKUP_FILE" -C /opt/cpaom/web

# 启动服务
systemctl start cpaom-web

echo "恢复完成"
```

## 性能优化

### 使用 Gunicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动多进程服务
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app

# 或使用配置文件
gunicorn -c gunicorn.conf.py app:app
```

Gunicorn 配置文件：

```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 数据库优化

```sql
-- 添加索引
CREATE INDEX IF NOT EXISTS idx_local_accounts_server_id ON local_accounts(server_id);
CREATE INDEX IF NOT EXISTS idx_local_accounts_email ON local_accounts(email);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_sync_logs_server_id ON sync_logs(server_id);

-- 定期清理
DELETE FROM operation_logs WHERE created_at < datetime('now', '-90 days');
DELETE FROM sync_logs WHERE created_at < datetime('now', '-30 days');

-- 优化数据库
VACUUM;
ANALYZE;
```

## 安全配置

### 防火墙配置

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### SSL 证书

使用 Let's Encrypt：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d cpaom.example.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 安全加固

```bash
# 创建专用用户
sudo useradd -r -s /bin/false cpaom

# 设置文件权限
sudo chown -R cpaom:cpaom /opt/cpaom
sudo chmod 750 /opt/cpaom/web
sudo chmod 640 /opt/cpaom/web/.env
sudo chmod 640 /opt/cpaom/web/config.json

# 禁用不必要的服务
sudo systemctl disable apache2  # 如果不使用
sudo systemctl disable mysql    # 如果不使用
```

## 故障排除

### 常见问题

**1. 服务无法启动**

```bash
# 检查端口占用
sudo netstat -tlnp | grep :5000

# 检查日志
sudo journalctl -u cpaom-web -n 50

# 检查配置文件
python -c "import json; json.load(open('config.json'))"
```

**2. 数据库错误**

```bash
# 检查数据库文件权限
ls -la data/cpa_manager.db

# 测试数据库连接
sqlite3 data/cpa_manager.db ".tables"

# 重建数据库 (谨慎操作)
rm data/cpa_manager.db
python -c "from utils.db_service import DatabaseService; DatabaseService('data/cpa_manager.db').init_db()"
```

**3. 内存不足**

```bash
# 检查内存使用
free -h
ps aux | grep python

# 减少 worker 数量
# 在 gunicorn.conf.py 中设置 workers = 2
```

**4. 磁盘空间不足**

```bash
# 检查磁盘使用
df -h

# 清理日志
sudo journalctl --vacuum-time=7d

# 清理旧备份
find /backup -name "*.tar.gz" -mtime +7 -delete
```

### 性能监控

```bash
# 系统资源监控
htop
iotop
nethogs

# 应用性能监控
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/health

# curl-format.txt 内容:
#     time_namelookup:  %{time_namelookup}\n
#        time_connect:  %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#    time_pretransfer:  %{time_pretransfer}\n
#       time_redirect:  %{time_redirect}\n
#  time_starttransfer:  %{time_starttransfer}\n
#                     ----------\n
#          time_total:  %{time_total}\n
```

## 升级指南

### 版本升级

```bash
# 1. 备份数据
./backup.sh

# 2. 停止服务
sudo systemctl stop cpaom-web

# 3. 更新代码
git pull origin main

# 4. 更新依赖
source .venv/bin/activate
pip install -r requirements.txt

# 5. 运行迁移 (如果有)
python migrate.py

# 6. 启动服务
sudo systemctl start cpaom-web

# 7. 验证升级
curl -f http://localhost:5000/health
```

### Docker 镜像升级

```bash
# 1. 拉取新镜像
docker-compose pull

# 2. 重启服务
docker-compose up -d

# 3. 清理旧镜像
docker image prune -f
```

## 扩展部署

### 负载均衡

```nginx
# nginx.conf
upstream cpaom_backend {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://cpaom_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 高可用部署

```yaml
# docker-swarm.yml
version: '3.8'

services:
  cpaom-web:
    image: ghcr.io/qizhuxu/cpaom/cpaom-web:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    ports:
      - "5000:5000"
    volumes:
      - nfs_data:/app/data
    networks:
      - cpaom_network

volumes:
  nfs_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nfs-server,rw
      device: ":/path/to/shared/data"

networks:
  cpaom_network:
    driver: overlay
```

部署到 Docker Swarm：

```bash
docker stack deploy -c docker-swarm.yml cpaom
```