import { defineStore } from 'pinia'
import authService from '@/services/authService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('huellitas_token') || null,
    user: JSON.parse(localStorage.getItem('huellitas_user') || 'null'),
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    currentUser: (state) => state.user,
    userRole: (state) => state.user?.rol || 'adoptante',
    isAdmin: (state) => state.user?.rol === 'admin',
    isRefugio: (state) => state.user?.rol === 'refugio',
    isAdoptante: (state) => !state.user?.rol || state.user?.rol === 'adoptante',
    userName: (state) => state.user?.nombre || state.user?.usuario || 'Usuario',
  },

  actions: {
    async login(usuario, password) {
      this.loading = true
      this.error = null
      try {
        const data = await authService.login(usuario, password)
        this.token = data.token
        this.user = data.usuario

        localStorage.setItem('huellitas_token', data.token)
        localStorage.setItem('huellitas_user', JSON.stringify(data.usuario))

        return { success: true, user: data.usuario }
      } catch (err) {
        const errorMsg =
          err.response?.data?.error ||
          'Error al conectar con el servidor. Verifica que el backend esté activo.'
        this.error = errorMsg
        return { success: false, error: errorMsg }
      } finally {
        this.loading = false
      }
    },

    async register(datosUsuario) {
      this.loading = true
      this.error = null
      try {
        const data = await authService.register(datosUsuario)
        return { success: true, data }
      } catch (err) {
        const errorMsg =
          err.response?.data?.error ||
          'No se pudo completar el registro. Intenta con otro usuario o verifica la conexión.'
        this.error = errorMsg
        return { success: false, error: errorMsg }
      } finally {
        this.loading = false
      }
    },

    async fetchPerfil() {
      try {
        const data = await authService.getPerfil()
        if (data) {
          this.user = { ...this.user, ...data }
          localStorage.setItem('huellitas_user', JSON.stringify(this.user))
        }
        return data
      } catch (err) {
        return null
      }
    },

    async updatePerfil(datos) {
      this.loading = true
      this.error = null
      try {
        const res = await authService.updatePerfil(datos)
        if (res.usuario) {
          this.user = { ...this.user, ...res.usuario }
          localStorage.setItem('huellitas_user', JSON.stringify(this.user))
        }
        return { success: true, data: res.usuario }
      } catch (err) {
        const errorMsg = err.response?.data?.error || 'Error al actualizar el perfil'
        this.error = errorMsg
        return { success: false, error: errorMsg }
      } finally {
        this.loading = false
      }
    },

    async checkAuth() {
      if (!this.token) return false
      try {
        await authService.verificarSesion()
        return true
      } catch (err) {
        this.logout()
        return false
      }
    },

    logout() {
      this.token = null
      this.user = null
      this.error = null
      localStorage.removeItem('huellitas_token')
      localStorage.removeItem('huellitas_user')
    },
  },
})
