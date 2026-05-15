/**
 * SettingsPanel组件测试
 *
 * 测试设置面板组件的核心功能：
 * - 显示模型配置
 * - 修改API设置
 * - 功能开关
 * - 保存设置
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useSettingsStore } from '@/stores/settings.js'

describe('SettingsPanel.vue - 设置面板组件', () => {
  let SettingsPanel
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const module = await import('@/components/SettingsPanel.vue')
    SettingsPanel = module.default
  })

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('应该有设置面板容器', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const panel = wrapper.find('.settings-panel')
      expect(panel.exists()).toBe(true)
    })

    it('应该显示标题', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('设置')
    })
  })

  describe('模型配置', () => {
    it('应该显示提供商选择', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('提供商')
    })

    it('应该显示模型选择', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('模型')
    })

    it('应该显示API密钥输入', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const apiKeyInput = wrapper.find('input[type="password"]')
      expect(apiKeyInput.exists()).toBe(true)
    })
  })

  describe('参数设置', () => {
    it('应该显示温度滑块', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const tempSlider = wrapper.find('input[type="range"]')
      expect(tempSlider.exists()).toBe(true)
    })

    it('应该显示最大token输入', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('最大Token')
    })

    it('应该更新温度值', async () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const tempSlider = wrapper.find('input[type="range"]')
      await tempSlider.setValue(0.9)

      const store = useSettingsStore()
      expect(store.temperature).toBe(0.9)
    })

    it('应该限制温度值在0-1之间', async () => {
      const store = useSettingsStore()
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const tempSlider = wrapper.find('input[type="range"]')
      await tempSlider.setValue(1.5)

      expect(store.temperature).toBeLessThanOrEqual(1)
    })
  })

  describe('功能开关', () => {
    it('应该显示RAG开关', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('RAG')
    })

    it('应该切换RAG状态', async () => {
      const store = useSettingsStore()
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const ragCheckbox = wrapper.find('input[name="rag"]')
      await ragCheckbox.setChecked(false)

      expect(store.ragEnabled).toBe(false)
    })

    it('应该显示记忆开关', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('记忆')
    })

    it('应该切换记忆状态', async () => {
      const store = useSettingsStore()
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const memoryCheckbox = wrapper.find('input[name="memory"]')
      await memoryCheckbox.setChecked(false)

      expect(store.memoryEnabled).toBe(false)
    })
  })

  describe('保存设置', () => {
    it('应该有保存按钮', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const saveButton = wrapper.find('.save-button')
      expect(saveButton.exists()).toBe(true)
    })

    it('应该触发保存事件', async () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const saveButton = wrapper.find('.save-button')
      await saveButton.trigger('click')

      expect(wrapper.emitted('save')).toBeTruthy()
    })

    it('应该在保存时调用store的saveSettings', async () => {
      const store = useSettingsStore()
      const saveSpy = vi.spyOn(store, 'saveSettings')

      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const saveButton = wrapper.find('.save-button')
      await saveButton.trigger('click')

      expect(saveSpy).toHaveBeenCalled()
    })
  })

  describe('关闭面板', () => {
    it('应该有关闭按钮', () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const closeButton = wrapper.find('.close-button')
      expect(closeButton.exists()).toBe(true)
    })

    it('应该触发关闭事件', async () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const closeButton = wrapper.find('.close-button')
      await closeButton.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })

  describe('状态同步', () => {
    it('应该显示store中的当前设置', () => {
      const store = useSettingsStore()
      store.setProvider('anthropic')
      store.setModel('claude-3-opus')

      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.text()).toContain('Anthropic')
      expect(wrapper.find('input[type="text"]').element.value).toBe('claude-3-opus')
    })

    it('应该响应store的变化', async () => {
      const store = useSettingsStore()
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      store.setTemperature(0.5)
      await wrapper.vm.$nextTick()

      const tempSlider = wrapper.find('input[type="range"]')
      expect(tempSlider.element.value).toBe('0.5')
    })
  })

  describe('输入验证', () => {
    it('应该验证API密钥不为空', async () => {
      const wrapper = mount(SettingsPanel, {
        global: {
          plugins: [pinia]
        }
      })

      const apiKeyInput = wrapper.find('input[type="password"]')
      await apiKeyInput.setValue('')

      const saveButton = wrapper.find('.save-button')
      await saveButton.trigger('click')

      // 应该显示错误提示
      expect(wrapper.text()).toContain('API密钥')
    })
  })
})
