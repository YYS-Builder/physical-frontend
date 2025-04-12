<template>
  <div class="document-viewer">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading document...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="alert alert-error">
        <p>{{ error }}</p>
        <button class="btn btn-outline" @click="retry">Retry</button>
      </div>
    </div>

    <div v-else class="document-content">
      <!-- Document Header -->
      <div class="document-header">
        <div class="document-info">
          <h1>{{ document.title }}</h1>
          <div class="document-meta">
            <span class="badge">
              <i class="icon-file"></i>
              {{ document.file_type }}
            </span>
            <span class="badge">
              <i class="icon-clock"></i>
              {{ formatDate(document.created_at) }}
            </span>
            <span class="badge">
              <i class="icon-eye"></i>
              {{ document.views }} views
            </span>
          </div>
        </div>
        <div class="document-actions">
          <button class="btn btn-outline" @click="shareDocument">
            <i class="icon-share"></i> Share
          </button>
          <button class="btn btn-primary" @click="startReading">
            <i class="icon-book"></i> Start Reading
          </button>
        </div>
      </div>

      <!-- Reading Progress -->
      <div v-if="readingSession" class="reading-progress">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${readingProgress}%` }"
          ></div>
        </div>
        <div class="progress-stats">
          <span>{{ readingProgress }}% Complete</span>
          <span>{{ pagesRead }}/{{ totalPages }} Pages</span>
          <span>{{ formatDuration(readingDuration) }}</span>
        </div>
      </div>

      <!-- Document Content -->
      <div class="document-body">
        <div v-if="document.file_type === 'pdf'" class="pdf-viewer">
          <!-- PDF viewer implementation -->
          <iframe
            :src="document.url"
            class="pdf-frame"
            frameborder="0"
          ></iframe>
        </div>
        <div v-else-if="document.file_type === 'epub'" class="epub-viewer">
          <!-- EPUB viewer implementation -->
          <div class="epub-content">
            {{ document.content }}
          </div>
        </div>
        <div v-else class="text-viewer">
          <pre class="document-text">{{ document.content }}</pre>
        </div>
      </div>

      <!-- Reading Controls -->
      <div v-if="readingSession" class="reading-controls">
        <button
          class="btn btn-outline"
          @click="previousPage"
          :disabled="currentPage === 1"
        >
          <i class="icon-arrow-left"></i> Previous
        </button>
        <div class="page-indicator">
          Page {{ currentPage }} of {{ totalPages }}
        </div>
        <button
          class="btn btn-outline"
          @click="nextPage"
          :disabled="currentPage === totalPages"
        >
          Next <i class="icon-arrow-right"></i>
        </button>
      </div>

      <!-- Document Analytics -->
      <div class="document-analytics">
        <h2>Reading Analytics</h2>
        <div class="analytics-grid">
          <div class="analytics-card">
            <h3>Reading Time</h3>
            <p class="analytics-value">{{ formatDuration(totalReadingTime) }}</p>
            <p class="analytics-label">Total time spent reading</p>
          </div>
          <div class="analytics-card">
            <h3>Reading Speed</h3>
            <p class="analytics-value">{{ readingSpeed }} pages/hour</p>
            <p class="analytics-label">Average reading speed</p>
          </div>
          <div class="analytics-card">
            <h3>Completion</h3>
            <p class="analytics-value">{{ completionPercentage }}%</p>
            <p class="analytics-label">Document completion</p>
          </div>
          <div class="analytics-card">
            <h3>Last Read</h3>
            <p class="analytics-value">{{ formatDate(lastRead) }}</p>
            <p class="analytics-label">Most recent reading session</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Share Modal -->
    <div v-if="showShareModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Share Document</h3>
          <button class="btn-icon" @click="closeShareModal">
            <i class="icon-close"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="share-link">Document Link</label>
            <div class="input-group">
              <input
                id="share-link"
                type="text"
                class="form-control"
                :value="shareLink"
                readonly
              />
              <button class="btn btn-outline" @click="copyShareLink">
                Copy Link
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>Share Options</label>
            <div class="share-options">
              <button class="btn btn-outline" @click="shareViaEmail">
                <i class="icon-mail"></i> Email
              </button>
              <button class="btn btn-outline" @click="shareViaMessage">
                <i class="icon-message"></i> Message
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { format, formatDistanceToNow } from 'date-fns'
import { useDocumentStore } from '@/stores/documents'
import { useReadingSessionStore } from '@/stores/readingSessions'

export default {
  name: 'DocumentViewer',
  setup() {
    const route = useRoute()
    const documentStore = useDocumentStore()
    const readingSessionStore = useReadingSessionStore()
    
    const document = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const showShareModal = ref(false)
    const readingSession = ref(null)
    const currentPage = ref(1)
    const totalPages = ref(0)
    const pagesRead = ref(0)
    const readingDuration = ref(0)
    const readingInterval = ref(null)
    
    const shareLink = computed(() => {
      return `${window.location.origin}/documents/${route.params.id}`
    })

    const readingProgress = computed(() => {
      return Math.round((pagesRead.value / totalPages.value) * 100)
    })

    const totalReadingTime = computed(() => {
      return document.value?.analytics?.total_duration_minutes || 0
    })

    const readingSpeed = computed(() => {
      return document.value?.analytics?.reading_speed_pages_per_hour || 0
    })

    const completionPercentage = computed(() => {
      return document.value?.analytics?.completion_percentage || 0
    })

    const lastRead = computed(() => {
      return document.value?.analytics?.last_read
    })

    const fetchDocument = async () => {
      loading.value = true
      error.value = null
      try {
        document.value = await documentStore.getDocument(route.params.id)
        totalPages.value = document.value.page_count || 1
      } catch (err) {
        error.value = 'Failed to load document. Please try again.'
        console.error('Error fetching document:', err)
      } finally {
        loading.value = false
      }
    }

    const startReading = async () => {
      try {
        readingSession.value = await readingSessionStore.startSession(route.params.id)
        startReadingTimer()
      } catch (err) {
        error.value = 'Failed to start reading session. Please try again.'
        console.error('Error starting reading session:', err)
      }
    }

    const startReadingTimer = () => {
      readingInterval.value = setInterval(() => {
        readingDuration.value += 1
      }, 60000) // Update every minute
    }

    const stopReadingTimer = () => {
      if (readingInterval.value) {
        clearInterval(readingInterval.value)
        readingInterval.value = null
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        pagesRead.value = Math.max(pagesRead.value, currentPage.value)
        updateReadingProgress()
      }
    }

    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        updateReadingProgress()
      }
    }

    const updateReadingProgress = async () => {
      if (readingSession.value) {
        try {
          await readingSessionStore.updateProgress(
            readingSession.value.id,
            {
              current_page: currentPage.value,
              pages_read: pagesRead.value,
              duration_minutes: readingDuration.value
            }
          )
        } catch (err) {
          console.error('Error updating reading progress:', err)
        }
      }
    }

    const shareDocument = () => {
      showShareModal.value = true
    }

    const copyShareLink = async () => {
      try {
        await navigator.clipboard.writeText(shareLink.value)
        // Show success message
      } catch (err) {
        console.error('Failed to copy link:', err)
      }
    }

    const shareViaEmail = () => {
      const subject = `Check out this document: ${document.value.title}`
      const body = `I'd like to share this document with you: ${shareLink.value}`
      window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
    }

    const shareViaMessage = () => {
      // Implement messaging integration
    }

    const closeShareModal = () => {
      showShareModal.value = false
    }

    const retry = () => {
      fetchDocument()
    }

    const formatDate = (date) => {
      return format(new Date(date), 'MMM d, yyyy')
    }

    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60)
      const remainingMinutes = minutes % 60
      if (hours > 0) {
        return `${hours}h ${remainingMinutes}m`
      }
      return `${remainingMinutes}m`
    }

    onMounted(() => {
      fetchDocument()
    })

    onUnmounted(() => {
      stopReadingTimer()
      if (readingSession.value) {
        readingSessionStore.endSession(readingSession.value.id)
      }
    })

    return {
      document,
      loading,
      error,
      showShareModal,
      readingSession,
      currentPage,
      totalPages,
      pagesRead,
      readingDuration,
      shareLink,
      readingProgress,
      totalReadingTime,
      readingSpeed,
      completionPercentage,
      lastRead,
      startReading,
      nextPage,
      previousPage,
      shareDocument,
      copyShareLink,
      shareViaEmail,
      shareViaMessage,
      closeShareModal,
      retry,
      formatDate,
      formatDuration
    }
  }
}
</script>

<style scoped>
.document-viewer {
  padding: var(--spacing-4);
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-6);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid var(--border-color);
}

.document-info h1 {
  margin-bottom: var(--spacing-2);
}

.document-meta {
  display: flex;
  gap: var(--spacing-2);
}

.document-actions {
  display: flex;
  gap: var(--spacing-2);
}

.reading-progress {
  margin-bottom: var(--spacing-4);
}

.progress-bar {
  height: 8px;
  background-color: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--spacing-2);
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color);
  transition: width var(--transition-normal);
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  color: var(--gray-600);
  font-size: var(--font-size-sm);
}

.document-body {
  margin-bottom: var(--spacing-6);
}

.pdf-viewer,
.epub-viewer,
.text-viewer {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.pdf-frame {
  width: 100%;
  height: 70vh;
  border: none;
}

.epub-content,
.document-text {
  padding: var(--spacing-4);
  font-size: var(--font-size-lg);
  line-height: 1.6;
  white-space: pre-wrap;
}

.reading-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-4);
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.page-indicator {
  color: var(--gray-600);
  font-weight: var(--font-weight-medium);
}

.document-analytics {
  margin-top: var(--spacing-6);
}

.document-analytics h2 {
  margin-bottom: var(--spacing-4);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

.analytics-card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-4);
  text-align: center;
}

.analytics-card h3 {
  color: var(--gray-600);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-2);
}

.analytics-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--gray-900);
  margin-bottom: var(--spacing-1);
}

.analytics-label {
  color: var(--gray-500);
  font-size: var(--font-size-sm);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8);
  text-align: center;
}

.loading-state .spinner {
  margin-bottom: var(--spacing-4);
}

@media (max-width: 768px) {
  .document-viewer {
    padding: var(--spacing-2);
  }

  .document-header {
    flex-direction: column;
    gap: var(--spacing-4);
  }

  .document-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .analytics-grid {
    grid-template-columns: 1fr;
  }
}
</style> 