import api from './api'

export default {
  async getFavoritos() {
    const response = await api.get('/api/favoritos')
    return response.data
  },

  async getFavoritoIds() {
    const response = await api.get('/api/favoritos/ids')
    return response.data
  },

  async agregarFavorito(mascotaId) {
    const response = await api.post(`/api/favoritos/${mascotaId}`)
    return response.data
  },

  async eliminarFavorito(mascotaId) {
    const response = await api.delete(`/api/favoritos/${mascotaId}`)
    return response.data
  },
}
