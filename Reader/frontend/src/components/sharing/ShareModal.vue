<template>
  <div class="share-modal">
    <div class="modal-header">
      <h2>Share {{ itemType }}</h2>
      <button @click="$emit('close')" class="close-button">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div class="modal-content">
      <div class="share-options">
        <div class="share-option">
          <h3>Share Link</h3>
          <div class="link-container">
            <input
              type="text"
              :value="shareLink"
              readonly
              class="link-input"
            >
            <button @click="copyLink" class="copy-button">
              <i class="fas fa-copy"></i>
            </button>
          </div>
          <div class="link-settings">
            <label class="setting-option">
              <input
                type="checkbox"
                v-model="settings.allowComments"
              >
              <span>Allow Comments</span>
            </label>
            <label class="setting-option">
              <input
                type="checkbox"
                v-model="settings.allowAnnotations"
              >
              <span>Allow Annotations</span>
            </label>
            <label class="setting-option">
              <input
                type="checkbox"
                v-model="settings.allowDownloads"
              >
              <span>Allow Downloads</span>
            </label>
          </div>
        </div>

        <div class="share-option">
          <h3>Share via Email</h3>
          <form @submit.prevent="sendEmail" class="email-form">
            <div class="form-group">
              <label for="email">Email Address</label>
              <input
                type="email"
                id="email"
                v-model="emailForm.recipient"
                placeholder="Enter email address"
                required
              >
            </div>
            <div class="form-group">
              <label for="message">Message (optional)</label>
              <textarea
                id="message"
                v-model="emailForm.message"
                placeholder="Add a personal message"
                rows="3"
              ></textarea>
            </div>
            <button type="submit" class="btn btn-primary">
              <i class="fas fa-paper-plane"></i> Send
            </button>
          </form>
        </div>

        <div class="share-option">
          <h3>Share with Team</h3>
          <div class="team-search">
            <input
              type="text"
              v-model="teamSearch"
              placeholder="Search team members"
              class="search-input"
            >
            <div class="team-list">
              <div
                v-for="member in filteredTeamMembers"
                :key="member.id"
                class="team-member"
              >
                <img
                  :src="member.avatar"
                  :alt="member.name"
                  class="member-avatar"
                >
                <div class="member-info">
                  <span class="member-name">{{ member.name }}</span>
                  <span class="member-role">{{ member.role }}</span>
                </div>
                <div class="member-actions">
                  <select
                    v-model="member.permission"
                    class="permission-select"
                  >
                    <option value="view">Can View</option>
                    <option value="comment">Can Comment</option>
                    <option value="edit">Can Edit</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="share-preview">
        <h3>Preview</h3>
        <div class="preview-card">
          <div class="preview-header">
            <img
              :src="item.thumbnail"
              :alt="item.title"
              class="preview-thumbnail"
            >
            <div class="preview-info">
              <h4>{{ item.title }}</h4>
              <p class="preview-description">{{ item.description }}</p>
            </div>
          </div>
          <div class="preview-details">
            <div class="detail-item">
              <i class="fas fa-user"></i>
              <span>Shared by {{ currentUser.name }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-clock"></i>
              <span>Shared {{ formatDate(new Date()) }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-lock"></i>
              <span>{{ settings.allowDownloads ? 'Downloadable' : 'View Only' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal-footer">
      <button @click="$emit('close')" class="btn btn-outline">
        Cancel
      </button>
      <button @click="saveSettings" class="btn btn-primary">
        Save Settings
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'

export default {
  name: 'ShareModal',
  props: {
    item: {
      type: Object,
      required: true
    },
    itemType: {
      type: String,
      required: true,
      validator: value => ['document', 'collection'].includes(value)
    }
  },
  setup(props) {
    const userStore = useUserStore()
    const currentUser = userStore.user

    const shareLink = computed(() => {
      return `${window.location.origin}/share/${props.item.id}`
    })

    const settings = ref({
      allowComments: true,
      allowAnnotations: true,
      allowDownloads: false
    })

    const emailForm = ref({
      recipient: '',
      message: ''
    })

    const teamSearch = ref('')
    const teamMembers = ref([
      {
        id: 1,
        name: 'John Doe',
        role: 'Editor',
        avatar: '/avatars/john.jpg',
        permission: 'view'
      },
      {
        id: 2,
        name: 'Jane Smith',
        role: 'Reviewer',
        avatar: '/avatars/jane.jpg',
        permission: 'comment'
      }
      // Add more team members as needed
    ])

    const filteredTeamMembers = computed(() => {
      const search = teamSearch.value.toLowerCase()
      return teamMembers.value.filter(member =>
        member.name.toLowerCase().includes(search) ||
        member.role.toLowerCase().includes(search)
      )
    })

    const copyLink = async () => {
      try {
        await navigator.clipboard.writeText(shareLink.value)
        // Show success message
      } catch (err) {
        console.error('Failed to copy link:', err)
        // Show error message
      }
    }

    const sendEmail = async () => {
      try {
        // Implement email sending logic
        emailForm.value = {
          recipient: '',
          message: ''
        }
        // Show success message
      } catch (err) {
        console.error('Failed to send email:', err)
        // Show error message
      }
    }

    const saveSettings = async () => {
      try {
        // Implement settings saving logic
        // Show success message
        this.$emit('close')
      } catch (err) {
        console.error('Failed to save settings:', err)
        // Show error message
      }
    }

    const formatDate = (date) => {
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }).format(date)
    }

    return {
      currentUser,
      shareLink,
      settings,
      emailForm,
      teamSearch,
      teamMembers,
      filteredTeamMembers,
      copyLink,
      sendEmail,
      saveSettings,
      formatDate
    }
  }
}
</script>

<style scoped>
.share-modal {
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.close-button {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.5rem;
}

.modal-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  padding: 1.5rem;
}

.share-options {
  display: grid;
  gap: 2rem;
}

.share-option {
  background-color: var(--color-background-alt);
  border-radius: var(--border-radius);
  padding: 1.5rem;
}

.share-option h3 {
  margin: 0 0 1rem;
  font-size: 1.25rem;
}

.link-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.link-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
  color: var(--color-text);
}

.copy-button {
  padding: 0.75rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
}

.link-settings {
  display: grid;
  gap: 0.75rem;
}

.setting-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.email-form {
  display: grid;
  gap: 1rem;
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

.form-group input,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
  color: var(--color-text);
}

.team-search {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-input {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
  color: var(--color-text);
}

.team-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 200px;
  overflow-y: auto;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background-color: var(--color-background);
  border-radius: var(--border-radius);
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.member-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.member-name {
  font-weight: 500;
}

.member-role {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.permission-select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
  color: var(--color-text);
}

.share-preview {
  background-color: var(--color-background-alt);
  border-radius: var(--border-radius);
  padding: 1.5rem;
}

.preview-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  padding: 1rem;
  box-shadow: var(--shadow-sm);
}

.preview-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.preview-thumbnail {
  width: 80px;
  height: 80px;
  border-radius: var(--border-radius);
  object-fit: cover;
}

.preview-info h4 {
  margin: 0 0 0.5rem;
}

.preview-description {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.preview-details {
  display: grid;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
}

@media (max-width: 768px) {
  .modal-content {
    grid-template-columns: 1fr;
  }

  .share-preview {
    display: none;
  }
}
</style> 