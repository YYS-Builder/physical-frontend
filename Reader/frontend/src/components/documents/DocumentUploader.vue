<!-- DocumentUploader.vue -->
<template>
  <div class="document-uploader">
    <div
      class="upload-zone"
      :class="{ 'is-dragging': isDragging, 'has-error': error }"
      @dragenter.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @dragover.prevent
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        multiple
        class="hidden"
        @change="handleFileSelect"
      >
      
      <div v-if="!processing && !error" class="upload-content">
        <i class="fas fa-cloud-upload-alt text-3xl mb-4"></i>
        <p class="text-lg font-medium">Drop documents here or click to upload</p>
        <p class="text-sm text-gray-500 mt-2">
          Supported formats: JPEG, PNG, TIFF (max 10MB)
        </p>
      </div>

      <div v-if="processing" class="processing-content">
        <div class="spinner"></div>
        <p class="text-lg font-medium mt-4">Processing document...</p>
      </div>

      <div v-if="error" class="error-content">
        <i class="fas fa-exclamation-circle text-3xl text-red-500 mb-4"></i>
        <p class="text-lg font-medium text-red-500">{{ error }}</p>
        <button
          class="mt-4 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
          @click.stop="clearError"
        >
          Try Again
        </button>
      </div>
    </div>

    <div v-if="processedDocuments.length > 0" class="processed-documents">
      <h3 class="text-lg font-medium mb-4">Processed Documents</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="doc in processedDocuments"
          :key="doc.url"
          class="document-preview"
        >
          <img :src="doc.url" :alt="doc.metadata?.name">
          <div class="document-info">
            <p class="font-medium">{{ doc.metadata?.name }}</p>
            <p class="text-sm text-gray-500">
              {{ formatSize(doc.size) }} • {{ doc.width }}x{{ doc.height }}
            </p>
          </div>
          <button
            class="delete-button"
            @click="removeDocument(doc)"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { imageProcessor } from '@/services/ImageProcessor'
import type { ProcessedImage } from '@/services/ImageProcessor'

const emit = defineEmits<{
  (e: 'upload', documents: ProcessedImage[]): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const processing = ref(false)
const error = ref<string | null>(null)
const processedDocuments = ref<ProcessedImage[]>([])

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files) {
    await processFiles(Array.from(input.files))
    input.value = '' // Reset input
  }
}

const handleDrop = async (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files) {
    await processFiles(Array.from(event.dataTransfer.files))
  }
}

const processFiles = async (files: File[]) => {
  processing.value = true
  error.value = null

  try {
    for (const file of files) {
      const processed = await imageProcessor.processImage(file, {
        maxWidth: 2048,
        maxHeight: 2048,
        quality: 0.8,
        format: 'jpeg',
        preserveMetadata: true
      })

      if (processed) {
        processedDocuments.value.push(processed)
      } else {
        error.value = imageProcessor.getError()
        break
      }
    }

    if (processedDocuments.value.length > 0) {
      emit('upload', processedDocuments.value)
    }
  } catch (err) {
    error.value = 'Failed to process documents. Please try again.'
  } finally {
    processing.value = false
  }
}

const removeDocument = (doc: ProcessedImage) => {
  const index = processedDocuments.value.indexOf(doc)
  if (index > -1) {
    processedDocuments.value.splice(index, 1)
  }
}

const clearError = () => {
  error.value = null
}

const formatSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.document-uploader {
  @apply space-y-8;
}

.upload-zone {
  @apply border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer
         transition-colors duration-200 relative min-h-[200px] flex items-center justify-center;
}

.upload-zone:hover {
  @apply border-gray-400 bg-gray-50;
}

.upload-zone.is-dragging {
  @apply border-blue-500 bg-blue-50;
}

.upload-zone.has-error {
  @apply border-red-500 bg-red-50;
}

.hidden {
  @apply sr-only;
}

.spinner {
  @apply w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin;
}

.document-preview {
  @apply relative bg-white rounded-lg shadow overflow-hidden;
}

.document-preview img {
  @apply w-full h-48 object-cover;
}

.document-info {
  @apply p-4;
}

.delete-button {
  @apply absolute top-2 right-2 w-8 h-8 bg-black bg-opacity-50 rounded-full text-white
         flex items-center justify-center hover:bg-opacity-70 transition-opacity duration-200;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style> 