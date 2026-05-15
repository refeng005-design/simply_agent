<template>
  <div class="message-input">
    <div class="input-container">
      <div class="input-wrapper">
        <textarea
          ref="textareaRef"
          v-model="inputValue"
          :placeholder="placeholder"
          :disabled="isLoading"
          :maxlength="maxLength"
          rows="1"
          class="input-textarea"
          @input="handleInput"
          @keydown="handleKeydown"
          @focus="handleFocus"
          @blur="handleBlur"
        ></textarea>
        <div class="input-actions">
          <button class="action-button" title="上传文件" disabled>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
            </svg>
          </button>
          <button
            :class="['send-button', { active: canSend, sending: isLoading }]"
            :disabled="isLoading || !canSend"
            @click="handleSend"
          >
            <svg v-if="!isLoading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="input-footer">
        <div class="footer-left">
          <span class="char-count" :class="{ warning: remainingChars < 100, danger: remainingChars < 20 }">
            {{ remainingChars }}
          </span>
        </div>
        <div class="footer-right">
          <span class="hint">Enter 发送 · Shift + Enter 换行</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat.js'

const emit = defineEmits(['send'])
const store = useChatStore()

const textareaRef = ref(null)
const isFocused = ref(false)
const maxLength = 4000
const placeholder = '发送消息给 AI...'

const inputValue = computed({
  get: () => store.input,
  set: (value) => store.setInput(value)
})

const isLoading = computed(() => store.isLoading)
const remainingChars = computed(() => maxLength - inputValue.value.length)
const canSend = computed(() => inputValue.value.trim().length > 0)

function handleInput() {
  adjustHeight()
}

function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function handleSend() {
  if (!canSend.value) return

  const message = inputValue.value.trim()
  emit('send', message)
  store.clearInput()

  nextTick(() => {
    adjustHeight()
  })
}

function handleFocus() {
  isFocused.value = true
}

function handleBlur() {
  isFocused.value = false
}

function adjustHeight() {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    const scrollHeight = textareaRef.value.scrollHeight
    const maxHeight = 180
    textareaRef.value.style.height = Math.min(scrollHeight, maxHeight) + 'px'
  }
}

watch(() => store.input, () => {
  nextTick(() => {
    adjustHeight()
  })
})
</script>

<style scoped>
.message-input {
  display: flex;
  flex-direction: column;
  padding: 16px 24px 24px;
  background: transparent;
  position: relative;
  z-index: 5;
}

.input-container {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.input-wrapper {
  position: relative;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 16px;
  padding: 4px;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04),
              0 8px 32px rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-wrapper:focus-within {
  border-color: rgba(139, 92, 246, 0.4);
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.12),
              0 8px 32px rgba(139, 92, 246, 0.08),
              0 0 0 3px rgba(139, 92, 246, 0.08);
}

.input-textarea {
  flex: 1;
  min-height: 44px;
  max-height: 180px;
  padding: 12px 14px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  line-height: 1.5;
  resize: none;
  outline: none;
  background: transparent;
  color: #1E293B;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.input-textarea::placeholder {
  color: #94A3B8;
}

.input-textarea:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  padding-bottom: 8px;
  padding-right: 4px;
}

.action-button {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748B;
  transition: all 0.2s ease;
}

.action-button:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.15);
  color: #7C3AED;
}

.action-button:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.send-button {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(226, 232, 240, 0.5);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.send-button.active {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
  color: white;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.4);
}

.send-button.active:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.5);
}

.send-button.active:active {
  transform: translateY(0);
}

.send-button.sending {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.send-button:disabled {
  cursor: not-allowed;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding: 0 8px;
}

.footer-left,
.footer-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.char-count {
  font-size: 12px;
  color: #94A3B8;
  font-variant-numeric: tabular-nums;
}

.char-count.warning {
  color: #F59E0B;
}

.char-count.danger {
  color: #EF4444;
}

.hint {
  font-size: 12px;
  color: #94A3B8;
  opacity: 0.8;
}

/* Responsive */
@media (max-width: 768px) {
  .message-input {
    padding: 12px 16px 16px;
  }

  .hint {
    display: none;
  }
}

@media (max-width: 480px) {
  .input-textarea {
    font-size: 14px;
  }

  .action-button {
    display: none;
  }
}
</style>
