<template>
  <div class="document-upload">
    <div class="upload-area" 
         @dragover.prevent="handleDragOver"
         @dragleave.prevent="handleDragLeave"
         @drop.prevent="handleDrop"
         :class="{ 'is-dragging': isDragging }">
      <div class="upload-content">
        <i class="fas fa-cloud-upload-alt"></i>
        <h3>Drag and drop your documents here</h3>
        <p>or</p>
        <button class="btn btn-primary" @click="triggerFileInput">
          Browse Files
        </button>
        <input
          type="file"
          ref="fileInput"
          @change="handleFileSelect"
          multiple
          accept=".pdf,.doc,.docx,.txt,.epub,.mobi"
          style="display: none"
        />
      </div>
    </div>

    <div class="upload-list" v-if="files.length > 0">
      <div v-for="(file, index) in files" :key="index" class="upload-item">
        <div class="file-info">
          <i :class="getFileIcon(file.type)"></i>
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
        </div>
        <div class="upload-progress">
          <div class="progress-bar" :style="{ width: file.progress + '%' }"></div>
          <span class="progress-text">{{ file.progress }}%</span>
        </div>
        <div class="upload-status">
          <span :class="['status', file.status]">{{ file.status }}</span>
          <button class="btn btn-icon" @click="removeFile(index)" v-if="file.status !== 'processing'">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="upload-actions" v-if="files.length > 0">
      <button class="btn btn-primary" @click="startUpload" :disabled="isUploading">
        {{ isUploading ? 'Uploading...' : 'Start Upload' }}
      </button>
      <button class="btn btn-secondary" @click="clearFiles" :disabled="isUploading">
        Clear All
      </button>
    </div>

    <div class="upload-options">
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="processImmediately">
          Process documents immediately after upload
        </label>
      </div>
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="extractMetadata">
          Extract metadata from documents
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useDocumentStore } from '@/stores/documents'

export default {
  name: 'DocumentUpload',
  setup() {
    const documentStore = useDocumentStore()
    const fileInput = ref(null)
    const isDragging = ref(false)
    const files = ref([])
    const isUploading = ref(false)
    const processImmediately = ref(true)
    const extractMetadata = ref(true)

    const handleDragOver = () => {
      isDragging.value = true
    }

    const handleDragLeave = () => {
      isDragging.value = false
    }

    const handleDrop = (event) => {
      isDragging.value = false
      const droppedFiles = Array.from(event.dataTransfer.files)
      addFiles(droppedFiles)
    }

    const triggerFileInput = () => {
      fileInput.value.click()
    }

    const handleFileSelect = (event) => {
      const selectedFiles = Array.from(event.target.files)
      addFiles(selectedFiles)
      event.target.value = null
    }

    const addFiles = (newFiles) => {
      newFiles.forEach(file => {
        files.value.push({
          file,
          name: file.name,
          size: file.size,
          type: file.type,
          progress: 0,
          status: 'pending'
        })
      })
    }

    const removeFile = (index) => {
      files.value.splice(index, 1)
    }

    const clearFiles = () => {
      files.value = []
    }

    const getFileIcon = (type) => {
      const icons = {
        'application/pdf': 'fas fa-file-pdf',
        'application/msword': 'fas fa-file-word',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fas fa-file-word',
        'text/plain': 'fas fa-file-alt',
        'application/epub+zip': 'fas fa-book',
        'application/x-mobipocket-ebook': 'fas fa-book'
      }
      return icons[type] || 'fas fa-file'
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const startUpload = async () => {
      isUploading.value = true
      
      for (const file of files.value) {
        try {
          file.status = 'uploading'
          const formData = new FormData()
          formData.append('file', file.file)
          formData.append('processImmediately', processImmediately.value)
          formData.append('extractMetadata', extractMetadata.value)

          const response = await documentStore.uploadDocument(formData, (progress) => {
            file.progress = progress
          })

          file.status = 'processing'
          if (processImmediately.value) {
            await documentStore.processDocument(response.id)
          }
          file.status = 'completed'
        } catch (error) {
          file.status = 'error'
          console.error('Upload failed:', error)
        }
      }

      isUploading.value = false
    }

    return {
      fileInput,
      isDragging,
      files,
      isUploading,
      processImmediately,
      extractMetadata,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      triggerFileInput,
      handleFileSelect,
      removeFile,
      clearFiles,
      getFileIcon,
      formatFileSize,
      startUpload
    }
  }
}
</script>

<style scoped>
.document-upload {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  background-color: var(--background-color);
  transition: all 0.3s ease;
}

.upload-area.is-dragging {
  border-color: var(--primary-color);
  background-color: var(--primary-color-light);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-content i {
  font-size: 3rem;
  color: var(--primary-color);
}

.upload-list {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.upload-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background-color: var(--background-color);
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-info i {
  color: var(--primary-color);
}

.file-name {
  flex: 1;
  font-weight: 500;
}

.file-size {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.upload-progress {
  position: relative;
  height: 4px;
  background-color: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  right: 0;
  top: -20px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.upload-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status {
  font-size: 0.875rem;
  text-transform: capitalize;
}

.status.pending {
  color: var(--text-secondary);
}

.status.uploading {
  color: var(--primary-color);
}

.status.processing {
  color: var(--warning-color);
}

.status.completed {
  color: var(--success-color);
}

.status.error {
  color: var(--error-color);
}

.upload-actions {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.upload-options {
  margin-top: 2rem;
  padding: 1rem;
  background-color: var(--background-color);
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.form-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .document-upload {
    padding: 1rem;
  }

  .upload-area {
    padding: 2rem 1rem;
  }

  .file-info {
    flex-wrap: wrap;
  }

  .file-name {
    width: 100%;
  }
}
</style> 