/**
 * 设置状态管理 Store
 *
 * 管理应用设置和用户偏好：
 * - 模型配置（提供商、模型名称）
 * - API设置（密钥、端点、参数）
 * - 功能开关（RAG、记忆）
 * - UI设置（主题）
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'simply-agent-settings'

export const useSettingsStore = defineStore('settings', () => {
  // 状态 - 模型配置
  const provider = ref('openai')
  const model = ref('gpt-3.5-turbo')
  const apiKey = ref('')
  const apiEndpoint = ref('/api')
  const temperature = ref(0.7)
  const maxTokens = ref(2048)

  // 状态 - 功能开关
  const ragEnabled = ref(true)
  const memoryEnabled = ref(true)

  // 状态 - UI设置
  const theme = ref('light')

  // 模型配置方法
  function setProvider(newProvider) {
    provider.value = newProvider
  }

  function setModel(newModel) {
    model.value = newModel
  }

  // API设置方法
  function setApiKey(key) {
    apiKey.value = key
  }

  function setApiEndpoint(endpoint) {
    apiEndpoint.value = endpoint
  }

  function setTemperature(value) {
    // 限制温度值在0-1之间
    temperature.value = Math.max(0, Math.min(1, value))
  }

  function setMaxTokens(value) {
    maxTokens.value = value
  }

  // 功能开关方法
  function toggleRag() {
    ragEnabled.value = !ragEnabled.value
  }

  function setRagEnabled(enabled) {
    ragEnabled.value = enabled
  }

  function toggleMemory() {
    memoryEnabled.value = !memoryEnabled.value
  }

  function setMemoryEnabled(enabled) {
    memoryEnabled.value = enabled
  }

  // UI设置方法
  function setTheme(newTheme) {
    theme.value = newTheme
  }

  // 持久化方法
  function saveSettings() {
    const settings = {
      provider: provider.value,
      model: model.value,
      apiKey: apiKey.value,
      apiEndpoint: apiEndpoint.value,
      temperature: temperature.value,
      maxTokens: maxTokens.value,
      ragEnabled: ragEnabled.value,
      memoryEnabled: memoryEnabled.value,
      theme: theme.value
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  }

  function loadSettings() {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        const settings = JSON.parse(saved)
        provider.value = settings.provider ?? 'openai'
        model.value = settings.model ?? 'gpt-3.5-turbo'
        apiKey.value = settings.apiKey ?? ''
        apiEndpoint.value = settings.apiEndpoint ?? '/api'
        temperature.value = settings.temperature ?? 0.7
        maxTokens.value = settings.maxTokens ?? 2048
        ragEnabled.value = settings.ragEnabled ?? true
        memoryEnabled.value = settings.memoryEnabled ?? true
        theme.value = settings.theme ?? 'light'
      } catch (e) {
        // 如果解析失败，使用默认值
        console.error('Failed to load settings:', e)
      }
    }
  }

  // 重置所有设置
  function $reset() {
    provider.value = 'openai'
    model.value = 'gpt-3.5-turbo'
    apiKey.value = ''
    apiEndpoint.value = '/api'
    temperature.value = 0.7
    maxTokens.value = 2048
    ragEnabled.value = true
    memoryEnabled.value = true
    theme.value = 'light'
  }

  // 导出配置对象（用于API调用等）
  function toConfig() {
    return {
      provider: provider.value,
      model: model.value,
      apiKey: apiKey.value,
      apiEndpoint: apiEndpoint.value,
      temperature: temperature.value,
      maxTokens: maxTokens.value,
      ragEnabled: ragEnabled.value,
      memoryEnabled: memoryEnabled.value
    }
  }

  return {
    // 状态
    provider,
    model,
    apiKey,
    apiEndpoint,
    temperature,
    maxTokens,
    ragEnabled,
    memoryEnabled,
    theme,
    // 方法
    setProvider,
    setModel,
    setApiKey,
    setApiEndpoint,
    setTemperature,
    setMaxTokens,
    toggleRag,
    setRagEnabled,
    toggleMemory,
    setMemoryEnabled,
    setTheme,
    saveSettings,
    loadSettings,
    $reset,
    toConfig
  }
})
