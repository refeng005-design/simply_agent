/**
 * API客户端配置测试
 *
 * 测试axios实例配置正确
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import axios from 'axios'


describe('api/client.js - API客户端配置', () => {
  let originalEnv

  beforeEach(() => {
    originalEnv = { ...import.meta.env }
  })

  afterEach(() => {
    // 恢复环境变量
    Object.assign(import.meta.env, originalEnv)
  })

  it('应该导出axios实例', async () => {
    const { apiClient } = await import('../src/api/client.js')

    expect(apiClient).toBeDefined()
    expect(apiClient.defaults).toBeDefined()
  })

  it('应该设置正确的baseURL', async () => {
    const { apiClient } = await import('../src/api/client.js')

    expect(apiClient.defaults.baseURL).toBe('/api')
  })

  it('应该设置正确的timeout', async () => {
    const { apiClient } = await import('../src/api/client.js')

    expect(apiClient.defaults.timeout).toBe(30000)
  })

  it('应该设置请求头为JSON', async () => {
    const { apiClient } = await import('../src/api/client.js')

    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json')
  })

  it('应该导出get/post/put/delete方法', async () => {
    const module = await import('../src/api/client.js')

    expect(module.apiClient.get).toBeDefined()
    expect(module.apiClient.post).toBeDefined()
    expect(module.apiClient.put).toBeDefined()
    expect(module.apiClient.delete).toBeDefined()
  })
})
