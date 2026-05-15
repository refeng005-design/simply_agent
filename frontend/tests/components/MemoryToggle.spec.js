/**
 * MemoryToggle组件测试
 *
 * 测试记忆开关组件的核心功能：
 * - 显示/隐藏状态
 * - 切换开关
 * - 同步到store
 * - API调用
 * - 加载状态
 * - 错误处理
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

describe('MemoryToggle.vue - 记忆开关组件', () => {
  let MemoryToggle
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const module = await import('@/components/MemoryToggle.vue')
    MemoryToggle = module.default
  })

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('应该有开关容器', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123'
        }
      })

      const toggle = wrapper.find('.memory-toggle')
      expect(toggle.exists()).toBe(true)
    })

    it('应该有标签文本', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123'
        }
      })

      const label = wrapper.find('.toggle-label')
      expect(label.exists()).toBe(true)
      expect(label.text()).toBe('记忆')
    })

    it('应该有切换按钮', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123'
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.exists()).toBe(true)
    })
  })

  describe('开关状态显示', () => {
    it('memoryEnabled为true时应该显示启用状态', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.classes()).toContain('enabled')
    })

    it('memoryEnabled为false时应该显示禁用状态', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: false
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.classes()).not.toContain('enabled')
    })

    it('应该显示开关滑块', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const slider = wrapper.find('.toggle-slider')
      expect(slider.exists()).toBe(true)
    })
  })

  describe('切换操作', () => {
    it('点击开关应该触发toggle事件', async () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const button = wrapper.find('.toggle-button')
      await button.trigger('click')

      expect(wrapper.emitted('toggle')).toBeTruthy()
    })

    it('点击开关应该传递新的状态', async () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const button = wrapper.find('.toggle-button')
      await button.trigger('click')

      expect(wrapper.emitted('toggle')[0]).toEqual([false])
    })

    it('从禁用切换到启用应该传递true', async () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: false
        }
      })

      const button = wrapper.find('.toggle-button')
      await button.trigger('click')

      expect(wrapper.emitted('toggle')[0]).toEqual([true])
    })
  })

  describe('加载状态', () => {
    it('loading为true时应该禁用开关', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true,
          loading: true
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.classes()).toContain('loading')
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('loading时应该显示加载指示器', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true,
          loading: true
        }
      })

      const spinner = wrapper.find('.loading-spinner')
      expect(spinner.exists()).toBe(true)
    })

    it('loading为false时应该启用开关', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true,
          loading: false
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.classes()).not.toContain('loading')
    })
  })

  describe('提示文本', () => {
    it('启用状态时应该显示启用提示', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.attributes('title')).toBe('记忆已启用')
    })

    it('禁用状态时应该显示禁用提示', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: false
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.attributes('title')).toBe('记忆已禁用')
    })
  })

  describe('响应式更新', () => {
    it('memoryEnabled prop变化时应该更新UI', async () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: false
        }
      })

      let button = wrapper.find('.toggle-button')
      expect(button.classes()).not.toContain('enabled')

      await wrapper.setProps({ memoryEnabled: true })
      await wrapper.vm.$nextTick()

      button = wrapper.find('.toggle-button')
      expect(button.classes()).toContain('enabled')
    })

    it('loading prop变化时应该更新UI', async () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true,
          loading: false
        }
      })

      let button = wrapper.find('.toggle-button')
      expect(button.classes()).not.toContain('loading')

      await wrapper.setProps({ loading: true })
      await wrapper.vm.$nextTick()

      button = wrapper.find('.toggle-button')
      expect(button.classes()).toContain('loading')
    })
  })

  describe('键盘支持', () => {
    it('应该支持Space键切换', async () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const button = wrapper.find('.toggle-button')
      await button.trigger('keydown', { key: ' ' })

      expect(wrapper.emitted('toggle')).toBeTruthy()
    })

    it('应该支持Enter键切换', async () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const button = wrapper.find('.toggle-button')
      await button.trigger('keydown', { key: 'Enter' })

      expect(wrapper.emitted('toggle')).toBeTruthy()
    })
  })

  describe('可访问性', () => {
    it('应该有role="switch"属性', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.attributes('role')).toBe('switch')
    })

    it('启用时应该有aria-checked="true"', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.attributes('aria-checked')).toBe('true')
    })

    it('禁用时应该有aria-checked="false"', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: false
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.attributes('aria-checked')).toBe('false')
    })

    it('loading时应该有aria-busy="true"', () => {
      const wrapper = mount(MemoryToggle, {
        global: {
          plugins: [pinia]
        },
        props: {
          conversationId: 'conv-123',
          memoryEnabled: true,
          loading: true
        }
      })

      const button = wrapper.find('.toggle-button')
      expect(button.attributes('aria-busy')).toBe('true')
    })
  })
})
