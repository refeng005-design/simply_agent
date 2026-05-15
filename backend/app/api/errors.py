"""
统一错误处理模块

定义自定义异常类和错误处理中间件
"""
import logging
from datetime import datetime
from flask import jsonify
from werkzeug.exceptions import HTTPException


logger = logging.getLogger(__name__)


# 自定义异常类
class APIError(Exception):
    """API基础异常类"""

    status_code = 500
    error_code = "API_ERROR"

    def __init__(self, message, status_code=None, error_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.payload = payload or {}

    def to_dict(self):
        """转换为字典格式"""
        result = {
            "error": self.message,
            "error_code": self.error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        result.update(self.payload)
        return result


class ValidationError(APIError):
    """验证错误 (400)"""

    status_code = 400
    error_code = "VALIDATION_ERROR"


class NotFoundError(APIError):
    """资源未找到错误 (404)"""

    status_code = 404
    error_code = "NOT_FOUND"


class AuthenticationError(APIError):
    """认证错误 (401)"""

    status_code = 401
    error_code = "AUTHENTICATION_ERROR"


class PermissionError(APIError):
    """权限错误 (403)"""

    status_code = 403
    error_code = "PERMISSION_ERROR"


class RateLimitError(APIError):
    """限流错误 (429)"""

    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"

    def __init__(self, message, retry_after=60):
        super().__init__(message)
        self.payload = {"retry_after": retry_after}


class ExternalServiceError(APIError):
    """外部服务错误 (502)"""

    status_code = 502
    error_code = "EXTERNAL_SERVICE_ERROR"


def init_error_handlers(app):
    """
    初始化错误处理器

    为Flask应用注册统一的错误处理
    """

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """处理自定义API错误"""
        logger.error(f"API Error: {error.error_code} - {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code

        # 添加CORS头
        response.headers['Access-Control-Allow-Origin'] = '*'

        # 添加重试头（针对限流错误）
        if isinstance(error, RateLimitError):
            response.headers['Retry-After'] = str(error.payload.get('retry_after', 60))

        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """处理HTTP异常"""
        logger.warning(f"HTTP Error: {error.code} - {error.name}")
        response = jsonify({
            "error": error.name,
            "error_code": f"HTTP_{error.code}",
            "timestamp": datetime.utcnow().isoformat()
        })
        response.status_code = error.code
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """处理未预期的错误"""
        logger.exception(f"Unexpected error: {str(error)}")
        response = jsonify({
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        })
        response.status_code = 500
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
