"""
Simply Agent 配置管理

支持从环境变量加载配置，提供开发/生产环境支持
"""
import os
import re
from urllib.parse import urlparse


class ProductionConfigError(Exception):
    """生产环境配置错误"""
    pass


class InvalidDatabaseURLError(Exception):
    """无效的数据库 URL"""
    pass


class Config:
    """应用配置基类"""

    def __init__(self):
        self.FLASK_ENV = os.getenv('FLASK_ENV', 'development')
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///simply_agent.db')
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.API_PORT = int(os.getenv('API_PORT', '5000'))

        # 验证数据库 URL 格式
        self._validate_database_url()

        # 根据环境设置默认值
        self._set_defaults()

    def _validate_database_url(self):
        """验证数据库 URL 格式"""
        valid_schemes = ['sqlite', 'mysql', 'postgresql', 'postgres']

        try:
            parsed = urlparse(self.DATABASE_URL)
            if not parsed.scheme or parsed.scheme not in valid_schemes:
                raise InvalidDatabaseURLError(
                    f"Invalid database URL scheme. Must be one of: {', '.join(valid_schemes)}"
                )
        except Exception as e:
            if isinstance(e, InvalidDatabaseURLError):
                raise
            raise InvalidDatabaseURLError(f"Invalid database URL format: {e}")

    def _set_defaults(self):
        """设置默认值（由子类覆盖）"""
        pass


class DevelopmentConfig(Config):
    """开发环境配置"""

    def _set_defaults(self):
        """设置开发环境默认值"""
        self.DEBUG = True
        self.DB_POOL_SIZE = 5
        self.DB_MAX_OVERFLOW = 10
        self.SESSION_COOKIE_SECURE = False
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = 'Lax'
        self.CORS_ENABLED = True
        self.CORS_ORIGINS = ['*']
        self.LOG_LEVEL = 'DEBUG'
        self.LOG_FILE = None  # 开发环境输出到控制台


class ProductionConfig(Config):
    """生产环境配置"""

    def __init__(self):
        super().__init__()
        # 生产环境验证
        self._validate_production_config()

    def _validate_production_config(self):
        """验证生产环境配置"""
        # 验证 SECRET_KEY 强度
        if len(self.SECRET_KEY) < 32:
            raise ProductionConfigError(
                f"SECRET_KEY must be at least 32 characters in production. "
                f"Current length: {len(self.SECRET_KEY)}"
            )

    def _set_defaults(self):
        """设置生产环境默认值"""
        self.DEBUG = False
        self.DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '20'))
        self.DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '40'))
        self.SESSION_COOKIE_SECURE = True
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
        self.CORS_ENABLED = os.getenv('CORS_ENABLED', 'true').lower() == 'true'
        self.CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', '/app/logs/app.log')


def get_config():
    """工厂函数：根据环境返回配置实例"""
    env = os.getenv('FLASK_ENV', 'development')

    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()


# 向后兼容：默认使用 DevelopmentConfig
Config = get_config
