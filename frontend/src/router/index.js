import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '@/views/LandingView.vue'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/HomeView.vue'
import RegisterView from '@/views/RegisterView.vue'
import RefugioView from '@/views/RefugioView.vue'
import AdminView from '@/views/AdminView.vue'

const routes = [
  // ── Página pública de inicio (sin autenticación requerida) ──
  {
    path: '/',
    name: 'Landing',
    component: LandingView,
    meta: { public: true },
  },

  // ── Registro de nuevos usuarios adoptantes (público) ──
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { guestOnly: true },
  },

  // ── Login (solo para usuarios no autenticados) ──
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { guestOnly: true },
  },

  // ── Panel del Adoptante (requiere autenticación) ──
  {
    path: '/app',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true, roles: ['adoptante', 'admin'] },
  },

  // ── Panel del Refugio (requiere autenticación y rol refugio o admin) ──
  {
    path: '/refugio',
    name: 'Refugio',
    component: RefugioView,
    meta: { requiresAuth: true, roles: ['refugio', 'admin'] },
  },

  // ── Panel de Administración (requiere autenticación y rol admin) ──
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },

  // ── Redirigir rutas no reconocidas al Landing ──
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

// Guardia de navegación global con roles
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('huellitas_token')
  const isAuthenticated = Boolean(token)

  let user = null
  try {
    const rawUser = localStorage.getItem('huellitas_user')
    if (rawUser) {
      user = JSON.parse(rawUser)
    }
  } catch (err) {
    console.error('Error al parsear usuario en storage:', err)
  }

  // 1. Redirigir si la ruta requiere autenticación y no hay token
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  // 2. Si es para invitados (login/register) y ya está autenticado, llevar al panel de su rol
  if (to.meta.guestOnly && isAuthenticated) {
    if (user?.rol === 'admin') {
      return next({ name: 'Admin' })
    }
    if (user?.rol === 'refugio') {
      return next({ name: 'Refugio' })
    }
    return next({ name: 'Home' })
  }

  // 3. Verificación de roles para rutas protegidas
  if (to.meta.roles && to.meta.roles.length > 0 && isAuthenticated) {
    const rol = user?.rol || 'adoptante'
    if (!to.meta.roles.includes(rol)) {
      // Redirigir según el rol del usuario para evitar accesos indebidos
      if (rol === 'admin') {
        return next({ name: 'Admin' })
      }
      if (rol === 'refugio') {
        return next({ name: 'Refugio' })
      }
      return next({ name: 'Home' })
    }
  }

  next()
})

export default router
