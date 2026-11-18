<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import adminService from '@/services/adminService'
import authService from '@/services/authService'
import refugiosService from '@/services/refugiosService'
import mascotasService from '@/services/mascotasService'
import adopcionesService from '@/services/adopcionesService'
import veterinarioService from '@/services/veterinarioService'
import PetDetailModal from '@/components/PetDetailModal.vue'
import {
  Heart,
  BarChart3,
  Users,
  Building,
  Folder,
  Inbox,
  Video,
  Award,
  Stethoscope,
  PieChart,
  Settings,
  LogOut,
  Search,
  PlusCircle,
  Edit,
  Trash2,
  Check,
  X,
  AlertCircle,
  Eye,
  RefreshCw,
  Power,
  ShieldCheck,
  Calendar,
  Clock,
  MapPin,
  Phone,
  Mail,
  UserCheck,
  Upload,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

// Tabs del Administrador (11 secciones requeridas)
// 1. Dashboard | 2. Usuarios | 3. Refugios | 4. Mascotas | 5. Solicitudes | 6. Entrevistas | 7. Adopciones | 8. Historial Vet | 9. Estadísticas | 10. Configuración | 11. Logout
const activeTab = ref('dashboard')

// Estado de indicadores y listas
const estadisticas = ref({
  total_usuarios: 0,
  total_adoptantes: 0,
  total_refugios: 0,
  total_mascotas: 0,
  mascotas_disponibles: 0,
  mascotas_adoptadas: 0,
  perros: 0,
  gatos: 0,
  solicitudes_recibidas: 0,
  solicitudes_pendientes: 0,
  adopciones_realizadas: 0,
  entrevistas_programadas: 0,
  solicitudes_por_estado: [],
  mascotas_por_ciudad: [],
  adopciones_por_mes: [],
})

const actividadReciente = ref([])
const usuariosList = ref([])
const refugiosList = ref([])
const mascotasList = ref([])
const solicitudesList = ref([])
const entrevistasList = ref([])
const historialesList = ref([])

// Filtros y búsquedas
const userSearch = ref('')
const userRoleFilter = ref('Todos')
const petSearch = ref('')
const petStatusFilter = ref('Todos')

// Modales de administración
const showUserModal = ref(false)
const showRefugioModal = ref(false)
const showMascotaModal = ref(false)
const showPetDetail = ref(false)
const selectedPetProfile = ref(null)

// Formularios
const userForm = reactive({
  id: null,
  nombre: '',
  usuario: '',
  edad: 25,
  ciudad: 'Popayán',
  rol: 'adoptante',
  password: '',
})

const refugioForm = reactive({
  id: null,
  nombre: '',
  ciudad: 'Popayán',
  direccion: '',
  telefono: '',
  email: '',
  usuario_id: null,
})

const mascotaForm = reactive({
  id: null,
  refugio_id: 1,
  nombre: '',
  tipo: 'Perro',
  edad: 2,
  sexo: 'Macho',
  tamano: 'Mediano',
  raza: 'Criollo',
  ciudad: 'Popayán',
  descripcion: '',
  personalidad: 'Cariñoso y leal',
  nivel_energia: 'Media',
  compatible_ninos: true,
  compatible_mascotas: true,
  vacunado: true,
  desparasitado: true,
  esterilizado: true,
  estado: 'Disponible',
  foto_url: '',
})

// Feedback
const feedback = reactive({ type: null, text: '' })
function showMsg(text, type = 'success') {
  feedback.text = text
  feedback.type = type
  setTimeout(() => { feedback.type = null; feedback.text = '' }, 4000)
}

onMounted(async () => {
  await cargarTodo()
})

async function cargarTodo() {
  await Promise.all([
    cargarEstadisticas(),
    cargarActividad(),
    cargarUsuarios(),
    cargarRefugios(),
    cargarMascotas(),
    cargarSolicitudes(),
    cargarEntrevistas(),
    cargarHistoriales(),
  ])
}

async function cargarEstadisticas() {
  try {
    const data = await adminService.getEstadisticas()
    if (data) estadisticas.value = { ...estadisticas.value, ...data }
  } catch (err) {}
}

async function cargarActividad() {
  try {
    const data = await adminService.getActividad()
    actividadReciente.value = data.actividad || []
  } catch (err) {}
}

async function cargarUsuarios() {
  try {
    const data = await authService.getUsuarios()
    usuariosList.value = data.usuarios || []
  } catch (err) {}
}

async function cargarRefugios() {
  try {
    const data = await refugiosService.getRefugios()
    refugiosList.value = data.refugios || []
  } catch (err) {}
}

async function cargarMascotas() {
  try {
    const data = await mascotasService.getMascotas()
    mascotasList.value = data.mascotas || []
  } catch (err) {}
}

async function cargarSolicitudes() {
  try {
    const data = await adopcionesService.getSolicitudes()
    solicitudesList.value = data.adopciones || []
  } catch (err) {}
}

async function cargarEntrevistas() {
  try {
    const data = await adopcionesService.getEntrevistas()
    entrevistasList.value = data.entrevistas || []
  } catch (err) {}
}

async function cargarHistoriales() {
  try {
    const data = await veterinarioService.getTodosLosControles()
    historialesList.value = data.historial || []
  } catch (err) {}
}

// ── GESTIÓN DE USUARIOS ──
const usuariosFiltrados = computed(() => {
  return usuariosList.value.filter((u) => {
    if (userRoleFilter.value !== 'Todos' && u.rol !== userRoleFilter.value) return false
    if (userSearch.value.trim()) {
      const q = userSearch.value.toLowerCase().trim()
      const matchName = u.nombre?.toLowerCase().includes(q)
      const matchUser = u.usuario?.toLowerCase().includes(q)
      const matchCity = u.ciudad?.toLowerCase().includes(q)
      if (!matchName && !matchUser && !matchCity) return false
    }
    return true
  })
})

function abrirEditarUsuario(u) {
  userForm.id = u.id
  userForm.nombre = u.nombre
  userForm.usuario = u.usuario
  userForm.edad = u.edad
  userForm.ciudad = u.ciudad
  userForm.rol = u.rol
  userForm.password = ''
  showUserModal.value = true
}

async function guardarUsuario() {
  try {
    const payload = { ...userForm }
    if (!payload.password) delete payload.password
    await authService.updateUsuario(userForm.id, payload)
    showMsg('Usuario actualizado con éxito')
    showUserModal.value = false
    await cargarUsuarios()
  } catch (err) {
    showMsg(err.response?.data?.error || 'Error al actualizar usuario', 'error')
  }
}

async function toggleEstadoCuenta(userId) {
  try {
    const res = await authService.toggleEstadoUsuario(userId)
    showMsg(res.mensaje || 'Estado de cuenta actualizado')
    await cargarUsuarios()
  } catch (err) {
    showMsg('Error al cambiar estado de la cuenta', 'error')
  }
}

// ── GESTIÓN DE REFUGIOS ──
function abrirCrearRefugio() {
  refugioForm.id = null
  refugioForm.nombre = ''
  refugioForm.ciudad = 'Popayán'
  refugioForm.direccion = ''
  refugioForm.telefono = ''
  refugioForm.email = ''
  refugioForm.usuario_id = null
  showRefugioModal.value = true
}

function abrirEditarRefugio(r) {
  refugioForm.id = r.id
  refugioForm.nombre = r.nombre
  refugioForm.ciudad = r.ciudad
  refugioForm.direccion = r.direccion
  refugioForm.telefono = r.telefono
  refugioForm.email = r.email
  refugioForm.usuario_id = r.usuario_id
  showRefugioModal.value = true
}

async function guardarRefugio() {
  if (!refugioForm.nombre.trim() || !refugioForm.ciudad.trim()) {
    showMsg('Nombre y ciudad son obligatorios', 'error')
    return
  }

  try {
    if (refugioForm.id) {
      await refugiosService.actualizarRefugio(refugioForm.id, refugioForm)
      showMsg('Refugio actualizado correctamente')
    } else {
      await refugiosService.crearRefugio(refugioForm)
      showMsg('Refugio registrado con éxito')
    }
    showRefugioModal.value = false
    await Promise.all([cargarRefugios(), cargarEstadisticas()])
  } catch (err) {
    showMsg(err.response?.data?.error || 'Error al guardar refugio', 'error')
  }
}

// ── GESTIÓN DE MASCOTAS ──
const mascotasFiltradasAdmin = computed(() => {
  return mascotasList.value.filter((m) => {
    if (petStatusFilter.value !== 'Todos' && m.estado !== petStatusFilter.value) return false
    if (petSearch.value.trim()) {
      const q = petSearch.value.toLowerCase().trim()
      const matchName = m.nombre?.toLowerCase().includes(q)
      const matchBreed = m.raza?.toLowerCase().includes(q)
      const matchCity = m.ciudad?.toLowerCase().includes(q)
      if (!matchName && !matchBreed && !matchCity) return false
    }
    return true
  })
})

function abrirCrearMascota() {
  mascotaForm.id = null
  mascotaForm.refugio_id = refugiosList.value[0]?.id || 1
  mascotaForm.nombre = ''
  mascotaForm.tipo = 'Perro'
  mascotaForm.edad = 2
  mascotaForm.sexo = 'Macho'
  mascotaForm.tamano = 'Mediano'
  mascotaForm.raza = 'Criollo'
  mascotaForm.ciudad = 'Popayán'
  mascotaForm.descripcion = ''
  mascotaForm.personalidad = 'Cariñoso y sociable'
  mascotaForm.nivel_energia = 'Media'
  mascotaForm.compatible_ninos = true
  mascotaForm.compatible_mascotas = true
  mascotaForm.vacunado = true
  mascotaForm.desparasitado = true
  mascotaForm.esterilizado = true
  mascotaForm.estado = 'Disponible'
  mascotaForm.foto_url = ''
  showMascotaModal.value = true
}

function abrirEditarMascota(m) {
  mascotaForm.id = m.id
  mascotaForm.refugio_id = m.refugio_id || 1
  mascotaForm.nombre = m.nombre
  mascotaForm.tipo = m.tipo
  mascotaForm.edad = m.edad
  mascotaForm.sexo = m.sexo
  mascotaForm.tamano = m.tamano
  mascotaForm.raza = m.raza
  mascotaForm.ciudad = m.ciudad
  mascotaForm.descripcion = m.descripcion
  mascotaForm.personalidad = m.personalidad
  mascotaForm.nivel_energia = m.nivel_energia
  mascotaForm.compatible_ninos = Boolean(m.compatible_ninos)
  mascotaForm.compatible_mascotas = Boolean(m.compatible_mascotas)
  mascotaForm.vacunado = Boolean(m.vacunado)
  mascotaForm.desparasitado = Boolean(m.desparasitado)
  mascotaForm.esterilizado = Boolean(m.esterilizado)
  mascotaForm.estado = m.estado
  mascotaForm.foto_url = m.foto_url || ''
  showMascotaModal.value = true
}

async function guardarMascotaAdmin() {
  if (!mascotaForm.nombre.trim()) {
    showMsg('Nombre de mascota es obligatorio', 'error')
    return
  }

  try {
    const payload = { ...mascotaForm, edad: Number(mascotaForm.edad) }
    if (mascotaForm.id) {
      await mascotasService.editarMascota(mascotaForm.id, payload)
      showMsg('Mascota actualizada correctamente')
    } else {
      await mascotasService.crearMascota(payload)
      showMsg('Mascota registrada exitosamente')
    }
    showMascotaModal.value = false
    await Promise.all([cargarMascotas(), cargarEstadisticas()])
  } catch (err) {
    showMsg('Error al guardar datos de mascota', 'error')
  }
}

async function eliminarMascotaAdmin(id) {
  if (!confirm(`¿Estás seguro de eliminar permanentemente la mascota #${id}?`)) return
  try {
    await mascotasService.eliminarMascota(id)
    showMsg(`Mascota #${id} eliminada`)
    await Promise.all([cargarMascotas(), cargarEstadisticas()])
  } catch (err) {
    showMsg('Error al eliminar mascota', 'error')
  }
}

// ── GESTIÓN DE SOLICITUDES Y ADOPCIONES ──
async function cambiarEstadoSolicitudAdmin(solicitudId, nuevoEstado) {
  try {
    await adopcionesService.actualizarEstado(solicitudId, nuevoEstado)
    showMsg(`Solicitud #${solicitudId} actualizada a "${nuevoEstado}"`)
    await Promise.all([cargarSolicitudes(), cargarMascotas(), cargarEstadisticas()])
  } catch (err) {
    showMsg(err.response?.data?.error || 'Error al actualizar estado administrativo', 'error')
  }
}

async function verDetalleMascota(mascotaId) {
  const p = await mascotasService.getMascotaPerfil(mascotaId)
  if (p) {
    selectedPetProfile.value = p
    showPetDetail.value = true
  }
}

// Gestión de Historial Veterinario por Admin
const showVeterinarioModal = ref(false)
const controlForm = reactive({
  mascota_id: '',
  tipo: 'Vacuna',
  descripcion: '',
  fecha: new Date().toISOString().substring(0, 10),
  proxima_fecha: '',
  veterinario: 'Dr. Camilo Muñoz - MV',
  observaciones: '',
})

function abrirNuevoControlAdmin() {
  if (mascotasList.value.length > 0) {
    controlForm.mascota_id = mascotasList.value[0].id
  }
  controlForm.tipo = 'Vacuna'
  controlForm.descripcion = 'Vacuna antirrábica y polivalente anual'
  controlForm.fecha = new Date().toISOString().substring(0, 10)
  controlForm.proxima_fecha = ''
  controlForm.veterinario = 'Dr. Camilo Muñoz - MV'
  controlForm.observaciones = 'Mascota evaluada en óptimas condiciones'
  showVeterinarioModal.value = true
}

async function guardarControlAdmin() {
  if (!controlForm.mascota_id) {
    showMsg('Debes seleccionar una mascota', 'error')
    return
  }
  if (!controlForm.descripcion.trim()) {
    showMsg('La descripción es obligatoria', 'error')
    return
  }

  try {
    await veterinarioService.registrarControl(controlForm.mascota_id, {
      tipo: controlForm.tipo,
      descripcion: controlForm.descripcion.trim(),
      fecha: controlForm.fecha,
      proxima_fecha: controlForm.proxima_fecha || null,
      veterinario: controlForm.veterinario.trim(),
      observaciones: controlForm.observaciones.trim(),
    })
    showMsg('Control veterinario registrado exitosamente')
    showVeterinarioModal.value = false
    await cargarHistoriales()
  } catch (err) {
    showMsg('Error al registrar el control veterinario', 'error')
  }
}

async function eliminarControlAdmin(controlId) {
  if (!confirm('¿Deseas eliminar este registro médico veterinario?')) return
  try {
    await veterinarioService.eliminarControl(controlId)
    showMsg('Registro veterinario eliminado')
    await cargarHistoriales()
  } catch (err) {
    showMsg('Error al eliminar registro veterinario', 'error')
  }
}

// Subida de foto local por Admin
const uploadingPhotoAdmin = ref(false)

async function onAdminFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return

  uploadingPhotoAdmin.value = true
  try {
    const res = await mascotasService.subirFoto(file)
    if (res && res.url) {
      mascotaForm.foto_url = res.url
      showMsg('¡Fotografía subida localmente con éxito!')
    }
  } catch (err) {
    showMsg(err.response?.data?.error || 'Error al subir la imagen', 'error')
  } finally {
    uploadingPhotoAdmin.value = false
    if (event.target) event.target.value = ''
  }
}

function logout() {
  authStore.logout()
  router.push('/login')
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const parts = dateStr.split('-')
  if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`
  return dateStr
}
</script>

<template>
  <div class="admin-app-layout">
    <!-- MENÚ LATERAL ADMINISTRATIVO (11 OPCIONES) -->
    <aside class="admin-sidebar">
      <div class="sidebar-top">
        <div class="brand-box" @click="activeTab = 'dashboard'">
          <Heart :size="24" class="logo-heart" />
          <span class="brand-title">Huellitas Admin</span>
        </div>
        <div class="admin-chip">
          <ShieldCheck :size="18" class="chip-shield" />
          <div>
            <span class="admin-name">{{ authStore.userName }}</span>
            <span class="admin-role">Super Administrador</span>
          </div>
        </div>
      </div>

      <nav class="sidebar-menu">
        <button type="button" class="menu-item" :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">
          <BarChart3 :size="18" />
          <span>Dashboard</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'usuarios' }" @click="activeTab = 'usuarios'">
          <Users :size="18" />
          <span>Gestión de usuarios</span>
          <span class="badge-count">{{ usuariosList.length }}</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'refugios' }" @click="activeTab = 'refugios'">
          <Building :size="18" />
          <span>Gestión de refugios</span>
          <span class="badge-count">{{ refugiosList.length }}</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'mascotas' }" @click="activeTab = 'mascotas'">
          <Folder :size="18" />
          <span>Gestión de mascotas</span>
          <span class="badge-count">{{ mascotasList.length }}</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'solicitudes' }" @click="activeTab = 'solicitudes'">
          <Inbox :size="18" />
          <span>Gestión de solicitudes</span>
          <span class="badge-count badge-amber">{{ estadisticas.solicitudes_pendientes }}</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'entrevistas' }" @click="activeTab = 'entrevistas'">
          <Video :size="18" />
          <span>Gestión de entrevistas</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'adopciones' }" @click="activeTab = 'adopciones'">
          <Award :size="18" />
          <span>Gestión de adopciones</span>
          <span class="badge-count badge-green">{{ estadisticas.adopciones_realizadas }}</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'veterinario' }" @click="activeTab = 'veterinario'">
          <Stethoscope :size="18" />
          <span>Historial veterinario</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'estadisticas' }" @click="activeTab = 'estadisticas'">
          <PieChart :size="18" />
          <span>Estadísticas</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'configuracion' }" @click="activeTab = 'configuracion'">
          <Settings :size="18" />
          <span>Configuración</span>
        </button>

        <div class="sidebar-divider"></div>

        <button type="button" class="menu-item btn-logout" @click="logout">
          <LogOut :size="18" />
          <span>Cerrar sesión</span>
        </button>
      </nav>
    </aside>

    <!-- ÁREA DE CONTENIDO -->
    <main class="admin-main">
      <header class="main-header">
        <div>
          <h2 class="header-title">
            <span v-if="activeTab === 'dashboard'">Dashboard General</span>
            <span v-else-if="activeTab === 'usuarios'">Administración de Usuarios y Cuentas</span>
            <span v-else-if="activeTab === 'refugios'">Gestión de Refugios Aliados</span>
            <span v-else-if="activeTab === 'mascotas'">Inventario General de Mascotas</span>
            <span v-else-if="activeTab === 'solicitudes'">Supervisión de Solicitudes de Adopción</span>
            <span v-else-if="activeTab === 'entrevistas'">Entrevistas Programadas</span>
            <span v-else-if="activeTab === 'adopciones'">Control y Finalización de Adopciones</span>
            <span v-else-if="activeTab === 'veterinario'">Historiales Veterinarios Globales</span>
            <span v-else-if="activeTab === 'estadisticas'">Métricas y Analítica de la Plataforma</span>
            <span v-else-if="activeTab === 'configuracion'">Configuración y Parámetros del Sistema</span>
          </h2>
          <p class="header-sub">Panel de Control &bull; Huellitas Felices Plataforma 2026</p>
        </div>

        <div class="header-tools">
          <button v-if="activeTab === 'refugios'" class="btn btn-primary btn-sm" @click="abrirCrearRefugio">
            <PlusCircle :size="16" />
            <span>Nuevo Refugio</span>
          </button>
          <button v-if="activeTab === 'mascotas'" class="btn btn-primary btn-sm" @click="abrirCrearMascota">
            <PlusCircle :size="16" />
            <span>Nueva Mascota</span>
          </button>
          <button class="btn btn-outline btn-sm" @click="cargarTodo" title="Refrescar datos de la base de datos">
            <RefreshCw :size="16" />
            <span>Sincronizar</span>
          </button>
        </div>
      </header>

      <!-- Feedback Banner -->
      <div v-if="feedback.type" class="feedback-banner" :class="'banner-' + feedback.type">
        <Check v-if="feedback.type === 'success'" :size="18" />
        <AlertCircle v-else :size="18" />
        <span>{{ feedback.text }}</span>
      </div>

      <!-- ════════ 6.1. DASHBOARD ADMINISTRATIVO ════════ -->
      <section v-if="activeTab === 'dashboard'" class="tab-pane">
        <!-- Indicadores Generales -->
        <div class="metrics-grid">
          <div class="stat-card" @click="activeTab = 'usuarios'">
            <span class="stat-val">{{ estadisticas.total_usuarios }}</span>
            <span class="stat-lbl">Total Usuarios</span>
          </div>
          <div class="stat-card" @click="activeTab = 'refugios'">
            <span class="stat-val">{{ estadisticas.total_refugios }}</span>
            <span class="stat-lbl">Refugios Aliados</span>
          </div>
          <div class="stat-card" @click="activeTab = 'mascotas'">
            <span class="stat-val">{{ estadisticas.total_mascotas }}</span>
            <span class="stat-lbl">Total Mascotas</span>
          </div>
          <div class="stat-card stat-green" @click="activeTab = 'mascotas'">
            <span class="stat-val">{{ estadisticas.mascotas_disponibles }}</span>
            <span class="stat-lbl">Disponibles</span>
          </div>
          <div class="stat-card stat-purple" @click="activeTab = 'mascotas'">
            <span class="stat-val">{{ estadisticas.mascotas_adoptadas }}</span>
            <span class="stat-lbl">Adoptadas</span>
          </div>
          <div class="stat-card stat-blue" @click="activeTab = 'solicitudes'">
            <span class="stat-val">{{ estadisticas.solicitudes_recibidas }}</span>
            <span class="stat-lbl">Solicitudes Recibidas</span>
          </div>
          <div class="stat-card stat-amber" @click="activeTab = 'solicitudes'">
            <span class="stat-val">{{ estadisticas.solicitudes_pendientes }}</span>
            <span class="stat-lbl">Solicitudes Pendientes</span>
          </div>
          <div class="stat-card stat-teal" @click="activeTab = 'adopciones'">
            <span class="stat-val">{{ estadisticas.adopciones_realizadas }}</span>
            <span class="stat-lbl">Adopciones Realizadas</span>
          </div>
        </div>

        <!-- Actividad Reciente -->
        <div class="pane-card-box">
          <h3 class="box-title">Actividad Reciente en la Plataforma</h3>
          <div v-if="actividadReciente.length > 0" class="activity-feed">
            <div v-for="(act, idx) in actividadReciente" :key="idx" class="activity-row">
              <div class="act-badge" :class="'act-' + act.tipo_actividad">
                <FileText v-if="act.tipo_actividad === 'adopcion'" :size="16" />
                <Video v-else :size="16" />
              </div>
              <div class="act-content">
                <span class="act-desc">{{ act.descripcion }}</span>
                <span class="act-meta">{{ formatDate(act.fecha) }} &bull; Estado: {{ act.estado }}</span>
              </div>
            </div>
          </div>
          <p v-else class="text-muted">No se registran eventos recientes.</p>
        </div>
      </section>

      <!-- ════════ 6.2. GESTIÓN DE USUARIOS ════════ -->
      <section v-else-if="activeTab === 'usuarios'" class="tab-pane">
        <div class="pane-card-box">
          <!-- Filtros de búsqueda -->
          <div class="search-filter-bar">
            <div class="search-wrap">
              <Search :size="18" class="icon-input" />
              <input type="text" v-model="userSearch" placeholder="Buscar por nombre, usuario o ciudad..." class="input input-search" />
            </div>
            <select v-model="userRoleFilter" class="select-filter">
              <option value="Todos">Todos los roles</option>
              <option value="adoptante">Adoptantes</option>
              <option value="refugio">Refugios</option>
              <option value="admin">Administradores</option>
            </select>
          </div>

          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Usuario</th>
                  <th>Edad</th>
                  <th>Ciudad</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in usuariosFiltrados" :key="u.id">
                  <td>#{{ u.id }}</td>
                  <td><strong>{{ u.nombre }}</strong></td>
                  <td>@{{ u.usuario }}</td>
                  <td>{{ u.edad }}</td>
                  <td>{{ u.ciudad }}</td>
                  <td>
                    <span class="role-pill" :class="'role-' + u.rol">{{ u.rol }}</span>
                  </td>
                  <td>
                    <span class="status-badge" :class="u.activo !== false ? 'badge-disponible' : 'badge-rechazada'">
                      {{ u.activo !== false ? 'Activo' : 'Desactivado' }}
                    </span>
                  </td>
                  <td>
                    <div class="actions-group">
                      <button class="btn btn-xs btn-outline" @click="abrirEditarUsuario(u)" title="Editar información">
                        <Edit :size="14" />
                      </button>
                      <button
                        class="btn btn-xs"
                        :class="u.activo !== false ? 'btn-red' : 'btn-green'"
                        @click="toggleEstadoCuenta(u.id)"
                        :title="u.activo !== false ? 'Desactivar cuenta' : 'Activar cuenta'"
                      >
                        <Power :size="14" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ════════ 6.3. GESTIÓN DE REFUGIOS ════════ -->
      <section v-else-if="activeTab === 'refugios'" class="tab-pane">
        <div class="pane-card-box">
          <div class="box-header-row">
            <h3 class="box-title">Refugios y Fundaciones Aliadas</h3>
            <button class="btn btn-primary btn-sm" @click="abrirCrearRefugio">
              <PlusCircle :size="16" />
              <span>Registrar Refugio</span>
            </button>
          </div>

          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Ciudad</th>
                  <th>Dirección</th>
                  <th>Teléfono</th>
                  <th>Correo</th>
                  <th>Mascotas</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in refugiosList" :key="r.id">
                  <td>#{{ r.id }}</td>
                  <td><strong>{{ r.nombre }}</strong></td>
                  <td>{{ r.ciudad }}</td>
                  <td>{{ r.direccion || '—' }}</td>
                  <td>{{ r.telefono || '—' }}</td>
                  <td>{{ r.email || '—' }}</td>
                  <td>{{ r.total_mascotas || 0 }}</td>
                  <td>
                    <button class="btn btn-xs btn-outline" @click="abrirEditarRefugio(r)" title="Editar">
                      <Edit :size="14" />
                      <span>Editar</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ════════ 6.4. GESTIÓN DE MASCOTAS ════════ -->
      <section v-else-if="activeTab === 'mascotas'" class="tab-pane">
        <div class="pane-card-box">
          <div class="search-filter-bar">
            <div class="search-wrap">
              <Search :size="18" class="icon-input" />
              <input type="text" v-model="petSearch" placeholder="Buscar mascota por nombre o raza..." class="input input-search" />
            </div>
            <select v-model="petStatusFilter" class="select-filter">
              <option value="Todos">Todos los estados</option>
              <option value="Disponible">Disponible</option>
              <option value="En revisión">En revisión</option>
              <option value="Adoptada">Adoptada</option>
            </select>
          </div>

          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Mascota</th>
                  <th>Tipo</th>
                  <th>Edad</th>
                  <th>Ciudad</th>
                  <th>Estado</th>
                  <th>Salud</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in mascotasFiltradasAdmin" :key="m.id">
                  <td>#{{ m.id }}</td>
                  <td><strong>{{ m.nombre }}</strong> ({{ m.raza || 'Criollo' }})</td>
                  <td>{{ m.tipo }} &bull; {{ m.sexo }}</td>
                  <td>{{ m.edad }} años</td>
                  <td>{{ m.ciudad }}</td>
                  <td>
                    <span class="status-badge" :class="'badge-' + (m.estado || '').toLowerCase().replace(' ', '-')">
                      {{ m.estado }}
                    </span>
                  </td>
                  <td>
                    <span v-if="m.vacunado" class="chip-mini chip-green">Vac</span>
                    <span v-if="m.desparasitado" class="chip-mini chip-green">Desp</span>
                    <span v-if="m.esterilizado" class="chip-mini chip-green">Est</span>
                  </td>
                  <td>
                    <div class="actions-group">
                      <button class="btn btn-xs btn-outline" @click="verDetalleMascota(m.id)" title="Ver detalle">
                        <Eye :size="14" />
                      </button>
                      <button class="btn btn-xs btn-outline" @click="abrirEditarMascota(m)" title="Editar">
                        <Edit :size="14" />
                      </button>
                      <button class="btn btn-xs btn-red" @click="eliminarMascotaAdmin(m.id)" title="Eliminar">
                        <Trash2 :size="14" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ════════ 6.5. GESTIÓN DE SOLICITUDES ════════ -->
      <section v-else-if="activeTab === 'solicitudes'" class="tab-pane">
        <div class="pane-card-box">
          <h3 class="box-title">Todas las Solicitudes en la Plataforma</h3>
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Adoptante</th>
                  <th>Mascota</th>
                  <th>Refugio</th>
                  <th>Fecha</th>
                  <th>Estado</th>
                  <th>Acción Administrativa</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in solicitudesList" :key="s.id">
                  <td>#{{ s.id }}</td>
                  <td>{{ s.usuario_nombre }}</td>
                  <td><strong>{{ s.mascota_nombre }}</strong> ({{ s.mascota_tipo }})</td>
                  <td>{{ s.refugio_nombre }}</td>
                  <td>{{ formatDate(s.fecha_solicitud) }}</td>
                  <td>
                    <span class="status-badge" :class="'badge-' + s.estado.toLowerCase().replace(' ', '-')">
                      {{ s.estado }}
                    </span>
                  </td>
                  <td>
                    <div class="actions-group">
                      <button
                        v-if="s.estado !== 'Aprobada'"
                        class="btn btn-xs btn-green"
                        @click="cambiarEstadoSolicitudAdmin(s.id, 'Aprobada')"
                      >
                        Aprobar
                      </button>
                      <button
                        v-if="s.estado !== 'Rechazada'"
                        class="btn btn-xs btn-red"
                        @click="cambiarEstadoSolicitudAdmin(s.id, 'Rechazada')"
                      >
                        Rechazar
                      </button>
                      <button
                        v-if="s.estado !== 'En revisión'"
                        class="btn btn-xs btn-outline"
                        @click="cambiarEstadoSolicitudAdmin(s.id, 'En revisión')"
                      >
                        Reabrir
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ════════ 6.6. GESTIÓN DE ENTREVISTAS ════════ -->
      <section v-else-if="activeTab === 'entrevistas'" class="tab-pane">
        <div class="pane-card-box">
          <h3 class="box-title">Entrevistas Registradas en el Sistema</h3>
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Fecha &bull; Hora</th>
                  <th>Mascota</th>
                  <th>Adoptante</th>
                  <th>Refugio</th>
                  <th>Modalidad</th>
                  <th>Estado</th>
                  <th>Observaciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in entrevistasList" :key="e.id">
                  <td>{{ formatDate(e.fecha) }} &bull; {{ e.hora }}</td>
                  <td><strong>{{ e.mascota_nombre }}</strong></td>
                  <td>{{ e.usuario_nombre }}</td>
                  <td>{{ e.refugio_nombre }}</td>
                  <td><span class="modalidad-chip">{{ e.modalidad }}</span></td>
                  <td>
                    <span class="status-badge" :class="'badge-' + e.estado.toLowerCase()">
                      {{ e.estado }}
                    </span>
                  </td>
                  <td>{{ e.observaciones || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ════════ 6.7. GESTIÓN DE ADOPCIONES ════════ -->
      <section v-else-if="activeTab === 'adopciones'" class="tab-pane">
        <div class="pane-card-box">
          <h3 class="box-title">Adopciones Finalizadas y Supervisión</h3>
          <p class="text-muted text-sm" style="margin-bottom: 1.2rem;">
            Cuando una solicitud se aprueba formalmente, la mascota cambia automáticamente su estado a <strong>Adoptada</strong> y se bloquea para nuevos procesos.
          </p>

          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Adoptante</th>
                  <th>Mascota</th>
                  <th>Refugio</th>
                  <th>Fecha Solicitud</th>
                  <th>Estado</th>
                  <th>Intervención</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="adop in solicitudesList.filter(s => s.estado === 'Aprobada')" :key="adop.id">
                  <td>#{{ adop.id }}</td>
                  <td>{{ adop.usuario_nombre }}</td>
                  <td><strong>{{ adop.mascota_nombre }}</strong></td>
                  <td>{{ adop.refugio_nombre }}</td>
                  <td>{{ formatDate(adop.fecha_solicitud) }}</td>
                  <td><span class="status-badge badge-aprobada">Finalizada / Aprobada</span></td>
                  <td>
                    <button class="btn btn-xs btn-outline" @click="cambiarEstadoSolicitudAdmin(adop.id, 'En revisión')">
                      Reabrir Proceso
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ════════ 6.8. HISTORIAL VETERINARIO ════════ -->
      <section v-else-if="activeTab === 'veterinario'" class="tab-pane">
        <div class="pane-card-box">
          <div class="box-header-flex">
            <div>
              <h3 class="box-title">Historial Veterinario General de la Plataforma</h3>
              <p class="box-subtitle">Registros clínicos, vacunas y controles médicos administrados.</p>
            </div>
            <button type="button" class="btn btn-primary btn-sm" @click="abrirNuevoControlAdmin">
              <PlusCircle :size="16" />
              <span>+ Registrar Control Veterinario</span>
            </button>
          </div>
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Mascota</th>
                  <th>Refugio</th>
                  <th>Tipo</th>
                  <th>Descripción</th>
                  <th>Fecha</th>
                  <th>Próxima Cita</th>
                  <th>Veterinario</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in historialesList" :key="h.id">
                  <td>#{{ h.id }}</td>
                  <td><strong>{{ h.mascota_nombre }}</strong></td>
                  <td>{{ h.refugio_nombre }}</td>
                  <td><span class="modalidad-chip">{{ h.tipo }}</span></td>
                  <td>{{ h.descripcion }}</td>
                  <td>{{ formatDate(h.fecha) }}</td>
                  <td>{{ formatDate(h.proxima_fecha) }}</td>
                  <td>{{ h.veterinario }}</td>
                  <td>
                    <button
                      type="button"
                      class="btn-action-icon btn-action-delete"
                      @click="eliminarControlAdmin(h.id)"
                      title="Eliminar registro médico"
                    >
                      <Trash2 :size="15" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ════════ 6.9. ESTADÍSTICAS COMPLETAS ════════ -->
      <section v-else-if="activeTab === 'estadisticas'" class="tab-pane">
        <div class="metrics-grid">
          <div class="stat-card">
            <span class="stat-val">{{ estadisticas.total_mascotas }}</span>
            <span class="stat-lbl">Mascotas Totales</span>
          </div>
          <div class="stat-card stat-green">
            <span class="stat-val">{{ estadisticas.perros }}</span>
            <span class="stat-lbl">Perros Registrados</span>
          </div>
          <div class="stat-card stat-amber">
            <span class="stat-val">{{ estadisticas.gatos }}</span>
            <span class="stat-lbl">Gatos Registrados</span>
          </div>
          <div class="stat-card stat-purple">
            <span class="stat-val">{{ estadisticas.adopciones_realizadas }}</span>
            <span class="stat-lbl">Adopciones Concluidas</span>
          </div>
        </div>

        <div class="two-columns">
          <div class="pane-card-box">
            <h3 class="box-title">Distribución de Mascotas por Ciudad</h3>
            <ul class="stats-list">
              <li v-for="(c, i) in estadisticas.mascotas_por_ciudad" :key="i">
                <span>{{ c.ciudad || 'No especificada' }}</span>
                <strong>{{ c.cantidad }} mascotas</strong>
              </li>
            </ul>
          </div>

          <div class="pane-card-box">
            <h3 class="box-title">Solicitudes por Estado</h3>
            <ul class="stats-list">
              <li v-for="(s, i) in estadisticas.solicitudes_por_estado" :key="i">
                <span>{{ s.estado }}</span>
                <strong>{{ s.cantidad }} solicitudes</strong>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- ════════ 6.10. CONFIGURACIÓN ════════ -->
      <section v-else-if="activeTab === 'configuracion'" class="tab-pane">
        <div class="pane-card-box form-card-box">
          <h3 class="box-title">Parámetros de la Plataforma</h3>
          <div class="config-grid">
            <div class="config-item">
              <label class="label">Base de Datos</label>
              <input type="text" class="input" disabled value="MySQL 8.0 &bull; huellitas_felices" />
            </div>
            <div class="config-item">
              <label class="label">Seguridad de Sesión</label>
              <input type="text" class="input" disabled value="JWT (HS256) &bull; 8 Horas de expiración" />
            </div>
            <div class="config-item">
              <label class="label">Autenticación por API Key</label>
              <input type="text" class="input" disabled value="Activa (X-API-KEY requerida para microservicios)" />
            </div>
            <div class="config-item">
              <label class="label">Copia de Seguridad del Sistema</label>
              <input type="text" class="input" disabled value="backup_huellitas_felices.zip &bull; migration.sql" />
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- MODAL EDITAR USUARIO -->
    <div v-if="showUserModal" class="modal-overlay" @click.self="showUserModal = false">
      <div class="modal-content form-dialog-card">
        <button class="close-btn" @click="showUserModal = false">&times;</button>
        <h3 class="dialog-title">Editar Usuario #{{ userForm.id }}</h3>
        <form @submit.prevent="guardarUsuario" class="stacked-form">
          <div class="form-group">
            <label class="label">Nombre completo</label>
            <input type="text" v-model="userForm.nombre" class="input" required />
          </div>
          <div class="two-columns">
            <div class="form-group">
              <label class="label">Usuario</label>
              <input type="text" v-model="userForm.usuario" class="input" required />
            </div>
            <div class="form-group">
              <label class="label">Edad</label>
              <input type="number" v-model="userForm.edad" class="input" required />
            </div>
          </div>
          <div class="two-columns">
            <div class="form-group">
              <label class="label">Ciudad</label>
              <input type="text" v-model="userForm.ciudad" class="input" required />
            </div>
            <div class="form-group">
              <label class="label">Rol en el sistema</label>
              <select v-model="userForm.rol" class="input select">
                <option value="adoptante">Adoptante</option>
                <option value="refugio">Refugio</option>
                <option value="admin">Administrador</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="label">Nueva Contraseña (opcional)</label>
            <input type="password" v-model="userForm.password" placeholder="Dejar en blanco para conservar actual" class="input" />
          </div>
          <div class="dialog-actions">
            <button type="submit" class="btn btn-primary">Guardar Cambios</button>
            <button type="button" class="btn btn-outline" @click="showUserModal = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL REFUGIO -->
    <div v-if="showRefugioModal" class="modal-overlay" @click.self="showRefugioModal = false">
      <div class="modal-content form-dialog-card">
        <button class="close-btn" @click="showRefugioModal = false">&times;</button>
        <h3 class="dialog-title">{{ refugioForm.id ? 'Editar Refugio' : 'Registrar Nuevo Refugio' }}</h3>
        <form @submit.prevent="guardarRefugio" class="stacked-form">
          <div class="form-group">
            <label class="label">Nombre del Refugio</label>
            <input type="text" v-model="refugioForm.nombre" class="input" required />
          </div>
          <div class="two-columns">
            <div class="form-group">
              <label class="label">Ciudad</label>
              <input type="text" v-model="refugioForm.ciudad" class="input" required />
            </div>
            <div class="form-group">
              <label class="label">Teléfono</label>
              <input type="text" v-model="refugioForm.telefono" class="input" />
            </div>
          </div>
          <div class="form-group">
            <label class="label">Dirección</label>
            <input type="text" v-model="refugioForm.direccion" class="input" />
          </div>
          <div class="form-group">
            <label class="label">Correo</label>
            <input type="email" v-model="refugioForm.email" class="input" />
          </div>
          <div class="dialog-actions">
            <button type="submit" class="btn btn-primary">Guardar Refugio</button>
            <button type="button" class="btn btn-outline" @click="showRefugioModal = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL MASCOTA ADMIN -->
    <div v-if="showMascotaModal" class="modal-overlay" @click.self="showMascotaModal = false">
      <div class="modal-content form-dialog-card modal-lg">
        <button class="close-btn" @click="showMascotaModal = false">&times;</button>
        <h3 class="dialog-title">{{ mascotaForm.id ? 'Editar Mascota' : 'Registrar Mascota en la Plataforma' }}</h3>
        <form @submit.prevent="guardarMascotaAdmin" class="stacked-form">
          <div class="two-columns">
            <div class="form-group">
              <label class="label">Nombre de la Mascota *</label>
              <input type="text" v-model="mascotaForm.nombre" class="input" required />
            </div>
            <div class="form-group">
              <label class="label">Refugio Responsable</label>
              <select v-model="mascotaForm.refugio_id" class="input select">
                <option v-for="r in refugiosList" :key="r.id" :value="r.id">{{ r.nombre }} ({{ r.ciudad }})</option>
              </select>
            </div>
          </div>
          <div class="three-columns">
            <div class="form-group">
              <label class="label">Tipo</label>
              <select v-model="mascotaForm.tipo" class="input select">
                <option value="Perro">Perro</option>
                <option value="Gato">Gato</option>
              </select>
            </div>
            <div class="form-group">
              <label class="label">Edad (años)</label>
              <input type="number" v-model="mascotaForm.edad" class="input" required />
            </div>
            <div class="form-group">
              <label class="label">Estado</label>
              <select v-model="mascotaForm.estado" class="input select">
                <option value="Disponible">Disponible</option>
                <option value="En revisión">En revisión</option>
                <option value="Adoptada">Adoptada</option>
              </select>
            </div>
          </div>
          <div class="two-columns">
            <div class="form-group">
              <label class="label">Ciudad</label>
              <input type="text" v-model="mascotaForm.ciudad" class="input" required />
            </div>
            <div class="form-group">
              <label class="label">Raza</label>
              <input type="text" v-model="mascotaForm.raza" class="input" />
            </div>
          </div>

          <div class="two-columns">
            <div class="form-group">
              <label class="label">Sexo</label>
              <select v-model="mascotaForm.sexo" class="input select">
                <option value="Macho">Macho</option>
                <option value="Hembra">Hembra</option>
              </select>
            </div>
            <div class="form-group">
              <label class="label">Tamaño</label>
              <select v-model="mascotaForm.tamano" class="input select">
                <option value="Pequeno">Pequeño</option>
                <option value="Mediano">Mediano</option>
                <option value="Grande">Grande</option>
              </select>
            </div>
          </div>

          <!-- Fotografía de la Mascota (Local o URL) -->
          <div class="form-group photo-uploader-field">
            <label class="label">Fotografía de la Mascota</label>
            <div class="photo-upload-row">
              <input
                type="file"
                ref="adminFileInput"
                accept="image/png, image/jpeg, image/jpg, image/webp, image/gif"
                @change="onAdminFileSelected"
                style="display: none"
              />
              <button
                type="button"
                class="btn btn-outline btn-sm btn-device-upload"
                @click="$refs.adminFileInput.click()"
                :disabled="uploadingPhotoAdmin"
              >
                <Upload :size="16" />
                <span v-if="!uploadingPhotoAdmin">📁 Subir desde mi dispositivo</span>
                <span v-else>Subiendo fotografía...</span>
              </button>
              <span class="or-separator">o URL:</span>
              <input
                type="url"
                v-model="mascotaForm.foto_url"
                placeholder="https://ejemplo.com/foto.jpg"
                class="input url-flex-input"
              />
            </div>

            <!-- Previsualización -->
            <div v-if="mascotaForm.foto_url" class="photo-preview-card">
              <img :src="mascotaForm.foto_url" alt="Previsualización" class="photo-preview-thumbnail" />
              <div class="photo-preview-details">
                <span class="preview-status-pill">✓ Fotografía vinculada</span>
                <button type="button" class="btn-remove-photo" @click="mascotaForm.foto_url = ''">Quitar foto</button>
              </div>
            </div>
          </div>

          <div class="dialog-actions">
            <button type="submit" class="btn btn-primary">Guardar Mascota</button>
            <button type="button" class="btn btn-outline" @click="showMascotaModal = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL NUEVO CONTROL VETERINARIO ADMIN -->
    <div v-if="showVeterinarioModal" class="modal-overlay" @click.self="showVeterinarioModal = false">
      <div class="modal-content form-dialog-card modal-md">
        <button class="close-btn" @click="showVeterinarioModal = false">&times;</button>
        <div class="dialog-header-wrap">
          <Stethoscope :size="24" class="dialog-icon-vet" />
          <h3 class="dialog-title">Registrar Control Veterinario</h3>
        </div>
        <form @submit.prevent="guardarControlAdmin" class="stacked-form">
          <div class="form-group">
            <label class="label">Mascota Paciente *</label>
            <select v-model="controlForm.mascota_id" class="input select" required>
              <option disabled value="">Seleccionar mascota...</option>
              <option v-for="m in mascotasList" :key="m.id" :value="m.id">
                {{ m.nombre }} (#{{ m.id }} - {{ m.tipo }} · {{ m.ciudad }})
              </option>
            </select>
          </div>

          <div class="two-columns">
            <div class="form-group">
              <label class="label">Tipo de Atención *</label>
              <select v-model="controlForm.tipo" class="input select" required>
                <option value="Vacuna">Vacunación / Refuerzo</option>
                <option value="Control">Control General / Consulta</option>
                <option value="Desparasitación">Desparasitación Interna / Externa</option>
                <option value="Esterilización">Esterilización / Castración</option>
                <option value="Cirugía">Procedimiento Quirúrgico</option>
                <option value="Urgencia">Atención de Urgencia</option>
              </select>
            </div>
            <div class="form-group">
              <label class="label">Fecha de Atención *</label>
              <input type="date" v-model="controlForm.fecha" class="input" required />
            </div>
          </div>

          <div class="two-columns">
            <div class="form-group">
              <label class="label">Próxima Cita (Opcional)</label>
              <input type="date" v-model="controlForm.proxima_fecha" class="input" />
            </div>
            <div class="form-group">
              <label class="label">Veterinario / Clínica *</label>
              <input type="text" v-model="controlForm.veterinario" class="input" placeholder="Ej: Dr. Camilo Muñoz - MV" required />
            </div>
          </div>

          <div class="form-group">
            <label class="label">Descripción del Procedimiento *</label>
            <input type="text" v-model="controlForm.descripcion" class="input" placeholder="Ej: Vacuna Séxtuple canina aplicada" required />
          </div>

          <div class="form-group">
            <label class="label">Observaciones Clínicas</label>
            <textarea rows="2" v-model="controlForm.observaciones" class="input textarea" placeholder="Evolución, recomendaciones, peso..."></textarea>
          </div>

          <div class="dialog-actions">
            <button type="submit" class="btn btn-primary">Guardar Registro Veterinario</button>
            <button type="button" class="btn btn-outline" @click="showVeterinarioModal = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL DETALLE DE MASCOTA CON HISTORIAL VETERINARIO -->
    <PetDetailModal
      v-if="showPetDetail && selectedPetProfile"
      :perfilData="selectedPetProfile"
      @close="showPetDetail = false"
    />
  </div>
</template>

<style scoped>
.admin-app-layout {
  display: flex;
  min-height: 100vh;
  background-color: #FAF7F2;
  color: #2D3142;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.admin-sidebar {
  width: 290px;
  background-color: #1F2430;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  padding: 1.8rem 1.2rem;
  box-sizing: border-box;
  flex-shrink: 0;
}

.sidebar-top {
  margin-bottom: 1.8rem;
}

.brand-box {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
  margin-bottom: 1.2rem;
}

.logo-heart { color: #E07A5F; }

.brand-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.35rem;
  font-weight: 800;
  color: #ffffff;
}

.admin-chip {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 0.65rem 0.85rem;
}

.chip-shield { color: #E07A5F; }
.admin-name { display: block; font-size: 0.9rem; font-weight: 700; color: #ffffff; }
.admin-role { font-size: 0.74rem; color: #A5D6A7; }

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.68rem 0.9rem;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: #A0A5B5;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
  position: relative;
}

.menu-item:hover { background-color: rgba(255, 255, 255, 0.08); color: #ffffff; }
.menu-item.active { background-color: #E07A5F; color: #ffffff; font-weight: 700; }

.badge-count {
  margin-left: auto;
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.badge-amber { background-color: #D97706; }
.badge-green { background-color: #2E7D32; }

.sidebar-divider {
  height: 1px;
  background-color: rgba(255, 255, 255, 0.12);
  margin: 1rem 0;
}

.btn-logout { color: #F87171; }
.btn-logout:hover { background-color: rgba(239, 68, 68, 0.15); color: #FCA5A5; }

/* PANEL PRINCIPAL */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 2rem 2.5rem;
  box-sizing: border-box;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #E6DEC8;
  padding-bottom: 1.2rem;
  margin-bottom: 1.8rem;
}

.header-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.8rem;
  font-weight: 800;
  color: #1F2430;
  margin: 0;
}

.header-sub { font-size: 0.9rem; color: #61677A; margin: 0.2rem 0 0; }
.header-tools { display: flex; gap: 0.7rem; }

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 1.8rem;
}

/* MÉTRICAS */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 1.1rem;
}

.stat-card {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 16px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.stat-card:hover { transform: translateY(-2px); }

.stat-val {
  font-family: 'Outfit', sans-serif;
  font-size: 1.85rem;
  font-weight: 800;
  color: #1F2430;
  line-height: 1;
  margin-bottom: 0.4rem;
}

.stat-lbl { font-size: 0.82rem; color: #61677A; font-weight: 600; }

.stat-green .stat-val { color: #2E7D32; }
.stat-purple .stat-val { color: #7E3AF2; }
.stat-blue .stat-val { color: #1A73E8; }
.stat-amber .stat-val { color: #D97706; }
.stat-teal .stat-val { color: #0D9488; }

.pane-card-box {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 18px;
  padding: 1.8rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.box-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1F2430;
  margin: 0 0 1rem;
}

.search-filter-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.4rem;
}

.search-wrap {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.icon-input {
  position: absolute;
  left: 12px;
  color: #8C92A4;
}

.input-search {
  padding-left: 2.4rem;
}

.select-filter {
  padding: 0.6rem 1rem;
  border-radius: 10px;
  border: 1.5px solid #E0D9CD;
  background: #ffffff;
  font-size: 0.88rem;
  font-family: inherit;
  cursor: pointer;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.data-table th {
  background-color: #F8F5EE;
  padding: 0.8rem 1rem;
  font-weight: 700;
  border-bottom: 1px solid #E6DEC8;
  text-align: left;
}

.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #EFE8DC;
  vertical-align: middle;
}

.role-pill {
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: capitalize;
}

.role-admin { background-color: #FDE8E8; color: #9B1C1C; }
.role-refugio { background-color: #EDF7EE; color: #2E7D32; }
.role-adoptante { background-color: #E8F0FE; color: #1A73E8; }

.status-badge {
  padding: 0.22rem 0.65rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
}

.badge-disponible { background-color: #EDF7EE; color: #2E7D32; }
.badge-en-revisión { background-color: #FEF3C7; color: #D97706; }
.badge-adoptada { background-color: #F3F4F6; color: #4B5563; }
.badge-rechazada { background-color: #FDE8E8; color: #9B1C1C; }
.badge-aprobada { background-color: #EDF7EE; color: #2E7D32; }

.actions-group {
  display: flex;
  gap: 0.4rem;
}

.btn-xs {
  padding: 0.35rem 0.65rem;
  font-size: 0.78rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.btn-green { background-color: #2E7D32; color: #ffffff; }
.btn-red { background-color: #9B1C1C; color: #ffffff; }

.activity-feed {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.activity-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background-color: #FAF7F2;
  border-radius: 12px;
}

.act-badge {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.act-adopcion { background: #FEF3C7; color: #D97706; }
.act-entrevista { background: #E8F0FE; color: #1A73E8; }

.act-content { display: flex; flex-direction: column; }
.act-desc { font-size: 0.9rem; font-weight: 600; color: #1F2430; }
.act-meta { font-size: 0.78rem; color: #61677A; }

.stats-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.stats-list li {
  display: flex;
  justify-content: space-between;
  padding: 0.6rem 0;
  border-bottom: 1px dashed #EFE8DC;
  font-size: 0.92rem;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.4rem;
}

/* MODALES */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(45, 49, 66, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.form-dialog-card {
  max-width: 540px;
  width: 100%;
  background: #ffffff;
  border-radius: 20px;
  padding: 2rem;
  position: relative;
}

.modal-lg { max-width: 720px; }

.dialog-title { font-family: 'Outfit', sans-serif; font-size: 1.4rem; margin: 0 0 1rem; }
.dialog-actions { display: flex; gap: 0.8rem; margin-top: 1rem; }

.close-btn {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #8C92A4;
  cursor: pointer;
}

.feedback-banner {
  padding: 0.85rem 1.2rem;
  border-radius: 10px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.9rem;
}

.banner-success { background: #EDF7EE; color: #2E7D32; border: 1px solid #A5D6A7; }
.banner-error { background: #FDE8E8; color: #9B1C1C; border: 1px solid #F8B4B4; }

.two-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.three-columns { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; }
.stacked-form { display: flex; flex-direction: column; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.label { font-size: 0.85rem; font-weight: 600; color: #2D3142; }

.input {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border-radius: 10px;
  border: 1.5px solid #E0D9CD;
  background: #ffffff;
  font-size: 0.9rem;
  font-family: inherit;
  box-sizing: border-box;
}

.input:focus { outline: none; border-color: #E07A5F; }

/* Estilos de cabecera flexible para secciones con botón */
.box-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.box-subtitle {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.2rem 0 0;
}

.dialog-header-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.2rem;
}

.dialog-icon-vet {
  color: #4E8752;
}

.modal-md {
  max-width: 580px;
}

/* Subida de foto local y previsualización */
.photo-uploader-field {
  background: #fdfaf6;
  border: 1px dashed #e2dcd2;
  border-radius: 14px;
  padding: 1rem;
}

.photo-upload-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-device-upload {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.or-separator {
  font-size: 0.82rem;
  color: #8C92A4;
  font-weight: 600;
}

.url-flex-input {
  flex: 1;
  min-width: 180px;
}

.photo-preview-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.8rem;
  padding: 0.6rem 0.8rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #E6DEC8;
}

.photo-preview-thumbnail {
  width: 54px;
  height: 54px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #e2e8f0;
}

.photo-preview-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.preview-status-pill {
  font-size: 0.78rem;
  font-weight: 700;
  color: #2E7D32;
  background: #EDF7EE;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  width: fit-content;
}

.btn-remove-photo {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  text-align: left;
}

.btn-remove-photo:hover {
  text-decoration: underline;
}

@media (max-width: 900px) {
  .admin-app-layout { flex-direction: column; }
  .admin-sidebar { width: 100%; }
  .sidebar-menu { flex-direction: row; flex-wrap: wrap; }
  .two-columns, .three-columns { grid-template-columns: 1fr; }
}
</style>
