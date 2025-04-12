import { api } from './api'
import { useNotificationStore } from '@/stores/notifications'

class NotificationService {
  constructor() {
    this.socket = null
    this.store = useNotificationStore()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
  }

  // REST API Methods
  async getNotifications(params = {}) {
    const response = await api.get('/notifications', { params })
    return response.data
  }

  async markAsRead(id) {
    const response = await api.patch(`/notifications/${id}/read`)
    return response.data
  }

  async markAllAsRead() {
    const response = await api.patch('/notifications/read-all')
    return response.data
  }

  async deleteNotification(id) {
    await api.delete(`/notifications/${id}`)
  }

  async clearAll() {
    await api.delete('/notifications')
  }

  async getUnreadCount() {
    const response = await api.get('/notifications/unread-count')
    return response.data.count
  }

  // WebSocket Methods
  connect() {
    if (this.socket) {
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    this.socket = new WebSocket(`${protocol}//${host}/ws/notifications`)

    this.socket.onopen = () => {
      console.log('WebSocket connection established')
      this.reconnectAttempts = 0
    }

    this.socket.onmessage = (event) => {
      try {
        const notification = JSON.parse(event.data)
        this.store.addNotification(notification)
      } catch (error) {
        console.error('Error parsing notification:', error)
      }
    }

    this.socket.onclose = () => {
      console.log('WebSocket connection closed')
      this.socket = null
      this.attemptReconnect()
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        this.connect()
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  // Fallback polling method
  subscribeToNotifications(callback) {
    if ('WebSocket' in window) {
      this.connect()
      return () => this.disconnect()
    } else {
      // Fallback to polling if WebSocket is not available
      const interval = setInterval(async () => {
        const count = await this.getUnreadCount()
        callback(count)
      }, 30000)
      return () => clearInterval(interval)
    }
  }
}

export const notificationService = new NotificationService() 