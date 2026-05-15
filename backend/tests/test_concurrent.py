"""
并发处理测试

测试对话服务在并发场景下的行为和性能优化
"""
import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

from app.services.conversation_service import ConversationService


class TestConcurrentProcessing:
    """并发处理测试"""

    def test_concurrent_reuses_llm_service_instance(self):
        """测试并发请求应该重用LLM服务实例而非重复创建"""
        # 记录LLM服务创建次数
        creation_count = {"count": 0}
        original_get_llm_service = None

        def mock_get_llm_service(*args, **kwargs):
            creation_count["count"] += 1
            # 返回mock服务
            mock_service = Mock()
            mock_service.chat = Mock(return_value={"content": "response"})
            mock_service.stream_chat = Mock(return_value=iter([{"content": "chunk"}]))
            return mock_service

        with patch('app.services.conversation_service.get_llm_service', side_effect=mock_get_llm_service):
            # 创建多个service实例（模拟多个并发请求）
            services = [ConversationService(provider_type="openai") for _ in range(5)]

            # 验证：理想情况下，LLM服务应该被重用，而不是创建5次
            # 这个测试会失败，因为当前实现每次都创建新的LLM服务
            assert creation_count["count"] <= 2, f"LLM service created {creation_count['count']} times, should be <= 2"

    def test_concurrent_chat_performance(self):
        """测试并发聊天请求的性能"""
        service = ConversationService(provider_type="openai")

        with patch.object(service, 'llm_service') as mock_llm:
            # 模拟API延迟
            def mock_chat(*args, **kwargs):
                time.sleep(0.1)
                return {"content": f"Response"}

            mock_llm.chat = mock_chat

            num_requests = 10

            # 测试顺序执行时间
            start = time.time()
            for _ in range(num_requests):
                service.chat([{"role": "user", "content": "test"}], "gpt-3.5")
            sequential_time = time.time() - start

            # 测试并发执行时间
            start = time.time()
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(service.chat, [{"role": "user", "content": "test"}], "gpt-3.5")
                    for _ in range(num_requests)
                ]
                for future in as_completed(futures):
                    future.result()
            concurrent_time = time.time() - start

            # 并发应该显著快于顺序执行
            # 这个测试会失败，因为当前实现没有优化并发性能
            speedup = sequential_time / concurrent_time
            assert speedup >= 2.5, f"Concurrent speedup is only {speedup:.2f}x, expected >= 2.5x"

    def test_concurrent_with_connection_pool(self):
        """测试并发请求使用连接池"""
        service = ConversationService(provider_type="openai")

        # 检查service是否有连接池配置
        # 这个测试会失败，因为当前实现没有连接池
        assert hasattr(service, 'connection_pool'), "Service should have connection pool"
        assert hasattr(service, 'max_connections'), "Service should have max_connections config"

    def test_concurrent_rate_limiting(self):
        """测试并发请求限流"""
        service = ConversationService(provider_type="openai")

        # 检查service是否有请求限流配置
        # 这个测试会失败，因为当前实现没有请求限流
        assert hasattr(service, 'rate_limiter'), "Service should have rate limiter"
        assert hasattr(service, 'max_concurrent_requests'), "Service should have max_concurrent_requests config"

    def test_concurrent_stream_isolation(self):
        """测试并发流式请求的隔离性"""
        service = ConversationService(provider_type="openai")

        with patch.object(service, 'llm_service') as mock_llm:
            def mock_stream_chat(messages, model, **kwargs):
                # 每个请求返回不同的内容以验证隔离
                msg_id = messages[0]['content']
                for i in range(3):
                    yield {"content": f"{msg_id}-chunk{i}"}

            mock_llm.stream_chat = mock_stream_chat

            def collect_stream(msg_id):
                chunks = []
                for chunk in service.stream_chat([{"role": "user", "content": msg_id}], "gpt-3.5"):
                    chunks.append(chunk)
                return chunks

            # 并发执行多个流式请求
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(collect_stream, f"msg{i}"): i
                    for i in range(5)
                }

                results = {}
                for future in as_completed(futures):
                    idx = futures[future]
                    results[idx] = future.result()

            # 验证每个流式请求的内容都是独立的
            for idx, chunks in results.items():
                expected_content = f"msg{idx}-chunk"
                for chunk in chunks:
                    assert chunk["content"].startswith(expected_content)

    def test_concurrent_error_does_not_block_other_requests(self):
        """测试一个请求的错误不应该阻塞其他并发请求"""
        service = ConversationService(provider_type="openai")

        with patch.object(service, 'llm_service') as mock_llm:
            request_count = {"count": 0}

            def mock_chat(*args, **kwargs):
                request_count["count"] += 1
                msg_content = args[0][0]['content']
                time.sleep(0.05)
                if "error" in msg_content:
                    raise ValueError(f"Error: {msg_content}")
                return {"content": f"OK: {msg_content}"}

            mock_llm.chat = mock_chat

            # 创建混合请求
            requests = [
                [{"role": "user", "content": "ok1"}],
                [{"role": "user", "content": "error"}],
                [{"role": "user", "content": "ok2"}],
                [{"role": "user", "content": "ok3"}],
            ]

            successful = 0
            errors = 0

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(service.chat, msg, "gpt-3.5")
                    for msg in requests
                ]

                for future in as_completed(futures):
                    try:
                        future.result()
                        successful += 1
                    except Exception:
                        errors += 1

            # 验证所有请求都被处理
            assert successful == 3, f"Expected 3 successful, got {successful}"
            assert errors == 1, f"Expected 1 error, got {errors}"
            assert request_count["count"] == 4, "All requests should be attempted"
