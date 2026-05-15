<template>
  <div class="settings-panel">
    <div class="panel-header">
      <h2>设置</h2>
      <button class="close-button" @click="handleClose">×</button>
    </div>

    <div class="panel-content">
      <section class="setting-section">
        <h3>模型配置</h3>
        <div class="form-group">
          <label>提供商</label>
          <select v-model="localProvider" class="form-control">
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="qwen">通义千问</option>
          </select>
        </div>
        <div class="form-group">
          <label>模型</label>
          <input v-model="localModel" type="text" class="form-control" placeholder="gpt-3.5-turbo" />
        </div>
        <div class="form-group">
          <label>API密钥</label>
          <input v-model="localApiKey" type="password" class="form-control" placeholder="sk-..." />
        </div>
      </section>

      <section class="setting-section">
        <h3>参数设置</h3>
        <div class="form-group">
          <label>温度: {{ localTemperature }}</label>
          <input
            v-model.number="localTemperature"
            type="range"
            min="0"
            max="1"
            step="0.1"
            class="form-control"
          />
        </div>
        <div class="form-group">
          <label>最大Token</label>
          <input v-model.number="localMaxTokens" type="number" class="form-control" min="1" max="32000" />
        </div>
      </section>

      <section class="setting-section">
        <h3>功能开关</h3>
        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input v-model="localRagEnabled" type="checkbox" name="rag" />
            <span>启用RAG（知识库检索）</span>
          </label>
        </div>
        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input v-model="localMemoryEnabled" type="checkbox" name="memory" />
            <span>启用对话记忆</span>
          </label>
        </div>
      </section>
    </div>

    <div class="panel-footer">
      <button class="save-button" @click="handleSave">保存设置</button>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings.js'

const emit = defineEmits(['close', 'save'])

const store = useSettingsStore()

const localProvider = computed({
  get: () => store.provider,
  set: (value) => store.setProvider(value)
})

const localModel = computed({
  get: () => store.model,
  set: (value) => store.setModel(value)
})

const localApiKey = computed({
  get: () => store.apiKey,
  set: (value) => store.setApiKey(value)
})

const localTemperature = computed({
  get: () => store.temperature,
  set: (value) => {
    store.setTemperature(Math.max(0, Math.min(1, value)))
  }
})

const localMaxTokens = computed({
  get: () => store.maxTokens,
  set: (value) => store.setMaxTokens(value)
})

const localRagEnabled = computed({
  get: () => store.ragEnabled,
  set: (value) => store.setRagEnabled(value)
})

const localMemoryEnabled = computed({
  get: () => store.memoryEnabled,
  set: (value) => store.setMemoryEnabled(value)
})

function handleClose() {
  emit('close')
}

function handleSave() {
  store.saveSettings()
  emit('save', store.toConfig())
}
</script>

<style scoped>
.settings-panel {
  width: 400px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.panel-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #333;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.setting-section {
  margin-bottom: 24px;
}

.setting-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-control:focus {
  border-color: #007aff;
}

.form-control[type="range"] {
  padding: 0;
}

.checkbox-group {
  margin-bottom: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label span {
  font-size: 14px;
  color: #333;
}

.panel-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.save-button {
  width: 100%;
  padding: 12px;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-button:hover {
  background-color: #0056b3;
}
</style>
