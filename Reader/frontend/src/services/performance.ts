import { ref, onMounted, onUnmounted } from 'vue'
import { PerformanceMonitor, type PerformanceMetrics } from './PerformanceMonitor'

const performanceMonitor = new PerformanceMonitor()

export const usePerformanceMonitor = () => {
  const metrics = ref<PerformanceMetrics>(performanceMonitor.getMetrics())
  const suggestions = ref<string[]>([])

  const getMetrics = async (): Promise<PerformanceMetrics> => {
    return performanceMonitor.getMetrics()
  }

  const getSuggestions = async (): Promise<string[]> => {
    return performanceMonitor.getOptimizationSuggestions()
  }

  const updateMetrics = async () => {
    metrics.value = await getMetrics()
    suggestions.value = await getSuggestions()
  }

  onMounted(() => {
    // Update metrics every 5 seconds
    const updateInterval = window.setInterval(updateMetrics, 5000)
    updateMetrics()

    return () => {
      clearInterval(updateInterval)
      performanceMonitor.cleanup()
    }
  })

  return {
    metrics,
    suggestions,
    getMetrics,
    getSuggestions
  }
} 