import { createRouter, createWebHistory } from 'vue-router'

const HOME_SCROLL_KEY = 'home_scroll_y'
const HOME_RESTORE_KEY = 'home_restore_scroll'

if ('scrollRestoration' in window.history) {
  window.history.scrollRestoration = 'manual'
}

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/chat', name: 'AIChat', component: () => import('../views/AIChat.vue') },
  { path: '/projects', name: 'Projects', component: () => import('../views/Projects.vue') },
  { path: '/project/:id', name: 'ProjectDetail', component: () => import('../views/ProjectDetail.vue') },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (to.name === 'Home') {
      if (from.name && from.name !== 'Home') {
        const savedHomeY = Number(sessionStorage.getItem(HOME_SCROLL_KEY) || 0)
        return { left: 0, top: savedHomeY }
      }

      return { left: 0, top: 0 }
    }

    if (savedPosition) return savedPosition

    return { left: 0, top: 0 }
  },
})

router.beforeEach((to, from) => {
  if (to.name === 'Home') {
    if (from.name && from.name !== 'Home') {
      sessionStorage.setItem(HOME_RESTORE_KEY, '1')
    } else {
      sessionStorage.removeItem(HOME_RESTORE_KEY)
    }
  }
})

export default router
