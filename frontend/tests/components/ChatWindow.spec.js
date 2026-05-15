/**
 * ChatWindow组件测试
 *
 * 测试聊天窗口容器组件的核心功能：
 * - 布局结构
 * - 子组件集成
 * - 消息发送流程
 * - 设置面板切换
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useChatStore } from '@/stores/chat.js'
import { useSettingsStore } from '@/stores/settings.js'

describe('ChatWindow.vue - 聊天窗口组件', () => {
  let ChatWindow
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const module = await import('@/components/ChatWindow.vue')
    ChatWindow = module.default
  })

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('应该有窗口容器', () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      const container = wrapper.find('.chat-window')
      expect(container.exists()).toBe(true)
    })
  })

  describe('子组件集成', () => {
    it('应该包含MessageList组件', () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      expect(wrapper.findComponent({ name: 'MessageList' }).exists()).toBe(true)
    })

    it('应该包含MessageInput组件', () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      expect(wrapper.findComponent({ name: 'MessageInput' }).exists()).toBe(true)
    })

    it('应该包含ModelSelector组件', () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      expect(wrapper.findComponent({ name: 'ModelSelector' }).exists()).toBe(true)
    })
  })

  describe('头部工具栏', () => {
    it('应该有设置按钮', () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      const settingsButton = wrapper.find('.settings-button')
      expect(settingsButton.exists()).toBe(true)
    })

    it('应该切换设置面板', async () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true,
            'settings-panel': true
          }
        }
      })

      const settingsButton = wrapper.find('.settings-button')
      await settingsButton.trigger('click')

      expect(wrapper.vm.showSettings).toBe(true)
    })

    it('应该显示当前模型', () => {
      const store = useSettingsStore()
      store.setModel('gpt-4')

      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true
          }
        }
      })

      expect(wrapper.findComponent({ name: 'ModelSelector' }).exists()).toBe(true)
    })
  })

  describe('消息发送流程', () => {
    it('应该从MessageInput接收消息并发送', async () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      const messageInput = wrapper.findComponent({ name: 'MessageInput' })
      await messageInput.vm.$emit('send', '测试消息')

      const store = useChatStore()
      expect(store.messages.length).toBeGreaterThan(0)
    })

    it('应该在发送时添加用户消息', async () => {
      const store = useChatStore()
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      const messageInput = wrapper.findComponent({ name: 'MessageInput' })
      await messageInput.vm.$emit('send', 'Hello')

      const lastMessage = store.messages[store.messages.length - 1]
      expect(lastMessage.role).toBe('user')
      expect(lastMessage.content).toBe('Hello')
    })
  })

  describe('设置面板', () => {
    it('应该显示设置面板当showSettings为true', async () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      expect(wrapper.find('.settings-overlay').exists()).toBe(false)

      wrapper.vm.showSettings = true
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.settings-overlay').exists()).toBe(true)
    })

    it('应该关闭设置面板', async () => {
      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      wrapper.vm.showSettings = true
      await wrapper.vm.$nextTick()

      wrapper.vm.closeSettings()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showSettings).toBe(false)
    })
  })

  describe('响应式布局', () => {
    it('应该在移动端隐藏侧边栏', () => {
      global.innerWidth = 375

      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      expect(wrapper.vm.isMobile).toBe(true)
    })
  })

  describe('状态同步', () => {
    it('应该同步聊天状态到子组件', () => {
      const store = useChatStore()
      store.setLoading(true)

      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      expect(wrapper.vm.isLoading).toBe(true)
    })

    it('应该同步设置状态到子组件', () => {
      const store = useSettingsStore()
      store.setProvider('openai')

      const wrapper = mount(ChatWindow, {
        global: {
          plugins: [pinia],
          stubs: {
            'message-list': true,
            'message-input': true,
            'model-selector': true
          }
        }
      })

      expect(wrapper.vm.currentProvider).toBe('openai')
    })
  })
})
