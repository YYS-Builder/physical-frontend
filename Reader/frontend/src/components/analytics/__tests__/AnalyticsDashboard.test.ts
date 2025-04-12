import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AnalyticsDashboard from '../AnalyticsDashboard.vue'
import { useAnalyticsStore } from '@/stores/analytics'
import type { AnalyticsStore } from '@/types/stores'

// Mock the analytics store
vi.mock('@/stores/analytics', () => ({
  useAnalyticsStore: vi.fn(() => ({
    summary: {
      totalDocuments: 100,
      totalReadingTime: 500,
      averageReadingSpeed: 200,
      completionRate: 75
    },
    readingActivity: [],
    documentTypes: [],
    readingSpeedTrend: [],
    completionRate: [],
    topDocuments: [],
    readingPatterns: [],
    loading: false,
    error: null,
    getSummary: vi.fn(),
    getReadingActivity: vi.fn(),
    getDocumentTypes: vi.fn(),
    getReadingSpeedTrend: vi.fn(),
    getCompletionRate: vi.fn(),
    getTopDocuments: vi.fn(),
    getReadingPatterns: vi.fn(),
    exportData: vi.fn()
  }))
}))

describe('AnalyticsDashboard', () => {
  let wrapper
  let analyticsStore: AnalyticsStore

  beforeEach(() => {
    analyticsStore = useAnalyticsStore()
    wrapper = mount(AnalyticsDashboard)
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.dashboard').exists()).toBe(true)
    expect(wrapper.find('.summary-cards').exists()).toBe(true)
  })

  it('fetches analytics data on mount', () => {
    expect(analyticsStore.getSummary).toHaveBeenCalled()
    expect(analyticsStore.getReadingActivity).toHaveBeenCalled()
    expect(analyticsStore.getDocumentTypes).toHaveBeenCalled()
    expect(analyticsStore.getReadingSpeedTrend).toHaveBeenCalled()
    expect(analyticsStore.getCompletionRate).toHaveBeenCalled()
    expect(analyticsStore.getTopDocuments).toHaveBeenCalled()
    expect(analyticsStore.getReadingPatterns).toHaveBeenCalled()
  })

  it('displays loading state', async () => {
    analyticsStore.loading = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.loading').exists()).toBe(true)
  })

  it('displays error state', async () => {
    analyticsStore.error = 'Failed to fetch analytics'
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.error').exists()).toBe(true)
    expect(wrapper.find('.error').text()).toContain('Failed to fetch analytics')
  })

  it('displays summary cards correctly', () => {
    const cards = wrapper.findAll('.summary-card')
    expect(cards).toHaveLength(4)

    expect(cards[0].find('.title').text()).toBe('Total Documents')
    expect(cards[0].find('.value').text()).toBe('100')

    expect(cards[1].find('.title').text()).toBe('Total Reading Time')
    expect(cards[1].find('.value').text()).toBe('500 min')

    expect(cards[2].find('.title').text()).toBe('Average Reading Speed')
    expect(cards[2].find('.value').text()).toBe('200 wpm')

    expect(cards[3].find('.title').text()).toBe('Completion Rate')
    expect(cards[3].find('.value').text()).toBe('75%')
  })

  it('updates date range and refreshes data', async () => {
    const startDate = '2023-01-01'
    const endDate = '2023-01-31'

    await wrapper.find('input[type="date"]').setValue(startDate)
    await wrapper.findAll('input[type="date"]')[1].setValue(endDate)

    expect(analyticsStore.getReadingActivity).toHaveBeenCalledWith({
      startDate,
      endDate
    })
    expect(analyticsStore.getReadingSpeedTrend).toHaveBeenCalledWith({
      startDate,
      endDate
    })
    expect(analyticsStore.getCompletionRate).toHaveBeenCalledWith({
      startDate,
      endDate
    })
  })

  it('exports data', async () => {
    const mockBlob = new Blob(['test'], { type: 'text/csv' })
    const mockUrl = 'blob:test'
    const mockCreateObjectURL = vi.fn(() => mockUrl)
    const mockRevokeObjectURL = vi.fn()

    global.URL.createObjectURL = mockCreateObjectURL
    global.URL.revokeObjectURL = mockRevokeObjectURL

    analyticsStore.exportData.mockResolvedValue(mockBlob)
    await wrapper.find('.btn-export').trigger('click')

    expect(analyticsStore.exportData).toHaveBeenCalled()
    expect(mockCreateObjectURL).toHaveBeenCalledWith(mockBlob)
    expect(mockRevokeObjectURL).toHaveBeenCalledWith(mockUrl)
  })

  it('formats duration correctly', () => {
    expect(wrapper.vm.formatDuration(65)).toBe('1h 5m')
    expect(wrapper.vm.formatDuration(120)).toBe('2h')
    expect(wrapper.vm.formatDuration(45)).toBe('45m')
  })

  it('formats date range correctly', () => {
    const startDate = '2023-01-01'
    const endDate = '2023-01-31'
    expect(wrapper.vm.formatDateRange(startDate, endDate)).toBe('Jan 1 - Jan 31, 2023')
  })
}) 