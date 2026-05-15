"""
限流中间件

提供基于IP和用户的请求限流功能
"""
import time
from collections import defaultdict
from functools import wraps
from flask import request, g
from app.api.errors import RateLimitError


class RateLimiter:
    """
    限流器

    使用滑动窗口算法实现请求限流
    """

    def __init__(self, default_limit=10, default_window=60):
        """
        初始化限流器

        Args:
            default_limit: 默认请求数限制
            default_window: 默认时间窗口（秒）
        """
        self.default_limit = default_limit
        self.default_window = default_window
        self.requests = defaultdict(list)  # {key: [timestamp1, timestamp2, ...]}
        self.exempt_routes = {'/api/health'}

    def _get_key(self):
        """获取限流键（IP或用户ID）"""
        # 优先使用用户ID（如果已认证）
        if hasattr(g, 'user_id') and g.user_id:
            return f"user:{g.user_id}"

        # 否则使用IP地址
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        else:
            ip = request.remote_addr or 'unknown'
        return f"ip:{ip}"

    def _clean_old_requests(self, key, window):
        """清理时间窗口外的旧请求记录"""
        now = time.time()
        self.requests[key] = [
            ts for ts in self.requests[key]
            if now - ts < window
        ]

    def is_allowed(self, key=None, limit=None, window=None):
        """
        检查请求是否允许

        Args:
            key: 限流键（默认自动获取）
            limit: 请求限制（默认使用default_limit）
            window: 时间窗口（默认使用default_window）

        Returns:
            bool: 是否允许请求
        """
        if key is None:
            key = self._get_key()
        if limit is None:
            limit = self.default_limit
        if window is None:
            window = self.default_window

        # 清理旧记录
        self._clean_old_requests(key, window)

        # 检查是否超过限制
        if len(self.requests[key]) >= limit:
            return False

        # 记录本次请求
        self.requests[key].append(time.time())
        return True

    def get_remaining(self, key=None, limit=None, window=None):
        """
        获取剩余可用请求数

        Args:
            key: 限流键（默认自动获取）
            limit: 请求限制
            window: 时间窗口

        Returns:
            int: 剩余请求数
        """
        if key is None:
            key = self._get_key()
        if limit is None:
            limit = self.default_limit
        if window is None:
            window = self.default_window

        self._clean_old_requests(key, window)
        return max(0, limit - len(self.requests[key]))

    def reset(self, key=None):
        """重置限流计数"""
        if key is None:
            key = self._get_key()
        if key in self.requests:
            del self.requests[key]


# 全局限流器实例
_rate_limiter = None


def get_rate_limiter():
    """获取全局限流器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(default_limit=10, default_window=60)
    return _rate_limiter


def rate_limit(limit=None, window=None, exempt=False):
    """
    限流装饰器

    Args:
        limit: 请求限制（可选）
        window: 时间窗口（可选）
        exempt: 是否豁免限流

    Usage:
        @app.route('/api/test')
        @rate_limit(limit=100, window=60)
        def test():
            return jsonify({'status': 'ok'})
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # 检查路由是否豁免
            if exempt:
                return f(*args, **kwargs)

            # 检查是否在豁免列表中
            if request.path in get_rate_limiter().exempt_routes:
                return f(*args, **kwargs)

            # 检查限流
            limiter = get_rate_limiter()
            if not limiter.is_allowed(limit=limit, window=window):
                remaining = 0
                retry_after = window or limiter.default_window
                raise RateLimitError(
                    "Rate limit exceeded",
                    retry_after=retry_after
                )

            # 添加限流响应头
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                remaining = limiter.get_remaining(limit=limit, window=window)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Limit'] = str(limit or limiter.default_limit)

            return response

        return wrapped

    return decorator


def init_rate_limiting(app):
    """
    初始化应用限流配置

    Args:
        app: Flask应用实例
    """
    # 设置限流配置
    app.rate_limit_config = {
        'default_limit': 10,
        'default_window': 60,
        'burst_limit': 20
    }

    # 添加before_request处理全局限流
    @app.before_request
    def check_rate_limit():
        """在每个请求前检查限流"""
        if request.path in get_rate_limiter().exempt_routes:
            return None

        limiter = get_rate_limiter()
        if not limiter.is_allowed():
            retry_after = limiter.default_window
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=retry_after
            )

        # 存储限流信息供后续使用
        g.rate_limit_remaining = limiter.get_remaining()

    # 添加after_request处理响应头
    @app.after_request
    def add_rate_limit_headers(response):
        """添加限流响应头"""
        if hasattr(g, 'rate_limit_remaining'):
            limiter = get_rate_limiter()
            response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
            response.headers['X-RateLimit-Limit'] = str(limiter.default_limit)
            response.headers['X-RateLimit-Reset'] = str(int(time.time()) + limiter.default_window)

        return response
