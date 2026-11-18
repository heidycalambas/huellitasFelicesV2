import { defineStore } from 'pinia'
import mascotasService from '@/services/mascotasService'

export const useMascotasStore = defineStore('mascotas', {
  state: () => ({
    mascotas: [],
    perfilActual: null,
    loading: false,
    loadingPerfil: false,
    error: null,
    filtros: {
      tipo: '',
      ciudad: '',
      estado: '',
      sexo: '',
      tamano: '',
      raza: '',
      search: '',
    },
  }),

  getters: {
    mascotasFiltradas: (state) => {
      return state.mascotas.filter((m) => {
        const coincideTipo = !state.filtros.tipo || state.filtros.tipo === 'Todos' || m.tipo.toLowerCase() === state.filtros.tipo.toLowerCase()
        const coincideCiudad = !state.filtros.ciudad || state.filtros.ciudad === 'Todas' || m.ciudad?.toLowerCase().includes(state.filtros.ciudad.toLowerCase())
        const coincideEstado = !state.filtros.estado || state.filtros.estado === 'Todos' || m.estado === state.filtros.estado
        const coincideSexo = !state.filtros.sexo || state.filtros.sexo === 'Todos' || m.sexo?.toLowerCase() === state.filtros.sexo.toLowerCase()
        const coincideTamano = !state.filtros.tamano || state.filtros.tamano === 'Todos' || m.tamano?.toLowerCase() === state.filtros.tamano.toLowerCase()
        const coincideSearch = !state.filtros.search ||
          m.nombre?.toLowerCase().includes(state.filtros.search.toLowerCase()) ||
          m.raza?.toLowerCase().includes(state.filtros.search.toLowerCase())
        return coincideTipo && coincideCiudad && coincideEstado && coincideSexo && coincideTamano && coincideSearch
      })
    },
    totalDisponibles: (state) => {
      return state.mascotas.filter((m) => m.estado === 'Disponible').length
    },
    totalAdoptadas: (state) => {
      return state.mascotas.filter((m) => m.estado === 'Adoptada').length
    },
  },

  actions: {
    async fetchMascotas(params = {}) {
      this.loading = true
      this.error = null
      try {
        const data = await mascotasService.getMascotas(params)
        this.mascotas = data.mascotas || []
        return this.mascotas
      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'No se pudieron cargar las mascotas desde el servidor'
        return []
      } finally {
        this.loading = false
      }
    },

    async fetchPerfil(id) {
      this.loadingPerfil = true
      this.perfilActual = null
      try {
        const data = await mascotasService.getMascotaPerfil(id)
        this.perfilActual = data
        return data
      } catch (err) {
        this.error = err.response?.data?.error || 'Error al obtener el perfil de la mascota'
        return null
      } finally {
        this.loadingPerfil = false
      }
    },

    async registrarMascota(mascotaData) {
      try {
        const response = await mascotasService.crearMascota(mascotaData)
        await this.fetchMascotas()
        return { success: true, data: response }
      } catch (err) {
        const errorMsg =
          err.response?.data?.error ||
          'Error al registrar la mascota en la base de datos'
        return { success: false, error: errorMsg }
      }
    },

    async editarMascota(id, mascotaData) {
      try {
        const response = await mascotasService.editarMascota(id, mascotaData)
        await this.fetchMascotas()
        return { success: true, data: response }
      } catch (err) {
        return { success: false, error: err.response?.data?.error || 'Error al actualizar mascota' }
      }
    },

    async cambiarEstadoMascota(id, estado) {
      try {
        const res = await mascotasService.cambiarEstado(id, estado)
        await this.fetchMascotas()
        return { success: true, data: res }
      } catch (err) {
        return { success: false, error: err.response?.data?.error || 'Error al cambiar estado' }
      }
    },

    async eliminarMascota(id) {
      try {
        await mascotasService.eliminarMascota(id)
        this.mascotas = this.mascotas.filter((m) => m.id !== id)
        return { success: true }
      } catch (err) {
        return { success: false, error: err.response?.data?.error || 'Error al eliminar mascota' }
      }
    },

    setFiltroTipo(tipo) {
      this.filtros.tipo = tipo
    },

    setFiltroCiudad(ciudad) {
      this.filtros.ciudad = ciudad
    },

    setFiltroEstado(estado) {
      this.filtros.estado = estado
    },

    limpiarFiltros() {
      this.filtros = {
        tipo: '',
        ciudad: '',
        estado: '',
        sexo: '',
        tamano: '',
        raza: '',
        search: '',
      }
    },
  },
})
