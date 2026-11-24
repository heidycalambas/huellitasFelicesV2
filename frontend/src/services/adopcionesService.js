import api from './api'

export default {
  /**
   * Registra una nueva solicitud de adopción.
   */
  async crearSolicitud(solicitudData) {
    const response = await api.post('/api/adopciones', solicitudData)
    return response.data
  },

  /**
   * Consulta las solicitudes de adopción (opcionalmente por usuario o refugio).
   */
  async getSolicitudes(params = {}) {
    const response = await api.get('/api/adopciones', { params })
    return response.data
  },

  /**
   * Consulta las solicitudes pendientes.
   */
  async getPendientes() {
    const response = await api.get('/api/adopciones/pendientes')
    return response.data
  },

  /**
   * Consulta el detalle de una solicitud específica.
   */
  async getAdopcion(id) {
    const response = await api.get(`/api/adopciones/${id}`)
    return response.data
  },

  /**
   * Actualiza el estado de una solicitud de adopción.
   */
  async actualizarEstado(id, estado) {
    const response = await api.patch(`/api/adopciones/${id}/estado`, { estado })
    return response.data
  },

  /**
   * Programa una entrevista para una solicitud de adopción.
   */
  async programarEntrevista(adopcionId, entrevistaData) {
    const response = await api.post(`/api/adopciones/${adopcionId}/entrevista`, entrevistaData)
    return response.data
  },

  /**
   * Consulta entrevistas programadas o históricas.
   */
  async getEntrevistas(params = {}) {
    const response = await api.get('/api/entrevistas', { params })
    return response.data
  },

  /**
   * Actualiza una entrevista.
   */
  async actualizarEntrevista(id, entrevistaData) {
    const response = await api.patch(`/api/entrevistas/${id}`, entrevistaData)
    return response.data
  },
}
