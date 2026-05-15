/**
 * 历史API
 *
 * 提供对话历史管理相关的API调用函数
 */
import apiClient from './client.js'

/**
 * 获取对话列表
 * @param {number} [limit=20] - 每页数量
 * @param {number} [offset=0] - 偏移量
 * @param {string} [search] - 搜索关键词（可选）
 * @returns {Promise<Object>} 对话列表
 */
async function getConversations(limit = 20, offset = 0, search = '') {
  let url = `/conversations?limit=${limit}&offset=${offset}`
  if (search) {
    url += `&search=${encodeURIComponent(search)}`
  }
  return apiClient.get(url)
}

/**
 * 获取对话详情
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 对话详情
 */
async function getConversation(conversationId) {
  return apiClient.get(`/conversations/${conversationId}`)
}

/**
 * 删除单个对话
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 删除结果
 */
async function deleteConversation(conversationId) {
  return apiClient.delete(`/conversations/${conversationId}`)
}

/**
 * 批量删除对话
 * @param {string[]} conversationIds - 对话ID列表
 * @returns {Promise<Object>} 删除结果
 */
async function deleteConversations(conversationIds) {
  return apiClient.delete('/conversations/batch', {
    data: { ids: conversationIds }
  })
}

/**
 * 清空对话消息
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 清空结果
 */
async function clearConversation(conversationId) {
  return apiClient.post(`/conversations/${conversationId}/clear`)
}

/**
 * 更新对话标题
 * @param {string} conversationId - 对话ID
 * @param {string} title - 新标题
 * @returns {Promise<Object>} 更新结果
 */
async function updateConversationTitle(conversationId, title) {
  return apiClient.post(`/conversations/${conversationId}`, {
    title
  })
}

/**
 * 导出对话
 * @param {string} conversationId - 对话ID
 * @param {string} [format='json'] - 导出格式 (json, markdown, txt)
 * @returns {Promise<Object>} 导出内容
 */
async function exportConversation(conversationId, format = 'json') {
  return apiClient.get(`/conversations/${conversationId}/export?format=${format}`)
}

export default {
  getConversations,
  getConversation,
  deleteConversation,
  deleteConversations,
  clearConversation,
  updateConversationTitle,
  exportConversation
}
