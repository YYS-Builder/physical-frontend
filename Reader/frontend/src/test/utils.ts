import { mount, VueWrapper } from '@vue/test-utils'
import { ComponentPublicInstance } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import { useDocumentStore } from '@/stores/document'
import { useAnalyticsStore } from '@/stores/analytics'

export const createTestWrapper = (
  component: any,
  options: any = {}
): VueWrapper<ComponentPublicInstance> => {
  const pinia = createPinia()
  setActivePinia(pinia)

  return mount(component, {
    global: {
      plugins: [pinia]
    },
    ...options
  })
}

export const mockUserStore = () => {
  const store = useUserStore()
  store.$patch({
    user: {
      id: 1,
      email: 'test@example.com',
      name: 'Test User'
    },
    isAuthenticated: true
  })
  return store
}

export const mockDocumentStore = () => {
  const store = useDocumentStore()
  store.$patch({
    documents: [
      {
        id: 1,
        title: 'Test Document',
        content: 'Test content',
        createdAt: new Date().toISOString()
      }
    ]
  })
  return store
}

export const mockAnalyticsStore = () => {
  const store = useAnalyticsStore()
  store.$patch({
    readingStats: {
      totalReadingTime: 120,
      documentsRead: 5,
      averageSpeed: 30,
      streakDays: 7,
      completionRate: 0.8
    }
  })
  return store
}

export const mockPerformanceMetrics = () => {
  const metrics = {
    fcp: 1000,
    lcp: 2000,
    fid: 50,
    cls: 0.1,
    ttfb: 300,
    tti: 2500,
    fmp: 1500,
    memory: {
      used: 1000000,
      total: 2000000,
      limit: 3000000
    },
    network: {
      requests: 10,
      transferred: 500000,
      time: 2000
    }
  }

  // Mock performance API
  window.performance.getEntriesByName = vi.fn().mockImplementation((name) => {
    if (name === 'first-contentful-paint') {
      return [{ startTime: metrics.fcp }]
    }
    if (name === 'largest-contentful-paint') {
      return [{ startTime: metrics.lcp }]
    }
    return []
  })

  window.performance.getEntriesByType = vi.fn().mockImplementation((type) => {
    if (type === 'resource') {
      return Array(metrics.network.requests).fill({
        transferSize: metrics.network.transferred / metrics.network.requests,
        duration: metrics.network.time / metrics.network.requests
      })
    }
    return []
  })

  return metrics
}

export const waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0)) 