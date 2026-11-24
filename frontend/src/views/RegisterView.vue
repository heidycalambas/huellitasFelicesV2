<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import {
  Heart,
  User,
  Lock,
  MapPin,
  Eye,
  EyeOff,
  AlertCircle,
  ArrowLeft,
  CheckCircle,
  Home,
  Clock,
  Sliders,
  PawPrint,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  // Información personal
  nombre: '',
  usuario: '',
  edad: 25,
  ciudad: 'Popayán',
  // Información del hogar
  tipo_vivienda: 'Casa',
  tiene_patio: true,
  otras_mascotas: false,
  // Experiencia y disponibilidad
  tiempo_disponible: 'Alta',
  experiencia: 'Cuento con el espacio, tiempo y cariño para cuidar a un animalito responsablemente.',
  // Preferencias de adopción
  preferencia_tipo: 'Todos',
  preferencia_tamano: 'Mediano',
  preferencia_edad: 'Joven',
  // Seguridad
  password: '',
  confirmPassword: '',
})

const showPassword = ref(false)
const showConfirm = ref(false)
const localError = ref(null)
const success = ref(false)
const loading = ref(false)

function goHome() {
  router.push({ name: 'Landing' })
}

function validate() {
  if (!form.nombre.trim()) return 'Por favor ingresa tu nombre completo.'
  if (!form.usuario.trim()) return 'Por favor elige un nombre de usuario.'
  if (!form.edad || form.edad < 18 || form.edad > 100) return 'Debes ser mayor de edad (18+ años) para adoptar.'
  if (!form.ciudad.trim()) return 'Por favor ingresa tu ciudad.'
  if (!form.experiencia.trim()) return 'Por favor cuéntanos brevemente sobre tu experiencia con animales.'
  if (form.password.length < 6)
    return 'La contraseña debe tener un mínimo de 6 caracteres.'
  if (form.password !== form.confirmPassword)
    return 'Las contraseñas no coinciden. Por favor verifícalas.'
  return null
}

async function handleRegister() {
  localError.value = null
  const err = validate()
  if (err) {
    localError.value = err
    // Desplazar al inicio del formulario para ver el error
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  loading.value = true
  try {
    const payload = {
      nombre: form.nombre.trim(),
      usuario: form.usuario.trim(),
      edad: Number(form.edad),
      ciudad: form.ciudad.trim(),
      tipo_vivienda: form.tipo_vivienda,
      tiene_patio: Boolean(form.tiene_patio),
      otras_mascotas: Boolean(form.otras_mascotas),
      tiempo_disponible: form.tiempo_disponible,
      experiencia: form.experiencia.trim(),
      preferencia_tipo: form.preferencia_tipo,
      preferencia_tamano: form.preferencia_tamano,
      preferencia_edad: form.preferencia_edad,
      password: form.password,
    }

    const result = await authStore.register(payload)

    if (result && result.success) {
      success.value = true
      window.scrollTo({ top: 0, behavior: 'smooth' })
      try {
        const loginRes = await authStore.login(form.usuario.trim(), form.password)
        if (loginRes.success) {
          setTimeout(() => router.push({ name: 'Home' }), 1800)
          return
        }
      } catch (loginErr) {
        // Fallback al login
      }
      setTimeout(() => router.push({ name: 'Login' }), 2000)
    } else {
      localError.value =
        result?.error ||
        authStore.error ||
        'No se pudo completar el registro. Intenta nuevamente.'
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  } catch (e) {
    localError.value =
      e?.response?.data?.error ||
      'Ocurrió un inconveniente al conectar con el servidor. Intenta de nuevo.'
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card-wrapper">
      <!-- Botón para volver al inicio -->
      <button class="back-link" @click="goHome" title="Volver a la página principal">
        <ArrowLeft :size="16" />
        <span>Volver al inicio</span>
      </button>

      <header class="form-header">
        <div class="header-icon-circle">
          <PawPrint :size="26" class="header-paw" />
        </div>
        <h1 class="register-title">Registro de Adoptante</h1>
        <p class="register-subtitle">
          Completa tus datos en 5 sencillas secciones para encontrar a tu compañero ideal e iniciar solicitudes de adopción responsable.
        </p>
      </header>

      <!-- Mensaje de éxito -->
      <div v-if="success" class="state-banner success-state">
        <CheckCircle :size="32" class="success-icon" />
        <div>
          <h3 class="state-title">¡Registro completado con éxito!</h3>
          <p class="state-msg">
            Bienvenido a Huellitas Felices. Te estamos redirigiendo a tu panel de adoptante...
          </p>
        </div>
      </div>

      <template v-else>
        <!-- Banner de error -->
        <div v-if="localError || authStore.error" class="state-banner error-state">
          <AlertCircle :size="20" class="error-icon" />
          <span>{{ localError || authStore.error }}</span>
        </div>

        <!-- Formulario organizado en 5 secciones -->
        <form @submit.prevent="handleRegister" class="register-form" novalidate>
          
          <!-- ── SECCIÓN 1: INFORMACIÓN PERSONAL ── -->
          <fieldset class="form-section-block">
            <legend class="section-legend">
              <span class="section-badge badge-personal">
                <User :size="15" />
                <span>1. Información Personal</span>
              </span>
            </legend>

            <div class="form-grid">
              <div class="input-field-group col-span-2">
                <label class="field-label" for="reg-nombre">Nombre completo *</label>
                <div class="input-inner-wrap">
                  <User :size="18" class="input-icon" />
                  <input
                    id="reg-nombre"
                    type="text"
                    v-model="form.nombre"
                    placeholder="Ej: Laura Sofía Gómez"
                    class="custom-input"
                    autocomplete="name"
                    required
                  />
                </div>
              </div>

              <div class="input-field-group">
                <label class="field-label" for="reg-usuario">Nombre de usuario *</label>
                <div class="input-inner-wrap">
                  <span class="input-icon input-at">@</span>
                  <input
                    id="reg-usuario"
                    type="text"
                    v-model="form.usuario"
                    placeholder="Ej: laura_gomez"
                    class="custom-input"
                    autocomplete="username"
                    required
                  />
                </div>
              </div>

              <div class="input-field-group">
                <label class="field-label" for="reg-edad">Edad (Años) *</label>
                <div class="input-inner-wrap">
                  <input
                    id="reg-edad"
                    type="number"
                    min="18"
                    max="100"
                    v-model="form.edad"
                    class="custom-input input-no-icon"
                    required
                  />
                </div>
              </div>

              <div class="input-field-group col-span-2">
                <label class="field-label" for="reg-ciudad">Ciudad de residencia *</label>
                <div class="input-inner-wrap">
                  <MapPin :size="18" class="input-icon" />
                  <select id="reg-ciudad" v-model="form.ciudad" class="custom-input custom-select">
                    <option value="Popayán">Popayán</option>
                    <option value="Cali">Cali</option>
                    <option value="Bogotá">Bogotá</option>
                    <option value="Medellín">Medellín</option>
                    <option value="Pasto">Pasto</option>
                    <option value="Santander de Quilichao">Santander de Quilichao</option>
                    <option value="Otra">Otra ciudad</option>
                  </select>
                </div>
              </div>
            </div>
          </fieldset>

          <!-- ── SECCIÓN 2: INFORMACIÓN DEL HOGAR ── -->
          <fieldset class="form-section-block">
            <legend class="section-legend">
              <span class="section-badge badge-hogar">
                <Home :size="15" />
                <span>2. Información del Hogar</span>
              </span>
            </legend>

            <div class="form-grid">
              <div class="input-field-group col-span-2">
                <label class="field-label" for="reg-vivienda">Tipo de vivienda *</label>
                <div class="input-inner-wrap">
                  <select id="reg-vivienda" v-model="form.tipo_vivienda" class="custom-input custom-select">
                    <option value="Casa">Casa</option>
                    <option value="Apartamento">Apartamento</option>
                    <option value="Finca / Parcela">Finca / Parcela</option>
                    <option value="Habitación / Otro">Otro</option>
                  </select>
                </div>
              </div>

              <div class="input-field-group radio-check-card">
                <span class="field-label">¿Tiene patio o jardín?</span>
                <div class="toggle-pills">
                  <label class="toggle-pill-btn" :class="{ active: form.tiene_patio === true }">
                    <input type="radio" :value="true" v-model="form.tiene_patio" /> Sí, cuenta con patio
                  </label>
                  <label class="toggle-pill-btn" :class="{ active: form.tiene_patio === false }">
                    <input type="radio" :value="false" v-model="form.tiene_patio" /> No tiene patio
                  </label>
                </div>
              </div>

              <div class="input-field-group radio-check-card">
                <span class="field-label">¿Convive con otras mascotas?</span>
                <div class="toggle-pills">
                  <label class="toggle-pill-btn" :class="{ active: form.otras_mascotas === true }">
                    <input type="radio" :value="true" v-model="form.otras_mascotas" /> Sí, tengo mascotas
                  </label>
                  <label class="toggle-pill-btn" :class="{ active: form.otras_mascotas === false }">
                    <input type="radio" :value="false" v-model="form.otras_mascotas" /> No, actualmente ninguna
                  </label>
                </div>
              </div>
            </div>
          </fieldset>

          <!-- ── SECCIÓN 3: EXPERIENCIA Y DISPONIBILIDAD ── -->
          <fieldset class="form-section-block">
            <legend class="section-legend">
              <span class="section-badge badge-exp">
                <Clock :size="15" />
                <span>3. Experiencia y Disponibilidad</span>
              </span>
            </legend>

            <div class="form-grid">
              <div class="input-field-group col-span-2">
                <label class="field-label" for="reg-tiempo">Tiempo diario disponible para la mascota *</label>
                <div class="input-inner-wrap">
                  <select id="reg-tiempo" v-model="form.tiempo_disponible" class="custom-input custom-select">
                    <option value="Alta">Alto (Más de 5 horas o trabajo desde casa)</option>
                    <option value="Media">Medio (2 a 4 horas al día)</option>
                    <option value="Baja">Bajo (1 a 2 horas al día)</option>
                  </select>
                </div>
              </div>

              <div class="input-field-group col-span-2">
                <label class="field-label" for="reg-exp">Experiencia previa y cuidados *</label>
                <div class="input-inner-wrap">
                  <textarea
                    id="reg-exp"
                    rows="3"
                    v-model="form.experiencia"
                    placeholder="Cuéntanos brevemente sobre tu experiencia con perros o gatos, paseos, visitas veterinarias..."
                    class="custom-input custom-textarea"
                  ></textarea>
                </div>
              </div>
            </div>
          </fieldset>

          <!-- ── SECCIÓN 4: PREFERENCIAS DE ADOPCIÓN ── -->
          <fieldset class="form-section-block">
            <legend class="section-legend">
              <span class="section-badge badge-pref">
                <Sliders :size="15" />
                <span>4. Preferencias de Adopción</span>
              </span>
            </legend>

            <div class="form-grid three-grid">
              <div class="input-field-group">
                <label class="field-label" for="reg-pref-tipo">Especie preferida</label>
                <select id="reg-pref-tipo" v-model="form.preferencia_tipo" class="custom-input custom-select">
                  <option value="Todos">Cualquiera / Ambos</option>
                  <option value="Perro">Solo Perros</option>
                  <option value="Gato">Solo Gatos</option>
                </select>
              </div>

              <div class="input-field-group">
                <label class="field-label" for="reg-pref-tam">Tamaño preferido</label>
                <select id="reg-pref-tam" v-model="form.preferencia_tamano" class="custom-input custom-select">
                  <option value="Cualquiera">Cualquiera</option>
                  <option value="Pequeno">Pequeño</option>
                  <option value="Mediano">Mediano</option>
                  <option value="Grande">Grande</option>
                </select>
              </div>

              <div class="input-field-group">
                <label class="field-label" for="reg-pref-edad">Etapa de vida</label>
                <select id="reg-pref-edad" v-model="form.preferencia_edad" class="custom-input custom-select">
                  <option value="Cualquiera">Cualquiera</option>
                  <option value="Cachorro">Cachorro</option>
                  <option value="Joven">Joven</option>
                  <option value="Adulto">Adulto</option>
                  <option value="Senior">Senior (Adulto mayor)</option>
                </select>
              </div>
            </div>
          </fieldset>

          <!-- ── SECCIÓN 5: SEGURIDAD ── -->
          <fieldset class="form-section-block">
            <legend class="section-legend">
              <span class="section-badge badge-seguridad">
                <Lock :size="15" />
                <span>5. Seguridad de tu Cuenta</span>
              </span>
            </legend>

            <div class="form-grid">
              <div class="input-field-group">
                <label class="field-label" for="reg-password">Contraseña *</label>
                <div class="input-inner-wrap">
                  <Lock :size="18" class="input-icon" />
                  <input
                    id="reg-password"
                    :type="showPassword ? 'text' : 'password'"
                    v-model="form.password"
                    placeholder="Mínimo 6 caracteres"
                    class="custom-input"
                    autocomplete="new-password"
                    required
                  />
                  <button
                    type="button"
                    class="toggle-eye-btn"
                    @click="showPassword = !showPassword"
                    tabindex="-1"
                    title="Mostrar / ocultar"
                  >
                    <EyeOff v-if="showPassword" :size="18" />
                    <Eye v-else :size="18" />
                  </button>
                </div>
              </div>

              <div class="input-field-group">
                <label class="field-label" for="reg-confirm">Confirmar Contraseña *</label>
                <div class="input-inner-wrap">
                  <Lock :size="18" class="input-icon" />
                  <input
                    id="reg-confirm"
                    :type="showConfirm ? 'text' : 'password'"
                    v-model="form.confirmPassword"
                    placeholder="Repite tu contraseña"
                    class="custom-input"
                    autocomplete="new-password"
                    required
                  />
                  <button
                    type="button"
                    class="toggle-eye-btn"
                    @click="showConfirm = !showConfirm"
                    tabindex="-1"
                    title="Mostrar / ocultar"
                  >
                    <EyeOff v-if="showConfirm" :size="18" />
                    <Eye v-else :size="18" />
                  </button>
                </div>
              </div>
            </div>
          </fieldset>

          <!-- 🐾 BOTÓN SUBMIT TIPO HUELLITA 🐾 -->
          <div class="submit-action-wrap">
            <button
              type="submit"
              class="btn-huellita submit-register-btn"
              :disabled="loading"
            >
              <span class="huellita-pad">
                <PawPrint :size="20" class="paw-icon" :class="{ 'paw-spin': loading }" />
              </span>
              <span class="huellita-text" v-if="!loading">Crear mi cuenta de adoptante</span>
              <span class="huellita-text" v-else>Creando tu cuenta...</span>
            </button>
          </div>

          <!-- Link al login -->
          <footer class="form-bottom-link">
            <span>¿Ya tienes una cuenta registrada?</span>
            <router-link to="/login" class="login-link">
              Inicia sesión aquí
            </router-link>
          </footer>
        </form>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* Página completa con scroll natural fluido */
.register-page {
  min-height: 100vh;
  width: 100%;
  background: radial-gradient(circle at 10% 20%, #fef8f4 0%, #f4ede2 90%);
  color: #2D3142;
  padding: 3rem 1.5rem;
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Crucial para evitar que el scroll corte el contenido superior */
}

/* Tarjeta contenedora centrada y amplia */
.register-card-wrapper {
  width: 100%;
  max-width: 820px;
  background-color: #ffffff;
  border-radius: 28px;
  box-shadow: 0 20px 60px rgba(45, 49, 66, 0.08);
  border: 1px solid rgba(230, 222, 200, 0.7);
  padding: 2.8rem 3rem;
  box-sizing: border-box;
  margin-bottom: 3rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: none;
  border: none;
  color: #6c757d;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 1.4rem;
  padding: 0.35rem 0.65rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.back-link:hover {
  color: #E07A5F;
  background-color: #F8EDE7;
  transform: translateX(-3px);
}

.form-header {
  text-align: center;
  margin-bottom: 2.2rem;
}

.header-icon-circle {
  width: 60px;
  height: 60px;
  margin: 0 auto 0.9rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #E07A5F, #f4a261);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 8px 18px rgba(224, 122, 95, 0.35);
}

.header-paw {
  animation: floatPaw 3s ease-in-out infinite;
}

@keyframes floatPaw {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-3px) rotate(6deg); }
}

.register-title {
  font-family: 'Outfit', sans-serif;
  font-size: 2.1rem;
  font-weight: 800;
  color: #1F2430;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.5px;
}

.register-subtitle {
  font-size: 0.95rem;
  color: #64748b;
  max-width: 620px;
  margin: 0 auto;
  line-height: 1.5;
}

/* Banners de estado */
.state-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.1rem 1.4rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  font-size: 0.93rem;
}

.error-state {
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  color: #b91c1c;
  font-weight: 500;
}

.error-icon {
  flex-shrink: 0;
  color: #dc2626;
}

.success-state {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.success-icon {
  flex-shrink: 0;
  color: #16a34a;
}

.state-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.15rem;
  font-weight: 800;
  margin: 0 0 0.25rem 0;
}

.state-msg {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

/* Formulario */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Secciones del formulario */
.form-section-block {
  border: 1px solid #e9e4dc;
  border-radius: 20px;
  padding: 1.6rem 1.6rem 1.4rem;
  margin: 0;
  background-color: #fcfbfa;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-section-block:focus-within {
  border-color: #E07A5F;
  box-shadow: 0 4px 16px rgba(224, 122, 95, 0.08);
  background-color: #ffffff;
}

.section-legend {
  padding: 0 0.5rem;
  margin-left: 0.5rem;
}

.section-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.95rem;
  border-radius: 999px;
  font-size: 0.84rem;
  font-weight: 700;
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.badge-personal {
  background-color: #E07A5F;
}

.badge-hogar {
  background-color: #4E8752;
}

.badge-exp {
  background-color: #3d5a80;
}

.badge-pref {
  background-color: #d97706;
}

.badge-seguridad {
  background-color: #475569;
}

/* Rejilla de campos */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.15rem;
  margin-top: 0.6rem;
}

.three-grid {
  grid-template-columns: 1fr 1fr 1fr;
}

.col-span-2 {
  grid-column: span 2;
}

.input-field-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #334155;
}

.input-inner-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: #94a3b8;
  pointer-events: none;
}

.input-at {
  font-weight: 700;
  font-size: 1rem;
}

.custom-input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.6rem;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  background-color: #ffffff;
  color: #1e293b;
  font-size: 0.92rem;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.custom-input:focus {
  border-color: #E07A5F;
  box-shadow: 0 0 0 3px rgba(224, 122, 95, 0.15);
}

.input-no-icon {
  padding-left: 1rem;
}

.custom-select {
  cursor: pointer;
  appearance: auto;
}

.custom-textarea {
  padding: 0.85rem 1rem;
  resize: vertical;
  min-height: 75px;
  font-family: inherit;
  line-height: 1.45;
}

.toggle-eye-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #94a3b8;
  padding: 0.3rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Radio Cards para Patio y Mascotas */
.radio-check-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 0.85rem 1rem;
}

.toggle-pills {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.3rem;
}

.toggle-pill-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 0.8rem;
  border-radius: 10px;
  border: 1.5px solid #e2e8f0;
  background-color: #f8fafc;
  font-size: 0.84rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.toggle-pill-btn input[type="radio"] {
  display: none;
}

.toggle-pill-btn.active {
  background-color: #F8EDE7;
  border-color: #E07A5F;
  color: #E07A5F;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(224, 122, 95, 0.15);
}

/* 🐾 BOTÓN SUBMIT TIPO HUELLITA 🐾 */
.submit-action-wrap {
  display: flex;
  justify-content: center;
  margin-top: 0.5rem;
}

.btn-huellita {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.9rem;
  width: 100%;
  max-width: 440px;
  padding: 0.85rem 1.8rem;
  font-family: 'Outfit', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #E07A5F, #e76f51);
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  box-shadow: 0 8px 22px rgba(224, 122, 95, 0.35);
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.btn-huellita:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 12px 28px rgba(224, 122, 95, 0.45);
  background: linear-gradient(135deg, #d86c50, #cf5f42);
}

.btn-huellita:active:not(:disabled) {
  transform: translateY(1px) scale(0.98);
}

.btn-huellita:disabled {
  opacity: 0.75;
  cursor: not-allowed;
  transform: none;
}

.huellita-pad {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ffffff;
  color: #E07A5F;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.btn-huellita:hover:not(:disabled) .huellita-pad {
  transform: rotate(-18deg) scale(1.12);
}

.huellita-text {
  letter-spacing: -0.2px;
}

.huellita-trail {
  opacity: 0.8;
  transition: transform 0.3s ease;
}

.btn-huellita:hover:not(:disabled) .huellita-trail {
  transform: translateX(5px) rotate(12deg);
  opacity: 1;
}

.paw-spin {
  animation: pawSpinAnim 1.2s linear infinite;
}

@keyframes pawSpinAnim {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Link inferior */
.form-bottom-link {
  text-align: center;
  font-size: 0.92rem;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.login-link {
  color: #E07A5F;
  font-weight: 700;
  text-decoration: none;
  transition: color 0.2s ease;
}

.login-link:hover {
  text-decoration: underline;
  color: #c85a3f;
}

/* Responsividad para móviles y tablets */
@media (max-width: 768px) {
  .register-card-wrapper {
    padding: 2rem 1.5rem;
    border-radius: 20px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .three-grid {
    grid-template-columns: 1fr;
  }

  .col-span-2 {
    grid-column: span 1;
  }

  .register-title {
    font-size: 1.7rem;
  }
}
</style>
