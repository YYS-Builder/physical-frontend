import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy-loaded components
const Home = () => import('@/pages/Home.vue')
const Login = () => import('@/pages/Login.vue')
const Register = () => import('@/pages/Register.vue')
const Dashboard = () => import('@/pages/Dashboard.vue')
const Documents = () => import('@/pages/Documents.vue')
const Collections = () => import('@/pages/Collections.vue')
const Analytics = () => import('@/pages/Analytics.vue')
const Profile = () => import('@/pages/Profile.vue')
const DocumentViewer = () => import('@/pages/DocumentViewer.vue')
const NotFound = () => import('@/pages/NotFound.vue')
const DocumentView = () => import('@/pages/DocumentView.vue')
const CollectionView = () => import('@/pages/CollectionView.vue')
const UserProfile = () => import('@/pages/UserProfile.vue')
const Settings = () => import('@/pages/Settings.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'Home',
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/documents',
    name: 'Documents',
    component: Documents,
    meta: { requiresAuth: true }
  },
  {
    path: '/collections',
    name: 'Collections',
    component: Collections,
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: {
      title: 'Analytics',
      requiresAuth: true
    }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: {
      title: 'Profile',
      requiresAuth: true
    }
  },
  {
    path: '/documents/:id',
    name: 'DocumentView',
    component: DocumentView,
    meta: {
      title: 'Document',
      requiresAuth: true
    }
  },
  {
    path: '/collections/:id',
    name: 'CollectionView',
    component: CollectionView,
    meta: {
      title: 'Collection',
      requiresAuth: true
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: 'Settings',
      requiresAuth: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: 'Not Found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  // Update document title
  document.title = `${to.meta.title} | Reader`

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

// Error handling
router.onError((error) => {
  console.error('Router error:', error)
  // Handle chunk loading errors
  if (/loading chunk \d+ failed/i.test(error.message)) {
    window.location.reload()
  }
})

export default router 