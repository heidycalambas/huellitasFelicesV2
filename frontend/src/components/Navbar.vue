<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import {
  Heart,
  Home,
  FileText,
  User,
  LogOut,
  PlusCircle,
  Menu,
  X,
  Compass,
} from 'lucide-vue-next'

const emit = defineEmits(['openMisSolicitudes', 'openMiPerfil', 'openRegistrarMascota'])

const router = useRouter()
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function scrollTo(selector) {
  mobileMenuOpen.value = false
  const el = document.querySelector(selector)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<template>
  <header class="navbar-wrapper">
    <div class="navbar-container">
      <!-- Logo y Marca -->
      <a href="#inicio" class="navbar-brand" @click.prevent="scrollTo('#inicio')">
        <div class="brand-icon">
          <Heart class="icon-heart" :size="22" />
        </div>
        <div class="brand-text">
          <span class="brand-title">Huellitas Felices</span>
          <span class="brand-sub">Adopción Responsable</span>
        </div>
      </a>

      <!-- Navegación Escritorio -->
      <nav class="nav-links">
        <a href="#inicio" class="nav-link" @click.prevent="scrollTo('#inicio')">
          <Home :size="17" />
          <span>Inicio</span>
        </a>
        <a href="#mascotas" class="nav-link" @click.prevent="scrollTo('#mascotas')">
          <Heart :size="17" />
          <span>Mascotas</span>
        </a>
        <a href="#proceso" class="nav-link" @click.prevent="scrollTo('#proceso')">
          <Compass :size="17" />
          <span>Proceso de adopción</span>
        </a>
        <button class="nav-link btn-nav" @click="emit('openMisSolicitudes')">
          <FileText :size="17" />
          <span>Mis solicitudes</span>
        </button>
        <button class="nav-link btn-nav" @click="emit('openMiPerfil')">
          <User :size="17" />
          <span>Mi perfil</span>
        </button>
      </nav>

      <!-- Acciones de Usuario -->
      <div class="nav-actions">
        <!-- Botón para registrar mascota (visible para admin o para evaluar funcionalidad) -->
        <button
          class="btn btn-secondary btn-sm"
          @click="emit('openRegistrarMascota')"
          title="Registrar una nueva mascota en la plataforma"
        >
          <PlusCircle :size="17" />
          <span>Nueva Mascota</span>
        </button>

        <!-- Información breve del usuario -->
        <div class="user-pill" v-if="authStore.user">
          <div class="user-avatar">
            {{ (authStore.user.nombre || authStore.user.usuario || 'U').charAt(0).toUpperCase() }}
          </div>
          <span class="user-name">{{ authStore.user.nombre || authStore.user.usuario }}</span>
        </div>

        <!-- Cerrar Sesión -->
        <button class="btn btn-outline btn-sm btn-logout" @click="handleLogout" title="Cerrar sesión">
          <LogOut :size="16" />
          <span class="logout-text">Salir</span>
        </button>

        <!-- Botón Menú Móvil -->
        <button class="mobile-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
          <Menu v-if="!mobileMenuOpen" :size="24" />
          <X v-else :size="24" />
        </button>
      </div>
    </div>

    <!-- Menú desplegable Móvil -->
    <div v-if="mobileMenuOpen" class="mobile-menu">
      <a href="#inicio" class="mobile-link" @click="scrollTo('#inicio')">
        <Home :size="18" />
        <span>Inicio</span>
      </a>
      <a href="#mascotas" class="mobile-link" @click="scrollTo('#mascotas')">
        <Heart :size="18" />
        <span>Mascotas</span>
      </a>
      <a href="#proceso" class="mobile-link" @click="scrollTo('#proceso')">
        <Compass :size="18" />
        <span>Proceso de adopción</span>
      </a>
      <button class="mobile-link" @click="emit('openMisSolicitudes'); mobileMenuOpen = false">
        <FileText :size="18" />
        <span>Mis solicitudes</span>
      </button>
      <button class="mobile-link" @click="emit('openMiPerfil'); mobileMenuOpen = false">
        <User :size="18" />
        <span>Mi perfil</span>
      </button>
      <button class="mobile-link text-primary" @click="emit('openRegistrarMascota'); mobileMenuOpen = false">
        <PlusCircle :size="18" />
        <span>Registrar Mascota</span>
      </button>
      <button class="mobile-link text-danger" @click="handleLogout">
        <LogOut :size="18" />
        <span>Cerrar sesión</span>
      </button>
    </div>
  </header>
</template>

<style scoped>
.navbar-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 4px 20px rgba(45, 49, 66, 0.04);
}

.navbar-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0.85rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-primary), #f4a261);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 4px 10px rgba(224, 122, 95, 0.35);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: var(--font-display);
  font-size: 1.22rem;
  font-weight: 800;
  color: var(--color-text);
  line-height: 1.1;
  letter-spacing: -0.3px;
}

.brand-sub {
  font-size: 0.72rem;
  color: var(--color-primary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 0.95rem;
  border-radius: var(--radius-full);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.btn-nav {
  cursor: pointer;
  border: none;
  background: transparent;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.75rem 0.35rem 0.4rem;
  background-color: var(--color-beige);
  border-radius: var(--radius-full);
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: var(--color-secondary);
  color: #ffffff;
  font-size: 0.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text);
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-logout {
  color: #dc2626;
  border-color: #fecaca;
}

.btn-logout:hover {
  background-color: #fee2e2;
  border-color: #fca5a5;
  color: #b91c1c;
}

.mobile-toggle {
  display: none;
  color: var(--color-text);
  padding: 0.4rem;
}

.mobile-menu {
  display: none;
}

@media (max-width: 992px) {
  .nav-links, .user-pill, .logout-text {
    display: none;
  }

  .mobile-toggle {
    display: flex;
  }

  .mobile-menu {
    display: flex;
    flex-direction: column;
    padding: 1rem 1.5rem;
    background: #ffffff;
    border-top: 1px solid var(--color-border);
    gap: 0.5rem;
  }

  .mobile-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-md);
    font-weight: 600;
    color: var(--color-text);
    width: 100%;
    text-align: left;
  }

  .mobile-link:hover {
    background-color: var(--color-cream);
  }

  .text-primary {
    color: var(--color-primary);
  }

  .text-danger {
    color: #dc2626;
  }
}
</style>
