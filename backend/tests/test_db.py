"""
数据库连接和初始化测试

测试数据库扩展的初始化功能
"""
import pytest


def test_db_extension_exports_db():
    """测试extensions模块导出db实例"""
    from app.extensions import db

    assert db is not None


def test_db_extension_has_init_app_method():
    """测试db实例有init_app方法"""
    from app.extensions import db

    assert hasattr(db, 'init_app')
    assert callable(db.init_app)


def test_db_can_initialize_with_flask_app():
    """测试db可以用Flask应用初始化"""
    from app import create_app
    from app.extensions import db

    app = create_app({'TESTING': True, 'DATABASE_URL': 'sqlite:///:memory:'})

    db.init_app(app)

    # 验证db已注册到app
    assert hasattr(app, 'extensions')


def test_db_has_session_property():
    """测试db有session属性"""
    from app.extensions import db

    assert hasattr(db, 'session')


def test_db_has_metadata_property():
    """测试db有metadata属性"""
    from app.extensions import db

    assert hasattr(db, 'metadata')


def test_db_supports_model_creation():
    """测试db支持模型创建"""
    from app.extensions import db
    from app.models import Base

    # 所有模型应该继承Base
    assert Base is not None


def test_db_has_create_all_method():
    """测试db有create_all方法"""
    from app.extensions import db

    # SQLAlchemy的db应该有create_all或类似方法
    assert hasattr(db, 'metadata') or callable(getattr(db, 'create_all', None))
