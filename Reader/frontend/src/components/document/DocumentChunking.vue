<template>
  <div class="document-chunking">
    <div class="chunking-header">
      <h4>Document Sections</h4>
      <div class="chunking-controls">
        <button
          class="control-button"
          @click="previousChunk"
          :disabled="currentChunkIndex === 0"
        >
          Previous
        </button>
        <span class="chunk-info">
          Section {{ currentChunkIndex + 1 }} of {{ totalChunks }}
        </span>
        <button
          class="control-button"
          @click="nextChunk"
          :disabled="currentChunkIndex === totalChunks - 1"
        >
          Next
        </button>
      </div>
    </div>
    
    <div class="chunking-content">
      <div class="chunk-text" v-if="currentChunk">
        {{ currentChunk.content }}
      </div>
      
      <div class="chunking-progress" v-if="totalChunks > 1">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
        <div class="progress-labels">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
    
    <div class="chunking-actions">
      <button
        class="action-button"
        @click="loadAllChunks"
        :disabled="loading"
      >
        {{ loading ? 'Loading...' : 'Load Full Document' }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'

interface DocumentChunk {
  id: string
  content: string
  index: number
  totalChunks: number
}

export default defineComponent({
  name: 'DocumentChunking',
  props: {
    chunks: {
      type: Array as () => DocumentChunk[],
      required: true
    }
  },
  setup(props) {
    const currentChunkIndex = ref(0)
    const loading = ref(false)
    
    const currentChunk = computed(() => {
      return props.chunks[currentChunkIndex.value]
    })
    
    const totalChunks = computed(() => {
      return props.chunks.length
    })
    
    const progressPercentage = computed(() => {
      return ((currentChunkIndex.value + 1) / totalChunks.value) * 100
    })
    
    const previousChunk = () => {
      if (currentChunkIndex.value > 0) {
        currentChunkIndex.value--
      }
    }
    
    const nextChunk = () => {
      if (currentChunkIndex.value < totalChunks.value - 1) {
        currentChunkIndex.value++
      }
    }
    
    const loadAllChunks = async () => {
      loading.value = true
      try {
        // TODO: Implement loading all chunks
        console.log('Loading all chunks...')
      } finally {
        loading.value = false
      }
    }
    
    return {
      currentChunkIndex,
      currentChunk,
      totalChunks,
      progressPercentage,
      loading,
      previousChunk,
      nextChunk,
      loadAllChunks
    }
  }
})
</script>

<style scoped>
.document-chunking {
  padding: 1rem;
  background-color: var(--color-background-soft);
  border-radius: 8px;
}

.chunking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chunking-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.control-button {
  padding: 0.5rem 1rem;
  background-color: var(--color-background-mute);
  color: var(--color-text);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.control-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chunk-info {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.chunking-content {
  margin-bottom: 1rem;
}

.chunk-text {
  padding: 1rem;
  background-color: var(--color-background-mute);
  border-radius: 4px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.chunking-progress {
  margin-top: 1rem;
}

.progress-bar {
  height: 4px;
  background-color: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-primary);
  transition: width 0.3s ease;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-light);
}

.chunking-actions {
  display: flex;
  justify-content: center;
}

.action-button {
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-button:disabled {
  background-color: var(--color-background-mute);
  cursor: not-allowed;
}
</style> 