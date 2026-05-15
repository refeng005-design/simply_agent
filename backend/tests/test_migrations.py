"""
数据库迁移测试

测试迁移文件的加载和执行
"""
import pytest
import os


def test_initial_migration_file_exists():
    """测试初始迁移文件存在"""
    migration_path = '/data/xyf/mypro/simply_agent/backend/migrations/001_initial.sql'

    assert os.path.exists(migration_path), f"Migration file not found: {migration_path}"


def test_initial_migration_creates_conversations_table():
    """测试初始迁移创建conversations表"""
    migration_path = '/data/xyf/mypro/simply_agent/backend/migrations/001_initial.sql'

    with open(migration_path, 'r') as f:
        content = f.read()

    assert 'CREATE TABLE' in content or 'create table' in content
    assert 'conversations' in content


def test_initial_migration_creates_messages_table():
    """测试初始迁移创建messages表"""
    migration_path = '/data/xyf/mypro/simply_agent/backend/migrations/001_initial.sql'

    with open(migration_path, 'r') as f:
        content = f.read()

    assert 'messages' in content


def test_initial_migration_creates_knowledge_entries_table():
    """测试初始迁移创建knowledge_entries表"""
    migration_path = '/data/xyf/mypro/simply_agent/backend/migrations/001_initial.sql'

    with open(migration_path, 'r') as f:
        content = f.read()

    assert 'knowledge_entries' in content


def test_initial_migration_creates_model_configs_table():
    """测试初始迁移创建model_configs表"""
    migration_path = '/data/xyf/mypro/simply_agent/backend/migrations/001_initial.sql'

    with open(migration_path, 'r') as f:
        content = f.read()

    assert 'model_configs' in content


def test_initial_migration_has_indexes():
    """测试初始迁移包含索引"""
    migration_path = '/data/xyf/mypro/simply_agent/backend/migrations/001_initial.sql'

    with open(migration_path, 'r') as f:
        content = f.read()

    # 检查是否有索引定义
    assert 'INDEX' in content or 'index' in content or 'KEY' in content


def test_initial_migration_has_foreign_keys():
    """测试初始迁移包含外键约束"""
    migration_path = '/data/xyf/mypro/simply_agent/backend/migrations/001_initial.sql'

    with open(migration_path, 'r') as f:
        content = f.read()

    # 检查是否有外键定义
    assert 'FOREIGN KEY' in content or 'foreign key' in content or 'REFERENCES' in content
