/**
 * 模型API
 *
 * 提供模型管理相关的API调用函数
 */
import apiClient from './client.js'

/**
 * 获取所有提供商列表
 * @returns {Promise<Object>} 提供商列表
 */
async function getProviders() {
  return apiClient.get('/providers')
}

/**
 * 获取指定提供商的模型列表
 * @param {string} provider - 提供商ID (openai, anthropic, qwen)
 * @returns {Promise<Object>} 模型列表
 */
async function getModels(provider) {
  return apiClient.get(`/providers/${provider}/models`)
}

/**
 * 获取模型详细信息
 * @param {string} provider - 提供商ID
 * @param {string} modelId - 模型ID
 * @returns {Promise<Object>} 模型详情
 */
async function getModel(provider, modelId) {
  return apiClient.get(`/providers/${provider}/models/${modelId}`)
}

/**
 * 测试模型连接
 * @param {string} provider - 提供商ID
 * @param {string} modelId - 模型ID
 * @param {string} [apiKey] - API密钥（可选，用于测试）
 * @returns {Promise<Object>} 测试结果
 */
async function testModel(provider, modelId, apiKey = null) {
  const payload = apiKey ? { api_key: apiKey } : {}
  return apiClient.post(`/providers/${provider}/models/${modelId}/test`, payload)
}

/**
 * 获取所有可用模型（跨所有提供商）
 * @param {boolean} [enabledOnly=false] - 是否只返回启用的模型
 * @returns {Promise<Object>} 所有模型列表
 */
async function getAllModels(enabledOnly = false) {
  let url = '/models'
  if (enabledOnly) {
    url += '?enabled=true'
  }
  return apiClient.get(url)
}

export default {
  getProviders,
  getModels,
  getModel,
  testModel,
  getAllModels
}
