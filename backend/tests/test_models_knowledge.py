"""
KnowledgeEntry模型测试

测试知识库条目数据模型的字段和行为
"""
import pytest


def test_knowledge_entry_model_has_required_fields():
    """测试KnowledgeEntry模型有必需的字段"""
    from app.models import KnowledgeEntry

    columns = [column.name for column in KnowledgeEntry.__table__.columns]

    assert 'id' in columns
    assert 'title' in columns
    assert 'content' in columns
    assert 'source' in columns
    assert 'created_at' in columns


def test_knowledge_entry_model_can_be_created():
    """测试可以创建KnowledgeEntry实例"""
    from app.models import KnowledgeEntry

    entry = KnowledgeEntry(
        title='Test Entry',
        content='Test content',
        source='user'
    )

    assert entry.title == 'Test Entry'
    assert entry.content == 'Test content'
    assert entry.source == 'user'


def test_knowledge_entry_model_has_default_source():
    """测试KnowledgeEntry有默认来源"""
    from app.models import KnowledgeEntry

    entry = KnowledgeEntry(title='Test', content='Content')

    assert entry.source == 'manual'


def test_knowledge_entry_model_supports_metadata():
    """测试KnowledgeEntry支持元数据"""
    from app.models import KnowledgeEntry

    entry = KnowledgeEntry(
        title='Test',
        content='Content',
        metadata={'key': 'value', 'tags': ['test']}
    )

    assert entry.metadata == {'key': 'value', 'tags': ['test']}


def test_knowledge_entry_model_string_representation():
    """测试KnowledgeEntry模型的字符串表示"""
    from app.models import KnowledgeEntry

    entry = KnowledgeEntry(title='My Knowledge', content='Some content')

    str_repr = str(entry)

    assert 'My Knowledge' in str_repr


def test_knowledge_entry_model_has_embedding_field():
    """测试KnowledgeEntry有向量嵌入字段"""
    from app.models import KnowledgeEntry

    entry = KnowledgeEntry(title='Test', content='Content')

    assert hasattr(entry, 'embedding')
    # 嵌入应该是列表或None
    assert entry.embedding is None or isinstance(entry.embedding, list)


def test_knowledge_entry_model_can_store_embedding():
    """测试KnowledgeEntry可以存储向量嵌入"""
    from app.models import KnowledgeEntry

    embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

    entry = KnowledgeEntry(
        title='Test',
        content='Content',
        embedding=embedding
    )

    assert entry.embedding == embedding
    assert len(entry.embedding) == 5
