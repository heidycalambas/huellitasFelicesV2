import { defineStore } from 'pinia'
import favoritosService from '@/services/favoritosService'

export const useFavoritosStore = defineStore('favoritos', {
  state: () => ({
    favoritos: [],
    favoriteIds: new Set(),
    loading: false,
    error: null,
  }),

  getters: {
    totalFavoritos: (state) => state.favoritos.length,
    isFavorito: (state) => (mascotaId) => state.favoriteIds.has(Number(mascotaId)),
  },

  actions: {
    async fetchFavoritos() {
      this.loading = true
      this.error = null
      try {
        const data = await favoritosService.getFavoritos()
        this.favoritos = data.favoritos || []
        this.favoriteIds = new Set(this.favoritos.map((f) => Number(f.id)))
        return this.favoritos
      } catch (err) {
        this.error = err.response?.data?.error || 'Error al cargar favoritos'
        return []
      } finally {
        this.loading = false
      }
    },

    async fetchIds() {
      try {
        const data = await favoritosService.getFavoritoIds()
        this.favoriteIds = new Set((data.ids || []).map(Number))
      } catch (err) {
        // silencioso
      }
    },

    async toggleFavorito(mascota) {
      const id = Number(mascota.id)
      if (this.favoriteIds.has(id)) {
        try {
          await favoritosService.eliminarFavorito(id)
          this.favoriteIds.delete(id)
          this.favoritos = this.favoritos.filter((f) => Number(f.id) !== id)
          return { success: true, isFav: false }
        } catch (err) {
          return { success: false, error: err.message }
        }
      } else {
        try {
          await favoritosService.agregarFavorito(id)
          this.favoriteIds.add(id)
          if (!this.favoritos.some((f) => Number(f.id) === id)) {
            this.favoritos.unshift(mascota)
          }
          return { success: true, isFav: true }
        } catch (err) {
          return { success: false, error: err.message }
        }
      }
    },
  },
})
