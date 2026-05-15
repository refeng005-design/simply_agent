/**
 * 设置状态管理测试
 *
 * 测试设置store的核心功能：
 * - 模型配置管理
 * - API设置
 * - 用户偏好
 * - 持久化存储
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useSettingsStore } from '@/stores/settings.js'

describe('Settings Store - 设置状态管理', () => {
  beforeEach(() => {
    // 每个测试前创建新的pinia实例
    setActivePinia(createPinia())
    // 清除所有mock
    vi.clearAllMocks()
    // 清除localStorage
    localStorage.clear()
  })

  describe('初始状态', () => {
    it('应该有默认的模型提供商', () => {
      const store = useSettingsStore()
      expect(store.provider).toBe('openai')
    })

    it('应该有默认的模型名称', () => {
      const store = useSettingsStore()
      expect(store.model).toBe('gpt-3.5-turbo')
    })

    it('应该有空的API密钥', () => {
      const store = useSettingsStore()
      expect(store.apiKey).toBe('')
    })

    it('应该有默认的API端点', () => {
      const store = useSettingsStore()
      expect(store.apiEndpoint).toBe('/api')
    })

    it('应该有默认的温度值', () => {
      const store = useSettingsStore()
      expect(store.temperature).toBe(0.7)
    })

    it('应该有默认的最大token数', () => {
      const store = useSettingsStore()
      expect(store.maxTokens).toBe(2048)
    })

    it('应该默认启用RAG', () => {
      const store = useSettingsStore()
      expect(store.ragEnabled).toBe(true)
    })

    it('应该默认启用对话记忆', () => {
      const store = useSettingsStore()
      expect(store.memoryEnabled).toBe(true)
    })

    it('应该有默认的主题设置', () => {
      const store = useSettingsStore()
      expect(store.theme).toBe('light')
    })
  })

  describe('模型配置', () => {
    it('应该设置模型提供商', () => {
      const store = useSettingsStore()

      store.setProvider('anthropic')

      expect(store.provider).toBe('anthropic')
    })

    it('应该设置模型名称', () => {
      const store = useSettingsStore()

      store.setModel('claude-3-opus')

      expect(store.model).toBe('claude-3-opus')
    })

    it('应该同时设置提供商和模型', () => {
      const store = useSettingsStore()

      store.setProvider('qwen')
      store.setModel('qwen-turbo')

      expect(store.provider).toBe('qwen')
      expect(store.model).toBe('qwen-turbo')
    })
  })

  describe('API设置', () => {
    it('应该设置API密钥', () => {
      const store = useSettingsStore()

      store.setApiKey('sk-test-key-123')

      expect(store.apiKey).toBe('sk-test-key-123')
    })

    it('应该设置API端点', () => {
      const store = useSettingsStore()

      store.setApiEndpoint('https://api.example.com')

      expect(store.apiEndpoint).toBe('https://api.example.com')
    })

    it('应该设置温度值', () => {
      const store = useSettingsStore()

      store.setTemperature(0.5)

      expect(store.temperature).toBe(0.5)
    })

    it('应该限制温度值在0-1之间', () => {
      const store = useSettingsStore()

      store.setTemperature(1.5)
      expect(store.temperature).toBe(1.0)

      store.setTemperature(-0.5)
      expect(store.temperature).toBe(0.0)
    })

    it('应该设置最大token数', () => {
      const store = useSettingsStore()

      store.setMaxTokens(4096)

      expect(store.maxTokens).toBe(4096)
    })
  })

  describe('功能开关', () => {
    it('应该切换RAG启用状态', () => {
      const store = useSettingsStore()

      store.toggleRag()

      expect(store.ragEnabled).toBe(false)

      store.toggleRag()

      expect(store.ragEnabled).toBe(true)
    })

    it('应该设置RAG状态', () => {
      const store = useSettingsStore()

      store.setRagEnabled(false)

      expect(store.ragEnabled).toBe(false)
    })

    it('应该切换记忆启用状态', () => {
      const store = useSettingsStore()

      store.toggleMemory()

      expect(store.memoryEnabled).toBe(false)

      store.toggleMemory()

      expect(store.memoryEnabled).toBe(true)
    })

    it('应该设置记忆状态', () => {
      const store = useSettingsStore()

      store.setMemoryEnabled(false)

      expect(store.memoryEnabled).toBe(false)
    })
  })

  describe('UI设置', () => {
    it('应该设置主题', () => {
      const store = useSettingsStore()

      store.setTheme('dark')

      expect(store.theme).toBe('dark')
    })

    it('应该支持light和dark主题', () => {
      const store = useSettingsStore()

      store.setTheme('light')
      expect(store.theme).toBe('light')

      store.setTheme('dark')
      expect(store.theme).toBe('dark')
    })
  })

  describe('持久化', () => {
    it('应该保存设置到localStorage', () => {
      const store = useSettingsStore()

      store.setApiKey('sk-test-key')
      store.setModel('gpt-4')
      store.saveSettings()

      const saved = localStorage.getItem('simply-agent-settings')
      expect(saved).toBeTruthy()

      const parsed = JSON.parse(saved)
      expect(parsed.apiKey).toBe('sk-test-key')
      expect(parsed.model).toBe('gpt-4')
    })

    it('应该从localStorage加载设置', () => {
      const settingsToSave = {
        provider: 'anthropic',
        model: 'claude-3-opus',
        apiKey: 'sk-key-456',
        apiEndpoint: 'https://api.custom.com',
        temperature: 0.8,
        maxTokens: 4096,
        ragEnabled: false,
        memoryEnabled: false,
        theme: 'dark'
      }

      localStorage.setItem('simply-agent-settings', JSON.stringify(settingsToSave))

      const store = useSettingsStore()
      store.loadSettings()

      expect(store.provider).toBe('anthropic')
      expect(store.model).toBe('claude-3-opus')
      expect(store.apiKey).toBe('sk-key-456')
      expect(store.apiEndpoint).toBe('https://api.custom.com')
      expect(store.temperature).toBe(0.8)
      expect(store.maxTokens).toBe(4096)
      expect(store.ragEnabled).toBe(false)
      expect(store.memoryEnabled).toBe(false)
      expect(store.theme).toBe('dark')
    })

    it('应该在localStorage为空时使用默认值', () => {
      const store = useSettingsStore()
      store.loadSettings()

      expect(store.provider).toBe('openai')
      expect(store.model).toBe('gpt-3.5-turbo')
      expect(store.apiKey).toBe('')
    })
  })

  describe('重置设置', () => {
    it('应该重置所有设置到默认值', () => {
      const store = useSettingsStore()

      // 修改一些设置
      store.setProvider('anthropic')
      store.setModel('claude-3-opus')
      store.setApiKey('sk-test-key')
      store.setTemperature(0.9)
      store.setRagEnabled(false)
      store.setTheme('dark')

      store.$reset()

      expect(store.provider).toBe('openai')
      expect(store.model).toBe('gpt-3.5-turbo')
      expect(store.apiKey).toBe('')
      expect(store.temperature).toBe(0.7)
      expect(store.ragEnabled).toBe(true)
      expect(store.theme).toBe('light')
    })
  })

  describe('配置导出', () => {
    it('应该导出完整的配置对象', () => {
      const store = useSettingsStore()
      store.setApiKey('sk-test')
      store.setModel('gpt-4')

      const config = store.toConfig()

      expect(config).toEqual({
        provider: 'openai',
        model: 'gpt-4',
        apiKey: 'sk-test',
        apiEndpoint: '/api',
        temperature: 0.7,
        maxTokens: 2048,
        ragEnabled: true,
        memoryEnabled: true
      })
    })

    it('导出的配置不包含UI设置', () => {
      const store = useSettingsStore()
      store.setTheme('dark')

      const config = store.toConfig()

      expect(config.theme).toBeUndefined()
    })
  })
})
