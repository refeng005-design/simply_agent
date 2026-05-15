/**
 * 聊天状态管理 Store
 *
 * 管理聊天相关的所有状态：
 * - 消息列表
 * - 当前对话
 * - 加载状态
 * - 流式响应
 * - 输入内容
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const currentConversationId = ref(null)
  const messages = ref([])
  const isLoading = ref(false)
  const isStreaming = ref(false)
  const input = ref('')
  const error = ref(null)

  // 消息管理
  function addMessage(message) {
    messages.value.push({ ...message })
  }

  function clearMessages() {
    messages.value = []
  }

  function deleteMessage(messageId) {
    const index = messages.value.findIndex(m => m.id === messageId)
    if (index !== -1) {
      messages.value.splice(index, 1)
    }
  }

  // 对话管理
  function setCurrentConversation(conversationId) {
    currentConversationId.value = conversationId
  }

  function clearCurrentConversation() {
    currentConversationId.value = null
  }

  function loadConversation(conversationId, messageHistory) {
    currentConversationId.value = conversationId
    messages.value = [...messageHistory]
  }

  // 加载状态
  function setLoading(loading) {
    isLoading.value = loading
  }

  function setStreaming(streaming) {
    isStreaming.value = streaming
  }

  // 输入管理
  function setInput(value) {
    input.value = value
  }

  function clearInput() {
    input.value = ''
  }

  function appendInput(value) {
    input.value += value
  }

  // 流式响应处理
  let streamingMessageId = null

  function startStreamingMessage(messageId) {
    streamingMessageId = messageId
    messages.value.push({
      id: messageId,
      role: 'assistant',
      content: ''
    })
  }

  function appendStreamingContent(content) {
    if (streamingMessageId) {
      const message = messages.value.find(m => m.id === streamingMessageId)
      if (message) {
        message.content += content
      }
    }
  }

  function completeStreamingMessage() {
    streamingMessageId = null
    isStreaming.value = false
  }

  // 错误处理
  function setError(errorMessage) {
    error.value = errorMessage
  }

  function clearError() {
    error.value = null
  }

  // 重置所有状态
  function $reset() {
    currentConversationId.value = null
    messages.value = []
    isLoading.value = false
    isStreaming.value = false
    input.value = ''
    error.value = null
    streamingMessageId = null
  }

  return {
    // 状态
    currentConversationId,
    messages,
    isLoading,
    isStreaming,
    input,
    error,
    // 方法
    addMessage,
    clearMessages,
    deleteMessage,
    setCurrentConversation,
    clearCurrentConversation,
    loadConversation,
    setLoading,
    setStreaming,
    setInput,
    clearInput,
    appendInput,
    startStreamingMessage,
    appendStreamingContent,
    completeStreamingMessage,
    setError,
    clearError,
    $reset
  }
})
