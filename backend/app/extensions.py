"""
Simply Agent Backend - 数据库扩展

初始化SQLAlchemy和其他扩展
"""
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import threading
import os


# 数据库元数据
metadata = MetaData(
    naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)


# 声明式基类
Model = declarative_base(metadata=metadata)


class SQLAlchemy:
    """简化的SQLAlchemy包装类"""

    def __init__(self):
        self.metadata = metadata
        self._session_factory = None
        self._scoped_session = None
        self._engine = None
        self._app = None
        self._lock = threading.Lock()

        # 内存存储（fallback）
        self._conversations = {}
        self._messages = {}
        self._conversation_counter = 0
        self._message_counter = 0

    def init_app(self, app):
        """初始化Flask应用"""
        self._app = app

        # 获取数据库URL
        database_url = app.config.get('DATABASE_URL', 'sqlite:///simply_agent.db')

        try:
            # 创建引擎
            self._engine = create_engine(
                database_url,
                echo=False,
                connect_args={'check_same_thread': False} if database_url.startswith('sqlite') else {}
            )

            # 创建会话工厂
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )

            # 创建作用域会话
            self._scoped_session = scoped_session(self._session_factory)

            # 将db实例注册到app扩展
            if not hasattr(app, 'extensions'):
                app.extensions = {}
            app.extensions['sqlalchemy'] = {
                'db': self,
                'metadata': self.metadata
            }

            # 创建所有表
            self.create_all()

        except Exception as e:
            print(f"Database initialization failed: {e}")
            print("Using in-memory storage instead")
            self._engine = None

    @property
    def session(self):
        """获取会话"""
        if self._scoped_session is not None:
            return self._scoped_session()

        # 返回内存会话
        class InMemorySession:
            def __init__(self, db):
                self.db = db
                self._pending_additions = []

            def add(self, item):
                self._pending_additions.append(item)

            def commit(self):
                for item in self._pending_additions:
                    if hasattr(item, '_save_to_memory'):
                        item._save_to_memory(self.db)
                self._pending_additions.clear()

            def rollback(self):
                self._pending_additions.clear()

            def close(self):
                pass

            def query(self, model):
                return InMemoryQuery(self.db, model)

        return InMemorySession(self)

    def create_all(self):
        """创建所有表"""
        if self._engine is not None:
            try:
                # 导入所有模型
                from app.models import Conversation, Message

                # 创建表
                Model.metadata.create_all(self._engine)
                print("Database tables created successfully")
            except Exception as e:
                print(f"Failed to create tables: {e}")

    def drop_all(self):
        """删除所有表"""
        if self._engine is not None:
            Model.metadata.drop_all(self._engine)


class InMemoryQuery:
    """内存查询模拟"""

    def __init__(self, db, model):
        self.db = db
        self.model = model
        self._filters = []
        self._order_clauses = []
        self._limit_val = None
        self._offset_val = 0

    def filter_by(self, **kwargs):
        """添加过滤条件"""
        self._filters.append(kwargs)
        return self

    def order_by(self, clause):
        """添加排序"""
        self._order_clauses.append(clause)
        return self

    def limit(self, val):
        """限制结果数量"""
        self._limit_val = val
        return self

    def offset(self, val):
        """设置偏移量"""
        self._offset_val = val
        return self

    def get(self, id):
        """获取单个对象"""
        if self.model.__name__ == 'Conversation':
            return self.db._conversations.get(str(id))
        elif self.model.__name__ == 'Message':
            for msg in self.db._messages.values():
                if msg.id == str(id):
                    return msg
        return None

    def all(self):
        """获取所有结果"""
        if self.model.__name__ == 'Conversation':
            results = list(self.db._conversations.values())
        elif self.model.__name__ == 'Message':
            results = list(self.db._messages.values())
        else:
            results = []

        # 应用过滤
        for filter_dict in self._filters:
            new_results = []
            for item in results:
                match = True
                for key, val in filter_dict.items():
                    if getattr(item, key, None) != val:
                        match = False
                        break
                if match:
                    new_results.append(item)
            results = new_results

        # 应用排序
        for clause in reversed(self._order_clauses):
            if hasattr(clause, 'desc'):
                # 降序
                results.sort(key=lambda x: getattr(x, clause._entity_name, ''), reverse=True)
            else:
                results.sort(key=lambda x: getattr(x, clause._entity_name, ''))

        # 应用偏移和限制
        if self._offset_val:
            results = results[self._offset_val:]
        if self._limit_val:
            results = results[:self._limit_val]

        return results

    def delete(self):
        """删除所有匹配的记录"""
        if self.model.__name__ == 'Conversation':
            self.db._conversations.clear()
        elif self.model.__name__ == 'Message':
            self.db._messages.clear()
        return self


# 创建db实例
db = SQLAlchemy()
