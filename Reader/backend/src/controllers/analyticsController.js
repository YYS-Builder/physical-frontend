const analyticsService = require('../services/analyticsService');
const { validationResult } = require('express-validator');
const { Document } = require('../models/Document');
const { ReadingSession } = require('../models/ReadingSession');
const { AIModel } = require('../../ai/model');
const logger = require('../utils/logger');

class AnalyticsController {
  constructor() {
    this.aiModel = new AIModel();
  }

  async getAnalytics(req, res) {
    try {
      const { dateRange, startDate, endDate } = req.query;
      const userId = req.user.id;

      // Get date range
      const dateFilter = this._getDateFilter(dateRange, startDate, endDate);

      // Get document statistics
      const documentStats = await this._getDocumentStats(userId, dateFilter);
      
      // Get reading statistics
      const readingStats = await this._getReadingStats(userId, dateFilter);
      
      // Get reading patterns
      const patterns = await this._getReadingPatterns(userId, dateFilter);

      // Get chart data
      const chartData = await this._getChartData(userId, dateFilter);

      res.json({
        ...documentStats,
        ...readingStats,
        patterns,
        ...chartData
      });
    } catch (error) {
      logger.error('Error getting analytics:', error);
      res.status(500).json({ error: 'Failed to get analytics data' });
    }
  }

  async getDocumentAnalytics(req, res) {
    try {
      const { documentId } = req.params;
      const userId = req.user.id;

      const document = await Document.findOne({
        _id: documentId,
        userId
      });

      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }

      const sessions = await ReadingSession.find({
        documentId,
        userId
      }).sort({ createdAt: -1 });

      const analytics = await this.aiModel.process_document(document.processedData);
      const patterns = await this.aiModel.analyze_reading_patterns({
        documentId,
        sessions
      });

      res.json({
        document: {
          title: document.title,
          type: document.fileType,
          createdAt: document.createdAt,
          lastRead: sessions[0]?.createdAt
        },
        analytics,
        patterns
      });
    } catch (error) {
      logger.error('Error getting document analytics:', error);
      res.status(500).json({ error: 'Failed to get document analytics' });
    }
  }

  async getReadingPatterns(req, res) {
    try {
      const { dateRange, startDate, endDate } = req.query;
      const userId = req.user.id;

      const dateFilter = this._getDateFilter(dateRange, startDate, endDate);
      const patterns = await this._getReadingPatterns(userId, dateFilter);

      res.json(patterns);
    } catch (error) {
      logger.error('Error getting reading patterns:', error);
      res.status(500).json({ error: 'Failed to get reading patterns' });
    }
  }

  async getReadingSpeed(req, res) {
    try {
      const { dateRange, startDate, endDate } = req.query;
      const userId = req.user.id;

      const dateFilter = this._getDateFilter(dateRange, startDate, endDate);
      const sessions = await ReadingSession.find({
        userId,
        ...dateFilter
      }).sort({ createdAt: -1 });

      const speedData = this._calculateReadingSpeed(sessions);

      res.json(speedData);
    } catch (error) {
      logger.error('Error getting reading speed:', error);
      res.status(500).json({ error: 'Failed to get reading speed data' });
    }
  }

  async exportData(req, res) {
    try {
      const { dateRange, startDate, endDate } = req.query;
      const userId = req.user.id;

      const dateFilter = this._getDateFilter(dateRange, startDate, endDate);

      const [documents, sessions] = await Promise.all([
        Document.find({ userId, ...dateFilter }),
        ReadingSession.find({ userId, ...dateFilter })
      ]);

      const csvData = this._generateCSV(documents, sessions);

      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', 'attachment; filename=analytics.csv');
      res.send(csvData);
    } catch (error) {
      logger.error('Error exporting analytics data:', error);
      res.status(500).json({ error: 'Failed to export analytics data' });
    }
  }

  _getDateFilter(dateRange, startDate, endDate) {
    const now = new Date();
    let start = new Date();
    let end = now;

    if (dateRange === 'custom' && startDate && endDate) {
      start = new Date(startDate);
      end = new Date(endDate);
    } else {
      switch (dateRange) {
        case '7':
          start.setDate(now.getDate() - 7);
          break;
        case '30':
          start.setDate(now.getDate() - 30);
          break;
        case '90':
          start.setDate(now.getDate() - 90);
          break;
        default:
          start.setDate(now.getDate() - 30);
      }
    }

    return {
      createdAt: {
        $gte: start,
        $lte: end
      }
    };
  }

  _calculateReadingSpeed(sessions) {
    const dailySpeed = {};
    sessions.forEach(session => {
      const date = session.createdAt.toISOString().split('T')[0];
      if (!dailySpeed[date]) {
        dailySpeed[date] = {
          totalPages: 0,
          totalTime: 0,
          sessions: 0
        };
      }
      dailySpeed[date].totalPages += session.pagesRead || 0;
      dailySpeed[date].totalTime += (session.endTime - session.startTime) / 1000; // Convert to seconds
      dailySpeed[date].sessions++;
    });

    return Object.entries(dailySpeed).map(([date, data]) => ({
      date,
      averageSpeed: data.totalTime > 0 ? (data.totalPages / data.totalTime) * 60 : 0, // Pages per minute
      sessions: data.sessions
    }));
  }

  async _getDocumentStats(userId, dateFilter) {
    const documents = await Document.find({ userId, ...dateFilter });
    const previousPeriod = await Document.find({
      userId,
      createdAt: {
        $lt: dateFilter.createdAt.$gte
      }
    });

    const totalDocuments = documents.length;
    const previousTotal = previousPeriod.length;
    const documentsChange = previousTotal > 0 
      ? ((totalDocuments - previousTotal) / previousTotal) * 100 
      : 0;

    return {
      totalDocuments,
      documentsChange
    };
  }

  async _getReadingStats(userId, dateFilter) {
    const sessions = await ReadingSession.find({ userId, ...dateFilter });
    const previousPeriod = await ReadingSession.find({
      userId,
      createdAt: {
        $lt: dateFilter.createdAt.$gte
      }
    });

    const totalReadingTime = sessions.reduce((sum, session) => sum + session.duration, 0);
    const previousReadingTime = previousPeriod.reduce((sum, session) => sum + session.duration, 0);
    const readingTimeChange = previousReadingTime > 0
      ? ((totalReadingTime - previousReadingTime) / previousReadingTime) * 100
      : 0;

    const averageReadingSpeed = sessions.length > 0
      ? sessions.reduce((sum, session) => sum + session.readingSpeed, 0) / sessions.length
      : 0;
    const previousSpeed = previousPeriod.length > 0
      ? previousPeriod.reduce((sum, session) => sum + session.readingSpeed, 0) / previousPeriod.length
      : 0;
    const speedChange = previousSpeed > 0
      ? ((averageReadingSpeed - previousSpeed) / previousSpeed) * 100
      : 0;

    const completionRate = sessions.length > 0
      ? (sessions.filter(s => s.completed).length / sessions.length) * 100
      : 0;
    const previousCompletion = previousPeriod.length > 0
      ? (previousPeriod.filter(s => s.completed).length / previousPeriod.length) * 100
      : 0;
    const completionChange = previousCompletion > 0
      ? ((completionRate - previousCompletion) / previousCompletion) * 100
      : 0;

    return {
      totalReadingTime,
      readingTimeChange,
      averageReadingSpeed,
      speedChange,
      completionRate,
      completionChange
    };
  }

  async _getReadingPatterns(userId, dateFilter) {
    const sessions = await ReadingSession.find({ userId, ...dateFilter });
    return await this.aiModel.analyze_reading_patterns(sessions);
  }

  async _getChartData(userId, dateFilter) {
    const sessions = await ReadingSession.find({ userId, ...dateFilter })
      .sort({ createdAt: 1 });

    const activityData = this._generateActivityData(sessions);
    const typesData = this._generateTypesData(sessions);
    const speedData = this._generateSpeedData(sessions);
    const completionData = this._generateCompletionData(sessions);

    return {
      activityData,
      typesData,
      speedData,
      completionData
    };
  }

  _generateActivityData(sessions) {
    const labels = [];
    const values = [];
    const dailyTotals = {};

    sessions.forEach(session => {
      const date = session.createdAt.toISOString().split('T')[0];
      dailyTotals[date] = (dailyTotals[date] || 0) + session.duration;
    });

    Object.entries(dailyTotals).forEach(([date, total]) => {
      labels.push(date);
      values.push(total);
    });

    return { labels, values };
  }

  _generateTypesData(sessions) {
    const typeCounts = {};
    sessions.forEach(session => {
      typeCounts[session.documentType] = (typeCounts[session.documentType] || 0) + 1;
    });

    return {
      labels: Object.keys(typeCounts),
      values: Object.values(typeCounts)
    };
  }

  _generateSpeedData(sessions) {
    const labels = [];
    const values = [];
    const dailySpeeds = {};

    sessions.forEach(session => {
      const date = session.createdAt.toISOString().split('T')[0];
      if (!dailySpeeds[date]) {
        dailySpeeds[date] = { total: 0, count: 0 };
      }
      dailySpeeds[date].total += session.readingSpeed;
      dailySpeeds[date].count += 1;
    });

    Object.entries(dailySpeeds).forEach(([date, data]) => {
      labels.push(date);
      values.push(data.total / data.count);
    });

    return { labels, values };
  }

  _generateCompletionData(sessions) {
    const labels = [];
    const values = [];
    const dailyCompletions = {};

    sessions.forEach(session => {
      const date = session.createdAt.toISOString().split('T')[0];
      if (!dailyCompletions[date]) {
        dailyCompletions[date] = { completed: 0, total: 0 };
      }
      dailyCompletions[date].total += 1;
      if (session.completed) {
        dailyCompletions[date].completed += 1;
      }
    });

    Object.entries(dailyCompletions).forEach(([date, data]) => {
      labels.push(date);
      values.push((data.completed / data.total) * 100);
    });

    return { labels, values };
  }

  _generateCSV(documents, sessions) {
    const headers = [
      'Date',
      'Document Title',
      'Document Type',
      'Reading Duration (minutes)',
      'Reading Speed (words/minute)',
      'Completion Status',
      'Notes'
    ];

    const rows = sessions.map(session => {
      const document = documents.find(d => d._id.toString() === session.documentId.toString());
      return [
        session.createdAt.toISOString().split('T')[0],
        document?.title || 'Unknown',
        document?.fileType || 'Unknown',
        (session.duration / 60).toFixed(2),
        session.readingSpeed.toFixed(2),
        session.completed ? 'Completed' : 'Incomplete',
        session.notes || ''
      ];
    });

    return [headers, ...rows]
      .map(row => row.join(','))
      .join('\n');
  }
}

module.exports = new AnalyticsController(); 