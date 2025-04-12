import { Ref } from 'vue'

export interface Document {
  id: string
  name: string
  type: string
  size: number
  createdAt: string
  updatedAt: string
}

export interface DocumentShare {
  id: string
  name: string
  email: string
  permission: 'view' | 'edit' | 'admin'
  avatar?: string
}

export interface ShareLink {
  link: string
  allowPublicAccess: boolean
  requirePassword: boolean
}

export interface DocumentStore {
  documents: Ref<Document[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  uploadProgress: Ref<number>
  
  uploadDocument: (formData: FormData, onProgress?: (progress: number) => void) => Promise<Document>
  processDocument: (documentId: string) => Promise<Document>
  getDocuments: () => Promise<void>
  getDocument: (id: string) => Promise<Document>
  deleteDocument: (id: string) => Promise<void>
  updateDocument: (id: string, data: Partial<Document>) => Promise<Document>
  getDocumentShares: (documentId: string) => Promise<{ data: DocumentShare[] }>
  shareDocument: (documentId: string, data: { email: string; permission: 'view' | 'edit' | 'admin' }) => Promise<{ data: DocumentShare }>
  removeShare: (documentId: string, userId: string) => Promise<void>
  updateSharePermission: (documentId: string, userId: string, data: { permission: 'view' | 'edit' | 'admin' }) => Promise<{ data: DocumentShare }>
  getShareLink: (documentId: string) => Promise<{ data: ShareLink }>
  updateShareLink: (documentId: string, data: { allowPublicAccess: boolean; requirePassword: boolean; password?: string }) => Promise<{ data: ShareLink }>
} 