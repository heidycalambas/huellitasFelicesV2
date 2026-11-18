<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useMascotasStore } from '@/stores/mascotasStore'
import { useFavoritosStore } from '@/stores/favoritosStore'
import { useAdopcionesStore } from '@/stores/adopcionesStore'
import mascotasService from '@/services/mascotasService'
import PetCard from '@/components/PetCard.vue'
import PetDetailModal from '@/components/PetDetailModal.vue'
import AdoptionModal from '@/components/AdoptionModal.vue'
import {
  Heart,
  Search,
  Filter,
  Sparkles,
  ShieldCheck,
  Home as HomeIcon,
  CheckCircle,
  Clock,
  Calendar,
  User,
  LogOut,
  Compass,
  FileText,
  Video,
  Smile,
  AlertCircle,
  Eye,
  RefreshCw,
  Building,
  Check,
  X,
  Lock,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const mascotasStore = useMascotasStore()
const favoritosStore = useFavoritosStore()
const adopcionesStore = useAdopcionesStore()

// Pestaña activa del menú del adoptante
// Inicio | Explorar mascotas | Mis favoritos | Mis solicitudes | Mis entrevistas | Mi perfil
const activeTab = ref('inicio')

// Modales
const showDetailModal = ref(false)
const showAdoptionModal = ref(false)
const showSolicitudDetailModal = ref(false)
const selectedPet = ref(null)
const selectedPetProfile = ref(null)
const selectedSolicitud = ref(null)

// Recomendaciones personalizadas
const recomendaciones = ref([])
const loadingRecomendaciones = ref(false)

// Filtros para explorar mascotas
const searchFilter = ref('')
const tipoFilter = ref('Todos')
const sexoFilter = ref('Todos')
const tamanoFilter = ref('Todos')
const ciudadFilter = ref('Todas')
const estadoFilter = ref('Disponible')
const edadFilter = ref('Todas')

// Formulario de perfil de usuario
const profileForm = reactive({
  nombre: '',
  usuario: '',
  edad: 25,
  ciudad: 'Popayán',
  tipo_vivienda: 'Casa',
  tiene_patio: true,
  otras_mascotas: false,
  tiempo_disponible: 'Alta',
  experiencia: '',
  preferencia_tipo: 'Todos',
  preferencia_tamano: 'Mediano',
  preferencia_edad: 'Joven',
  password: '',
  confirmPassword: '',
})
const profileSaveSuccess = ref(false)
const profileSaveError = ref(null)
const profileSaving = ref(false)

onMounted(async () => {
  await Promise.all([
    mascotasStore.fetchMascotas(),
    favoritosStore.fetchFavoritos(),
    favoritosStore.fetchIds(),
    adopcionesStore.fetchSolicitudes(),
    adopcionesStore.fetchEntrevistas(),
    loadUserProfile(),
  ])
  cargarRecomendaciones()
})

async function loadUserProfile() {
  const p = await authStore.fetchPerfil()
  if (p) {
    profileForm.nombre = p.nombre || ''
    profileForm.usuario = p.usuario || ''
    profileForm.edad = p.edad || 25
    profileForm.ciudad = p.ciudad || 'Popayán'
    profileForm.tipo_vivienda = p.tipo_vivienda || 'Casa'
    profileForm.tiene_patio = Boolean(p.tiene_patio)
    profileForm.otras_mascotas = Boolean(p.otras_mascotas)
    profileForm.tiempo_disponible = p.tiempo_disponible || 'Alta'
    profileForm.experiencia = p.experiencia || ''
    profileForm.preferencia_tipo = p.preferencia_tipo || 'Todos'
    profileForm.preferencia_tamano = p.preferencia_tamano || 'Mediano'
    profileForm.preferencia_edad = p.preferencia_edad || 'Joven'
  }
}

async function cargarRecomendaciones() {
  loadingRecomendaciones.value = true
  try {
    const res = await mascotasService.getRecomendaciones({
      tipo: profileForm.preferencia_tipo || 'Todos',
      tamano: profileForm.preferencia_tamano || 'Mediano',
      edad_min: 0,
      edad_max: 20,
    })
    recomendaciones.value = res.recomendaciones || []
  } catch (err) {
    recomendaciones.value = []
  } finally {
    loadingRecomendaciones.value = false
  }
}

// Lista de mascotas filtrada según criterios en tiempo real
const listaExplorar = computed(() => {
  return mascotasStore.mascotas.filter((pet) => {
    // Búsqueda por texto (nombre o raza)
    if (searchFilter.value.trim()) {
      const q = searchFilter.value.toLowerCase().trim()
      const matchName = pet.nombre?.toLowerCase().includes(q)
      const matchBreed = pet.raza?.toLowerCase().includes(q)
      if (!matchName && !matchBreed) return false
    }

    // Tipo (Perro o Gato)
    if (tipoFilter.value !== 'Todos') {
      if (pet.tipo?.toLowerCase() !== tipoFilter.value.toLowerCase()) return false
    }

    // Sexo
    if (sexoFilter.value !== 'Todos') {
      if (pet.sexo?.toLowerCase() !== sexoFilter.value.toLowerCase()) return false
    }

    // Tamaño
    if (tamanoFilter.value !== 'Todos') {
      if (pet.tamano?.toLowerCase() !== tamanoFilter.value.toLowerCase()) return false
    }

    // Ciudad
    if (ciudadFilter.value !== 'Todas') {
      if (!pet.ciudad?.toLowerCase().includes(ciudadFilter.value.toLowerCase())) return false
    }

    // Estado (por defecto Disponible)
    if (estadoFilter.value !== 'Todos') {
      if (pet.estado?.toLowerCase() !== estadoFilter.value.toLowerCase()) return false
    }

    // Edad
    if (edadFilter.value !== 'Todas') {
      const e = pet.edad
      if (edadFilter.value === 'Cachorro' && e > 1) return false
      if (edadFilter.value === 'Joven' && (e < 1 || e > 3)) return false
      if (edadFilter.value === 'Adulto' && (e < 4 || e > 7)) return false
      if (edadFilter.value === 'Senior' && e < 8) return false
    }

    return true
  })
})

function resetFiltros() {
  searchFilter.value = ''
  tipoFilter.value = 'Todos'
  sexoFilter.value = 'Todos'
  tamanoFilter.value = 'Todos'
  ciudadFilter.value = 'Todas'
  estadoFilter.value = 'Disponible'
  edadFilter.value = 'Todas'
}

// Abrir modal de detalle completo de mascota
async function handleVerDetalle(mascota) {
  selectedPet.value = mascota
  selectedPetProfile.value = { mascota }
  showDetailModal.value = true
  const perfil = await mascotasStore.fetchPerfil(mascota.id)
  if (perfil) {
    selectedPetProfile.value = perfil
  }
}

// Iniciar solicitud de adopción
function handleIniciarAdopcion(mascota) {
  selectedPet.value = mascota
  showDetailModal.value = false
  showAdoptionModal.value = true
}

// Recargar al completar adopción
async function handleAdopcionCompletada() {
  await Promise.all([
    mascotasStore.fetchMascotas(),
    adopcionesStore.fetchSolicitudes(),
  ])
}

// Ver detalle de una solicitud
function verDetalleSolicitud(solicitud) {
  selectedSolicitud.value = solicitud
  showSolicitudDetailModal.value = true
}

// Guardar cambios en el perfil de adoptante
async function guardarPerfil() {
  profileSaveError.value = null
  profileSaveSuccess.value = false

  if (profileForm.password && profileForm.password !== profileForm.confirmPassword) {
    profileSaveError.value = 'Las contraseñas no coinciden'
    return
  }

  profileSaving.value = true
  try {
    const payload = {
      nombre: profileForm.nombre,
      edad: Number(profileForm.edad),
      ciudad: profileForm.ciudad,
      tipo_vivienda: profileForm.tipo_vivienda,
      tiene_patio: profileForm.tiene_patio,
      otras_mascotas: profileForm.otras_mascotas,
      tiempo_disponible: profileForm.tiempo_disponible,
      experiencia: profileForm.experiencia,
      preferencia_tipo: profileForm.preferencia_tipo,
      preferencia_tamano: profileForm.preferencia_tamano,
      preferencia_edad: profileForm.preferencia_edad,
    }
    if (profileForm.password) {
      payload.password = profileForm.password
    }

    const res = await authStore.updatePerfil(payload)
    if (res.success) {
      profileSaveSuccess.value = true
      profileForm.password = ''
      profileForm.confirmPassword = ''
      cargarRecomendaciones()
      setTimeout(() => {
        profileSaveSuccess.value = false
      }, 4000)
    } else {
      profileSaveError.value = res.error || 'No se pudo guardar el perfil'
    }
  } catch (err) {
    profileSaveError.value = 'Error al conectar con el servidor'
  } finally {
    profileSaving.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push({ name: 'Login' })
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const parts = dateStr.split('-')
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`
  }
  return dateStr
}
</script>

<template>
  <div class="adoptante-app-layout">
    <!-- BARRA LATERAL / MENÚ DEL ADOPTANTE -->
    <aside class="sidebar-adoptante">
      <div class="sidebar-header">
        <div class="brand-logo" @click="activeTab = 'inicio'">
          <Heart :size="24" class="logo-heart" />
          <span class="brand-title">Huellitas Felices</span>
        </div>
        <div class="user-chip-sidebar">
          <div class="user-avatar-circle">
            <User :size="18" />
          </div>
          <div class="user-info-text">
            <span class="user-name-label">{{ authStore.userName }}</span>
            <span class="user-role-badge">Adoptante</span>
          </div>
        </div>
      </div>

      <!-- Menú de secciones del adoptante -->
      <nav class="sidebar-nav">
        <button
          type="button"
          class="nav-tab-btn"
          :class="{ active: activeTab === 'inicio' }"
          @click="activeTab = 'inicio'"
        >
          <HomeIcon :size="19" />
          <span>Inicio</span>
        </button>

        <button
          type="button"
          class="nav-tab-btn"
          :class="{ active: activeTab === 'explorar' }"
          @click="activeTab = 'explorar'"
        >
          <Compass :size="19" />
          <span>Explorar mascotas</span>
        </button>

        <button
          type="button"
          class="nav-tab-btn"
          :class="{ active: activeTab === 'favoritos' }"
          @click="activeTab = 'favoritos'"
        >
          <Heart :size="19" />
          <span>Mis favoritos</span>
          <span v-if="favoritosStore.totalFavoritos > 0" class="counter-badge">
            {{ favoritosStore.totalFavoritos }}
          </span>
        </button>

        <button
          type="button"
          class="nav-tab-btn"
          :class="{ active: activeTab === 'solicitudes' }"
          @click="activeTab = 'solicitudes'"
        >
          <FileText :size="19" />
          <span>Mis solicitudes</span>
          <span v-if="adopcionesStore.totalSolicitudes > 0" class="counter-badge">
            {{ adopcionesStore.totalSolicitudes }}
          </span>
        </button>

        <button
          type="button"
          class="nav-tab-btn"
          :class="{ active: activeTab === 'entrevistas' }"
          @click="activeTab = 'entrevistas'"
        >
          <Video :size="19" />
          <span>Mis entrevistas</span>
          <span v-if="adopcionesStore.entrevistasProgramadas > 0" class="counter-badge badge-green">
            {{ adopcionesStore.entrevistasProgramadas }}
          </span>
        </button>

        <button
          type="button"
          class="nav-tab-btn"
          :class="{ active: activeTab === 'perfil' }"
          @click="activeTab = 'perfil'"
        >
          <User :size="19" />
          <span>Mi perfil</span>
        </button>

        <div class="sidebar-divider"></div>

        <button type="button" class="nav-tab-btn btn-logout" @click="handleLogout">
          <LogOut :size="19" />
          <span>Cerrar sesión</span>
        </button>
      </nav>
    </aside>

    <!-- ÁREA PRINCIPAL DINÁMICA -->
    <main class="main-content-panel">
      <!-- Top header bar con bienvenida y accesos rápidos -->
      <header class="content-header-bar">
        <div>
          <h2 class="view-main-title">
            <span v-if="activeTab === 'inicio'">Panel Principal</span>
            <span v-else-if="activeTab === 'explorar'">Catálogo de Mascotas</span>
            <span v-else-if="activeTab === 'favoritos'">Mis Mascotas Favoritas</span>
            <span v-else-if="activeTab === 'solicitudes'">Mis Solicitudes de Adopción</span>
            <span v-else-if="activeTab === 'entrevistas'">Mis Entrevistas Programadas</span>
            <span v-else-if="activeTab === 'perfil'">Mi Perfil y Preferencias</span>
          </h2>
          <p class="view-sub-title">Bienvenido/a a la plataforma oficial de Huellitas Felices</p>
        </div>

        <div class="header-action-pills">
          <span class="city-pill">📍 {{ profileForm.ciudad || 'Popayán' }}</span>
          <button
            v-if="activeTab !== 'explorar'"
            class="btn btn-primary btn-sm"
            @click="activeTab = 'explorar'"
          >
            <Compass :size="16" />
            <span>Explorar Mascotas</span>
          </button>
        </div>
      </header>

      <!-- ═══════════════════════════════════════════════
           SECCIÓN 3.1: INICIO
           ═══════════════════════════════════════════════ -->
      <section v-if="activeTab === 'inicio'" class="tab-view-container">
        <!-- Saludo de bienvenida -->
        <div class="welcome-banner">
          <div class="welcome-text">
            <span class="welcome-chip">👋 ¡Hola, {{ authStore.userName }}!</span>
            <h1 class="welcome-heading">Bienvenido/a a Huellitas Felices</h1>
            <p class="welcome-desc">
              Aquí puedes encontrar a tu próximo compañero de vida, gestionar tus procesos de adopción y dar seguimiento a tus entrevistas veterinarias.
            </p>
            <button class="btn btn-primary btn-cta-inicio" @click="activeTab = 'explorar'">
              <Compass :size="18" />
              <span>Explorar mascotas disponibles</span>
            </button>
          </div>
        </div>

        <!-- Métricas principales -->
        <div class="metrics-grid">
          <div class="metric-card" @click="activeTab = 'explorar'">
            <div class="metric-icon icon-coral"><Heart :size="24" /></div>
            <div>
              <span class="metric-value">{{ mascotasStore.totalDisponibles }}</span>
              <span class="metric-label">Mascotas Disponibles</span>
            </div>
          </div>

          <div class="metric-card" @click="activeTab = 'solicitudes'">
            <div class="metric-icon icon-blue"><FileText :size="24" /></div>
            <div>
              <span class="metric-value">{{ adopcionesStore.totalSolicitudes }}</span>
              <span class="metric-label">Solicitudes Enviadas</span>
            </div>
          </div>

          <div class="metric-card" @click="activeTab = 'solicitudes'">
            <div class="metric-icon icon-amber"><Clock :size="24" /></div>
            <div>
              <span class="metric-value">{{ adopcionesStore.solicitudesEnRevision }}</span>
              <span class="metric-label">En Revisión</span>
            </div>
          </div>

          <div class="metric-card" @click="activeTab = 'favoritos'">
            <div class="metric-icon icon-red"><Heart :size="24" fill="#E07A5F" /></div>
            <div>
              <span class="metric-value">{{ favoritosStore.totalFavoritos }}</span>
              <span class="metric-label">Mascotas Favoritas</span>
            </div>
          </div>
        </div>

        <!-- Recomendaciones de mascotas según perfil -->
        <div class="section-card-panel">
          <div class="panel-header-row">
            <div>
              <h3 class="panel-title">Mascotas recomendadas para ti</h3>
              <p class="panel-subtitle">
                Basadas en tus preferencias: {{ profileForm.preferencia_tipo }} &bull; Tamaño {{ profileForm.preferencia_tamano }}
              </p>
            </div>
            <button class="btn-text-action" @click="activeTab = 'explorar'">Ver catálogo completo &rarr;</button>
          </div>

          <div v-if="recomendaciones.length > 0" class="pets-grid-cards">
            <PetCard
              v-for="pet in recomendaciones.slice(0, 3)"
              :key="pet.id"
              :mascota="pet"
              @verDetalle="handleVerDetalle"
              @iniciarAdopcion="handleIniciarAdopcion"
            />
          </div>
          <div v-else class="empty-notice-box">
            <Sparkles :size="24" />
            <p>Configura tus preferencias en tu perfil para recibir recomendaciones ideales.</p>
          </div>
        </div>

        <!-- Últimas actualizaciones -->
        <div class="section-card-panel">
          <h3 class="panel-title">Últimas actualizaciones</h3>
          <div v-if="adopcionesStore.solicitudes.length > 0" class="updates-timeline">
            <div
              v-for="sol in adopcionesStore.solicitudes.slice(0, 3)"
              :key="sol.id"
              class="timeline-item"
            >
              <div class="timeline-dot" :class="'dot-' + sol.estado.toLowerCase().replace(' ', '-')"></div>
              <div class="timeline-content">
                <strong>Solicitud #{{ sol.id }} para {{ sol.mascota_nombre }}</strong>
                <span class="timeline-status">Estado: {{ sol.estado }} &bull; Refugio: {{ sol.refugio_nombre }}</span>
                <span class="timeline-date">{{ formatDate(sol.fecha_solicitud) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-notice-box">
            <p>Aún no tienes solicitudes registradas. ¡Encuentra a tu mascota ideal en el catálogo!</p>
          </div>
        </div>
      </section>

      <!-- ═══════════════════════════════════════════════
           SECCIÓN 3.2: EXPLORAR MASCOTAS (CATÁLOGO MYSQL)
           ═══════════════════════════════════════════════ -->
      <section v-else-if="activeTab === 'explorar'" class="tab-view-container">
        <!-- Barra de Búsqueda y Filtros Exhaustivos -->
        <div class="filters-card-wrapper">
          <div class="search-input-row">
            <div class="search-box-wrap">
              <Search :size="18" class="search-icon" />
              <input
                type="text"
                v-model="searchFilter"
                placeholder="Buscar por nombre o raza (Ej: Luna, Pastor Alemán, Michi)..."
                class="search-text-input"
              />
            </div>
            <button class="btn btn-outline btn-reset-filters" @click="resetFiltros" title="Restablecer filtros">
              <RefreshCw :size="16" />
              <span>Limpiar filtros</span>
            </button>
          </div>

          <!-- Filtros de fila: Tipo, Edad, Sexo, Tamaño, Ciudad, Estado -->
          <div class="filters-chips-grid">
            <div class="filter-group">
              <label class="filter-label">Tipo</label>
              <select v-model="tipoFilter" class="filter-select">
                <option value="Todos">Todos (Perros y Gatos)</option>
                <option value="Perro">🐶 Perros</option>
                <option value="Gato">🐱 Gatos</option>
              </select>
            </div>

            <div class="filter-group">
              <label class="filter-label">Sexo</label>
              <select v-model="sexoFilter" class="filter-select">
                <option value="Todos">Todos</option>
                <option value="Macho">Macho</option>
                <option value="Hembra">Hembra</option>
              </select>
            </div>

            <div class="filter-group">
              <label class="filter-label">Tamaño</label>
              <select v-model="tamanoFilter" class="filter-select">
                <option value="Todos">Todos los tamaños</option>
                <option value="Pequeno">Pequeño</option>
                <option value="Mediano">Mediano</option>
                <option value="Grande">Grande</option>
              </select>
            </div>

            <div class="filter-group">
              <label class="filter-label">Etapa / Edad</label>
              <select v-model="edadFilter" class="filter-select">
                <option value="Todas">Todas las edades</option>
                <option value="Cachorro">Cachorro (&le; 1 año)</option>
                <option value="Joven">Joven (1 a 3 años)</option>
                <option value="Adulto">Adulto (4 a 7 años)</option>
                <option value="Senior">Senior (8+ años)</option>
              </select>
            </div>

            <div class="filter-group">
              <label class="filter-label">Ciudad</label>
              <select v-model="ciudadFilter" class="filter-select">
                <option value="Todas">Todas las ciudades</option>
                <option value="Popayan">Popayán</option>
                <option value="Cali">Cali</option>
                <option value="Bogota">Bogotá</option>
              </select>
            </div>

            <div class="filter-group">
              <label class="filter-label">Estado</label>
              <select v-model="estadoFilter" class="filter-select">
                <option value="Disponible">Solo Disponibles (Default)</option>
                <option value="En revisión">En revisión</option>
                <option value="Adoptada">Adoptadas</option>
                <option value="Todos">Todos los estados</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Indicador de total encontrado -->
        <div class="catalog-summary-bar">
          <span class="count-pill">
            Mostrando <strong>{{ listaExplorar.length }}</strong> mascotas registradas
          </span>
          <span v-if="estadoFilter === 'Disponible'" class="state-hint">
            (Filtrando únicamente mascotas en adopción disponibles)
          </span>
        </div>

        <!-- Grilla de Tarjetas con PetCard.vue -->
        <div v-if="listaExplorar.length > 0" class="pets-grid-cards">
          <PetCard
            v-for="pet in listaExplorar"
            :key="pet.id"
            :mascota="pet"
            @verDetalle="handleVerDetalle"
            @iniciarAdopcion="handleIniciarAdopcion"
          />
        </div>

        <!-- Estado vacío -->
        <div v-else class="empty-catalog-state">
          <AlertCircle :size="48" class="empty-icon" />
          <h3 class="empty-title">No encontramos mascotas con los filtros seleccionados</h3>
          <p class="empty-desc">Prueba ampliando tu búsqueda o restableciendo los filtros de ciudad, tamaño y edad.</p>
          <button class="btn btn-outline" @click="resetFiltros">
            Restablecer todos los filtros
          </button>
        </div>
      </section>

      <!-- ═══════════════════════════════════════════════
           SECCIÓN 3.4: MIS FAVORITOS
           ═══════════════════════════════════════════════ -->
      <section v-else-if="activeTab === 'favoritos'" class="tab-view-container">
        <div class="tab-header-box">
          <h3 class="section-title">Mascotas que has guardado en favoritos</h3>
          <p class="section-desc">Conserva a tus mascotas preferidas para revisar sus historiales o iniciar adopción cuando estés listo/a.</p>
        </div>

        <div v-if="favoritosStore.favoritos.length > 0" class="pets-grid-cards">
          <PetCard
            v-for="pet in favoritosStore.favoritos"
            :key="pet.id"
            :mascota="pet"
            @verDetalle="handleVerDetalle"
            @iniciarAdopcion="handleIniciarAdopcion"
          />
        </div>

        <div v-else class="empty-catalog-state">
          <Heart :size="48" class="empty-icon-coral" />
          <h3 class="empty-title">Aún no tienes mascotas en tus favoritos</h3>
          <p class="empty-desc">Haz clic en el corazón de cualquier tarjeta del catálogo para guardarla aquí.</p>
          <button class="btn btn-primary" @click="activeTab = 'explorar'">
            <Compass :size="18" />
            <span>Explorar catálogo</span>
          </button>
        </div>
      </section>

      <!-- ═══════════════════════════════════════════════
           SECCIÓN 3.5: MIS SOLICITUDES
           ═══════════════════════════════════════════════ -->
      <section v-else-if="activeTab === 'solicitudes'" class="tab-view-container">
        <div class="tab-header-box">
          <h3 class="section-title">Historial de solicitudes de adopción</h3>
          <p class="section-desc">Monitorea el estado y las observaciones de tus procesos con los refugios.</p>
        </div>

        <div v-if="adopcionesStore.solicitudes.length > 0" class="solicitudes-table-card">
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Mascota</th>
                  <th>Fecha</th>
                  <th>Refugio</th>
                  <th>Motivo</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sol in adopcionesStore.solicitudes" :key="sol.id">
                  <td><strong>#{{ sol.id }}</strong></td>
                  <td>
                    <div class="pet-table-chip">
                      <strong>{{ sol.mascota_nombre }}</strong>
                      <span class="sub-chip">{{ sol.mascota_tipo }}</span>
                    </div>
                  </td>
                  <td>{{ formatDate(sol.fecha_solicitud) }}</td>
                  <td>{{ sol.refugio_nombre || 'Refugio Aliado' }}</td>
                  <td class="motivo-cell">{{ sol.motivo }}</td>
                  <td>
                    <span
                      class="status-pill-table"
                      :class="'status-' + sol.estado.toLowerCase().replace(' ', '-')"
                    >
                      {{ sol.estado }}
                    </span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-outline" @click="verDetalleSolicitud(sol)">
                      <Eye :size="15" />
                      <span>Ver detalle</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-else class="empty-catalog-state">
          <FileText :size="48" class="empty-icon" />
          <h3 class="empty-title">No tienes solicitudes de adopción activas</h3>
          <p class="empty-desc">Cuando solicites una mascota, aquí podrás hacer seguimiento de la revisión, entrevista y aprobación.</p>
          <button class="btn btn-primary" @click="activeTab = 'explorar'">
            <span>Ir al catálogo</span>
          </button>
        </div>
      </section>

      <!-- ═══════════════════════════════════════════════
           SECCIÓN 3.6: MIS ENTREVISTAS
           ═══════════════════════════════════════════════ -->
      <section v-else-if="activeTab === 'entrevistas'" class="tab-view-container">
        <div class="tab-header-box">
          <h3 class="section-title">Entrevistas programadas de adopción</h3>
          <p class="section-desc">Revisa la fecha, hora y modalidad de tus entrevistas acordadas con los refugios.</p>
        </div>

        <div v-if="adopcionesStore.entrevistas.length > 0" class="entrevistas-cards-grid">
          <div
            v-for="ent in adopcionesStore.entrevistas"
            :key="ent.id"
            class="entrevista-card"
          >
            <div class="entrevista-card-header">
              <span class="modalidad-badge">{{ ent.modalidad || 'Virtual' }}</span>
              <span class="estado-entrevista" :class="'ent-' + ent.estado.toLowerCase()">
                {{ ent.estado }}
              </span>
            </div>

            <div class="entrevista-card-body">
              <h4 class="ent-pet-name">Mascota: <strong>{{ ent.mascota_nombre }}</strong></h4>
              <p class="ent-shelter">Refugio: <strong>{{ ent.refugio_nombre }}</strong> ({{ ent.refugio_ciudad }})</p>
              
              <div class="ent-meta-row">
                <span class="meta-item">
                  <Calendar :size="15" />
                  <span>{{ formatDate(ent.fecha) }}</span>
                </span>
                <span class="meta-item">
                  <Clock :size="15" />
                  <span>{{ ent.hora }}</span>
                </span>
              </div>

              <div class="ent-obs-box" v-if="ent.observaciones">
                <strong>Observaciones:</strong> {{ ent.observaciones }}
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-catalog-state">
          <Video :size="48" class="empty-icon" />
          <h3 class="empty-title">Aún no tienes entrevistas programadas</h3>
          <p class="empty-desc">Una vez que un refugio revise tu solicitud, coordinará contigo una entrevista virtual o presencial.</p>
        </div>
      </section>

      <!-- ═══════════════════════════════════════════════
           SECCIÓN 3.7: MI PERFIL Y PREFERENCIAS
           ═══════════════════════════════════════════════ -->
      <section v-else-if="activeTab === 'perfil'" class="tab-view-container">
        <div class="profile-card-container">
          <div class="tab-header-box">
            <h3 class="section-title">Información de tu Perfil y Preferencias</h3>
            <p class="section-desc">Mantén tus datos actualizados para agilizar tus formularios de adopción y recibir mejores recomendaciones.</p>
          </div>

          <div v-if="profileSaveSuccess" class="alert-box alert-success">
            <Check :size="18" />
            <span>Perfil actualizado exitosamente en el sistema.</span>
          </div>
          <div v-if="profileSaveError" class="alert-box alert-error">
            <AlertCircle :size="18" />
            <span>{{ profileSaveError }}</span>
          </div>

          <form @submit.prevent="guardarPerfil" class="profile-form">
            <!-- 1. Datos Personales -->
            <fieldset class="profile-fieldset">
              <legend>1. Información Personal</legend>
              <div class="two-columns">
                <div class="form-group">
                  <label class="label">Nombre completo</label>
                  <input type="text" v-model="profileForm.nombre" class="input" required />
                </div>
                <div class="form-group">
                  <label class="label">Usuario</label>
                  <input type="text" v-model="profileForm.usuario" class="input" disabled title="El nombre de usuario es tu identificador fijo" />
                </div>
              </div>

              <div class="two-columns">
                <div class="form-group">
                  <label class="label">Edad</label>
                  <input type="number" min="18" max="100" v-model="profileForm.edad" class="input" required />
                </div>
                <div class="form-group">
                  <label class="label">Ciudad</label>
                  <input type="text" v-model="profileForm.ciudad" class="input" required />
                </div>
              </div>
            </fieldset>

            <!-- 2. Información del Hogar -->
            <fieldset class="profile-fieldset">
              <legend>2. Información del Hogar</legend>
              <div class="form-group">
                <label class="label">Tipo de vivienda</label>
                <select v-model="profileForm.tipo_vivienda" class="input select">
                  <option value="Casa">Casa</option>
                  <option value="Apartamento">Apartamento</option>
                  <option value="Finca / Parcela">Finca / Parcela</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>

              <div class="two-columns">
                <div class="form-group">
                  <label class="label">¿Tiene patio o jardín?</label>
                  <select v-model="profileForm.tiene_patio" class="input select">
                    <option :value="true">Sí tiene patio</option>
                    <option :value="false">No tiene patio</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="label">¿Convive con otras mascotas?</label>
                  <select v-model="profileForm.otras_mascotas" class="input select">
                    <option :value="true">Sí tiene otras mascotas</option>
                    <option :value="false">No tiene otras mascotas</option>
                  </select>
                </div>
              </div>
            </fieldset>

            <!-- 3. Experiencia y Disponibilidad -->
            <fieldset class="profile-fieldset">
              <legend>3. Experiencia y Disponibilidad</legend>
              <div class="form-group">
                <label class="label">Tiempo diario disponible</label>
                <select v-model="profileForm.tiempo_disponible" class="input select">
                  <option value="Alta">Alto (Más de 5 horas o trabajo en casa)</option>
                  <option value="Media">Medio (2 a 4 horas al día)</option>
                  <option value="Baja">Bajo (1 a 2 horas al día)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="label">Experiencia con animales</label>
                <textarea rows="2" v-model="profileForm.experiencia" class="input textarea"></textarea>
              </div>
            </fieldset>

            <!-- 4. Preferencias de Adopción -->
            <fieldset class="profile-fieldset">
              <legend>4. Preferencias de Adopción</legend>
              <div class="three-columns">
                <div class="form-group">
                  <label class="label">Tipo de mascota</label>
                  <select v-model="profileForm.preferencia_tipo" class="input select">
                    <option value="Todos">Cualquiera / Ambos</option>
                    <option value="Perro">Perro</option>
                    <option value="Gato">Gato</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="label">Tamaño preferido</label>
                  <select v-model="profileForm.preferencia_tamano" class="input select">
                    <option value="Cualquiera">Cualquiera</option>
                    <option value="Pequeno">Pequeño</option>
                    <option value="Mediano">Mediano</option>
                    <option value="Grande">Grande</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="label">Edad preferida</label>
                  <select v-model="profileForm.preferencia_edad" class="input select">
                    <option value="Cualquiera">Cualquiera</option>
                    <option value="Cachorro">Cachorro</option>
                    <option value="Joven">Joven</option>
                    <option value="Adulto">Adulto</option>
                    <option value="Senior">Senior</option>
                  </select>
                </div>
              </div>
            </fieldset>

            <!-- 5. Seguridad (Opcional) -->
            <fieldset class="profile-fieldset">
              <legend>5. Seguridad (Dejar en blanco si no deseas cambiar contraseña)</legend>
              <div class="two-columns">
                <div class="form-group">
                  <label class="label">Nueva Contraseña</label>
                  <input type="password" v-model="profileForm.password" placeholder="••••••••" class="input" />
                </div>
                <div class="form-group">
                  <label class="label">Confirmar Nueva Contraseña</label>
                  <input type="password" v-model="profileForm.confirmPassword" placeholder="••••••••" class="input" />
                </div>
              </div>
            </fieldset>

            <div class="profile-actions">
              <button type="submit" class="btn btn-primary btn-save-profile" :disabled="profileSaving">
                <span v-if="!profileSaving">Guardar Cambios</span>
                <span v-else>Guardando...</span>
              </button>
            </div>
          </form>
        </div>
      </section>
    </main>

    <!-- ═══════════════════════════════════════════════
         MODALES
         ═══════════════════════════════════════════════ -->

    <!-- Modal 1: Detalle Completo de Mascota con Historial Veterinario -->
    <PetDetailModal
      v-if="showDetailModal && selectedPetProfile"
      :perfilData="selectedPetProfile"
      @close="showDetailModal = false"
      @iniciarAdopcion="handleIniciarAdopcion"
    />

    <!-- Modal 2: Formulario de Adopción Real -->
    <AdoptionModal
      v-if="showAdoptionModal && selectedPet"
      :mascota="selectedPet"
      @close="showAdoptionModal = false"
      @adopcionCompletada="handleAdopcionCompletada"
    />

    <!-- Modal 3: Detalle de Solicitud de Adopción -->
    <div
      v-if="showSolicitudDetailModal && selectedSolicitud"
      class="modal-overlay"
      @click.self="showSolicitudDetailModal = false"
    >
      <div class="modal-content info-dialog-card">
        <button class="close-btn-float" @click="showSolicitudDetailModal = false">&times;</button>
        <div class="info-dialog-header">
          <FileText :size="24" class="dialog-icon" />
          <div>
            <h3 class="dialog-title">Solicitud #{{ selectedSolicitud.id }}</h3>
            <p class="dialog-sub">Mascota: <strong>{{ selectedSolicitud.mascota_nombre }}</strong> &bull; Refugio: {{ selectedSolicitud.refugio_nombre }}</p>
          </div>
        </div>

        <div class="info-dialog-body">
          <div class="detail-row">
            <span class="d-label">Estado actual:</span>
            <span class="status-pill-table" :class="'status-' + selectedSolicitud.estado.toLowerCase().replace(' ', '-')">
              {{ selectedSolicitud.estado }}
            </span>
          </div>
          <div class="detail-row">
            <span class="d-label">Fecha de envío:</span>
            <span>{{ formatDate(selectedSolicitud.fecha_solicitud) }}</span>
          </div>
          <div class="detail-row">
            <span class="d-label">Motivo explicado:</span>
            <p class="d-text">{{ selectedSolicitud.motivo }}</p>
          </div>
          <div class="detail-row">
            <span class="d-label">Vivienda declarada:</span>
            <span>{{ selectedSolicitud.lugar_mascota }}</span>
          </div>
          <div class="detail-row">
            <span class="d-label">Personas en casa:</span>
            <span>{{ selectedSolicitud.personas_casa }}</span>
          </div>
          <div class="detail-row">
            <span class="d-label">Otras mascotas:</span>
            <span>{{ selectedSolicitud.tiene_otras_mascotas ? 'Sí' : 'No' }}</span>
          </div>
        </div>

        <div class="info-dialog-footer">
          <button class="btn btn-outline" @click="showSolicitudDetailModal = false">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.adoptante-app-layout {
  display: flex;
  min-height: 100vh;
  background-color: #FAF7F2;
  color: #2D3142;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

/* SIDEBAR DEL ADOPTANTE */
.sidebar-adoptante {
  width: 280px;
  background-color: #ffffff;
  border-right: 1px solid #E6DEC8;
  display: flex;
  flex-direction: column;
  padding: 1.8rem 1.2rem;
  box-sizing: border-box;
  flex-shrink: 0;
}

.sidebar-header {
  margin-bottom: 2rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
  margin-bottom: 1.4rem;
}

.logo-heart {
  color: #E07A5F;
}

.brand-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.35rem;
  font-weight: 800;
  color: #1F2430;
  letter-spacing: -0.4px;
}

.user-chip-sidebar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #FAF7F2;
  border: 1px solid #EFE8DC;
  border-radius: 14px;
  padding: 0.7rem 0.9rem;
}

.user-avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #F8EDE7;
  color: #E07A5F;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info-text {
  display: flex;
  flex-direction: column;
}

.user-name-label {
  font-size: 0.92rem;
  font-weight: 700;
  color: #1F2430;
}

.user-role-badge {
  font-size: 0.75rem;
  color: #4E8752;
  font-weight: 700;
}

/* MENÚ DE NAVEGACIÓN */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
}

.nav-tab-btn {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: #61677A;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
  position: relative;
}

.nav-tab-btn:hover {
  background-color: #F8F5EE;
  color: #2D3142;
}

.nav-tab-btn.active {
  background-color: #F8EDE7;
  color: #E07A5F;
  font-weight: 700;
}

.counter-badge {
  margin-left: auto;
  background-color: #E07A5F;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.counter-badge.badge-green {
  background-color: #4E8752;
}

.sidebar-divider {
  height: 1px;
  background-color: #EFE8DC;
  margin: 1rem 0;
}

.btn-logout {
  color: #9B1C1C;
}

.btn-logout:hover {
  background-color: #FDE8E8;
  color: #C81E1E;
}

/* ÁREA DE CONTENIDO PRINCIPAL */
.main-content-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 2rem 2.5rem;
  box-sizing: border-box;
}

.content-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #E6DEC8;
  padding-bottom: 1.2rem;
}

.view-main-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.85rem;
  font-weight: 800;
  color: #1F2430;
  margin: 0;
}

.view-sub-title {
  font-size: 0.9rem;
  color: #61677A;
  margin: 0.2rem 0 0;
}

.header-action-pills {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.city-pill {
  background-color: #ffffff;
  border: 1px solid #E0D9CD;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  font-size: 0.86rem;
  font-weight: 600;
  color: #4A4E69;
}

.tab-view-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 3.1: ESTILOS DE INICIO */
.welcome-banner {
  background: linear-gradient(135deg, #FAF2EB 0%, #F5EAE0 100%);
  border: 1px solid #ECDCCC;
  border-radius: 20px;
  padding: 2.2rem;
}

.welcome-chip {
  display: inline-block;
  background-color: #E07A5F;
  color: #ffffff;
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  margin-bottom: 0.8rem;
}

.welcome-heading {
  font-family: 'Outfit', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: #1F2430;
  margin: 0 0 0.6rem;
}

.welcome-desc {
  font-size: 1rem;
  line-height: 1.6;
  color: #4A4E69;
  max-width: 650px;
  margin-bottom: 1.4rem;
}

.btn-cta-inicio {
  padding: 0.75rem 1.4rem;
  font-size: 0.96rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.2rem;
}

.metric-card {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 16px;
  padding: 1.3rem;
  display: flex;
  align-items: center;
  gap: 1.1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.07);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-coral { background-color: #F8EDE7; color: #E07A5F; }
.icon-blue { background-color: #E8F0FE; color: #1A73E8; }
.icon-amber { background-color: #FEF3C7; color: #D97706; }
.icon-red { background-color: #FCE8E6; color: #D93025; }

.metric-value {
  display: block;
  font-family: 'Outfit', sans-serif;
  font-size: 1.7rem;
  font-weight: 800;
  color: #1F2430;
  line-height: 1;
}

.metric-label {
  font-size: 0.84rem;
  color: #61677A;
  font-weight: 600;
}

.section-card-panel {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 18px;
  padding: 1.8rem;
}

.panel-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.4rem;
}

.panel-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1F2430;
  margin: 0;
}

.panel-subtitle {
  font-size: 0.88rem;
  color: #61677A;
  margin: 0.25rem 0 0;
}

.btn-text-action {
  background: none;
  border: none;
  color: #E07A5F;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-text-action:hover {
  text-decoration: underline;
}

/* TIMELINE DE ACTUALIZACIONES */
.updates-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.8rem 1rem;
  background-color: #FAF7F2;
  border-radius: 12px;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.dot-en-revisión { background-color: #D97706; }
.dot-entrevista { background-color: #1A73E8; }
.dot-aprobada { background-color: #2E7D32; }
.dot-rechazada { background-color: #C05621; }

.timeline-content {
  display: flex;
  flex-direction: column;
  font-size: 0.9rem;
}

.timeline-status {
  font-size: 0.82rem;
  color: #61677A;
}

.timeline-date {
  font-size: 0.78rem;
  color: #8C92A4;
}

/* 3.2: FILTROS Y GRILLA DE MASCOTAS */
.filters-card-wrapper {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 18px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.search-input-row {
  display: flex;
  gap: 1rem;
}

.search-box-wrap {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 14px;
  color: #8C92A4;
}

.search-text-input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.6rem;
  border-radius: 12px;
  border: 1.5px solid #E0D9CD;
  background: #FAF7F2;
  font-size: 0.95rem;
  font-family: inherit;
  color: #2D3142;
  box-sizing: border-box;
}

.search-text-input:focus {
  outline: none;
  border-color: #E07A5F;
  background: #ffffff;
}

.btn-reset-filters {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.2rem;
  white-space: nowrap;
}

.filters-chips-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.8rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.filter-label {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #61677A;
  letter-spacing: 0.4px;
}

.filter-select {
  padding: 0.55rem 0.75rem;
  border-radius: 10px;
  border: 1.5px solid #E0D9CD;
  background: #ffffff;
  font-size: 0.86rem;
  color: #2D3142;
  font-family: inherit;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #E07A5F;
}

.catalog-summary-bar {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-size: 0.92rem;
  color: #4A4E69;
}

.count-pill {
  background-color: #EFE8DC;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  font-size: 0.85rem;
}

.state-hint {
  font-size: 0.82rem;
  color: #2E7D32;
  font-style: italic;
}

.pets-grid-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 1.5rem;
}

.empty-catalog-state {
  background: #ffffff;
  border: 1px dashed #D8CFC4;
  border-radius: 20px;
  padding: 3.5rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
}

.empty-icon { color: #8C92A4; }
.empty-icon-coral { color: #E07A5F; }

.empty-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.4rem;
  margin: 0;
  color: #1F2430;
}

.empty-desc {
  font-size: 0.95rem;
  color: #61677A;
  max-width: 480px;
  margin: 0;
}

/* 3.5 & 3.6: TABLAS Y TARJETAS DE SOLICITUDES Y ENTREVISTAS */
.tab-header-box {
  margin-bottom: 1rem;
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.45rem;
  font-weight: 800;
  color: #1F2430;
  margin: 0 0 0.3rem 0;
}

.section-desc {
  font-size: 0.92rem;
  color: #61677A;
  margin: 0;
}

.solicitudes-table-card {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  text-align: left;
}

.data-table th {
  background-color: #F8F5EE;
  color: #1F2430;
  padding: 0.9rem 1.1rem;
  font-weight: 700;
  border-bottom: 1px solid #E6DEC8;
  white-space: nowrap;
}

.data-table td {
  padding: 0.9rem 1.1rem;
  border-bottom: 1px solid #EFE8DC;
  color: #2D3142;
  vertical-align: middle;
}

.pet-table-chip {
  display: flex;
  flex-direction: column;
}

.sub-chip {
  font-size: 0.75rem;
  color: #8C92A4;
}

.motivo-cell {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-pill-table {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-en-revisión { background-color: #FEF3C7; color: #D97706; }
.status-entrevista { background-color: #E8F0FE; color: #1A73E8; }
.status-aprobada { background-color: #EDF7EE; color: #2E7D32; }
.status-rechazada { background-color: #FDE8E8; color: #9B1C1C; }

/* Entrevistas Grid */
.entrevistas-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.4rem;
}

.entrevista-card {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 16px;
  padding: 1.4rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.entrevista-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 1px solid #EFE8DC;
  padding-bottom: 0.8rem;
}

.modalidad-badge {
  background-color: #F8EDE7;
  color: #E07A5F;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
}

.estado-entrevista {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
}

.ent-programada { background-color: #FEF3C7; color: #D97706; }
.ent-realizada { background-color: #EDF7EE; color: #2E7D32; }
.ent-cancelada { background-color: #FDE8E8; color: #9B1C1C; }

.ent-pet-name {
  font-size: 1.15rem;
  color: #1F2430;
  margin: 0 0 0.3rem;
}

.ent-shelter {
  font-size: 0.88rem;
  color: #61677A;
  margin: 0 0 0.8rem;
}

.ent-meta-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.8rem;
}

.ent-obs-box {
  background-color: #FAF7F2;
  border-radius: 10px;
  padding: 0.7rem;
  font-size: 0.85rem;
  color: #4A4E69;
}

/* 3.7: PERFIL FORM */
.profile-card-container {
  background-color: #ffffff;
  border: 1px solid #E6DEC8;
  border-radius: 20px;
  padding: 2.2rem;
  max-width: 820px;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1rem;
}

.profile-fieldset {
  border: 1px solid #EFE8DC;
  border-radius: 14px;
  padding: 1.4rem;
  background-color: #FCFAF7;
}

.profile-fieldset legend {
  font-size: 0.9rem;
  font-weight: 700;
  color: #4E8752;
  padding: 0 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.three-columns {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.8rem;
}

.form-group {
  margin-bottom: 0.8rem;
}

.label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #2D3142;
  margin-bottom: 0.35rem;
}

.input {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border-radius: 10px;
  border: 1.5px solid #E0D9CD;
  background: #ffffff;
  font-size: 0.92rem;
  font-family: inherit;
  color: #2D3142;
  box-sizing: border-box;
}

.input:focus {
  outline: none;
  border-color: #E07A5F;
}

.input.textarea {
  resize: vertical;
}

.btn-save-profile {
  padding: 0.85rem 2rem;
  font-size: 1rem;
}

.alert-box {
  padding: 0.9rem 1.2rem;
  border-radius: 12px;
  margin-bottom: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.92rem;
}

.alert-success { background: #EDF7EE; color: #2E7D32; border: 1px solid #A5D6A7; }
.alert-error { background: #FDE8E8; color: #9B1C1C; border: 1px solid #F8B4B4; }

/* MODAL DE SOLICITUD DETALLE */
.info-dialog-card {
  max-width: 520px;
  width: 100%;
  background: #ffffff;
  border-radius: 20px;
  padding: 2rem;
  position: relative;
}

.close-btn-float {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #8C92A4;
  cursor: pointer;
}

.info-dialog-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  border-bottom: 1px solid #EFE8DC;
  padding-bottom: 1rem;
  margin-bottom: 1.2rem;
}

.dialog-icon { color: #E07A5F; }
.dialog-title { font-size: 1.35rem; margin: 0; color: #1F2430; }
.dialog-sub { font-size: 0.85rem; color: #61677A; margin: 0.2rem 0 0; }

.info-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  border-bottom: 1px dashed #EFE8DC;
  padding-bottom: 0.5rem;
}

.d-label { font-weight: 700; color: #61677A; }
.d-text { margin: 0; max-width: 300px; text-align: right; }

.info-dialog-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

/* RESPONSIVE */
@media (max-width: 1080px) {
  .filters-chips-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 820px) {
  .adoptante-app-layout {
    flex-direction: column;
  }
  .sidebar-adoptante {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #E6DEC8;
  }
  .sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .filters-chips-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
