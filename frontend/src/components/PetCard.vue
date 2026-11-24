<script setup>
import { computed } from 'vue'
import { MapPin, Calendar, Heart, ShieldCheck, Sparkles } from 'lucide-vue-next'
import { useFavoritosStore } from '@/stores/favoritosStore'

const props = defineProps({
  mascota: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['verDetalle', 'iniciarAdopcion', 'toggleFavorito'])
const favoritosStore = useFavoritosStore()

const isFav = computed(() => {
  return favoritosStore.isFavorito(props.mascota.id)
})

async function handleFavClick(e) {
  e.stopPropagation()
  await favoritosStore.toggleFavorito(props.mascota)
  emit('toggleFavorito', props.mascota)
}

// Fotos predeterminadas de alta calidad según tipo y nombre
const petPhoto = computed(() => {
  if (props.mascota.foto_url) return props.mascota.foto_url

  const nombreLower = (props.mascota.nombre || '').toLowerCase()
  const tipoLower = (props.mascota.tipo || '').toLowerCase()

  if (nombreLower.includes('luna')) {
    return 'https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=700&q=80'
  }
  if (nombreLower.includes('max')) {
    return 'https://images.unsplash.com/photo-1589941013453-ec89f33b5e95?auto=format&fit=crop&w=700&q=80'
  }
  if (nombreLower.includes('michi')) {
    return 'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=700&q=80'
  }
  if (nombreLower.includes('simba')) {
    return 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=700&q=80'
  }
  if (nombreLower.includes('rocky')) {
    return 'https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?auto=format&fit=crop&w=700&q=80'
  }
  if (nombreLower.includes('nala')) {
    return 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=700&q=80'
  }

  // Fallbacks generales
  if (tipoLower === 'gato') {
    return 'https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&w=700&q=80'
  }
  return 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=700&q=80'
})

// Clases de estado
const statusBadgeClass = computed(() => {
  const est = (props.mascota.estado || '').toLowerCase()
  if (est === 'disponible') return 'badge-disponible'
  if (est === 'en revisión' || est === 'entrevista') return 'badge-revision'
  return 'badge-adoptada'
})

const isDisponible = computed(() => {
  return (props.mascota.estado || '').toLowerCase() === 'disponible'
})
</script>

<template>
  <div class="pet-card">
    <!-- Contenedor de Imagen y Badge de Estado -->
    <div class="card-image-wrap">
      <img
        :src="petPhoto"
        :alt="mascota.nombre"
        class="card-image"
        loading="lazy"
      />
      <span class="status-badge" :class="statusBadgeClass">
        {{ mascota.estado || 'Disponible' }}
      </span>
      <span class="type-badge">
        {{ mascota.tipo }}
      </span>

      <!-- Icono de Favoritos en la tarjeta -->
      <button
        type="button"
        class="fav-badge-btn"
        :class="{ active: isFav }"
        @click="handleFavClick"
        :title="isFav ? 'Quitar de favoritos' : 'Agregar a favoritos'"
        aria-label="Favorito"
      >
        <Heart :size="19" :fill="isFav ? '#E07A5F' : 'none'" />
      </button>
    </div>

    <!-- Cuerpo de la Tarjeta -->
    <div class="card-body">
      <div class="card-header-info">
        <h3 class="pet-name">{{ mascota.nombre }}</h3>
        <span class="pet-breed">{{ mascota.raza || 'Criollo' }}</span>
      </div>

      <!-- Metadatos rápidos -->
      <div class="pet-meta-row">
        <span class="meta-item">
          <Calendar :size="15" class="meta-icon" />
          <span>{{ mascota.edad }} {{ mascota.edad === 1 ? 'año' : 'años' }}</span>
        </span>
        <span class="meta-item">
          <Sparkles :size="15" class="meta-icon" />
          <span>{{ mascota.sexo || 'N/A' }}</span>
        </span>
        <span class="meta-item" v-if="mascota.ciudad">
          <MapPin :size="15" class="meta-icon" />
          <span>{{ mascota.ciudad }}</span>
        </span>
      </div>

      <!-- Descripción corta -->
      <p class="pet-description">
        {{ mascota.descripcion || 'Una mascota cariñosa en busca de un hogar donde recibir y dar amor.' }}
      </p>

      <!-- Chips de Compatibilidad y Salud -->
      <div class="pet-tags">
        <span class="tag-pill" v-if="mascota.compatible_ninos">
          <ShieldCheck :size="13" /> Niños
        </span>
        <span class="tag-pill" v-if="mascota.compatible_mascotas">
          <ShieldCheck :size="13" /> Mascotas
        </span>
        <span class="tag-pill" v-if="mascota.vacunado">
          <ShieldCheck :size="13" /> Vacunado
        </span>
        <span class="tag-pill" v-if="mascota.esterilizado">
          <ShieldCheck :size="13" /> Esterilizado
        </span>
      </div>

      <!-- Botones de Acción -->
      <div class="card-actions">
        <button
          class="btn btn-outline btn-card"
          @click="emit('verDetalle', mascota)"
          title="Ver perfil completo"
        >
          Conocer más
        </button>

        <button
          v-if="isDisponible"
          class="btn btn-primary btn-card"
          @click="emit('iniciarAdopcion', mascota)"
          title="Iniciar solicitud de adopción"
        >
          <Heart :size="16" />
          <span>Adoptar</span>
        </button>
        <button
          v-else
          class="btn btn-card btn-disabled"
          disabled
        >
          No disponible
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pet-card {
  background-color: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  transition: all var(--transition-normal);
  position: relative;
}

.pet-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(224, 122, 95, 0.4);
}

.card-image-wrap {
  position: relative;
  width: 100%;
  height: 220px;
  background-color: var(--color-beige);
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.pet-card:hover .card-image {
  transform: scale(1.04);
}

.status-badge {
  position: absolute;
  top: 14px;
  left: 14px;
  padding: 0.35rem 0.85rem;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.badge-disponible {
  background-color: rgba(232, 245, 233, 0.95);
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}

.badge-revision {
  background-color: rgba(254, 243, 199, 0.95);
  color: #d97706;
  border: 1px solid #fde68a;
}

.badge-adoptada {
  background-color: rgba(243, 244, 246, 0.95);
  color: #4b5563;
  border: 1px solid #d1d5db;
}

.type-badge {
  position: absolute;
  bottom: 12px;
  left: 14px;
  background-color: rgba(45, 49, 66, 0.82);
  color: #ffffff;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.76rem;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.fav-badge-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8C92A4;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
  transition: all 0.2s ease;
  z-index: 5;
}

.fav-badge-btn:hover {
  transform: scale(1.12);
  color: #E07A5F;
}

.fav-badge-btn.active {
  color: #E07A5F;
  background: #ffffff;
}

.card-body {
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-header-info {
  margin-bottom: 0.75rem;
}

.pet-name {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.pet-breed {
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.pet-meta-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.9rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.meta-icon {
  color: var(--color-primary);
}

.pet-description {
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--color-text);
  opacity: 0.85;
  margin-bottom: 1.1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pet-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 1.3rem;
  min-height: 26px;
}

.tag-pill {
  background-color: var(--color-beige);
  color: var(--color-text);
  padding: 0.22rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.card-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: auto;
}

.btn-card {
  flex: 1;
  padding: 0.65rem 0.8rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

.btn-disabled {
  background-color: var(--color-beige);
  color: var(--color-text-muted);
  cursor: not-allowed;
  border: 1px solid var(--color-border);
}
</style>
