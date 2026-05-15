/**
 * ConfirmDialog组件测试
 *
 * 测试确认对话框组件的核心功能：
 * - 显示/隐藏对话框
 * - 确认/取消操作
 * - 自定义标题和消息
 * - 事件触发
 * - 键盘快捷键（ESC关闭）
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

describe('ConfirmDialog.vue - 确认对话框组件', () => {
  let ConfirmDialog
  let pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const module = await import('@/components/ConfirmDialog.vue')
    ConfirmDialog = module.default
  })

  describe('基础渲染', () => {
    it('应该成功渲染组件', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: false
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('默认情况下不应该显示对话框', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: false
        }
      })

      const dialog = wrapper.find('.confirm-dialog')
      expect(dialog.exists()).toBe(true)
      // 对话框应该被隐藏
      expect(dialog.classes()).toContain('hidden')
    })

    it('show为true时应该显示对话框', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const dialog = wrapper.find('.confirm-dialog')
      expect(dialog.classes()).not.toContain('hidden')
    })

    it('应该有遮罩层', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const overlay = wrapper.find('.dialog-overlay')
      expect(overlay.exists()).toBe(true)
    })
  })

  describe('内容显示', () => {
    it('应该显示默认标题', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const title = wrapper.find('.dialog-title')
      expect(title.text()).toBe('确认操作')
    })

    it('应该显示自定义标题', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true,
          title: '删除对话'
        }
      })

      const title = wrapper.find('.dialog-title')
      expect(title.text()).toBe('删除对话')
    })

    it('应该显示默认消息', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const message = wrapper.find('.dialog-message')
      expect(message.text()).toBe('确定要执行此操作吗？')
    })

    it('应该显示自定义消息', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true,
          message: '删除后无法恢复，确定删除吗？'
        }
      })

      const message = wrapper.find('.dialog-message')
      expect(message.text()).toBe('删除后无法恢复，确定删除吗？')
    })
  })

  describe('按钮显示', () => {
    it('应该有取消和确认按钮', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const buttons = wrapper.findAll('.dialog-button')
      expect(buttons.length).toBe(2)
    })

    it('应该显示默认按钮文本', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const buttons = wrapper.findAll('.dialog-button')
      expect(buttons[0].text()).toBe('取消')
      expect(buttons[1].text()).toBe('确认')
    })

    it('应该显示自定义确认按钮文本', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true,
          confirmText: '删除'
        }
      })

      const buttons = wrapper.findAll('.dialog-button')
      expect(buttons[1].text()).toBe('删除')
    })

    it('应该显示自定义取消按钮文本', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true,
          cancelText: '保留'
        }
      })

      const buttons = wrapper.findAll('.dialog-button')
      expect(buttons[0].text()).toBe('保留')
    })
  })

  describe('确认操作', () => {
    it('点击确认按钮应该触发confirm事件', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const confirmButton = wrapper.findAll('.dialog-button')[1]
      await confirmButton.trigger('click')

      expect(wrapper.emitted('confirm')).toBeTruthy()
    })

    it('点击确认按钮应该关闭对话框', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const confirmButton = wrapper.findAll('.dialog-button')[1]
      await confirmButton.trigger('click')

      expect(wrapper.emitted('update:show')).toBeTruthy()
      expect(wrapper.emitted('update:show')[0]).toEqual([false])
    })
  })

  describe('取消操作', () => {
    it('点击取消按钮应该触发cancel事件', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const cancelButton = wrapper.findAll('.dialog-button')[0]
      await cancelButton.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('点击取消按钮应该关闭对话框', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const cancelButton = wrapper.findAll('.dialog-button')[0]
      await cancelButton.trigger('click')

      expect(wrapper.emitted('update:show')).toBeTruthy()
      expect(wrapper.emitted('update:show')[0]).toEqual([false])
    })
  })

  describe('遮罩层操作', () => {
    it('点击遮罩层应该触发cancel事件', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const overlay = wrapper.find('.dialog-overlay')
      await overlay.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('点击遮罩层应该关闭对话框', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        }
      })

      const overlay = wrapper.find('.dialog-overlay')
      await overlay.trigger('click')

      expect(wrapper.emitted('update:show')).toBeTruthy()
    })

    it('closeOnOverlayClick为false时不应该关闭', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true,
          closeOnOverlayClick: false
        }
      })

      const overlay = wrapper.find('.dialog-overlay')
      await overlay.trigger('click')

      expect(wrapper.emitted('update:show')).toBeFalsy()
    })
  })

  describe('键盘快捷键', () => {
    it('按ESC键应该关闭对话框', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        },
        attachTo: document.body
      })

      await wrapper.trigger('keydown', { key: 'Escape' })

      expect(wrapper.emitted('update:show')).toBeTruthy()

      wrapper.unmount()
    })

    it('按ESC键应该触发cancel事件', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true
        },
        attachTo: document.body
      })

      await wrapper.trigger('keydown', { key: 'Escape' })

      expect(wrapper.emitted('cancel')).toBeTruthy()

      wrapper.unmount()
    })
  })

  describe('危险操作样式', () => {
    it('danger为true时确认按钮应该是危险样式', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true,
          danger: true
        }
      })

      const confirmButton = wrapper.findAll('.dialog-button')[1]
      expect(confirmButton.classes()).toContain('danger')
    })

    it('danger为false时确认按钮不应该有危险样式', () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: true,
          danger: false
        }
      })

      const confirmButton = wrapper.findAll('.dialog-button')[1]
      expect(confirmButton.classes()).not.toContain('danger')
    })
  })

  describe('响应式更新', () => {
    it('show prop变化时应该更新显示状态', async () => {
      const wrapper = mount(ConfirmDialog, {
        global: {
          plugins: [pinia]
        },
        props: {
          show: false
        }
      })

      let dialog = wrapper.find('.confirm-dialog')
      expect(dialog.classes()).toContain('hidden')

      await wrapper.setProps({ show: true })
      await wrapper.vm.$nextTick()

      dialog = wrapper.find('.confirm-dialog')
      expect(dialog.classes()).not.toContain('hidden')
    })
  })
})
