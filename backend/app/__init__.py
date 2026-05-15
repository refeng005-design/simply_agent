"""
Simply Agent Backend Application

Flask应用工厂模块
"""
from flask import Flask
from .config import Config


def create_app(config_override=None):
    """
    创建Flask应用实例

    Args:
        config_override: 可选的配置字典，用于测试环境

    Returns:
        Flask应用实例
    """
    app = Flask(__name__)

    # 加载默认配置
    config = Config()
    app.config['FLASK_ENV'] = config.FLASK_ENV
    app.config['DATABASE_URL'] = config.DATABASE_URL
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['API_PORT'] = config.API_PORT

    # 应用覆盖配置（主要用于测试）
    if config_override:
        app.config.update(config_override)

    # 注册蓝图和错误处理
    from .api import register_blueprints
    register_blueprints(app)

    # 初始化数据库
    from .extensions import db
    db.init_app(app)

    return app
