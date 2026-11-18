<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMascotasStore } from '@/stores/mascotasStore'

const router = useRouter()
const mascotasStore = useMascotasStore()

// Mascotas base seleccionadas: principalmente 2 perros y 2 gatos hermosos de alta calidad
const fallbackPets = [
  {
    id: 'f1',
    nombre: 'Luna',
    tipo: 'Perro',
    src: 'https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=900&q=80',
    alt: 'Perro Golden Retriever cariñoso en adopción',
  },
  {
    id: 'f2',
    nombre: 'Simba',
    tipo: 'Gato',
    src: 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=900&q=80',
    alt: 'Gato anaranjado de ojos expresivos en adopción',
  },
  {
    id: 'f3',
    nombre: 'Max',
    tipo: 'Perro',
    src: 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=900&q=80',
    alt: 'Perro mestizo alegre esperando un hogar',
  },
  {
    id: 'f4',
    nombre: 'Michi',
    tipo: 'Gato',
    src: 'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=900&q=80',
    alt: 'Gato blanco elegante mirando a la cámara',
  },
  {
    id: 'f5',
    nombre: 'Rocky',
    tipo: 'Perro',
    src: 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=900&q=80',
    alt: 'Perrito juguetón esperando una familia',
  },
  {
    id: 'f6',
    nombre: 'Nala',
    tipo: 'Gato',
    src: 'https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&w=900&q=80',
    alt: 'Gatita tierna y tranquila',
  },
]

// Lista reactiva de mascotas
const petsList = ref([...fallbackPets])

// Cargar mascotas de la base de datos con foto válida y alternar estrictamente Perro - Gato
onMounted(async () => {
  try {
    await mascotasStore.fetchMascotas()
    if (mascotasStore.mascotas && mascotasStore.mascotas.length > 0) {
      // Filtrar mascotas que tienen fotografía válida cargada desde URL
      const validPets = mascotasStore.mascotas
        .filter((m) => m.foto_url && (m.foto_url.startsWith('http://') || m.foto_url.startsWith('https://')))
        .map((m) => ({
          id: m.id,
          nombre: m.nombre,
          tipo: m.tipo,
          src: m.foto_url,
          alt: `${m.nombre} (${m.tipo}) disponible para adopción`,
        }))

      const dogs = validPets.filter((m) => m.tipo?.toLowerCase() === 'perro')
      const cats = validPets.filter((m) => m.tipo?.toLowerCase() === 'gato')

      // Alternar estrictamente perro, gato, perro, gato...
      const alternated = []
      const totalPairs = 3 // 3 perros y 3 gatos para un total de 6

      for (let i = 0; i < totalPairs; i++) {
        if (dogs[i]) alternated.push(dogs[i])
        if (cats[i]) alternated.push(cats[i])
      }

      if (alternated.length >= 4) {
        petsList.value = alternated
      } else {
        petsList.value = [...alternated, ...fallbackPets.slice(alternated.length)]
      }
    }
  } catch (err) {
    // Si la API no está disponible, se mantienen las mascotas base alternadas
  }

  startAutoplay()
})

// Carrusel dinámico
const currentIndex = ref(0)
let timer = null
const isHovered = ref(false)

function startAutoplay() {
  stopAutoplay()
  timer = setInterval(() => {
    if (!isHovered.value) {
      advance()
    }
  }, 3800)
}

function stopAutoplay() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function advance() {
  const total = petsList.value.length
  if (total > 0) {
    currentIndex.value = (currentIndex.value + 1) % total
  }
}

function prev() {
  const total = petsList.value.length
  if (total > 0) {
    currentIndex.value = (currentIndex.value - 1 + total) % total
  }
}

function selectPet(index) {
  currentIndex.value = index
  startAutoplay()
}

// Obtener items visibles para la curva en arco (5 slots: -2, -1, 0, 1, 2)
const visibleSlots = computed(() => {
  const list = petsList.value
  const total = list.length
  if (total === 0) return []

  const slots = [-2, -1, 0, 1, 2]
  return slots.map((offset) => {
    const rawIndex = (currentIndex.value + offset) % total
    const actualIndex = rawIndex < 0 ? rawIndex + total : rawIndex
    return {
      offset,
      pet: list[actualIndex],
      actualIndex,
    }
  })
})

onUnmounted(() => {
  stopAutoplay()
})

// Navegar directamente al registro
function handleCtaClick() {
  router.push({ name: 'Register' })
}

// Modal informativo para secciones del navbar
const modalInfo = ref(null)

function openInfo(type) {
  modalInfo.value = type
}

function closeInfo() {
  modalInfo.value = null
}
</script>

<template>
  <main class="home-wrapper">
    <!-- Barra superior en una sola línea continua -->
    <header class="top-nav-bar">
      <div class="brand-item" @click="router.push('/')">
        <span class="brand-name">Huellitas Felices</span>
      </div>
      <nav class="nav-links-right" aria-label="Enlaces de navegación">
        <button type="button" class="nav-pill-item btn-link" @click="openInfo('quienes')">Quiénes somos</button>
        <button type="button" class="nav-pill-item btn-link" @click="openInfo('historias')">Historias</button>
        <button type="button" class="nav-pill-item btn-link" @click="openInfo('apoyanos')">Apóyanos</button>
        <div class="nav-auth-actions">
          <router-link to="/login" class="nav-btn-login">Iniciar sesión</router-link>
          <router-link to="/register" class="nav-btn-register">Registrarse</router-link>
        </div>
      </nav>
    </header>

    <!-- Título principal y Pequeño texto de invitación -->
    <header class="home-header">
      <h1 class="main-title">
        Cada mascota merece un hogar lleno de amor
      </h1>

      <p class="invite-quote">
        «El amor verdadero no pregunta de dónde vienes, solo te mira a los ojos y te dice: "Por fin estás en casa".»
      </p>
    </header>

    <!-- Galería central de mascotas (carrusel en arco) con nombre debajo de cada imagen -->
    <section
      class="gallery-section"
      aria-label="Galería interactiva de mascotas en adopción"
      @mouseenter="isHovered = true"
      @mouseleave="isHovered = false"
    >
      <div class="gallery-arc-container">
        <div
          v-for="slot in visibleSlots"
          :key="`${slot.pet.id}-${slot.offset}`"
          class="slot-column"
          :class="[
            `slot-${slot.offset}`,
            { 'is-center': slot.offset === 0 }
          ]"
          @click="selectPet(slot.actualIndex)"
          :role="slot.offset === 0 ? 'figure' : 'button'"
          :aria-label="slot.offset === 0 ? `Mascota destacada: ${slot.pet.nombre}` : `Ver a ${slot.pet.nombre}`"
        >
          <div class="arc-card">
            <img
              :src="slot.pet.src"
              :alt="slot.pet.alt"
              class="pet-photo"
              loading="eager"
            />
            <!-- Velo sutil en las tarjetas laterales para resaltar la central -->
            <div v-if="slot.offset !== 0" class="card-soft-overlay"></div>
          </div>
          <!-- Nombre de la mascota debajo de la imagen -->
          <span class="pet-name-caption">
            {{ slot.pet.nombre }}
          </span>
        </div>
      </div>

      <!-- Indicadores de posición minimalistas -->
      <nav class="gallery-indicators" aria-label="Indicadores del carrusel">
        <button
          v-for="(pet, idx) in petsList"
          :key="pet.id"
          class="indicator-pill"
          :class="{ active: idx === currentIndex }"
          @click="selectPet(idx)"
          :aria-label="`Ir a mascota ${idx + 1}`"
          :aria-current="idx === currentIndex ? 'true' : 'false'"
        ></button>
      </nav>
    </section>

    <!-- Botón principal destacado "Brinda un hogar" -->
    <footer class="home-footer-action">
      <div class="cta-container">
        <button
          type="button"
          class="btn-brinda-hogar"
          @click="handleCtaClick"
          title="Presiona para registrarte y brindar un hogar a una mascota"
        >
          Brinda un hogar
        </button>
      </div>
    </footer>

    <!-- Footer Institucional con Contacto e Información -->
    <footer class="institutional-footer">
      <div class="footer-grid">
        <div class="footer-col brand-col">
          <h3 class="footer-brand-title">Huellitas Felices</h3>
          <p class="footer-text">
            Plataforma dedicada a la adopción responsable, rescate y bienestar de perros y gatos en Colombia. Creemos en segundas oportunidades y hogares llenos de amor y respeto.
          </p>
        </div>

        <div class="footer-col">
          <h4 class="footer-heading">Contacto Institucional</h4>
          <ul class="footer-list">
            <li><strong>Email:</strong> contacto@huellitasfelices.org</li>
            <li><strong>Línea de atención:</strong> +57 (300) 111-2233</li>
            <li><strong>Sedes:</strong> Popayán &bull; Cali &bull; Bogotá</li>
            <li><strong>Horario:</strong> Lunes a Sábado, 8:00 AM - 5:00 PM</li>
          </ul>
        </div>

        <div class="footer-col">
          <h4 class="footer-heading">Navegación</h4>
          <ul class="footer-list">
            <li><a href="#" @click.prevent="openInfo('quienes')">Quiénes somos</a></li>
            <li><a href="#" @click.prevent="openInfo('historias')">Historias de éxito</a></li>
            <li><a href="#" @click.prevent="openInfo('apoyanos')">Cómo apoyar un refugio</a></li>
            <li><router-link to="/login">Iniciar sesión</router-link></li>
            <li><router-link to="/register">Crear cuenta de adoptante</router-link></li>
          </ul>
        </div>
      </div>

      <div class="footer-bottom">
        <p>© 2026 Huellitas Felices &bull; Todos los derechos reservados &bull; Adopción Responsable</p>
      </div>
    </footer>

    <!-- Modal Informativo para Navbar -->
    <div v-if="modalInfo" class="info-modal-backdrop" @click.self="closeInfo">
      <div class="info-modal-card">
        <button class="info-modal-close" @click="closeInfo">&times;</button>
        <div v-if="modalInfo === 'quienes'">
          <h3 class="modal-info-title">Quiénes Somos</h3>
          <p class="modal-info-p">
            Huellitas Felices es una iniciativa sin fines de lucro que articula refugios certificados, veterinarios y adoptantes comprometidos. Nuestro objetivo principal es garantizar que cada perro o gato rescatado encuentre un entorno amoroso y seguro, con seguimiento veterinario continuo y asesoría responsable.
          </p>
          <div class="info-badges-row">
            <span>🐾 Refugios Verificados</span>
            <span>💉 Esquema Veterinario Completo</span>
            <span>🏡 Hogares Protegidos</span>
          </div>
        </div>
        <div v-else-if="modalInfo === 'historias'">
          <h3 class="modal-info-title">Historias que Inspiran</h3>
          <p class="modal-info-p">
            Más de 350 colitas felices han encontrado una nueva familia a través de nuestra red. Desde cachorros rescatados en situaciones de vulnerabilidad hasta mascotas adultas que hoy duermen tranquilas al lado de sus seres queridos.
          </p>
          <blockquote class="modal-info-quote">
            «Adoptar a Luna fue la mejor decisión de nuestras vidas. Llena cada rincón de nuestra casa de alegría.» — Familia Pérez
          </blockquote>
        </div>
        <div v-else-if="modalInfo === 'apoyanos'">
          <h3 class="modal-info-title">Cómo Apoyarnos</h3>
          <p class="modal-info-p">
            Puedes sumarte a nuestra causa adoptando, compartiendo los perfiles de mascotas, donando concentrado o insumos médicos a los refugios de tu ciudad, o brindando hogar de paso.
          </p>
          <p class="modal-info-p">
            Contáctanos a <strong>contacto@huellitasfelices.org</strong> para coordinar voluntariado o aportes a refugios de Popayán, Cali y Bogotá.
          </p>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
/* ─────────────────────────────────────────────────────────────
   1. DISEÑO GENERAL DEL HOME
   - Fondo crema / beige muy claro (#FAF7F2)
   - Minimalista, limpio, moderno, ocupa visualmente la pantalla
───────────────────────────────────────────────────────────── */
.home-wrapper {
  min-height: 100vh;
  width: 100%;
  background-color: #FAF7F2;
  color: #2D3142;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 1.6rem 2rem 3rem;
  box-sizing: border-box;
  overflow-x: hidden;
  position: relative;
  user-select: none;
}

/* ─────────────────────────────────────────────────────────────
   BARRA SUPERIOR (HEADER EN UNA SOLA LÍNEA)
───────────────────────────────────────────────────────────── */
.top-nav-bar {
  width: 100%;
  max-width: 1240px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0 1.2rem;
  white-space: nowrap;
}

.brand-name {
  font-family: 'Outfit', 'Plus Jakarta Sans', system-ui, sans-serif;
  font-size: 1.22rem;
  font-weight: 800;
  color: #1F2430;
  letter-spacing: -0.4px;
}

.nav-links-right {
  display: flex;
  align-items: center;
  gap: 2rem;
  white-space: nowrap;
}

.nav-pill-item {
  font-size: 0.94rem;
  font-weight: 600;
  color: #61677A;
  cursor: default;
  transition: color 0.2s ease;
}

.nav-pill-item:hover {
  color: #E07A5F;
}

/* ─────────────────────────────────────────────────────────────
   2. TÍTULO PRINCIPAL Y TEXTO DE INVITACIÓN
───────────────────────────────────────────────────────────── */
.home-header {
  position: relative;
  width: 100%;
  max-width: 820px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.1rem;
  margin-bottom: 1.2rem;
  padding: 0 1rem;
}

/* Doodles decorativos fieles a la referencia */
.doodle-top-left {
  position: absolute;
  top: 18px;
  left: 20px;
  opacity: 0.65;
}

.doodle-top-right {
  position: absolute;
  top: 10px;
  right: -20px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  opacity: 0.75;
}

.doodle-text {
  font-family: 'Caveat', 'Comic Sans MS', cursive, sans-serif;
  font-size: 1.05rem;
  color: #2D3142;
  transform: rotate(5deg);
  font-weight: 600;
}

.doodle-arrow {
  margin-top: -2px;
  margin-right: 6px;
}

.main-title {
  font-family: 'Outfit', 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  font-size: clamp(2.2rem, 5.2vw, 4rem);
  font-weight: 800;
  color: #1F2430;
  line-height: 1.15;
  letter-spacing: -1.6px;
  margin: 0;
  max-width: 760px;
}

.invite-quote {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  font-size: clamp(0.95rem, 1.8vw, 1.15rem);
  color: #61677A;
  line-height: 1.6;
  max-width: 620px;
  margin: 0;
  font-weight: 500;
  font-style: normal;
}

/* ─────────────────────────────────────────────────────────────
   3. GALERÍA CENTRAL DE MASCOTAS (CARRUSEL EN ARCO)
   - Con el nombre de cada mascota debajo de su imagen
───────────────────────────────────────────────────────────── */
.gallery-section {
  width: 100%;
  max-width: 1300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 1.5rem 0;
  position: relative;
}

.gallery-arc-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.4rem;
  width: 100%;
  padding: 1.5rem 0;
  perspective: 1200px;
}

.slot-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  transition: all 0.65s cubic-bezier(0.25, 1, 0.5, 1);
  cursor: pointer;
}

.arc-card {
  position: relative;
  border-radius: 26px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(45, 49, 66, 0.08);
  background-color: #EDE8DE;
  transition: all 0.65s cubic-bezier(0.25, 1, 0.5, 1);
}

.pet-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.65s cubic-bezier(0.25, 1, 0.5, 1);
}

.card-soft-overlay {
  position: absolute;
  inset: 0;
  background: rgba(250, 247, 242, 0.15);
  pointer-events: none;
  transition: opacity 0.3s ease;
}

/* Nombre debajo de la mascota */
.pet-name-caption {
  font-family: 'Outfit', 'Plus Jakarta Sans', system-ui, sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: #61677A;
  margin-top: 0.8rem;
  letter-spacing: -0.2px;
  transition: all 0.35s ease;
}

/* ── CONFIGURACIÓN EN ARCO DE CADA SLOT ── */

/* Centro (Slot 0): Más grande, vertical, protagónico */
.slot-0 {
  transform: translateY(-8px) scale(1.08);
  z-index: 10;
  cursor: default;
}

.slot-0 .arc-card {
  width: 250px;
  height: 380px;
  border-radius: 28px;
  box-shadow: 0 24px 55px -10px rgba(45, 49, 66, 0.22);
  border: 4px solid #FFFFFF;
}

.slot-0 .pet-name-caption {
  font-size: 1.25rem;
  font-weight: 800;
  color: #1F2430;
  margin-top: 0.9rem;
}

.slot-0:hover .pet-photo {
  transform: scale(1.03);
}

/* Laterales internos (Slots -1 y +1) */
.slot--1 {
  transform: translateY(14px) rotate(-3.5deg) scale(0.92);
  opacity: 0.88;
  z-index: 5;
}

.slot-1 {
  transform: translateY(14px) rotate(3.5deg) scale(0.92);
  opacity: 0.88;
  z-index: 5;
}

.slot--1 .arc-card,
.slot-1 .arc-card {
  width: 195px;
  height: 310px;
  border: 2px solid rgba(255, 255, 255, 0.8);
}

/* Laterales externos (Slots -2 y +2) */
.slot--2 {
  transform: translateY(38px) rotate(-7deg) scale(0.8);
  opacity: 0.68;
  z-index: 2;
}

.slot-2 {
  transform: translateY(38px) rotate(7deg) scale(0.8);
  opacity: 0.68;
  z-index: 2;
}

.slot--2 .arc-card,
.slot-2 .arc-card {
  width: 165px;
  height: 260px;
  border: 2px solid rgba(255, 255, 255, 0.6);
}

/* Efecto hover suave en columnas laterales */
.slot-column:not(.is-center):hover {
  opacity: 1;
  transform: translateY(8px) scale(0.97);
}

.slot-column:not(.is-center):hover .arc-card {
  box-shadow: 0 16px 36px rgba(45, 49, 66, 0.16);
}

.slot-column:not(.is-center):hover .pet-name-caption {
  color: #E07A5F;
}

/* Indicadores tipo pills */
.gallery-indicators {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.4rem;
}

.indicator-pill {
  height: 8px;
  width: 8px;
  border-radius: 9999px;
  background-color: #D6CEBF;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: all 0.35s ease;
}

.indicator-pill.active {
  width: 26px;
  background-color: #E07A5F;
}

/* ─────────────────────────────────────────────────────────────
   4. BOTÓN PRINCIPAL "BRINDA UN HOGAR"
───────────────────────────────────────────────────────────── */
.home-footer-action {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
}

.cta-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Doodle estilo mano alzada junto al botón */
.doodle-cta {
  position: absolute;
  left: -155px;
  bottom: 6px;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  opacity: 0.78;
}

.doodle-cta-label {
  font-family: 'Caveat', 'Comic Sans MS', cursive, sans-serif;
  font-size: 1.05rem;
  color: #2D3142;
  font-weight: 600;
  white-space: nowrap;
}

.doodle-cta-arrow {
  transform: translateY(-2px);
}

/* Botón estilo píldora cálido idéntico a la referencia */
.btn-brinda-hogar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1.1rem 2.8rem;
  border-radius: 9999px;
  background-color: #FF7262;
  color: #FFFFFF;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.2px;
  border: none;
  outline: none;
  cursor: pointer;
  box-shadow: 0 10px 28px rgba(255, 114, 98, 0.42);
  transition: all 0.24s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-brinda-hogar:hover {
  background-color: #F85F4D;
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 16px 36px rgba(255, 114, 98, 0.52);
}

.btn-brinda-hogar:active {
  transform: translateY(0) scale(0.99);
}

/* ─────────────────────────────────────────────────────────────
   ADAPTABILIDAD RESPONSIVE (Móviles, Tablets, Laptops)
───────────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .slot--2, .slot-2 {
    display: none;
  }
  .slot-0 .arc-card {
    width: 220px;
    height: 330px;
  }
  .slot--1 .arc-card, .slot-1 .arc-card {
    width: 165px;
    height: 260px;
  }
  .doodle-top-right {
    display: none;
  }
}

@media (max-width: 768px) {
  .home-wrapper {
    padding: 1.5rem 1rem 2.5rem;
    gap: 1rem;
  }

  .nav-links-right {
    gap: 1.1rem;
  }

  .nav-pill-item {
    font-size: 0.85rem;
  }

  .main-title {
    font-size: 2.2rem;
    letter-spacing: -1px;
  }

  .invite-quote {
    font-size: 0.95rem;
  }

  .doodle-top-left, .doodle-cta {
    display: none;
  }

  .gallery-arc-container {
    gap: 0.8rem;
    padding: 1rem 0;
  }

  .slot-0 .arc-card {
    width: 190px;
    height: 280px;
    border-radius: 22px;
  }

  .slot--1 .arc-card, .slot-1 .arc-card {
    width: 125px;
    height: 200px;
    border-radius: 18px;
  }

  .slot--1, .slot-1 {
    transform: translateY(12px) scale(0.9);
  }

  .btn-brinda-hogar {
    padding: 0.95rem 2.2rem;
    font-size: 1.02rem;
  }
}

@media (max-width: 480px) {
  .slot--1, .slot-1 {
    display: none;
  }

  .slot-0 {
    transform: none;
  }

  .slot-0 .arc-card {
    width: 230px;
    height: 330px;
    box-shadow: 0 18px 40px rgba(45, 49, 66, 0.2);
  }

  .main-title {
    font-size: 1.85rem;
  }
}

/* ─────────────────────────────────────────────────────────────
   ENLACES NAVBAR & ACCIONES AUTH
───────────────────────────────────────────────────────────── */
.btn-link {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font-family: inherit;
}

.nav-auth-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-left: 1rem;
}

.nav-btn-login {
  color: #2D3142;
  text-decoration: none;
  font-size: 0.92rem;
  font-weight: 600;
  padding: 0.45rem 1rem;
  border-radius: 999px;
  border: 1px solid #D8CFC4;
  transition: all 0.2s ease;
}

.nav-btn-login:hover {
  background-color: #F3EDE2;
  border-color: #E07A5F;
  color: #E07A5F;
}

.nav-btn-register {
  background-color: #E07A5F;
  color: #ffffff;
  text-decoration: none;
  font-size: 0.92rem;
  font-weight: 700;
  padding: 0.45rem 1.1rem;
  border-radius: 999px;
  box-shadow: 0 4px 12px rgba(224, 122, 95, 0.25);
  transition: all 0.2s ease;
}

.nav-btn-register:hover {
  background-color: #c9674e;
  transform: translateY(-1px);
}

/* ─────────────────────────────────────────────────────────────
   FOOTER INSTITUCIONAL
───────────────────────────────────────────────────────────── */
.institutional-footer {
  width: 100%;
  max-width: 1240px;
  margin-top: 3.5rem;
  padding-top: 2.5rem;
  border-top: 1px solid #E6DEC8;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1.2fr;
  gap: 2.5rem;
}

.footer-brand-title {
  font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
  font-size: 1.35rem;
  font-weight: 800;
  color: #1F2430;
  margin: 0 0 0.8rem 0;
}

.footer-text {
  font-size: 0.92rem;
  line-height: 1.6;
  color: #61677A;
  margin: 0;
  max-width: 380px;
}

.footer-heading {
  font-size: 1.02rem;
  font-weight: 700;
  color: #1F2430;
  margin: 0 0 0.9rem 0;
}

.footer-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.footer-list li, .footer-list a {
  font-size: 0.88rem;
  color: #61677A;
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-list a:hover {
  color: #E07A5F;
}

.footer-bottom {
  text-align: center;
  font-size: 0.84rem;
  color: #8C92A4;
  padding: 1.2rem 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

/* ─────────────────────────────────────────────────────────────
   MODAL INFORMATIVO
───────────────────────────────────────────────────────────── */
.info-modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(45, 49, 66, 0.45);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.info-modal-card {
  background-color: #FAF7F2;
  border-radius: 20px;
  max-width: 520px;
  width: 100%;
  padding: 2.2rem;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.18);
  position: relative;
  box-sizing: border-box;
}

.info-modal-close {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #61677A;
  cursor: pointer;
  line-height: 1;
}

.modal-info-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: #1F2430;
  margin: 0 0 1rem 0;
}

.modal-info-p {
  font-size: 0.95rem;
  line-height: 1.65;
  color: #4A4E69;
  margin-bottom: 1rem;
}

.info-badges-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 1rem;
}

.info-badges-row span {
  background-color: #EFE8DC;
  color: #2D3142;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
}

.modal-info-quote {
  border-left: 4px solid #E07A5F;
  margin: 1.2rem 0;
  padding: 0.5rem 1rem;
  background: #F3EDE2;
  border-radius: 0 10px 10px 0;
  font-style: italic;
  color: #2D3142;
  font-size: 0.92rem;
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 1.8rem;
  }
  .nav-links-right {
    gap: 0.8rem;
  }
}
</style>
