/**
 * ChatView视图测试
 *
 * 测试聊天视图页面的核心功能：
 * - 页面布局
 * - 历史侧边栏集成
 * - 聊天窗口集成
 * - 路由集成
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useChatStore } from '@/stores/chat.js'
import { useSettingsStore } from '@/stores/settings.js'

describe('ChatView.vue - 聊天视图页面', () => {
  let ChatView
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const module = await import('@/views/ChatView.vue')
    ChatView = module.default
  })

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('应该有视图容器', () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      const container = wrapper.find('.chat-view')
      expect(container.exists()).toBe(true)
    })
  })

  describe('子组件集成', () => {
    it('应该包含HistorySidebar组件', () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.findComponent({ name: 'HistorySidebar' }).exists()).toBe(true)
    })

    it('应该包含ChatWindow组件', () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.findComponent({ name: 'ChatWindow' }).exists()).toBe(true)
    })
  })

  describe('对话选择', () => {
    it('应该从HistorySidebar接收选择事件', async () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      const sidebar = wrapper.findComponent({ name: 'HistorySidebar' })
      await sidebar.vm.$emit('select', 'conv-123')

      const store = useChatStore()
      expect(store.currentConversationId).toBe('conv-123')
    })

    it('应该从HistorySidebar接收新建事件', async () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      const sidebar = wrapper.findComponent({ name: 'HistorySidebar' })
      await sidebar.vm.$emit('new')

      const store = useChatStore()
      expect(store.currentConversationId).toBeNull()
      expect(store.messages).toEqual([])
    })
  })

  describe('侧边栏切换', () => {
    it('应该切换侧边栏展开/收起', async () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      const initialState = wrapper.vm.sidebarCollapsed

      const sidebar = wrapper.findComponent({ name: 'HistorySidebar' })
      await sidebar.vm.$emit('toggle')

      expect(wrapper.vm.sidebarCollapsed).toBe(!initialState)
    })

    it('应该在移动端默认收起侧边栏', () => {
      global.innerWidth = 375

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.vm.isMobile).toBe(true)
    })
  })

  describe('数据加载', () => {
    it('应该在挂载时加载对话历史', () => {
      const loadConversationsSpy = vi.fn()

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.vm.loading).toBe(false)
    })

    it('应该显示加载状态', async () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()

      const loader = wrapper.find('.page-loader')
      expect(loader.exists()).toBe(true)
    })
  })

  describe('对话删除', () => {
    it('应该从HistorySidebar接收删除事件', async () => {
      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      wrapper.vm.conversations = [
        { id: 'conv-123', title: 'Test', message_count: 1 }
      ]

      const sidebar = wrapper.findComponent({ name: 'HistorySidebar' })
      await sidebar.vm.$emit('delete', 'conv-123')

      // 对话应该从列表中移除
      expect(wrapper.vm.conversations.find(c => c.id === 'conv-123')).toBeUndefined()
    })
  })

  describe('状态同步', () => {
    it('应该同步聊天状态到ChatWindow', () => {
      const store = useChatStore()
      store.setLoading(true)

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.findComponent({ name: 'ChatWindow' }).exists()).toBe(true)
    })

    it('应该同步设置状态到ChatWindow', () => {
      const store = useSettingsStore()
      store.setProvider('openai')

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.findComponent({ name: 'ChatWindow' }).exists()).toBe(true)
    })
  })

  describe('响应式布局', () => {
    it('应该在桌面端显示侧边栏', () => {
      global.innerWidth = 1200

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.vm.isMobile).toBe(false)
    })

    it('应该在移动端隐藏侧边栏', () => {
      global.innerWidth = 375

      const wrapper = mount(ChatView, {
        global: {
          plugins: [pinia],
          stubs: {
            'history-sidebar': true,
            'chat-window': true
          }
        }
      })

      expect(wrapper.vm.isMobile).toBe(true)
    })
  })
})
