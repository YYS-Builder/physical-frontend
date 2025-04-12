<template>
  <div class="version-control">
    <div class="version-header">
      <h2>Version History</h2>
      <div class="header-actions">
        <button 
          class="action-btn"
          @click="createNewVersion"
          :disabled="creatingVersion"
        >
          <i class="fas fa-plus"></i>
          {{ creatingVersion ? 'Creating...' : 'Create New Version' }}
        </button>
      </div>
    </div>

    <div class="version-content">
      <!-- Version List -->
      <div class="version-list">
        <div 
          v-for="version in versions" 
          :key="version.id"
          class="version-item"
          :class="{ 
            'active': selectedVersion?.id === version.id,
            'current': version.isCurrent
          }"
        >
          <div class="version-info">
            <div class="version-header">
              <h3 class="version-title">
                Version {{ version.number }}
                <span v-if="version.isCurrent" class="current-badge">Current</span>
              </h3>
              <span class="version-date">{{ formatDate(version.createdAt) }}</span>
            </div>
            <div class="version-meta">
              <span class="meta-item">
                <i class="fas fa-user"></i>
                {{ version.author }}
              </span>
              <span class="meta-item">
                <i class="fas fa-file-alt"></i>
                {{ formatFileSize(version.size) }}
              </span>
              <span class="meta-item">
                <i class="fas fa-comment"></i>
                {{ version.comment || 'No comment' }}
              </span>
            </div>
          </div>
          <div class="version-actions">
            <button 
              class="action-btn"
              @click="selectVersion(version)"
              :disabled="version.isCurrent"
            >
              <i class="fas fa-eye"></i>
              View
            </button>
            <button 
              class="action-btn"
              @click="restoreVersion(version)"
              :disabled="version.isCurrent || restoring"
            >
              <i class="fas fa-history"></i>
              Restore
            </button>
            <button 
              class="action-btn text-red-600"
              @click="deleteVersion(version)"
              :disabled="version.isCurrent || deleting"
            >
              <i class="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Version Preview -->
      <div v-if="selectedVersion" class="version-preview">
        <div class="preview-header">
          <h3>Preview - Version {{ selectedVersion.number }}</h3>
          <button 
            class="close-btn"
            @click="selectedVersion = null"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="preview-content">
          <div v-if="previewLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading preview...</p>
          </div>
          <div v-else-if="previewError" class="error-state">
            <i class="fas fa-exclamation-circle"></i>
            <p>{{ previewError }}</p>
            <button class="retry-btn" @click="loadPreview">
              Retry
            </button>
          </div>
          <div v-else class="preview-document">
            <!-- Document preview content -->
            <img 
              v-if="previewData.type === 'image'"
              :src="previewData.content"
              :alt="`Version ${selectedVersion.number}`"
            />
            <div 
              v-else-if="previewData.type === 'text'"
              class="text-content"
              v-html="previewData.content"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Create Version Modal -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Create New Version</h3>
          <button 
            class="close-btn"
            @click="showCreateModal = false"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="version-comment">Version Comment</label>
            <textarea
              id="version-comment"
              v-model="newVersionComment"
              class="form-input"
              rows="3"
              placeholder="Describe the changes in this version..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            class="action-btn"
            @click="showCreateModal = false"
          >
            Cancel
          </button>
          <button 
            class="action-btn bg-blue-600 text-white"
            @click="confirmCreateVersion"
            :disabled="!newVersionComment.trim() || creatingVersion"
          >
            Create Version
          </button>
        </div>
      </div>
    </div>

    <!-- Loading and error states -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading versions...</p>
    </div>
    <div v-if="error" class="error-overlay">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadVersions">
        Retry
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDocumentStore } from '@/stores/documents'
import { formatDate, formatFileSize } from '@/utils/format'

const props = defineProps<{
  documentId: string
}>()

const documentStore = useDocumentStore()
const loading = ref(false)
const error = ref<string | null>(null)
const versions = ref<any[]>([])
const selectedVersion = ref<any>(null)
const previewLoading = ref(false)
const previewError = ref<string | null>(null)
const previewData = ref<any>({})
const showCreateModal = ref(false)
const newVersionComment = ref('')
const creatingVersion = ref(false)
const restoring = ref(false)
const deleting = ref(false)

// Load document versions
const loadVersions = async () => {
  try {
    loading.value = true
    error.value = null
    versions.value = await documentStore.getDocumentVersions(props.documentId)
  } catch (err) {
    error.value = 'Failed to load versions. Please try again.'
    console.error('Error loading versions:', err)
  } finally {
    loading.value = false
  }
}

// Select version and load preview
const selectVersion = async (version: any) => {
  selectedVersion.value = version
  await loadPreview()
}

// Load version preview
const loadPreview = async () => {
  if (!selectedVersion.value) return

  try {
    previewLoading.value = true
    previewError.value = null
    previewData.value = await documentStore.getVersionPreview(
      props.documentId,
      selectedVersion.value.id
    )
  } catch (err) {
    previewError.value = 'Failed to load preview. Please try again.'
    console.error('Error loading preview:', err)
  } finally {
    previewLoading.value = false
  }
}

// Create new version
const createNewVersion = () => {
  showCreateModal.value = true
  newVersionComment.value = ''
}

const confirmCreateVersion = async () => {
  try {
    creatingVersion.value = true
    await documentStore.createDocumentVersion(
      props.documentId,
      newVersionComment.value.trim()
    )
    showCreateModal.value = false
    await loadVersions()
  } catch (err) {
    error.value = 'Failed to create version. Please try again.'
    console.error('Error creating version:', err)
  } finally {
    creatingVersion.value = false
  }
}

// Restore version
const restoreVersion = async (version: any) => {
  if (!confirm('Are you sure you want to restore this version?')) return

  try {
    restoring.value = true
    await documentStore.restoreDocumentVersion(
      props.documentId,
      version.id
    )
    await loadVersions()
    selectedVersion.value = null
  } catch (err) {
    error.value = 'Failed to restore version. Please try again.'
    console.error('Error restoring version:', err)
  } finally {
    restoring.value = false
  }
}

// Delete version
const deleteVersion = async (version: any) => {
  if (!confirm('Are you sure you want to delete this version?')) return

  try {
    deleting.value = true
    await documentStore.deleteDocumentVersion(
      props.documentId,
      version.id
    )
    await loadVersions()
    if (selectedVersion.value?.id === version.id) {
      selectedVersion.value = null
    }
  } catch (err) {
    error.value = 'Failed to delete version. Please try again.'
    console.error('Error deleting version:', err)
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadVersions()
})
</script>

<style scoped>
.version-control {
  @apply flex flex-col h-full bg-white;
}

.version-header {
  @apply flex justify-between items-center p-4 border-b border-gray-200;
}

.version-header h2 {
  @apply text-xl font-semibold text-gray-800;
}

.header-actions {
  @apply flex gap-2;
}

.action-btn {
  @apply flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors;
}

.action-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.version-content {
  @apply flex flex-1 overflow-hidden;
}

.version-list {
  @apply flex-1 overflow-auto p-4 border-r border-gray-200;
}

.version-item {
  @apply flex flex-col gap-4 p-4 mb-4 bg-white rounded-lg border border-gray-200;
}

.version-item.active {
  @apply border-blue-500 bg-blue-50;
}

.version-item.current {
  @apply border-green-500;
}

.version-info {
  @apply flex-1;
}

.version-header {
  @apply flex justify-between items-center mb-2;
}

.version-title {
  @apply text-lg font-medium text-gray-800;
}

.current-badge {
  @apply ml-2 px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full;
}

.version-date {
  @apply text-sm text-gray-500;
}

.version-meta {
  @apply flex gap-4 text-sm text-gray-600;
}

.meta-item {
  @apply flex items-center gap-2;
}

.version-actions {
  @apply flex gap-2;
}

.version-preview {
  @apply w-1/2 flex flex-col border-l border-gray-200;
}

.preview-header {
  @apply flex justify-between items-center p-4 border-b border-gray-200;
}

.preview-header h3 {
  @apply text-lg font-medium text-gray-800;
}

.close-btn {
  @apply p-2 rounded-lg hover:bg-gray-100;
}

.preview-content {
  @apply flex-1 overflow-auto p-4;
}

.loading-state,
.error-state {
  @apply flex flex-col items-center justify-center h-full text-gray-500;
}

.spinner {
  @apply w-8 h-8 border-4 border-gray-300 border-t-transparent rounded-full animate-spin;
}

.retry-btn {
  @apply mt-4 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200;
}

.preview-document {
  @apply h-full;
}

.preview-document img {
  @apply max-w-full h-auto;
}

.text-content {
  @apply p-4;
}

.modal-overlay {
  @apply fixed inset-0 flex items-center justify-center bg-black bg-opacity-50;
}

.modal-content {
  @apply w-full max-w-md bg-white rounded-lg shadow-xl;
}

.modal-header {
  @apply flex justify-between items-center p-4 border-b border-gray-200;
}

.modal-body {
  @apply p-4;
}

.modal-footer {
  @apply flex justify-end gap-2 p-4 border-t border-gray-200;
}

.form-group {
  @apply flex flex-col gap-1;
}

.form-group label {
  @apply text-sm font-medium text-gray-700;
}

.form-input {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.loading-overlay,
.error-overlay {
  @apply absolute inset-0 flex flex-col items-center justify-center bg-black bg-opacity-50 text-white;
}
</style> 