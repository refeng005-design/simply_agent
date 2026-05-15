/**
 * 端到端测试
 *
 * 测试聊天功能的完整用户流程
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import ChatView from '@/views/ChatView.vue'
import MessageList from '@/components/MessageList.vue'
import MessageInput from '@/components/MessageInput.vue'
import ModelSelector from '@/components/ModelSelector.vue'
import { useChatStore } from '@/stores/chat'

describe('E2E: Chat Flow', () => {
  let pinia
  let chatStore

  beforeEach(() => {
    pinia = createPinia()
    chatStore = useChatStore(pinia)
    // Mock API calls
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Complete Chat Flow', () => {
    it('should allow user to select model, send message, and receive response', async () => {
      // Mock successful API response
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          content: 'Hello! How can I help you today?'
        })
      })

      // Mount chat view
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia]
        }
      })

      // 1. 验证组件渲染
      expect(wrapper.findComponent(MessageList).exists()).toBe(true)
      expect(wrapper.findComponent(MessageInput).exists()).toBe(true)
      expect(wrapper.findComponent(ModelSelector).exists()).toBe(true)

      // 2. 选择模型
      const modelSelector = wrapper.findComponent(ModelSelector)
      await modelSelector.vm.$emit('update:model', 'gpt-4')
      expect(chatStore.currentModel).toBe('gpt-4')

      // 3. 发送消息
      const messageInput = wrapper.findComponent(MessageInput)
      await messageInput.vm.$emit('send', 'Hello, AI!')
      await messageInput.vm.$emit('submit')

      // 等待异步操作
      await wrapper.vm.$nextTick()

      // 4. 验证API被调用
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/chat'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: expect.stringContaining('Hello, AI!')
        })
      )

      // 5. 验证消息被添加到聊天历史
      expect(chatStore.messages.length).toBeGreaterThan(0)
      expect(chatStore.messages[chatStore.messages.length - 1].content).toBe('Hello! How can I help you today?')
    })

    it('should handle streaming response correctly', async () => {
      // Mock streaming response
      const streamChunks = [
        { content: 'Hello' },
        { content: ' there' },
        { content: '!' }
      ]

      let chunkIndex = 0
      global.fetch.mockResolvedValue({
        ok: true,
        body: {
          getReader: () => ({
            read: async () => {
              if (chunkIndex < streamChunks.length) {
                const chunk = streamChunks[chunkIndex]
                chunkIndex++
                return {
                  done: false,
                  value: new TextEncoder().encode(`data: ${JSON.stringify(chunk)}\n\n`)
                }
              }
              return { done: true }
            }
          })
        }
      })

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia]
        }
      })

      const messageInput = wrapper.findComponent(MessageInput)
      await messageInput.vm.$emit('send', 'Test streaming')

      // 等待流式响应完成
      await new Promise(resolve => setTimeout(resolve, 100))

      // 验证流式消息被正确组装
      const lastMessage = chatStore.messages[chatStore.messages.length - 1]
      expect(lastMessage.content).toBe('Hello there!')
    })
  })

  describe('Error Handling Flow', () => {
    it('should display error message when API fails', async () => {
      // Mock API error
      global.fetch.mockRejectedValue(new Error('Network error'))

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia]
        }
      })

      const messageInput = wrapper.findComponent(MessageInput)
      await messageInput.vm.$emit('send', 'Test error')

      await wrapper.vm.$nextTick()

      // 验证错误状态
      expect(chatStore.error).toBeTruthy()
    })

    it('should retry failed requests', async () => {
      let attemptCount = 0
      global.fetch.mockImplementation(() => {
        attemptCount++
        if (attemptCount < 3) {
          return Promise.reject(new Error('Network error'))
        }
        return Promise.resolve({
          ok: true,
          json: async () => ({ content: 'Success after retry' })
        })
      })

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia]
        }
      })

      const messageInput = wrapper.findComponent(MessageInput)
      await messageInput.vm.$emit('send', 'Test retry')

      await new Promise(resolve => setTimeout(resolve, 200))

      // 验证重试发生
      expect(attemptCount).toBe(3)
      expect(chatStore.messages[chatStore.messages.length - 1].content).toBe('Success after retry')
    })
  })

  describe('Settings Flow', () => {
    it('should persist settings across sessions', async () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia]
        }
      })

      // 更改设置
      const settingsPanel = wrapper.findComponent('[data-test="settings-panel"]')
      if (settingsPanel.exists()) {
        await settingsPanel.vm.$emit('update:temperature', 0.7)
        await settingsPanel.vm.$emit('update:maxTokens', 2000)
      }

      // 验证设置被保存
      const settings = JSON.parse(localStorage.getItem('chat-settings') || '{}')
      expect(settings.temperature).toBe(0.7)
      expect(settings.maxTokens).toBe(2000)
    })
  })

  describe('History Flow', () => {
    it('should load and display chat history', async () => {
      const mockHistory = [
        { id: '1', title: 'Previous Chat 1', messages: [] },
        { id: '2', title: 'Previous Chat 2', messages: [] }
      ]

      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockHistory
      })

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia]
        }
      })

      // 等待历史加载
      await new Promise(resolve => setTimeout(resolve, 100))

      // 验证历史被加载
      expect(chatStore.conversations.length).toBe(2)
    })
  })

  describe('Memory Toggle Flow', () => {
    it('should respect memory toggle setting', async () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia]
        }
      })

      // 关闭记忆
      chatStore.memoryEnabled = false

      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ content: 'Response' })
      })

      const messageInput = wrapper.findComponent(MessageInput)
      await messageInput.vm.$emit('send', 'Test')

      // 验证请求不包含历史消息
      const fetchCall = global.fetch.mock.calls[global.fetch.mock.calls.length - 1]
      const body = JSON.parse(fetchCall[1].body)
      expect(body.messages.length).toBe(1) // 只有当前消息
    })
  })
})
