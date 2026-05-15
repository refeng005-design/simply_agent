"""
配置管理测试

测试配置类能正确从环境变量加载并提供合理的默认值
"""
import os
import pytest


def test_config_loads_from_env():
    """测试配置能从环境变量加载"""
    # 设置环境变量
    os.environ['DATABASE_URL'] = 'mysql://test:3306/db'
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'test-secret-key-that-is-long-enough'  # 至少32字符
    os.environ['API_PORT'] = '8080'

    # 导入配置（需要在设置环境变量后导入）
    from app.config import Config

    config = Config()

    assert config.DATABASE_URL == 'mysql://test:3306/db'
    assert config.FLASK_ENV == 'production'
    assert config.SECRET_KEY == 'test-secret-key-that-is-long-enough'
    assert config.API_PORT == 8080

    # 清理环境变量
    del os.environ['DATABASE_URL']
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']
    del os.environ['API_PORT']


def test_config_default_values():
    """测试配置有合理的默认值"""
    # 清除可能存在的环境变量
    for key in ['DATABASE_URL', 'FLASK_ENV', 'SECRET_KEY', 'API_PORT']:
        os.environ.pop(key, None)

    # 重新导入配置以获取默认值
    import importlib
    import app.config
    importlib.reload(app.config)
    from app.config import Config

    config = Config()

    assert config.FLASK_ENV == 'development'
    assert config.DATABASE_URL == 'sqlite:///simply_agent.db'
    assert config.SECRET_KEY == 'dev-secret-key-change-in-production'
    assert config.API_PORT == 5000  # 现在是整数类型


def test_config_is_immutable_after_creation():
    """测试配置在创建后不应该被修改"""
    from app.config import Config

    config = Config()

    # 尝试修改配置应该失败或创建新实例
    original_env = config.FLASK_ENV

    # 获取新实例应该是独立的
    new_config = Config()
    assert new_config.FLASK_ENV == original_env


# ==================== 生产环境配置测试 ====================

def test_production_config_requires_strong_secret_key():
    """测试生产环境要求强密钥"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'weak'  # 弱密钥

    from app.config import Config, ProductionConfigError

    # 生产环境使用弱密钥应该抛出异常
    with pytest.raises(ProductionConfigError, match="SECRET_KEY must be at least 32 characters"):
        config = Config()

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']


def test_production_config_has_debug_disabled():
    """测试生产环境 DEBUG 必须为 False"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'a' * 32  # 足够长的密钥

    from app.config import Config

    config = Config()

    assert config.DEBUG is False

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']


def test_production_config_has_database_pool_settings():
    """测试生产环境有数据库连接池配置"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'a' * 32

    from app.config import Config

    config = Config()

    # 生产环境应该有连接池配置
    assert hasattr(config, 'DB_POOL_SIZE')
    assert config.DB_POOL_SIZE >= 5
    assert hasattr(config, 'DB_MAX_OVERFLOW')
    assert config.DB_MAX_OVERFLOW >= 10

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']


def test_production_config_has_session_security():
    """测试生产环境有会话安全配置"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'a' * 32

    from app.config import Config

    config = Config()

    # 生产环境应该启用会话安全
    assert hasattr(config, 'SESSION_COOKIE_SECURE')
    assert config.SESSION_COOKIE_SECURE is True
    assert hasattr(config, 'SESSION_COOKIE_HTTPONLY')
    assert config.SESSION_COOKIE_HTTPONLY is True
    assert hasattr(config, 'SESSION_COOKIE_SAMESITE')
    assert config.SESSION_COOKIE_SAMESITE in ['Lax', 'Strict']

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']


def test_production_config_has_cors_settings():
    """测试生产环境有 CORS 配置"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'a' * 32

    from app.config import Config

    config = Config()

    # 生产环境应该有 CORS 配置
    assert hasattr(config, 'CORS_ENABLED')
    assert isinstance(config.CORS_ENABLED, bool)
    assert hasattr(config, 'CORS_ORIGINS')
    assert isinstance(config.CORS_ORIGINS, list)

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']


def test_production_config_has_logging_settings():
    """测试生产环境有日志配置"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'a' * 32

    from app.config import Config

    config = Config()

    # 生产环境应该有日志配置
    assert hasattr(config, 'LOG_LEVEL')
    assert config.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    assert hasattr(config, 'LOG_FILE')
    assert config.LOG_FILE is not None

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']


def test_development_config_allows_weak_secret_key():
    """测试开发环境允许使用弱密钥"""
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'dev-key'

    from app.config import Config

    # 开发环境不应该抛出异常
    config = Config()
    assert config.SECRET_KEY == 'dev-key'

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']


def test_development_config_has_debug_enabled():
    """测试开发环境 DEBUG 默认为 True"""
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'dev-key'

    from app.config import Config

    config = Config()

    assert config.DEBUG is True

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']


def test_config_validates_database_url_format():
    """测试配置验证数据库 URL 格式"""
    from app.config import Config, InvalidDatabaseURLError

    # 无效的数据库 URL
    os.environ['DATABASE_URL'] = 'invalid-database-url'

    with pytest.raises(InvalidDatabaseURLError):
        config = Config()

    # 清理
    del os.environ['DATABASE_URL']


def test_config_supports_environment_specific_settings():
    """测试配置支持环境特定的设置"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'a' * 32

    from app.config import Config

    config = Config()

    # 生产环境应该有特定的配置类
    assert config.__class__.__name__ == 'ProductionConfig'

    # 清理
    del os.environ['FLASK_ENV']
    del os.environ['SECRET_KEY']
