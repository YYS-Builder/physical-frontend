import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationService } from '@/services/notifications'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref([])
  const loading = ref(false)
  const error = ref(null)
  const connectionStatus = ref('disconnected')

  const unreadCount = computed(() => {
    return notifications.value.filter(n => !n.read).length
  })

  const getNotifications = async () => {
    loading.value = true
    error.value = null
    try {
      notifications.value = await notificationService.getNotifications()
    } catch (err) {
      error.value = 'Failed to fetch notifications'
      throw err
    } finally {
      loading.value = false
    }
  }

  const markAsRead = async (id) => {
    try {
      await notificationService.markAsRead(id)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
    } catch (err) {
      console.error('Failed to mark notification as read:', err)
      throw err
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead()
      notifications.value.forEach(n => n.read = true)
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err)
      throw err
    }
  }

  const deleteNotification = async (id) => {
    try {
      await notificationService.deleteNotification(id)
      notifications.value = notifications.value.filter(n => n.id !== id)
    } catch (err) {
      console.error('Failed to delete notification:', err)
      throw err
    }
  }

  const clearAll = async () => {
    try {
      await notificationService.clearAll()
      notifications.value = []
    } catch (err) {
      console.error('Failed to clear notifications:', err)
      throw err
    }
  }

  const addNotification = (notification) => {
    notifications.value.unshift(notification)
  }

  const setConnectionStatus = (status) => {
    connectionStatus.value = status
  }

  return {
    notifications,
    loading,
    error,
    connectionStatus,
    unreadCount,
    getNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
    addNotification,
    setConnectionStatus
  }
}) 