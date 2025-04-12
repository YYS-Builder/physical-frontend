const documentProcessingService = require('../services/documentProcessing');
const { Document } = require('../models');
const { validationResult } = require('express-validator');

class DocumentProcessingController {
  async uploadDocument(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      const filePath = req.file.path;
      const processingResult = await documentProcessingService.processDocument(filePath);

      // Create document record in database
      const document = await Document.create({
        title: req.file.originalname,
        fileType: req.file.mimetype,
        filePath: filePath,
        processedData: processingResult.data,
        metadata: processingResult.metadata,
        userId: req.user.id
      });

      // Clean up the uploaded file after processing
      await documentProcessingService.cleanup(filePath);

      res.status(201).json({
        success: true,
        document: {
          id: document.id,
          title: document.title,
          fileType: document.fileType,
          metadata: document.metadata,
          processedAt: document.createdAt
        }
      });
    } catch (error) {
      console.error('Error uploading document:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to process document'
      });
    }
  }

  async getProcessingStatus(req, res) {
    try {
      const { documentId } = req.params;
      const document = await Document.findByPk(documentId);

      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }

      res.json({
        status: document.status,
        progress: document.progress,
        processedData: document.processedData,
        metadata: document.metadata
      });
    } catch (error) {
      console.error('Error getting processing status:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get processing status'
      });
    }
  }

  async getProcessedContent(req, res) {
    try {
      const { documentId } = req.params;
      const document = await Document.findByPk(documentId);

      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }

      if (document.status !== 'completed') {
        return res.status(400).json({ error: 'Document processing not completed' });
      }

      res.json({
        content: document.processedData.text,
        metadata: document.metadata
      });
    } catch (error) {
      console.error('Error getting processed content:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get processed content'
      });
    }
  }

  async deleteDocument(req, res) {
    try {
      const { documentId } = req.params;
      const document = await Document.findByPk(documentId);

      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }

      // Delete the processed file if it exists
      if (document.filePath) {
        await documentProcessingService.cleanup(document.filePath);
      }

      // Delete the document record
      await document.destroy();

      res.json({
        success: true,
        message: 'Document deleted successfully'
      });
    } catch (error) {
      console.error('Error deleting document:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to delete document'
      });
    }
  }
}

module.exports = new DocumentProcessingController(); 