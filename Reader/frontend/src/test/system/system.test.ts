import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import App from '@/App.vue'
import { createTestWrapper, mockUserStore, mockDocumentStore, mockAnalyticsStore } from '@/test/utils'
import { useUserStore } from '@/stores/user'
import { useDocumentStore } from '@/stores/document'
import { useAnalyticsStore } from '@/stores/analytics'

describe('System Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUserStore()
    mockDocumentStore()
    mockAnalyticsStore()
  })

  it('initializes application correctly', async () => {
    const wrapper = createTestWrapper(App)
    expect(wrapper.exists()).toBe(true)
    
    // Check if main layout components are rendered
    expect(wrapper.find('nav').exists()).toBe(true)
    expect(wrapper.find('main').exists()).toBe(true)
    expect(wrapper.find('footer').exists()).toBe(true)
  })

  it('handles user authentication flow', async () => {
    const wrapper = createTestWrapper(App)
    const userStore = useUserStore()
    
    // Test login
    await userStore.login('test@example.com', 'password')
    expect(userStore.isAuthenticated).toBe(true)
    expect(userStore.user).toBeDefined()
    
    // Test logout
    await userStore.logout()
    expect(userStore.isAuthenticated).toBe(false)
    expect(userStore.user).toBeNull()
  })

  it('manages document operations', async () => {
    const wrapper = createTestWrapper(App)
    const documentStore = useDocumentStore()
    
    // Test document upload
    const testFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    await documentStore.uploadDocument(testFile)
    expect(documentStore.documents.length).toBeGreaterThan(0)
    
    // Test document deletion
    const documentId = documentStore.documents[0].id
    await documentStore.deleteDocument(documentId)
    expect(documentStore.documents.find(doc => doc.id === documentId)).toBeUndefined()
  })

  it('tracks analytics data', async () => {
    const wrapper = createTestWrapper(App)
    const analyticsStore = useAnalyticsStore()
    
    // Simulate reading activity
    await analyticsStore.trackReadingTime(300) // 5 minutes
    expect(analyticsStore.readingStats.totalReadingTime).toBeGreaterThan(0)
    
    // Check document completion
    await analyticsStore.trackDocumentCompletion('test-doc-id')
    expect(analyticsStore.readingStats.documentsRead).toBeGreaterThan(0)
  })

  it('handles error states gracefully', async () => {
    const wrapper = createTestWrapper(App)
    const userStore = useUserStore()
    
    // Test invalid login
    await expect(userStore.login('invalid@example.com', 'wrong')).rejects.toThrow()
    
    // Test network error handling
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'))
    await expect(userStore.login('test@example.com', 'password')).rejects.toThrow()
  })

  it('maintains data persistence', async () => {
    const wrapper = createTestWrapper(App)
    const userStore = useUserStore()
    const documentStore = useDocumentStore()
    
    // Simulate data persistence
    await userStore.login('test@example.com', 'password')
    const testFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    await documentStore.uploadDocument(testFile)
    
    // Verify data is stored
    expect(localStorage.getItem('user')).toBeDefined()
    expect(localStorage.getItem('documents')).toBeDefined()
  })

  it('handles concurrent operations', async () => {
    const wrapper = createTestWrapper(App)
    const documentStore = useDocumentStore()
    
    // Simulate multiple concurrent uploads
    const uploadPromises = Array(5).fill(null).map((_, i) => {
      const file = new File([`content ${i}`], `test${i}.pdf`, { type: 'application/pdf' })
      return documentStore.uploadDocument(file)
    })
    
    await Promise.all(uploadPromises)
    expect(documentStore.documents.length).toBe(5)
  })
}) 