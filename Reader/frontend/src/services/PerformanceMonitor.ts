import { ref } from 'vue'
import type { Ref } from 'vue'

export interface PerformanceMetrics {
  fcp: number // First Contentful Paint
  lcp: number // Largest Contentful Paint
  fid: number // First Input Delay
  cls: number // Cumulative Layout Shift
  ttfb: number // Time to First Byte
  tti: number // Time to Interactive
  fmp: number // First Meaningful Paint
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

export interface PerformanceThresholds {
  fcp: number
  lcp: number
  fid: number
  cls: number
  ttfb: number
  tti: number
  fmp: number
}

export class PerformanceMonitor {
  private metrics: Ref<PerformanceMetrics> = ref({
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
  })

  private thresholds: PerformanceThresholds = {
    fcp: 1800, // 1.8 seconds
    lcp: 2500, // 2.5 seconds
    fid: 100,  // 100 milliseconds
    cls: 0.1,  // 0.1
    ttfb: 200, // 200 milliseconds
    tti: 3800, // 3.8 seconds
    fmp: 2000  // 2 seconds
  }

  private observer: PerformanceObserver | null = null
  private resourceTimingBuffer: PerformanceResourceTiming[] = []

  constructor() {
    this.setupPerformanceObserver()
    this.setupResourceTiming()
    this.setupMemoryMonitoring()
  }

  private setupPerformanceObserver() {
    if (typeof PerformanceObserver === 'undefined') return

    this.observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        switch (entry.entryType) {
          case 'paint':
            if (entry.name === 'first-contentful-paint') {
              this.metrics.value.fcp = entry.startTime
            }
            break
          case 'largest-contentful-paint':
            this.metrics.value.lcp = entry.startTime
            break
          case 'layout-shift':
            if (!entry.hadRecentInput) {
              this.metrics.value.cls += entry.value
            }
            break
        }
      }
    })

    this.observer.observe({ entryTypes: ['paint', 'largest-contentful-paint', 'layout-shift'] })
  }

  private setupResourceTiming() {
    if (typeof PerformanceObserver === 'undefined') return

    const resourceObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'resource') {
          this.resourceTimingBuffer.push(entry as PerformanceResourceTiming)
          this.updateNetworkMetrics()
        }
      }
    })

    resourceObserver.observe({ entryTypes: ['resource'] })
  }

  private setupMemoryMonitoring() {
    if (typeof performance.memory === 'undefined') return

    setInterval(() => {
      const memory = performance.memory
      this.metrics.value.memory = {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit
      }
    }, 5000)
  }

  private updateNetworkMetrics() {
    const network = this.metrics.value.network
    network.requests = this.resourceTimingBuffer.length
    network.transferred = this.resourceTimingBuffer.reduce((total, entry) => {
      return total + (entry.transferSize || 0)
    }, 0)
    network.time = this.resourceTimingBuffer.reduce((total, entry) => {
      return total + (entry.duration || 0)
    }, 0)
  }

  public getMetrics(): PerformanceMetrics {
    return this.metrics.value
  }

  public getThresholds(): PerformanceThresholds {
    return this.thresholds
  }

  public isMetricBelowThreshold(metric: keyof PerformanceMetrics): boolean {
    if (typeof this.metrics.value[metric] === 'number') {
      return this.metrics.value[metric] < this.thresholds[metric]
    }
    return false
  }

  public getPerformanceScore(): number {
    const metrics = this.metrics.value
    const weights = {
      fcp: 0.2,
      lcp: 0.25,
      fid: 0.15,
      cls: 0.15,
      ttfb: 0.1,
      tti: 0.1,
      fmp: 0.05
    }

    let score = 0
    let totalWeight = 0

    for (const [metric, weight] of Object.entries(weights)) {
      const value = metrics[metric as keyof PerformanceMetrics]
      const threshold = this.thresholds[metric as keyof PerformanceThresholds]
      
      if (typeof value === 'number' && typeof threshold === 'number') {
        const normalizedValue = Math.min(value / threshold, 1)
        score += (1 - normalizedValue) * weight
        totalWeight += weight
      }
    }

    return totalWeight > 0 ? (score / totalWeight) * 100 : 0
  }

  public getOptimizationSuggestions(): string[] {
    const suggestions: string[] = []
    const metrics = this.metrics.value

    if (metrics.fcp > this.thresholds.fcp) {
      suggestions.push('Optimize First Contentful Paint by reducing render-blocking resources')
    }

    if (metrics.lcp > this.thresholds.lcp) {
      suggestions.push('Improve Largest Contentful Paint by optimizing images and critical resources')
    }

    if (metrics.fid > this.thresholds.fid) {
      suggestions.push('Reduce First Input Delay by minimizing main thread work')
    }

    if (metrics.cls > this.thresholds.cls) {
      suggestions.push('Reduce Cumulative Layout Shift by specifying image dimensions and avoiding layout shifts')
    }

    if (metrics.ttfb > this.thresholds.ttfb) {
      suggestions.push('Optimize Time to First Byte by improving server response time')
    }

    if (metrics.tti > this.thresholds.tti) {
      suggestions.push('Improve Time to Interactive by reducing JavaScript execution time')
    }

    if (metrics.memory.used > metrics.memory.limit * 0.8) {
      suggestions.push('High memory usage detected. Consider optimizing memory-intensive operations')
    }

    if (metrics.network.requests > 50) {
      suggestions.push('High number of network requests. Consider bundling resources and using HTTP/2')
    }

    return suggestions
  }

  public cleanup() {
    if (this.observer) {
      this.observer.disconnect()
    }
  }
}

export const performanceMonitor = new PerformanceMonitor() 