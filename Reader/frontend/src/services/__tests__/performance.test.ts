import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { usePerformanceMonitor } from '../performance'
import { PerformanceMonitor } from '../PerformanceMonitor'
import type { PerformanceMetrics } from '../PerformanceMonitor'

describe('PerformanceService', () => {
  let mockPerformanceMonitor: PerformanceMonitor

  beforeEach(() => {
    mockPerformanceMonitor = {
      getMetrics: vi.fn().mockReturnValue({
        fcp: 1000,
        lcp: 2000,
        fid: 50,
        cls: 0.1,
        ttfb: 300,
        tti: 3000,
        fmp: 1500,
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
      }),
      getOptimizationSuggestions: vi.fn().mockReturnValue([
        'Optimize images',
        'Enable compression',
        'Reduce third-party scripts'
      ]),
      cleanup: vi.fn()
    } as unknown as PerformanceMonitor

    vi.spyOn(PerformanceMonitor.prototype, 'getMetrics').mockImplementation(mockPerformanceMonitor.getMetrics)
    vi.spyOn(PerformanceMonitor.prototype, 'getOptimizationSuggestions').mockImplementation(mockPerformanceMonitor.getOptimizationSuggestions)
    vi.spyOn(PerformanceMonitor.prototype, 'cleanup').mockImplementation(mockPerformanceMonitor.cleanup)
  })

  it('should return metrics and suggestions', async () => {
    const { metrics, suggestions, getMetrics, getSuggestions } = usePerformanceMonitor()

    expect(metrics.value).toEqual(mockPerformanceMonitor.getMetrics())
    expect(suggestions.value).toEqual([])

    const fetchedMetrics = await getMetrics()
    const fetchedSuggestions = await getSuggestions()

    expect(fetchedMetrics).toEqual(mockPerformanceMonitor.getMetrics())
    expect(fetchedSuggestions).toEqual(mockPerformanceMonitor.getOptimizationSuggestions())
  })

  it('should update metrics periodically', async () => {
    const { metrics, suggestions } = usePerformanceMonitor()

    // Wait for the first update
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(metrics.value).toEqual(mockPerformanceMonitor.getMetrics())
    expect(suggestions.value).toEqual(mockPerformanceMonitor.getOptimizationSuggestions())
  })

  it('should cleanup on unmount', async () => {
    const TestComponent = {
      template: '<div></div>',
      setup() {
        usePerformanceMonitor()
      }
    }

    const wrapper = mount(TestComponent)
    await wrapper.unmount()

    expect(mockPerformanceMonitor.cleanup).toHaveBeenCalled()
  })
}) 