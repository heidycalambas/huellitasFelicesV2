import api from './api'

export default {
  async getHistorialMascota(mascotaId) {
    const response = await api.get(`/api/mascotas/${mascotaId}/historial-veterinario`)
    return response.data
  },

  async registrarControl(mascotaId, data) {
    const response = await api.post(`/api/mascotas/${mascotaId}/controles`, data)
    return response.data
  },

  async getTodosLosControles(params = {}) {
    const response = await api.get('/api/seguimiento/todos', { params })
    return response.data
  },

  async actualizarControl(controlId, data) {
    const response = await api.put(`/api/seguimiento/controles/${controlId}`, data)
    return response.data
  },

  async eliminarControl(controlId) {
    const response = await api.delete(`/api/seguimiento/controles/${controlId}`)
    return response.data
  },

  async getIndicadores() {
    const response = await api.get('/api/seguimiento/indicadores')
    return response.data
  },

  async getProximosControles(dias = 30) {
    const response = await api.get('/api/seguimiento/proximos-controles', { params: { dias } })
    return response.data
  },
}
