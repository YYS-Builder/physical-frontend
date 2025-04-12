const { ReadingSession, Document, User } = require('../models');
const { Op } = require('sequelize');
const moment = require('moment');
const { createObjectCsvWriter } = require('csv-writer');

class AnalyticsService {
  async getReadingStats(userId, options = {}) {
    const { startDate, endDate, documentId } = options;
    
    const where = { userId };
    if (startDate) where.startTime = { [Op.gte]: startDate };
    if (endDate) where.endTime = { [Op.lte]: endDate };
    if (documentId) where.documentId = documentId;

    const sessions = await ReadingSession.findAll({
      where,
      include: [{
        model: Document,
        attributes: ['title', 'fileType']
      }],
      order: [['startTime', 'DESC']]
    });

    return this.aggregateReadingStats(sessions);
  }

  async getPerformanceMetrics(userId, options = {}) {
    const { startDate, endDate, documentId } = options;
    
    const where = { userId };
    if (startDate) where.startTime = { [Op.gte]: startDate };
    if (endDate) where.endTime = { [Op.lte]: endDate };
    if (documentId) where.documentId = documentId;

    const sessions = await ReadingSession.findAll({
      where,
      include: [{
        model: Document,
        attributes: ['title', 'fileType', 'processedData']
      }],
      order: [['startTime', 'DESC']]
    });

    return this.calculatePerformanceMetrics(sessions);
  }

  async getDocumentAnalytics(documentId, options = {}) {
    const { startDate, endDate } = options;
    
    const where = { documentId };
    if (startDate) where.startTime = { [Op.gte]: startDate };
    if (endDate) where.endTime = { [Op.lte]: endDate };

    const sessions = await ReadingSession.findAll({
      where,
      include: [{
        model: User,
        attributes: ['name', 'email']
      }],
      order: [['startTime', 'DESC']]
    });

    return this.aggregateDocumentAnalytics(sessions);
  }

  async exportAnalytics(userId, format = 'csv', options = {}) {
    const stats = await this.getReadingStats(userId, options);
    const metrics = await this.getPerformanceMetrics(userId, options);

    switch (format.toLowerCase()) {
      case 'csv':
        return this.exportToCSV(stats, metrics);
      case 'json':
        return this.exportToJSON(stats, metrics);
      default:
        throw new Error('Unsupported export format');
    }
  }

  aggregateReadingStats(sessions) {
    const totalSessions = sessions.length;
    const totalReadingTime = sessions.reduce((sum, session) => 
      sum + (session.endTime - session.startTime), 0);
    
    const documentsRead = new Set(sessions.map(s => s.documentId)).size;
    const averageSessionDuration = totalReadingTime / totalSessions;

    const dailyStats = this.calculateDailyStats(sessions);
    const documentStats = this.calculateDocumentStats(sessions);

    return {
      totalSessions,
      totalReadingTime,
      documentsRead,
      averageSessionDuration,
      dailyStats,
      documentStats
    };
  }

  calculatePerformanceMetrics(sessions) {
    const metrics = {
      readingSpeed: this.calculateReadingSpeed(sessions),
      comprehension: this.calculateComprehension(sessions),
      focus: this.calculateFocus(sessions),
      consistency: this.calculateConsistency(sessions)
    };

    return {
      ...metrics,
      trends: this.calculateTrends(sessions, metrics)
    };
  }

  aggregateDocumentAnalytics(sessions) {
    return {
      totalReads: sessions.length,
      uniqueReaders: new Set(sessions.map(s => s.userId)).size,
      averageReadingTime: this.calculateAverageReadingTime(sessions),
      completionRate: this.calculateCompletionRate(sessions),
      readerEngagement: this.calculateReaderEngagement(sessions)
    };
  }

  calculateDailyStats(sessions) {
    const dailyStats = {};
    sessions.forEach(session => {
      const date = moment(session.startTime).format('YYYY-MM-DD');
      if (!dailyStats[date]) {
        dailyStats[date] = {
          sessions: 0,
          readingTime: 0,
          documents: new Set()
        };
      }
      dailyStats[date].sessions++;
      dailyStats[date].readingTime += session.endTime - session.startTime;
      dailyStats[date].documents.add(session.documentId);
    });

    return Object.entries(dailyStats).map(([date, stats]) => ({
      date,
      sessions: stats.sessions,
      readingTime: stats.readingTime,
      documents: stats.documents.size
    }));
  }

  calculateDocumentStats(sessions) {
    const documentStats = {};
    sessions.forEach(session => {
      const docId = session.documentId;
      if (!documentStats[docId]) {
        documentStats[docId] = {
          title: session.Document.title,
          type: session.Document.fileType,
          reads: 0,
          totalTime: 0
        };
      }
      documentStats[docId].reads++;
      documentStats[docId].totalTime += session.endTime - session.startTime;
    });

    return Object.values(documentStats).map(stats => ({
      ...stats,
      averageTime: stats.totalTime / stats.reads
    }));
  }

  calculateReadingSpeed(sessions) {
    const validSessions = sessions.filter(s => s.pagesRead > 0);
    if (validSessions.length === 0) return 0;

    const totalPages = validSessions.reduce((sum, s) => sum + s.pagesRead, 0);
    const totalTime = validSessions.reduce((sum, s) => 
      sum + (s.endTime - s.startTime), 0);

    return (totalPages / totalTime) * 3600; // pages per hour
  }

  calculateComprehension(sessions) {
    const validSessions = sessions.filter(s => s.quizScore !== null);
    if (validSessions.length === 0) return null;

    return validSessions.reduce((sum, s) => sum + s.quizScore, 0) / validSessions.length;
  }

  calculateFocus(sessions) {
    const validSessions = sessions.filter(s => s.distractionCount !== null);
    if (validSessions.length === 0) return null;

    const totalDistractions = validSessions.reduce((sum, s) => sum + s.distractionCount, 0);
    const totalTime = validSessions.reduce((sum, s) => 
      sum + (s.endTime - s.startTime), 0);

    return 1 - (totalDistractions / totalTime);
  }

  calculateConsistency(sessions) {
    if (sessions.length < 2) return null;

    const dates = sessions.map(s => moment(s.startTime).startOf('day').valueOf());
    const uniqueDays = new Set(dates).size;
    const totalDays = moment(sessions[0].startTime).diff(moment(sessions[sessions.length - 1].startTime), 'days') + 1;

    return uniqueDays / totalDays;
  }

  calculateTrends(sessions, metrics) {
    const weeklyData = this.groupByWeek(sessions);
    return {
      readingSpeed: this.calculateWeeklyTrend(weeklyData, 'readingSpeed'),
      comprehension: this.calculateWeeklyTrend(weeklyData, 'comprehension'),
      focus: this.calculateWeeklyTrend(weeklyData, 'focus'),
      consistency: this.calculateWeeklyTrend(weeklyData, 'consistency')
    };
  }

  groupByWeek(sessions) {
    const weeklyData = {};
    sessions.forEach(session => {
      const week = moment(session.startTime).startOf('week').format('YYYY-MM-DD');
      if (!weeklyData[week]) {
        weeklyData[week] = [];
      }
      weeklyData[week].push(session);
    });
    return weeklyData;
  }

  calculateWeeklyTrend(weeklyData, metric) {
    return Object.entries(weeklyData).map(([week, weekSessions]) => ({
      week,
      value: this[`calculate${metric.charAt(0).toUpperCase() + metric.slice(1)}`](weekSessions)
    }));
  }

  async exportToCSV(stats, metrics) {
    const csvWriter = createObjectCsvWriter({
      path: 'analytics.csv',
      header: [
        { id: 'metric', title: 'Metric' },
        { id: 'value', title: 'Value' },
        { id: 'unit', title: 'Unit' }
      ]
    });

    const records = [
      { metric: 'Total Sessions', value: stats.totalSessions, unit: 'sessions' },
      { metric: 'Total Reading Time', value: stats.totalReadingTime, unit: 'seconds' },
      { metric: 'Documents Read', value: stats.documentsRead, unit: 'documents' },
      { metric: 'Average Session Duration', value: stats.averageSessionDuration, unit: 'seconds' },
      { metric: 'Reading Speed', value: metrics.readingSpeed, unit: 'pages/hour' },
      { metric: 'Comprehension', value: metrics.comprehension, unit: 'score' },
      { metric: 'Focus', value: metrics.focus, unit: 'score' },
      { metric: 'Consistency', value: metrics.consistency, unit: 'score' }
    ];

    await csvWriter.writeRecords(records);
    return 'analytics.csv';
  }

  exportToJSON(stats, metrics) {
    return {
      readingStats: stats,
      performanceMetrics: metrics
    };
  }
}

module.exports = new AnalyticsService(); 