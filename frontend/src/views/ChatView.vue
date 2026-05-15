<template>
  <div class="chat-view">
    <Transition name="fade">
      <div v-if="loading" class="page-loader">
        <div class="loader-content">
          <div class="loader-spinner"></div>
          <p>加载中...</p>
        </div>
      </div>
    </Transition>

    <HistorySidebar
      :conversations="conversations"
      :loading="loadingConversations"
      :has-more="hasMoreConversations"
      :collapsed="sidebarCollapsed"
      @select="handleSelectConversation"
      @delete="handleDeleteConversation"
      @new="handleNewConversation"
      @toggle="toggleSidebar"
      @loadMore="loadMoreConversations"
    />

    <ChatWindow @message-sent="loadConversations" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat.js'
import { useSettingsStore } from '@/stores/settings.js'
import HistorySidebar from '@/components/HistorySidebar.vue'
import ChatWindow from '@/components/ChatWindow.vue'
import historyApi from '@/api/history.js'

const chatStore = useChatStore()
const settingsStore = useSettingsStore()

const loading = ref(false)
const loadingConversations = ref(false)
const conversations = ref([])
const hasMoreConversations = ref(false)
const sidebarCollapsed = ref(false)
const windowWidth = ref(window.innerWidth)

const isMobile = computed(() => windowWidth.value < 768)

async function loadConversations() {
  loadingConversations.value = true
  try {
    const result = await historyApi.getConversations(50, 0)
    conversations.value = result.conversations || []
    hasMoreConversations.value = result.conversations && result.conversations.length >= 50
  } catch (error) {
    console.error('Failed to load conversations:', error)
    conversations.value = []
  } finally {
    loadingConversations.value = false
  }
}

async function loadMoreConversations() {
  // Implement load more logic
}

function handleSelectConversation(convId) {
  chatStore.setCurrentConversation(convId)
}

async function handleDeleteConversation(convId) {
  try {
    conversations.value = conversations.value.filter(c => c.id !== convId)

    if (chatStore.currentConversationId === convId) {
      chatStore.clearCurrentConversation()
      chatStore.clearMessages()
    }
  } catch (error) {
    console.error('Failed to delete conversation:', error)
  }
}

function handleNewConversation() {
  chatStore.clearCurrentConversation()
  chatStore.clearMessages()
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function handleResize() {
  windowWidth.value = window.innerWidth
  if (windowWidth.value < 768) {
    sidebarCollapsed.value = true
  }
}

onMounted(() => {
  loadConversations()
  window.addEventListener('resize', handleResize)
  handleResize()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.chat-view {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  overflow: hidden;
  position: relative;
}

.chat-view::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 80%;
  height: 150%;
  background: radial-gradient(
    ellipse at center,
    rgba(139, 92, 246, 0.04) 0%,
    transparent 70%
  );
  pointer-events: none;
}

.chat-view::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 60%;
  height: 100%;
  background: radial-gradient(
    ellipse at center,
    rgba(59, 130, 246, 0.03) 0%,
    transparent 70%
  );
  pointer-events: none;
}

.page-loader {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loader-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loader-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(148, 163, 184, 0.15);
  border-top-color: #8B5CF6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loader-content p {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .chat-view {
    flex-direction: column;
  }
}
</style>
