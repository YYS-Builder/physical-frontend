import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import ShareDialog from '../ShareDialog.vue'
import { useDocumentStore } from '@/stores/documents'
import type { DocumentStore } from '@/stores/documents'

// Mock the document store
vi.mock('@/stores/documents', () => ({
  useDocumentStore: vi.fn(() => ({
    getDocumentShares: vi.fn().mockResolvedValue([]),
    getShareLink: vi.fn().mockResolvedValue({ link: 'https://example.com/share/123' }),
    shareDocument: vi.fn(),
    removeShare: vi.fn(),
    updateSharePermission: vi.fn(),
    updateShareLink: vi.fn()
  }))
}))

// Mock console.error
vi.spyOn(console, 'error').mockImplementation(() => {})

// Mock navigator.clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined)
  }
})

describe('ShareDialog', () => {
  let wrapper: VueWrapper
  let documentStore: DocumentStore

  beforeEach(() => {
    documentStore = useDocumentStore()
    wrapper = mount(ShareDialog, {
      props: {
        documentId: '123'
      },
      global: {
        stubs: {
          'font-awesome-icon': true
        }
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.dialog-header').exists()).toBe(true)
    expect(wrapper.find('.share-options').exists()).toBe(true)
  })

  it('fetches shared users and share link on mount', async () => {
    await wrapper.vm.$nextTick()
    expect(documentStore.getDocumentShares).toHaveBeenCalledWith('123')
    expect(documentStore.getShareLink).toHaveBeenCalledWith('123')
  })

  it('adds a user to share with', async () => {
    const user = {
      id: '456',
      name: 'Test User',
      email: 'test@example.com',
      permission: 'view'
    }

    documentStore.shareDocument.mockResolvedValue({ data: user })
    wrapper.vm.searchQuery = 'test@example.com'

    await wrapper.find('.btn-primary').trigger('click')
    expect(documentStore.shareDocument).toHaveBeenCalledWith('123', {
      email: 'test@example.com',
      permission: 'view'
    })
    expect(wrapper.vm.sharedUsers).toContainEqual(user)
  })

  it('removes a user from sharing', async () => {
    const user = {
      id: '456',
      name: 'Test User',
      email: 'test@example.com',
      permission: 'view'
    }

    wrapper.vm.sharedUsers = [user]
    await wrapper.find('.btn-icon').trigger('click')
    expect(documentStore.removeShare).toHaveBeenCalledWith('123', '456')
    expect(wrapper.vm.sharedUsers).toHaveLength(0)
  })

  it('updates user permission', async () => {
    const user = {
      id: '456',
      name: 'Test User',
      email: 'test@example.com',
      permission: 'view'
    }

    wrapper.vm.sharedUsers = [user]
    const select = wrapper.find('select')
    await select.setValue('edit')

    expect(documentStore.updateSharePermission).toHaveBeenCalledWith('123', '456', {
      permission: 'edit'
    })
  })

  it('updates share link access', async () => {
    wrapper.vm.allowPublicAccess = true
    wrapper.vm.requirePassword = true
    wrapper.vm.linkPassword = 'test123'

    await wrapper.vm.updateLinkAccess()
    expect(documentStore.updateShareLink).toHaveBeenCalledWith('123', {
      allowPublicAccess: true,
      requirePassword: true,
      password: 'test123'
    })
  })

  it('copies share link to clipboard', async () => {
    wrapper.vm.shareLink = 'https://example.com/share/123'
    await wrapper.vm.copyLink()
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('https://example.com/share/123')
  })

  it('handles errors when fetching data', async () => {
    documentStore.getDocumentShares.mockRejectedValue(new Error('Failed to fetch shares'))
    documentStore.getShareLink.mockRejectedValue(new Error('Failed to fetch link'))

    await wrapper.vm.getSharedUsers()
    await wrapper.vm.getShareLink()

    expect(console.error).toHaveBeenCalledWith('Failed to fetch shared users:', expect.any(Error))
    expect(console.error).toHaveBeenCalledWith('Failed to fetch share link:', expect.any(Error))
  })

  it('emits save event with correct data', async () => {
    const user = {
      id: '456',
      name: 'Test User',
      email: 'test@example.com',
      permission: 'view'
    }

    wrapper.vm.sharedUsers = [user]
    wrapper.vm.shareLink = 'https://example.com/share/123'
    wrapper.vm.allowPublicAccess = true
    wrapper.vm.requirePassword = false

    await wrapper.vm.saveChanges()
    expect(wrapper.emitted('save')).toBeTruthy()
    expect(wrapper.emitted('save')[0][0]).toEqual({
      sharedUsers: [user],
      shareLink: 'https://example.com/share/123',
      allowPublicAccess: true,
      requirePassword: false
    })
  })
}) 