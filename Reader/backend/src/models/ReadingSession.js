const { Model, DataTypes } = require('sequelize');
const sequelize = require('../config/database');

class ReadingSession extends Model {}

ReadingSession.init({
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  startTime: {
    type: DataTypes.DATE,
    allowNull: false
  },
  endTime: {
    type: DataTypes.DATE,
    allowNull: false
  },
  pagesRead: {
    type: DataTypes.INTEGER,
    allowNull: true
  },
  quizScore: {
    type: DataTypes.FLOAT,
    allowNull: true,
    validate: {
      min: 0,
      max: 100
    }
  },
  distractionCount: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: 0
  },
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  userId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'Users',
      key: 'id'
    }
  },
  documentId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'Documents',
      key: 'id'
    }
  }
}, {
  sequelize,
  modelName: 'ReadingSession',
  tableName: 'reading_sessions',
  timestamps: true,
  indexes: [
    {
      fields: ['userId']
    },
    {
      fields: ['documentId']
    },
    {
      fields: ['startTime']
    }
  ]
});

module.exports = ReadingSession; 