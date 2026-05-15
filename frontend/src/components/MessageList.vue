<template>
  <div class="message-list" ref="listContainer">
    <Transition name="fade">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-illustration">
          <div class="floating-shapes">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
          </div>
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 12H8.01M12 12H12.01M16 12H16.01M21 12C21 16.4183 16.9706 20 12 20C7.02944 20 3 16.4183 3 12C3 7.58172 7.02944 4 12 4C16.9706 4 21 7.58172 21 12Z" stroke="url(#empty-gradient)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="empty-gradient" x1="3" y1="4" x2="21" y2="20" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#A78BFA"/>
                  <stop offset="100%" stop-color="#60A5FA"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
        <h2 class="empty-title">开始一段新对话</h2>
        <p class="empty-description">向 AI 助手提问任何问题，获取智能回答</p>
        <div class="suggestion-chips">
          <button
            v-for="(suggestion, index) in suggestions"
            :key="index"
            class="suggestion-chip"
            @click="handleSuggestion(suggestion)"
          >
            <span class="chip-icon">{{ suggestion.icon }}</span>
            {{ suggestion.text }}
          </button>
        </div>
      </div>
    </Transition>

    <!-- Messages with simplified layout (no virtual scroll) -->
    <TransitionGroup name="message" tag="div" class="messages-container">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message-wrapper', message.role]"
        :data-message-id="message.id"
      >
        <div class="message-avatar">
          <div v-if="message.role === 'user'" class="avatar user-avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
          <div v-else class="avatar ai-avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
        </div>
        <div :class="['message', message.role]">
          <div class="message-content" v-html="formatMessage(message.content)"></div>
          <div v-if="isStreaming && message.id === streamingMessageId" class="streaming-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <div class="message-meta">
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { computed, watch, nextTick, ref, onMounted, onUnmounted, shallowRef } from 'vue'
import { useChatStore } from '@/stores/chat.js'

// Performance optimization config
const VIRTUAL_SCROLL_THRESHOLD = 100
const ESTIMATED_MESSAGE_HEIGHT = 120
const BATCH_UPDATE_DELAY = 16
const SCROLL_THROTTLE_DELAY = 50
const INPUT_DEBOUNCE_DELAY = 100
const VISIBLE_BUFFER = 5

// Export config for testing
const virtualScrollEnabled = ref(true)
const batchUpdateEnabled = ref(true)
const scrollThrottleEnabled = ref(true)
const useRAF = ref(true)
const inputDebounceEnabled = ref(true)

defineExpose({
  virtualScrollEnabled,
  batchUpdateEnabled,
  scrollThrottleEnabled,
  useRAF,
  inputDebounceEnabled
})

const store = useChatStore()
const listContainer = ref(null)

// Virtual scroll state
const scrollTop = ref(0)
const containerHeight = ref(0)
const messageOffsets = shallowRef(new Map())

// Batch update state
let pendingUpdates = []
let batchUpdateTimer = null
let rafId = null

// Throttle state
let lastScrollTime = 0
let scrollThrottleTimer = null

// Debounce state
let inputDebounceTimer = null

// Suggestion chips for empty state
const suggestions = [
  { icon: '💡', text: '帮我写一段代码' },
  { icon: '📝', text: '解释一个概念' },
  { icon: '🔍', text: '分析数据' },
  { icon: '✨', text: '创意头脑风暴' }
]

const messages = computed(() => store.messages)
const isStreaming = computed(() => store.isStreaming)

const streamingMessageId = computed(() => {
  if (!isStreaming.value) return null
  const lastMessage = messages.value[messages.value.length - 1]
  return lastMessage?.id || null
})

// Virtual scroll computed
const visibleMessages = computed(() => {
  if (!virtualScrollEnabled.value || messages.value.length <= VIRTUAL_SCROLL_THRESHOLD) {
    return messages.value
  }

  const startIndex = Math.max(0, Math.floor(scrollTop.value / ESTIMATED_MESSAGE_HEIGHT) - VISIBLE_BUFFER)
  const endIndex = Math.min(
    messages.value.length,
    Math.ceil((scrollTop.value + containerHeight.value) / ESTIMATED_MESSAGE_HEIGHT) + VISIBLE_BUFFER
  )

  return messages.value.slice(startIndex, endIndex)
})

function getMessageOffset(messageId) {
  const index = messages.value.findIndex(m => m.id === messageId)
  return index * ESTIMATED_MESSAGE_HEIGHT
}

function updateContainerHeight() {
  if (listContainer.value) {
    containerHeight.value = listContainer.value.clientHeight
  }
}

function handleScroll() {
  if (listContainer.value) {
    scrollTop.value = listContainer.value.scrollTop
  }
}

function scheduleScroll(callback) {
  if (!useRAF.value) {
    callback()
    return
  }

  if (rafId) {
    cancelAnimationFrame(rafId)
  }

  rafId = requestAnimationFrame(() => {
    callback()
    rafId = null
  })
}

function throttledScrollToBottom() {
  if (!scrollThrottleEnabled.value) {
    scrollToBottom()
    return
  }

  const now = Date.now()
  if (now - lastScrollTime >= SCROLL_THROTTLE_DELAY) {
    lastScrollTime = now
    scheduleScroll(scrollToBottom)
  }
}

async function scrollToBottom() {
  await nextTick()
  if (listContainer.value) {
    // Use direct scrollTop for more reliable scrolling within container
    listContainer.value.scrollTop = listContainer.value.scrollHeight
  }
}

function processBatchUpdates() {
  if (pendingUpdates.length === 0) return

  const updates = [...pendingUpdates]
  pendingUpdates = []

  updates.forEach(update => update())

  batchUpdateTimer = null
}

function debouncedInputHandler() {
  if (!inputDebounceEnabled.value) {
    throttledScrollToBottom()
    return
  }

  if (inputDebounceTimer) {
    clearTimeout(inputDebounceTimer)
  }

  inputDebounceTimer = setTimeout(() => {
    throttledScrollToBottom()
    inputDebounceTimer = null
  }, INPUT_DEBOUNCE_DELAY)
}

function queueUpdate(update) {
  if (!batchUpdateEnabled.value) {
    update()
    return
  }

  pendingUpdates.push(update)

  if (!batchUpdateTimer) {
    batchUpdateTimer = setTimeout(processBatchUpdates, BATCH_UPDATE_DELAY)
  }
}

// Format message content (basic markdown-like formatting)
function formatMessage(content) {
  if (!content) return ''
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
}

// Format timestamp
function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function handleSuggestion(suggestion) {
  store.setInput(suggestion.text)
}

watch(messages, () => {
  queueUpdate(() => {
    throttledScrollToBottom()
  })
}, { deep: true })

watch(() => store.input, () => {
  if (isStreaming.value) {
    debouncedInputHandler()
  }
})

onMounted(() => {
  updateContainerHeight()
  if (listContainer.value) {
    listContainer.value.addEventListener('scroll', handleScroll, { passive: true })
  }
  window.addEventListener('resize', updateContainerHeight)
})

onUnmounted(() => {
  if (batchUpdateTimer) {
    clearTimeout(batchUpdateTimer)
  }
  if (rafId) {
    cancelAnimationFrame(rafId)
  }
  if (inputDebounceTimer) {
    clearTimeout(inputDebounceTimer)
  }
  if (listContainer.value) {
    listContainer.value.removeEventListener('scroll', handleScroll)
  }
  window.removeEventListener('resize', updateContainerHeight)
})
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  scroll-behavior: smooth;
}

.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: transparent;
}

.message-list::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-illustration {
  position: relative;
  margin-bottom: 32px;
}

.floating-shapes {
  position: absolute;
  width: 200px;
  height: 200px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
}

.shape-1 {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #A78BFA, #60A5FA);
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  animation: float 6s ease-in-out infinite;
}

.shape-2 {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #60A5FA, #34D399);
  bottom: 20px;
  right: 20px;
  animation: float 8s ease-in-out infinite reverse;
}

.shape-3 {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #F472B6, #A78BFA);
  bottom: 0;
  left: 20px;
  animation: float 7s ease-in-out infinite 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) translateX(-50%); }
  50% { transform: translateY(-20px) translateX(-50%); }
}

.empty-icon {
  position: relative;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
  border-radius: 50%;
  margin: 0 auto;
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.2),
                0 0 40px rgba(139, 92, 246, 0.1);
  }
  50% {
    box-shadow: 0 0 0 20px rgba(139, 92, 246, 0),
                0 0 60px rgba(139, 92, 246, 0.15);
  }
}

.empty-title {
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: 15px;
  color: #64748B;
  margin: 0 0 32px 0;
  max-width: 320px;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 480px;
}

.suggestion-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 18px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 12px;
  font-size: 14px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.suggestion-chip:hover {
  background: rgba(139, 92, 246, 0.08);
  border-color: rgba(139, 92, 246, 0.3);
  color: #7C3AED;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);
}

.chip-icon {
  font-size: 16px;
}

/* Message Wrapper */
.message-wrapper {
  display: flex;
  gap: 12px;
  max-width: 85%;
  will-change: transform;
  contain: content;
  backface-visibility: hidden;
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-wrapper.assistant {
  align-self: flex-start;
}

/* Message Avatar */
.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
  color: white;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.ai-avatar {
  background: linear-gradient(135deg, #F1F5F9, #E2E8F0);
  color: #64748B;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

/* Message Bubble */
.message {
  display: flex;
  flex-direction: column;
  padding: 14px 18px;
  border-radius: 16px;
  position: relative;
  word-wrap: break-word;
  white-space: pre-wrap;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.message.user {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 12px rgba(139, 92, 246, 0.25),
              inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.message.user::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  border-radius: 16px 16px 0 0;
}

.message.assistant {
  background: rgba(255, 255, 255, 0.9);
  color: #334155;
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.message-content {
  font-size: 15px;
  line-height: 1.6;
}

.message-content :deep(strong) {
  font-weight: 600;
}

.message-content :deep(em) {
  font-style: italic;
  opacity: 0.9;
}

.message-content :deep(code) {
  background: rgba(0, 0, 0, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
}

.message.user .message-content :deep(code) {
  background: rgba(0, 0, 0, 0.15);
}

/* Message Meta */
.message-meta {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-time {
  font-size: 11px;
  opacity: 0.6;
}

.message.user .message-time {
  color: white;
}

.message.assistant .message-time {
  color: #94A3B8;
}

/* Streaming Indicator */
.streaming-indicator {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  padding-left: 0;
}

.message.user .streaming-indicator {
  justify-content: flex-end;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.message.user .dot {
  background-color: rgba(255, 255, 255, 0.6);
}

.message.assistant .dot {
  background-color: #CBD5E1;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
.dot:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Transitions */
.fade-enter-active {
  transition: opacity 0.3s ease;
}

.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.message-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.message-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Responsive */
@media (max-width: 768px) {
  .message-list {
    padding: 16px;
  }

  .message-wrapper {
    max-width: 90%;
  }

  .empty-title {
    font-size: 20px;
  }

  .empty-description {
    font-size: 14px;
  }

  .suggestion-chips {
    flex-direction: column;
  }

  .suggestion-chip {
    width: 100%;
    justify-content: center;
  }
}
</style>
