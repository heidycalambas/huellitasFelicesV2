import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
const API_KEY = import.meta.env.VITE_API_KEY || 'huellitas_api_secret_key_2026'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Interceptor para peticiones: añade JWT y X-API-KEY automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('huellitas_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    if (API_KEY) {
      config.headers['X-API-KEY'] = API_KEY
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para respuestas: manejo centralizado de 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('huellitas_token')
      localStorage.removeItem('huellitas_user')

      const path = window.location.pathname || '/'
      // Solo redirigir al login si el usuario está dentro de una sección protegida
      const isProtected = path.startsWith('/app') || path.startsWith('/refugio') || path.startsWith('/admin')

      if (isProtected && !path.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
