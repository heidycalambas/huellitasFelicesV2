<script setup>
import { onMounted, ref } from 'vue'
import { useAdopcionesStore } from '@/stores/adopcionesStore'
import { useAuthStore } from '@/stores/authStore'
import adopcionesService from '@/services/adopcionesService'
import { X, FileText, Calendar, Check, AlertCircle, RefreshCw } from 'lucide-vue-next'

const emit = defineEmits(['close'])
const adopcionesStore = useAdopcionesStore()
const authStore = useAuthStore()

const updatingId = ref(null)

onMounted(async () => {
  await adopcionesStore.fetchSolicitudes()
})

async function cambiarEstado(id, nuevoEstado) {
  updatingId.value = id
  try {
    await adopcionesService.actualizarEstado(id, nuevoEstado)
    await adopcionesStore.fetchSolicitudes()
  } catch (err) {
    console.error(err)
  } finally {
    updatingId.value = null
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content adoptions-modal">
      <button class="close-btn" @click="emit('close')" title="Cerrar">
        <X :size="20" />
      </button>

      <div class="modal-header">
        <div class="header-icon">
          <FileText :size="24" />
        </div>
        <div>
          <h2 class="title">{{ authStore.isAdmin ? 'Gestión de Solicitudes (Admin)' : 'Mis Solicitudes de Adopción' }}</h2>
          <p class="subtitle">Historial de solicitudes registradas en la base de datos.</p>
        </div>
      </div>

      <!-- Estado de Carga -->
      <div v-if="adopcionesStore.loading" class="loading-state">
        <RefreshCw :size="24" class="spin-icon" />
        <span>Cargando solicitudes...</span>
      </div>

      <!-- Sin solicitudes -->
      <div v-else-if="adopcionesStore.solicitudes.length === 0" class="empty-state">
        <FileText :size="48" class="empty-icon" />
        <h4>No tienes solicitudes registradas</h4>
        <p>Explora nuestro catálogo y selecciona "Adoptar" para iniciar un proceso.</p>
      </div>

      <!-- Lista de Solicitudes -->
      <div v-else class="solicitudes-list">
        <div
          v-for="sol in adopcionesStore.solicitudes"
          :key="sol.id"
          class="solicitud-card"
        >
          <div class="sol-top">
            <div>
              <h4 class="mascota-title">{{ sol.mascota_nombre }}</h4>
              <span class="sol-date">
                <Calendar :size="14" /> Solicitado el: {{ sol.fecha_solicitud }}
              </span>
            </div>
            <span
              class="sol-badge"
              :class="{
                'badge-rev': sol.estado === 'En revisión',
                'badge-ent': sol.estado === 'Entrevista',
                'badge-apr': sol.estado === 'Aprobada',
                'badge-rec': sol.estado === 'Rechazada' || sol.estado === 'Cancelada',
              }"
            >
              {{ sol.estado }}
            </span>
          </div>

          <div class="sol-details">
            <p><strong>Responsable:</strong> {{ sol.responsable }} ({{ sol.usuario_nombre }})</p>
            <p><strong>Lugar:</strong> {{ sol.lugar_mascota }}</p>
            <p><strong>Motivo:</strong> {{ sol.motivo }}</p>
            <p v-if="sol.experiencia"><strong>Experiencia:</strong> {{ sol.experiencia }}</p>
          </div>

          <!-- Acciones de Administrador para cambiar estado -->
          <div v-if="authStore.isAdmin" class="admin-actions">
            <span class="admin-label">Cambiar Estado:</span>
            <button
              class="btn-state btn-ent"
              :disabled="updatingId === sol.id"
              @click="cambiarEstado(sol.id, 'Entrevista')"
            >
              Entrevista
            </button>
            <button
              class="btn-state btn-apr"
              :disabled="updatingId === sol.id"
              @click="cambiarEstado(sol.id, 'Aprobada')"
            >
              Aprobar
            </button>
            <button
              class="btn-state btn-rec"
              :disabled="updatingId === sol.id"
              @click="cambiarEstado(sol.id, 'Rechazada')"
            >
              Rechazar
            </button>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-outline" @click="emit('close')">
          Cerrar
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.adoptions-modal {
  max-width: 680px;
  padding: 1.85rem;
}

.close-btn {
  position: absolute;
  top: 18px;
  right: 18px;
  color: var(--color-text-muted);
}

.modal-header {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.title {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--color-text);
}

.subtitle {
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.loading-state, .empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.empty-icon {
  color: var(--color-border);
}

.spin-icon {
  animation: spin 1s linear infinite;
  color: var(--color-primary);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.solicitudes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 55vh;
  overflow-y: auto;
  padding-right: 0.35rem;
}

.solicitud-card {
  background-color: var(--color-cream);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.sol-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.mascota-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--color-text);
}

.sol-date {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  gap: 0.3rem;
  margin-top: 0.15rem;
}

.sol-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 700;
}

.badge-rev {
  background-color: #fef3c7;
  color: #d97706;
}

.badge-ent {
  background-color: #e0e7ff;
  color: #4338ca;
}

.badge-apr {
  background-color: #dcfce7;
  color: #15803d;
}

.badge-rec {
  background-color: #fee2e2;
  color: #b91c1c;
}

.sol-details {
  font-size: 0.88rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  background: #ffffff;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sol-details strong {
  color: var(--color-text);
}

.admin-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
}

.admin-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-text-muted);
}

.btn-state {
  padding: 0.3rem 0.65rem;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.btn-ent {
  background-color: #e0e7ff;
  color: #4338ca;
}

.btn-apr {
  background-color: #dcfce7;
  color: #15803d;
}

.btn-rec {
  background-color: #fee2e2;
  color: #b91c1c;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
</style>
