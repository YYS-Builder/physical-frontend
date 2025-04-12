import { Store } from 'pinia'

export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  read: boolean
  createdAt: Date
}

export interface AnalyticsSummary {
  totalDocuments: number
  totalReadingTime: number
  averageReadingSpeed: number
  completionRate: number
}

export interface Document {
  id: string
  title: string
  type: string
  size: number
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
}

export interface Share {
  id: string
  userId: string
  permission: 'view' | 'edit'
}

export interface NotificationStore extends Store {
  notifications: Notification[]
  loading: boolean
  error: string | null
  getNotifications: () => Promise<void>
  markAsRead: (id: string) => Promise<void>
  markAllAsRead: () => Promise<void>
  deleteNotification: (id: string) => Promise<void>
  clearAll: () => Promise<void>
}

export interface AnalyticsStore extends Store {
  summary: AnalyticsSummary
  readingActivity: any[]
  documentTypes: any[]
  readingSpeedTrend: any[]
  completionRate: any[]
  topDocuments: any[]
  readingPatterns: any[]
  loading: boolean
  error: string | null
  getSummary: () => Promise<void>
  getReadingActivity: (params?: { startDate?: string; endDate?: string }) => Promise<void>
  getDocumentTypes: () => Promise<void>
  getReadingSpeedTrend: (params?: { startDate?: string; endDate?: string }) => Promise<void>
  getCompletionRate: (params?: { startDate?: string; endDate?: string }) => Promise<void>
  getTopDocuments: () => Promise<void>
  getReadingPatterns: (params?: { startDate?: string; endDate?: string }) => Promise<void>
  exportData: () => Promise<Blob>
}

export interface DocumentStore extends Store {
  documents: Document[]
  loading: boolean
  error: string | null
  uploadDocument: (file: File) => Promise<Document>
  processDocument: (id: string) => Promise<void>
  getDocumentShares: (id: string) => Promise<Share[]>
  getShareLink: (id: string) => Promise<string>
  shareDocument: (id: string, data: { email: string; permission: string }) => Promise<Share>
  removeShare: (id: string, userId: string) => Promise<void>
  updateSharePermission: (id: string, userId: string, data: { permission: string }) => Promise<void>
  updateShareLink: (id: string, data: { allowPublicAccess: boolean; requirePassword: boolean; password?: string }) => Promise<void>
} 