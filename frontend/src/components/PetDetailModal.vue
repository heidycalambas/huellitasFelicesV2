<script setup>
import { computed } from 'vue'
import {
  X,
  Heart,
  MapPin,
  Calendar,
  Building,
  Phone,
  Mail,
  ShieldCheck,
  Smile,
  Zap,
  Activity,
  User,
  Stethoscope,
  Clock,
  AlertCircle,
} from 'lucide-vue-next'
import { useFavoritosStore } from '@/stores/favoritosStore'

const props = defineProps({
  perfilData: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'iniciarAdopcion'])
const favoritosStore = useFavoritosStore()

const mascota = computed(() => props.perfilData?.mascota || props.perfilData || {})
const refugio = computed(() => props.perfilData?.refugio || {})
const historial = computed(() => props.perfilData?.historial || [])

const isDisponible = computed(() => {
  return (mascota.value.estado || '').toLowerCase() === 'disponible'
})

const isFav = computed(() => {
  return mascota.value.id ? favoritosStore.isFavorito(mascota.value.id) : false
})

async function toggleFavorito() {
  if (mascota.value.id) {
    await favoritosStore.toggleFavorito(mascota.value)
  }
}

const petPhoto = computed(() => {
  if (mascota.value.foto_url) return mascota.value.foto_url

  const nombreLower = (mascota.value.nombre || '').toLowerCase()
  const tipoLower = (mascota.value.tipo || '').toLowerCase()

  if (nombreLower.includes('luna')) {
    return 'https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=800&q=80'
  }
  if (nombreLower.includes('max')) {
    return 'https://images.unsplash.com/photo-1589941013453-ec89f33b5e95?auto=format&fit=crop&w=800&q=80'
  }
  if (nombreLower.includes('michi')) {
    return 'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=800&q=80'
  }
  if (nombreLower.includes('simba')) {
    return 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80'
  }
  if (nombreLower.includes('rocky')) {
    return 'https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?auto=format&fit=crop&w=800&q=80'
  }
  if (nombreLower.includes('nala')) {
    return 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80'
  }

  if (tipoLower === 'gato') {
    return 'https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&w=800&q=80'
  }
  return 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80'
})

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const parts = dateStr.split('-')
    if (parts.length === 3) {
      return `${parts[2]}/${parts[1]}/${parts[0]}`
    }
    return dateStr
  } catch (e) {
    return dateStr
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content pet-modal">
      <!-- Botón Cerrar -->
      <button class="close-btn" @click="emit('close')" title="Cerrar modal">
        <X :size="20" />
      </button>

      <!-- Encabezado con Imagen y Acciones Rápidas -->
      <div class="modal-header-image">
        <img :src="petPhoto" :alt="mascota.nombre" class="modal-cover-img" />
        <div class="modal-header-overlay">
          <div class="badge-row">
            <span class="status-pill" :class="{ 'pill-adoptada': !isDisponible }">
              {{ mascota.estado || 'Disponible' }}
            </span>
            <span class="type-pill">{{ mascota.tipo }}</span>
          </div>
          <h2 class="pet-title">{{ mascota.nombre }}</h2>
          <p class="pet-subtitle">{{ mascota.raza || 'Criollo' }} &bull; {{ mascota.ciudad }}</p>
        </div>

        <!-- Botón flotante para favoritos -->
        <button
          type="button"
          class="fav-toggle-floating"
          :class="{ active: isFav }"
          @click="toggleFavorito"
          :title="isFav ? 'Quitar de favoritos' : 'Agregar a favoritos'"
        >
          <Heart :size="20" :fill="isFav ? '#E07A5F' : 'none'" />
        </button>
      </div>

      <!-- Contenido Detallado de la Mascota -->
      <div class="modal-body">
        
        <!-- ── 1. FICHA TÉCNICA PRINCIPAL ── -->
        <div class="attr-grid">
          <div class="attr-card">
            <span class="attr-label">Edad</span>
            <span class="attr-val">{{ mascota.edad }} {{ mascota.edad === 1 ? 'año' : 'años' }}</span>
          </div>
          <div class="attr-card">
            <span class="attr-label">Sexo</span>
            <span class="attr-val">{{ mascota.sexo || 'N/A' }}</span>
          </div>
          <div class="attr-card">
            <span class="attr-label">Tamaño</span>
            <span class="attr-val">{{ mascota.tamano || 'Mediano' }}</span>
          </div>
          <div class="attr-card">
            <span class="attr-label">Nivel de Energía</span>
            <span class="attr-val">{{ mascota.nivel_energia || 'Media' }}</span>
          </div>
        </div>

        <!-- ── 2. DESCRIPCIÓN ── -->
        <div class="section-block">
          <h4 class="section-title">Sobre {{ mascota.nombre }}</h4>
          <p class="section-text">
            {{ mascota.descripcion || 'Esta mascota busca un hogar responsable y cariñoso donde compartir su vida.' }}
          </p>
        </div>

        <!-- ── 3. PERSONALIDAD Y CONVIVENCIA ── -->
        <div class="section-block">
          <h4 class="section-title">Personalidad y Convivencia</h4>
          <div class="features-list">
            <div class="feature-item">
              <Smile :size="18" class="feat-icon" />
              <span>Personalidad: <strong>{{ mascota.personalidad || 'Amigable y sociable' }}</strong></span>
            </div>
            <div class="feature-item">
              <ShieldCheck :size="18" class="feat-icon" />
              <span>Compatible con niños: <strong>{{ mascota.compatible_ninos ? 'Sí' : 'No' }}</strong></span>
            </div>
            <div class="feature-item">
              <ShieldCheck :size="18" class="feat-icon" />
              <span>Compatible con otras mascotas: <strong>{{ mascota.compatible_mascotas ? 'Sí' : 'No' }}</strong></span>
            </div>
          </div>
        </div>

        <!-- ── 4. RESUMEN VETERINARIO ── -->
        <div class="section-block">
          <h4 class="section-title">Información Veterinaria</h4>
          <div class="health-badges">
            <div class="health-chip" :class="{ 'chip-active': mascota.vacunado, 'chip-inactive': !mascota.vacunado }">
              <ShieldCheck :size="16" />
              <span>Vacunado: <strong>{{ mascota.vacunado ? 'Sí' : 'No' }}</strong></span>
            </div>
            <div class="health-chip" :class="{ 'chip-active': mascota.desparasitado, 'chip-inactive': !mascota.desparasitado }">
              <ShieldCheck :size="16" />
              <span>Desparasitado: <strong>{{ mascota.desparasitado ? 'Sí' : 'No' }}</strong></span>
            </div>
            <div class="health-chip" :class="{ 'chip-active': mascota.esterilizado, 'chip-inactive': !mascota.esterilizado }">
              <ShieldCheck :size="16" />
              <span>Esterilizado: <strong>{{ mascota.esterilizado ? 'Sí' : 'No' }}</strong></span>
            </div>
          </div>
        </div>

        <!-- ── 5. HISTORIAL VETERINARIO COMPLETO (TABLA CRONOLÓGICA) ── -->
        <div class="section-block vet-history-section">
          <div class="section-title-wrap">
            <Stethoscope :size="20" class="vet-icon-head" />
            <h4 class="section-title">Historial veterinario de {{ mascota.nombre }}</h4>
          </div>

          <div v-if="historial && historial.length > 0" class="table-responsive">
            <table class="vet-table">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Descripción</th>
                  <th>Fecha</th>
                  <th>Próxima fecha</th>
                  <th>Veterinario</th>
                  <th>Observaciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in historial" :key="item.id">
                  <td>
                    <span class="vet-type-pill">{{ item.tipo }}</span>
                  </td>
                  <td>{{ item.descripcion }}</td>
                  <td class="date-cell">{{ formatDate(item.fecha) }}</td>
                  <td class="date-cell">
                    <span v-if="item.proxima_fecha" class="next-date-pill">
                      {{ formatDate(item.proxima_fecha) }}
                    </span>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td>{{ item.veterinario || 'Profesional de refugio' }}</td>
                  <td class="obs-cell">{{ item.observaciones || 'Sin observaciones' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="empty-history-box">
            <AlertCircle :size="24" class="empty-icon" />
            <p>Esta mascota todavía no tiene registros veterinarios previos en la plataforma.</p>
          </div>
        </div>

        <!-- ── 6. INFORMACIÓN DEL REFUGIO ── -->
        <div class="section-block refuge-block" v-if="refugio && refugio.nombre">
          <h4 class="section-title">
            <Building :size="18" class="refuge-icon" />
            <span>Refugio Responsable</span>
          </h4>
          <div class="refuge-details">
            <p class="refuge-name"><strong>{{ refugio.nombre }}</strong></p>
            <p v-if="refugio.direccion" class="refuge-meta">
              <MapPin :size="15" /> {{ refugio.direccion }}, {{ refugio.ciudad }}
            </p>
            <p v-if="refugio.telefono" class="refuge-meta">
              <Phone :size="15" /> {{ refugio.telefono }}
            </p>
            <p v-if="refugio.email" class="refuge-meta">
              <Mail :size="15" /> {{ refugio.email }}
            </p>
          </div>
        </div>

        <!-- ── 7. ACCIONES INFERIORES ── -->
        <div class="modal-footer">
          <button type="button" class="btn btn-outline" @click="emit('close')">
            Volver al catálogo
          </button>

          <button
            type="button"
            class="btn btn-fav-action"
            :class="{ active: isFav }"
            @click="toggleFavorito"
          >
            <Heart :size="17" :fill="isFav ? '#E07A5F' : 'none'" />
            <span>{{ isFav ? 'En mis favoritos' : 'Agregar a favoritos' }}</span>
          </button>

          <button
            v-if="isDisponible"
            type="button"
            class="btn btn-primary btn-adopt"
            @click="emit('iniciarAdopcion', mascota)"
          >
            <Heart :size="18" />
            <span>Solicitar adopción</span>
          </button>
          <button
            v-else
            type="button"
            class="btn btn-disabled"
            disabled
            title="La mascota ya no está disponible para nuevos procesos de adopción"
          >
            Mascota {{ mascota.estado }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(45, 49, 66, 0.55);
  backdrop-filter: blur(5px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.pet-modal {
  background: #ffffff;
  border-radius: 24px;
  max-width: 780px;
  width: 100%;
  max-height: 92vh;
  overflow-y: auto;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.22);
  position: relative;
  display: flex;
  flex-direction: column;
}

.close-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 20;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  color: #2D3142;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #ffffff;
  transform: scale(1.08);
}

.fav-toggle-floating {
  position: absolute;
  top: 14px;
  right: 60px;
  z-index: 20;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  color: #61677A;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.fav-toggle-floating:hover {
  transform: scale(1.1);
  color: #E07A5F;
}

.fav-toggle-floating.active {
  color: #E07A5F;
}

.modal-header-image {
  position: relative;
  height: 290px;
  width: 100%;
  background: #F3EDE2;
}

.modal-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-header-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1.8rem 2rem 1.4rem;
  background: linear-gradient(to top, rgba(20, 20, 28, 0.88) 0%, transparent 100%);
  color: #ffffff;
}

.badge-row {
  display: flex;
  gap: 0.6rem;
  margin-bottom: 0.4rem;
}

.status-pill {
  background-color: #2e7d32;
  color: #ffffff;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
}

.status-pill.pill-adoptada {
  background-color: #61677A;
}

.type-pill {
  background-color: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(4px);
  color: #ffffff;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
}

.pet-title {
  font-family: 'Outfit', sans-serif;
  font-size: 2.1rem;
  font-weight: 800;
  margin: 0;
  color: #ffffff;
}

.pet-subtitle {
  font-size: 0.95rem;
  opacity: 0.9;
  margin: 0.25rem 0 0;
}

.modal-body {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.8rem;
}

.attr-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.attr-card {
  background: #FAF7F2;
  border: 1px solid #EFE8DC;
  border-radius: 14px;
  padding: 0.9rem;
  text-align: center;
}

.attr-label {
  display: block;
  font-size: 0.76rem;
  color: #61677A;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.4px;
  margin-bottom: 0.3rem;
}

.attr-val {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1F2430;
}

.section-block {
  border-bottom: 1px solid #EFE8DC;
  padding-bottom: 1.5rem;
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: #1F2430;
  margin: 0 0 0.8rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
}

.vet-icon-head {
  color: #4E8752;
}

.section-text {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #4A4E69;
  margin: 0;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.92rem;
  color: #2D3142;
}

.feat-icon {
  color: #E07A5F;
}

.health-badges {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.health-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.5rem 0.95rem;
  border-radius: 999px;
  font-size: 0.88rem;
  border: 1px solid #D8CFC4;
  background: #FAF7F2;
  color: #61677A;
}

.health-chip.chip-active {
  background: #EDF7EE;
  color: #2E7D32;
  border-color: #A5D6A7;
}

.health-chip.chip-inactive {
  background: #FDF2E9;
  color: #C05621;
  border-color: #FBD38D;
}

/* Tabla veterinaria */
.table-responsive {
  width: 100%;
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid #E6DEC8;
}

.vet-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
  text-align: left;
}

.vet-table th {
  background-color: #F3EDE2;
  color: #1F2430;
  padding: 0.75rem 1rem;
  font-weight: 700;
  border-bottom: 1px solid #E6DEC8;
  white-space: nowrap;
}

.vet-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #EFE8DC;
  color: #2D3142;
}

.vet-table tr:last-child td {
  border-bottom: none;
}

.vet-type-pill {
  background-color: #E8F0FE;
  color: #1A73E8;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.78rem;
}

.next-date-pill {
  background-color: #FEF3C7;
  color: #D97706;
  padding: 0.18rem 0.55rem;
  border-radius: 6px;
  font-weight: 600;
}

.empty-history-box {
  background: #FAF7F2;
  border: 1px dashed #D8CFC4;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  color: #61677A;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.empty-icon {
  color: #8C92A4;
}

/* Bloque refugio */
.refuge-block {
  background-color: #FAF7F2;
  border-radius: 14px;
  padding: 1.2rem;
  border: 1px solid #EFE8DC;
}

.refuge-icon {
  color: #4E8752;
}

.refuge-details {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.refuge-name {
  font-size: 1.05rem;
  margin: 0;
  color: #1F2430;
}

.refuge-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.88rem;
  color: #61677A;
  margin: 0;
}

/* Footer modal */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.btn-fav-action {
  background-color: #FAF7F2;
  border: 1.5px solid #D8CFC4;
  color: #2D3142;
  padding: 0.65rem 1.1rem;
  border-radius: 10px;
  font-size: 0.92rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-fav-action:hover {
  border-color: #E07A5F;
  color: #E07A5F;
}

.btn-fav-action.active {
  border-color: #E07A5F;
  background-color: #FDF2E9;
  color: #E07A5F;
}

.btn-adopt {
  padding: 0.75rem 1.4rem;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-disabled {
  background-color: #F3EDE2;
  color: #8C92A4;
  padding: 0.75rem 1.4rem;
  border-radius: 10px;
  border: 1px solid #D8CFC4;
  font-size: 0.95rem;
  cursor: not-allowed;
}

@media (max-width: 650px) {
  .attr-grid {
    grid-template-columns: 1fr 1fr;
  }
  .modal-footer {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
