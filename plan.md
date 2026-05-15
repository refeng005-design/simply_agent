# Simply Agent - 技术方案文档

## 一、技术栈选型

| 层次 | 技术选择 | 说明 |
|------|----------|------|
| 后端框架 | Flask 3.x | 轻量、灵活、API开发友好 |
| 前端框架 | Vue 3 + Vite | 现代化、开发体验好 |
| UI组件库 | Element Plus | Vue生态成熟组件库 |
| 数据库 | MySQL 8.0 | 存储对话历史、知识库、配置 |
| ORM | SQLAlchemy | Python生态主流ORM |
| 向量数据库 | Chroma | 本地向量存储，支持知识库检索 |
| LLM集成 | LangChain | 统一多模型接口，简化调用 |
| API文档 | Flask-RESTX | 自动生成Swagger文档 |
| 部署 | Docker + Docker Compose | 容器化部署 |

---

## 二、项目目录结构

```
simply_agent/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py        # Flask应用初始化
│   │   ├── config.py          # 配置管理
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   ├── knowledge.py
│   │   │   └── model_config.py
│   │   ├── schemas/           # 请求/响应Schema
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   └── knowledge.py
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py     # LLM统一接口
│   │   │   ├── rag_service.py     # 知识库检索
│   │   │   └── conversation_service.py
│   │   ├── api/               # API路由
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── models.py
│   │   │   ├── history.py
│   │   │   └── knowledge.py
│   │   ├── utils/             # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py
│   │   │   └── prompt_builder.py
│   │   └── extensions.py      # Flask扩展初始化
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_llm_service.py
│   │   ├── test_rag_service.py
│   │   └── test_api.py
│   ├── migrations/            # 数据库迁移
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # 组件
│   │   │   ├── ChatWindow.vue
│   │   │   ├── MessageList.vue
│   │   │   ├── MessageInput.vue
│   │   │   ├── ModelSelector.vue
│   │   │   ├── HistorySidebar.vue
│   │   │   └── SettingsPanel.vue
│   │   ├── views/
│   │   │   └── ChatView.vue
│   │   ├── stores/            # Pinia状态管理
│   │   │   ├── chat.js
│   │   │   └── settings.js
│   │   ├── api/
│   │   │   └── client.js      # API客户端
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── data/                       # 数据目录
│   ├── chroma/                # 向量数据库
│   └── knowledge/             # 知识库文件
│
├── docker-compose.yml          # 容器编排
├── .env.example               # 环境变量模板
├── spec.md                    # 产品规格文档
└── plan.md                    # 本文档
```

---

## 三、核心数据模型

### 3.1 数据库表设计

#### 表：conversations（对话会话）

```sql
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(64),                -- 用户标识（可选）
    title VARCHAR(200),                 -- 对话标题（首条消息摘要）
    model_name VARCHAR(50) NOT NULL,    -- 使用的模型
    memory_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);
```

#### 表：messages（消息记录）

```sql
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id)
);
```

#### 表：knowledge_entries（知识库条目）

```sql
CREATE TABLE knowledge_entries (
    id VARCHAR(36) PRIMARY KEY,
    category VARCHAR(100),              -- 分类
    question TEXT,                      -- 问题
    answer TEXT,                        -- 答案
    metadata JSON,                      -- 额外信息
    vector_id VARCHAR(100),             -- Chroma向量ID
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_enabled (enabled)
);
```

#### 表：model_configs（模型配置）

```sql
CREATE TABLE model_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    provider ENUM('openai', 'anthropic', 'qwen', 'zhipu') NOT NULL,
    api_key VARCHAR(200),
    api_endpoint VARCHAR(200),
    model_name VARCHAR(100),            -- 实际模型名，如 gpt-4o
    max_tokens INT DEFAULT 2000,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    enabled BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 0,             -- 优先级，备用模型排序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 SQLAlchemy模型定义

```python
# backend/app/models/conversation.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64))
    title = Column(String(200))
    model_name = Column(String(50), nullable=False)
    memory_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    updated_at = Column(DateTime, server_default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP')

# 其他模型类似...
```

---

## 四、API接口定义

### 4.1 对话接口

#### POST /api/chat/completions
创建对话 completion

**Request:**
```json
{
    "conversation_id": "optional-uuid",      // 可选，继续对话
    "message": "用户输入的内容",
    "model_name": "gpt-4o",                  // 可选，默认使用配置的默认模型
    "stream": true                           // 是否流式响应
}
```

**Response (stream=false):**
```json
{
    "conversation_id": "uuid",
    "message_id": "uuid",
    "content": "AI回复内容",
    "model_name": "gpt-4o",
    "created_at": "2026-05-13T10:00:00Z"
}
```

**Response (stream=true):** Server-Sent Events 格式

### 4.2 模型管理接口

#### GET /api/models
获取可用模型列表

**Response:**
```json
{
    "models": [
        {
            "name": "gpt-4o",
            "provider": "openai",
            "enabled": true,
            "is_default": true
        },
        {
            "name": "claude-sonnet-4-20250514",
            "provider": "anthropic",
            "enabled": true,
            "is_default": false
        }
    ]
}
```

#### PUT /api/models/{name}/select
选择当前模型

### 4.3 对话历史接口

#### GET /api/history
获取对话历史列表

**Query Params:** `page=1&limit=20`

**Response:**
```json
{
    "total": 42,
    "items": [
        {
            "id": "uuid",
            "title": "如何退货？",
            "model_name": "gpt-4o",
            "created_at": "2026-05-13T09:30:00Z",
            "message_count": 5
        }
    ]
}
```

#### GET /api/history/{conversation_id}
获取对话详情

#### DELETE /api/history/{conversation_id}
删除对话

### 4.4 知识库接口

#### POST /api/knowledge/upload
上传知识库内容

**Request:**
```json
{
    "category": "产品说明",
    "entries": [
        {
            "question": "如何退货？",
            "answer": "您可以在订单页面点击退货..."
        }
    ]
}
```

#### GET /api/knowledge/search
搜索知识库

**Query Params:** `q=关键词&limit=5`

---

## 五、核心模块设计

### 5.1 LLM服务层（llm_service.py）

统一多模型调用的抽象接口：

```python
class LLMService:
    def chat(self, messages: List[Message], model: str, stream: bool = False) -> str:
        """统一对话接口"""

    def get_available_models(self) -> List[ModelInfo]:
        """获取可用模型列表"""

    def switch_model(self, model_name: str) -> bool:
        """切换模型"""
```

支持 providers：
- OpenAI: GPT-4o, GPT-4.1, GPT-3.5
- Anthropic: Claude 4.7, Claude 3.5 Sonnet
- 阿里云: 通义千问
- 智谱AI: GLM-4

### 5.2 RAG服务层（rag_service.py）

知识库检索增强：

```python
class RAGService:
    def __init__(self):
        self.vector_store = Chroma(persist_directory="./data/chroma")

    def search(self, query: str, top_k: int = 3) -> List[KnowledgeEntry]:
        """向量检索相关内容"""

    def add_entry(self, question: str, answer: str, category: str):
        """添加知识库条目并生成向量"""

    def build_prompt(self, query: str, context: List[str]) -> str:
        """构建带上下文的Prompt"""
```

### 5.3 对话服务层（conversation_service.py）

会话管理：

```python
class ConversationService:
    def create_conversation(self, model_name: str) -> Conversation:
        """创建新对话"""

    def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        """添加消息"""

    def get_history(self, conversation_id: str, limit: int = 10) -> List[Message]:
        """获取历史消息"""

    def get_context_messages(self, conversation_id: str) -> List[Message]:
        """获取用于LLM的上下文消息"""
```

---

## 六、前端核心组件

### 6.1 组件结构

| 组件 | 职责 |
|------|------|
| ChatWindow.vue | 主聊天窗口容器 |
| MessageList.vue | 消息列表展示，支持流式渲染 |
| MessageInput.vue | 输入框，支持多行、快捷键发送 |
| ModelSelector.vue | 模型选择下拉框 |
| HistorySidebar.vue | 历史对话侧边栏 |
| SettingsPanel.vue | 设置面板（记忆开关等） |

### 6.2 状态管理（Pinia）

```javascript
// stores/chat.js
export const useChatStore = defineStore('chat', {
    state: () => ({
        currentConversation: null,
        messages: [],
        isLoading: false,
        currentModel: 'gpt-4o',
        memoryEnabled: true
    }),
    actions: {
        async sendMessage(content) { },
        async loadHistory(conversationId) { },
        async switchModel(modelName) { }
    }
})
```

### 6.3 API通信

```javascript
// api/client.js
import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
    timeout: 30000
})

// 支持流式响应
export async function streamChat(params, onChunk) {
    const response = await fetch('/api/chat/completions', {
        method: 'POST',
        body: JSON.stringify(params)
    })
    const reader = response.body.getReader()
    // ... SSE 处理逻辑
}
```

---

## 七、实施阶段

### 阶段一：基础框架搭建（2天）

- [ ] 创建项目目录结构
- [ ] 初始化后端Flask项目
- [ ] 初始化前端Vue3项目
- [ ] 配置开发环境（热重载、调试）
- [ ] 编写Hello World接口验证前后端联通

### 阶段二：数据模型与数据库（1天）

- [ ] 设计并创建数据库表
- [ ] 编写SQLAlchemy模型
- [ ] 配置数据库连接池
- [ ] 编写基础CRUD测试

### 阶段三：LLM服务集成（2天）

- [ ] 实现LLMService抽象层
- [ ] 集成OpenAI SDK
- [ ] 集成Anthropic SDK
- [ ] 实现模型切换逻辑
- [ ] 编写单元测试

### 阶段四：知识库RAG（2天）

- [ ] 搭建Chroma向量数据库
- [ ] 实现文本向量化（使用OpenAI Embeddings或本地模型）
- [ ] 实现RAGService检索逻辑
- [ ] 实现知识库管理API
- [ ] 测试检索准确性

### 阶段五：对话核心功能（2天）

- [ ] 实现ConversationService
- [ ] 实现对话API（/api/chat/completions）
- [ ] 支持流式响应（SSE）
- [ ] 实现上下文记忆逻辑
- [ ] 集成RAG到对话流程

### 阶段六：前端界面开发（3天）

- [ ] 搭建页面布局（聊天区+历史侧边栏）
- [ ] 实现MessageList组件（支持流式渲染）
- [ ] 实现MessageInput组件
- [ ] 实现ModelSelector组件
- [ ] 实现HistorySidebar组件
- [ ] 实现SettingsPanel（记忆开关）
- [ ] API对接与状态管理

### 阶段七：历史与设置功能（1天）

- [ ] 对话历史API
- [ ] 前端历史记录展示
- [ ] 删除/清空历史功能
- [ ] 记忆开关功能

### 阶段八：测试与优化（2天）

- [ ] 端到端测试
- [ ] 并发测试
- [ ] 错误处理完善
- [ ] 响应速度优化
- [ ] 用户体验细节打磨

### 阶段九：部署准备（1天）

- [ ] 编写Dockerfile
- [ ] 配置docker-compose
- [ ] 环境变量管理
- [ ] 部署文档编写

**预计总工时：16天**

---

## 八、环境变量配置

```bash
# .env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key

# 数据库
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/simply_agent

# Redis（可选，用于缓存）
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxx

# 阿里云通义千问
DASHSCOPE_API_KEY=sk-xxx

# 向量数据库
CHROMA_PERSIST_DIR=./data/chroma

# 前端
VITE_API_URL=http://localhost:5000/api
```

---

*文档版本：v1.0*
*创建日期：2026-05-13*
*基于 spec.md v1.0*
