/**
 * Simply Agent Frontend - API客户端配置
 *
 * 创建预配置的axios实例用于后端API通信
 * 支持自动重试、指数退避等优化
 */
import axios from 'axios'


// 导出配置和函数供测试使用
export { RETRY_CONFIG, shouldRetry, isIdempotentMethod, getRetryDelay }


// 重试配置
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000,      // 初始重试延迟（毫秒）
  maxRetryDelay: 10000,  // 最大重试延迟
  backoffMultiplier: 2,  // 指数退避倍数
  // 幂等方法列表（可以安全重试）
  idempotentMethods: ['get', 'head', 'put', 'delete', 'options']
}


/**
 * 判断是否应该重试
 */
function shouldRetry(error, retryCount, config) {
  // 超过最大重试次数
  if (retryCount >= (config?.maxRetries || RETRY_CONFIG.maxRetries)) {
    return false
  }

  // 没有响应对象（网络错误）
  if (!error.response) {
    return true
  }

  const status = error.response.status

  // 5xx 服务器错误应该重试
  if (status >= 500 && status < 600) {
    return true
  }

  // 429 Too Many Requests 应该重试
  if (status === 429) {
    return true
  }

  // 4xx 客户端错误不重试（除非配置了特定重试）
  if (status >= 400 && status < 500) {
    return false
  }

  return false
}


/**
 * 检查请求方法是否幂等
 */
function isIdempotentMethod(config) {
  const method = (config.method || 'get').toLowerCase()
  return RETRY_CONFIG.idempotentMethods.includes(method)
}


/**
 * 计算重试延迟（指数退避）
 */
function getRetryDelay(retryCount, config) {
  const baseDelay = config?.retryDelay || RETRY_CONFIG.retryDelay
  const multiplier = config?.backoffMultiplier || RETRY_CONFIG.backoffMultiplier
  const maxDelay = config?.maxRetryDelay || RETRY_CONFIG.maxRetryDelay

  // 指数退避：delay * (multiplier ^ retryCount)
  let delay = baseDelay * Math.pow(multiplier, retryCount)

  // 添加随机抖动（±25%）避免雷群效应
  const jitter = delay * 0.25 * (Math.random() * 2 - 1)
  delay = delay + jitter

  // 确保最终值不超过最大延迟
  delay = Math.min(delay, maxDelay)

  return Math.max(0, delay)
}


/**
 * 延迟函数
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}


// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})


// 添加重试配置到客户端
apiClient.retryConfig = RETRY_CONFIG


// 请求拦截器 - 添加认证token等
apiClient.interceptors.request.use(
  (config) => {
    // 可以从localStorage获取token
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 初始化重试计数
    config._retryCount = 0
    config._retryConfig = {
      ...RETRY_CONFIG,
      ...config.retryConfig
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)


// 响应拦截器 - 统一错误处理和重试逻辑
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const config = error.config || {}

    // 如果没有config或者已经重试过多次，直接拒绝
    if (!config._retryConfig) {
      return Promise.reject(error)
    }

    const retryCount = config._retryCount || 0

    // 检查是否应该重试
    if (shouldRetry(error, retryCount, config._retryConfig)) {
      // 对于非幂等方法，默认不重试（除非明确配置）
      if (!isIdempotentMethod(config) && !config._retryConfig.forceRetry) {
        console.warn(`Skipping retry for non-idempotent method: ${config.method}`)
        return Promise.reject(error.response?.data || error.message)
      }

      // 增加重试计数
      config._retryCount = retryCount + 1

      // 计算重试延迟
      const retryDelay = getRetryDelay(retryCount, config._retryConfig)

      console.warn(
        `Request failed, retrying (${config._retryCount}/${config._retryConfig.maxRetries}) ` +
        `after ${retryDelay.toFixed(0)}ms...`,
        error.message
      )

      // 等待后重试
      await delay(retryDelay)

      // 重新发起请求
      return apiClient.request(config)
    }

    // 统一错误处理
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // 未授权，清除token并跳转登录
          localStorage.removeItem('auth_token')
          break
        case 403:
          console.error('没有权限访问')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 429:
          console.error('请求过于频繁，请稍后再试')
          break
        case 500:
          console.error('服务器内部错误')
          break
        default:
          console.error(`请求失败: ${status}`)
      }

      return Promise.reject(data || error.message)
    }

    return Promise.reject(error)
  }
)


export default apiClient
