<template>
  <div class="metadata-editor">
    <div class="editor-header">
      <h2>Document Metadata</h2>
      <div class="header-actions">
        <button 
          class="action-btn"
          :class="{ 'text-green-600': hasChanges }"
          @click="saveChanges"
          :disabled="!hasChanges || saving"
        >
          <i class="fas fa-save"></i>
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
        <button 
          class="action-btn text-gray-600"
          @click="resetChanges"
          :disabled="!hasChanges"
        >
          <i class="fas fa-undo"></i>
          Reset
        </button>
      </div>
    </div>

    <div class="editor-content">
      <!-- Basic Information -->
      <div class="section">
        <h3>Basic Information</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="title">Title</label>
            <input
              id="title"
              v-model="editedMetadata.title"
              type="text"
              class="form-input"
              :class="{ 'border-red-500': errors.title }"
            />
            <span v-if="errors.title" class="error-message">{{ errors.title }}</span>
          </div>

          <div class="form-group">
            <label for="author">Author</label>
            <input
              id="author"
              v-model="editedMetadata.author"
              type="text"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="description">Description</label>
            <textarea
              id="description"
              v-model="editedMetadata.description"
              class="form-input"
              rows="3"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Document Properties -->
      <div class="section">
        <h3>Document Properties</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="language">Language</label>
            <select
              id="language"
              v-model="editedMetadata.language"
              class="form-input"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
              <option value="pt">Portuguese</option>
              <option value="ru">Russian</option>
              <option value="zh">Chinese</option>
              <option value="ja">Japanese</option>
              <option value="ko">Korean</option>
            </select>
          </div>

          <div class="form-group">
            <label for="category">Category</label>
            <select
              id="category"
              v-model="editedMetadata.category"
              class="form-input"
            >
              <option value="book">Book</option>
              <option value="article">Article</option>
              <option value="report">Report</option>
              <option value="paper">Paper</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label for="tags">Tags</label>
            <div class="tags-input">
              <div 
                v-for="(tag, index) in editedMetadata.tags" 
                :key="index"
                class="tag"
              >
                {{ tag }}
                <button 
                  class="tag-remove"
                  @click="removeTag(index)"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <input
                v-model="newTag"
                type="text"
                class="tag-input"
                placeholder="Add tag..."
                @keydown.enter.prevent="addTag"
                @keydown.backspace="handleBackspace"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Advanced Settings -->
      <div class="section">
        <h3>Advanced Settings</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="visibility">Visibility</label>
            <select
              id="visibility"
              v-model="editedMetadata.visibility"
              class="form-input"
            >
              <option value="public">Public</option>
              <option value="private">Private</option>
              <option value="shared">Shared</option>
            </select>
          </div>

          <div class="form-group">
            <label for="expiration">Expiration Date</label>
            <input
              id="expiration"
              v-model="editedMetadata.expirationDate"
              type="date"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="editedMetadata.allowComments"
                class="form-checkbox"
              />
              Allow Comments
            </label>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="editedMetadata.allowDownloads"
                class="form-checkbox"
              />
              Allow Downloads
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading and error states -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading metadata...</p>
    </div>
    <div v-if="error" class="error-overlay">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadMetadata">
        Retry
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDocumentStore } from '@/stores/documents'

const props = defineProps<{
  documentId: string
}>()

const documentStore = useDocumentStore()
const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)
const newTag = ref('')
const errors = ref<Record<string, string>>({})

const originalMetadata = ref<any>({})
const editedMetadata = ref<any>({})

// Computed properties
const hasChanges = computed(() => {
  return JSON.stringify(originalMetadata.value) !== JSON.stringify(editedMetadata.value)
})

// Load document metadata
const loadMetadata = async () => {
  try {
    loading.value = true
    error.value = null
    const metadata = await documentStore.getDocumentMetadata(props.documentId)
    originalMetadata.value = { ...metadata }
    editedMetadata.value = { ...metadata }
  } catch (err) {
    error.value = 'Failed to load document metadata. Please try again.'
    console.error('Error loading metadata:', err)
  } finally {
    loading.value = false
  }
}

// Save changes
const saveChanges = async () => {
  try {
    saving.value = true
    errors.value = {}

    // Validate required fields
    if (!editedMetadata.value.title?.trim()) {
      errors.value.title = 'Title is required'
      return
    }

    await documentStore.updateDocumentMetadata(props.documentId, editedMetadata.value)
    originalMetadata.value = { ...editedMetadata.value }
  } catch (err) {
    error.value = 'Failed to save changes. Please try again.'
    console.error('Error saving metadata:', err)
  } finally {
    saving.value = false
  }
}

// Reset changes
const resetChanges = () => {
  editedMetadata.value = { ...originalMetadata.value }
  errors.value = {}
}

// Tag management
const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !editedMetadata.value.tags.includes(tag)) {
    editedMetadata.value.tags.push(tag)
    newTag.value = ''
  }
}

const removeTag = (index: number) => {
  editedMetadata.value.tags.splice(index, 1)
}

const handleBackspace = (e: KeyboardEvent) => {
  if (e.key === 'Backspace' && !newTag.value && editedMetadata.value.tags.length > 0) {
    editedMetadata.value.tags.pop()
  }
}

onMounted(() => {
  loadMetadata()
})
</script>

<style scoped>
.metadata-editor {
  @apply flex flex-col h-full bg-white;
}

.editor-header {
  @apply flex justify-between items-center p-4 border-b border-gray-200;
}

.editor-header h2 {
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

.editor-content {
  @apply flex-1 overflow-auto p-4;
}

.section {
  @apply mb-6;
}

.section h3 {
  @apply text-lg font-medium text-gray-700 mb-4;
}

.form-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
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

.error-message {
  @apply text-sm text-red-500;
}

.tags-input {
  @apply flex flex-wrap gap-2 p-2 border border-gray-300 rounded-lg;
}

.tag {
  @apply flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm;
}

.tag-remove {
  @apply text-blue-600 hover:text-blue-800;
}

.tag-input {
  @apply flex-1 min-w-[100px] outline-none;
}

.checkbox-label {
  @apply flex items-center gap-2;
}

.form-checkbox {
  @apply rounded border-gray-300 text-blue-600 focus:ring-blue-500;
}

.loading-overlay,
.error-overlay {
  @apply absolute inset-0 flex flex-col items-center justify-center bg-black bg-opacity-50 text-white;
}

.spinner {
  @apply w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin;
}

.retry-btn {
  @apply mt-4 px-4 py-2 bg-white text-black rounded-lg hover:bg-gray-100;
}
</style> 