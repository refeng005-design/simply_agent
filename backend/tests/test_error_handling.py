"""
错误处理中间件测试

测试API统一的错误处理机制
"""
import pytest
import json
from flask import Flask
from unittest.mock import patch, Mock

from app import create_app
from app.api import api_bp


class TestErrorHandling:
    """错误处理测试"""

    def test_validation_error_returns_400(self):
        """测试验证错误返回400状态码"""
        app = create_app({'TESTING': True})

        # 添加一个会触发验证错误的测试路由
        @app.route('/test/validation')
        def test_validation():
            from app.api.errors import ValidationError
            raise ValidationError("Invalid input data")

        client = app.test_client()
        response = client.get('/test/validation')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Invalid input data'
        assert 'error_code' in data

    def test_not_found_error_returns_404(self):
        """测试404错误返回正确的格式"""
        app = create_app({'TESTING': True})

        # 添加一个会触发404错误的测试路由
        @app.route('/test/notfound')
        def test_not_found():
            from app.api.errors import NotFoundError
            raise NotFoundError("Resource not found")

        client = app.test_client()
        response = client.get('/test/notfound')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Resource not found'
        assert 'error_code' in data

    def test_internal_error_returns_500(self):
        """测试内部错误返回500状态码"""
        app = create_app({'TESTING': True})

        # 添加一个会触发内部错误的测试路由
        @app.route('/test/internal')
        def test_internal():
            raise Exception("Unexpected error")

        client = app.test_client()
        response = client.get('/test/internal')

        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert 'error_code' in data

    def test_authentication_error_returns_401(self):
        """测试认证错误返回401状态码"""
        app = create_app({'TESTING': True})

        # 添加一个会触发认证错误的测试路由
        @app.route('/test/auth')
        def test_auth():
            from app.api.errors import AuthenticationError
            raise AuthenticationError("Invalid credentials")

        client = app.test_client()
        response = client.get('/test/auth')

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid credentials'
        assert 'error_code' in data

    def test_permission_error_returns_403(self):
        """测试权限错误返回403状态码"""
        app = create_app({'TESTING': True})

        # 添加一个会触发权限错误的测试路由
        @app.route('/test/permission')
        def test_permission():
            from app.api.errors import PermissionError
            raise PermissionError("Access denied")

        client = app.test_client()
        response = client.get('/test/permission')

        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['error'] == 'Access denied'
        assert 'error_code' in data

    def test_rate_limit_error_returns_429(self):
        """测试限流错误返回429状态码"""
        app = create_app({'TESTING': True})

        # 添加一个会触发限流错误的测试路由
        @app.route('/test/ratelimit')
        def test_ratelimit():
            from app.api.errors import RateLimitError
            raise RateLimitError("Too many requests")

        client = app.test_client()
        response = client.get('/test/ratelimit')

        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['error'] == 'Too many requests'
        assert 'error_code' in data
        assert 'retry_after' in data

    def test_error_response_has_consistent_format(self):
        """测试错误响应具有一致的格式"""
        app = create_app({'TESTING': True})

        @app.route('/test/error')
        def test_error():
            raise ValueError("Test error")

        client = app.test_client()
        response = client.get('/test/error')

        data = json.loads(response.data)
        # 验证所有错误响应都包含必需字段
        assert 'error' in data
        assert 'error_code' in data
        assert 'timestamp' in data

    def test_error_is_logged(self):
        """测试错误被正确记录"""
        import logging
        from io import StringIO

        # 设置临时日志处理器捕获日志
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.ERROR)

        # 获取errors模块的logger并添加handler
        from app.api import errors
        errors.logger.addHandler(handler)

        try:
            app = create_app({'TESTING': True})

            @app.route('/test/log')
            def test_log():
                raise ValueError("Error to log")

            client = app.test_client()
            response = client.get('/test/log')

            # 验证日志被记录
            log_output = log_stream.getvalue()
            assert "Error to log" in log_output or "Unexpected error" in log_output
        finally:
            errors.logger.removeHandler(handler)

    def test_cors_headers_on_error(self):
        """测试错误响应包含CORS头"""
        app = create_app({'TESTING': True})

        @app.route('/test/cors')
        def test_cors():
            raise ValueError("Test error")

        client = app.test_client()
        response = client.get('/test/cors')

        # 验证CORS头存在
        # 这个测试会失败，因为当前实现没有CORS配置
        assert 'Access-Control-Allow-Origin' in response.headers
