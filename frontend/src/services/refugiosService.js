import api from './api'

export default {
  async getRefugios() {
    const response = await api.get('/api/refugios')
    return response.data
  },

  async getRefugio(id) {
    const response = await api.get(`/api/refugios/${id}`)
    return response.data
  },

  async getMiRefugio() {
    const response = await api.get('/api/refugios/mi-refugio')
    return response.data
  },

  async actualizarMiRefugio(data) {
    const response = await api.put('/api/refugios/mi-refugio', data)
    return response.data
  },

  async crearRefugio(data) {
    const response = await api.post('/api/refugios', data)
    return response.data
  },

  async actualizarRefugio(id, data) {
    const response = await api.put(`/api/refugios/${id}`, data)
    return response.data
  },
}
