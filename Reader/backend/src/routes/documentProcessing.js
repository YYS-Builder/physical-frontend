const express = require('express');
const router = express.Router();
const documentProcessingController = require('../controllers/documentProcessingController');
const documentProcessingService = require('../services/documentProcessing');
const { authenticate } = require('../middleware/auth');
const { body } = require('express-validator');

// Configure multer for file uploads
const upload = documentProcessingService.configureMulter();

// Validation middleware
const validateDocumentUpload = [
  body('title').optional().isString().trim(),
  body('collectionId').optional().isUUID()
];

// Document upload and processing
router.post(
  '/upload',
  authenticate,
  upload.single('document'),
  validateDocumentUpload,
  documentProcessingController.uploadDocument
);

// Get processing status
router.get(
  '/status/:documentId',
  authenticate,
  documentProcessingController.getProcessingStatus
);

// Get processed content
router.get(
  '/content/:documentId',
  authenticate,
  documentProcessingController.getProcessedContent
);

// Delete document
router.delete(
  '/:documentId',
  authenticate,
  documentProcessingController.deleteDocument
);

module.exports = router; 