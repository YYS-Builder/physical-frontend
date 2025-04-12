import { defineStore } from 'pinia'
import { performanceMonitor } from '@/services/PerformanceMonitor'

interface PerformanceMetrics {
  fcp: number
  lcp: number
  fid: number
  cls: number
  ttfb: number
  tti: number
  fmp: number
  memory: {
    used: number
    total: number
    limit: number
  }
  network: {
    requests: number
    transferred: number
    time: number
  }
}

export const usePerformanceStore = defineStore('performance', {
  state: () => ({
    metrics: {
      fcp: 0,
      lcp: 0,
      fid: 0,
      cls: 0,
      ttfb: 0,
      tti: 0,
      fmp: 0,
      memory: {
        used: 0,
        total: 0,
        limit: 0
      },
      network: {
        requests: 0,
        transferred: 0,
        time: 0
      }
    } as PerformanceMetrics,
    suggestions: [] as string[],
    updateInterval: null as number | null
  }),

  getters: {
    performanceScore: (state) => {
      const weights = {
        fcp: 0.2,
        lcp: 0.25,
        fid: 0.15,
        cls: 0.15,
        ttfb: 0.1,
        tti: 0.1,
        fmp: 0.05
      }

      const scores = {
        fcp: Math.max(0, 100 - (state.metrics.fcp / 2000) * 100),
        lcp: Math.max(0, 100 - (state.metrics.lcp / 4000) * 100),
        fid: Math.max(0, 100 - (state.metrics.fid / 100) * 100),
        cls: Math.max(0, 100 - (state.metrics.cls / 0.25) * 100),
        ttfb: Math.max(0, 100 - (state.metrics.ttfb / 600) * 100),
        tti: Math.max(0, 100 - (state.metrics.tti / 5000) * 100),
        fmp: Math.max(0, 100 - (state.metrics.fmp / 3000) * 100)
      }

      return Object.entries(weights).reduce(
        (score, [metric, weight]) => score + scores[metric as keyof typeof scores] * weight,
        0
      )
    },

    memoryUsage: (state) => {
      if (state.metrics.memory.total === 0) return 0
      return (state.metrics.memory.used / state.metrics.memory.total) * 100
    },

    networkUsage: (state) => ({
      requests: state.metrics.network.requests,
      transferred: state.metrics.network.transferred,
      time: state.metrics.network.time
    })
  },

  actions: {
    async updateMetrics() {
      try {
        const metrics = await performanceMonitor.getMetrics()
        this.metrics = metrics
        this.suggestions = await performanceMonitor.getOptimizationSuggestions()
      } catch (error) {
        console.error('Failed to update performance metrics:', error)
      }
    },

    startMonitoring(interval = 5000) {
      this.updateMetrics()
      this.updateInterval = window.setInterval(() => {
        this.updateMetrics()
      }, interval)
    },

    stopMonitoring() {
      if (this.updateInterval) {
        window.clearInterval(this.updateInterval)
        this.updateInterval = null
      }
    }
  }
}) 