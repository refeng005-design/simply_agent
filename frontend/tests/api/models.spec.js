/**
 * 模型API测试
 *
 * 测试模型管理相关的API调用：
 * - 获取支持的提供商列表
 * - 获取指定提供商的模型列表
 * - 获取模型详细信息
 * - 测试模型连接
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'

// Mock apiClient
vi.mock('../../src/api/client.js', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('api/models.js - 模型API', () => {
  let apiClient
  let modelsApi

  beforeEach(async () => {
    vi.clearAllMocks()

    // 动态导入以获取mock的apiClient
    const clientModule = await import('../../src/api/client.js')
    apiClient = clientModule.default

    // 导入models API模块
    const modelsModule = await import('../../src/api/models.js')
    modelsApi = modelsModule.default
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('getProviders - 获取提供商列表', () => {
    it('应该发送GET请求到/providers端点', async () => {
      const mockResponse = {
        providers: [
          {
            id: 'openai',
            name: 'OpenAI',
            description: 'OpenAI GPT models',
            enabled: true
          },
          {
            id: 'anthropic',
            name: 'Anthropic',
            description: 'Anthropic Claude models',
            enabled: true
          },
          {
            id: 'qwen',
            name: '通义千问',
            description: 'Alibaba Qwen models',
            enabled: false
          }
        ]
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await modelsApi.getProviders()

      expect(apiClient.get).toHaveBeenCalledWith('/providers')
      expect(response.providers).toHaveLength(3)
      expect(response.providers[0].id).toBe('openai')
    })

    it('应该返回空列表当没有提供商时', async () => {
      const mockResponse = { providers: [] }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await modelsApi.getProviders()

      expect(response.providers).toEqual([])
    })
  })

  describe('getModels - 获取模型列表', () => {
    it('应该发送GET请求到/providers/:provider/models端点', async () => {
      const mockResponse = {
        provider: 'openai',
        models: [
          {
            id: 'gpt-3.5-turbo',
            name: 'GPT-3.5 Turbo',
            description: 'Fast and efficient model',
            context_length: 16385,
            enabled: true
          },
          {
            id: 'gpt-4',
            name: 'GPT-4',
            description: 'Most capable model',
            context_length: 8192,
            enabled: true
          },
          {
            id: 'gpt-4-turbo',
            name: 'GPT-4 Turbo',
            description: 'Latest GPT-4 variant',
            context_length: 128000,
            enabled: true
          }
        ]
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await modelsApi.getModels('openai')

      expect(apiClient.get).toHaveBeenCalledWith('/providers/openai/models')
      expect(response.models).toHaveLength(3)
      expect(response.models[0].id).toBe('gpt-3.5-turbo')
    })

    it('应该支持获取不同提供商的模型', async () => {
      const mockResponse = {
        provider: 'anthropic',
        models: [
          {
            id: 'claude-3-opus',
            name: 'Claude 3 Opus',
            description: 'Most powerful Claude',
            context_length: 200000,
            enabled: true
          }
        ]
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await modelsApi.getModels('anthropic')

      expect(apiClient.get).toHaveBeenCalledWith('/providers/anthropic/models')
      expect(response.provider).toBe('anthropic')
    })

    it('应该处理不存在的提供商', async () => {
      const mockError = { message: 'Provider not found' }
      apiClient.get.mockRejectedValue(mockError)

      await expect(modelsApi.getModels('nonexistent'))
        .rejects.toEqual(mockError)
    })
  })

  describe('getModel - 获取模型详情', () => {
    it('应该发送GET请求到/providers/:provider/models/:model端点', async () => {
      const mockResponse = {
        id: 'gpt-4',
        name: 'GPT-4',
        provider: 'openai',
        description: 'Most capable model',
        context_length: 8192,
        max_tokens: 4096,
        temperature: { min: 0, max: 2, default: 1 },
        enabled: true,
        pricing: {
          input: 0.03,
          output: 0.06,
          unit: 'per_1k_tokens'
        }
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await modelsApi.getModel('openai', 'gpt-4')

      expect(apiClient.get).toHaveBeenCalledWith('/providers/openai/models/gpt-4')
      expect(response.id).toBe('gpt-4')
      expect(response.context_length).toBe(8192)
    })

    it('应该包含定价信息', async () => {
      const mockResponse = {
        id: 'claude-3-opus',
        name: 'Claude 3 Opus',
        provider: 'anthropic',
        pricing: {
          input: 0.015,
          output: 0.075,
          unit: 'per_1k_tokens'
        }
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await modelsApi.getModel('anthropic', 'claude-3-opus')

      expect(response.pricing).toBeDefined()
      expect(response.pricing.input).toBe(0.015)
      expect(response.pricing.output).toBe(0.075)
    })
  })

  describe('testModel - 测试模型连接', () => {
    it('应该发送POST请求到/providers/:provider/models/:model/test端点', async () => {
      const mockResponse = {
        success: true,
        model: 'gpt-3.5-turbo',
        provider: 'openai',
        latency: 245,
        message: 'Connection successful'
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const response = await modelsApi.testModel('openai', 'gpt-3.5-turbo')

      expect(apiClient.post).toHaveBeenCalledWith('/providers/openai/models/gpt-3.5-turbo/test', {})
      expect(response.success).toBe(true)
    })

    it('应该支持带API密钥的测试', async () => {
      const mockResponse = {
        success: true,
        model: 'claude-3-opus',
        provider: 'anthropic'
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const response = await modelsApi.testModel('anthropic', 'claude-3-opus', 'sk-test-key')

      expect(apiClient.post).toHaveBeenCalledWith(
        '/providers/anthropic/models/claude-3-opus/test',
        { api_key: 'sk-test-key' }
      )
    })

    it('应该处理连接失败', async () => {
      const mockResponse = {
        success: false,
        error: 'Invalid API key'
      }
      apiClient.post.mockResolvedValue(mockResponse)

      const response = await modelsApi.testModel('openai', 'gpt-4', 'invalid-key')

      expect(response.success).toBe(false)
      expect(response.error).toBe('Invalid API key')
    })

    it('应该处理网络错误', async () => {
      const mockError = { message: 'Network timeout' }
      apiClient.post.mockRejectedValue(mockError)

      await expect(modelsApi.testModel('openai', 'gpt-4'))
        .rejects.toEqual(mockError)
    })
  })

  describe('getAllModels - 获取所有可用模型', () => {
    it('应该聚合所有提供商的模型', async () => {
      const mockResponse = {
        models: [
          {
            id: 'gpt-3.5-turbo',
            name: 'GPT-3.5 Turbo',
            provider: 'openai',
            enabled: true
          },
          {
            id: 'gpt-4',
            name: 'GPT-4',
            provider: 'openai',
            enabled: true
          },
          {
            id: 'claude-3-opus',
            name: 'Claude 3 Opus',
            provider: 'anthropic',
            enabled: true
          },
          {
            id: 'qwen-turbo',
            name: 'Qwen Turbo',
            provider: 'qwen',
            enabled: false
          }
        ]
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await modelsApi.getAllModels()

      expect(apiClient.get).toHaveBeenCalledWith('/models')
      expect(response.models).toHaveLength(4)
    })

    it('应该支持只返回启用的模型', async () => {
      const mockResponse = {
        models: [
          { id: 'gpt-3.5-turbo', provider: 'openai', enabled: true },
          { id: 'gpt-4', provider: 'openai', enabled: true },
          { id: 'qwen-turbo', provider: 'qwen', enabled: false }
        ]
      }
      apiClient.get.mockResolvedValue(mockResponse)

      const response = await modelsApi.getAllModels(true)

      expect(apiClient.get).toHaveBeenCalledWith('/models?enabled=true')
    })
  })
})
