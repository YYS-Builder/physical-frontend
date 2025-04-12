<template>
  <div class="collection-list">
    <div class="header">
      <h1>Collections</h1>
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search collections..."
          class="search-input"
        />
        <button class="btn-create" @click="showCreateModal = true">
          <i class="fas fa-plus"></i> New Collection
        </button>
      </div>
    </div>

    <div class="filters">
      <select v-model="sortBy" class="filter-select">
        <option value="name">Sort by Name</option>
        <option value="createdAt">Sort by Date Created</option>
        <option value="updatedAt">Sort by Last Updated</option>
      </select>
      <select v-model="privacyFilter" class="filter-select">
        <option value="all">All Privacy Settings</option>
        <option value="public">Public</option>
        <option value="private">Private</option>
      </select>
    </div>

    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading collections...
    </div>

    <div v-else-if="error" class="error">
      <i class="fas fa-exclamation-circle"></i> {{ error }}
    </div>

    <div v-else-if="filteredCollections.length === 0" class="empty-state">
      <i class="fas fa-folder-open"></i>
      <p>No collections found</p>
      <button class="btn-create" @click="showCreateModal = true">
        Create your first collection
      </button>
    </div>

    <RecycleScroller
      v-else
      class="collections-grid"
      :items="filteredCollections"
      :item-size="300"
      key-field="id"
    >
      <template #default="{ item }">
        <div class="collection-card">
          <div class="card-header">
            <h3>{{ item.name }}</h3>
            <div class="privacy-badge" :class="item.isPublic ? 'public' : 'private'">
              {{ item.isPublic ? 'Public' : 'Private' }}
            </div>
          </div>
          <p class="description">{{ item.description }}</p>
          <div class="stats">
            <div class="stat">
              <i class="fas fa-file"></i>
              <span>{{ item.documentCount }} documents</span>
            </div>
            <div class="stat">
              <i class="fas fa-users"></i>
              <span>{{ item.memberCount }} members</span>
            </div>
          </div>
          <div class="actions">
            <button class="btn-view" @click="viewCollection(item)">
              <i class="fas fa-eye"></i> View
            </button>
            <button class="btn-edit" @click="editCollection(item)">
              <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn-delete" @click="confirmDelete(item)">
              <i class="fas fa-trash"></i> Delete
            </button>
          </div>
        </div>
      </template>
    </RecycleScroller>

    <!-- Create/Edit Collection Modal -->
    <Modal
      v-model="showCreateModal"
      :title="editingCollection ? 'Edit Collection' : 'Create Collection'"
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
            @click="showCreateModal = false"
            class="btn btn-outline"
          >
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            {{ editingCollection ? 'Save Changes' : 'Create Collection' }}
          </button>
        </div>
      </form>
    </Modal>

    <!-- Delete Confirmation Modal -->
    <Modal
      v-model="showDeleteModal"
      title="Delete Collection"
    >
      <p>Are you sure you want to delete this collection? This action cannot be undone.</p>
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

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCollectionStore } from '@/stores/collections'
import Modal from '@/components/common/Modal.vue'
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'

const router = useRouter()
const store = useCollectionStore()
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const sortBy = ref('updatedAt')
const sortOrder = ref('desc')
const privacyFilter = ref('all')
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const editingCollection = ref(null)
const collectionToDelete = ref(null)

const collectionForm = ref({
  name: '',
  description: '',
  is_public: false
})

const filteredCollections = computed(() => {
  let collections = store.collections

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    collections = collections.filter(collection =>
      collection.name.toLowerCase().includes(query) ||
      collection.description.toLowerCase().includes(query)
    )
  }

  // Apply privacy filter
  if (privacyFilter.value !== 'all') {
    collections = collections.filter(collection =>
      privacyFilter.value === 'public' ? collection.is_public : !collection.is_public
    )
  }

  // Apply sorting
  collections.sort((a, b) => {
    let comparison = 0
    if (sortBy.value === 'name') {
      comparison = a.name.localeCompare(b.name)
    } else if (sortBy.value === 'document_count') {
      comparison = a.document_count - b.document_count
    } else {
      comparison = new Date(a[sortBy.value]) - new Date(b[sortBy.value])
    }
    return sortOrder.value === 'asc' ? comparison : -comparison
  })

  return collections
})

const fetchCollections = async () => {
  loading.value = true
  error.value = null
  try {
    await store.getCollections()
  } catch (err) {
    error.value = 'Failed to load collections'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const viewCollection = (collection) => {
  router.push(`/collections/${collection.id}`)
}

const editCollection = (collection) => {
  editingCollection.value = collection
  collectionForm.value = {
    name: collection.name,
    description: collection.description,
    is_public: collection.is_public
  }
  showCreateModal.value = true
}

const saveCollection = async () => {
  try {
    if (editingCollection.value) {
      await store.updateCollection(editingCollection.value.id, collectionForm.value)
    } else {
      await store.createCollection(collectionForm.value)
    }
    showCreateModal.value = false
    editingCollection.value = null
    collectionForm.value = {
      name: '',
      description: '',
      is_public: false
    }
  } catch (err) {
    error.value = 'Failed to save collection'
    console.error(err)
  }
}

const deleteCollection = (collection) => {
  collectionToDelete.value = collection
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  try {
    await store.deleteCollection(collectionToDelete.value.id)
    showDeleteModal.value = false
    collectionToDelete.value = null
  } catch (err) {
    error.value = 'Failed to delete collection'
    console.error(err)
  }
}

onMounted(() => {
  fetchCollections()
})
</script>

<style scoped>
.collections-grid {
  height: calc(100vh - 200px);
  width: 100%;
}

.collection-card {
  height: 300px;
  margin: 1rem;
}

.collection-list {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
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

.btn-create {
  padding: 0.5rem 1rem;
  border: none;
  background-color: var(--color-primary);
  color: var(--color-background);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-create:hover {
  background-color: var(--color-primary-hover);
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.collection-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-input {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }

  .filters {
    flex-direction: column;
  }

  .collections-grid {
    grid-template-columns: 1fr;
  }
}
</style> 