import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApi } from '@/services/api'

interface Collaborator {
  id: string
  name: string
  email: string
  avatar?: string
  status: 'online' | 'offline' | 'typing'
  lastSeen?: string
}

interface CollaborationSession {
  id: string
  documentId: string
  users: Collaborator[]
  lastActivity: string
}

export const useCollaborationStore = defineStore('collaboration', () => {
  const api = useApi()
  const activeSessions = ref<Record<string, CollaborationSession>>({})
  const typingUsers = ref<Record<string, string[]>>({})
  const lastSaved = ref<Record<string, string>>({})

  const getSession = computed(() => {
    return (documentId: string) => activeSessions.value[documentId]
  })

  const getSessionUsers = computed(() => {
    return (documentId: string) => activeSessions.value[documentId]?.users || []
  })

  const getTypingUsers = computed(() => {
    return (documentId: string) => typingUsers.value[documentId] || []
  })

  const getLastSaved = computed(() => {
    return (documentId: string) => lastSaved.value[documentId] || ''
  })

  const joinSession = async (documentId: string) => {
    try {
      const response = await api.post(`/documents/${documentId}/collaboration/join`)
      activeSessions.value[documentId] = response.data
      return response.data
    } catch (error) {
      console.error('Failed to join collaboration session:', error)
      throw error
    }
  }

  const leaveSession = async (documentId: string) => {
    try {
      await api.post(`/documents/${documentId}/collaboration/leave`)
      delete activeSessions.value[documentId]
      delete typingUsers.value[documentId]
      delete lastSaved.value[documentId]
    } catch (error) {
      console.error('Failed to leave collaboration session:', error)
      throw error
    }
  }

  const startTyping = async (documentId: string) => {
    try {
      await api.post(`/documents/${documentId}/collaboration/typing/start`)
      if (!typingUsers.value[documentId]) {
        typingUsers.value[documentId] = []
      }
      typingUsers.value[documentId].push('current-user')
    } catch (error) {
      console.error('Failed to start typing:', error)
      throw error
    }
  }

  const stopTyping = async (documentId: string) => {
    try {
      await api.post(`/documents/${documentId}/collaboration/typing/stop`)
      if (typingUsers.value[documentId]) {
        typingUsers.value[documentId] = typingUsers.value[documentId].filter(
          id => id !== 'current-user'
        )
      }
    } catch (error) {
      console.error('Failed to stop typing:', error)
      throw error
    }
  }

  const updateLastSaved = (documentId: string, timestamp: string) => {
    lastSaved.value[documentId] = timestamp
  }

  const handleUserJoined = (documentId: string, user: Collaborator) => {
    if (!activeSessions.value[documentId]) {
      activeSessions.value[documentId] = {
        id: documentId,
        documentId,
        users: [],
        lastActivity: new Date().toISOString()
      }
    }
    activeSessions.value[documentId].users.push(user)
  }

  const handleUserLeft = (documentId: string, userId: string) => {
    if (activeSessions.value[documentId]) {
      activeSessions.value[documentId].users = activeSessions.value[documentId].users.filter(
        user => user.id !== userId
      )
    }
  }

  const handleUserTyping = (documentId: string, userId: string) => {
    if (!typingUsers.value[documentId]) {
      typingUsers.value[documentId] = []
    }
    if (!typingUsers.value[documentId].includes(userId)) {
      typingUsers.value[documentId].push(userId)
    }
  }

  const handleUserStoppedTyping = (documentId: string, userId: string) => {
    if (typingUsers.value[documentId]) {
      typingUsers.value[documentId] = typingUsers.value[documentId].filter(
        id => id !== userId
      )
    }
  }

  return {
    activeSessions,
    typingUsers,
    lastSaved,
    getSession,
    getSessionUsers,
    getTypingUsers,
    getLastSaved,
    joinSession,
    leaveSession,
    startTyping,
    stopTyping,
    updateLastSaved,
    handleUserJoined,
    handleUserLeft,
    handleUserTyping,
    handleUserStoppedTyping
  }
}) 