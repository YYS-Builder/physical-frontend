<template>
  <div class="share-dialog">
    <div class="dialog-header">
      <h3>Share Document</h3>
      <button class="btn btn-icon" @click="$emit('close')">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div class="dialog-content">
      <div class="share-options">
        <div class="form-group">
          <label>Share with</label>
          <div class="input-group">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search users or enter email"
              @keyup.enter="addUser"
            />
            <button class="btn btn-primary" @click="addUser">Add</button>
          </div>
        </div>

        <div class="permission-options">
          <label>Permission</label>
          <div class="radio-group">
            <label>
              <input
                type="radio"
                v-model="selectedPermission"
                value="view"
              />
              Can view
            </label>
            <label>
              <input
                type="radio"
                v-model="selectedPermission"
                value="edit"
              />
              Can edit
            </label>
            <label>
              <input
                type="radio"
                v-model="selectedPermission"
                value="admin"
              />
              Can manage
            </label>
          </div>
        </div>
      </div>

      <div class="shared-users" v-if="sharedUsers.length > 0">
        <h4>Shared with</h4>
        <div class="user-list">
          <div v-for="user in sharedUsers" :key="user.id" class="user-item">
            <div class="user-info">
              <img :src="user.avatar" :alt="user.name" class="avatar" />
              <span class="name">{{ user.name }}</span>
              <span class="email">{{ user.email }}</span>
            </div>
            <div class="user-actions">
              <select v-model="user.permission" @change="updatePermission(user)">
                <option value="view">Can view</option>
                <option value="edit">Can edit</option>
                <option value="admin">Can manage</option>
              </select>
              <button class="btn btn-icon" @click="removeUser(user)">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="share-link" v-if="shareLink">
        <h4>Share link</h4>
        <div class="link-container">
          <input
            type="text"
            :value="shareLink"
            readonly
            @click="selectLink"
          />
          <button class="btn btn-secondary" @click="copyLink">
            Copy link
          </button>
        </div>
        <div class="link-options">
          <label>
            <input
              type="checkbox"
              v-model="allowPublicAccess"
              @change="updateLinkAccess"
            />
            Allow public access
          </label>
          <label>
            <input
              type="checkbox"
              v-model="requirePassword"
              @change="updateLinkAccess"
            />
            Require password
          </label>
          <input
            v-if="requirePassword"
            type="password"
            v-model="linkPassword"
            placeholder="Enter password"
            @change="updateLinkAccess"
          />
        </div>
      </div>
    </div>

    <div class="dialog-footer">
      <button class="btn btn-secondary" @click="$emit('close')">
        Cancel
      </button>
      <button class="btn btn-primary" @click="saveChanges">
        Save changes
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useDocumentStore } from '@/stores/documents'

export default {
  name: 'ShareDialog',
  props: {
    documentId: {
      type: String,
      required: true
    }
  },
  setup(props, { emit }) {
    const documentStore = useDocumentStore()
    const searchQuery = ref('')
    const selectedPermission = ref('view')
    const sharedUsers = ref([])
    const shareLink = ref('')
    const allowPublicAccess = ref(false)
    const requirePassword = ref(false)
    const linkPassword = ref('')

    const getSharedUsers = async () => {
      try {
        const response = await documentStore.getDocumentShares(props.documentId)
        sharedUsers.value = response.data
      } catch (error) {
        console.error('Failed to fetch shared users:', error)
      }
    }

    const getShareLink = async () => {
      try {
        const response = await documentStore.getShareLink(props.documentId)
        shareLink.value = response.data.link
        allowPublicAccess.value = response.data.allowPublicAccess
        requirePassword.value = response.data.requirePassword
      } catch (error) {
        console.error('Failed to fetch share link:', error)
      }
    }

    const addUser = async () => {
      if (!searchQuery.value) return

      try {
        const response = await documentStore.shareDocument(props.documentId, {
          email: searchQuery.value,
          permission: selectedPermission.value
        })
        sharedUsers.value.push(response.data)
        searchQuery.value = ''
      } catch (error) {
        console.error('Failed to add user:', error)
      }
    }

    const removeUser = async (user) => {
      try {
        await documentStore.removeShare(props.documentId, user.id)
        sharedUsers.value = sharedUsers.value.filter(u => u.id !== user.id)
      } catch (error) {
        console.error('Failed to remove user:', error)
      }
    }

    const updatePermission = async (user) => {
      try {
        await documentStore.updateSharePermission(props.documentId, user.id, {
          permission: user.permission
        })
      } catch (error) {
        console.error('Failed to update permission:', error)
      }
    }

    const updateLinkAccess = async () => {
      try {
        await documentStore.updateShareLink(props.documentId, {
          allowPublicAccess: allowPublicAccess.value,
          requirePassword: requirePassword.value,
          password: linkPassword.value
        })
      } catch (error) {
        console.error('Failed to update link access:', error)
      }
    }

    const copyLink = () => {
      navigator.clipboard.writeText(shareLink.value)
    }

    const selectLink = (event) => {
      event.target.select()
    }

    const saveChanges = () => {
      // Emit event to parent component
      emit('save', {
        sharedUsers: sharedUsers.value,
        shareLink: shareLink.value,
        allowPublicAccess: allowPublicAccess.value,
        requirePassword: requirePassword.value
      })
    }

    // Fetch initial data
    getSharedUsers()
    getShareLink()

    return {
      searchQuery,
      selectedPermission,
      sharedUsers,
      shareLink,
      allowPublicAccess,
      requirePassword,
      linkPassword,
      addUser,
      removeUser,
      updatePermission,
      updateLinkAccess,
      copyLink,
      selectLink,
      saveChanges
    }
  }
}
</script>

<style scoped>
.share-dialog {
  background-color: var(--background-color);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.dialog-content {
  padding: 1rem;
}

.share-options {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.input-group input {
  flex: 1;
}

.permission-options {
  margin-top: 1rem;
}

.radio-group {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.shared-users {
  margin-top: 2rem;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background-color: var(--background-color-light);
  border-radius: 4px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.name {
  font-weight: 500;
}

.email {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.share-link {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.link-container {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.link-container input {
  flex: 1;
}

.link-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .share-dialog {
    margin: 1rem;
  }

  .user-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .user-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style> 