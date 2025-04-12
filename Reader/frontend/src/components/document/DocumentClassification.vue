<template>
  <div class="document-classification">
    <div class="classification-header">
      <h3>Document Classification</h3>
      <div class="classification-confidence" :class="confidenceClass">
        {{ confidenceScore }}%
      </div>
    </div>
    
    <div class="classification-category">
      <div class="category-label">Category</div>
      <div class="category-value">{{ category }}</div>
    </div>
    
    <div class="classification-subcategories" v-if="subcategories.length">
      <div class="subcategories-label">Subcategories</div>
      <div class="subcategories-list">
        <span
          v-for="subcategory in subcategories"
          :key="subcategory"
          class="subcategory-tag"
        >
          {{ subcategory }}
        </span>
      </div>
    </div>
    
    <div class="classification-tags" v-if="tags.length">
      <div class="tags-label">Tags</div>
      <div class="tags-list">
        <span
          v-for="tag in tags"
          :key="tag"
          class="tag"
        >
          {{ tag }}
        </span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'DocumentClassification',
  props: {
    category: {
      type: String,
      required: true
    },
    confidence: {
      type: Number,
      required: true
    },
    subcategories: {
      type: Array as () => string[],
      default: () => []
    },
    tags: {
      type: Array as () => string[],
      default: () => []
    }
  },
  setup(props) {
    const confidenceScore = computed(() => {
      return Math.round(props.confidence * 100)
    })
    
    const confidenceClass = computed(() => {
      if (props.confidence >= 0.8) {
        return 'confidence-high'
      } else if (props.confidence >= 0.6) {
        return 'confidence-medium'
      } else {
        return 'confidence-low'
      }
    })
    
    return {
      confidenceScore,
      confidenceClass
    }
  }
})
</script>

<style scoped>
.document-classification {
  padding: 1rem;
  border-radius: 8px;
  background-color: var(--color-background-soft);
}

.classification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.classification-confidence {
  font-size: 1.25rem;
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.confidence-high {
  color: var(--color-success);
  background-color: var(--color-success-bg);
}

.confidence-medium {
  color: var(--color-warning);
  background-color: var(--color-warning-bg);
}

.confidence-low {
  color: var(--color-danger);
  background-color: var(--color-danger-bg);
}

.classification-category {
  margin-bottom: 1rem;
}

.category-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin-bottom: 0.25rem;
}

.category-value {
  font-size: 1.25rem;
  font-weight: 500;
  color: var(--color-text);
}

.classification-subcategories {
  margin-bottom: 1rem;
}

.subcategories-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin-bottom: 0.5rem;
}

.subcategories-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.subcategory-tag {
  padding: 0.25rem 0.75rem;
  background-color: var(--color-background-mute);
  border-radius: 4px;
  font-size: 0.875rem;
  color: var(--color-text);
}

.classification-tags {
  margin-top: 1rem;
}

.tags-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin-bottom: 0.5rem;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  background-color: var(--color-background-mute);
  border-radius: 4px;
  font-size: 0.875rem;
  color: var(--color-text);
}
</style> 