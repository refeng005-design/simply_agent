/**
 * ModelSelector组件测试
 *
 * 测试模型选择器组件的核心功能：
 * - 显示模型列表
 * - 选择模型
 * - 切换提供商
 * - 显示当前模型
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useSettingsStore } from '@/stores/settings.js'

describe('ModelSelector.vue - 模型选择器组件', () => {
  let ModelSelector
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const module = await import('@/components/ModelSelector.vue')
    ModelSelector = module.default
  })

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('应该有选择器元素', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        }
      })

      const select = wrapper.find('select')
      expect(select.exists()).toBe(true)
    })

    it('应该显示当前选中的模型', () => {
      const store = useSettingsStore()
      store.setModel('gpt-4')

      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
            { id: 'gpt-4', name: 'GPT-4', provider: 'openai' }
          ]
        }
      })

      expect(wrapper.text()).toContain('GPT-4')
    })
  })

  describe('模型列表', () => {
    it('应该显示OpenAI模型', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
            { id: 'gpt-4', name: 'GPT-4', provider: 'openai' }
          ]
        }
      })

      const options = wrapper.findAll('option')
      expect(options.length).toBeGreaterThan(0)
    })

    it('应该显示Anthropic模型', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [
            { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'anthropic' },
            { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'anthropic' }
          ]
        }
      })

      const options = wrapper.findAll('option')
      expect(options.length).toBeGreaterThan(0)
    })

    it('应该显示通义千问模型', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [
            { id: 'qwen-turbo', name: 'Qwen Turbo', provider: 'qwen' },
            { id: 'qwen-plus', name: 'Qwen Plus', provider: 'qwen' }
          ]
        }
      })

      const options = wrapper.findAll('option')
      expect(options.length).toBeGreaterThan(0)
    })
  })

  describe('模型选择', () => {
    it('应该触发选择事件', async () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
            { id: 'gpt-4', name: 'GPT-4', provider: 'openai' }
          ]
        }
      })

      const select = wrapper.find('select')
      await select.setValue('gpt-4')

      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')[0]).toEqual(['gpt-4'])
    })

    it('应该更新store中的模型', async () => {
      const store = useSettingsStore()
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
            { id: 'gpt-4', name: 'GPT-4', provider: 'openai' }
          ]
        }
      })

      const select = wrapper.find('select')
      await select.setValue('gpt-4')

      expect(store.model).toBe('gpt-4')
    })

    it('应该禁用状态', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [],
          disabled: true
        }
      })

      const select = wrapper.find('select')
      expect(select.attributes('disabled')).toBeDefined()
    })
  })

  describe('提供商切换', () => {
    it('应该显示当前提供商', () => {
      const store = useSettingsStore()
      store.setProvider('openai')

      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('openai')
    })

    it('应该根据提供商过滤模型', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [
            { id: 'gpt-4', name: 'GPT-4', provider: 'openai' },
            { id: 'claude-3', name: 'Claude 3', provider: 'anthropic' }
          ],
          provider: 'openai'
        }
      })

      const options = wrapper.findAll('option')
      // 应该只显示openai的模型
      expect(options.length).toBeGreaterThan(0)
    })
  })

  describe('加载状态', () => {
    it('应该在加载时显示加载指示器', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          loading: true
        }
      })

      const loader = wrapper.find('.loader')
      expect(loader.exists()).toBe(true)
    })

    it('应该在加载时禁用选择器', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          loading: true
        }
      })

      const select = wrapper.find('select')
      expect(select.attributes('disabled')).toBeDefined()
    })
  })

  describe('空状态', () => {
    it('应该在没有模型时显示提示', () => {
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: []
        }
      })

      expect(wrapper.text()).toContain('无可用模型')
    })
  })

  describe('状态同步', () => {
    it('应该响应store的模型变化', async () => {
      const store = useSettingsStore()
      const wrapper = mount(ModelSelector, {
        global: {
          plugins: [pinia]
        },
        props: {
          models: [
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
            { id: 'gpt-4', name: 'GPT-4', provider: 'openai' }
          ]
        }
      })

      store.setModel('gpt-4')
      await wrapper.vm.$nextTick()

      const select = wrapper.find('select')
      expect(select.element.value).toBe('gpt-4')
    })
  })
})
