import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { analyticsService } from '@/services/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
  // State
  const loading = ref(false)
  const error = ref(null)
  const totalDocuments = ref(0)
  const documentsChange = ref(0)
  const totalReadingTime = ref(0)
  const readingTimeChange = ref(0)
  const averageReadingSpeed = ref(0)
  const speedChange = ref(0)
  const completionRate = ref(0)
  const completionChange = ref(0)
  const topDocuments = ref([])
  const readingPatterns = ref([])
  const activityData = ref({ labels: [], values: [] })
  const typesData = ref({ labels: [], values: [] })
  const speedData = ref({ labels: [], values: [] })
  const completionData = ref({ labels: [], values: [] })

  // Actions
  const getAnalytics = async (params) => {
    loading.value = true
    error.value = null
    try {
      const data = await analyticsService.getAnalytics(params)
      updateState(data)
    } catch (err) {
      error.value = 'Failed to fetch analytics data'
      console.error('Error fetching analytics:', err)
    } finally {
      loading.value = false
    }
  }

  const updateState = (data) => {
    totalDocuments.value = data.totalDocuments
    documentsChange.value = data.documentsChange
    totalReadingTime.value = data.totalReadingTime
    readingTimeChange.value = data.readingTimeChange
    averageReadingSpeed.value = data.averageReadingSpeed
    speedChange.value = data.speedChange
    completionRate.value = data.completionRate
    completionChange.value = data.completionChange
    topDocuments.value = data.topDocuments
    readingPatterns.value = data.readingPatterns
    activityData.value = data.activityData
    typesData.value = data.typesData
    speedData.value = data.speedData
    completionData.value = data.completionData
  }

  const exportData = async (params) => {
    try {
      const blob = await analyticsService.exportData(params)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analytics-${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      error.value = 'Failed to export analytics data'
      console.error('Error exporting analytics:', err)
    }
  }

  // Computed
  const hasError = computed(() => error.value !== null)
  const isLoading = computed(() => loading.value)

  return {
    // State
    loading,
    error,
    totalDocuments,
    documentsChange,
    totalReadingTime,
    readingTimeChange,
    averageReadingSpeed,
    speedChange,
    completionRate,
    completionChange,
    topDocuments,
    readingPatterns,
    activityData,
    typesData,
    speedData,
    completionData,

    // Actions
    getAnalytics,
    exportData,

    // Computed
    hasError,
    isLoading
  }
}) 