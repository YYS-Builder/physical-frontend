<!-- PerformanceDashboard.vue -->
<template>
  <div class="performance-dashboard p-6">
    <div class="performance-score mb-8" data-test="performance-score">
      <h2 class="text-2xl font-bold mb-2">Performance Score</h2>
      <div class="text-4xl font-bold" :class="scoreClass">
        {{ Math.round(performanceScore) }}
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <div v-for="metric in coreMetrics" :key="metric.name" class="metric-card p-4 bg-white rounded-lg shadow" data-test="core-metric">
        <h3 class="text-lg font-semibold mb-2">{{ metric.label }}</h3>
        <div class="text-2xl font-bold" :class="getMetricClass(metric.value)" :data-test="`${metric.name}-value`">
          {{ formatValue(metric.value, metric.unit) }}
        </div>
      </div>
    </div>

    <div class="system-metrics grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="memory-usage p-4 bg-white rounded-lg shadow" data-test="memory-usage">
        <h3 class="text-lg font-semibold mb-2">Memory Usage</h3>
        <div class="text-2xl font-bold" :class="getMemoryClass">
          {{ Math.round(memoryUsage) }}%
        </div>
        <div class="text-sm text-gray-600">
          {{ formatBytes(metrics.memory.used) }} / {{ formatBytes(metrics.memory.total) }}
        </div>
      </div>

      <div class="network-usage p-4 bg-white rounded-lg shadow" data-test="network-usage">
        <h3 class="text-lg font-semibold mb-2">Network Usage</h3>
        <div class="text-2xl font-bold">
          {{ networkUsage.requests }} requests
        </div>
        <div class="text-sm text-gray-600">
          {{ formatBytes(networkUsage.transferred) }} transferred
        </div>
      </div>
    </div>

    <div class="optimization-suggestions">
      <h2 class="text-2xl font-bold mb-4">Optimization Suggestions</h2>
      <ul class="space-y-2">
        <li v-for="(suggestion, index) in suggestions" :key="index" class="flex items-start" data-test="suggestion">
          <span class="text-yellow-500 mr-2">•</span>
          <span>{{ suggestion }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed } from 'vue'
import { usePerformanceStore } from '@/stores/performance'

const store = usePerformanceStore()

const coreMetrics = computed(() => [
  { name: 'fcp', label: 'First Contentful Paint', value: store.metrics.fcp, unit: 'ms' },
  { name: 'lcp', label: 'Largest Contentful Paint', value: store.metrics.lcp, unit: 'ms' },
  { name: 'fid', label: 'First Input Delay', value: store.metrics.fid, unit: 'ms' },
  { name: 'cls', label: 'Cumulative Layout Shift', value: store.metrics.cls, unit: '' },
  { name: 'ttfb', label: 'Time to First Byte', value: store.metrics.ttfb, unit: 'ms' },
  { name: 'tti', label: 'Time to Interactive', value: store.metrics.tti, unit: 'ms' },
  { name: 'fmp', label: 'First Meaningful Paint', value: store.metrics.fmp, unit: 'ms' }
])

const performanceScore = computed(() => store.performanceScore)
const memoryUsage = computed(() => store.memoryUsage)
const networkUsage = computed(() => store.networkUsage)
const suggestions = computed(() => store.suggestions)
const metrics = computed(() => store.metrics)

const scoreClass = computed(() => {
  if (performanceScore.value >= 90) return 'text-green-500'
  if (performanceScore.value >= 70) return 'text-yellow-500'
  return 'text-red-500'
})

const getMemoryClass = computed(() => {
  if (memoryUsage.value < 50) return 'text-green-500'
  if (memoryUsage.value < 80) return 'text-yellow-500'
  return 'text-red-500'
})

const getMetricClass = (value: number) => {
  if (value < 1000) return 'text-green-500'
  if (value < 2000) return 'text-yellow-500'
  return 'text-red-500'
}

const formatValue = (value: number, unit: string) => {
  if (unit === 'ms') {
    if (value >= 1000) return `${(value / 1000).toFixed(1)}s`
    return `${value}ms`
  }
  return value.toFixed(2)
}

const formatBytes = (bytes: number) => {
  const units = ['B', 'KB', 'MB', 'GB']
  let value = bytes
  let unitIndex = 0

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex++
  }

  return `${value.toFixed(1)} ${units[unitIndex]}`
}

onMounted(() => {
  store.startMonitoring()
})

onUnmounted(() => {
  store.stopMonitoring()
})
</script>

<style scoped>
.performance-dashboard {
  background-color: #f8fafc;
  min-height: 100vh;
}

.metric-card {
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
}
</style> 