<template>
  <div class="lazy-image" :style="{ aspectRatio: aspectRatio }">
    <img
      v-if="isLoaded"
      :src="src"
      :alt="alt"
      :class="['image', { 'fade-in': isLoaded }]"
      @load="handleLoad"
      @error="handleError"
    />
    <div v-else class="placeholder" :style="{ backgroundColor: placeholderColor }">
      <i v-if="showIcon" :class="['fas', placeholderIcon]"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  aspectRatio: {
    type: String,
    default: '16/9'
  },
  placeholderColor: {
    type: String,
    default: 'var(--color-background-secondary)'
  },
  placeholderIcon: {
    type: String,
    default: 'fa-image'
  },
  showIcon: {
    type: Boolean,
    default: true
  },
  threshold: {
    type: Number,
    default: 0.1
  }
})

const emit = defineEmits(['load', 'error'])

const isLoaded = ref(false)
const observer = ref<IntersectionObserver | null>(null)

const handleLoad = () => {
  emit('load')
}

const handleError = () => {
  emit('error')
}

const handleIntersection = (entries: IntersectionObserverEntry[]) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      isLoaded.value = true
      observer.value?.disconnect()
    }
  })
}

onMounted(() => {
  observer.value = new IntersectionObserver(handleIntersection, {
    threshold: props.threshold
  })
  observer.value.observe(document.querySelector('.lazy-image')!)
})

onBeforeUnmount(() => {
  observer.value?.disconnect()
})
</script>

<style scoped>
.lazy-image {
  position: relative;
  overflow: hidden;
  background-color: var(--color-background-secondary);
}

.image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image.fade-in {
  opacity: 1;
}

.placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--color-text-tertiary);
}

.placeholder i {
  font-size: 2rem;
}
</style> 