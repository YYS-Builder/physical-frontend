import { describe, it, expect, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import PerformanceDashboard from '../PerformanceDashboard.vue'
import { usePerformanceMonitor } from '@/services/performance'
import type { PerformanceMetrics } from '@/services/PerformanceMonitor'

const mockMetrics: PerformanceMetrics = {
  fcp: 1000,
  lcp: 2000,
  fid: 50,
  cls: 0.1,
  ttfb: 300,
  tti: 3000,
  fmp: 1500,
  memory: {
    used: 100,
    total: 1000,
    limit: 2000
  },
  network: {
    requests: 10,
    transferred: 1000,
    time: 500
  }
}

const mockSuggestions = ref([
  'Optimize images',
  'Enable compression',
  'Reduce third-party scripts'
])

vi.mock('@/services/performance', () => ({
  usePerformanceMonitor: vi.fn(() => ({
    metrics: ref(mockMetrics),
    suggestions: mockSuggestions,
    getMetrics: vi.fn(),
    getSuggestions: vi.fn()
  }))
}))

describe('PerformanceDashboard', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders correctly', () => {
    const wrapper = mount(PerformanceDashboard)
    expect(wrapper.exists()).toBe(true)
  })

  it('displays performance score', () => {
    const wrapper = mount(PerformanceDashboard)
    const scoreElement = wrapper.find('[data-test="performance-score"]')
    expect(scoreElement.exists()).toBe(true)
    expect(scoreElement.text()).toContain('Performance Score')
  })

  it('displays core metrics', () => {
    const wrapper = mount(PerformanceDashboard)
    const metrics = wrapper.findAll('[data-test="core-metric"]')
    expect(metrics).toHaveLength(7) // FCP, LCP, FID, CLS, TTFB, TTI, FMP
  })

  it('displays system metrics', () => {
    const wrapper = mount(PerformanceDashboard)
    const memoryMetric = wrapper.find('[data-test="memory-usage"]')
    const networkMetric = wrapper.find('[data-test="network-usage"]')
    expect(memoryMetric.exists()).toBe(true)
    expect(networkMetric.exists()).toBe(true)
  })

  it('displays optimization suggestions', () => {
    const wrapper = mount(PerformanceDashboard)
    const suggestions = wrapper.findAll('[data-test="suggestion"]')
    expect(suggestions).toHaveLength(3)
  })

  it('updates metrics periodically', async () => {
    const wrapper = mount(PerformanceDashboard)
    const getMetrics = vi.fn()
    const getSuggestions = vi.fn()

    vi.mocked(usePerformanceMonitor).mockImplementation(() => ({
      metrics: ref(mockMetrics),
      suggestions: ref([]),
      getMetrics,
      getSuggestions
    }))

    await wrapper.vm.$nextTick()
    expect(getMetrics).toHaveBeenCalled()
    expect(getSuggestions).toHaveBeenCalled()
  })

  it('formats values correctly', () => {
    const wrapper = mount(PerformanceDashboard)
    const fcpValue = wrapper.find('[data-test="fcp-value"]')
    expect(fcpValue.text()).toContain('1.0s')
  })

  it('cleans up intervals on unmount', () => {
    const wrapper = mount(PerformanceDashboard)
    const clearInterval = vi.spyOn(window, 'clearInterval')
    wrapper.unmount()
    expect(clearInterval).toHaveBeenCalled()
  })
}) 