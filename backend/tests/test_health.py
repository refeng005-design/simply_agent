"""
健康检查API测试

测试健康检查端点返回正确的状态和信息
"""
import pytest


def test_health_check_returns_200():
    """测试健康检查返回200状态码"""
    from app import create_app

    app = create_app()
    client = app.test_client()

    response = client.get('/api/health')

    assert response.status_code == 200


def test_health_check_returns_json():
    """测试健康检查返回JSON数据"""
    from app import create_app

    app = create_app()
    client = app.test_client()

    response = client.get('/api/health')

    assert response.content_type == 'application/json'


def test_health_check_contains_status():
    """测试健康检查响应包含status字段"""
    from app import create_app

    app = create_app()
    client = app.test_client()

    response = client.get('/api/health')
    data = response.get_json()

    assert 'status' in data
    assert data['status'] == 'healthy'


def test_health_check_contains_version():
    """测试健康检查响应包含version字段"""
    from app import create_app

    app = create_app()
    client = app.test_client()

    response = client.get('/api/health')
    data = response.get_json()

    assert 'version' in data
    assert isinstance(data['version'], str)
