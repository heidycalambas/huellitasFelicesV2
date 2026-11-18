import { defineStore } from 'pinia'
import adopcionesService from '@/services/adopcionesService'
import { useAuthStore } from './authStore'

export const useAdopcionesStore = defineStore('adopciones', {
  state: () => ({
    solicitudes: [],
    entrevistas: [],
    loading: false,
    loadingEntrevistas: false,
    submitting: false,
    error: null,
    successMessage: null,
  }),

  getters: {
    totalSolicitudes: (state) => state.solicitudes.length,
    solicitudesEnRevision: (state) =>
      state.solicitudes.filter((s) => s.estado === 'En revisión').length,
    solicitudesAprobadas: (state) =>
      state.solicitudes.filter((s) => s.estado === 'Aprobada').length,
    totalEntrevistas: (state) => state.entrevistas.length,
    entrevistasProgramadas: (state) =>
      state.entrevistas.filter((e) => e.estado === 'Programada').length,
  },

  actions: {
    async fetchSolicitudes(params = {}) {
      const authStore = useAuthStore()
      this.loading = true
      this.error = null
      try {
        const queryParams = { ...params }
        if (authStore.isAdoptante && authStore.user?.id) {
          queryParams.usuario_id = authStore.user.id
        } else if (authStore.isRefugio && authStore.user?.refugio_id) {
          queryParams.refugio_id = authStore.user.refugio_id
        }
        const data = await adopcionesService.getSolicitudes(queryParams)
        this.solicitudes = data.adopciones || []
        return this.solicitudes
      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Error al cargar las solicitudes de adopción'
        return []
      } finally {
        this.loading = false
      }
    },

    async fetchEntrevistas(params = {}) {
      this.loadingEntrevistas = true
      try {
        const data = await adopcionesService.getEntrevistas(params)
        this.entrevistas = data.entrevistas || []
        return this.entrevistas
      } catch (err) {
        return []
      } finally {
        this.loadingEntrevistas = false
      }
    },

    async crearSolicitud(solicitudData) {
      this.submitting = true
      this.error = null
      this.successMessage = null
      try {
        const response = await adopcionesService.crearSolicitud(solicitudData)
        this.successMessage = response.mensaje || '¡Solicitud registrada correctamente!'
        await this.fetchSolicitudes()
        return { success: true, data: response }
      } catch (err) {
        const errorMsg =
          err.response?.data?.error ||
          'No se pudo registrar la solicitud de adopción'
        this.error = errorMsg
        return { success: false, error: errorMsg }
      } finally {
        this.submitting = false
      }
    },

    async actualizarEstadoSolicitud(id, nuevoEstado) {
      try {
        const res = await adopcionesService.actualizarEstado(id, nuevoEstado)
        await this.fetchSolicitudes()
        return { success: true, data: res }
      } catch (err) {
        return { success: false, error: err.response?.data?.error || 'Error al actualizar estado' }
      }
    },

    async programarEntrevista(adopcionId, data) {
      try {
        const res = await adopcionesService.programarEntrevista(adopcionId, data)
        await this.fetchSolicitudes()
        await this.fetchEntrevistas()
        return { success: true, data: res }
      } catch (err) {
        return { success: false, error: err.response?.data?.error || 'Error al programar entrevista' }
      }
    },

    async actualizarEntrevista(id, data) {
      try {
        const res = await adopcionesService.actualizarEntrevista(id, data)
        await this.fetchEntrevistas()
        return { success: true, data: res }
      } catch (err) {
        return { success: false, error: err.response?.data?.error || 'Error al actualizar entrevista' }
      }
    },

    limpiarMensajes() {
      this.error = null
      this.successMessage = null
    },
  },
})
