# Simply Agent

一个基于 LLM 的智能对话代理系统，支持多模型接入、知识库 RAG、流式对话等功能。

## 特性

- 多 LLM 提供商支持（OpenAI、Anthropic、通义千问等）
- 知识库 RAG（检索增强生成）
- 流式对话响应
- 对话历史管理
- Docker 容器化部署
- 生产环境配置

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 使用 Docker Compose 启动

1. 克隆仓库
```bash
git clone <repository-url>
cd simply_agent
```

2. 配置环境变量
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件，配置 API 密钥等信息
```

3. 启动服务
```bash
# 启动基础服务（使用 SQLite）
docker-compose up -d

# 或使用 MySQL
docker-compose --profile mysql up -d

# 或使用 PostgreSQL
docker-compose --profile postgres up -d
```

4. 访问应用
- 前端: http://localhost
- 后端 API: http://localhost:5000
- API 文档: http://localhost:5000/api/docs

### 开发环境运行

#### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

## 配置说明

### 环境变量

主要环境变量配置（详见 `backend/.env.example`）：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_ENV` | 运行环境 | `development` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///simply_agent.db` |
| `SECRET_KEY` | 应用密钥 | - |
| `API_PORT` | API 端口 | `5000` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |
| `QWEN_API_KEY` | 通义千问 API 密钥 | - |

### 数据库选择

项目支持多种数据库：

- **SQLite**: 默认，适合开发和小规模部署
- **MySQL**: 适合生产环境
- **PostgreSQL**: 适合生产环境

使用 MySQL 或 PostgreSQL 时，需要在 `.env` 中配置相应的连接字符串，并使用 Docker Compose profile 启动。

## 项目结构

```
simply_agent/
├── backend/                 # 后端服务
│   ├── app/                # 应用代码
│   ├── tests/              # 测试代码
│   ├── migrations/         # 数据库迁移
│   ├── requirements.txt    # Python 依赖
│   ├── Dockerfile          # 后端 Docker 镜像
│   └── .env.example        # 环境变量模板
├── frontend/               # 前端服务
│   ├── src/               # 源代码
│   ├── tests/             # 测试代码
│   ├── package.json       # Node 依赖
│   ├── Dockerfile         # 前端 Docker 镜像
│   └── vite.config.js     # Vite 配置
├── docker-compose.yml      # Docker 编排文件
└── README.md              # 项目文档
```

## 测试

### 后端测试
```bash
cd backend
pytest tests/ -v
```

### 前端测试
```bash
cd frontend
npm test
```

## 部署

详细的部署指南请参考 [DEPLOY.md](DEPLOY.md)。

### 生产环境配置要点

1. 设置强密钥：`SECRET_KEY` 必须至少 32 字符
2. 使用生产数据库：MySQL 或 PostgreSQL
3. 配置 CORS：限制允许的来源
4. 启用日志：配置日志文件路径
5. 设置资源限制：在 docker-compose.yml 中配置

## 常见问题

### 如何生成强密钥？

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 如何查看日志？

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 如何重置数据库？

```bash
# 停止服务并删除数据卷
docker-compose down -v

# 重新启动
docker-compose up -d
```

## 开发指南

项目采用 TDD（测试驱动开发）模式，详见 [tasks.md](tasks.md)。

## 许可证

MIT License

## 联系方式

- 问题反馈: GitHub Issues
- 文档: [DEPLOY.md](DEPLOY.md)
