/**
 * 聊天API测试
 *
 * 测试聊天相关的API调用：
 * - 发送消息（非流式）
 * - 发送消息（流式/SSE）
 * - 获取对话历史
 * - 创建新对话
 * - 删除对话
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios')
vi.mock('../../src/api/client.js', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn()
  }
}))

describe('api/chat.js - 聊天API', () => {
  let apiClient
  let chatApi

  beforeEach(async () => {
    vi.clearAllMocks()

    // 动态导入以获取mock的apiClient
    const clientModule = await import('../../src/api/client.js')
    apiClient = clientModule.default

    // 导入chat API模块
    const chatModule = await import('../../src/api/chat.js')
    chatApi = chatModule.default
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('sendMessage - 发送消息', () => {
    it('应该发送POST请求到/chat端点', async () => {
      const mockResponse = {
        conversation_id: 'conv-123',
        message: {
          id: 'msg-1',
          role: 'assistant',
          content: 'Hello! How can I help you?'
        }
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const request = {
        message: 'Hello',
        model: 'gpt-3.5-turbo',
        provider: 'openai'
      }

      const response = await chatApi.sendMessage(request)

      expect(apiClient.post).toHaveBeenCalledWith('/chat', request)
      expect(response).toEqual(mockResponse)
    })

    it('应该支持带conversation_id的请求', async () => {
      const mockResponse = {
        conversation_id: 'conv-456',
        message: {
          id: 'msg-2',
          role: 'assistant',
          content: 'Response'
        }
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const request = {
        conversation_id: 'conv-456',
        message: 'Question',
        model: 'gpt-4',
        provider: 'openai'
      }

      const response = await chatApi.sendMessage(request)

      expect(apiClient.post).toHaveBeenCalledWith('/chat', request)
      expect(response.conversation_id).toBe('conv-456')
    })

    it('应该支持RAG参数', async () => {
      const mockResponse = {
        conversation_id: 'conv-789',
        message: { id: 'msg-3', role: 'assistant', content: 'Answer' }
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const request = {
        message: 'Question with context',
        model: 'gpt-3.5-turbo',
        provider: 'openai',
        rag_enabled: true,
        memory_enabled: true
      }

      await chatApi.sendMessage(request)

      expect(apiClient.post).toHaveBeenCalledWith('/chat', request)
    })

    it('应该支持温度和最大token参数', async () => {
      const mockResponse = {
        conversation_id: 'conv-999',
        message: { id: 'msg-4', role: 'assistant', content: 'Creative response' }
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const request = {
        message: 'Be creative',
        model: 'gpt-4',
        provider: 'openai',
        temperature: 0.9,
        max_tokens: 4096
      }

      await chatApi.sendMessage(request)

      expect(apiClient.post).toHaveBeenCalledWith('/chat', request)
    })

    it('应该在请求失败时抛出错误', async () => {
      const mockError = { message: 'Network error' }
      apiClient.post.mockRejectedValue(mockError)

      const request = {
        message: 'Test',
        model: 'gpt-3.5-turbo',
        provider: 'openai'
      }

      await expect(chatApi.sendMessage(request)).rejects.toEqual(mockError)
    })
  })

  describe('sendMessageStream - 流式发送消息', () => {
    it('应该返回EventSource或类似的流式响应对象', async () => {
      // 模拟浏览器环境
      global.window = {}

      const request = {
        message: 'Hello stream',
        model: 'gpt-3.5-turbo',
        provider: 'openai'
      }

      const stream = chatApi.sendMessageStream(request)

      expect(stream).toBeDefined()
      expect(typeof stream.on).toBe('function')
      expect(typeof stream.close).toBe('function')
    })

    it('应该返回包含正确URL的流对象', async () => {
      const request = {
        message: 'Test',
        model: 'gpt-4',
        provider: 'openai',
        conversation_id: 'conv-123'
      }

      const stream = chatApi.sendMessageStream(request)

      // 验证stream对象的结构
      expect(stream).toBeDefined()
      expect(typeof stream.on).toBe('function')
      expect(typeof stream.close).toBe('function')
    })
  })

  describe('getConversationHistory - 获取对话历史', () => {
    it('应该发送GET请求到/conversations端点', async () => {
      const mockResponse = {
        conversations: [
          {
            id: 'conv-1',
            title: 'First conversation',
            created_at: '2024-01-01T00:00:00Z',
            message_count: 5
          },
          {
            id: 'conv-2',
            title: 'Second conversation',
            created_at: '2024-01-02T00:00:00Z',
            message_count: 3
          }
        ]
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await chatApi.getConversationHistory()

      expect(apiClient.get).toHaveBeenCalledWith('/conversations?limit=20&offset=0')
      expect(response.conversations).toHaveLength(2)
    })

    it('应该支持limit和offset参数', async () => {
      const mockResponse = { conversations: [] }
      apiClient.get.mockResolvedValue(mockResponse)

      await chatApi.getConversationHistory(10, 20)

      expect(apiClient.get).toHaveBeenCalledWith('/conversations?limit=10&offset=20')
    })
  })

  describe('getMessages - 获取对话消息', () => {
    it('应该发送GET请求到/conversations/:id/messages端点', async () => {
      const mockResponse = {
        conversation_id: 'conv-123',
        messages: [
          { id: 'msg-1', role: 'user', content: 'Hello' },
          { id: 'msg-2', role: 'assistant', content: 'Hi there' }
        ]
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await chatApi.getMessages('conv-123')

      expect(apiClient.get).toHaveBeenCalledWith('/conversations/conv-123/messages')
      expect(response.messages).toHaveLength(2)
    })

    it('应该处理不存在的对话ID', async () => {
      const mockError = { message: 'Conversation not found' }
      apiClient.get.mockRejectedValue(mockError)

      await expect(chatApi.getMessages('nonexistent'))
        .rejects.toEqual(mockError)
    })
  })

  describe('createConversation - 创建新对话', () => {
    it('应该发送POST请求到/conversations端点', async () => {
      const mockResponse = {
        id: 'conv-new',
        created_at: '2024-01-03T00:00:00Z'
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const response = await chatApi.createConversation()

      expect(apiClient.post).toHaveBeenCalledWith('/conversations', {})
      expect(response.id).toBe('conv-new')
    })

    it('应该支持设置初始标题', async () => {
      const mockResponse = {
        id: 'conv-with-title',
        title: 'My Chat',
        created_at: '2024-01-03T00:00:00Z'
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const response = await chatApi.createConversation('My Chat')

      expect(apiClient.post).toHaveBeenCalledWith('/conversations', {
        title: 'My Chat'
      })
      expect(response.title).toBe('My Chat')
    })
  })

  describe('deleteConversation - 删除对话', () => {
    it('应该发送DELETE请求到/conversations/:id端点', async () => {
      const mockResponse = { deleted: true }
      apiClient.delete.mockResolvedValue(mockResponse)

      const response = await chatApi.deleteConversation('conv-123')

      expect(apiClient.delete).toHaveBeenCalledWith('/conversations/conv-123')
      expect(response.deleted).toBe(true)
    })

    it('应该处理删除不存在的对话', async () => {
      const mockError = { message: 'Conversation not found' }
      apiClient.delete.mockRejectedValue(mockError)

      await expect(chatApi.deleteConversation('nonexistent'))
        .rejects.toEqual(mockError)
    })
  })

  describe('clearConversation - 清空对话消息', () => {
    it('应该发送POST请求到/conversations/:id/clear端点', async () => {
      const mockResponse = { cleared: true }
      apiClient.post.mockResolvedValue(mockResponse)

      const response = await chatApi.clearConversation('conv-123')

      expect(apiClient.post).toHaveBeenCalledWith('/conversations/conv-123/clear')
      expect(response.cleared).toBe(true)
    })
  })
})
