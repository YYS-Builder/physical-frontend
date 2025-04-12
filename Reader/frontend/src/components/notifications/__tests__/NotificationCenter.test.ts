import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import NotificationCenter from '../NotificationCenter.vue'
import { useNotificationStore } from '@/stores/notifications'

// Mock the notification store
vi.mock('@/stores/notifications', () => ({
  useNotificationStore: vi.fn(() => ({
    notifications: [],
    loading: false,
    error: null,
    getNotifications: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    deleteNotification: vi.fn(),
    clearAll: vi.fn()
  }))
}))

describe('NotificationCenter', () => {
  let wrapper
  let notificationStore

  beforeEach(() => {
    notificationStore = useNotificationStore()
    wrapper = mount(NotificationCenter)
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.notification-center').exists()).toBe(true)
    expect(wrapper.find('.header').exists()).toBe(true)
  })

  it('fetches notifications on mount', () => {
    expect(notificationStore.getNotifications).toHaveBeenCalled()
  })

  it('displays loading state', async () => {
    notificationStore.loading = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.loading').exists()).toBe(true)
  })

  it('displays error state', async () => {
    notificationStore.error = 'Failed to fetch notifications'
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.error').exists()).toBe(true)
    expect(wrapper.find('.error').text()).toContain('Failed to fetch notifications')
  })

  it('displays empty state', async () => {
    notificationStore.notifications = []
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })

  it('marks a notification as read', async () => {
    const notification = {
      id: '123',
      title: 'Test Notification',
      message: 'This is a test',
      type: 'info',
      read: false,
      createdAt: new Date()
    }

    notificationStore.notifications = [notification]
    await wrapper.vm.$nextTick()

    await wrapper.find('.btn-icon').trigger('click')
    expect(notificationStore.markAsRead).toHaveBeenCalledWith('123')
  })

  it('marks all notifications as read', async () => {
    const notifications = [
      {
        id: '123',
        title: 'Test Notification 1',
        message: 'This is a test',
        type: 'info',
        read: false,
        createdAt: new Date()
      },
      {
        id: '456',
        title: 'Test Notification 2',
        message: 'This is another test',
        type: 'success',
        read: false,
        createdAt: new Date()
      }
    ]

    notificationStore.notifications = notifications
    await wrapper.vm.$nextTick()

    await wrapper.find('.btn-secondary').trigger('click')
    expect(notificationStore.markAllAsRead).toHaveBeenCalled()
  })

  it('deletes a notification', async () => {
    const notification = {
      id: '123',
      title: 'Test Notification',
      message: 'This is a test',
      type: 'info',
      read: true,
      createdAt: new Date()
    }

    notificationStore.notifications = [notification]
    await wrapper.vm.$nextTick()

    const deleteButton = wrapper.findAll('.btn-icon')[1]
    await deleteButton.trigger('click')
    expect(notificationStore.deleteNotification).toHaveBeenCalledWith('123')
  })

  it('clears all notifications', async () => {
    const notifications = [
      {
        id: '123',
        title: 'Test Notification 1',
        message: 'This is a test',
        type: 'info',
        read: true,
        createdAt: new Date()
      },
      {
        id: '456',
        title: 'Test Notification 2',
        message: 'This is another test',
        type: 'success',
        read: true,
        createdAt: new Date()
      }
    ]

    notificationStore.notifications = notifications
    await wrapper.vm.$nextTick()

    await wrapper.find('.btn-danger').trigger('click')
    expect(notificationStore.clearAll).toHaveBeenCalled()
  })

  it('formats dates correctly', () => {
    const date = new Date('2023-01-01T12:00:00Z')
    expect(wrapper.vm.formatDate(date)).toBe('Jan 1, 2023')
  })

  it('gets correct notification icon', () => {
    expect(wrapper.vm.getNotificationIcon('info')).toBe('fas fa-info-circle')
    expect(wrapper.vm.getNotificationIcon('success')).toBe('fas fa-check-circle')
    expect(wrapper.vm.getNotificationIcon('warning')).toBe('fas fa-exclamation-circle')
    expect(wrapper.vm.getNotificationIcon('error')).toBe('fas fa-times-circle')
    expect(wrapper.vm.getNotificationIcon('unknown')).toBe('fas fa-bell')
  })
}) 