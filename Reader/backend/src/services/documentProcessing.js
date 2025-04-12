const fs = require('fs').promises;
const path = require('path');
const multer = require('multer');
const pdf = require('pdf-parse');
const mammoth = require('mammoth');
const Tesseract = require('tesseract.js');
const epub = require('epub');
const { promisify } = require('util');
const { pipeline } = require('stream');
const pipelineAsync = promisify(pipeline);

class DocumentProcessingService {
  constructor() {
    this.uploadDir = path.join(process.cwd(), 'uploads');
    this.processedDir = path.join(process.cwd(), 'processed');
    this.initializeDirectories();
  }

  async initializeDirectories() {
    try {
      await fs.mkdir(this.uploadDir, { recursive: true });
      await fs.mkdir(this.processedDir, { recursive: true });
    } catch (error) {
      console.error('Error initializing directories:', error);
      throw error;
    }
  }

  configureMulter() {
    const storage = multer.diskStorage({
      destination: (req, file, cb) => {
        cb(null, this.uploadDir);
      },
      filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniqueSuffix + path.extname(file.originalname));
      }
    });

    const fileFilter = (req, file, cb) => {
      const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
        'text/plain'
      ];

      if (allowedTypes.includes(file.mimetype)) {
        cb(null, true);
      } else {
        cb(new Error('Invalid file type. Only PDF, DOC, DOCX, JPEG, PNG, and TXT files are allowed.'));
      }
    };

    return multer({
      storage,
      fileFilter,
      limits: {
        fileSize: 10 * 1024 * 1024 // 10MB limit
      }
    });
  }

  async processDocument(filePath, options = {}) {
    const fileExtension = path.extname(filePath).toLowerCase();
    let result;

    try {
      switch (fileExtension) {
        case '.pdf':
          result = await this.processPDF(filePath, options);
          break;
        case '.epub':
          result = await this.processEPUB(filePath, options);
          break;
        case '.doc':
        case '.docx':
          result = await this.processWord(filePath, options);
          break;
        case '.jpg':
        case '.jpeg':
        case '.png':
          result = await this.processImage(filePath, options);
          break;
        case '.txt':
          result = await this.processText(filePath, options);
          break;
        default:
          throw new Error(`Unsupported file type: ${fileExtension}`);
      }

      return {
        success: true,
        data: result,
        metadata: {
          fileType: fileExtension,
          processedAt: new Date(),
          size: (await fs.stat(filePath)).size
        }
      };
    } catch (error) {
      console.error('Error processing document:', error);
      throw error;
    }
  }

  async processPDF(filePath, options) {
    try {
      const dataBuffer = await fs.readFile(filePath);
      const data = await pdf(dataBuffer);
      
      return {
        text: data.text,
        numPages: data.numpages,
        info: data.info,
        metadata: data.metadata
      };
    } catch (error) {
      console.error('Error processing PDF:', error);
      throw error;
    }
  }

  async processEPUB(filePath, options) {
    try {
      const epubBook = new epub(filePath);
      const metadata = await new Promise((resolve, reject) => {
        epubBook.on('end', () => {
          resolve(epubBook.metadata);
        });
        epubBook.on('error', reject);
        epubBook.parse();
      });

      // Extract text content
      const chapters = await new Promise((resolve, reject) => {
        const chapters = [];
        epubBook.on('end', () => {
          resolve(chapters);
        });
        epubBook.on('error', reject);
        
        epubBook.on('data', (chapter) => {
          chapters.push({
            title: chapter.title,
            content: chapter.body
          });
        });
      });

      // Calculate reading statistics
      const totalChapters = chapters.length;
      const totalWords = chapters.reduce((sum, chapter) => {
        return sum + chapter.content.split(/\s+/).length;
      }, 0);

      return {
        metadata: {
          title: metadata.title,
          author: metadata.creator,
          language: metadata.language,
          publisher: metadata.publisher,
          published: metadata.pubdate,
          description: metadata.description
        },
        content: chapters,
        statistics: {
          totalChapters,
          totalWords,
          estimatedReadingTime: Math.ceil(totalWords / 200) // Assuming 200 words per minute
        }
      };
    } catch (error) {
      console.error('Error processing EPUB:', error);
      throw error;
    }
  }

  async processWord(filePath, options) {
    try {
      const result = await mammoth.extractRawText({ path: filePath });
      return {
        text: result.value,
        messages: result.messages
      };
    } catch (error) {
      console.error('Error processing Word document:', error);
      throw error;
    }
  }

  async processImage(filePath, options) {
    try {
      const result = await Tesseract.recognize(
        filePath,
        'eng',
        {
          logger: m => console.log(m)
        }
      );

      return {
        text: result.data.text,
        confidence: result.data.confidence,
        hocr: result.data.hocr
      };
    } catch (error) {
      console.error('Error processing image:', error);
      throw error;
    }
  }

  async processText(filePath, options) {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return {
        text: content
      };
    } catch (error) {
      console.error('Error processing text file:', error);
      throw error;
    }
  }

  async cleanup(filePath) {
    try {
      await fs.unlink(filePath);
    } catch (error) {
      console.error('Error cleaning up file:', error);
      throw error;
    }
  }

  async saveProcessedDocument(content, filename) {
    try {
      const filePath = path.join(this.processedDir, filename);
      await fs.writeFile(filePath, content);
      return filePath;
    } catch (error) {
      console.error('Error saving processed document:', error);
      throw error;
    }
  }
}

module.exports = new DocumentProcessingService(); 