<template>
  <div class="collaboration-status">
    <div class="status-header">
      <h4>Active Collaborators</h4>
      <div class="user-count">{{ users.length }} active</div>
    </div>
    
    <div class="user-list">
      <div
        v-for="user in users"
        :key="user.id"
        class="user-item"
      >
        <div class="user-avatar">
          <img
            v-if="user.avatar"
            :src="user.avatar"
            :alt="user.name"
          />
          <div v-else class="avatar-placeholder">
            {{ user.name.charAt(0) }}
          </div>
        </div>
        
        <div class="user-info">
          <div class="user-name">{{ user.name }}</div>
          <div class="user-status" :class="statusClass(user.status)">
            {{ user.status }}
          </div>
        </div>
        
        <div class="user-actions">
          <button
            v-if="user.id !== currentUserId"
            class="action-button"
            @click="startChat(user.id)"
          >
            Chat
          </button>
        </div>
      </div>
    </div>
    
    <div class="status-footer">
      <div class="typing-indicator" v-if="typingUsers.length">
        {{ typingText }}
      </div>
      <div class="last-saved" v-if="lastSaved">
        Last saved {{ lastSaved }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

interface Collaborator {
  id: string
  name: string
  avatar?: string
  status: string
}

export default defineComponent({
  name: 'CollaborationStatus',
  props: {
    users: {
      type: Array as () => Collaborator[],
      required: true
    },
    typingUsers: {
      type: Array as () => string[],
      default: () => []
    },
    lastSaved: {
      type: String,
      default: ''
    },
    currentUserId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const typingText = computed(() => {
      if (props.typingUsers.length === 1) {
        return `${props.typingUsers[0]} is typing...`
      } else if (props.typingUsers.length > 1) {
        return 'Multiple people are typing...'
      }
      return ''
    })
    
    const statusClass = (status: string) => {
      return {
        'status-active': status === 'active',
        'status-idle': status === 'idle',
        'status-away': status === 'away'
      }
    }
    
    const startChat = (userId: string) => {
      // TODO: Implement chat functionality
      console.log('Starting chat with user:', userId)
    }
    
    return {
      typingText,
      statusClass,
      startChat
    }
  }
})
</script>

<style scoped>
.collaboration-status {
  padding: 1rem;
  background-color: var(--color-background-soft);
  border-radius: 8px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.user-count {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background-color: var(--color-background-mute);
  border-radius: 4px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary);
  color: white;
  font-weight: 500;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: var(--color-text);
}

.user-status {
  font-size: 0.75rem;
  color: var(--color-text-light);
}

.status-active {
  color: var(--color-success);
}

.status-idle {
  color: var(--color-warning);
}

.status-away {
  color: var(--color-text-light);
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  padding: 0.25rem 0.5rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
}

.status-footer {
  margin-top: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--color-text-light);
}

.typing-indicator {
  color: var(--color-primary);
}

.last-saved {
  color: var(--color-text-light);
}
</style> 