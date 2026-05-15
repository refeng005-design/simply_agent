<template>
  <div :class="['history-sidebar', { collapsed }]">
    <div class="sidebar-header">
      <Transition name="slide">
        <button v-if="!collapsed" class="new-chat-button" @click="handleNewChat">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>新建对话</span>
        </button>
      </Transition>
      <button :class="['toggle-button', { collapsed }]" @click="handleToggle" :title="collapsed ? '展开侧边栏' : '收起侧边栏'">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path v-if="!collapsed" d="M11 19l-7-7 7-7M18 19l-7-7 7-7"/>
          <path v-else d="M13 5l7 7-7 7M6 5l7 7-7 7"/>
        </svg>
      </button>
    </div>

    <Transition name="fade">
      <div v-if="!collapsed" class="sidebar-content">
        <div v-if="loading" class="loader-container">
          <div class="loader"></div>
        </div>

        <div v-else-if="conversations.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
          </div>
          <p>暂无对话历史</p>
        </div>

        <div v-else class="conversation-list">
          <div
            v-for="conv in conversations"
            :key="conv.id"
            :class="['conversation-item', { active: conv.id === currentConversationId }]"
            @click="handleSelect(conv.id)"
          >
            <div class="conversation-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <div class="conversation-info">
              <div class="conversation-title">{{ conv.title || '未命名对话' }}</div>
              <div class="conversation-meta">
                <span class="message-count">{{ conv.message_count || 0 }} 条消息</span>
              </div>
            </div>
            <button
              class="delete-button"
              @click.stop="handleDeleteClick(conv.id)"
              title="删除对话"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <button
          v-if="hasMore && !loading"
          class="load-more-button"
          @click="handleLoadMore"
        >
          <span>加载更多</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 9l6 6 6-6"/>
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat.js'

const props = defineProps({
  conversations: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  hasMore: {
    type: Boolean,
    default: false
  },
  collapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'delete', 'new', 'toggle', 'loadMore'])

const store = useChatStore()

const currentConversationId = computed(() => store.currentConversationId)

function handleSelect(convId) {
  emit('select', convId)
  store.setCurrentConversation(convId)
}

function handleDeleteClick(convId) {
  emit('delete', convId)
}

function handleNewChat() {
  emit('new')
  store.clearCurrentConversation()
  store.clearMessages()
}

function handleToggle() {
  emit('toggle')
}

function handleLoadMore() {
  emit('loadMore')
}
</script>

<style scoped>
.history-sidebar {
  width: 280px;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 20;
}

.history-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(180deg,
    rgba(139, 92, 246, 0.05) 0%,
    transparent 100%
  );
  pointer-events: none;
}

.history-sidebar.collapsed {
  width: 48px;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  display: flex;
  gap: 8px;
  align-items: center;
  position: relative;
  z-index: 1;
}

.new-chat-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.new-chat-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.new-chat-button:active {
  transform: translateY(0);
}

.toggle-button {
  width: 36px;
  height: 36px;
  padding: 0;
  background: rgba(148, 163, 184, 0.1);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748B;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.toggle-button:hover {
  background: rgba(139, 92, 246, 0.15);
  color: #7C3AED;
}

.toggle-button.collapsed {
  width: 32px;
  height: 32px;
  margin: 0 auto;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.sidebar-content::-webkit-scrollbar {
  width: 4px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.2);
  border-radius: 2px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.3);
}

.loader-container {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.loader {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(148, 163, 184, 0.15);
  border-top-color: #8B5CF6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 48px 16px;
  color: #94A3B8;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(148, 163, 184, 0.08);
  border-radius: 16px;
  color: #94A3B8;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
}

.conversation-item:hover {
  background: rgba(148, 163, 184, 0.08);
}

.conversation-item.active {
  background: rgba(139, 92, 246, 0.1);
}

.conversation-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: linear-gradient(180deg, #8B5CF6, #7C3AED);
  border-radius: 0 2px 2px 0;
}

.conversation-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 8px;
  color: #64748B;
  flex-shrink: 0;
}

.conversation-item.active .conversation-icon {
  background: rgba(139, 92, 246, 0.15);
  color: #7C3AED;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-item.active .conversation-title {
  color: #7C3AED;
}

.conversation-meta {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #94A3B8;
}

.delete-button {
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  color: #94A3B8;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.15s ease;
}

.conversation-item:hover .delete-button {
  opacity: 1;
}

.delete-button:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.load-more-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px;
  background: rgba(148, 163, 184, 0.08);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #64748B;
  margin-top: 8px;
  transition: all 0.15s ease;
}

.load-more-button:hover {
  background: rgba(148, 163, 184, 0.15);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* Responsive */
@media (max-width: 768px) {
  .history-sidebar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
  }

  .history-sidebar.collapsed {
    width: 0;
    overflow: hidden;
  }
}
</style>
