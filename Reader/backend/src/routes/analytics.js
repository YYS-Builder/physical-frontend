const express = require('express');
const router = express.Router();
const analyticsController = require('../controllers/analyticsController');
const { authenticate } = require('../middleware/auth');
const { query, param } = require('express-validator');

// Validation middleware
const validateDateRange = [
  query('startDate').optional().isISO8601().toDate(),
  query('endDate').optional().isISO8601().toDate()
];

const validateDocumentId = [
  param('documentId').isUUID()
];

const validateExport = [
  query('format').isIn(['csv', 'json']),
  ...validateDateRange
];

// Apply authentication middleware to all routes
router.use(authenticate);

// Get analytics data
router.get('/', analyticsController.getAnalytics);

// Get document-specific analytics
router.get('/documents/:documentId', analyticsController.getDocumentAnalytics);

// Get reading patterns
router.get('/patterns', analyticsController.getReadingPatterns);

// Get reading speed data
router.get('/speed', analyticsController.getReadingSpeed);

// Export analytics data
router.get('/export', analyticsController.exportData);

module.exports = router; 