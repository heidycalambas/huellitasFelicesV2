<script setup>
import { useAuthStore } from '@/stores/authStore'
import { X, User, MapPin, Home, Shield, Award, Calendar } from 'lucide-vue-next'

const emit = defineEmits(['close'])
const authStore = useAuthStore()
const user = authStore.user || {}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content profile-modal">
      <button class="close-btn" @click="emit('close')" title="Cerrar">
        <X :size="20" />
      </button>

      <div class="profile-header">
        <div class="avatar-large">
          {{ (user.nombre || user.usuario || 'U').charAt(0).toUpperCase() }}
        </div>
        <div class="profile-titles">
          <h2 class="user-fullname">{{ user.nombre || user.usuario }}</h2>
          <span class="user-badge">{{ user.rol || 'Adoptante' }}</span>
        </div>
      </div>

      <div class="profile-details-grid">
        <div class="p-item">
          <span class="p-label"><User :size="15" /> Nombre de usuario</span>
          <span class="p-val">@{{ user.usuario }}</span>
        </div>
        <div class="p-item">
          <span class="p-label"><MapPin :size="15" /> Ciudad</span>
          <span class="p-val">{{ user.ciudad || 'No especificada' }}</span>
        </div>
        <div class="p-item">
          <span class="p-label"><Home :size="15" /> Tipo de Vivienda</span>
          <span class="p-val">{{ user.tipo_vivienda || 'Casa' }}</span>
        </div>
        <div class="p-item">
          <span class="p-label"><Award :size="15" /> Rol de Cuenta</span>
          <span class="p-val">{{ user.rol === 'admin' ? 'Administrador del Sistema' : 'Adoptante Registrado' }}</span>
        </div>
      </div>

      <div class="profile-extra" v-if="user.experiencia">
        <span class="p-label"><Shield :size="15" /> Experiencia con Mascotas</span>
        <p class="p-desc">{{ user.experiencia }}</p>
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
.profile-modal {
  max-width: 500px;
  padding: 1.85rem;
}

.close-btn {
  position: absolute;
  top: 18px;
  right: 18px;
  color: var(--color-text-muted);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), #f4a261);
  color: #ffffff;
  font-size: 1.8rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(224, 122, 95, 0.35);
}

.user-fullname {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--color-text);
}

.user-badge {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  background-color: var(--color-secondary-light);
  color: var(--color-secondary);
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-top: 0.25rem;
}

.profile-details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.p-item {
  background-color: var(--color-cream);
  padding: 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.p-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 600;
  text-transform: uppercase;
}

.p-val {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-text);
}

.profile-extra {
  margin-top: 1rem;
  background-color: var(--color-cream);
  padding: 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.p-desc {
  font-size: 0.9rem;
  color: var(--color-text);
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
</style>
