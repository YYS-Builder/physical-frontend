import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DocumentUpload from '../DocumentUpload.vue'
import { useDocumentStore } from '@/stores/documents'

// Mock the document store
vi.mock('@/stores/documents', () => ({
  useDocumentStore: vi.fn(() => ({
    uploadDocument: vi.fn(),
    processDocument: vi.fn()
  }))
}))

describe('DocumentUpload', () => {
  let wrapper
  let documentStore

  beforeEach(() => {
    documentStore = useDocumentStore()
    wrapper = mount(DocumentUpload)
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.upload-area').exists()).toBe(true)
    expect(wrapper.find('input[type="file"]').exists()).toBe(true)
  })

  it('handles file selection', async () => {
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const input = wrapper.find('input[type="file"]')
    
    await input.trigger('change', {
      target: {
        files: [file]
      }
    })

    expect(wrapper.vm.files).toHaveLength(1)
    expect(wrapper.vm.files[0].name).toBe('test.pdf')
  })

  it('handles drag and drop', async () => {
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const dropEvent = {
      dataTransfer: {
        files: [file]
      },
      preventDefault: vi.fn()
    }

    await wrapper.find('.upload-area').trigger('dragover', dropEvent)
    expect(wrapper.vm.isDragging).toBe(true)

    await wrapper.find('.upload-area').trigger('drop', dropEvent)
    expect(wrapper.vm.isDragging).toBe(false)
    expect(wrapper.vm.files).toHaveLength(1)
  })

  it('removes files', async () => {
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    wrapper.vm.files = [{
      file,
      name: 'test.pdf',
      size: 1000,
      type: 'application/pdf',
      progress: 0,
      status: 'pending'
    }]

    await wrapper.find('.btn-icon').trigger('click')
    expect(wrapper.vm.files).toHaveLength(0)
  })

  it('uploads files', async () => {
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    wrapper.vm.files = [{
      file,
      name: 'test.pdf',
      size: 1000,
      type: 'application/pdf',
      progress: 0,
      status: 'pending'
    }]

    documentStore.uploadDocument.mockResolvedValue({ id: '123' })
    documentStore.processDocument.mockResolvedValue({})

    await wrapper.find('.btn-primary').trigger('click')
    expect(documentStore.uploadDocument).toHaveBeenCalled()
    expect(documentStore.processDocument).toHaveBeenCalledWith('123')
  })

  it('handles upload errors', async () => {
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    wrapper.vm.files = [{
      file,
      name: 'test.pdf',
      size: 1000,
      type: 'application/pdf',
      progress: 0,
      status: 'pending'
    }]

    documentStore.uploadDocument.mockRejectedValue(new Error('Upload failed'))

    await wrapper.find('.btn-primary').trigger('click')
    expect(wrapper.vm.files[0].status).toBe('error')
  })

  it('formats file size correctly', () => {
    expect(wrapper.vm.formatFileSize(1000)).toBe('1 KB')
    expect(wrapper.vm.formatFileSize(1000000)).toBe('1 MB')
    expect(wrapper.vm.formatFileSize(1000000000)).toBe('1 GB')
  })

  it('gets correct file icon', () => {
    expect(wrapper.vm.getFileIcon('application/pdf')).toBe('fas fa-file-pdf')
    expect(wrapper.vm.getFileIcon('application/msword')).toBe('fas fa-file-word')
    expect(wrapper.vm.getFileIcon('text/plain')).toBe('fas fa-file-alt')
    expect(wrapper.vm.getFileIcon('unknown')).toBe('fas fa-file')
  })
}) 