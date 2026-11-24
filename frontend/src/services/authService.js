import api from './api'

export default {
  /**
   * Inicia sesión con usuario y contraseña.
   */
  async login(usuario, password) {
    const response = await api.post('/auth/login', { usuario, password })
    return response.data
  },

  /**
   * Registra un nuevo usuario adoptante.
   */
  async register(datosUsuario) {
    const response = await api.post('/auth/register', datosUsuario)
    return response.data
  },

  /**
   * Verifica la validez del token actual.
   */
  async verificarSesion() {
    const response = await api.get('/auth/me')
    return response.data
  },

  /**
   * Obtiene el perfil completo del usuario autenticado.
   */
  async getPerfil() {
    const response = await api.get('/api/usuarios/perfil')
    return response.data
  },

  /**
   * Actualiza el perfil del usuario autenticado.
   */
  async updatePerfil(datos) {
    const response = await api.put('/api/usuarios/perfil', datos)
    return response.data
  },

  /**
   * Consulta todos los usuarios (solo Admin).
   */
  async getUsuarios(params = {}) {
    const response = await api.get('/api/usuarios', { params })
    return response.data
  },

  /**
   * Edita usuario por ID (solo Admin).
   */
  async updateUsuario(id, datos) {
    const response = await api.put(`/api/usuarios/${id}`, datos)
    return response.data
  },

  /**
   * Activa o desactiva la cuenta de un usuario (solo Admin).
   */
  async toggleEstadoUsuario(id) {
    const response = await api.patch(`/api/usuarios/${id}/estado`)
    return response.data
  },
}
