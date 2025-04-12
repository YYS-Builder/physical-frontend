const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { validationResult } = require('express-validator');

class UserService {
  async register(userData) {
    try {
      // Check if user already exists
      const existingUser = await User.findOne({ email: userData.email });
      if (existingUser) {
        throw new Error('Email already registered');
      }

      // Hash password
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(userData.password, salt);

      // Create new user
      const user = new User({
        ...userData,
        password: hashedPassword
      });

      await user.save();

      // Generate JWT token
      const token = this.generateToken(user);

      return {
        user: {
          id: user._id,
          name: user.name,
          email: user.email,
          username: user.username,
          avatar: user.avatar,
          bio: user.bio
        },
        token
      };
    } catch (error) {
      throw error;
    }
  }

  async login(email, password) {
    try {
      // Find user
      const user = await User.findOne({ email });
      if (!user) {
        throw new Error('Invalid credentials');
      }

      // Check password
      const isMatch = await bcrypt.compare(password, user.password);
      if (!isMatch) {
        throw new Error('Invalid credentials');
      }

      // Generate JWT token
      const token = this.generateToken(user);

      return {
        user: {
          id: user._id,
          name: user.name,
          email: user.email,
          username: user.username,
          avatar: user.avatar,
          bio: user.bio
        },
        token
      };
    } catch (error) {
      throw error;
    }
  }

  async getProfile(userId) {
    try {
      const user = await User.findById(userId).select('-password');
      if (!user) {
        throw new Error('User not found');
      }
      return user;
    } catch (error) {
      throw error;
    }
  }

  async updateProfile(userId, updateData) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      // Update user data
      Object.keys(updateData).forEach(key => {
        if (updateData[key] !== undefined) {
          user[key] = updateData[key];
        }
      });

      await user.save();
      return user;
    } catch (error) {
      throw error;
    }
  }

  async changePassword(userId, currentPassword, newPassword) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      // Check current password
      const isMatch = await bcrypt.compare(currentPassword, user.password);
      if (!isMatch) {
        throw new Error('Current password is incorrect');
      }

      // Hash new password
      const salt = await bcrypt.genSalt(10);
      user.password = await bcrypt.hash(newPassword, salt);

      await user.save();
      return { message: 'Password updated successfully' };
    } catch (error) {
      throw error;
    }
  }

  async getPreferences(userId) {
    try {
      const user = await User.findById(userId).select('preferences');
      if (!user) {
        throw new Error('User not found');
      }
      return user.preferences;
    } catch (error) {
      throw error;
    }
  }

  async updatePreferences(userId, preferences) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      user.preferences = {
        ...user.preferences,
        ...preferences
      };

      await user.save();
      return user.preferences;
    } catch (error) {
      throw error;
    }
  }

  async deleteAccount(userId, password) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      // Verify password
      const isMatch = await bcrypt.compare(password, user.password);
      if (!isMatch) {
        throw new Error('Password is incorrect');
      }

      await User.findByIdAndDelete(userId);
      return { message: 'Account deleted successfully' };
    } catch (error) {
      throw error;
    }
  }

  generateToken(user) {
    return jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );
  }
}

module.exports = new UserService(); 