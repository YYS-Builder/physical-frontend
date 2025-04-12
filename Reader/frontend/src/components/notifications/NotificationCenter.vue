<template>
  <div class="notification-center">
    <div class="notification-header">
      <h2>Notifications</h2>
      <div class="notification-actions">
        <button @click="markAllAsRead" class="btn btn-sm btn-outline">
          Mark all as read
        </button>
        <button @click="clearAll" class="btn btn-sm btn-outline">
          Clear all
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading notifications...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="getNotifications" class="btn btn-sm btn-primary">
        Retry
      </button>
    </div>

    <div v-else-if="notifications.length === 0" class="empty-state">
      <p>No notifications</p>
    </div>

    <div v-else class="notification-list">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-item"
        :class="{ unread: !notification.read }"
      >
        <div class="notification-icon">
          <i :class="getNotificationIcon(notification.type)"></i>
        </div>
        <div class="notification-content">
          <h3>{{ notification.title }}</h3>
          <p>{{ notification.message }}</p>
          <span class="timestamp">{{ formatDate(notification.created_at) }}</span>
        </div>
        <div class="notification-actions">
          <button
            v-if="!notification.read"
            @click="markAsRead(notification.id)"
            class="btn btn-sm btn-outline"
          >
            Mark as read
          </button>
          <button
            @click="deleteNotification(notification.id)"
            class="btn btn-sm btn-outline"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import { notificationService } from '@/services/notifications'

export default {
  name: 'NotificationCenter',
  setup() {
    const store = useNotificationStore()
    const loading = ref(false)
    const error = ref(null)
    const connectionStatus = ref('disconnected')

    const getNotifications = async () => {
      loading.value = true
      error.value = null
      try {
        const notifications = await notificationService.getNotifications()
        store.notifications = notifications
      } catch (err) {
        error.value = 'Failed to load notifications'
        console.error('Error loading notifications:', err)
      } finally {
        loading.value = false
      }
    }

    const markAsRead = async (id) => {
      try {
        await notificationService.markAsRead(id)
        const notification = store.notifications.find(n => n.id === id)
        if (notification) {
          notification.read = true
        }
      } catch (err) {
        console.error('Error marking notification as read:', err)
        error.value = 'Failed to mark notification as read'
      }
    }

    const markAllAsRead = async () => {
      try {
        await notificationService.markAllAsRead()
        store.notifications.forEach(n => n.read = true)
      } catch (err) {
        console.error('Error marking all notifications as read:', err)
        error.value = 'Failed to mark all notifications as read'
      }
    }

    const deleteNotification = async (id) => {
      try {
        await notificationService.deleteNotification(id)
        store.notifications = store.notifications.filter(n => n.id !== id)
      } catch (err) {
        console.error('Error deleting notification:', err)
        error.value = 'Failed to delete notification'
      }
    }

    const clearAll = async () => {
      try {
        await notificationService.clearAll()
        store.notifications = []
      } catch (err) {
        console.error('Error clearing notifications:', err)
        error.value = 'Failed to clear notifications'
      }
    }

    const getNotificationIcon = (type) => {
      const icons = {
        info: 'fas fa-info-circle',
        success: 'fas fa-check-circle',
        warning: 'fas fa-exclamation-circle',
        error: 'fas fa-times-circle',
        share: 'fas fa-share-alt',
        comment: 'fas fa-comment',
        mention: 'fas fa-at',
        system: 'fas fa-cog'
      }
      return icons[type] || icons.info
    }

    const formatDate = (date) => {
      const now = new Date()
      const notificationDate = new Date(date)
      const diff = now - notificationDate

      if (diff < 60000) { // Less than 1 minute
        return 'Just now'
      } else if (diff < 3600000) { // Less than 1 hour
        const minutes = Math.floor(diff / 60000)
        return `${minutes}m ago`
      } else if (diff < 86400000) { // Less than 1 day
        const hours = Math.floor(diff / 3600000)
        return `${hours}h ago`
      } else {
        return notificationDate.toLocaleDateString()
      }
    }

    let unsubscribe
    onMounted(() => {
      getNotifications()
      unsubscribe = notificationService.subscribeToNotifications((count) => {
        if (count > store.unreadCount) {
          getNotifications() // Refresh notifications if new ones are available
        }
      })
    })

    onUnmounted(() => {
      if (unsubscribe) {
        unsubscribe()
      }
    })

    return {
      loading,
      error,
      connectionStatus,
      notifications: store.notifications,
      unreadCount: store.unreadCount,
      getNotifications,
      markAsRead,
      markAllAsRead,
      deleteNotification,
      clearAll,
      getNotificationIcon,
      formatDate
    }
  }
}
</script>

<style scoped>
.notification-center {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.notification-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.notification-actions {
  display: flex;
  gap: 0.5rem;
}

.loading,
.error,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.error {
  color: var(--color-error);
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 600px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: var(--border-radius);
  background-color: var(--color-background);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.notification-item:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.notification-item.unread {
  background-color: var(--color-primary-light);
  border-left: 4px solid var(--color-primary);
}

.notification-icon {
  font-size: 1.5rem;
  color: var(--color-primary);
  min-width: 2rem;
  text-align: center;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-content h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.notification-content p {
  margin: 0;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timestamp {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .notification-item {
    flex-direction: column;
  }

  .notification-actions {
    margin-top: 1rem;
    justify-content: flex-end;
  }

  .notification-content p {
    white-space: normal;
  }
}
</style> 