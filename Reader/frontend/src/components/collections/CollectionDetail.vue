<template>
  <div class="collection-detail">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading collection...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchCollection" class="btn btn-primary">Retry</button>
    </div>

    <template v-else>
      <div class="collection-header">
        <div class="collection-info">
          <h1>{{ collection.name }}</h1>
          <p class="collection-description">{{ collection.description }}</p>
          <div class="collection-meta">
            <span class="meta-item">
              <i class="fas fa-file"></i>
              {{ collection.document_count }} documents
            </span>
            <span class="meta-item">
              <i class="fas fa-users"></i>
              {{ collection.member_count }} members
            </span>
            <span class="meta-item">
              <i :class="collection.is_public ? 'fas fa-globe' : 'fas fa-lock'"></i>
              {{ collection.is_public ? 'Public' : 'Private' }}
            </span>
          </div>
        </div>

        <div class="collection-actions">
          <button @click="showShareModal = true" class="btn btn-outline">
            <i class="fas fa-share-alt"></i> Share
          </button>
          <button @click="showAddDocumentModal = true" class="btn btn-primary">
            <i class="fas fa-plus"></i> Add Document
          </button>
          <button @click="editCollection" class="btn btn-outline">
            <i class="fas fa-edit"></i> Edit
          </button>
        </div>
      </div>

      <div class="document-section">
        <div class="section-header">
          <h2>Documents</h2>
          <div class="document-filters">
            <div class="search-box">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search documents..."
                class="search-input"
              />
              <i class="fas fa-search search-icon"></i>
            </div>
            <select v-model="sortBy" class="filter-select">
              <option value="title">Title</option>
              <option value="created_at">Date Added</option>
              <option value="updated_at">Last Updated</option>
              <option value="size">Size</option>
            </select>
            <select v-model="sortOrder" class="filter-select">
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </div>
        </div>

        <div v-if="documentsLoading" class="loading">
          <div class="spinner"></div>
          <p>Loading documents...</p>
        </div>

        <div v-else-if="documentsError" class="error">
          <p>{{ documentsError }}</p>
          <button @click="fetchDocuments" class="btn btn-primary">Retry</button>
        </div>

        <div v-else-if="filteredDocuments.length === 0" class="empty-state">
          <p>No documents found</p>
          <button @click="showAddDocumentModal = true" class="btn btn-primary">
            Add your first document
          </button>
        </div>

        <div v-else class="document-grid">
          <div
            v-for="document in filteredDocuments"
            :key="document.id"
            class="document-card"
          >
            <div class="document-icon">
              <i :class="getDocumentIcon(document.type)"></i>
            </div>
            <div class="document-info">
              <h3>{{ document.title }}</h3>
              <p class="document-meta">
                <span>{{ formatFileSize(document.size) }}</span>
                <span>{{ formatDate(document.created_at) }}</span>
              </p>
            </div>
            <div class="document-actions">
              <button
                @click="viewDocument(document)"
                class="btn btn-outline"
              >
                View
              </button>
              <button
                @click="editDocument(document)"
                class="btn btn-outline"
              >
                Edit
              </button>
              <button
                @click="deleteDocument(document)"
                class="btn btn-outline"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Edit Collection Modal -->
    <Modal
      v-model="showEditModal"
      title="Edit Collection"
    >
      <form @submit.prevent="saveCollection" class="collection-form">
        <div class="form-group">
          <label for="name">Name</label>
          <input
            id="name"
            v-model="collectionForm.name"
            type="text"
            required
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="collectionForm.description"
            class="form-input"
            rows="3"
          ></textarea>
        </div>
        <div class="form-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="collectionForm.is_public"
            />
            Public Collection
          </label>
        </div>
        <div class="form-actions">
          <button
            type="button"
            @click="showEditModal = false"
            class="btn btn-outline"
          >
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            Save Changes
          </button>
        </div>
      </form>
    </Modal>

    <!-- Add Document Modal -->
    <Modal
      v-model="showAddDocumentModal"
      title="Add Document"
    >
      <form @submit.prevent="uploadDocument" class="document-form">
        <div class="form-group">
          <label for="title">Title</label>
          <input
            id="title"
            v-model="documentForm.title"
            type="text"
            required
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label for="file">File</label>
          <input
            id="file"
            type="file"
            @change="handleFileChange"
            required
            class="form-input"
          />
        </div>
        <div class="form-actions">
          <button
            type="button"
            @click="showAddDocumentModal = false"
            class="btn btn-outline"
          >
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            Upload
          </button>
        </div>
      </form>
    </Modal>

    <!-- Share Modal -->
    <Modal
      v-model="showShareModal"
      title="Share Collection"
    >
      <div class="share-form">
        <div class="form-group">
          <label>Share Link</label>
          <div class="share-link">
            <input
              :value="shareLink"
              type="text"
              readonly
              class="form-input"
            />
            <button
              @click="copyShareLink"
              class="btn btn-outline"
            >
              Copy
            </button>
          </div>
        </div>
        <div class="form-group">
          <label>Invite by Email</label>
          <div class="invite-form">
            <input
              v-model="inviteEmail"
              type="email"
              placeholder="Enter email address"
              class="form-input"
            />
            <button
              @click="sendInvite"
              class="btn btn-primary"
            >
              Send Invite
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <!-- Delete Confirmation Modal -->
    <Modal
      v-model="showDeleteModal"
      title="Delete Document"
    >
      <p>Are you sure you want to delete this document? This action cannot be undone.</p>
      <div class="modal-actions">
        <button
          @click="showDeleteModal = false"
          class="btn btn-outline"
        >
          Cancel
        </button>
        <button
          @click="confirmDelete"
          class="btn btn-danger"
        >
          Delete
        </button>
      </div>
    </Modal>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCollectionStore } from '@/stores/collections'
import { useDocumentStore } from '@/stores/documents'
import Modal from '@/components/common/Modal.vue'

export default {
  name: 'CollectionDetail',
  components: {
    Modal
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const collectionStore = useCollectionStore()
    const documentStore = useDocumentStore()

    const loading = ref(false)
    const error = ref(null)
    const documentsLoading = ref(false)
    const documentsError = ref(null)
    const searchQuery = ref('')
    const sortBy = ref('updated_at')
    const sortOrder = ref('desc')
    const showEditModal = ref(false)
    const showAddDocumentModal = ref(false)
    const showShareModal = ref(false)
    const showDeleteModal = ref(false)
    const documentToDelete = ref(null)
    const inviteEmail = ref('')

    const collection = computed(() => collectionStore.currentCollection)
    const documents = computed(() => documentStore.documents)

    const collectionForm = ref({
      name: '',
      description: '',
      is_public: false
    })

    const documentForm = ref({
      title: '',
      file: null
    })

    const shareLink = computed(() => {
      return `${window.location.origin}/collections/${route.params.id}/share`
    })

    const filteredDocuments = computed(() => {
      let filtered = documents.value

      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(doc =>
          doc.title.toLowerCase().includes(query)
        )
      }

      // Apply sorting
      filtered.sort((a, b) => {
        let comparison = 0
        if (sortBy.value === 'title') {
          comparison = a.title.localeCompare(b.title)
        } else if (sortBy.value === 'size') {
          comparison = a.size - b.size
        } else {
          comparison = new Date(a[sortBy.value]) - new Date(b[sortBy.value])
        }
        return sortOrder.value === 'asc' ? comparison : -comparison
      })

      return filtered
    })

    const fetchCollection = async () => {
      loading.value = true
      error.value = null
      try {
        await collectionStore.getCollection(route.params.id)
      } catch (err) {
        error.value = 'Failed to load collection'
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    const fetchDocuments = async () => {
      documentsLoading.value = true
      documentsError.value = null
      try {
        await documentStore.getDocuments(route.params.id)
      } catch (err) {
        documentsError.value = 'Failed to load documents'
        console.error(err)
      } finally {
        documentsLoading.value = false
      }
    }

    const editCollection = () => {
      collectionForm.value = {
        name: collection.value.name,
        description: collection.value.description,
        is_public: collection.value.is_public
      }
      showEditModal.value = true
    }

    const saveCollection = async () => {
      try {
        await collectionStore.updateCollection(route.params.id, collectionForm.value)
        showEditModal.value = false
      } catch (err) {
        error.value = 'Failed to update collection'
        console.error(err)
      }
    }

    const handleFileChange = (event) => {
      documentForm.value.file = event.target.files[0]
    }

    const uploadDocument = async () => {
      try {
        const formData = new FormData()
        formData.append('title', documentForm.value.title)
        formData.append('file', documentForm.value.file)
        formData.append('collection_id', route.params.id)

        await documentStore.createDocument(formData)
        showAddDocumentModal.value = false
        documentForm.value = {
          title: '',
          file: null
        }
      } catch (err) {
        documentsError.value = 'Failed to upload document'
        console.error(err)
      }
    }

    const viewDocument = (document) => {
      router.push(`/documents/${document.id}`)
    }

    const editDocument = (document) => {
      // TODO: Implement document editing
      console.log('Edit document:', document)
    }

    const deleteDocument = (document) => {
      documentToDelete.value = document
      showDeleteModal.value = true
    }

    const confirmDelete = async () => {
      try {
        await documentStore.deleteDocument(documentToDelete.value.id)
        showDeleteModal.value = false
        documentToDelete.value = null
      } catch (err) {
        documentsError.value = 'Failed to delete document'
        console.error(err)
      }
    }

    const copyShareLink = () => {
      navigator.clipboard.writeText(shareLink.value)
    }

    const sendInvite = async () => {
      try {
        await collectionStore.inviteMember(route.params.id, inviteEmail.value)
        inviteEmail.value = ''
      } catch (err) {
        error.value = 'Failed to send invite'
        console.error(err)
      }
    }

    const getDocumentIcon = (type) => {
      const icons = {
        pdf: 'fas fa-file-pdf',
        doc: 'fas fa-file-word',
        docx: 'fas fa-file-word',
        txt: 'fas fa-file-alt',
        epub: 'fas fa-book',
        default: 'fas fa-file'
      }
      return icons[type] || icons.default
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString()
    }

    onMounted(() => {
      fetchCollection()
      fetchDocuments()
    })

    return {
      loading,
      error,
      documentsLoading,
      documentsError,
      collection,
      searchQuery,
      sortBy,
      sortOrder,
      showEditModal,
      showAddDocumentModal,
      showShareModal,
      showDeleteModal,
      collectionForm,
      documentForm,
      inviteEmail,
      shareLink,
      filteredDocuments,
      fetchCollection,
      fetchDocuments,
      editCollection,
      saveCollection,
      handleFileChange,
      uploadDocument,
      viewDocument,
      editDocument,
      deleteDocument,
      confirmDelete,
      copyShareLink,
      sendInvite,
      getDocumentIcon,
      formatFileSize,
      formatDate
    }
  }
}
</script>

<style scoped>
.collection-detail {
  padding: 2rem;
}

.collection-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--color-border);
}

.collection-info h1 {
  margin: 0 0 1rem;
  font-size: 2rem;
}

.collection-description {
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
}

.collection-meta {
  display: flex;
  gap: 1.5rem;
  color: var(--color-text-tertiary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.collection-actions {
  display: flex;
  gap: 0.5rem;
}

.document-section {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.document-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-box {
  position: relative;
}

.search-input {
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  width: 300px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-tertiary);
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
}

.document-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.document-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.document-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.document-icon {
  font-size: 2rem;
  color: var(--color-primary);
  text-align: center;
}

.document-info {
  flex: 1;
}

.document-info h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}

.document-meta {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}

.document-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.share-link {
  display: flex;
  gap: 0.5rem;
}

.invite-form {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .collection-header {
    flex-direction: column;
    gap: 1rem;
  }

  .collection-actions {
    width: 100%;
    justify-content: space-between;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .document-filters {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .share-link,
  .invite-form {
    flex-direction: column;
  }
}
</style> 
}
</style> 