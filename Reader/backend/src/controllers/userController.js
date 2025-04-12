const userService = require('../services/userService');
const { validationResult } = require('express-validator');

class UserController {
  async register(req, res) {
    try {
      const result = await userService.register(req.body);
      res.status(201).json(result);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  }

  async login(req, res) {
    try {
      const { email, password } = req.body;
      const result = await userService.login(email, password);
      res.json(result);
    } catch (error) {
      res.status(401).json({ message: error.message });
    }
  }

  async getProfile(req, res) {
    try {
      const user = await userService.getProfile(req.user.id);
      res.json(user);
    } catch (error) {
      res.status(404).json({ message: error.message });
    }
  }

  async updateProfile(req, res) {
    try {
      const user = await userService.updateProfile(req.user.id, req.body);
      res.json(user);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  }

  async changePassword(req, res) {
    try {
      const { currentPassword, newPassword } = req.body;
      const result = await userService.changePassword(
        req.user.id,
        currentPassword,
        newPassword
      );
      res.json(result);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  }

  async getPreferences(req, res) {
    try {
      const preferences = await userService.getPreferences(req.user.id);
      res.json(preferences);
    } catch (error) {
      res.status(404).json({ message: error.message });
    }
  }

  async updatePreferences(req, res) {
    try {
      const preferences = await userService.updatePreferences(
        req.user.id,
        req.body
      );
      res.json(preferences);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  }

  async deleteAccount(req, res) {
    try {
      const { password } = req.body;
      const result = await userService.deleteAccount(req.user.id, password);
      res.json(result);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  }
}

module.exports = new UserController(); 