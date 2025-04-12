import { ref, type Ref } from 'vue'

interface ImageDimensions {
  width: number
  height: number
}

interface ProcessingOptions {
  maxWidth?: number
  maxHeight?: number
  quality?: number
}

export interface ImageProcessingOptions extends ProcessingOptions {
  format?: 'jpeg' | 'png' | 'webp'
  preserveMetadata?: boolean
}

export interface ProcessedImage {
  url: string
  width: number
  height: number
  size: number
  format: string
  metadata?: Record<string, unknown>
}

export class ImageProcessor {
  private processing: Ref<boolean> = ref(false)
  private error: Ref<string | null> = ref(null)
  private readonly MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
  private readonly MIN_DIMENSIONS = { width: 50, height: 50 }

  /**
   * Validates an image file
   * @param file - The image file to validate
   * @returns Promise<boolean> - Whether the file is valid
   */
  async validateImage(file: File): Promise<boolean> {
    this.error.value = null

    // Check file type
    if (!file.type.startsWith('image/')) {
      this.error.value = 'Invalid file type. Please upload an image.'
      return false
    }

    // Check file size
    if (file.size > this.MAX_FILE_SIZE) {
      this.error.value = 'Image size exceeds 10MB limit.'
      return false
    }

    // Check image dimensions
    const dimensions = await this.getImageDimensions(file)
    if (dimensions.width < this.MIN_DIMENSIONS.width || 
        dimensions.height < this.MIN_DIMENSIONS.height) {
      this.error.value = 'Image dimensions too small. Minimum 50x50 pixels required.'
      return false
    }

    return true
  }

  /**
   * Gets the dimensions of an image file
   * @param file - The image file
   * @returns Promise<ImageDimensions> - The image dimensions
   */
  private getImageDimensions(file: File): Promise<ImageDimensions> {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        resolve({
          width: img.width,
          height: img.height
        })
      }
      img.onerror = () => {
        this.error.value = 'Failed to load image. Please try another file.'
        reject(new Error('Failed to load image'))
      }
      img.src = URL.createObjectURL(file)
    })
  }

  /**
   * Processes an image file
   * @param file - The image file to process
   * @param options - Processing options
   * @returns Promise<Blob> - The processed image
   */
  async processImage(file: File, options: ProcessingOptions = {}): Promise<Blob> {
    this.error.value = null

    try {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      
      if (!ctx) {
        throw new Error('Failed to get canvas context')
      }

      const img = await this.loadImage(file)
      const dimensions = this.calculateDimensions(img, options)

      canvas.width = dimensions.width
      canvas.height = dimensions.height
      ctx.drawImage(img, 0, 0, dimensions.width, dimensions.height)

      return new Promise((resolve, reject) => {
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob)
            } else {
              reject(new Error('Failed to create image blob'))
            }
          },
          file.type,
          options.quality
        )
      })
    } catch (err) {
      this.error.value = err instanceof Error ? err.message : 'Failed to process image'
      throw err
    }
  }

  /**
   * Loads an image file
   * @param file - The image file
   * @returns Promise<HTMLImageElement> - The loaded image
   */
  private loadImage(file: File): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('Failed to load image'))
      img.src = URL.createObjectURL(file)
    })
  }

  /**
   * Calculates the dimensions for the processed image
   * @param img - The source image
   * @param options - Processing options
   * @returns ImageDimensions - The calculated dimensions
   */
  private calculateDimensions(img: HTMLImageElement, options: ProcessingOptions): ImageDimensions {
    let { width, height } = img

    if (options.maxWidth && width > options.maxWidth) {
      height = (height * options.maxWidth) / width
      width = options.maxWidth
    }

    if (options.maxHeight && height > options.maxHeight) {
      width = (width * options.maxHeight) / height
      height = options.maxHeight
    }

    return { width, height }
  }

  /**
   * Processes an image with the specified options
   * @param file - The image file to process
   * @param options - Processing options
   * @returns Promise<ProcessedImage | null> - The processed image or null if processing fails
   */
  async processImageWithOptions(file: File, options: ImageProcessingOptions = {}): Promise<ProcessedImage | null> {
    try {
      this.processing.value = true
      this.error.value = null

      const isValid = await this.validateImage(file)
      if (!isValid) return null

      const blob = await this.processImage(file, options)
      const url = URL.createObjectURL(blob)
      
      // Create a temporary image to get dimensions
      const tempImg = await this.loadImage(new File([blob], 'temp', { type: blob.type }))

      return {
        url,
        width: tempImg.width,
        height: tempImg.height,
        size: blob.size,
        format: options.format || file.type.split('/')[1],
        metadata: options.preserveMetadata ? await this.extractMetadata(file) : undefined
      }
    } catch (err) {
      this.error.value = err instanceof Error ? err.message : 'Failed to process image'
      return null
    } finally {
      this.processing.value = false
    }
  }

  /**
   * Extracts metadata from an image file
   * @param file - The image file
   * @returns Promise<Record<string, unknown>> - The extracted metadata
   */
  private async extractMetadata(file: File): Promise<Record<string, unknown>> {
    const metadata: Record<string, unknown> = {
      name: file.name,
      type: file.type,
      size: file.size,
      lastModified: file.lastModified
    }

    try {
      const exif = await this.readExifData(file)
      if (exif) {
        metadata.exif = exif
      }
    } catch (err) {
      console.warn('Failed to extract EXIF data:', err)
    }

    return metadata
  }

  /**
   * Reads EXIF data from an image file
   * @param file - The image file
   * @returns Promise<Record<string, unknown> | null> - The EXIF data or null if not available
   */
  private async readExifData(file: File): Promise<Record<string, unknown> | null> {
    if (!file.type.startsWith('image/jpeg')) {
      return null
    }

    try {
      const arrayBuffer = await file.arrayBuffer()
      const view = new DataView(arrayBuffer)
      
      // Check for EXIF header
      if (view.getUint16(0) !== 0xFFD8) {
        return null
      }

      // TODO: Implement EXIF parsing
      return null
    } catch (err) {
      console.warn('Failed to read EXIF data:', err)
      return null
    }
  }

  /**
   * Returns the current processing state
   * @returns boolean - Whether the processor is currently processing an image
   */
  isProcessing(): boolean {
    return this.processing.value
  }

  /**
   * Returns the current error message, if any
   * @returns string | null - The error message or null if no error
   */
  getError(): string | null {
    return this.error.value
  }
}

export const imageProcessor = new ImageProcessor() 