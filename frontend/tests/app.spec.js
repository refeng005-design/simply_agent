/**
 * App根组件测试
 *
 * 测试App组件能正确渲染
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'


describe('App.vue - 根组件', () => {
  it('应该成功渲染组件', async () => {
    const App = (await import('../src/App.vue')).default

    const wrapper = mount(App, {
      global: {
        stubs: {
          'router-view': true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('应该有根元素div', async () => {
    const App = (await import('../src/App.vue')).default

    const wrapper = mount(App, {
      global: {
        stubs: {
          'router-view': true
        }
      }
    })

    const rootDiv = wrapper.find('div')

    expect(rootDiv.exists()).toBe(true)
  })

  it('应该包含应用标题', async () => {
    const App = (await import('../src/App.vue')).default

    const wrapper = mount(App, {
      global: {
        stubs: {
          'router-view': true
        }
      }
    })

    expect(wrapper.text()).toContain('Simply Agent')
  })

  it('应该导出组件定义', async () => {
    const module = await import('../src/App.vue')

    expect(module.default).toBeDefined()
    expect(typeof module.default).toBe('object')
  })
})
