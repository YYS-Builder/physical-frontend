<template>
  <div class="document-viewer">
    <div class="viewer-header">
      <div class="document-info">
        <h2>{{ document.name }}</h2>
        <div class="document-meta">
          <span class="document-type">{{ document.type }}</span>
          <span class="document-size">{{ formatSize(document.size) }}</span>
          <span class="document-date">{{ formatDate(document.createdAt) }}</span>
        </div>
      </div>
      <div class="viewer-actions">
        <button class="action-button" @click="toggleShare">
          <span class="icon">🔗</span>
          Share
        </button>
        <button class="action-button" @click="downloadDocument">
          <span class="icon">⬇️</span>
          Download
        </button>
      </div>
    </div>

    <div class="viewer-content">
      <div class="document-panel">
        <DocumentChunking
          v-if="chunks.length"
          :chunks="chunks"
          @load-all="loadAllChunks"
        />
        <div v-else class="loading-state">
          Loading document...
        </div>
      </div>

      <div class="analysis-panel">
        <div class="panel-section">
          <SentimentAnalysis
            v-if="sentiment"
            :sentiment="sentiment.sentiment"
            :score="sentiment.score"
            :summary="sentiment.summary"
            :keywords="sentiment.keywords"
          />
        </div>

        <div class="panel-section">
          <EntityExtraction
            v-if="entities"
            :entities="entities.entities"
          />
        </div>

        <div class="panel-section">
          <DocumentClassification
            v-if="classification"
            :category="classification.category"
            :confidence="classification.confidence"
            :subcategories="classification.subcategories"
            :tags="classification.tags"
          />
        </div>
      </div>
    </div>

    <div class="viewer-footer">
      <CollaborationStatus
        v-if="collaborators.length"
        :users="collaborators"
        :typing-users="typingUsers"
        :last-saved="lastSaved"
        :current-user-id="currentUserId"
      />
    </div>

    <ShareDialog
      v-if="showShareDialog"
      :document-id="document.id"
      @close="showShareDialog = false"
      @save="handleShareSave"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import DocumentChunking from './DocumentChunking.vue'
import SentimentAnalysis from './SentimentAnalysis.vue'
import EntityExtraction from './EntityExtraction.vue'
import DocumentClassification from './DocumentClassification.vue'
import ShareDialog from './ShareDialog.vue'
import CollaborationStatus from './CollaborationStatus.vue'
import { useDocumentStore } from '@/stores/documents'
import { useCollaborationStore } from '@/stores/collaboration'

interface Document {
  id: string
  name: string
  type: string
  size: number
  createdAt: string
}

interface SentimentResult {
  sentiment: string
  score: number
  summary: string
  keywords: string[]
}

interface EntityResult {
  entities: Array<{
    id: string
    text: string
    type: string
    confidence: number
  }>
}

interface ClassificationResult {
  category: string
  confidence: number
  subcategories: string[]
  tags: string[]
}

export default defineComponent({
  name: 'DocumentViewer',
  components: {
    DocumentChunking,
    SentimentAnalysis,
    EntityExtraction,
    DocumentClassification,
    ShareDialog,
    CollaborationStatus
  },
  props: {
    documentId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const documentStore = useDocumentStore()
    const collaborationStore = useCollaborationStore()
    
    const document = ref<Document | null>(null)
    const chunks = ref<any[]>([])
    const sentiment = ref<SentimentResult | null>(null)
    const entities = ref<EntityResult | null>(null)
    const classification = ref<ClassificationResult | null>(null)
    const showShareDialog = ref(false)
    const collaborators = ref<any[]>([])
    const typingUsers = ref<string[]>([])
    const lastSaved = ref('')
    const currentUserId = ref('')

    const loadDocument = async () => {
      try {
        // Load document details
        document.value = await documentStore.getDocument(props.documentId)
        
        // Load document chunks
        chunks.value = await documentStore.getDocumentChunks(props.documentId)
        
        // Load analysis results
        sentiment.value = await documentStore.getSentimentAnalysis(props.documentId)
        entities.value = await documentStore.getEntityExtraction(props.documentId)
        classification.value = await documentStore.getDocumentClassification(props.documentId)
        
        // Join collaboration session
        await collaborationStore.joinSession(props.documentId)
        collaborators.value = await collaborationStore.getSessionUsers(props.documentId)
      } catch (error) {
        console.error('Failed to load document:', error)
      }
    }

    const toggleShare = () => {
      showShareDialog.value = !showShareDialog.value
    }

    const downloadDocument = async () => {
      try {
        await documentStore.downloadDocument(props.documentId)
      } catch (error) {
        console.error('Failed to download document:', error)
      }
    }

    const loadAllChunks = async () => {
      try {
        chunks.value = await documentStore.getAllChunks(props.documentId)
      } catch (error) {
        console.error('Failed to load all chunks:', error)
      }
    }

    const handleShareSave = async (shareData: any) => {
      try {
        await documentStore.updateDocumentShares(props.documentId, shareData)
        showShareDialog.value = false
      } catch (error) {
        console.error('Failed to save share settings:', error)
      }
    }

    const formatSize = (bytes: number) => {
      const units = ['B', 'KB', 'MB', 'GB']
      let size = bytes
      let unitIndex = 0
      
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
      }
      
      return `${size.toFixed(1)} ${units[unitIndex]}`
    }

    const formatDate = (date: string) => {
      return new Date(date).toLocaleDateString()
    }

    onMounted(() => {
      loadDocument()
    })

    return {
      document,
      chunks,
      sentiment,
      entities,
      classification,
      showShareDialog,
      collaborators,
      typingUsers,
      lastSaved,
      currentUserId,
      toggleShare,
      downloadDocument,
      loadAllChunks,
      handleShareSave,
      formatSize,
      formatDate
    }
  }
})
</script>

<style scoped>
.document-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--color-background);
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.document-info h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-text);
}

.document-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.viewer-actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: var(--color-background-mute);
  color: var(--color-text);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-button .icon {
  font-size: 1rem;
}

.viewer-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.document-panel {
  flex: 2;
  padding: 1rem;
  overflow-y: auto;
  border-right: 1px solid var(--color-border);
}

.analysis-panel {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.panel-section {
  background-color: var(--color-background-soft);
  border-radius: 8px;
  overflow: hidden;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-light);
}

.viewer-footer {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
}
</style> 