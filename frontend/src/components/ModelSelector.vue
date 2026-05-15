<template>
  <div class="model-selector">
    <div class="selector-wrapper">
      <div class="selector-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
      </div>
      <select
        v-model="selectedModel"
        :disabled="disabled || loading"
        class="model-select"
        @change="handleChange"
      >
        <option v-if="filteredModels.length === 0" value="">
          无可用模型
        </option>
        <option
          v-for="model in filteredModels"
          :key="model.id"
          :value="model.id"
        >
          {{ model.name }}
        </option>
      </select>
      <div v-if="loading" class="loader"></div>
      <div v-else class="selector-arrow">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M6 9l6 6 6-6"/>
        </svg>
      </div>
    </div>
    <div :class="['provider-badge', providerClass]">
      <span class="provider-dot"></span>
      {{ providerLabel }}
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings.js'

const props = defineProps({
  models: {
    type: Array,
    default: () => [
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
      { id: 'gpt-4', name: 'GPT-4', provider: 'openai' },
      { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'anthropic' },
      { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'anthropic' },
      { id: 'qwen-turbo', name: 'Qwen Turbo', provider: 'qwen' },
      { id: 'qwen-plus', name: 'Qwen Plus', provider: 'qwen' }
    ]
  },
  provider: {
    type: String,
    default: null
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select'])

const store = useSettingsStore()

const selectedModel = computed({
  get: () => store.model,
  set: (value) => store.setModel(value)
})

const currentProvider = computed(() => props.provider || store.provider)

const providerLabel = computed(() => {
  const labels = {
    openai: 'OpenAI',
    anthropic: 'Claude',
    qwen: 'Qwen'
  }
  return labels[currentProvider.value] || currentProvider.value
})

const providerClass = computed(() => {
  return `provider-${currentProvider.value}`
})

const filteredModels = computed(() => {
  if (props.provider) {
    return props.models.filter(m => m.provider === props.provider)
  }
  return props.models
})

function handleChange() {
  emit('select', selectedModel.value)
}

watch(() => props.provider, (newProvider) => {
  if (newProvider) {
    store.setProvider(newProvider)
  }
})
</script>

<style scoped>
.model-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selector-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.selector-icon {
  position: absolute;
  left: 10px;
  color: #64748B;
  pointer-events: none;
}

.model-select {
  padding: 8px 36px 8px 32px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.8);
  color: #334155;
  cursor: pointer;
  outline: none;
  transition: all 0.15s ease;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  min-width: 160px;
}

.model-select:hover {
  border-color: rgba(139, 92, 246, 0.3);
  background: rgba(255, 255, 255, 0.95);
}

.model-select:focus {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.model-select:disabled {
  background: rgba(248, 250, 252, 0.8);
  color: #94A3B8;
  cursor: not-allowed;
}

.model-select::-ms-expand {
  display: none;
}

.model-select option {
  padding: 8px;
  background: white;
}

.selector-arrow {
  position: absolute;
  right: 10px;
  color: #94A3B8;
  pointer-events: none;
  transition: transform 0.2s ease;
}

.model-select:focus + .loader + .selector-arrow,
.model-select:focus + .selector-arrow {
  transform: translateY(2px);
}

.loader {
  position: absolute;
  right: 10px;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(148, 163, 184, 0.2);
  border-top-color: #8B5CF6;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.provider-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.provider-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.provider-openai {
  background: rgba(16, 163, 127, 0.1);
  color: #0EA5A9;
}

.provider-anthropic {
  background: rgba(139, 92, 246, 0.1);
  color: #8B5CF6;
}

.provider-qwen {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
}

/* Responsive */
@media (max-width: 768px) {
  .model-select {
    min-width: 120px;
    font-size: 12px;
    padding: 7px 30px 7px 28px;
  }

  .provider-badge {
    display: none;
  }
}

@media (max-width: 480px) {
  .selector-wrapper {
    max-width: 100px;
  }

  .model-select {
    min-width: auto;
    max-width: 100px;
  }

  .selector-icon {
    left: 8px;
  }

  .model-select {
    padding-left: 26px;
  }
}
</style>
