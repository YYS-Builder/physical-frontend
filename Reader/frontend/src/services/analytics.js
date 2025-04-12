import api from './api'

class AnalyticsService {
  async getAnalytics(params = {}) {
    try {
      const response = await api.get('/analytics', { params })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch analytics data')
    }
  }

  async getDocumentAnalytics(documentId, params = {}) {
    try {
      const response = await api.get(`/analytics/documents/${documentId}`, { params })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch document analytics')
    }
  }

  async exportData(params = {}) {
    try {
      const response = await api.get('/analytics/export', {
        params,
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to export analytics data')
    }
  }

  async getReadingPatterns(params = {}) {
    try {
      const response = await api.get('/analytics/patterns', { params })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch reading patterns')
    }
  }

  async getReadingSpeed(params = {}) {
    try {
      const response = await api.get('/analytics/speed', { params })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch reading speed data')
    }
  }

  async getCompletionRates(params) {
    const { dateRange, startDate, endDate } = params
    const queryParams = new URLSearchParams()

    if (dateRange !== 'custom') {
      queryParams.append('dateRange', dateRange)
    } else {
      if (startDate) queryParams.append('startDate', startDate)
      if (endDate) queryParams.append('endDate', endDate)
    }

    const response = await api.get(`/analytics/completion?${queryParams.toString()}`)
    return response.data
  }
}

export const analyticsService = new AnalyticsService() 