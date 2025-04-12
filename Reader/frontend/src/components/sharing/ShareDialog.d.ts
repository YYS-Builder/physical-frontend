import { ComponentPublicInstance } from 'vue'
import { DocumentShare, ShareLink } from '@/stores/documents'

export interface ShareDialogProps {
  documentId: string
  show: boolean
}

export interface ShareDialogEmits {
  (e: 'update:show', value: boolean): void
  (e: 'close'): void
}

export interface ShareDialogData {
  sharedUsers: DocumentShare[]
  shareLink: ShareLink | null
  loading: boolean
  error: string | null
  newUserEmail: string
  newUserPermission: 'view' | 'edit' | 'admin'
  showNewUserForm: boolean
}

export interface ShareDialogMethods {
  loadShares: () => Promise<void>
  loadShareLink: () => Promise<void>
  addUser: () => Promise<void>
  removeUser: (userId: string) => Promise<void>
  updatePermission: (userId: string, permission: 'view' | 'edit' | 'admin') => Promise<void>
  updateShareLink: (data: { allowPublicAccess: boolean; requirePassword: boolean; password?: string }) => Promise<void>
  copyLink: () => Promise<void>
}

export interface ShareDialogComponent extends ComponentPublicInstance, ShareDialogData, ShareDialogMethods {
  $props: ShareDialogProps
  $emit: ShareDialogEmits
} 