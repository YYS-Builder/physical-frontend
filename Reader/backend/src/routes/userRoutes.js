const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const authMiddleware = require('../middleware/authMiddleware');
const { body } = require('express-validator');

// Validation middleware
const registerValidation = [
  body('email').isEmail().withMessage('Please provide a valid email'),
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long'),
  body('name').notEmpty().withMessage('Name is required'),
  body('username')
    .isLength({ min: 3 })
    .withMessage('Username must be at least 3 characters long')
];

const loginValidation = [
  body('email').isEmail().withMessage('Please provide a valid email'),
  body('password').notEmpty().withMessage('Password is required')
];

const updateProfileValidation = [
  body('name').optional().notEmpty().withMessage('Name cannot be empty'),
  body('username')
    .optional()
    .isLength({ min: 3 })
    .withMessage('Username must be at least 3 characters long'),
  body('bio').optional(),
  body('avatar').optional().isURL().withMessage('Avatar must be a valid URL')
];

const changePasswordValidation = [
  body('currentPassword').notEmpty().withMessage('Current password is required'),
  body('newPassword')
    .isLength({ min: 6 })
    .withMessage('New password must be at least 6 characters long')
];

const deleteAccountValidation = [
  body('password').notEmpty().withMessage('Password is required')
];

// Public routes
router.post('/register', registerValidation, userController.register);
router.post('/login', loginValidation, userController.login);

// Protected routes
router.get('/profile', authMiddleware, userController.getProfile);
router.put(
  '/profile',
  authMiddleware,
  updateProfileValidation,
  userController.updateProfile
);
router.put(
  '/password',
  authMiddleware,
  changePasswordValidation,
  userController.changePassword
);
router.get('/preferences', authMiddleware, userController.getPreferences);
router.put('/preferences', authMiddleware, userController.updatePreferences);
router.delete(
  '/account',
  authMiddleware,
  deleteAccountValidation,
  userController.deleteAccount
);

module.exports = router; 