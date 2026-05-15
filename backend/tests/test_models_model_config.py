"""
ModelConfig模型测试

测试LLM模型配置数据模型的字段和行为
"""
import pytest


def test_model_config_model_has_required_fields():
    """测试ModelConfig模型有必需的字段"""
    from app.models import ModelConfig

    columns = [column.name for column in ModelConfig.__table__.columns]

    assert 'id' in columns
    assert 'provider' in columns
    assert 'model_name' in columns
    assert 'api_key' in columns
    assert 'is_active' in columns


def test_model_config_model_can_be_created():
    """测试可以创建ModelConfig实例"""
    from app.models import ModelConfig

    config = ModelConfig(
        provider='openai',
        model_name='gpt-4',
        api_key='sk-test-key'
    )

    assert config.provider == 'openai'
    assert config.model_name == 'gpt-4'
    assert config.api_key == 'sk-test-key'


def test_model_config_model_has_default_is_active():
    """测试ModelConfig默认激活状态"""
    from app.models import ModelConfig

    config = ModelConfig(
        provider='anthropic',
        model_name='claude-3'
    )

    assert config.is_active is True


def test_model_config_model_supports_temperature():
    """测试ModelConfig支持温度参数"""
    from app.models import ModelConfig

    config = ModelConfig(
        provider='openai',
        model_name='gpt-4',
        temperature=0.7
    )

    assert config.temperature == 0.7


def test_model_config_model_supports_max_tokens():
    """测试ModelConfig支持最大token数"""
    from app.models import ModelConfig

    config = ModelConfig(
        provider='openai',
        model_name='gpt-4',
        max_tokens=4096
    )

    assert config.max_tokens == 4096


def test_model_config_model_string_representation():
    """测试ModelConfig模型的字符串表示"""
    from app.models import ModelConfig

    config = ModelConfig(
        provider='openai',
        model_name='gpt-4'
    )

    str_repr = str(config)

    assert 'openai' in str_repr or 'gpt-4' in str_repr


def test_model_config_model_supports_all_providers():
    """测试ModelConfig支持所有提供商"""
    from app.models import ModelConfig

    providers = ['openai', 'anthropic', 'qwen', 'ollama']

    for provider in providers:
        config = ModelConfig(
            provider=provider,
            model_name='test-model'
        )
        assert config.provider == provider
