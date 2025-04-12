<template>
  <div class="share-dialog">
    <div class="dialog-header">
      <h3>Share Document</h3>
      <button class="close-button" @click="$emit('close')">
        <span class="icon">×</span>
      </button>
    </div>
    
    <div class="dialog-content">
      <div class="share-section">
        <h4>Share with people</h4>
        <div class="share-input">
          <input
            type="text"
            v-model="email"
            placeholder="Enter email address"
            @keyup.enter="addShare"
          />
          <select v-model="permission">
            <option value="read">Can view</option>
            <option value="write">Can edit</option>
            <option value="admin">Can manage</option>
          </select>
          <button
            class="add-button"
            @click="addShare"
            :disabled="!email || !permission"
          >
            Add
          </button>
        </div>
        
        <div class="share-list">
          <div
            v-for="share in shares"
            :key="share.id"
            class="share-item"
          >
            <div class="share-info">
              <div class="share-email">{{ share.email }}</div>
              <div class="share-permission">{{ share.permission }}</div>
            </div>
            <button
              class="remove-button"
              @click="removeShare(share.id)"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
      
      <div class="share-section">
        <h4>Share with link</h4>
        <div class="link-options">
          <div class="option">
            <input
              type="checkbox"
              id="allowPublic"
              v-model="allowPublicAccess"
            />
            <label for="allowPublic">Allow public access</label>
          </div>
          <div class="option">
            <input
              type="checkbox"
              id="requirePassword"
              v-model="requirePassword"
            />
            <label for="requirePassword">Require password</label>
          </div>
          <div class="option" v-if="requirePassword">
            <input
              type="password"
              v-model="password"
              placeholder="Enter password"
            />
          </div>
        </div>
        
        <div class="link-section" v-if="shareLink">
          <div class="link-input">
            <input
              type="text"
              :value="shareLink"
              readonly
            />
            <button
              class="copy-button"
              @click="copyLink"
            >
              Copy
            </button>
          </div>
          <div class="link-expiry">
            <label>Expires in</label>
            <select v-model="expiry">
              <option value="1">1 day</option>
              <option value="7">7 days</option>
              <option value="30">30 days</option>
              <option value="never">Never</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    
    <div class="dialog-footer">
      <button
        class="cancel-button"
        @click="$emit('close')"
      >
        Cancel
      </button>
      <button
        class="save-button"
        @click="saveChanges"
        :disabled="!hasChanges"
      >
        Save Changes
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'

interface Share {
  id: string
  email: string
  permission: string
}

export default defineComponent({
  name: 'ShareDialog',
  props: {
    documentId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const email = ref('')
    const permission = ref('read')
    const shares = ref<Share[]>([])
    const allowPublicAccess = ref(false)
    const requirePassword = ref(false)
    const password = ref('')
    const shareLink = ref('')
    const expiry = ref('7')
    
    const hasChanges = computed(() => {
      return shares.value.length > 0 || shareLink.value !== ''
    })
    
    const addShare = () => {
      if (email.value && permission.value) {
        shares.value.push({
          id: Math.random().toString(36).substr(2, 9),
          email: email.value,
          permission: permission.value
        })
        email.value = ''
        permission.value = 'read'
      }
    }
    
    const removeShare = (id: string) => {
      shares.value = shares.value.filter(share => share.id !== id)
    }
    
    const copyLink = () => {
      if (shareLink.value) {
        navigator.clipboard.writeText(shareLink.value)
      }
    }
    
    const saveChanges = () => {
      // TODO: Implement save changes
      console.log('Saving changes:', {
        documentId: props.documentId,
        shares: shares.value,
        linkSettings: {
          allowPublicAccess: allowPublicAccess.value,
          requirePassword: requirePassword.value,
          password: password.value,
          expiry: expiry.value
        }
      })
    }
    
    return {
      email,
      permission,
      shares,
      allowPublicAccess,
      requirePassword,
      password,
      shareLink,
      expiry,
      hasChanges,
      addShare,
      removeShare,
      copyLink,
      saveChanges
    }
  }
})
</script>

<style scoped>
.share-dialog {
  width: 500px;
  background-color: var(--color-background);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-text-light);
  cursor: pointer;
  padding: 0.5rem;
}

.dialog-content {
  padding: 1rem;
}

.share-section {
  margin-bottom: 1.5rem;
}

.share-section h4 {
  margin-bottom: 1rem;
  color: var(--color-text);
}

.share-input {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.share-input input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.share-input select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.add-button {
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-button:disabled {
  background-color: var(--color-background-mute);
  cursor: not-allowed;
}

.share-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.share-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: var(--color-background-soft);
  border-radius: 4px;
}

.share-info {
  display: flex;
  gap: 1rem;
}

.share-email {
  font-weight: 500;
}

.share-permission {
  color: var(--color-text-light);
}

.remove-button {
  padding: 0.25rem 0.5rem;
  background-color: var(--color-danger);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.link-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.link-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.link-input {
  display: flex;
  gap: 0.5rem;
}

.link-input input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.copy-button {
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.link-expiry {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.link-expiry select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid var(--color-border);
}

.cancel-button {
  padding: 0.5rem 1rem;
  background-color: var(--color-background-mute);
  color: var(--color-text);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-button {
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-button:disabled {
  background-color: var(--color-background-mute);
  cursor: not-allowed;
}
</style> 