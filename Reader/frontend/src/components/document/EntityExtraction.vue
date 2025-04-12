<template>
  <div class="entity-extraction">
    <div class="entity-header">
      <h3>Entity Extraction</h3>
      <div class="entity-count">
        {{ entities.length }} entities found
      </div>
    </div>
    
    <div class="entity-types" v-if="entitySummary">
      <div
        v-for="(count, type) in entitySummary"
        :key="type"
        class="entity-type"
      >
        <div class="entity-type-label">{{ type }}</div>
        <div class="entity-type-count">{{ count }}</div>
      </div>
    </div>
    
    <div class="entity-list">
      <div
        v-for="entity in sortedEntities"
        :key="entity.id"
        class="entity-item"
      >
        <div class="entity-content">
          <span class="entity-text">{{ entity.text }}</span>
          <span class="entity-type-tag">{{ entity.type }}</span>
        </div>
        <div class="entity-confidence">
          <div class="confidence-bar">
            <div
              class="confidence-fill"
              :style="{ width: `${entity.confidence * 100}%` }"
            ></div>
          </div>
          <span class="confidence-value">
            {{ Math.round(entity.confidence * 100) }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

interface Entity {
  id: string
  text: string
  type: string
  confidence: number
}

export default defineComponent({
  name: 'EntityExtraction',
  props: {
    entities: {
      type: Array as () => Entity[],
      required: true
    }
  },
  setup(props) {
    const entitySummary = computed(() => {
      const summary: Record<string, number> = {}
      props.entities.forEach(entity => {
        summary[entity.type] = (summary[entity.type] || 0) + 1
      })
      return summary
    })
    
    const sortedEntities = computed(() => {
      return [...props.entities].sort((a, b) => b.confidence - a.confidence)
    })
    
    return {
      entitySummary,
      sortedEntities
    }
  }
})
</script>

<style scoped>
.entity-extraction {
  padding: 1rem;
  border-radius: 8px;
  background-color: var(--color-background-soft);
}

.entity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.entity-count {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.entity-types {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.entity-type {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: var(--color-background-mute);
  border-radius: 4px;
}

.entity-type-label {
  font-weight: 500;
  color: var(--color-text);
}

.entity-type-count {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.entity-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.entity-item {
  padding: 0.75rem;
  background-color: var(--color-background-mute);
  border-radius: 4px;
}

.entity-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.entity-text {
  font-weight: 500;
  color: var(--color-text);
}

.entity-type-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background-color: var(--color-background-soft);
  border-radius: 4px;
  color: var(--color-text-light);
}

.entity-confidence {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confidence-bar {
  flex: 1;
  height: 4px;
  background-color: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background-color: var(--color-primary);
  transition: width 0.3s ease;
}

.confidence-value {
  font-size: 0.75rem;
  color: var(--color-text-light);
  min-width: 3rem;
  text-align: right;
}
</style> 