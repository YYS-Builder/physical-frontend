<template>
  <div class="sentiment-analysis">
    <div class="sentiment-header">
      <h3>Sentiment Analysis</h3>
      <div class="sentiment-score" :class="sentimentClass">
        {{ sentimentScore }}%
      </div>
    </div>
    
    <div class="sentiment-details">
      <div class="sentiment-bar">
        <div
          class="sentiment-fill"
          :style="{ width: `${sentimentScore}%` }"
        ></div>
      </div>
      
      <div class="sentiment-labels">
        <span>Negative</span>
        <span>Neutral</span>
        <span>Positive</span>
      </div>
    </div>
    
    <div class="sentiment-summary" v-if="summary">
      <h4>Summary</h4>
      <p>{{ summary }}</p>
    </div>
    
    <div class="sentiment-keywords" v-if="keywords.length">
      <h4>Key Phrases</h4>
      <div class="keyword-tags">
        <span
          v-for="keyword in keywords"
          :key="keyword"
          class="keyword-tag"
        >
          {{ keyword }}
        </span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'SentimentAnalysis',
  props: {
    sentiment: {
      type: String,
      required: true
    },
    score: {
      type: Number,
      required: true
    },
    summary: {
      type: String,
      default: ''
    },
    keywords: {
      type: Array as () => string[],
      default: () => []
    }
  },
  setup(props) {
    const sentimentScore = computed(() => {
      return Math.round(props.score * 100)
    })
    
    const sentimentClass = computed(() => {
      return {
        'sentiment-positive': props.sentiment === 'positive',
        'sentiment-neutral': props.sentiment === 'neutral',
        'sentiment-negative': props.sentiment === 'negative'
      }
    })
    
    return {
      sentimentScore,
      sentimentClass
    }
  }
})
</script>

<style scoped>
.sentiment-analysis {
  padding: 1rem;
  border-radius: 8px;
  background-color: var(--color-background-soft);
}

.sentiment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.sentiment-score {
  font-size: 1.5rem;
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.sentiment-positive {
  color: var(--color-success);
  background-color: var(--color-success-bg);
}

.sentiment-neutral {
  color: var(--color-warning);
  background-color: var(--color-warning-bg);
}

.sentiment-negative {
  color: var(--color-danger);
  background-color: var(--color-danger-bg);
}

.sentiment-details {
  margin-bottom: 1rem;
}

.sentiment-bar {
  height: 8px;
  background-color: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.sentiment-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.sentiment-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.sentiment-summary {
  margin-bottom: 1rem;
}

.sentiment-summary h4 {
  margin-bottom: 0.5rem;
  color: var(--color-text);
}

.sentiment-summary p {
  color: var(--color-text-light);
  line-height: 1.5;
}

.sentiment-keywords {
  margin-top: 1rem;
}

.sentiment-keywords h4 {
  margin-bottom: 0.5rem;
  color: var(--color-text);
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  padding: 0.25rem 0.75rem;
  background-color: var(--color-background-mute);
  border-radius: 4px;
  font-size: 0.875rem;
  color: var(--color-text);
}
</style> 