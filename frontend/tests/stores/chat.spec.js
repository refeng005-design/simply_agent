/**
 * 聊天状态管理测试
 *
 * 测试聊天store的核心功能：
 * - 消息列表管理
 * - 当前对话状态
 * - 发送消息状态
 * - 流式响应处理
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useChatStore } from '@/stores/chat.js'

describe('Chat Store - 聊天状态管理', () => {
  beforeEach(() => {
    // 每个测试前创建新的pinia实例
    setActivePinia(createPinia())
    // 清除所有mock
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该有空的当前对话ID', () => {
      const store = useChatStore()
      expect(store.currentConversationId).toBeNull()
    })

    it('应该有空的消息列表', () => {
      const store = useChatStore()
      expect(store.messages).toEqual([])
    })

    it('应该处于空闲状态', () => {
      const store = useChatStore()
      expect(store.isLoading).toBe(false)
      expect(store.isStreaming).toBe(false)
    })

    it('应该有空的输入内容', () => {
      const store = useChatStore()
      expect(store.input).toBe('')
    })
  })

  describe('消息管理', () => {
    it('应该添加用户消息', () => {
      const store = useChatStore()
      const userMessage = {
        id: 'msg-1',
        role: 'user',
        content: 'Hello'
      }

      store.addMessage(userMessage)

      expect(store.messages).toHaveLength(1)
      expect(store.messages[0]).toEqual(userMessage)
    })

    it('应该添加助手消息', () => {
      const store = useChatStore()
      const assistantMessage = {
        id: 'msg-2',
        role: 'assistant',
        content: 'Hi there'
      }

      store.addMessage(assistantMessage)

      expect(store.messages).toHaveLength(1)
      expect(store.messages[0]).toEqual(assistantMessage)
    })

    it('应该按顺序添加多条消息', () => {
      const store = useChatStore()

      store.addMessage({ id: '1', role: 'user', content: 'First' })
      store.addMessage({ id: '2', role: 'assistant', content: 'Response' })
      store.addMessage({ id: '3', role: 'user', content: 'Second' })

      expect(store.messages).toHaveLength(3)
      expect(store.messages[0].content).toBe('First')
      expect(store.messages[1].content).toBe('Response')
      expect(store.messages[2].content).toBe('Second')
    })

    it('应该清空消息列表', () => {
      const store = useChatStore()

      store.addMessage({ id: '1', role: 'user', content: 'Test' })
      expect(store.messages).toHaveLength(1)

      store.clearMessages()
      expect(store.messages).toEqual([])
    })

    it('应该删除指定消息', () => {
      const store = useChatStore()

      store.addMessage({ id: '1', role: 'user', content: 'First' })
      store.addMessage({ id: '2', role: 'assistant', content: 'Response' })
      store.addMessage({ id: '3', role: 'user', content: 'Second' })

      store.deleteMessage('2')

      expect(store.messages).toHaveLength(2)
      expect(store.messages.find(m => m.id === '2')).toBeUndefined()
    })
  })

  describe('对话管理', () => {
    it('应该设置当前对话ID', () => {
      const store = useChatStore()

      store.setCurrentConversation('conv-123')

      expect(store.currentConversationId).toBe('conv-123')
    })

    it('应该清空当前对话ID', () => {
      const store = useChatStore()
      store.setCurrentConversation('conv-123')

      store.clearCurrentConversation()

      expect(store.currentConversationId).toBeNull()
    })

    it('应该加载对话历史', () => {
      const store = useChatStore()
      const history = [
        { id: '1', role: 'user', content: 'Hello' },
        { id: '2', role: 'assistant', content: 'Hi' }
      ]

      store.loadConversation('conv-456', history)

      expect(store.currentConversationId).toBe('conv-456')
      expect(store.messages).toEqual(history)
    })
  })

  describe('加载状态', () => {
    it('应该设置加载状态', () => {
      const store = useChatStore()

      store.setLoading(true)
      expect(store.isLoading).toBe(true)

      store.setLoading(false)
      expect(store.isLoading).toBe(false)
    })

    it('应该设置流式响应状态', () => {
      const store = useChatStore()

      store.setStreaming(true)
      expect(store.isStreaming).toBe(true)

      store.setStreaming(false)
      expect(store.isStreaming).toBe(false)
    })
  })

  describe('输入管理', () => {
    it('应该设置输入内容', () => {
      const store = useChatStore()

      store.setInput('Hello world')

      expect(store.input).toBe('Hello world')
    })

    it('应该清空输入内容', () => {
      const store = useChatStore()
      store.setInput('Some text')

      store.clearInput()

      expect(store.input).toBe('')
    })

    it('应该追加输入内容', () => {
      const store = useChatStore()
      store.setInput('Hello ')

      store.appendInput('world')

      expect(store.input).toBe('Hello world')
    })
  })

  describe('流式响应处理', () => {
    it('应该创建新的助手消息用于流式响应', () => {
      const store = useChatStore()

      store.startStreamingMessage('msg-stream')

      expect(store.messages).toHaveLength(1)
      expect(store.messages[0].id).toBe('msg-stream')
      expect(store.messages[0].role).toBe('assistant')
      expect(store.messages[0].content).toBe('')
    })

    it('应该追加流式内容到现有消息', () => {
      const store = useChatStore()
      store.startStreamingMessage('msg-stream')

      store.appendStreamingContent('Hello ')

      expect(store.messages[0].content).toBe('Hello ')

      store.appendStreamingContent('world')

      expect(store.messages[0].content).toBe('Hello world')
    })

    it('应该完成流式消息', () => {
      const store = useChatStore()
      store.startStreamingMessage('msg-stream')
      store.appendStreamingContent('Final content')

      store.completeStreamingMessage()

      expect(store.isStreaming).toBe(false)
      expect(store.messages[0].content).toBe('Final content')
    })
  })

  describe('重置状态', () => {
    it('应该重置所有状态到初始值', () => {
      const store = useChatStore()
      store.setCurrentConversation('conv-123')
      store.addMessage({ id: '1', role: 'user', content: 'Test' })
      store.setInput('Some input')
      store.setLoading(true)
      store.setStreaming(true)

      store.$reset()

      expect(store.currentConversationId).toBeNull()
      expect(store.messages).toEqual([])
      expect(store.input).toBe('')
      expect(store.isLoading).toBe(false)
      expect(store.isStreaming).toBe(false)
    })
  })

  describe('错误处理', () => {
    it('应该存储错误信息', () => {
      const store = useChatStore()

      store.setError('Network error')

      expect(store.error).toBe('Network error')
    })

    it('应该清除错误信息', () => {
      const store = useChatStore()
      store.setError('Some error')

      store.clearError()

      expect(store.error).toBeNull()
    })
  })
})
