# Simply Agent - 原子任务列表

> **规则说明**：
> - 每个任务只修改/创建一个文件
> - 奇数任务 = 写测试（TDD的Red阶段）
> - 偶数任务 = 写实现（TDD的Green阶段）
> - 按顺序执行，不可跳过

---

## 阶段一：基础框架搭建（10个任务）

### 后端初始化

- [ ] **T1** `backend/tests/test_config.py` - 测试配置加载功能
- [ ] **T2** `backend/app/config.py` - 实现配置管理（支持环境变量、开发/生产环境）
- [ ] **T3** `backend/tests/test_app.py` - 测试Flask应用创建
- [ ] **T4** `backend/app/__init__.py` - 创建Flask应用工厂函数
- [ ] **T5** `backend/tests/test_health.py` - 测试健康检查接口
- [ ] **T6** `backend/app/api/__init__.py` - 实现健康检查API路由
- [ ] **T7** `backend/requirements.txt` - 编写Python依赖清单
- [ ] **T8** `backend/run.py` - 创建应用启动入口
- [ ] **T9** `backend/.env.example` - 创建环境变量模板
- [ ] **T10** `backend/Dockerfile` - 编写后端Dockerfile

### 前端初始化

- [ ] **T11** `frontend/tests/main.spec.js` - 测试应用挂载
- [ ] **T12** `frontend/src/main.js` - 创建Vue应用入口
- [ ] **T13** `frontend/tests/app.spec.js` - 测试App组件渲染
- [ ] **T14** `frontend/src/App.vue` - 创建根组件
- [ ] **T15** `frontend/tests/api-client.spec.js` - 测试API客户端配置
- [ ] **T16** `frontend/src/api/client.js` - 创建axios实例配置
- [ ] **T17** `frontend/package.json` - 编写前端依赖清单
- [ ] **T18** `frontend/vite.config.js` - 配置Vite
- [ ] **T19** `frontend/index.html` - 创建HTML入口
- [ ] **T20** `frontend/Dockerfile` - 编写前端Dockerfile

---

## 阶段二：数据模型与数据库（16个任务）

- [ ] **T21** `backend/tests/test_models_conversation.py` - 测试Conversation模型
- [ ] **T22** `backend/app/models/conversation.py` - 实现Conversation数据模型
- [ ] **T23** `backend/tests/test_models_message.py` - 测试Message模型
- [ ] **T24** `backend/app/models/message.py` - 实现Message数据模型
- [ ] **T25** `backend/tests/test_models_knowledge.py` - 测试KnowledgeEntry模型
- [ ] **T26** `backend/app/models/knowledge.py` - 实现KnowledgeEntry数据模型
- [ ] **T27** `backend/tests/test_models_model_config.py` - 测试ModelConfig模型
- [ ] **T28** `backend/app/models/model_config.py` - 实现ModelConfig数据模型
- [ ] **T29** `backend/tests/test_db.py` - 测试数据库连接和初始化
- [ ] **T30** `backend/app/extensions.py` - 实现数据库扩展初始化（SQLAlchemy）
- [ ] **T31** `backend/tests/test_base.py` - 测试Base模型类
- [ ] **T32** `backend/app/models/__init__.py` - 创建Base类和模型导出
- [ ] **T33** `backend/tests/test_migrations.py` - 测试数据库迁移
- [ ] **T34** `backend/migrations/001_initial.sql` - 编写初始建表SQL
- [ ] **T35** `backend/tests/test_schemas_chat.py` - 测试聊天相关Schema
- [ ] **T36** `backend/app/schemas/chat.py` - 实现聊天请求/响应Schema

---

## 阶段三：LLM服务集成（14个任务）

- [ ] **T37** `backend/tests/test_llm_service_base.py` - 测试LLMService基类
- [ ] **T38** `backend/app/services/llm_service.py` - 实现LLMService抽象基类
- [ ] **T39** `backend/tests/test_openai_provider.py` - 测试OpenAI提供商
- [ ] **T40** `backend/app/services/providers/openai_provider.py` - 实现OpenAI调用
- [ ] **T41** `backend/tests/test_anthropic_provider.py` - 测试Anthropic提供商
- [ ] **T42** `backend/app/services/providers/anthropic_provider.py` - 实现Anthropic调用
- [ ] **T43** `backend/tests/test_qwen_provider.py` - 测试通义千问提供商
- [ ] **T44** `backend/app/services/providers/qwen_provider.py` - 实现通义千问调用
- [ ] **T45** `backend/tests/test_llm_factory.py` - 测试提供商工厂
- [ ] **T46** `backend/app/services/providers/factory.py` - 实现提供商工厂
- [ ] **T47** `backend/tests/test_llm_service_impl.py` - 测试LLMService完整实现
- [ ] **T48** `backend/app/services/llm_service.py` - 完善LLMService实现
- [ ] **T49** `backend/tests/test_models_api.py` - 测试模型列表API
- [ ] **T50** `backend/app/api/models.py` - 实现模型管理API

---

## 阶段四：知识库RAG（12个任务）

- [ ] **T51** `backend/tests/test_vector_store.py` - 测试向量存储
- [ ] **T52** `backend/app/utils/vector_store.py` - 实现Chroma向量存储封装
- [ ] **T53** `backend/tests/test_embeddings.py` - 测试文本向量化
- [ ] **T54** `backend/app/utils/embeddings.py` - 实现文本向量化工具
- [ ] **T55** `backend/tests/test_rag_service.py` - 测试RAG服务
- [ ] **T56** `backend/app/services/rag_service.py` - 实现RAG服务
- [ ] **T57** `backend/tests/test_prompt_builder.py` - 测试Prompt构建器
- [ ] **T58** `backend/app/utils/prompt_builder.py` - 实现RAG Prompt模板
- [ ] **T59** `backend/tests/test_knowledge_api.py` - 测试知识库API
- [ ] **T60** `backend/app/api/knowledge.py` - 实现知识库管理API
- [ ] **T61** `backend/tests/test_schemas_knowledge.py` - 测试知识库Schema
- [ ] **T62** `backend/app/schemas/knowledge.py` - 实现知识库请求/响应Schema

---

## 阶段五：对话核心功能（12个任务）

- [ ] **T63** `backend/tests/test_conversation_service.py` - 测试对话服务
- [ ] **T64** `backend/app/services/conversation_service.py` - 实现对话服务
- [ ] **T65** `backend/tests/test_chat_api.py` - 测试对话API
- [ ] **T66** `backend/app/api/chat.py` - 实现对话API（非流式）
- [ ] **T67** `backend/tests/test_chat_stream.py` - 测试流式对话
- [ ] **T68** `backend/app/api/chat.py` - 增加流式响应支持（SSE）
- [ ] **T69** `backend/tests/test_chat_with_rag.py` - 测试RAG增强对话
- [ ] **T70** `backend/app/api/chat.py` - 集成RAG到对话流程
- [ ] **T71** `backend/tests/test_chat_history_api.py` - 测试历史API
- [ ] **T72** `backend/app/api/history.py` - 实现对话历史API
- [ ] **T73** `backend/tests/test_chat_memory.py` - 测试记忆控制
- [ ] **T74** `backend/app/services/conversation_service.py` - 增加记忆开关逻辑

---

## 阶段六：前端界面开发（24个任务）

### 状态管理

- [ ] **T75** `frontend/tests/stores/chat.spec.js` - 测试聊天状态
- [ ] **T76** `frontend/src/stores/chat.js` - 创建聊天状态管理
- [ ] **T77** `frontend/tests/stores/settings.spec.js` - 测试设置状态
- [ ] **T78** `frontend/src/stores/settings.js` - 创建设置状态管理

### API客户端

- [ ] **T79** `frontend/tests/api/chat.spec.js` - 测试聊天API调用
- [ ] **T80** `frontend/src/api/chat.js` - 实现聊天API函数
- [ ] **T81** `frontend/tests/api/history.spec.js` - 测试历史API调用
- [ ] **T82** `frontend/src/api/history.js` - 实现历史API函数
- [ ] **T83** `frontend/tests/api/models.spec.js` - 测试模型API调用
- [ ] **T84** `frontend/src/api/models.js` - 实现模型API函数

### 组件开发

- [ ] **T85** `frontend/tests/components/MessageList.spec.js` - 测试消息列表
- [ ] **T86** `frontend/src/components/MessageList.vue` - 实现消息列表组件
- [ ] **T87** `frontend/tests/components/MessageInput.spec.js` - 测试输入框
- [ ] **T88** `frontend/src/components/MessageInput.vue` - 实现输入框组件
- [ ] **T89** `frontend/tests/components/ModelSelector.spec.js` - 测试模型选择器
- [ ] **T90** `frontend/src/components/ModelSelector.vue` - 实现模型选择组件
- [ ] **T91** `frontend/tests/components/HistorySidebar.spec.js` - 测试历史侧边栏
- [ ] **T92** `frontend/src/components/HistorySidebar.vue` - 实现历史侧边栏
- [ ] **T93** `frontend/tests/components/SettingsPanel.spec.js` - 测试设置面板
- [ ] **T94** `frontend/src/components/SettingsPanel.vue` - 实现设置面板
- [ ] **T95** `frontend/tests/components/ChatWindow.spec.js` - 测试聊天窗口
- [ ] **T96** `frontend/src/components/ChatWindow.vue` - 实现聊天窗口容器
- [ ] **T97** `frontend/tests/views/ChatView.spec.js` - 测试聊天视图
- [ ] **T98** `frontend/src/views/ChatView.vue` - 实现聊天视图页面

---

## 阶段七：历史与设置功能（8个任务）

- [ ] **T99** `backend/tests/test_history_delete.py` - 测试删除对话
- [ ] **T100** `backend/app/api/history.py` - 增加删除对话接口
- [ ] **T101** `backend/tests/test_history_clear.py` - 测试清空历史
- [ ] **T102** `backend/app/api/history.py` - 增加清空历史接口
- [ ] **T103** `frontend/tests/components/ConfirmDialog.spec.js` - 测试确认对话框
- [ ] **T104** `frontend/src/components/ConfirmDialog.vue` - 实现确认对话框
- [ ] **T105** `frontend/tests/components/MemoryToggle.spec.js` - 测试记忆开关
- [ ] **T106** `frontend/src/components/MemoryToggle.vue` - 实现记忆开关组件

---

## 阶段八：测试与优化（10个任务）

- [ ] **T107** `backend/tests/test_concurrent.py` - 测试并发处理
- [ ] **T108** `backend/app/services/conversation_service.py` - 优化并发处理
- [ ] **T109** `backend/tests/test_error_handling.py` - 测试错误处理
- [ ] **T110** `backend/app/api/__init__.py` - 统一错误处理中间件
- [ ] **T111** `backend/tests/test_rate_limit.py` - 测试限流
- [ ] **T112** `backend/app/api/__init__.py` - 添加限流中间件
- [ ] **T113** `frontend/tests/e2e/chat.spec.js` - 端到端测试
- [ ] **T114** `frontend/src/api/client.js` - 优化请求重试逻辑
- [ ] **T115** `frontend/tests/components/MessageList.spec.js` - 测试流式渲染优化
- [ ] **T116** `frontend/src/components/MessageList.vue` - 优化流式渲染性能

---

## 阶段九：部署准备（6个任务）

- [ ] **T117** `docker-compose.yml` - 编写容器编排文件
- [ ] **T118** `.env.example` - 更新环境变量模板
- [ ] **T119** `backend/tests/test_config.py` - 测试生产环境配置
- [ ] **T120** `backend/app/config.py` - 完善生产环境配置
- [ ] **T121** `README.md` - 编写部署文档
- [ ] **T122** `DEPLOY.md` - 编写详细部署指南

---

## 附录：测试先行示例

### T1-T2 示例（配置管理）

**T1: 先写测试** - `backend/tests/test_config.py`
```python
def test_config_loads_from_env():
    """测试配置能从环境变量加载"""
    os.environ['DATABASE_URL'] = 'mysql://test'
    config = Config()
    assert config.DATABASE_URL == 'mysql://test'

def test_config_default_values():
    """测试配置有合理的默认值"""
    config = Config()
    assert config.FLASK_ENV == 'development'
```

**T2: 再写实现** - `backend/app/config.py`
```python
class Config:
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
```

---

**总计：122个原子任务**

---

*文档版本：v1.0*
*创建日期：2026-05-13*
*基于 plan.md v1.0*
