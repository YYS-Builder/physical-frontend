<template>
  <div class="document-processor">
    <div class="processor-header">
      <h1>Process Documents</h1>
      <div class="processor-actions">
        <button @click="showUploadModal = true" class="btn btn-primary">
          <i class="fas fa-upload"></i> Upload Document
        </button>
      </div>
    </div>

    <div class="processor-content">
      <div class="processing-queue">
        <h2>Processing Queue</h2>
        <div v-if="queueLoading" class="loading">
          <div class="spinner"></div>
          <p>Loading queue...</p>
        </div>
        <div v-else-if="queueError" class="error">
          <p>{{ queueError }}</p>
          <button @click="fetchQueue" class="btn btn-primary">Retry</button>
        </div>
        <div v-else-if="processingQueue.length === 0" class="empty-state">
          <p>No documents in queue</p>
        </div>
        <div v-else class="queue-list">
          <div
            v-for="item in processingQueue"
            :key="item.id"
            class="queue-item"
            :class="{ 'is-processing': item.status === 'processing' }"
          >
            <div class="item-icon">
              <i :class="getDocumentIcon(item.type)"></i>
            </div>
            <div class="item-info">
              <h3>{{ item.title }}</h3>
              <p class="item-meta">
                <span>{{ formatFileSize(item.size) }}</span>
                <span>{{ formatDate(item.created_at) }}</span>
              </p>
              <div class="progress-bar">
                <div
                  class="progress"
                  :style="{ width: `${item.progress}%` }"
                ></div>
              </div>
            </div>
            <div class="item-status">
              <span class="status-badge" :class="item.status">
                {{ item.status }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="preview-section">
        <h2>Document Preview</h2>
        <div v-if="previewLoading" class="loading">
          <div class="spinner"></div>
          <p>Loading preview...</p>
        </div>
        <div v-else-if="previewError" class="error">
          <p>{{ previewError }}</p>
          <button @click="loadPreview" class="btn btn-primary">Retry</button>
        </div>
        <div v-else-if="!currentDocument" class="empty-state">
          <p>Select a document to preview</p>
        </div>
        <div v-else class="preview-content">
          <div class="preview-header">
            <h3>{{ currentDocument.title }}</h3>
            <div class="preview-actions">
              <button
                @click="downloadDocument"
                class="btn btn-outline"
                :disabled="currentDocument.status !== 'completed'"
              >
                <i class="fas fa-download"></i> Download
              </button>
              <button
                @click="saveToCollection"
                class="btn btn-primary"
                :disabled="currentDocument.status !== 'completed'"
              >
                <i class="fas fa-save"></i> Save to Collection
              </button>
            </div>
          </div>
          <div class="preview-container">
            <iframe
              v-if="currentDocument.type === 'pdf'"
              :src="previewUrl"
              class="preview-frame"
            ></iframe>
            <div
              v-else-if="currentDocument.type === 'txt'"
              class="text-preview"
            >
              <pre>{{ previewContent }}</pre>
            </div>
            <div
              v-else
              class="unsupported-preview"
            >
              <p>Preview not available for this file type</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <Modal
      v-model="showUploadModal"
      title="Upload Document"
    >
      <form @submit.prevent="uploadDocument" class="upload-form">
        <div class="form-group">
          <label for="title">Title</label>
          <input
            id="title"
            v-model="uploadForm.title"
            type="text"
            required
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label for="file">File</label>
          <div class="file-upload">
            <input
              id="file"
              type="file"
              @change="handleFileChange"
              required
              class="form-input"
              accept=".pdf,.txt,.doc,.docx,.epub"
            />
            <div v-if="uploadForm.file" class="file-info">
              <span>{{ uploadForm.file.name }}</span>
              <span>{{ formatFileSize(uploadForm.file.size) }}</span>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label for="processing-options">Processing Options</label>
          <div class="checkbox-group">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="uploadForm.options.extractText"
              />
              Extract Text
            </label>
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="uploadForm.options.generateThumbnail"
              />
              Generate Thumbnail
            </label>
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="uploadForm.options.ocr"
              />
              OCR (Optical Character Recognition)
            </label>
          </div>
        </div>
        <div class="form-actions">
          <button
            type="button"
            @click="showUploadModal = false"
            class="btn btn-outline"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="uploading"
          >
            <span v-if="uploading">
              <i class="fas fa-spinner fa-spin"></i> Uploading...
            </span>
            <span v-else>Upload</span>
          </button>
        </div>
      </form>
    </Modal>

    <!-- Save to Collection Modal -->
    <Modal
      v-model="showSaveModal"
      title="Save to Collection"
    >
      <form @submit.prevent="confirmSave" class="save-form">
        <div class="form-group">
          <label for="collection">Select Collection</label>
          <select
            id="collection"
            v-model="selectedCollection"
            required
            class="form-input"
          >
            <option value="">Choose a collection</option>
            <option
              v-for="collection in collections"
              :key="collection.id"
              :value="collection.id"
            >
              {{ collection.name }}
            </option>
          </select>
        </div>
        <div class="form-actions">
          <button
            type="button"
            @click="showSaveModal = false"
            class="btn btn-outline"
          >
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            Save
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useDocumentStore } from '@/stores/documents'
import { useCollectionStore } from '@/stores/collections'
import Modal from '@/components/common/Modal.vue'

export default {
  name: 'DocumentProcessor',
  components: {
    Modal
  },
  setup() {
    const documentStore = useDocumentStore()
    const collectionStore = useCollectionStore()

    const queueLoading = ref(false)
    const queueError = ref(null)
    const previewLoading = ref(false)
    const previewError = ref(null)
    const uploading = ref(false)
    const showUploadModal = ref(false)
    const showSaveModal = ref(false)
    const selectedCollection = ref('')
    const currentDocument = ref(null)
    const previewContent = ref('')
    const previewUrl = ref('')

    const processingQueue = computed(() => documentStore.processingQueue)
    const collections = computed(() => collectionStore.collections)

    const uploadForm = ref({
      title: '',
      file: null,
      options: {
        extractText: true,
        generateThumbnail: true,
        ocr: false
      }
    })

    const fetchQueue = async () => {
      queueLoading.value = true
      queueError.value = null
      try {
        await documentStore.getProcessingQueue()
      } catch (err) {
        queueError.value = 'Failed to load processing queue'
        console.error(err)
      } finally {
        queueLoading.value = false
      }
    }

    const handleFileChange = (event) => {
      uploadForm.value.file = event.target.files[0]
    }

    const uploadDocument = async () => {
      uploading.value = true
      try {
        const formData = new FormData()
        formData.append('title', uploadForm.value.title)
        formData.append('file', uploadForm.value.file)
        formData.append('options', JSON.stringify(uploadForm.value.options))

        await documentStore.uploadDocument(formData)
        showUploadModal.value = false
        uploadForm.value = {
          title: '',
          file: null,
          options: {
            extractText: true,
            generateThumbnail: true,
            ocr: false
          }
        }
      } catch (err) {
        previewError.value = 'Failed to upload document'
        console.error(err)
      } finally {
        uploading.value = false
      }
    }

    const loadPreview = async (document) => {
      currentDocument.value = document
      previewLoading.value = true
      previewError.value = null
      try {
        if (document.type === 'pdf') {
          previewUrl.value = await documentStore.getDocumentPreview(document.id)
        } else if (document.type === 'txt') {
          previewContent.value = await documentStore.getDocumentContent(document.id)
        }
      } catch (err) {
        previewError.value = 'Failed to load preview'
        console.error(err)
      } finally {
        previewLoading.value = false
      }
    }

    const downloadDocument = async () => {
      try {
        await documentStore.downloadDocument(currentDocument.value.id)
      } catch (err) {
        previewError.value = 'Failed to download document'
        console.error(err)
      }
    }

    const saveToCollection = () => {
      showSaveModal.value = true
    }

    const confirmSave = async () => {
      try {
        await documentStore.saveToCollection(
          currentDocument.value.id,
          selectedCollection.value
        )
        showSaveModal.value = false
        selectedCollection.value = ''
      } catch (err) {
        previewError.value = 'Failed to save document'
        console.error(err)
      }
    }

    const getDocumentIcon = (type) => {
      const icons = {
        pdf: 'fas fa-file-pdf',
        doc: 'fas fa-file-word',
        docx: 'fas fa-file-word',
        txt: 'fas fa-file-alt',
        epub: 'fas fa-book',
        default: 'fas fa-file'
      }
      return icons[type] || icons.default
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString()
    }

    onMounted(() => {
      fetchQueue()
    })

    return {
      queueLoading,
      queueError,
      previewLoading,
      previewError,
      uploading,
      showUploadModal,
      showSaveModal,
      selectedCollection,
      currentDocument,
      previewContent,
      previewUrl,
      processingQueue,
      collections,
      uploadForm,
      fetchQueue,
      handleFileChange,
      uploadDocument,
      loadPreview,
      downloadDocument,
      saveToCollection,
      confirmSave,
      getDocumentIcon,
      formatFileSize,
      formatDate
    }
  }
}
</script>

<style scoped>
.document-processor {
  padding: 2rem;
}

.processor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.processor-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
}

.processing-queue,
.preview-section {
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  transition: all 0.2s ease;
}

.queue-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-sm);
}

.queue-item.is-processing {
  border-left: 4px solid var(--color-primary);
}

.item-icon {
  font-size: 1.5rem;
  color: var(--color-primary);
}

.item-info {
  flex: 1;
}

.item-info h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
}

.item-meta {
  display: flex;
  gap: 1rem;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 4px;
  background-color: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: var(--color-primary);
  transition: width 0.3s ease;
}

.item-status {
  min-width: 100px;
  text-align: right;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius);
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.pending {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
}

.status-badge.processing {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.status-badge.completed {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.status-badge.error {
  background-color: var(--color-error-light);
  color: var(--color-error-dark);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.preview-actions {
  display: flex;
  gap: 0.5rem;
}

.preview-container {
  height: calc(100vh - 300px);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.text-preview {
  padding: 1rem;
  height: 100%;
  overflow: auto;
  background-color: var(--color-background);
}

.text-preview pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: monospace;
}

.unsupported-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
}

.file-upload {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-info {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (max-width: 1024px) {
  .processor-content {
    grid-template-columns: 1fr;
  }

  .preview-container {
    height: 400px;
  }
}

@media (max-width: 768px) {
  .processor-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .processor-actions {
    width: 100%;
  }

  .preview-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .preview-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style> 