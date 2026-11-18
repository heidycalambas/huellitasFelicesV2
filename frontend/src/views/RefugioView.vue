<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import refugiosService from '@/services/refugiosService'
import mascotasService from '@/services/mascotasService'
import adopcionesService from '@/services/adopcionesService'
import veterinarioService from '@/services/veterinarioService'
import PetDetailModal from '@/components/PetDetailModal.vue'
import {
  Heart,
  Building,
  PlusCircle,
  Folder,
  Inbox,
  Video,
  Stethoscope,
  Award,
  BarChart3,
  LogOut,
  Edit,
  Trash2,
  Check,
  X,
  AlertCircle,
  Calendar,
  Clock,
  User,
  MapPin,
  Phone,
  Mail,
  ShieldCheck,
  Eye,
  Upload,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

// Tabs del panel de refugio:
// 1. Dashboard | 2. Info refugio | 3. Registrar mascota | 4. Mis mascotas | 5. Solicitudes recibidas | 6. Entrevistas | 7. Historial veterinario | 8. Adopciones realizadas | 9. Estadísticas
const activeTab = ref('dashboard')

// Datos del refugio y métricas
const refugio = ref(null)
const metricas = ref({
  mascotas_registradas: 0,
  mascotas_disponibles: 0,
  mascotas_en_proceso: 0,
  mascotas_adoptadas: 0,
  solicitudes_pendientes: 0,
  entrevistas_programadas: 0,
  por_tipo: [],
})

// Listas de datos
const misMascotas = ref([])
const solicitudes = ref([])
const entrevistas = ref([])
const historiales = ref([])
const adopcionesFinalizadas = ref([])

// Formulario de edición/registro de mascota
const mascotaForm = reactive({
  id: null,
  nombre: '',
  tipo: 'Perro',
  edad: 2,
  sexo: 'Macho',
  tamano: 'Mediano',
  raza: 'Criollo',
  ciudad: 'Popayán',
  descripcion: '',
  personalidad: 'Cariñoso, leal y amigable',
  nivel_energia: 'Media',
  compatible_ninos: true,
  compatible_mascotas: true,
  vacunado: true,
  desparasitado: true,
  esterilizado: true,
  estado: 'Disponible',
  foto_url: '',
})

// Formulario de control veterinario
const controlForm = reactive({
  mascota_id: '',
  tipo: 'Vacuna',
  descripcion: '',
  fecha: new Date().toISOString().split('T')[0],
  proxima_fecha: '',
  veterinario: 'Dr. Veterinario',
  observaciones: '',
})

// Formulario de programación de entrevista
const entrevistaModalData = reactive({
  show: false,
  adopcion_id: null,
  mascota_nombre: '',
  usuario_nombre: '',
  fecha: '',
  hora: '10:00',
  modalidad: 'Virtual',
  observaciones: 'Verificación de condiciones de vivienda y disponibilidad',
})

// Modal de detalle de mascota
const showPetDetail = ref(false)
const selectedPetProfile = ref(null)

// Mensajes de feedback
const feedback = reactive({
  type: null, // 'success' | 'error'
  text: '',
})

function showMsg(text, type = 'success') {
  feedback.text = text
  feedback.type = type
  setTimeout(() => {
    feedback.type = null
    feedback.text = ''
  }, 4000)
}

onMounted(async () => {
  await cargarDatosRefugio()
})

async function cargarDatosRefugio() {
  try {
    const data = await refugiosService.getMiRefugio()
    if (data.refugio) {
      refugio.value = data.refugio
      metricas.value = data.metricas || metricas.value
      mascotaForm.ciudad = refugio.value.ciudad || 'Popayán'
      await Promise.all([
        cargarMisMascotas(),
        cargarSolicitudes(),
        cargarEntrevistas(),
        cargarHistoriales(),
      ])
    }
  } catch (err) {
    showMsg('No se pudo cargar la información del refugio', 'error')
  }
}

async function cargarMisMascotas() {
  if (!refugio.value) return
  const data = await mascotasService.getMascotas({ refugio_id: refugio.value.id })
  misMascotas.value = data.mascotas || []
}

async function cargarSolicitudes() {
  if (!refugio.value) return
  const data = await adopcionesService.getSolicitudes({ refugio_id: refugio.value.id })
  solicitudes.value = data.adopciones || []
  adopcionesFinalizadas.value = solicitudes.value.filter((s) => s.estado === 'Aprobada')
}

async function cargarEntrevistas() {
  if (!refugio.value) return
  const data = await adopcionesService.getEntrevistas({ refugio_id: refugio.value.id })
  entrevistas.value = data.entrevistas || []
}

async function cargarHistoriales() {
  if (!refugio.value) return
  const data = await veterinarioService.getTodosLosControles({ refugio_id: refugio.value.id })
  historiales.value = data.historial || []
}

// Guardar información del propio refugio
async function guardarInfoRefugio() {
  try {
    await refugiosService.actualizarMiRefugio({
      nombre: refugio.value.nombre,
      ciudad: refugio.value.ciudad,
      direccion: refugio.value.direccion,
      telefono: refugio.value.telefono,
      email: refugio.value.email,
    })
    showMsg('Información del refugio actualizada correctamente')
  } catch (err) {
    showMsg('Error al actualizar datos del refugio', 'error')
  }
}

// Preparar registro o edición de mascota
function resetMascotaForm() {
  mascotaForm.id = null
  mascotaForm.nombre = ''
  mascotaForm.tipo = 'Perro'
  mascotaForm.edad = 2
  mascotaForm.sexo = 'Macho'
  mascotaForm.tamano = 'Mediano'
  mascotaForm.raza = 'Criollo'
  mascotaForm.ciudad = refugio.value?.ciudad || 'Popayán'
  mascotaForm.descripcion = ''
  mascotaForm.personalidad = 'Cariñoso, leal y amigable'
  mascotaForm.nivel_energia = 'Media'
  mascotaForm.compatible_ninos = true
  mascotaForm.compatible_mascotas = true
  mascotaForm.vacunado = true
  mascotaForm.desparasitado = true
  mascotaForm.esterilizado = true
  mascotaForm.estado = 'Disponible'
  mascotaForm.foto_url = ''
}

function editarMascota(m) {
  mascotaForm.id = m.id
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
  activeTab.value = 'registrar'
}

// Subida de fotografía local desde dispositivo para Refugios
const uploadingPhotoRefugio = ref(false)

async function onRefugioFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return

  uploadingPhotoRefugio.value = true
  try {
    const res = await mascotasService.subirFoto(file)
    if (res && res.url) {
      mascotaForm.foto_url = res.url
      showMsg('¡Fotografía subida localmente con éxito!')
    }
  } catch (err) {
    showMsg(err.response?.data?.error || 'Error al subir la imagen', 'error')
  } finally {
    uploadingPhotoRefugio.value = false
    if (event.target) event.target.value = ''
  }
}

async function guardarMascota() {
  if (!mascotaForm.nombre.trim()) {
    showMsg('El nombre de la mascota es obligatorio', 'error')
    return
  }

  const payload = {
    ...mascotaForm,
    refugio_id: refugio.value?.id,
    edad: Number(mascotaForm.edad),
  }

  try {
    if (mascotaForm.id) {
      await mascotasService.editarMascota(mascotaForm.id, payload)
      showMsg(`Mascota "${mascotaForm.nombre}" actualizada correctamente`)
    } else {
      await mascotasService.crearMascota(payload)
      showMsg(`Mascota "${mascotaForm.nombre}" registrada con éxito en el refugio`)
    }
    await cargarMisMascotas()
    resetMascotaForm()
    activeTab.value = 'mis-mascotas'
  } catch (err) {
    showMsg('Error al guardar los datos de la mascota', 'error')
  }
}

// Gestión de solicitudes
async function cambiarEstadoSolicitud(solicitudId, nuevoEstado) {
  try {
    await adopcionesService.actualizarEstado(solicitudId, nuevoEstado)
    showMsg(`Solicitud #${solicitudId} actualizada a estado: ${nuevoEstado}`)
    await Promise.all([cargarSolicitudes(), cargarMisMascotas()])
  } catch (err) {
    showMsg(err.response?.data?.error || 'Error al cambiar estado de solicitud', 'error')
  }
}

// Programar entrevista
function abrirModalEntrevista(sol) {
  entrevistaModalData.show = true
  entrevistaModalData.adopcion_id = sol.id
  entrevistaModalData.mascota_nombre = sol.mascota_nombre
  entrevistaModalData.usuario_nombre = sol.usuario_nombre
  entrevistaModalData.fecha = new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0]
  entrevistaModalData.hora = '10:00'
  entrevistaModalData.modalidad = 'Virtual'
  entrevistaModalData.observaciones = 'Verificación de condiciones de vivienda y disponibilidad'
}

async function confirmarEntrevista() {
  if (!entrevistaModalData.fecha || !entrevistaModalData.hora) {
    showMsg('Fecha y hora son obligatorias', 'error')
    return
  }

  try {
    await adopcionesService.programarEntrevista(entrevistaModalData.adopcion_id, {
      fecha: entrevistaModalData.fecha,
      hora: entrevistaModalData.hora,
      modalidad: entrevistaModalData.modalidad,
      observaciones: entrevistaModalData.observaciones,
    })
    showMsg('Entrevista programada con éxito')
    entrevistaModalData.show = false
    await Promise.all([cargarSolicitudes(), cargarEntrevistas()])
  } catch (err) {
    showMsg('Error al programar la entrevista', 'error')
  }
}

// Historial veterinario: agregar control
async function agregarControlVeterinario() {
  if (!controlForm.mascota_id || !controlForm.descripcion.trim()) {
    showMsg('Selecciona una mascota y escribe la descripción de la atención', 'error')
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
    showMsg('Control veterinario registrado con éxito')
    controlForm.descripcion = ''
    controlForm.proxima_fecha = ''
    controlForm.observaciones = ''
    await cargarHistoriales()
  } catch (err) {
    showMsg('Error al registrar control veterinario', 'error')
  }
}

async function verDetalleMascota(mascotaId) {
  const p = await mascotasService.getMascotaPerfil(mascotaId)
  if (p) {
    selectedPetProfile.value = p
    showPetDetail.value = true
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
  <div class="refugio-layout">
    <!-- BARRA LATERAL DEL REFUGIO -->
    <aside class="refugio-sidebar">
      <div class="sidebar-top">
        <div class="brand-box" @click="activeTab = 'dashboard'">
          <Heart :size="24" class="heart-icon" />
          <span class="brand-name">Huellitas Felices</span>
        </div>
        <div class="refugio-badge-card" v-if="refugio">
          <Building :size="20" class="badge-icon" />
          <div>
            <h4 class="refugio-name">{{ refugio.nombre }}</h4>
            <span class="refugio-city">{{ refugio.ciudad }} &bull; Refugio Aliado</span>
          </div>
        </div>
      </div>

      <!-- Menú de 10 opciones requerido -->
      <nav class="sidebar-menu">
        <button type="button" class="menu-item" :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">
          <BarChart3 :size="18" />
          <span>Dashboard</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'info' }" @click="activeTab = 'info'">
          <Building :size="18" />
          <span>Información del refugio</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'registrar' }" @click="resetMascotaForm(); activeTab = 'registrar'">
          <PlusCircle :size="18" />
          <span>Registrar mascota</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'mis-mascotas' }" @click="activeTab = 'mis-mascotas'">
          <Folder :size="18" />
          <span>Mis mascotas</span>
          <span class="menu-counter">{{ misMascotas.length }}</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'solicitudes' }" @click="activeTab = 'solicitudes'">
          <Inbox :size="18" />
          <span>Solicitudes recibidas</span>
          <span v-if="metricas.solicitudes_pendientes > 0" class="menu-counter badge-amber">
            {{ metricas.solicitudes_pendientes }}
          </span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'entrevistas' }" @click="activeTab = 'entrevistas'">
          <Video :size="18" />
          <span>Entrevistas</span>
          <span v-if="metricas.entrevistas_programadas > 0" class="menu-counter badge-green">
            {{ metricas.entrevistas_programadas }}
          </span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'veterinario' }" @click="activeTab = 'veterinario'">
          <Stethoscope :size="18" />
          <span>Historial veterinario</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'adopciones' }" @click="activeTab = 'adopciones'">
          <Award :size="18" />
          <span>Adopciones realizadas</span>
          <span class="menu-counter">{{ adopcionesFinalizadas.length }}</span>
        </button>

        <button type="button" class="menu-item" :class="{ active: activeTab === 'estadisticas' }" @click="activeTab = 'estadisticas'">
          <BarChart3 :size="18" />
          <span>Estadísticas</span>
        </button>

        <div class="sidebar-divider"></div>

        <button type="button" class="menu-item btn-logout" @click="logout">
          <LogOut :size="18" />
          <span>Cerrar sesión</span>
        </button>
      </nav>
    </aside>

    <!-- PANEL PRINCIPAL -->
    <main class="refugio-main">
      <header class="main-header">
        <div>
          <h2 class="header-title">
            <span v-if="activeTab === 'dashboard'">Dashboard del Refugio</span>
            <span v-else-if="activeTab === 'info'">Información Institucional del Refugio</span>
            <span v-else-if="activeTab === 'registrar'">{{ mascotaForm.id ? 'Editar Mascota' : 'Registrar Nueva Mascota' }}</span>
            <span v-else-if="activeTab === 'mis-mascotas'">Mis Mascotas Bajo Cuidado</span>
            <span v-else-if="activeTab === 'solicitudes'">Solicitudes de Adopción Recibidas</span>
            <span v-else-if="activeTab === 'entrevistas'">Gestión de Entrevistas</span>
            <span v-else-if="activeTab === 'veterinario'">Historial Veterinario y Atenciones</span>
            <span v-else-if="activeTab === 'adopciones'">Adopciones Concluidas con Éxito</span>
            <span v-else-if="activeTab === 'estadisticas'">Estadísticas y Métricas del Refugio</span>
          </h2>
          <p class="header-sub" v-if="refugio">Gestión integral &bull; {{ refugio.nombre }} ({{ refugio.ciudad }})</p>
        </div>

        <div class="header-tools">
          <button v-if="activeTab !== 'registrar'" class="btn btn-primary btn-sm" @click="resetMascotaForm(); activeTab = 'registrar'">
            <PlusCircle :size="16" />
            <span>Nueva Mascota</span>
          </button>
        </div>
      </header>

      <!-- Banner de alerta / feedback -->
      <div v-if="feedback.type" class="feedback-banner" :class="'banner-' + feedback.type">
        <Check v-if="feedback.type === 'success'" :size="18" />
        <AlertCircle v-else :size="18" />
        <span>{{ feedback.text }}</span>
      </div>

      <!-- ════════ 1. DASHBOARD ════════ -->
      <section v-if="activeTab === 'dashboard'" class="tab-pane">
        <div class="metrics-grid">
          <div class="stat-card">
            <span class="stat-val">{{ metricas.mascotas_registradas }}</span>
            <span class="stat-lbl">Mascotas Registradas</span>
          </div>
          <div class="stat-card stat-green">
            <span class="stat-val">{{ metricas.mascotas_disponibles }}</span>
            <span class="stat-lbl">Mascotas Disponibles</span>
          </div>
          <div class="stat-card stat-amber">
            <span class="stat-val">{{ metricas.mascotas_en_proceso }}</span>
            <span class="stat-lbl">Mascotas en Proceso</span>
          </div>
          <div class="stat-card stat-purple">
            <span class="stat-val">{{ metricas.mascotas_adoptadas }}</span>
            <span class="stat-lbl">Mascotas Adoptadas</span>
          </div>
          <div class="stat-card stat-orange">
            <span class="stat-val">{{ metricas.solicitudes_pendientes }}</span>
            <span class="stat-lbl">Solicitudes Pendientes</span>
          </div>
          <div class="stat-card stat-blue">
            <span class="stat-val">{{ metricas.entrevistas_programadas }}</span>
            <span class="stat-lbl">Entrevistas Programadas</span>
          </div>
        </div>

        <!-- Acciones rápidas de atención -->
        <div class="pane-card-box">
          <h3 class="box-title">Solicitudes que requieren revisión</h3>
          <div v-if="solicitudes.filter(s => s.estado === 'En revisión').length > 0" class="mini-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Mascota</th>
                  <th>Solicitante</th>
                  <th>Fecha</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sol in solicitudes.filter(s => s.estado === 'En revisión').slice(0, 5)" :key="sol.id">
                  <td>#{{ sol.id }}</td>
                  <td><strong>{{ sol.mascota_nombre }}</strong></td>
                  <td>{{ sol.usuario_nombre }}</td>
                  <td>{{ formatDate(sol.fecha_solicitud) }}</td>
                  <td>
                    <button class="btn btn-sm btn-primary" @click="activeTab = 'solicitudes'">
                      Gestionar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted">No tienes solicitudes pendientes de revisión inmediata.</p>
        </div>
      </section>

      <!-- ════════ 2. INFORMACIÓN DEL REFUGIO ════════ -->
      <section v-else-if="activeTab === 'info'" class="tab-pane">
        <div class="pane-card-box form-card-box" v-if="refugio">
          <form @submit.prevent="guardarInfoRefugio" class="stacked-form">
            <div class="form-group">
              <label class="label">Nombre del Refugio / Fundación</label>
              <input type="text" v-model="refugio.nombre" class="input" required />
            </div>
            <div class="two-columns">
              <div class="form-group">
                <label class="label">Ciudad</label>
                <input type="text" v-model="refugio.ciudad" class="input" required />
              </div>
              <div class="form-group">
                <label class="label">Teléfono de contacto</label>
                <input type="text" v-model="refugio.telefono" class="input" />
              </div>
            </div>
            <div class="form-group">
              <label class="label">Dirección física</label>
              <input type="text" v-model="refugio.direccion" class="input" />
            </div>
            <div class="form-group">
              <label class="label">Correo electrónico oficial</label>
              <input type="email" v-model="refugio.email" class="input" />
            </div>
            <button type="submit" class="btn btn-primary">
              Guardar Cambios del Refugio
            </button>
          </form>
        </div>
      </section>

      <!-- ════════ 3. REGISTRAR / EDITAR MASCOTA ════════ -->
      <section v-else-if="activeTab === 'registrar'" class="tab-pane">
        <div class="pane-card-box form-card-box">
          <form @submit.prevent="guardarMascota" class="stacked-form">
            <div class="two-columns">
              <div class="form-group">
                <label class="label">Nombre de la Mascota *</label>
                <input type="text" v-model="mascotaForm.nombre" class="input" required placeholder="Ej: Toby" />
              </div>
              <div class="form-group">
                <label class="label">Tipo de Animal *</label>
                <select v-model="mascotaForm.tipo" class="input select">
                  <option value="Perro">🐶 Perro</option>
                  <option value="Gato">🐱 Gato</option>
                </select>
              </div>
            </div>

            <div class="three-columns">
              <div class="form-group">
                <label class="label">Edad (en años) *</label>
                <input type="number" min="0" max="25" v-model="mascotaForm.edad" class="input" required />
              </div>
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

            <div class="two-columns">
              <div class="form-group">
                <label class="label">Raza</label>
                <input type="text" v-model="mascotaForm.raza" class="input" placeholder="Ej: Mestizo / Criollo" />
              </div>
              <div class="form-group">
                <label class="label">Ciudad</label>
                <input type="text" v-model="mascotaForm.ciudad" class="input" required />
              </div>
            </div>

            <div class="form-group">
              <label class="label">Descripción general</label>
              <textarea rows="2" v-model="mascotaForm.descripcion" class="input textarea" placeholder="Historia de rescate, comportamiento..."></textarea>
            </div>

            <div class="two-columns">
              <div class="form-group">
                <label class="label">Personalidad</label>
                <input type="text" v-model="mascotaForm.personalidad" class="input" placeholder="Ej: Juguetón, amigable, protector" />
              </div>
              <div class="form-group">
                <label class="label">Nivel de Energía</label>
                <select v-model="mascotaForm.nivel_energia" class="input select">
                  <option value="Baja">Baja</option>
                  <option value="Media">Media</option>
                  <option value="Alta">Alta</option>
                </select>
              </div>
            </div>

            <div class="two-columns">
              <div class="form-group">
                <label class="label">Estado de la Mascota</label>
                <select v-model="mascotaForm.estado" class="input select">
                  <option value="Disponible">Disponible</option>
                  <option value="En revisión">En revisión</option>
                  <option value="Adoptada">Adoptada</option>
                </select>
              </div>
            </div>

            <!-- Subida de Fotografía (Local desde dispositivo o URL externa) -->
            <div class="form-group photo-uploader-field">
              <label class="label">Fotografía de la Mascota</label>
              <div class="photo-upload-row">
                <input
                  type="file"
                  ref="refugioFileInput"
                  accept="image/png, image/jpeg, image/jpg, image/webp, image/gif"
                  @change="onRefugioFileSelected"
                  style="display: none"
                />
                <button
                  type="button"
                  class="btn btn-outline btn-sm btn-device-upload"
                  @click="$refs.refugioFileInput.click()"
                  :disabled="uploadingPhotoRefugio"
                >
                  <Upload :size="16" />
                  <span v-if="!uploadingPhotoRefugio">📁 Subir foto desde mi dispositivo</span>
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

              <!-- Vista previa miniatura -->
              <div v-if="mascotaForm.foto_url" class="photo-preview-card">
                <img :src="mascotaForm.foto_url" alt="Previsualización" class="photo-preview-thumbnail" />
                <div class="photo-preview-details">
                  <span class="preview-status-pill">✓ Fotografía vinculada</span>
                  <button type="button" class="btn-remove-photo" @click="mascotaForm.foto_url = ''">Quitar foto</button>
                </div>
              </div>
            </div>

            <!-- Compatibilidades y Estado de Salud -->
            <fieldset class="checks-fieldset">
              <legend>Compatibilidad y Salud Veterinaria</legend>
              <div class="checkboxes-grid">
                <label class="check-item">
                  <input type="checkbox" v-model="mascotaForm.compatible_ninos" />
                  <span>Compatible con niños</span>
                </label>
                <label class="check-item">
                  <input type="checkbox" v-model="mascotaForm.compatible_mascotas" />
                  <span>Compatible con otras mascotas</span>
                </label>
                <label class="check-item">
                  <input type="checkbox" v-model="mascotaForm.vacunado" />
                  <span>Vacunado al día</span>
                </label>
                <label class="check-item">
                  <input type="checkbox" v-model="mascotaForm.desparasitado" />
                  <span>Desparasitado</span>
                </label>
                <label class="check-item">
                  <input type="checkbox" v-model="mascotaForm.esterilizado" />
                  <span>Esterilizado</span>
                </label>
              </div>
            </fieldset>

            <div class="form-actions-row">
              <button type="submit" class="btn btn-primary">
                {{ mascotaForm.id ? 'Guardar Cambios de la Mascota' : 'Registrar Mascota en Refugio' }}
              </button>
              <button type="button" class="btn btn-outline" @click="activeTab = 'mis-mascotas'">
                Cancelar
              </button>
            </div>
          </form>
        </div>
      </section>

      <!-- ════════ 4. MIS MASCOTAS ════════ -->
      <section v-else-if="activeTab === 'mis-mascotas'" class="tab-pane">
        <div class="pane-card-box">
          <div class="box-header-row">
            <h3 class="box-title">Mascotas bajo administración de tu refugio</h3>
            <span class="count-chip">{{ misMascotas.length }} registradas</span>
          </div>

          <div v-if="misMascotas.length > 0" class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Tipo / Raza</th>
                  <th>Edad</th>
                  <th>Sexo</th>
                  <th>Salud</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in misMascotas" :key="m.id">
                  <td>
                    <strong>{{ m.nombre }}</strong>
                  </td>
                  <td>{{ m.tipo }} - {{ m.raza || 'Criollo' }}</td>
                  <td>{{ m.edad }} años</td>
                  <td>{{ m.sexo }}</td>
                  <td>
                    <div class="mini-chips">
                      <span v-if="m.vacunado" class="chip-mini chip-green">Vac</span>
                      <span v-if="m.desparasitado" class="chip-mini chip-green">Desp</span>
                      <span v-if="m.esterilizado" class="chip-mini chip-green">Est</span>
                    </div>
                  </td>
                  <td>
                    <span class="status-badge" :class="'badge-' + (m.estado || '').toLowerCase().replace(' ', '-')">
                      {{ m.estado }}
                    </span>
                  </td>
                  <td>
                    <div class="actions-group">
                      <button class="btn btn-sm btn-outline" @click="verDetalleMascota(m.id)" title="Ver perfil completo">
                        <Eye :size="15" />
                      </button>
                      <button class="btn btn-sm btn-outline" @click="editarMascota(m)" title="Editar información">
                        <Edit :size="15" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted">Aún no has registrado mascotas para este refugio.</p>
        </div>
      </section>

      <!-- ════════ 5. SOLICITUDES RECIBIDAS ════════ -->
      <section v-else-if="activeTab === 'solicitudes'" class="tab-pane">
        <div class="pane-card-box">
          <div class="box-header-row">
            <h3 class="box-title">Solicitudes de Adopción para Mascotas de tu Refugio</h3>
            <span class="count-chip">{{ solicitudes.length }} solicitudes</span>
          </div>

          <div v-if="solicitudes.length > 0" class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Mascota</th>
                  <th>Adoptante</th>
                  <th>Fecha</th>
                  <th>Vivienda</th>
                  <th>Estado</th>
                  <th>Gestión</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sol in solicitudes" :key="sol.id">
                  <td>#{{ sol.id }}</td>
                  <td><strong>{{ sol.mascota_nombre }}</strong> ({{ sol.mascota_tipo }})</td>
                  <td>
                    <div>
                      <strong>{{ sol.usuario_nombre }}</strong>
                      <div class="text-muted text-xs">@{{ sol.usuario_username }}</div>
                    </div>
                  </td>
                  <td>{{ formatDate(sol.fecha_solicitud) }}</td>
                  <td>{{ sol.lugar_mascota }}</td>
                  <td>
                    <span class="status-badge" :class="'badge-' + (sol.estado || '').toLowerCase().replace(' ', '-')">
                      {{ sol.estado }}
                    </span>
                  </td>
                  <td>
                    <div class="manage-btn-row">
                      <button
                        v-if="sol.estado === 'En revisión'"
                        class="btn btn-xs btn-primary"
                        @click="abrirModalEntrevista(sol)"
                      >
                        Programar entrevista
                      </button>
                      <button
                        v-if="sol.estado === 'Entrevista' || sol.estado === 'En revisión'"
                        class="btn btn-xs btn-green"
                        @click="cambiarEstadoSolicitud(sol.id, 'Aprobada')"
                      >
                        Aprobar
                      </button>
                      <button
                        v-if="sol.estado !== 'Rechazada' && sol.estado !== 'Aprobada'"
                        class="btn btn-xs btn-red"
                        @click="cambiarEstadoSolicitud(sol.id, 'Rechazada')"
                      >
                        Rechazar
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted">No has recibido solicitudes de adopción aún.</p>
        </div>
      </section>

      <!-- ════════ 6. ENTREVISTAS ════════ -->
      <section v-else-if="activeTab === 'entrevistas'" class="tab-pane">
        <div class="pane-card-box">
          <div class="box-header-row">
            <h3 class="box-title">Entrevistas Programadas y Realizadas</h3>
            <span class="count-chip">{{ entrevistas.length }} entrevistas</span>
          </div>

          <div v-if="entrevistas.length > 0" class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Fecha y Hora</th>
                  <th>Mascota</th>
                  <th>Adoptante</th>
                  <th>Modalidad</th>
                  <th>Observaciones</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ent in entrevistas" :key="ent.id">
                  <td>{{ formatDate(ent.fecha) }} &bull; {{ ent.hora }}</td>
                  <td><strong>{{ ent.mascota_nombre }}</strong></td>
                  <td>{{ ent.usuario_nombre }}</td>
                  <td><span class="modalidad-chip">{{ ent.modalidad }}</span></td>
                  <td>{{ ent.observaciones || '—' }}</td>
                  <td>
                    <span class="status-badge" :class="'badge-' + (ent.estado || '').toLowerCase()">
                      {{ ent.estado }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted">No tienes entrevistas registradas actualmente.</p>
        </div>
      </section>

      <!-- ════════ 7. HISTORIAL VETERINARIO ════════ -->
      <section v-else-if="activeTab === 'veterinario'" class="tab-pane">
        <!-- Formulario para registrar nuevo control -->
        <div class="pane-card-box form-card-box">
          <h3 class="box-title">Registrar Atención o Control Veterinario</h3>
          <form @submit.prevent="agregarControlVeterinario" class="stacked-form">
            <div class="two-columns">
              <div class="form-group">
                <label class="label">Mascota atendida *</label>
                <select v-model="controlForm.mascota_id" class="input select" required>
                  <option value="" disabled>Selecciona una mascota...</option>
                  <option v-for="m in misMascotas" :key="m.id" :value="m.id">
                    {{ m.nombre }} ({{ m.tipo }} - {{ m.raza }})
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label class="label">Tipo de atención *</label>
                <select v-model="controlForm.tipo" class="input select">
                  <option value="Vacuna">Vacuna</option>
                  <option value="Desparasitación">Desparasitación</option>
                  <option value="Control">Control General</option>
                  <option value="Esterilización">Esterilización</option>
                  <option value="Tratamiento">Tratamiento Médico</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="label">Descripción del procedimiento *</label>
              <input type="text" v-model="controlForm.descripcion" class="input" required placeholder="Ej: Aplicación de vacuna antirrábica y refuerzo anual" />
            </div>

            <div class="three-columns">
              <div class="form-group">
                <label class="label">Fecha de atención</label>
                <input type="date" v-model="controlForm.fecha" class="input" required />
              </div>
              <div class="form-group">
                <label class="label">Próxima fecha / Refuerzo</label>
                <input type="date" v-model="controlForm.proxima_fecha" class="input" />
              </div>
              <div class="form-group">
                <label class="label">Veterinario responsable</label>
                <input type="text" v-model="controlForm.veterinario" class="input" placeholder="Nombre del doctor/a" />
              </div>
            </div>

            <div class="form-group">
              <label class="label">Observaciones médicas</label>
              <textarea rows="2" v-model="controlForm.observaciones" class="input textarea" placeholder="Evolución clínica, peso, recomendaciones..."></textarea>
            </div>

            <button type="submit" class="btn btn-primary">
              Guardar Registro Veterinario
            </button>
          </form>
        </div>

        <!-- Tabla de controles registrados -->
        <div class="pane-card-box">
          <h3 class="box-title">Historial médico acumulado de tus mascotas</h3>
          <div v-if="historiales.length > 0" class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Mascota</th>
                  <th>Tipo</th>
                  <th>Descripción</th>
                  <th>Fecha</th>
                  <th>Próxima Cita</th>
                  <th>Veterinario</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in historiales" :key="h.id">
                  <td><strong>{{ h.mascota_nombre }}</strong></td>
                  <td><span class="modalidad-chip">{{ h.tipo }}</span></td>
                  <td>{{ h.descripcion }}</td>
                  <td>{{ formatDate(h.fecha) }}</td>
                  <td>{{ formatDate(h.proxima_fecha) }}</td>
                  <td>{{ h.veterinario }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted">Aún no hay controles veterinarios registrados.</p>
        </div>
      </section>

      <!-- ════════ 8. ADOPCIONES REALIZADAS ════════ -->
      <section v-else-if="activeTab === 'adopciones'" class="tab-pane">
        <div class="pane-card-box">
          <div class="box-header-row">
            <h3 class="box-title">Procesos de Adopción Finalizados con Éxito</h3>
            <span class="count-chip">{{ adopcionesFinalizadas.length }} adoptados</span>
          </div>

          <div v-if="adopcionesFinalizadas.length > 0" class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Mascota</th>
                  <th>Adoptante</th>
                  <th>Fecha Solicitud</th>
                  <th>Responsable Hogar</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="adop in adopcionesFinalizadas" :key="adop.id">
                  <td>#{{ adop.id }}</td>
                  <td><strong>{{ adop.mascota_nombre }}</strong> ({{ adop.mascota_tipo }})</td>
                  <td>{{ adop.usuario_nombre }}</td>
                  <td>{{ formatDate(adop.fecha_solicitud) }}</td>
                  <td>{{ adop.responsable }}</td>
                  <td><span class="status-badge badge-aprobada">Aprobada</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted">No se han concretado adopciones finalizadas aún.</p>
        </div>
      </section>

      <!-- ════════ 9. ESTADÍSTICAS ════════ -->
      <section v-else-if="activeTab === 'estadisticas'" class="tab-pane">
        <div class="metrics-grid">
          <div class="stat-card">
            <span class="stat-val">{{ misMascotas.length }}</span>
            <span class="stat-lbl">Total Mascotas</span>
          </div>
          <div class="stat-card stat-green">
            <span class="stat-val">{{ misMascotas.filter(m => m.tipo === 'Perro').length }}</span>
            <span class="stat-lbl">Perros</span>
          </div>
          <div class="stat-card stat-amber">
            <span class="stat-val">{{ misMascotas.filter(m => m.tipo === 'Gato').length }}</span>
            <span class="stat-lbl">Gatos</span>
          </div>
          <div class="stat-card stat-purple">
            <span class="stat-val">{{ adopcionesFinalizadas.length }}</span>
            <span class="stat-lbl">Adopciones Exitosas</span>
          </div>
        </div>

        <div class="pane-card-box">
          <h3 class="box-title">Distribución de mascotas por estado</h3>
          <div class="progress-bars-box">
            <div class="bar-row">
              <span>Disponibles: {{ metricas.mascotas_disponibles }}</span>
              <div class="bar-container">
                <div class="bar-fill bar-green" :style="{ width: ((metricas.mascotas_disponibles / (misMascotas.length || 1)) * 100) + '%' }"></div>
              </div>
            </div>
            <div class="bar-row">
              <span>Adoptadas: {{ metricas.mascotas_adoptadas }}</span>
              <div class="bar-container">
                <div class="bar-fill bar-purple" :style="{ width: ((metricas.mascotas_adoptadas / (misMascotas.length || 1)) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- MODAL PARA PROGRAMAR ENTREVISTA -->
    <div v-if="entrevistaModalData.show" class="modal-overlay" @click.self="entrevistaModalData.show = false">
      <div class="modal-content form-dialog-card">
        <button class="close-btn" @click="entrevistaModalData.show = false">&times;</button>
        <h3 class="dialog-title">Programar Entrevista</h3>
        <p class="dialog-sub">
          Mascota: <strong>{{ entrevistaModalData.mascota_nombre }}</strong> &bull; Solicitante: <strong>{{ entrevistaModalData.usuario_nombre }}</strong>
        </p>

        <form @submit.prevent="confirmarEntrevista" class="stacked-form">
          <div class="two-columns">
            <div class="form-group">
              <label class="label">Fecha</label>
              <input type="date" v-model="entrevistaModalData.fecha" class="input" required />
            </div>
            <div class="form-group">
              <label class="label">Hora</label>
              <input type="time" v-model="entrevistaModalData.hora" class="input" required />
            </div>
          </div>

          <div class="form-group">
            <label class="label">Modalidad</label>
            <select v-model="entrevistaModalData.modalidad" class="input select">
              <option value="Virtual">Virtual (Videollamada / Meet)</option>
              <option value="Presencial">Presencial en el refugio</option>
            </select>
          </div>

          <div class="form-group">
            <label class="label">Observaciones e Instrucciones</label>
            <textarea rows="2" v-model="entrevistaModalData.observaciones" class="input textarea"></textarea>
          </div>

          <div class="dialog-actions">
            <button type="submit" class="btn btn-primary">Confirmar y Programar</button>
            <button type="button" class="btn btn-outline" @click="entrevistaModalData.show = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL DETALLE DE MASCOTA -->
    <PetDetailModal
      v-if="showPetDetail && selectedPetProfile"
      :perfilData="selectedPetProfile"
      @close="showPetDetail = false"
    />
  </div>
</template>

<style scoped>
.refugio-layout {
  display: flex;
  min-height: 100vh;
  background-color: #FAF7F2;
  color: #2D3142;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.refugio-sidebar {
  width: 290px;
  background-color: #ffffff;
  border-right: 1px solid #E6DEC8;
  display: flex;
  flex-direction: column;
  padding: 1.8rem 1.2rem;
  box-sizing: border-box;
  flex-shrink: 0;
}

.brand-box {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
  margin-bottom: 1.2rem;
}

.heart-icon { color: #E07A5F; }
.brand-name {
  font-family: 'Outfit', sans-serif;
  font-size: 1.3rem;
  font-weight: 800;
  color: #1F2430;
}

.refugio-badge-card {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  background-color: #FAF7F2;
  border: 1px solid #EFE8DC;
  border-radius: 12px;
  padding: 0.75rem 0.9rem;
  margin-bottom: 1.5rem;
}

.badge-icon { color: #4E8752; }
.refugio-name { font-size: 0.92rem; font-weight: 700; margin: 0; color: #1F2430; }
.refugio-city { font-size: 0.75rem; color: #61677A; }

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
  padding: 0.7rem 0.95rem;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: #61677A;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
  position: relative;
}

.menu-item:hover { background-color: #F8F5EE; color: #1F2430; }
.menu-item.active { background-color: #F8EDE7; color: #E07A5F; font-weight: 700; }

.menu-counter {
  margin-left: auto;
  background-color: #EFE8DC;
  color: #2D3142;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.menu-counter.badge-amber { background-color: #FEF3C7; color: #D97706; }
.menu-counter.badge-green { background-color: #EDF7EE; color: #2E7D32; }

.sidebar-divider {
  height: 1px;
  background-color: #EFE8DC;
  margin: 1rem 0;
}

.btn-logout { color: #9B1C1C; }
.btn-logout:hover { background-color: #FDE8E8; color: #C81E1E; }

/* PANEL PRINCIPAL */
.refugio-main {
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

.header-sub {
  font-size: 0.9rem;
  color: #61677A;
  margin: 0.2rem 0 0;
}

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 1.8rem;
}

/* MÉTRICAS */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.2rem;
}

.stat-card {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 16px;
  padding: 1.3rem;
  display: flex;
  flex-direction: column;
}

.stat-val {
  font-family: 'Outfit', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: #1F2430;
  line-height: 1;
  margin-bottom: 0.4rem;
}

.stat-lbl {
  font-size: 0.84rem;
  color: #61677A;
  font-weight: 600;
}

.stat-green .stat-val { color: #2E7D32; }
.stat-amber .stat-val { color: #D97706; }
.stat-purple .stat-val { color: #7E3AF2; }
.stat-orange .stat-val { color: #E07A5F; }
.stat-blue .stat-val { color: #1A73E8; }

/* PANE CARDS Y TABLAS */
.pane-card-box {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 18px;
  padding: 1.8rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.box-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
}

.box-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.3rem;
  font-weight: 700;
  color: #1F2430;
  margin: 0 0 1rem;
}

.count-chip {
  background-color: #EFE8DC;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
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

.status-badge {
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
  white-space: nowrap;
}

.badge-disponible { background-color: #EDF7EE; color: #2E7D32; }
.badge-en-revisión { background-color: #FEF3C7; color: #D97706; }
.badge-entrevista { background-color: #E8F0FE; color: #1A73E8; }
.badge-adoptada { background-color: #F3F4F6; color: #4B5563; }
.badge-aprobada { background-color: #EDF7EE; color: #2E7D32; }
.badge-rechazada { background-color: #FDE8E8; color: #9B1C1C; }

.modalidad-chip {
  background-color: #F8EDE7;
  color: #E07A5F;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
}

.mini-chips {
  display: flex;
  gap: 0.3rem;
}

.chip-mini {
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-weight: 700;
}

.chip-green { background: #EDF7EE; color: #2E7D32; }

.manage-btn-row {
  display: flex;
  gap: 0.4rem;
}

.btn-xs {
  padding: 0.3rem 0.65rem;
  font-size: 0.78rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.btn-green { background-color: #2E7D32; color: #ffffff; }
.btn-red { background-color: #9B1C1C; color: #ffffff; }

/* FORMS */
.form-card-box {
  max-width: 820px;
}

.stacked-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.three-columns {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #2D3142;
}

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

.checks-fieldset {
  border: 1px solid #EFE8DC;
  border-radius: 12px;
  padding: 1.2rem;
  background-color: #FCFAF7;
}

.checks-fieldset legend {
  font-size: 0.85rem;
  font-weight: 700;
  color: #4E8752;
  padding: 0 0.5rem;
}

.checkboxes-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.88rem;
  cursor: pointer;
}

.form-actions-row {
  display: flex;
  gap: 0.8rem;
  margin-top: 0.5rem;
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

/* MODAL ENTREVISTA */
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
  max-width: 520px;
  width: 100%;
  background: #ffffff;
  border-radius: 20px;
  padding: 2rem;
  position: relative;
}

.dialog-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.4rem;
  margin: 0 0 0.3rem;
}

.dialog-sub {
  font-size: 0.88rem;
  color: #61677A;
  margin: 0 0 1.2rem;
}

.dialog-actions {
  display: flex;
  gap: 0.8rem;
  margin-top: 1rem;
}

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

/* PROGRESS BARS */
.progress-bars-box {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.bar-row {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.bar-container {
  height: 12px;
  background-color: #EFE8DC;
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.4s ease;
}

.bar-green { background-color: #2E7D32; }
.bar-purple { background-color: #7E3AF2; }

/* Subida de foto local y previsualización */
.photo-uploader-field {
  background: #fdfaf6;
  border: 1px dashed #e2dcd2;
  border-radius: 14px;
  padding: 1.1rem;
  margin: 0.5rem 0;
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
  min-width: 200px;
}

.photo-preview-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.9rem;
  padding: 0.65rem 0.9rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #E6DEC8;
}

.photo-preview-thumbnail {
  width: 58px;
  height: 58px;
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
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  text-align: left;
}

.btn-remove-photo:hover {
  text-decoration: underline;
}

@media (max-width: 900px) {
  .refugio-layout { flex-direction: column; }
  .refugio-sidebar { width: 100%; border-right: none; border-bottom: 1px solid #E6DEC8; }
  .sidebar-menu { flex-direction: row; flex-wrap: wrap; }
  .two-columns, .three-columns { grid-template-columns: 1fr; }
}
</style>
