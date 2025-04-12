import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useDocumentStore = defineStore('documents', () => {
  const documents = ref([])
  const loading = ref(false)
  const error = ref(null)
  const uploadProgress = ref(0)

  const uploadDocument = async (formData, onProgress) => {
    try {
      loading.value = true
      error.value = null
      uploadProgress.value = 0

      const response = await api.post('/documents/upload', formData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          uploadProgress.value = progress
          onProgress?.(progress)
        }
      })

      documents.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to upload document'
      throw err
    } finally {
      loading.value = false
    }
  }

  const processDocument = async (documentId) => {
    try {
      loading.value = true
      error.value = null

      const response = await api.post(`/documents/${documentId}/process`)
      const updatedDocument = response.data

      const index = documents.value.findIndex(doc => doc.id === documentId)
      if (index !== -1) {
        documents.value[index] = updatedDocument
      }

      return updatedDocument
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to process document'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getDocuments = async () => {
    try {
      loading.value = true
      error.value = null

      const response = await api.get('/documents')
      documents.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch documents'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getDocument = async (id) => {
    try {
      loading.value = true
      error.value = null

      const response = await api.get(`/documents/${id}`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch document'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteDocument = async (id) => {
    try {
      loading.value = true
      error.value = null

      await api.delete(`/documents/${id}`)
      documents.value = documents.value.filter(doc => doc.id !== id)
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to delete document'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateDocument = async (id, data) => {
    try {
      loading.value = true
      error.value = null

      const response = await api.put(`/documents/${id}`, data)
      const updatedDocument = response.data

      const index = documents.value.findIndex(doc => doc.id === id)
      if (index !== -1) {
        documents.value[index] = updatedDocument
      }

      return updatedDocument
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update document'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getDocumentShares = async (documentId) => {
    try {
      loading.value = true
      error.value = null

      const response = await api.get(`/documents/${documentId}/shares`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch document shares'
      throw err
    } finally {
      loading.value = false
    }
  }

  const shareDocument = async (documentId, data) => {
    try {
      loading.value = true
      error.value = null

      const response = await api.post(`/documents/${documentId}/shares`, data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to share document'
      throw err
    } finally {
      loading.value = false
    }
  }

  const removeShare = async (documentId, userId) => {
    try {
      loading.value = true
      error.value = null

      await api.delete(`/documents/${documentId}/shares/${userId}`)
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to remove share'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateSharePermission = async (documentId, userId, data) => {
    try {
      loading.value = true
      error.value = null

      const response = await api.put(`/documents/${documentId}/shares/${userId}`, data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update share permission'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getShareLink = async (documentId) => {
    try {
      loading.value = true
      error.value = null

      const response = await api.get(`/documents/${documentId}/share-link`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch share link'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateShareLink = async (documentId, data) => {
    try {
      loading.value = true
      error.value = null

      const response = await api.put(`/documents/${documentId}/share-link`, data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update share link'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    documents,
    loading,
    error,
    uploadProgress,
    uploadDocument,
    processDocument,
    getDocuments,
    getDocument,
    deleteDocument,
    updateDocument,
    getDocumentShares,
    shareDocument,
    removeShare,
    updateSharePermission,
    getShareLink,
    updateShareLink
  }
}) 