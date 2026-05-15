/**
 * Vue应用入口测试
 *
 * 测试main.js能正确创建和挂载Vue应用
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'


describe('main.js - Vue应用入口', () => {
  beforeEach(() => {
    // 每个测试前清除mock
    vi.clearAllMocks()
  })

  it('应该创建Vue应用实例', async () => {
    const { createApp } = await import('../src/main.js')

    expect(createApp).toBeDefined()
    expect(typeof createApp).toBe('function')
  })

  it('应该使用App组件作为根组件', async () => {
    const mainModule = await import('../src/main.js')

    // main.js 应该导出App组件
    expect(mainModule.App).toBeDefined()
  })

  it('应该将应用挂载到#app元素', async () => {
    // 创建DOM元素
    document.body.innerHTML = '<div id="app"></div>'

    // 动态导入main.js以触发挂载
    await import('../src/main.js')

    const appElement = document.getElementById('app')

    expect(appElement).not.toBeNull()
    // 挂载后应该有子元素
    expect(appElement.children.length).toBeGreaterThan(0)
  })

  it('导出createApp函数供测试使用', async () => {
    const { createApp } = await import('../src/main.js')

    expect(createApp).toBeDefined()
    expect(typeof createApp).toBe('function')
  })
})
