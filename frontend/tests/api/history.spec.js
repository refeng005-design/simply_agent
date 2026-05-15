/**
 * 历史API测试
 *
 * 测试对话历史相关的API调用：
 * - 获取对话列表
 * - 获取对话详情
 * - 删除对话
 * - 清空对话
 * - 导出对话
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'

// Mock apiClient
vi.mock('../../src/api/client.js', () => ({
  default: {
    get: vi.fn(),
    delete: vi.fn(),
    post: vi.fn()
  }
}))

describe('api/history.js - 历史API', () => {
  let apiClient
  let historyApi

  beforeEach(async () => {
    vi.clearAllMocks()

    // 动态导入以获取mock的apiClient
    const clientModule = await import('../../src/api/client.js')
    apiClient = clientModule.default

    // 导入history API模块
    const historyModule = await import('../../src/api/history.js')
    historyApi = historyModule.default
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('getConversations - 获取对话列表', () => {
    it('应该发送GET请求到/conversations端点', async () => {
      const mockResponse = {
        conversations: [
          {
            id: 'conv-1',
            title: 'First Chat',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T01:00:00Z',
            message_count: 10
          },
          {
            id: 'conv-2',
            title: 'Second Chat',
            created_at: '2024-01-02T00:00:00Z',
            updated_at: '2024-01-02T02:00:00Z',
            message_count: 5
          }
        ],
        total: 2,
        limit: 20,
        offset: 0
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await historyApi.getConversations()

      expect(apiClient.get).toHaveBeenCalledWith('/conversations?limit=20&offset=0')
      expect(response.conversations).toHaveLength(2)
      expect(response.total).toBe(2)
    })

    it('应该支持分页参数', async () => {
      const mockResponse = { conversations: [], total: 0, limit: 10, offset: 20 }
      apiClient.get.mockResolvedValue(mockResponse)

      await historyApi.getConversations(10, 20)

      expect(apiClient.get).toHaveBeenCalledWith('/conversations?limit=10&offset=20')
    })

    it('应该支持搜索参数', async () => {
      const mockResponse = { conversations: [], total: 0 }
      apiClient.get.mockResolvedValue(mockResponse)

      await historyApi.getConversations(20, 0, 'search query')

      expect(apiClient.get).toHaveBeenCalledWith('/conversations?limit=20&offset=0&search=search%20query')
    })

    it('应该处理空列表', async () => {
      const mockResponse = {
        conversations: [],
        total: 0,
        limit: 20,
        offset: 0
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await historyApi.getConversations()

      expect(response.conversations).toEqual([])
      expect(response.total).toBe(0)
    })
  })

  describe('getConversation - 获取对话详情', () => {
    it('应该发送GET请求到/conversations/:id端点', async () => {
      const mockResponse = {
        id: 'conv-123',
        title: 'My Conversation',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T01:00:00Z',
        model: 'gpt-3.5-turbo',
        provider: 'openai',
        messages: [
          { id: 'msg-1', role: 'user', content: 'Hello', created_at: '2024-01-01T00:00:00Z' },
          { id: 'msg-2', role: 'assistant', content: 'Hi', created_at: '2024-01-01T00:00:01Z' }
        ]
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await historyApi.getConversation('conv-123')

      expect(apiClient.get).toHaveBeenCalledWith('/conversations/conv-123')
      expect(response.id).toBe('conv-123')
      expect(response.messages).toHaveLength(2)
    })

    it('应该处理不存在的对话', async () => {
      const mockError = { message: 'Conversation not found' }
      apiClient.get.mockRejectedValue(mockError)

      await expect(historyApi.getConversation('nonexistent'))
        .rejects.toEqual(mockError)
    })
  })

  describe('deleteConversation - 删除对话', () => {
    it('应该发送DELETE请求到/conversations/:id端点', async () => {
      const mockResponse = {
        deleted: true,
        id: 'conv-123'
      }
      apiClient.delete.mockResolvedValue(mockResponse)

      const response = await historyApi.deleteConversation('conv-123')

      expect(apiClient.delete).toHaveBeenCalledWith('/conversations/conv-123')
      expect(response.deleted).toBe(true)
    })

    it('应该处理删除不存在的对话', async () => {
      const mockError = { message: 'Conversation not found' }
      apiClient.delete.mockRejectedValue(mockError)

      await expect(historyApi.deleteConversation('nonexistent'))
        .rejects.toEqual(mockError)
    })

    it('应该支持批量删除', async () => {
      const mockResponse = {
        deleted: true,
        count: 3
      }
      apiClient.delete.mockResolvedValue(mockResponse)

      const ids = ['conv-1', 'conv-2', 'conv-3']
      const response = await historyApi.deleteConversations(ids)

      expect(apiClient.delete).toHaveBeenCalledWith('/conversations/batch', {
        data: { ids }
      })
      expect(response.count).toBe(3)
    })
  })

  describe('clearConversation - 清空对话消息', () => {
    it('应该发送POST请求到/conversations/:id/clear端点', async () => {
      const mockResponse = {
        cleared: true,
        id: 'conv-123',
        message_count: 0
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const response = await historyApi.clearConversation('conv-123')

      expect(apiClient.post).toHaveBeenCalledWith('/conversations/conv-123/clear')
      expect(response.cleared).toBe(true)
    })

    it('应该处理清空不存在的对话', async () => {
      const mockError = { message: 'Conversation not found' }
      apiClient.post.mockRejectedValue(mockError)

      await expect(historyApi.clearConversation('nonexistent'))
        .rejects.toEqual(mockError)
    })
  })

  describe('updateConversationTitle - 更新对话标题', () => {
    it('应该发送PUT请求到/conversations/:id端点', async () => {
      const mockResponse = {
        id: 'conv-123',
        title: 'New Title',
        updated_at: '2024-01-01T02:00:00Z'
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const response = await historyApi.updateConversationTitle('conv-123', 'New Title')

      expect(apiClient.post).toHaveBeenCalledWith('/conversations/conv-123', {
        title: 'New Title'
      })
      expect(response.title).toBe('New Title')
    })

    it('应该拒绝空标题', async () => {
      const mockError = { message: 'Title cannot be empty' }
      apiClient.post.mockRejectedValue(mockError)

      await expect(historyApi.updateConversationTitle('conv-123', ''))
        .rejects.toEqual(mockError)
    })
  })

  describe('exportConversation - 导出对话', () => {
    it('应该发送GET请求到/conversations/:id/export端点', async () => {
      const mockResponse = {
        id: 'conv-123',
        format: 'json',
        content: {
          conversation: {
            id: 'conv-123',
            title: 'Export Test',
            messages: []
          }
        }
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await historyApi.exportConversation('conv-123', 'json')

      expect(apiClient.get).toHaveBeenCalledWith('/conversations/conv-123/export?format=json')
      expect(response.format).toBe('json')
    })

    it('应该支持markdown格式导出', async () => {
      const mockResponse = {
        id: 'conv-123',
        format: 'markdown',
        content: '# Export Test\n\n## User\nHello\n\n## Assistant\nHi'
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await historyApi.exportConversation('conv-123', 'markdown')

      expect(apiClient.get).toHaveBeenCalledWith('/conversations/conv-123/export?format=markdown')
      expect(response.format).toBe('markdown')
    })

    it('应该支持txt格式导出', async () => {
      const mockResponse = {
        id: 'conv-123',
        format: 'txt',
        content: 'Export Test\n\nUser: Hello\nAssistant: Hi'
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await historyApi.exportConversation('conv-123', 'txt')

      expect(apiClient.get).toHaveBeenCalledWith('/conversations/conv-123/export?format=txt')
    })
  })
})
