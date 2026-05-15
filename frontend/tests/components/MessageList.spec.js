/**
 * MessageList组件测试
 *
 * 测试消息列表组件的核心功能：
 * - 渲染消息列表
 * - 区分用户/助手消息样式
 * - 显示流式消息
 * - 滚动到底部
 * - 空状态显示
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useChatStore } from '@/stores/chat.js'

describe('MessageList.vue - 消息列表组件', () => {
  let MessageList
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    // 动态导入组件
    const module = await import('@/components/MessageList.vue')
    MessageList = module.default
  })

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('应该有容器元素', () => {
      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      const container = wrapper.find('.message-list')
      expect(container.exists()).toBe(true)
    })

    it('应该显示空状态提示', () => {
      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('开始对话')
    })
  })

  describe('消息显示', () => {
    it('应该显示用户消息', () => {
      const store = useChatStore()
      store.addMessage({
        id: 'msg-1',
        role: 'user',
        content: '你好'
      })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('你好')
    })

    it('应该显示助手消息', () => {
      const store = useChatStore()
      store.addMessage({
        id: 'msg-2',
        role: 'assistant',
        content: '你好！有什么可以帮助你的吗？'
      })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('你好！有什么可以帮助你的吗？')
    })

    it('应该为用户消息添加正确的样式类', () => {
      const store = useChatStore()
      store.addMessage({
        id: 'msg-1',
        role: 'user',
        content: '测试消息'
      })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      const userMessage = wrapper.find('.message.user')
      expect(userMessage.exists()).toBe(true)
    })

    it('应该为助手消息添加正确的样式类', () => {
      const store = useChatStore()
      store.addMessage({
        id: 'msg-1',
        role: 'assistant',
        content: '助手回复'
      })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      const assistantMessage = wrapper.find('.message.assistant')
      expect(assistantMessage.exists()).toBe(true)
    })

    it('应该按顺序显示多条消息', () => {
      const store = useChatStore()
      store.addMessage({ id: '1', role: 'user', content: '第一条' })
      store.addMessage({ id: '2', role: 'assistant', content: '回复一' })
      store.addMessage({ id: '3', role: 'user', content: '第二条' })
      store.addMessage({ id: '4', role: 'assistant', content: '回复二' })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      const messages = wrapper.findAll('.message')
      expect(messages).toHaveLength(4)
      expect(messages[0].text()).toContain('第一条')
      expect(messages[1].text()).toContain('回复一')
      expect(messages[2].text()).toContain('第二条')
      expect(messages[3].text()).toContain('回复二')
    })
  })

  describe('流式消息显示', () => {
    it('应该显示正在流式输出的消息', () => {
      const store = useChatStore()
      store.setStreaming(true)
      store.startStreamingMessage('msg-stream')
      store.appendStreamingContent('正在')

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('正在')
    })

    it('应该为流式消息添加加载指示器', () => {
      const store = useChatStore()
      store.setStreaming(true)
      store.startStreamingMessage('msg-stream')

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      const loadingIndicator = wrapper.find('.streaming-indicator')
      expect(loadingIndicator.exists()).toBe(true)
    })

    it('应该更新流式消息内容', async () => {
      const store = useChatStore()
      store.setStreaming(true)
      store.startStreamingMessage('msg-stream')
      store.appendStreamingContent('初始')

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('初始')

      // 模拟追加内容
      store.appendStreamingContent('追加')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('初始追加')
    })
  })

  describe('交互行为', () => {
    it('应该在消息变化时滚动到底部', async () => {
      const store = useChatStore()

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      // Mock scrollIntoView
      const scrollMock = vi.fn()
      wrapper.vm.$refs.listContainer = {
        querySelector: () => ({
          scrollIntoView: scrollMock
        })
      }

      store.addMessage({ id: '1', role: 'user', content: '新消息' })
      await wrapper.vm.$nextTick()
      await wrapper.vm.$nextTick()

      // 验证组件能够处理滚动
      expect(wrapper.findAll('.message')).toHaveLength(1)
    })

    it('应该支持删除消息', async () => {
      const store = useChatStore()
      store.addMessage({ id: '1', role: 'user', content: '要删除的消息' })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('要删除的消息')

      store.deleteMessage('1')
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('要删除的消息')
    })
  })

  describe('边界情况', () => {
    it('应该处理空内容消息', () => {
      const store = useChatStore()
      store.addMessage({
        id: 'msg-1',
        role: 'user',
        content: ''
      })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      const messages = wrapper.findAll('.message')
      expect(messages).toHaveLength(1)
    })

    it('应该处理长文本消息', () => {
      const longText = 'A'.repeat(1000)
      const store = useChatStore()
      store.addMessage({
        id: 'msg-1',
        role: 'assistant',
        content: longText
      })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain(longText)
    })

    it('应该处理特殊字符消息', () => {
      const specialText = '<script>alert("test")</script>'
      const store = useChatStore()
      store.addMessage({
        id: 'msg-1',
        role: 'user',
        content: specialText
      })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      // 应该转义HTML，不作为HTML渲染
      expect(wrapper.html()).not.toContain('<script>')
    })
  })

  describe('状态同步', () => {
    it('应该响应store中消息的变化', async () => {
      const store = useChatStore()
      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.findAll('.message')).toHaveLength(0)

      store.addMessage({ id: '1', role: 'user', content: '新消息' })
      await wrapper.vm.$nextTick()

      expect(wrapper.findAll('.message')).toHaveLength(1)
    })

    it('应该在清空消息后显示空状态', async () => {
      const store = useChatStore()
      store.addMessage({ id: '1', role: 'user', content: '消息' })

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.findAll('.message')).toHaveLength(1)

      store.clearMessages()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('开始对话')
    })
  })

  describe('流式渲染性能优化', () => {
    it('应该使用虚拟滚动处理大量消息', async () => {
      const store = useChatStore()

      // 添加大量消息
      for (let i = 0; i < 1000; i++) {
        store.addMessage({
          id: `msg-${i}`,
          role: i % 2 === 0 ? 'user' : 'assistant',
          content: `消息 ${i}`
        })
      }

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      // 这个测试会失败，因为当前实现没有虚拟滚动
      // 应该只渲染可见区域的消息
      const renderedMessages = wrapper.findAll('.message')

      // 理想情况下，不应该渲染全部1000条消息
      expect(renderedMessages.length).toBeLessThan(100)
      expect(wrapper.vm).toHaveProperty('virtualScrollEnabled')
    })

    it('应该批量处理流式内容更新', async () => {
      const store = useChatStore()
      store.setStreaming(true)
      store.startStreamingMessage('msg-stream')

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      // 模拟快速追加内容
      const startTime = Date.now()
      for (let i = 0; i < 100; i++) {
        store.appendStreamingContent(`chunk${i}`)
      }
      await wrapper.vm.$nextTick()
      const duration = Date.now() - startTime

      // 批量更新应该更快（这个阈值可能需要调整）
      // 当前实现每次追加都触发更新，应该优化为批量处理
      expect(duration).toBeLessThan(50)

      // 验证批量处理配置存在
      expect(wrapper.vm).toHaveProperty('batchUpdateEnabled')
    })

    it('应该节流滚动操作避免频繁滚动', async () => {
      const store = useChatStore()
      store.setStreaming(true)
      store.startStreamingMessage('msg-stream')

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      const scrollMock = vi.fn()
      wrapper.vm.$refs.listContainer = {
        querySelector: () => ({
          scrollIntoView: scrollMock
        })
      }

      // 快速追加多个chunk
      for (let i = 0; i < 20; i++) {
        store.appendStreamingContent(`chunk${i}`)
      }

      await wrapper.vm.$nextTick()

      // 验证滚动被节流（不是每个chunk都触发滚动）
      expect(scrollMock.mock.calls.length).toBeLessThan(20)

      // 验证节流配置存在
      expect(wrapper.vm).toHaveProperty('scrollThrottleEnabled')
    })

    it('应该使用requestAnimationFrame优化渲染', async () => {
      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      // 验证组件使用RAF进行渲染优化
      expect(wrapper.vm).toHaveProperty('useRAF')
    })

    it('应该只更新变化的消息而不是整个列表', async () => {
      const store = useChatStore()

      // 添加多条消息
      for (let i = 0; i < 10; i++) {
        store.addMessage({
          id: `msg-${i}`,
          role: 'assistant',
          content: `初始内容 ${i}`
        })
      }

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      // 验证使用key来优化渲染（只有变化的消息会重新渲染）
      const messages = wrapper.findAll('.message')
      expect(messages).toHaveLength(10)

      // 检查每个消息都有唯一的data-message-id属性（用于追踪）
      const messageElements = wrapper.findAll('.message')
      messageElements.forEach((msg, index) => {
        expect(msg.attributes('data-message-id')).toBe(`msg-${index}`)
      })
    })

    it('应该使用debounce处理输入流', async () => {
      const store = useChatStore()
      store.setStreaming(true)
      store.startStreamingMessage('msg-stream')

      const wrapper = mount(MessageList, {
        global: {
          plugins: [pinia]
        }
      })

      // 模拟非常快速的输入（比如每1ms一个字符）
      const rapidUpdates = []
      for (let i = 0; i < 50; i++) {
        rapidUpdates.push(() => store.appendStreamingContent(`char${i}`))
      }

      const startTime = Date.now()
      rapidUpdates.forEach(fn => fn())
      await wrapper.vm.$nextTick()
      const duration = Date.now() - startTime

      // 使用debounce后，应该比逐个更新更快
      expect(wrapper.vm).toHaveProperty('inputDebounceEnabled')
    })
  })
})
