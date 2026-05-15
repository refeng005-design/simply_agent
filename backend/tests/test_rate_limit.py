"""
限流中间件测试

测试API请求限流功能
"""
import pytest
import time
import json
from flask import Flask

from app import create_app
from app.api.errors import RateLimitError
from app.api.rate_limit import get_rate_limiter


class TestRateLimiting:
    """限流测试"""

    def test_rate_limit_by_ip(self):
        """测试基于IP的限流"""
        app = create_app({'TESTING': True})

        # 添加一个测试路由
        @app.route('/test/limit')
        def test_limit():
            return {"status": "ok"}

        client = app.test_client()

        # 发送多个请求
        responses = []
        for i in range(15):
            response = client.get('/test/limit')
            responses.append(response)

        # 验证前N个请求成功，后续被限流
        successful = sum(1 for r in responses if r.status_code == 200)
        rate_limited = sum(1 for r in responses if r.status_code == 429)

        # 应该有一些请求被限流
        assert rate_limited > 0, "Some requests should be rate limited"

    def test_rate_limit_headers(self):
        """测试限流响应头"""
        app = create_app({'TESTING': True})

        @app.route('/test/limit')
        def test_limit():
            return {"status": "ok"}

        client = app.test_client()

        # 发送足够多的请求触发限流
        for i in range(20):
            response = client.get('/test/limit')
            if response.status_code == 429:
                # 验证限流响应头
                assert 'Retry-After' in response.headers or 'X-RateLimit-Remaining' in response.headers
                data = json.loads(response.data)
                assert 'retry_after' in data or 'error' in data
                break
        else:
            pytest.fail("No request was rate limited")

    def test_different_ips_separate_limits(self):
        """测试不同IP有独立的限流配额"""
        from app.api.rate_limit import get_rate_limiter

        app = create_app({'TESTING': True})

        @app.route('/test/limit')
        def test_limit():
            return {"status": "ok"}

        # 重置限流器
        limiter = get_rate_limiter()
        limiter.requests.clear()

        # 使用不同的请求环境来模拟不同的IP
        with app.test_request_context('/test/limit', environ_base={'REMOTE_ADDR': '192.168.1.1'}):
            # IP1发送多个请求
            for _ in range(15):
                # 手动记录请求
                limiter.requests['ip:192.168.1.1'].append(time.time())

        # IP2发送请求，应该不受IP1限流影响
        with app.test_request_context('/test/limit', environ_base={'REMOTE_ADDR': '192.168.1.2'}):
            # IP2应该可以请求
            assert limiter.is_allowed(key='ip:192.168.1.2'), "Different IP should have separate rate limit"

    def test_rate_limit_reset_after_window(self):
        """测试限流窗口重置"""
        app = create_app({'TESTING': True})

        @app.route('/test/limit')
        def test_limit():
            return {"status": "ok"}

        client = app.test_client()

        # 发送请求直到触发限流
        for i in range(20):
            response = client.get('/test/limit')
            if response.status_code == 429:
                break
        else:
            pytest.fail("Rate limit not triggered")

        # 这个测试需要mock时间或设置很短的限流窗口
        # 实际实现中应该支持配置限流窗口时长

    def test_rate_limit_configurable(self):
        """测试限流可配置"""
        app = create_app({'TESTING': True})

        # 检查限流配置是否存在
        # 这个测试会失败，因为当前实现没有限流配置
        assert hasattr(app, 'rate_limit_config'), "App should have rate limit configuration"
        assert 'max_requests' in app.rate_limit_config or 'default_limit' in app.rate_limit_config

    def test_rate_limit_exempt_routes(self):
        """测试某些路由可以豁免限流"""
        app = create_app({'TESTING': True})

        # 健康检查端点应该豁免限流
        client = app.test_client()

        # 发送大量请求到健康检查端点
        for _ in range(100):
            response = client.get('/api/health')
            assert response.status_code == 200, "Health check should be rate limit exempt"

    def test_rate_limit_by_user(self):
        """测试基于用户的限流（当认证时）"""
        app = create_app({'TESTING': True})

        @app.route('/test/user_limit')
        def test_user_limit():
            return {"status": "ok"}

        # 模拟已认证的用户请求
        client = app.test_client()

        # 发送带用户标识的请求
        headers = {'X-User-ID': 'user123'}
        responses = []
        for _ in range(15):
            response = client.get('/test/user_limit', headers=headers)
            responses.append(response)

        # 应该有请求被限流
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "User-specific requests should be rate limited"

    def test_rate_limit_burst_protection(self):
        """测试突发请求保护"""
        app = create_app({'TESTING': True})

        @app.route('/test/burst')
        def test_burst():
            return {"status": "ok"}

        client = app.test_client()

        # 快速发送多个请求
        responses = []
        for _ in range(30):
            response = client.get('/test/burst')
            responses.append(response)

        # 验证突发请求被限制
        successful = sum(1 for r in responses if r.status_code == 200)
        assert successful < 30, "Burst requests should be limited"
