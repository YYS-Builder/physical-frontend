import { useNotificationStore } from '@/stores/notifications'

class NotificationService {
  constructor() {
    this.socket = null
    this.store = useNotificationStore()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000 // 1 second
  }

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

  sendNotification(notification) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(notification))
    } else {
      console.error('WebSocket is not connected')
    }
  }
}

export const notificationService = new NotificationService() 