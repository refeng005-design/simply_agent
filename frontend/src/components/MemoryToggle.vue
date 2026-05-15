<template>
  <div class="memory-toggle-container memory-toggle">
    <span class="toggle-label">记忆</span>
    <button
      class="toggle-button"
      :class="{ enabled: memoryEnabled, loading }"
      :disabled="loading"
      :role="role"
      :aria-checked="String(memoryEnabled)"
      :aria-busy="String(loading)"
      :title="memoryEnabled ? '记忆已启用' : '记忆已禁用'"
      @click="handleClick"
      @keydown.space.prevent="handleClick"
      @keydown.enter.prevent="handleClick"
    >
      <span class="toggle-slider">
        <span v-if="loading" class="loading-spinner"></span>
      </span>
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  conversationId: {
    type: String,
    required: true
  },
  memoryEnabled: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  role: {
    type: String,
    default: 'switch'
  }
})

const emit = defineEmits(['toggle'])

const handleClick = () => {
  if (!props.loading) {
    emit('toggle', !props.memoryEnabled)
  }
}
</script>

<style scoped>
.memory-toggle-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-label {
  font-size: 14px;
  color: #666;
  user-select: none;
}

.toggle-button {
  position: relative;
  width: 44px;
  height: 24px;
  background: #ccc;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  padding: 2px;
}

.toggle-button:focus {
  outline: 2px solid #4a9eff;
  outline-offset: 2px;
}

.toggle-button.enabled {
  background: #4caf50;
}

.toggle-button.loading {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-button:disabled {
  cursor: not-allowed;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-button.enabled .toggle-slider {
  transform: translateX(20px);
}

.loading-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #ccc;
  border-top-color: #666;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
