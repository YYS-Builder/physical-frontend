const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const authMiddleware = require('../middleware/auth');
const { body } = require('express-validator');

// Validation middleware
const validateRegistration = [
  body('email').isEmail().withMessage('Please provide a valid email'),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long'),
  body('username')
    .isLength({ min: 3 })
    .withMessage('Username must be at least 3 characters long'),
  body('name').notEmpty().withMessage('Name is required')
];

const validateLogin = [
  body('email').isEmail().withMessage('Please provide a valid email'),
  body('password').notEmpty().withMessage('Password is required')
];

const validateProfileUpdate = [
  body('email').optional().isEmail().withMessage('Please provide a valid email'),
  body('username')
    .optional()
    .isLength({ min: 3 })
    .withMessage('Username must be at least 3 characters long'),
  body('name').optional().notEmpty().withMessage('Name cannot be empty'),
  body('bio').optional().isLength({ max: 500 }).withMessage('Bio must be less than 500 characters'),
  body('avatar').optional().isURL().withMessage('Avatar must be a valid URL')
];

const validatePasswordChange = [
  body('currentPassword').notEmpty().withMessage('Current password is required'),
  body('newPassword')
    .isLength({ min: 8 })
    .withMessage('New password must be at least 8 characters long')
];

const validatePreferences = [
  body('theme').optional().isIn(['light', 'dark']).withMessage('Invalid theme'),
  body('language').optional().isIn(['en', 'es', 'fr']).withMessage('Invalid language'),
  body('notifications').optional().isBoolean().withMessage('Notifications must be a boolean'),
  body('fontSize').optional().isInt({ min: 12, max: 24 }).withMessage('Invalid font size')
];

const validateAccountDeletion = [
  body('password').notEmpty().withMessage('Password is required')
];

// Public routes
router.post('/register', validateRegistration, userController.register);
router.post('/login', validateLogin, userController.login);

// Protected routes
router.get('/profile', authMiddleware, userController.getProfile);
router.put('/profile', authMiddleware, validateProfileUpdate, userController.updateProfile);
router.put('/password', authMiddleware, validatePasswordChange, userController.changePassword);
router.get('/preferences', authMiddleware, userController.getPreferences);
router.put('/preferences', authMiddleware, validatePreferences, userController.updatePreferences);
router.delete('/account', authMiddleware, validateAccountDeletion, userController.deleteAccount);

module.exports = router; 