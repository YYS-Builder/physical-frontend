import type { DefineComponent } from 'vue'
import type { RouterLink, RouterView } from 'vue-router'

declare module 'vue' {
  export type GlobalComponents = {
    RouterLink: typeof RouterLink
    RouterView: typeof RouterView
  }

  export interface ComponentCustomProperties {
    $router: import('vue-router').Router
    $route: import('vue-router').RouteLocationNormalized
  }
}

declare module '*.vue' {
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Augment the global scope
declare global {
  interface Window {
    __VUE_DEVTOOLS_GLOBAL_HOOK__: any
  }
} 