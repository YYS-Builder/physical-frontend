const { Model, DataTypes } = require('sequelize');
const sequelize = require('../config/database');

class Document extends Model {}

Document.init({
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  fileType: {
    type: DataTypes.STRING,
    allowNull: false
  },
  filePath: {
    type: DataTypes.STRING,
    allowNull: true
  },
  processedData: {
    type: DataTypes.JSONB,
    allowNull: true
  },
  metadata: {
    type: DataTypes.JSONB,
    allowNull: true
  },
  status: {
    type: DataTypes.ENUM('pending', 'processing', 'completed', 'failed'),
    defaultValue: 'pending'
  },
  progress: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },
  userId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'Users',
      key: 'id'
    }
  },
  collectionId: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'Collections',
      key: 'id'
    }
  }
}, {
  sequelize,
  modelName: 'Document',
  tableName: 'documents',
  timestamps: true,
  indexes: [
    {
      fields: ['userId']
    },
    {
      fields: ['collectionId']
    },
    {
      fields: ['status']
    }
  ]
});

module.exports = Document; 