import api from './api'

export default {
  async getEstadisticas() {
    const response = await api.get('/api/admin/estadisticas')
    return response.data
  },

  async getActividad() {
    const response = await api.get('/api/admin/actividad')
    return response.data
  },
}
