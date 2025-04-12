import { describe, it, expect, beforeEach, vi } from 'vitest'
import { PerformanceMonitor } from '../PerformanceMonitor'
import type { PerformanceMetrics, PerformanceThresholds } from '../PerformanceMonitor'

describe('PerformanceMonitor', () => {
  let monitor: PerformanceMonitor
  let mockPerformanceObserver: any
  let mockPerformance: any

  beforeEach(() => {
    // Mock PerformanceObserver
    mockPerformanceObserver = {
      observe: vi.fn(),
      disconnect: vi.fn()
    }
    global.PerformanceObserver = vi.fn().mockImplementation((callback) => {
      return {
        observe: mockPerformanceObserver.observe,
        disconnect: mockPerformanceObserver.disconnect
      }
    }) as any
    // @ts-ignore - Adding static property to mock
    global.PerformanceObserver.supportedEntryTypes = ['paint', 'largest-contentful-paint', 'layout-shift', 'resource']

    // Mock Performance API
    mockPerformance = {
      memory: {
        usedJSHeapSize: 1000000,
        totalJSHeapSize: 2000000,
        jsHeapSizeLimit: 3000000
      }
    }
    global.performance = mockPerformance as Performance

    monitor = new PerformanceMonitor()
  })

  it('initializes with default metrics', () => {
    const metrics = monitor.getMetrics()
    expect(metrics).toEqual({
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
  })

  it('returns correct thresholds', () => {
    const thresholds = monitor.getThresholds()
    expect(thresholds).toEqual({
      fcp: 1800,
      lcp: 2500,
      fid: 100,
      cls: 0.1,
      ttfb: 200,
      tti: 3800,
      fmp: 2000
    })
  })

  it('calculates performance score correctly', () => {
    const metrics: PerformanceMetrics = {
      fcp: 1000,
      lcp: 1500,
      fid: 50,
      cls: 0.05,
      ttfb: 100,
      tti: 2000,
      fmp: 1000,
      memory: {
        used: 1000000,
        total: 2000000,
        limit: 3000000
      },
      network: {
        requests: 10,
        transferred: 1000000,
        time: 1000
      }
    }

    // Mock getMetrics to return our test metrics
    vi.spyOn(monitor, 'getMetrics').mockReturnValue(metrics)

    const score = monitor.getPerformanceScore()
    expect(score).toBeGreaterThan(0)
    expect(score).toBeLessThanOrEqual(100)
  })

  it('provides optimization suggestions based on metrics', () => {
    const metrics: PerformanceMetrics = {
      fcp: 2000, // Above threshold
      lcp: 3000, // Above threshold
      fid: 50,   // Below threshold
      cls: 0.2,  // Above threshold
      ttfb: 300, // Above threshold
      tti: 4000, // Above threshold
      fmp: 1000, // Below threshold
      memory: {
        used: 2500000, // Above 80% of limit
        total: 2000000,
        limit: 3000000
      },
      network: {
        requests: 60, // Above threshold
        transferred: 1000000,
        time: 1000
      }
    }

    // Mock getMetrics to return our test metrics
    vi.spyOn(monitor, 'getMetrics').mockReturnValue(metrics)

    const suggestions = monitor.getOptimizationSuggestions()
    expect(suggestions).toContain('Optimize First Contentful Paint by reducing render-blocking resources')
    expect(suggestions).toContain('Improve Largest Contentful Paint by optimizing images and critical resources')
    expect(suggestions).toContain('Reduce Cumulative Layout Shift by specifying image dimensions and avoiding layout shifts')
    expect(suggestions).toContain('Optimize Time to First Byte by improving server response time')
    expect(suggestions).toContain('Improve Time to Interactive by reducing JavaScript execution time')
    expect(suggestions).toContain('High memory usage detected. Consider optimizing memory-intensive operations')
    expect(suggestions).toContain('High number of network requests. Consider bundling resources and using HTTP/2')
  })

  it('cleans up observers on cleanup', () => {
    monitor.cleanup()
    expect(mockPerformanceObserver.disconnect).toHaveBeenCalled()
  })

  it('handles missing PerformanceObserver gracefully', () => {
    // @ts-ignore - Mocking global object
    global.PerformanceObserver = undefined
    const newMonitor = new PerformanceMonitor()
    expect(newMonitor.getMetrics()).toBeDefined()
  })

  it('handles missing performance.memory gracefully', () => {
    // @ts-ignore - Mocking global object
    global.performance.memory = undefined
    const newMonitor = new PerformanceMonitor()
    expect(newMonitor.getMetrics().memory).toEqual({
      used: 0,
      total: 0,
      limit: 0
    })
  })
}) 