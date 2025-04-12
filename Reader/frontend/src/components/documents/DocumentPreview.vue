<template>
  <div class="document-preview">
    <!-- Header with document info and controls -->
    <div class="preview-header">
      <div class="document-info">
        <h2>{{ document.title }}</h2>
        <div class="document-meta">
          <span class="meta-item">
            <i class="fas fa-file-alt"></i>
            {{ document.type }}
          </span>
          <span class="meta-item">
            <i class="fas fa-clock"></i>
            {{ formatDate(document.createdAt) }}
          </span>
          <span class="meta-item">
            <i class="fas fa-user"></i>
            {{ document.author }}
          </span>
        </div>
      </div>
      <div class="preview-controls">
        <button 
          class="control-btn"
          :class="{ active: viewMode === 'single' }"
          @click="setViewMode('single')"
          title="Single Page View"
        >
          <i class="fas fa-file"></i>
        </button>
        <button 
          class="control-btn"
          :class="{ active: viewMode === 'double' }"
          @click="setViewMode('double')"
          title="Double Page View"
        >
          <i class="fas fa-copy"></i>
        </button>
        <button 
          class="control-btn"
          :class="{ active: viewMode === 'scroll' }"
          @click="setViewMode('scroll')"
          title="Scroll View"
        >
          <i class="fas fa-scroll"></i>
        </button>
        <div class="zoom-controls">
          <button 
            class="control-btn"
            @click="zoomOut"
            :disabled="zoom <= 0.5"
            title="Zoom Out"
          >
            <i class="fas fa-search-minus"></i>
          </button>
          <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
          <button 
            class="control-btn"
            @click="zoomIn"
            :disabled="zoom >= 2"
            title="Zoom In"
          >
            <i class="fas fa-search-plus"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Document content area -->
    <div class="preview-content" :class="viewMode">
      <div 
        class="document-pages"
        :style="{ transform: `scale(${zoom})` }"
      >
        <div 
          v-for="page in pages" 
          :key="page.number"
          class="page"
          :class="{ active: currentPage === page.number }"
        >
          <img 
            v-if="page.type === 'image'"
            :src="page.content"
            :alt="`Page ${page.number}`"
            @click="selectPage(page.number)"
          />
          <div 
            v-else-if="page.type === 'text'"
            class="text-content"
            v-html="page.content"
            @click="selectPage(page.number)"
          />
          <div class="page-number">{{ page.number }}</div>
        </div>
      </div>
    </div>

    <!-- Navigation controls -->
    <div class="preview-navigation">
      <button 
        class="nav-btn"
        @click="previousPage"
        :disabled="currentPage === 1"
      >
        <i class="fas fa-chevron-left"></i>
      </button>
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button 
        class="nav-btn"
        @click="nextPage"
        :disabled="currentPage === totalPages"
      >
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Loading and error states -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading document...</p>
    </div>
    <div v-if="error" class="error-overlay">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadDocument">
        Retry
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDocumentStore } from '@/stores/documents'
import { formatDate } from '@/utils/date'

const props = defineProps<{
  documentId: string
}>()

const documentStore = useDocumentStore()
const loading = ref(false)
const error = ref<string | null>(null)
const document = ref<any>({})
const pages = ref<any[]>([])
const currentPage = ref(1)
const totalPages = computed(() => pages.value.length)
const viewMode = ref<'single' | 'double' | 'scroll'>('single')
const zoom = ref(1)

// Load document data
const loadDocument = async () => {
  try {
    loading.value = true
    error.value = null
    const doc = await documentStore.getDocument(props.documentId)
    document.value = doc
    pages.value = await documentStore.getDocumentPages(props.documentId)
  } catch (err) {
    error.value = 'Failed to load document. Please try again.'
    console.error('Error loading document:', err)
  } finally {
    loading.value = false
  }
}

// Navigation methods
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const selectPage = (pageNumber: number) => {
  currentPage.value = pageNumber
}

// View mode methods
const setViewMode = (mode: 'single' | 'double' | 'scroll') => {
  viewMode.value = mode
}

// Zoom methods
const zoomIn = () => {
  if (zoom.value < 2) {
    zoom.value += 0.1
  }
}

const zoomOut = () => {
  if (zoom.value > 0.5) {
    zoom.value -= 0.1
  }
}

// Keyboard navigation
const handleKeyPress = (e: KeyboardEvent) => {
  switch (e.key) {
    case 'ArrowRight':
      nextPage()
      break
    case 'ArrowLeft':
      previousPage()
      break
    case '+':
      zoomIn()
      break
    case '-':
      zoomOut()
      break
  }
}

onMounted(() => {
  loadDocument()
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})
</script>

<style scoped>
.document-preview {
  @apply flex flex-col h-full bg-gray-100;
}

.preview-header {
  @apply flex justify-between items-center p-4 bg-white border-b border-gray-200;
}

.document-info h2 {
  @apply text-xl font-semibold text-gray-800;
}

.document-meta {
  @apply flex gap-4 mt-2 text-sm text-gray-600;
}

.meta-item {
  @apply flex items-center gap-2;
}

.preview-controls {
  @apply flex items-center gap-2;
}

.control-btn {
  @apply p-2 rounded-lg hover:bg-gray-100 transition-colors;
}

.control-btn.active {
  @apply bg-blue-100 text-blue-600;
}

.control-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.zoom-controls {
  @apply flex items-center gap-2 ml-4;
}

.zoom-level {
  @apply text-sm text-gray-600;
}

.preview-content {
  @apply flex-1 overflow-auto p-4;
}

.preview-content.single {
  @apply flex justify-center;
}

.preview-content.double {
  @apply grid grid-cols-2 gap-4;
}

.preview-content.scroll {
  @apply flex flex-col gap-4;
}

.document-pages {
  @apply transition-transform duration-200;
}

.page {
  @apply relative bg-white shadow-md rounded-lg overflow-hidden;
}

.page img {
  @apply w-full h-auto;
}

.text-content {
  @apply p-4;
}

.page-number {
  @apply absolute bottom-2 right-2 text-sm text-gray-500;
}

.page.active {
  @apply ring-2 ring-blue-500;
}

.preview-navigation {
  @apply flex justify-center items-center gap-4 p-4 bg-white border-t border-gray-200;
}

.nav-btn {
  @apply p-2 rounded-lg hover:bg-gray-100 transition-colors;
}

.nav-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.page-info {
  @apply text-sm text-gray-600;
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