/**
 * 聊天API
 *
 * 提供聊天相关的API调用函数
 */
import apiClient from './client.js'

/**
 * 发送消息（非流式）
 * @param {Object} request - 请求参数
 * @param {string} request.message - 用户消息
 * @param {string} request.model - 模型名称
 * @param {string} request.provider - 提供商
 * @param {string} [request.conversation_id] - 对话ID（可选）
 * @param {boolean} [request.rag_enabled] - 是否启用RAG
 * @param {boolean} [request.memory_enabled] - 是否启用记忆
 * @param {number} [request.temperature] - 温度参数
 * @param {number} [request.max_tokens] - 最大token数
 * @returns {Promise<Object>} 响应数据
 */
async function sendMessage(request) {
  // 转换为后端期望的格式
  const payload = {
    messages: [
      { role: 'user', content: request.message }
    ],
    model: request.model,
    provider: request.provider || 'openai',
    conversation_id: request.conversation_id,
    use_rag: request.rag_enabled || false,
    memory_enabled: request.memory_enabled !== false,
    ...(request.temperature !== undefined && { temperature: request.temperature }),
    ...(request.max_tokens !== undefined && { max_tokens: request.max_tokens })
  }
  return apiClient.post('/chat', payload)
}

/**
 * 发送消息（流式/SSE）
 * @param {Object} request - 请求参数
 * @returns {Object} 流式响应对象，包含on和close方法
 */
function sendMessageStream(request) {
  // 转换为后端期望的格式
  const payload = {
    messages: [
      { role: 'user', content: request.message }
    ],
    model: request.model,
    provider: request.provider || 'openai',
    conversation_id: request.conversation_id,
    use_rag: request.rag_enabled || false,
    memory_enabled: request.memory_enabled !== false,
    ...(request.temperature !== undefined && { temperature: request.temperature }),
    ...(request.max_tokens !== undefined && { max_tokens: request.max_tokens })
  }

  // 使用 fetch API 进行流式请求
  let abortController = null
  let reader = null

  const stream = {
    on: async (eventName, callback) => {
      if (eventName !== 'message') {
        console.warn('Only "message" event is supported')
        return
      }

      try {
        abortController = new AbortController()

        const response = await fetch('/api/chat/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload),
          signal: abortController.signal
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // 处理 SSE 格式
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // 保留未完成的行

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim()
              if (data === '[DONE]') {
                callback({ data: '[DONE]' })
                continue
              }

              try {
                const parsed = JSON.parse(data)
                // 直接传递解析后的对象
                callback(parsed)
              } catch (e) {
                console.error('Failed to parse SSE data:', data, e)
              }
            }
          }
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('Stream aborted')
        } else {
          console.error('Stream error:', error)
          callback({ error: error.message })
        }
      }
    },
    close: () => {
      if (abortController) {
        abortController.abort()
      }
      if (reader) {
        reader.cancel()
      }
    }
  }

  return stream
}

/**
 * 获取对话历史列表
 * @param {number} [limit=20] - 每页数量
 * @param {number} [offset=0] - 偏移量
 * @returns {Promise<Object>} 对话列表
 */
async function getConversationHistory(limit = 20, offset = 0) {
  return apiClient.get(`/conversations?limit=${limit}&offset=${offset}`)
}

/**
 * 获取指定对话的消息列表
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 消息列表
 */
async function getMessages(conversationId) {
  return apiClient.get(`/conversations/${conversationId}/messages`)
}

/**
 * 创建新对话
 * @param {string} [title] - 对话标题（可选）
 * @returns {Promise<Object>} 新创建的对话
 */
async function createConversation(title = null) {
  const payload = title ? { title } : {}
  return apiClient.post('/conversations', payload)
}

/**
 * 删除对话
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 删除结果
 */
async function deleteConversation(conversationId) {
  return apiClient.delete(`/conversations/${conversationId}`)
}

/**
 * 清空对话消息
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 清空结果
 */
async function clearConversation(conversationId) {
  return apiClient.post(`/conversations/${conversationId}/clear`)
}

export default {
  sendMessage,
  sendMessageStream,
  getConversationHistory,
  getMessages,
  createConversation,
  deleteConversation,
  clearConversation
}
