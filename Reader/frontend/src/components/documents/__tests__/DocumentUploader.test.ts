import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DocumentUploader from '../DocumentUploader.vue'
import { imageProcessor } from '@/services/ImageProcessor'

vi.mock('@/services/ImageProcessor', () => ({
  imageProcessor: {
    processImage: vi.fn(),
    getError: vi.fn()
  }
}))

describe('DocumentUploader', () => {
  let wrapper: ReturnType<typeof mount>
  const mockProcessedImage = {
    url: 'data:image/jpeg;base64,mockdata',
    width: 800,
    height: 600,
    size: 1024 * 1024,
    format: 'jpeg',
    metadata: {
      name: 'test.jpg',
      type: 'image/jpeg',
      size: 1024 * 1024,
      lastModified: Date.now()
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
    wrapper = mount(DocumentUploader)
  })

  it('renders upload zone with correct text', () => {
    expect(wrapper.find('.upload-zone').exists()).toBe(true)
    expect(wrapper.text()).toContain('Drop documents here or click to upload')
    expect(wrapper.text()).toContain('Supported formats: JPEG, PNG, TIFF (max 10MB)')
  })

  it('handles file selection', async () => {
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    vi.mocked(imageProcessor.processImage).mockResolvedValueOnce(mockProcessedImage)
    
    await input.trigger('change', {
      target: {
        files: [file]
      }
    })

    expect(imageProcessor.processImage).toHaveBeenCalledWith(file, {
      maxWidth: 2048,
      maxHeight: 2048,
      quality: 0.8,
      format: 'jpeg',
      preserveMetadata: true
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('upload')?.[0][0]).toEqual([mockProcessedImage])
  })

  it('handles drag and drop', async () => {
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
    vi.mocked(imageProcessor.processImage).mockResolvedValueOnce(mockProcessedImage)

    await wrapper.find('.upload-zone').trigger('dragenter')
    expect(wrapper.find('.upload-zone').classes()).toContain('is-dragging')

    await wrapper.find('.upload-zone').trigger('drop', {
      dataTransfer: {
        files: [file]
      }
    })

    expect(imageProcessor.processImage).toHaveBeenCalledWith(file, expect.any(Object))
    expect(wrapper.emitted('upload')?.[0][0]).toEqual([mockProcessedImage])
  })

  it('displays processing state', async () => {
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
    vi.mocked(imageProcessor.processImage).mockImplementationOnce(() => {
      return new Promise(resolve => setTimeout(() => resolve(mockProcessedImage), 100))
    })

    await wrapper.find('input[type="file"]').trigger('change', {
      target: { files: [file] }
    })

    expect(wrapper.find('.processing-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Processing document...')
  })

  it('handles processing errors', async () => {
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
    const errorMessage = 'Failed to process image'
    
    vi.mocked(imageProcessor.processImage).mockResolvedValueOnce(null)
    vi.mocked(imageProcessor.getError).mockReturnValueOnce(errorMessage)

    await wrapper.find('input[type="file"]').trigger('change', {
      target: { files: [file] }
    })

    expect(wrapper.find('.error-content').exists()).toBe(true)
    expect(wrapper.text()).toContain(errorMessage)
  })

  it('allows removing processed documents', async () => {
    vi.mocked(imageProcessor.processImage).mockResolvedValueOnce(mockProcessedImage)
    
    await wrapper.find('input[type="file"]').trigger('change', {
      target: { files: [new File([''], 'test.jpg', { type: 'image/jpeg' })] }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('.document-preview')).toHaveLength(1)

    await wrapper.find('.delete-button').trigger('click')
    expect(wrapper.findAll('.document-preview')).toHaveLength(0)
  })

  it('formats file sizes correctly', () => {
    const wrapper = mount(DocumentUploader)
    
    // @ts-ignore - accessing private method for testing
    expect(wrapper.vm.formatSize(500)).toBe('500 B')
    expect(wrapper.vm.formatSize(1500)).toBe('1.5 KB')
    expect(wrapper.vm.formatSize(1500000)).toBe('1.4 MB')
  })
}) 