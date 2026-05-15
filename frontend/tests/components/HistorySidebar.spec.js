/**
 * HistorySidebar组件测试
 *
 * 测试历史侧边栏组件的核心功能：
 * - 显示对话历史列表
 * - 选择对话
 * - 删除对话
 * - 新建对话
 * - 展开/收起
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useChatStore } from '@/stores/chat.js'

describe('HistorySidebar.vue - 历史侧边栏组件', () => {
  let HistorySidebar
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const module = await import('@/components/HistorySidebar.vue')
    HistorySidebar = module.default
  })

  const mockConversations = [
    { id: 'conv-1', title: '关于AI的讨论', created_at: '2026-01-10T10:00:00', message_count: 5 },
    { id: 'conv-2', title: '代码帮助', created_at: '2026-01-09T15:30:00', message_count: 12 },
    { id: 'conv-3', title: '天气查询', created_at: '2026-01-08T09:00:00', message_count: 3 }
  ]

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: []
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('应该有侧边栏容器', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: []
        }
      })

      const sidebar = wrapper.find('.history-sidebar')
      expect(sidebar.exists()).toBe(true)
    })

    it('应该显示新建对话按钮', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: []
        }
      })

      const newButton = wrapper.find('.new-chat-button')
      expect(newButton.exists()).toBe(true)
    })
  })

  describe('对话列表显示', () => {
    it('应该显示对话列表', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      const items = wrapper.findAll('.conversation-item')
      expect(items.length).toBe(3)
    })

    it('应该显示对话标题', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      expect(wrapper.text()).toContain('关于AI的讨论')
      expect(wrapper.text()).toContain('代码帮助')
      expect(wrapper.text()).toContain('天气查询')
    })

    it('应该高亮当前选中的对话', () => {
      const store = useChatStore()
      store.setCurrentConversation('conv-2')

      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      const items = wrapper.findAll('.conversation-item')
      const activeItem = items.find(item => item.classes().includes('active'))
      expect(activeItem.exists()).toBe(true)
    })

    it('应该在空列表时显示提示', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: []
        }
      })

      expect(wrapper.text()).toContain('暂无对话')
    })
  })

  describe('选择对话', () => {
    it('应该触发选择事件', async () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      const items = wrapper.findAll('.conversation-item')
      await items[0].trigger('click')

      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')[0]).toEqual(['conv-1'])
    })

    it('应该更新store中的当前对话', async () => {
      const store = useChatStore()
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      const items = wrapper.findAll('.conversation-item')
      await items[1].trigger('click')

      expect(store.currentConversationId).toBe('conv-2')
    })
  })

  describe('删除对话', () => {
    it('应该触发删除事件', async () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      const deleteButton = wrapper.find('.conversation-item .delete-button')
      await deleteButton.trigger('click')
      await deleteButton.trigger('click') // Double click to confirm

      expect(wrapper.emitted('delete')).toBeTruthy()
    })

    it('应该在删除后更新列表', async () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      let items = wrapper.findAll('.conversation-item')
      expect(items.length).toBe(3)

      await wrapper.setProps({ conversations: mockConversations.slice(1) })
      items = wrapper.findAll('.conversation-item')

      expect(items.length).toBe(2)
    })
  })

  describe('新建对话', () => {
    it('应该触发新建事件', async () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      const newButton = wrapper.find('.new-chat-button')
      await newButton.trigger('click')

      expect(wrapper.emitted('new')).toBeTruthy()
    })

    it('应该清空当前对话', async () => {
      const store = useChatStore()
      store.setCurrentConversation('conv-1')

      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations
        }
      })

      const newButton = wrapper.find('.new-chat-button')
      await newButton.trigger('click')

      expect(store.currentConversationId).toBeNull()
    })
  })

  describe('展开/收起', () => {
    it('应该支持展开收起侧边栏', async () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations,
          collapsed: false
        }
      })

      const toggleButton = wrapper.find('.toggle-button')
      await toggleButton.trigger('click')

      expect(wrapper.emitted('toggle')).toBeTruthy()
    })

    it('应该在收起时隐藏对话列表', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations,
          collapsed: true
        }
      })

      const list = wrapper.find('.conversation-list')
      expect(list.exists()).toBe(false)
    })
  })

  describe('加载状态', () => {
    it('应该在加载时显示加载指示器', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: [],
          loading: true
        }
      })

      const loader = wrapper.find('.loader')
      expect(loader.exists()).toBe(true)
    })
  })

  describe('分页', () => {
    it('应该在有更多对话时显示加载更多按钮', () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations,
          hasMore: true
        }
      })

      const loadMoreButton = wrapper.find('.load-more-button')
      expect(loadMoreButton.exists()).toBe(true)
    })

    it('应该触发加载更多事件', async () => {
      const wrapper = mount(HistorySidebar, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversations: mockConversations,
          hasMore: true
        }
      })

      const loadMoreButton = wrapper.find('.load-more-button')
      await loadMoreButton.trigger('click')

      expect(wrapper.emitted('loadMore')).toBeTruthy()
    })
  })
})
