import { vi } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'

// Mock IntersectionObserver
const mockIntersectionObserver = vi.fn()
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
})
window.IntersectionObserver = mockIntersectionObserver

// Mock ResizeObserver
const mockResizeObserver = vi.fn()
mockResizeObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
})
window.ResizeObserver = mockResizeObserver

// Mock Performance API
const mockPerformance = {
  now: vi.fn(),
  mark: vi.fn(),
  measure: vi.fn(),
  getEntriesByName: vi.fn(),
  getEntriesByType: vi.fn(),
  clearMarks: vi.fn(),
  clearMeasures: vi.fn(),
  memory: {
    usedJSHeapSize: 1000000,
    totalJSHeapSize: 2000000,
    jsHeapSizeLimit: 3000000
  }
}
window.performance = mockPerformance as unknown as Performance

// Configure Vue Test Utils
config.global.plugins = [createPinia()]

// Mock fetch
global.fetch = vi.fn()

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn(),
  removeItem: vi.fn(),
  length: 0,
  key: vi.fn()
}
global.localStorage = localStorageMock as unknown as Storage

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn(),
  removeItem: vi.fn(),
  length: 0,
  key: vi.fn()
}
global.sessionStorage = sessionStorageMock as unknown as Storage

// Mock performance API
Object.defineProperty(window, 'performance', {
  value: {
    memory: {
      usedJSHeapSize: 0,
      totalJSHeapSize: 0,
      jsHeapSizeLimit: 0
    },
    getEntriesByType: () => [],
    mark: vi.fn(),
    measure: vi.fn(),
    clearMarks: vi.fn(),
    clearMeasures: vi.fn()
  },
  writable: true
})

// Mock PerformanceObserver
Object.defineProperty(window, 'PerformanceObserver', {
  value: vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    disconnect: vi.fn()
  })),
  writable: true
}) 