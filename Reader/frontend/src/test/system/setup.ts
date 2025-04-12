import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { vi } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock fetch
global.fetch = vi.fn()

// Mock IntersectionObserver
const mockIntersectionObserver = vi.fn()
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
})
window.IntersectionObserver = mockIntersectionObserver

// Configure Vue Test Utils
config.global.plugins = [createPinia()]

// Mock router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn()
  }),
  useRoute: () => ({
    path: '/',
    query: {},
    params: {}
  })
}))

// Mock stores
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    user: null,
    isAuthenticated: false,
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn()
  })
}))

vi.mock('@/stores/document', () => ({
  useDocumentStore: () => ({
    documents: [],
    uploadDocument: vi.fn(),
    deleteDocument: vi.fn(),
    getDocument: vi.fn()
  })
}))

vi.mock('@/stores/analytics', () => ({
  useAnalyticsStore: () => ({
    trackEvent: vi.fn(),
    trackPageView: vi.fn(),
    getAnalytics: vi.fn()
  })
})) 