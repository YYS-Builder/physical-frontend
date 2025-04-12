<template>
  <div class="user-profile">
    <div class="profile-header">
      <div class="profile-avatar">
        <img :src="user.avatar || defaultAvatar" :alt="user.name" class="avatar-image">
        <button @click="changeAvatar" class="avatar-edit">
          <i class="fas fa-camera"></i>
        </button>
      </div>
      <div class="profile-info">
        <h1>{{ user.name }}</h1>
        <p class="email">{{ user.email }}</p>
        <div class="profile-stats">
          <div class="stat-item">
            <span class="stat-value">{{ userStats.documents }}</span>
            <span class="stat-label">Documents</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ userStats.collections }}</span>
            <span class="stat-label">Collections</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ userStats.readingTime }}</span>
            <span class="stat-label">Reading Time</span>
          </div>
        </div>
      </div>
    </div>

    <div class="profile-content">
      <div class="profile-section">
        <h2>Account Settings</h2>
        <form @submit.prevent="updateProfile" class="settings-form">
          <div class="form-group">
            <label for="name">Name</label>
            <input
              type="text"
              id="name"
              v-model="form.name"
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input
              type="email"
              id="email"
              v-model="form.email"
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="bio">Bio</label>
            <textarea
              id="bio"
              v-model="form.bio"
              :disabled="loading"
              rows="3"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <i class="fas fa-save"></i> Save Changes
            </button>
          </div>
        </form>
      </div>

      <div class="profile-section">
        <h2>Security</h2>
        <form @submit.prevent="changePassword" class="settings-form">
          <div class="form-group">
            <label for="currentPassword">Current Password</label>
            <input
              type="password"
              id="currentPassword"
              v-model="passwordForm.currentPassword"
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              v-model="passwordForm.newPassword"
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              v-model="passwordForm.confirmPassword"
              :disabled="loading"
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <i class="fas fa-key"></i> Change Password
            </button>
          </div>
        </form>
      </div>

      <div class="profile-section">
        <h2>Preferences</h2>
        <form @submit.prevent="updatePreferences" class="settings-form">
          <div class="form-group">
            <label>Theme</label>
            <div class="theme-options">
              <label class="theme-option">
                <input
                  type="radio"
                  v-model="preferences.theme"
                  value="light"
                  :disabled="loading"
                >
                <span>Light</span>
              </label>
              <label class="theme-option">
                <input
                  type="radio"
                  v-model="preferences.theme"
                  value="dark"
                  :disabled="loading"
                >
                <span>Dark</span>
              </label>
              <label class="theme-option">
                <input
                  type="radio"
                  v-model="preferences.theme"
                  value="system"
                  :disabled="loading"
                >
                <span>System</span>
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>Reading Settings</label>
            <div class="preference-options">
              <label class="preference-option">
                <input
                  type="checkbox"
                  v-model="preferences.autoScroll"
                  :disabled="loading"
                >
                <span>Auto-scroll</span>
              </label>
              <label class="preference-option">
                <input
                  type="checkbox"
                  v-model="preferences.showProgress"
                  :disabled="loading"
                >
                <span>Show reading progress</span>
              </label>
              <label class="preference-option">
                <input
                  type="checkbox"
                  v-model="preferences.rememberPosition"
                  :disabled="loading"
                >
                <span>Remember reading position</span>
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <i class="fas fa-save"></i> Save Preferences
            </button>
          </div>
        </form>
      </div>

      <div class="profile-section">
        <h2>Danger Zone</h2>
        <div class="danger-zone">
          <div class="danger-item">
            <h3>Export Data</h3>
            <p>Download all your documents and reading data</p>
            <button @click="exportData" class="btn btn-outline">
              <i class="fas fa-download"></i> Export Data
            </button>
          </div>
          <div class="danger-item">
            <h3>Delete Account</h3>
            <p>Permanently delete your account and all data</p>
            <button @click="confirmDelete" class="btn btn-danger">
              <i class="fas fa-trash"></i> Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Account Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content">
        <h2>Delete Account</h2>
        <p>Are you sure you want to delete your account? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="btn btn-outline">
            Cancel
          </button>
          <button @click="deleteAccount" class="btn btn-danger">
            Delete Account
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import defaultAvatar from '@/assets/default-avatar.png'

export default {
  name: 'UserProfile',
  setup() {
    const userStore = useUserStore()
    const loading = ref(false)
    const showDeleteModal = ref(false)

    const user = ref({
      name: '',
      email: '',
      avatar: '',
      bio: ''
    })

    const userStats = ref({
      documents: 0,
      collections: 0,
      readingTime: '0h 0m'
    })

    const form = ref({
      name: '',
      email: '',
      bio: ''
    })

    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    const preferences = ref({
      theme: 'system',
      autoScroll: true,
      showProgress: true,
      rememberPosition: true
    })

    const fetchUserData = async () => {
      try {
        loading.value = true
        const data = await userStore.getProfile()
        user.value = data.user
        userStats.value = data.stats
        form.value = { ...data.user }
        preferences.value = data.preferences
      } catch (err) {
        console.error('Failed to fetch user data:', err)
      } finally {
        loading.value = false
      }
    }

    const updateProfile = async () => {
      try {
        loading.value = true
        await userStore.updateProfile(form.value)
        user.value = { ...form.value }
      } catch (err) {
        console.error('Failed to update profile:', err)
      } finally {
        loading.value = false
      }
    }

    const changePassword = async () => {
      try {
        loading.value = true
        await userStore.changePassword(passwordForm.value)
        passwordForm.value = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
      } catch (err) {
        console.error('Failed to change password:', err)
      } finally {
        loading.value = false
      }
    }

    const updatePreferences = async () => {
      try {
        loading.value = true
        await userStore.updatePreferences(preferences.value)
      } catch (err) {
        console.error('Failed to update preferences:', err)
      } finally {
        loading.value = false
      }
    }

    const changeAvatar = async () => {
      try {
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = 'image/*'
        input.onchange = async (e) => {
          const file = e.target.files[0]
          if (file) {
            loading.value = true
            const avatarUrl = await userStore.uploadAvatar(file)
            user.value.avatar = avatarUrl
            loading.value = false
          }
        }
        input.click()
      } catch (err) {
        console.error('Failed to change avatar:', err)
      }
    }

    const exportData = async () => {
      try {
        loading.value = true
        await userStore.exportData()
      } catch (err) {
        console.error('Failed to export data:', err)
      } finally {
        loading.value = false
      }
    }

    const confirmDelete = () => {
      showDeleteModal.value = true
    }

    const deleteAccount = async () => {
      try {
        loading.value = true
        await userStore.deleteAccount()
        // Redirect to login page or handle logout
      } catch (err) {
        console.error('Failed to delete account:', err)
      } finally {
        loading.value = false
        showDeleteModal.value = false
      }
    }

    onMounted(() => {
      fetchUserData()
    })

    return {
      user,
      userStats,
      form,
      passwordForm,
      preferences,
      loading,
      showDeleteModal,
      defaultAvatar,
      updateProfile,
      changePassword,
      updatePreferences,
      changeAvatar,
      exportData,
      confirmDelete,
      deleteAccount
    }
  }
}
</script>

<style scoped>
.user-profile {
  padding: 2rem;
}

.profile-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 3rem;
}

.profile-avatar {
  position: relative;
  width: 150px;
  height: 150px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-edit {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-info {
  flex: 1;
}

.profile-info h1 {
  margin: 0 0 0.5rem;
  font-size: 2rem;
}

.email {
  margin: 0 0 1rem;
  color: var(--color-text-secondary);
}

.profile-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.profile-content {
  display: grid;
  gap: 2rem;
}

.profile-section {
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.profile-section h2 {
  margin: 0 0 1.5rem;
  font-size: 1.25rem;
}

.settings-form {
  display: grid;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: var(--color-text-secondary);
}

input[type="text"],
input[type="email"],
input[type="password"],
textarea {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
  color: var(--color-text);
}

input:disabled,
textarea:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.theme-options,
.preference-options {
  display: flex;
  gap: 1rem;
}

.theme-option,
.preference-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.danger-zone {
  display: grid;
  gap: 1.5rem;
}

.danger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--color-background-alt);
  border-radius: var(--border-radius);
}

.danger-item h3 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
}

.danger-item p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  padding: 2rem;
  max-width: 500px;
  width: 100%;
}

.modal-content h2 {
  margin: 0 0 1rem;
}

.modal-content p {
  margin: 0 0 1.5rem;
  color: var(--color-text-secondary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .profile-stats {
    justify-content: center;
  }

  .danger-item {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
}
</style> 