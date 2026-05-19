<template>
  <div class="chat-window">
    <header class="chat-header">
      <div class="header-left">
        <div class="brand">
          <div class="brand-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#brand-gradient)" stroke="white" stroke-width="1.5"/>
              <path d="M2 17L12 22L22 17" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="brand-gradient" x1="2" y1="2" x2="22" y2="12" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#A78BFA"/>
                  <stop offset="100%" stop-color="#60A5FA"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span class="brand-name">Simply Agent</span>
        </div>
        <ModelSelector
          :models="availableModels"
          @select="handleModelSelect"
        />
      </div>
      <div class="header-right">
        <button class="icon-button" @click="toggleSettings" title="设置">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3m15.364 6.364l-4.243-4.243M9.879 14.121L5.636 18.364M18.364 18.364l-4.243-4.243M9.879 9.879L5.636 5.636"/>
          </svg>
        </button>
      </div>
    </header>

    <main class="chat-main">
      <MessageList />
      <MessageInput @send="handleSendMessage" />
    </main>

    <Transition name="fade">
      <div v-if="showSettings" class="settings-overlay" @click.self="closeSettings">
        <SettingsPanel @close="closeSettings" @save="handleSettingsSave" />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat.js'
import { useSettingsStore } from '@/stores/settings.js'
import chatApi from '@/api/chat.js'
import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
import ModelSelector from './ModelSelector.vue'
import SettingsPanel from './SettingsPanel.vue'

const emit = defineEmits(['message-sent'])

const chatStore = useChatStore()
const settingsStore = useSettingsStore()

const showSettings = ref(false)
const windowWidth = ref(window.innerWidth)
const isProcessing = ref(false)

const availableModels = [
  { id: 'mimo-v2.5-pro', name: 'MiMo V2.5 Pro (最强)', provider: 'openai' },
  { id: 'mimo-v2.5', name: 'MiMo V2.5', provider: 'openai' },
  { id: 'mimo-v2-pro', name: 'MiMo V2 Pro', provider: 'openai' },
  { id: 'mimo-v2-omni', name: 'MiMo V2 Omni', provider: 'openai' }
]

const isLoading = computed(() => chatStore.isLoading || isProcessing.value)
const isStreaming = computed(() => chatStore.isStreaming)
const currentProvider = computed(() => settingsStore.provider)
const currentModel = computed(() => settingsStore.model || 'gpt-3.5-turbo')

const isMobile = computed(() => windowWidth.value < 768)

function handleModelSelect(modelId) {
  settingsStore.setModel(modelId)
}

async function handleSendMessage(message) {
  if (!message.trim() || isProcessing.value) return

  // Add user message
  const userMessageId = `msg-${Date.now()}`
  chatStore.addMessage({
    id: userMessageId,
    role: 'user',
    content: message,
    timestamp: new Date().toISOString()
  })

  isProcessing.value = true
  chatStore.setLoading(true)

  // Create assistant message placeholder
  const assistantMessageId = `msg-${Date.now() + 1}`
  chatStore.startStreamingMessage(assistantMessageId)
  chatStore.setStreaming(true)

  try {
    // Get current model info
    const modelInfo = availableModels.find(m => m.id === currentModel.value)
    const provider = modelInfo?.provider || 'openai'

    // Call backend API
    const stream = chatApi.sendMessageStream({
      message: message,
      model: currentModel.value,
      provider: provider,
      conversation_id: chatStore.currentConversationId,
      rag_enabled: settingsStore.ragEnabled,
      memory_enabled: settingsStore.memoryEnabled
    })

    // Handle streaming response
    stream.on('message', (data) => {
      // data 是解析后的对象，包含 content 或 error
      console.log('[ChatWindow] Received data:', data)

      if (data.conversation_id) {
        console.log('[ChatWindow] Setting conversation ID:', data.conversation_id)
        chatStore.setCurrentConversation(data.conversation_id)
        return
      }

      // 检查结束标记 - 修复：使用 data === '[DONE]' 而不是 data.data
      const isDone = data === '[DONE]' || data.data === '[DONE]'
      if (isDone) {
        console.log('[ChatWindow] Stream done, completing message')
        chatStore.completeStreamingMessage()
        isProcessing.value = false
        chatStore.setLoading(false)
        emit('message-sent')
        return
      }

      if (data.content) {
        console.log('[ChatWindow] Appending content:', data.content)
        chatStore.appendStreamingContent(data.content)
        console.log('[ChatWindow] Current messages:', chatStore.messages)
      }

      if (data.error) {
        console.log('[ChatWindow] Error received:', data.error)
        chatStore.setError(data.error)
        chatStore.completeStreamingMessage()
        isProcessing.value = false
        chatStore.setLoading(false)
      }
    })

    // Set timeout to close stream
    setTimeout(() => {
      stream.close()
      if (chatStore.isStreaming) {
        chatStore.completeStreamingMessage()
        isProcessing.value = false
        chatStore.setLoading(false)
      }
    }, 60000) // 60 second timeout

  } catch (error) {
    console.error('Failed to send message:', error)
    chatStore.setError(error.message || '发送消息失败')
    chatStore.completeStreamingMessage()
    isProcessing.value = false
    chatStore.setLoading(false)
  }
}

function toggleSettings() {
  showSettings.value = !showSettings.value
}

function closeSettings() {
  showSettings.value = false
}

function handleSettingsSave(config) {
  console.log('Settings saved:', config)
  closeSettings()
}

function handleResize() {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)

  // 如果当前模型不在可用模型列表中，自动设置为第一个可用模型
  const currentModelId = settingsStore.model
  const isValidModel = availableModels.some(m => m.id === currentModelId)
  if (!isValidModel && availableModels.length > 0) {
    settingsStore.setModel(availableModels[0].id)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  position: relative;
}

.chat-window::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 300px;
  background: linear-gradient(180deg,
    rgba(139, 92, 246, 0.08) 0%,
    rgba(59, 130, 246, 0.04) 50%,
    transparent 100%
  );
  pointer-events: none;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  min-height: 64px;
  position: relative;
  z-index: 10;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3),
              inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.brand-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg,
    rgba(255, 255, 255, 0.2) 0%,
    transparent 50%
  );
  border-radius: 12px;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #7C3AED 0%, #3B82F6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.header-right {
  display: flex;
  gap: 8px;
}

.icon-button {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  color: #64748B;
}

.icon-button:hover {
  background: rgba(139, 92, 246, 0.15);
  color: #7C3AED;
  transform: translateY(-1px);
}

.icon-button:active {
  transform: translateY(0);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

/* Fade transition for settings overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .chat-header {
    padding: 12px 16px;
    min-height: 56px;
  }

  .header-left {
    gap: 12px;
  }

  .brand-name {
    display: none;
  }

  .brand-icon {
    width: 36px;
    height: 36px;
  }

  .icon-button {
    width: 36px;
    height: 36px;
  }
}

@media (max-width: 480px) {
  .header-left {
    gap: 8px;
  }
}
</style>
