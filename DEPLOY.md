# Simply Agent 部署指南

本文档提供 Simply Agent 的详细部署指南，包括开发环境、测试环境和生产环境的部署。

## 目录

- [环境要求](#环境要求)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署](#docker-部署)
- [数据库配置](#数据库配置)
- [反向代理配置](#反向代理配置)
- [监控与日志](#监控与日志)
- [安全加固](#安全加固)
- [故障排查](#故障排查)
- [性能优化](#性能优化)

---

## 环境要求

### 硬件要求

**最小配置（开发/测试）**
- CPU: 2 核
- 内存: 4 GB
- 磁盘: 20 GB

**推荐配置（生产）**
- CPU: 4 核+
- 内存: 8 GB+
- 磁盘: 50 GB+ SSD

### 软件要求

- Docker 20.10+
- Docker Compose 2.0+
- (可选) Nginx 1.18+
- (可选) Python 3.9+
- (可选) Node.js 20+

---

## 开发环境部署

### 方式一：使用 Docker Compose（推荐）

1. **准备环境变量文件**
```bash
cd simply_agent
cp backend/.env.example backend/.env
```

2. **编辑配置文件**
```bash
vim backend/.env
```

关键配置：
```env
FLASK_ENV=development
DATABASE_URL=sqlite:///simply_agent.db
SECRET_KEY=dev-secret-key
API_PORT=5000
OPENAI_API_KEY=your-key-here
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **验证部署**
```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 方式二：本地运行

#### 后端
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行
python run.py
```

#### 前端
```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

---

## 生产环境部署

### 1. 准备工作

#### 生成强密钥
```bash
# 生成 SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# 生成数据库密码
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

#### 配置环境变量
编辑 `backend/.env`：
```env
# 应用配置
FLASK_ENV=production
SECRET_KEY=<生成的强密钥，至少32字符>
API_PORT=5000

# 数据库配置（根据选择配置）
# SQLite（小规模）
DATABASE_URL=sqlite:///simply_agent.db

# MySQL（推荐）
DATABASE_URL=mysql://simply_agent:<password>@mysql:3306/simply_agent

# PostgreSQL
DATABASE_URL=postgresql://simply_agent:<password>@postgres:5432/simply_agent

# LLM API 配置
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
QWEN_API_KEY=sk-...

# 安全配置
SESSION_COOKIE_SAMESITE=Lax
CORS_ENABLED=true
CORS_ORIGINS=https://yourdomain.com

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# 数据库连接池
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

### 2. 选择数据库方案

#### SQLite（适合小规模部署）
默认配置，无需额外设置。

#### MySQL（推荐）
```bash
# 启动 MySQL
docker-compose --profile mysql up -d mysql

# 等待 MySQL 就绪
docker-compose logs -f mysql
```

配置环境变量：
```env
DATABASE_URL=mysql://simply_agent:yourpassword@mysql:3306/simply_agent
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=simply_agent
MYSQL_USER=simply_agent
MYSQL_PASSWORD=yourpassword
```

#### PostgreSQL
```bash
# 启动 PostgreSQL
docker-compose --profile postgres up -d postgres
```

配置环境变量：
```env
DATABASE_URL=postgresql://simply_agent:yourpassword@postgres:5432/simply_agent
POSTGRES_DB=simply_agent
POSTGRES_USER=simply_agent
POSTGRES_PASSWORD=yourpassword
```

### 3. 启动生产服务

```bash
# 使用 SQLite
docker-compose up -d

# 使用 MySQL
docker-compose --profile mysql up -d

# 使用 PostgreSQL
docker-compose --profile postgres up -d
```

### 4. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 检查健康状态
curl http://localhost:5000/api/health

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## Docker 部署

### 镜像构建

#### 后端镜像
```bash
cd backend
docker build -t simply-agent-backend:latest .
```

#### 前端镜像
```bash
cd frontend
docker build -t simply-agent-frontend:latest .
```

### 使用 Docker Compose

```bash
# 构建并启动
docker-compose up -d --build

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重启服务
docker-compose restart
```

### 资源限制

编辑 `docker-compose.yml`，添加资源限制：
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  frontend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### 数据持久化

Docker Compose 已配置以下数据卷：
- `backend-data`: 后端数据
- `backend-logs`: 后端日志
- `chroma-data`: 向量数据库
- `mysql-data`: MySQL 数据
- `postgres-data`: PostgreSQL 数据

备份命令：
```bash
# 备份所有数据卷
docker run --rm \
  -v simply_agent_backend-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/backend-data.tar.gz /data

# 备份特定数据卷
docker run --rm \
  -v simply_agent_mysql-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/mysql-data.tar.gz /data
```

---

## 数据库配置

### 数据库迁移

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行迁移
python -c "from app.extensions import db; from app import create_app; app = create_app(); app.app_context().push(); db.create_all()"
```

### 数据库备份

#### MySQL
```bash
# 备份
docker-compose exec mysql mysqldump -u simply_agent -p simply_agent > backup.sql

# 恢复
docker-compose exec -T mysql mysql -u simply_agent -p simply_agent < backup.sql
```

#### PostgreSQL
```bash
# 备份
docker-compose exec postgres pg_dump -U simply_agent simply_agent > backup.sql

# 恢复
docker-compose exec -T postgres psql -U simply_agent simply_agent < backup.sql
```

#### SQLite
```bash
# 备份
docker-compose cp backend:/app/simply_agent.db ./backup.db

# 恢复
docker-compose cp ./backup.db backend:/app/simply_agent.db
```

---

## 反向代理配置

### 使用 Nginx

创建 Nginx 配置文件 `/etc/nginx/sites-available/simply-agent`：

```nginx
upstream backend {
    server localhost:5000;
}

upstream frontend {
    server localhost:80;
}

server {
    listen 80;
    server_name yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 前端
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 流式响应支持
        proxy_buffering off;
        proxy_cache off;
    }

    # 日志
    access_log /var/log/nginx/simply-agent-access.log;
    error_log /var/log/nginx/simply-agent-error.log;
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/simply-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 监控与日志

### 日志管理

#### 查看实时日志
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

#### 日志轮转
编辑 `/etc/logrotate.d/docker-compose`：
```
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 监控指标

#### 健康检查
```bash
# 后端健康检查
curl http://localhost:5000/api/health

# 服务状态
docker-compose ps
```

#### 资源监控
```bash
# 容器资源使用
docker stats

# 磁盘使用
docker system df
```

---

## 安全加固

### 1. 网络安全

#### 修改默认端口
编辑 `docker-compose.yml`：
```yaml
services:
  backend:
    ports:
      - "8000:5000"  # 使用非标准端口
```

#### 配置防火墙
```bash
# UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -P INPUT DROP
```

### 2. 应用安全

#### 环境变量验证
```bash
# 检查密钥长度
python -c "import os; key = os.getenv('SECRET_KEY', ''); print(f'Key length: {len(key)}')"

# 验证数据库连接
python -c "from app.config import Config; c = Config(); print(c.DATABASE_URL)"
```

#### CORS 配置
生产环境限制 CORS 来源：
```env
CORS_ENABLED=true
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. 容器安全

#### 使用非 root 用户
编辑 `backend/Dockerfile`：
```dockerfile
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser
```

#### 扫描漏洞
```bash
# Trivy
trivy image simply-agent-backend:latest

# Docker Bench
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /usr/lib/systemd:/usr/lib/systemd:ro \
  -v /var/run/docker:/var/run/docker:ro \
  -v /etc:/etc:ro \
  --label docker_bench_security \
  docker/docker-bench-security
```

---

## 故障排查

### 常见问题

#### 1. 服务启动失败
```bash
# 查看日志
docker-compose logs backend

# 检查配置
docker-compose config

# 重新构建
docker-compose up -d --build
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose ps mysql

# 测试连接
docker-compose exec backend python -c "from app.extensions import db; print(db.engine)"

# 检查网络
docker network ls
docker network inspect simply-agent-network
```

#### 3. 内存不足
```bash
# 检查内存使用
docker stats

# 清理未使用的资源
docker system prune -a

# 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. API 请求超时
```bash
# 检查后端日志
docker-compose logs -f backend

# 增加超时时间（nginx）
proxy_read_timeout 300;
proxy_connect_timeout 300;
```

### 调试模式

#### 启用调试日志
编辑 `backend/.env`：
```env
LOG_LEVEL=DEBUG
FLASK_ENV=development
```

#### 进入容器调试
```bash
# 后端容器
docker-compose exec backend bash

# 前端容器
docker-compose exec frontend sh
```

---

## 性能优化

### 1. 数据库优化

#### 连接池配置
```env
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

#### 慢查询日志（MySQL）
```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

### 2. 缓存配置

#### Redis（可选）
添加到 `docker-compose.yml`：
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
```

### 3. 前端优化

#### CDN 配置
```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router'],
          'ui': ['element-plus']
        }
      }
    }
  }
}
```

### 4. 后端优化

#### Gunicorn 配置
编辑 `backend/run.py`：
```python
# 生产环境使用 Gunicorn
# gunicorn -w 4 -k gevent -b 0.0.0.0:5000 'app:create_app()'
```

---

## 升级与维护

### 升级应用

```bash
# 拉取最新代码
git pull origin main

# 备份数据
docker-compose exec mysql mysqldump -u simply_agent -p simply_agent > backup.sql

# 重新构建并启动
docker-compose up -d --build

# 清理旧镜像
docker image prune -a
```

### 定期维护

#### 数据库备份脚本
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"
docker-compose exec -T mysql mysqldump -u simply_agent -p${MYSQL_PASSWORD} simply_agent > ${BACKUP_DIR}/backup_${DATE}.sql
find ${BACKUP_DIR} -name "backup_*.sql" -mtime +7 -delete
```

#### 日志清理
```bash
#!/bin/bash
# cleanup.sh
docker system prune -f --volumes
docker logs $(docker ps -qa) 2>&1 | grep -A 10 "Error"
```

---

## 附录

### A. 环境变量清单

完整的环境变量列表见 `backend/.env.example`。

### B. 端口清单

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|----------|----------|------|
| frontend | 80 | 80 | 前端服务 |
| backend | 5000 | 5000 | 后端 API |
| mysql | 3306 | 3306 | MySQL 数据库 |
| postgres | 5432 | 5432 | PostgreSQL 数据库 |
| chroma | 8000 | 8000 | 向量数据库 |

### C. 支持与联系

- 文档: [README.md](README.md)
- 问题反馈: GitHub Issues
- 邮件: support@example.com

---

*文档版本: v1.0*
*最后更新: 2026-05-14*
