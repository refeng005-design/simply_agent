"""
Flask应用工厂测试

测试应用创建函数能正确创建Flask应用实例
"""
import pytest


def test_create_app_returns_flask_app():
    """测试create_app返回Flask应用实例"""
    from app import create_app

    app = create_app()

    assert app is not None
    assert hasattr(app, 'test_client')
    assert app.name == 'app'


def test_create_app_with_test_config():
    """测试create_app能接受测试配置"""
    from app import create_app

    app = create_app({'TESTING': True, 'SECRET_KEY': 'test-key'})

    assert app.config['TESTING'] is True
    assert app.config['SECRET_KEY'] == 'test-key'


def test_create_app_registers_blueprints():
    """测试create_app注册了API蓝图"""
    from app import create_app

    app = create_app()

    # 检查api蓝图已注册
    assert 'api' in app.blueprints
    assert app.blueprints['api'] is not None


def test_create_app_default_config():
    """测试create_app使用默认配置"""
    from app import create_app
    from app.config import Config

    app = create_app()

    # 应用配置应与Config类一致
    config = Config()
    assert app.config['FLASK_ENV'] == config.FLASK_ENV
    assert app.config['SECRET_KEY'] == config.SECRET_KEY
