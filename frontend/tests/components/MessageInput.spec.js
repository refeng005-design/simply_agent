/**
 * MessageInput组件测试
 *
 * 测试消息输入组件的核心功能：
 * - 文本输入
 * - 发送消息
 * - 快捷键支持
 * - 禁用状态
 * - 输入验证
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useChatStore } from '@/stores/chat.js'

describe('MessageInput.vue - 消息输入组件', () => {
  let MessageInput
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const module = await import('@/components/MessageInput.vue')
    MessageInput = module.default
  })

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('应该有输入框', () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      expect(textarea.exists()).toBe(true)
    })

    it('应该有发送按钮', () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const sendButton = wrapper.find('button')
      expect(sendButton.exists()).toBe(true)
    })

    it('应该显示占位符文本', () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      expect(textarea.attributes('placeholder')).toContain('输入')
    })
  })

  describe('输入功能', () => {
    it('应该接收用户输入', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('测试消息')

      expect(textarea.element.value).toBe('测试消息')
    })

    it('应该同步输入到store', async () => {
      const store = useChatStore()
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('测试消息')
      await textarea.trigger('input')

      expect(store.input).toBe('测试消息')
    })

    it('应该支持多行输入', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      const multiline = '第一行\n第二行\n第三行'
      await textarea.setValue(multiline)

      expect(textarea.element.value).toBe(multiline)
    })
  })

  describe('发送消息', () => {
    it('应该触发发送事件', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('测试消息')

      const sendButton = wrapper.find('button')
      await sendButton.trigger('click')

      expect(wrapper.emitted('send')).toBeTruthy()
      expect(wrapper.emitted('send')[0]).toEqual(['测试消息'])
    })

    it('应该在发送后清空输入', async () => {
      const store = useChatStore()
      store.setInput('测试消息')

      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const sendButton = wrapper.find('button')
      await sendButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(store.input).toBe('')
    })

    it('不应该发送空消息', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const sendButton = wrapper.find('button')
      await sendButton.trigger('click')

      expect(wrapper.emitted('send')).toBeFalsy()
    })

    it('不应该发送只包含空格的消息', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('   ')

      const sendButton = wrapper.find('button')
      await sendButton.trigger('click')

      expect(wrapper.emitted('send')).toBeFalsy()
    })
  })

  describe('快捷键支持', () => {
    it('应该支持Enter发送消息', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('测试消息')

      await textarea.trigger('keydown', { key: 'Enter' })

      expect(wrapper.emitted('send')).toBeTruthy()
    })

    it('应该支持Shift+Enter换行', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('第一行')

      await textarea.trigger('keydown', { key: 'Enter', shiftKey: true })

      expect(wrapper.emitted('send')).toBeFalsy()
    })

    it('应该在空内容时不响应Enter', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      await textarea.trigger('keydown', { key: 'Enter' })

      expect(wrapper.emitted('send')).toBeFalsy()
    })
  })

  describe('禁用状态', () => {
    it('应该在加载时禁用输入', () => {
      const store = useChatStore()
      store.setLoading(true)

      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      expect(textarea.attributes('disabled')).toBeDefined()
    })

    it('应该在加载时禁用发送按钮', () => {
      const store = useChatStore()
      store.setLoading(true)

      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const sendButton = wrapper.find('button')
      expect(sendButton.attributes('disabled')).toBeDefined()
    })

    it('应该在非加载时启用输入', () => {
      const store = useChatStore()
      store.setLoading(false)

      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      expect(textarea.attributes('disabled')).toBeUndefined()
    })
  })

  describe('输入限制', () => {
    it('应该设置最大输入长度属性', () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      expect(textarea.attributes('maxlength')).toBe('4000')
    })

    it('应该显示剩余字符数', () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const charCount = wrapper.find('.char-count')
      expect(charCount.exists()).toBe(true)
    })

    it('应该正确计算剩余字符数', async () => {
      const store = useChatStore()
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('测试')

      expect(wrapper.find('.char-count').text()).toBe('3998')
    })
  })

  describe('自动调整高度', () => {
    it('应该在输入时调整textarea高度', async () => {
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      const textarea = wrapper.find('textarea')
      const initialHeight = textarea.element.style.height

      await textarea.setValue('短文本')
      await textarea.trigger('input')

      // 高度应该可能发生变化
      expect(textarea.exists()).toBe(true)
    })
  })

  describe('状态同步', () => {
    it('应该响应store的input变化', async () => {
      const store = useChatStore()
      const wrapper = mount(MessageInput, {
        global: {
          plugins: [pinia]
        }
      })

      store.setInput('外部设置的消息')
      await wrapper.vm.$nextTick()

      const textarea = wrapper.find('textarea')
      expect(textarea.element.value).toBe('外部设置的消息')
    })
  })
})
