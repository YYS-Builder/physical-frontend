import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { performanceService } from './services/performance'

// Import global styles
import './styles/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Start performance monitoring
performanceService.startMonitoring()

app.mount('#app') 