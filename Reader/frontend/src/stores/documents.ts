import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/services/api'

interface Document {
  id: string
  name: string
  type: string
  size: number
  createdAt: string
  updatedAt: string
}

interface DocumentChunk {
  id: string
  content: string
  index: number
  totalChunks: number
}

interface SentimentAnalysis {
  sentiment: string
  score: number
  summary: string
  keywords: string[]
}

interface Entity {
  id: string
  text: string
  type: string
  confidence: number
}

interface DocumentClassification {
  category: string
  confidence: number
  subcategories: string[]
  tags: string[]
}

interface ShareSettings {
  publicAccess: boolean
  requirePassword: boolean
  password?: string
  expiry?: string
}

export const useDocumentStore = defineStore('documents', () => {
  const api = useApi()
  const documents = ref<Document[]>([])
  const currentDocument = ref<Document | null>(null)
  const chunks = ref<Record<string, DocumentChunk[]>>({})
  const analysisResults = ref<Record<string, {
    sentiment?: SentimentAnalysis
    entities?: Entity[]
    classification?: DocumentClassification
  }>>({})

  const getDocument = async (documentId: string) => {
    try {
      const response = await api.get(`/documents/${documentId}`)
      currentDocument.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to get document:', error)
      throw error
    }
  }

  const getDocumentChunks = async (documentId: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/chunks`)
      chunks.value[documentId] = response.data
      return response.data
    } catch (error) {
      console.error('Failed to get document chunks:', error)
      throw error
    }
  }

  const getAllChunks = async (documentId: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/chunks/all`)
      chunks.value[documentId] = response.data
      return response.data
    } catch (error) {
      console.error('Failed to get all chunks:', error)
      throw error
    }
  }

  const getSentimentAnalysis = async (documentId: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/analysis/sentiment`)
      if (!analysisResults.value[documentId]) {
        analysisResults.value[documentId] = {}
      }
      analysisResults.value[documentId].sentiment = response.data
      return response.data
    } catch (error) {
      console.error('Failed to get sentiment analysis:', error)
      throw error
    }
  }

  const getEntityExtraction = async (documentId: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/analysis/entities`)
      if (!analysisResults.value[documentId]) {
        analysisResults.value[documentId] = {}
      }
      analysisResults.value[documentId].entities = response.data
      return response.data
    } catch (error) {
      console.error('Failed to get entity extraction:', error)
      throw error
    }
  }

  const getDocumentClassification = async (documentId: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/analysis/classification`)
      if (!analysisResults.value[documentId]) {
        analysisResults.value[documentId] = {}
      }
      analysisResults.value[documentId].classification = response.data
      return response.data
    } catch (error) {
      console.error('Failed to get document classification:', error)
      throw error
    }
  }

  const downloadDocument = async (documentId: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/download`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', currentDocument.value?.name || 'document')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to download document:', error)
      throw error
    }
  }

  const updateDocumentShares = async (documentId: string, settings: ShareSettings) => {
    try {
      await api.put(`/documents/${documentId}/shares`, settings)
    } catch (error) {
      console.error('Failed to update document shares:', error)
      throw error
    }
  }

  return {
    documents,
    currentDocument,
    chunks,
    analysisResults,
    getDocument,
    getDocumentChunks,
    getAllChunks,
    getSentimentAnalysis,
    getEntityExtraction,
    getDocumentClassification,
    downloadDocument,
    updateDocumentShares
  }
}) 