import api from './api'

export default {
  /**
   * Obtiene la lista de mascotas con filtros opcionales (tipo, ciudad, estado, etc.).
   */
  async getMascotas(params = {}) {
    const response = await api.get('/api/mascotas', { params })
    return response.data
  },

  /**
   * Obtiene el perfil completo de una mascota junto con los datos de su refugio e historial.
   */
  async getMascotaPerfil(id) {
    const response = await api.get(`/api/mascotas/${id}/perfil`)
    return response.data
  },

  /**
   * Registra una nueva mascota en la base de datos.
   */
  async crearMascota(mascotaData) {
    const response = await api.post('/api/mascotas', mascotaData)
    return response.data
  },

  /**
   * Edita una mascota existente.
   */
  async editarMascota(id, mascotaData) {
    const response = await api.put(`/api/mascotas/${id}`, mascotaData)
    return response.data
  },

  /**
   * Cambia el estado de una mascota.
   */
  async cambiarEstado(id, estado) {
    const response = await api.patch(`/api/mascotas/${id}/estado`, { estado })
    return response.data
  },

  /**
   * Elimina una mascota (solo Admin).
   */
  async eliminarMascota(id) {
    const response = await api.delete(`/api/mascotas/${id}`)
    return response.data
  },

  /**
   * Obtiene mascotas disponibles filtrando por ciudad.
   */
  async getDisponiblesPorCiudad(ciudad) {
    const response = await api.get('/api/mascotas/disponibles', { params: { ciudad } })
    return response.data
  },

  /**
   * Obtiene recomendaciones personalizadas de mascotas.
   */
  async getRecomendaciones(preferencias = {}) {
    const response = await api.post('/api/mascotas/recomendaciones', preferencias)
    return response.data
  },

  /**
   * Obtiene estadísticas de mascotas.
   */
  async getEstadisticas() {
    const response = await api.get('/api/mascotas/estadisticas')
    return response.data
  },

  /**
   * Sube una imagen localmente desde el dispositivo al servidor.
   */
  async subirFoto(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}
