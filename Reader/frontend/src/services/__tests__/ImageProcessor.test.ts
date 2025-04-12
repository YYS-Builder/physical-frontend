import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ImageProcessor, type ImageProcessingOptions } from '../ImageProcessor'

describe('ImageProcessor', () => {
  let imageProcessor: ImageProcessor
  let mockFile: File
  let mockImage: HTMLImageElement

  beforeEach(() => {
    imageProcessor = new ImageProcessor()

    // Mock File
    mockFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    Object.defineProperty(mockFile, 'size', { value: 1024 * 1024 }) // 1MB

    // Mock Image
    mockImage = new Image()
    Object.defineProperty(mockImage, 'width', { value: 1000 })
    Object.defineProperty(mockImage, 'height', { value: 800 })

    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'mock-url')

    // Mock canvas and context
    const mockContext = {
      drawImage: vi.fn(),
    }
    const mockCanvas = {
      getContext: vi.fn(() => mockContext),
      toDataURL: vi.fn(() => 'data:image/jpeg;base64,mockdata'),
    }
    global.document.createElement = vi.fn((tag) => {
      if (tag === 'canvas') return mockCanvas as unknown as HTMLCanvasElement
      return document.createElement(tag)
    })
  })

  it('should validate image file type', async () => {
    const invalidFile = new File([''], 'test.txt', { type: 'text/plain' })
    const result = await imageProcessor.processImage(invalidFile)
    expect(result).toBeNull()
    expect(imageProcessor.getError()).toBe('Invalid file type. Please upload an image.')
  })

  it('should validate image file size', async () => {
    const largeFile = new File([''], 'large.jpg', { type: 'image/jpeg' })
    Object.defineProperty(largeFile, 'size', { value: 20 * 1024 * 1024 }) // 20MB
    const result = await imageProcessor.processImage(largeFile)
    expect(result).toBeNull()
    expect(imageProcessor.getError()).toBe('Image size exceeds 10MB limit.')
  })

  it('should process image with default options', async () => {
    const result = await imageProcessor.processImage(mockFile)
    expect(result).not.toBeNull()
    if (result) {
      expect(result.format).toBe('jpeg')
      expect(result.width).toBeLessThanOrEqual(2048)
      expect(result.height).toBeLessThanOrEqual(2048)
      expect(result.metadata).toBeDefined()
    }
  })

  it('should process image with custom options', async () => {
    const options: ImageProcessingOptions = {
      maxWidth: 800,
      maxHeight: 600,
      quality: 0.9,
      format: 'png',
      preserveMetadata: false
    }
    const result = await imageProcessor.processImage(mockFile, options)
    expect(result).not.toBeNull()
    if (result) {
      expect(result.format).toBe('png')
      expect(result.width).toBeLessThanOrEqual(800)
      expect(result.height).toBeLessThanOrEqual(600)
      expect(result.metadata).toBeUndefined()
    }
  })

  it('should handle processing errors gracefully', async () => {
    // Mock canvas context to throw error
    global.document.createElement = vi.fn(() => {
      throw new Error('Canvas creation failed')
    })
    const result = await imageProcessor.processImage(mockFile)
    expect(result).toBeNull()
    expect(imageProcessor.getError()).toBe('Canvas creation failed')
  })

  it('should update processing state correctly', async () => {
    expect(imageProcessor.isProcessing()).toBe(false)
    const processPromise = imageProcessor.processImage(mockFile)
    expect(imageProcessor.isProcessing()).toBe(true)
    await processPromise
    expect(imageProcessor.isProcessing()).toBe(false)
  })

  it('should extract basic metadata', async () => {
    const result = await imageProcessor.processImage(mockFile)
    expect(result?.metadata).toEqual({
      name: 'test.jpg',
      type: 'image/jpeg',
      size: 1024 * 1024,
      lastModified: expect.any(Number)
    })
  })
}) 