/**
 * API客户端重试逻辑测试
 *
 * 测试请求失败时的自动重试功能
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('API Client Retry Logic', () => {
  let apiClient
  let mockRequest

  beforeEach(async () => {
    vi.clearAllMocks()

    // 创建mock的request函数
    mockRequest = vi.fn()

    // Mock axios.create返回一个模拟的客户端
    vi.mocked(axios.create).mockReturnValue({
      request: mockRequest,
      get: mockRequest,
      post: mockRequest,
      put: mockRequest,
      delete: mockRequest,
      interceptors: {
        request: { use: vi.fn((fn) => fn({ headers: {} })) },
        response: { use: vi.fn((onSuccess, onError) => {
          // 保存错误处理器用于测试
          mockRequest._errorHandler = onError
        })}
      },
      retryConfig: {
        maxRetries: 3,
        retryDelay: 1000,
        backoffMultiplier: 2
      }
    })

    // 动态导入客户端
    const module = await import('@/api/client')
    apiClient = module.default
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Retry Configuration', () => {
    it('should have retry configuration', () => {
      expect(apiClient.retryConfig).toBeDefined()
      expect(apiClient.retryConfig.maxRetries).toBe(3)
      expect(apiClient.retryConfig.retryDelay).toBe(1000)
    })

    it('should have idempotent methods list', async () => {
      // 导入RETRY_CONFIG来验证
      const { RETRY_CONFIG } = await import('@/api/client')
      expect(RETRY_CONFIG.idempotentMethods).toContain('get')
      expect(RETRY_CONFIG.idempotentMethods).toContain('put')
      expect(RETRY_CONFIG.idempotentMethods).toContain('delete')
    })
  })

  describe('Retry Logic Functions', () => {
    it('should calculate exponential backoff delay', async () => {
      const { getRetryDelay } = await import('@/api/client')

      const delay1 = getRetryDelay(0, {})
      const delay2 = getRetryDelay(1, {})
      const delay3 = getRetryDelay(2, {})

      // 验证指数增长
      expect(delay2).toBeGreaterThan(delay1)
      expect(delay3).toBeGreaterThan(delay2)
    })

    it('should respect max retry delay', async () => {
      const { getRetryDelay } = await import('@/api/client')

      const delay = getRetryDelay(100, { maxRetryDelay: 5000 })

      expect(delay).toBeLessThanOrEqual(5000)
    })

    it('should add jitter to delay', async () => {
      const { getRetryDelay } = await import('@/api/client')

      const delays = []
      for (let i = 0; i < 10; i++) {
        delays.push(getRetryDelay(1, {}))
      }

      // 验证延迟有变化（由于jitter）
      const uniqueDelays = new Set(delays)
      expect(uniqueDelays.size).toBeGreaterThan(1)
    })

    it('should identify idempotent methods correctly', async () => {
      const { isIdempotentMethod } = await import('@/api/client')

      expect(isIdempotentMethod({ method: 'GET' })).toBe(true)
      expect(isIdempotentMethod({ method: 'get' })).toBe(true)
      expect(isIdempotentMethod({ method: 'PUT' })).toBe(true)
      expect(isIdempotentMethod({ method: 'POST' })).toBe(false)
      expect(isIdempotentMethod({ method: 'post' })).toBe(false)
      expect(isIdempotentMethod({})).toBe(true) // 默认GET
    })

    it('should determine when to retry', async () => {
      const { shouldRetry } = await import('@/api/client')

      // 网络错误（无响应）
      expect(shouldRetry(new Error('Network error'), 0, {})).toBe(true)

      // 5xx错误
      expect(shouldRetry({ response: { status: 500 } }, 0, {})).toBe(true)
      expect(shouldRetry({ response: { status: 503 } }, 0, {})).toBe(true)

      // 429限流
      expect(shouldRetry({ response: { status: 429 } }, 0, {})).toBe(true)

      // 4xx客户端错误（不重试）
      expect(shouldRetry({ response: { status: 400 } }, 0, {})).toBe(false)
      expect(shouldRetry({ response: { status: 404 } }, 0, {})).toBe(false)

      // 超过最大重试次数
      expect(shouldRetry(new Error('Network error'), 3, { maxRetries: 3 })).toBe(false)
    })
  })

  describe('Request Interceptor', () => {
    it('should add auth token when available', async () => {
      localStorage.setItem('auth_token', 'test-token')

      // 重新导入以触发拦截器
      vi.resetModules()
      vi.mocked(axios.create).mockReturnValue({
        request: vi.fn(),
        interceptors: {
          request: { use: vi.fn((fn) => {
            const config = fn({ headers: {} })
            expect(config.headers.Authorization).toBe('Bearer test-token')
          })},
          response: { use: vi.fn() }
        },
        retryConfig: {}
      })

      await import('@/api/client')

      localStorage.removeItem('auth_token')
    })

    it('should initialize retry count on request', async () => {
      vi.resetModules()
      const capturedConfig = {}

      vi.mocked(axios.create).mockReturnValue({
        request: vi.fn(),
        interceptors: {
          request: { use: vi.fn((fn) => {
            const config = fn({ headers: {}, method: 'get' })
            capturedConfig._retryCount = config._retryCount
            capturedConfig._retryConfig = config._retryConfig
          })},
          response: { use: vi.fn() }
        },
        retryConfig: {}
      })

      await import('@/api/client')

      expect(capturedConfig._retryCount).toBe(0)
      expect(capturedConfig._retryConfig).toBeDefined()
    })
  })

  describe('Per-Request Retry Override', () => {
    it('should allow custom retry config per request', async () => {
      vi.resetModules()

      const capturedConfig = {}

      vi.mocked(axios.create).mockReturnValue({
        request: vi.fn(),
        interceptors: {
          request: { use: vi.fn((fn) => {
            const config = fn({
              headers: {},
              method: 'get',
              retryConfig: { maxRetries: 5 }
            })
            capturedConfig._retryConfig = config._retryConfig
          })},
          response: { use: vi.fn() }
        },
        retryConfig: {}
      })

      await import('@/api/client')

      expect(capturedConfig._retryConfig.maxRetries).toBe(5)
    })
  })
})
