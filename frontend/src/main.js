/**
 * Simply Agent Frontend - Vue应用入口
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 创建并挂载Vue应用
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 挂载到DOM
app.mount('#app')

// 导出供测试使用
export { app as createApp, App }
