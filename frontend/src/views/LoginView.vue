<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import {
  Heart,
  Lock,
  User,
  Eye,
  EyeOff,
  AlertCircle,
  ArrowLeft,
  PawPrint,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  usuario: '',
  password: '',
})

const showPassword = ref(false)
const localValidation = ref(null)

// Cuentas de prueba para agilizar la evaluación
const demoUsers = [
  { usuario: 'carlos', pass: 'adoptante123', label: 'Carlos (Adoptante)' },
  { usuario: 'maria', pass: 'adoptante123', label: 'María (Adoptante)' },
  { usuario: 'refugio_1', pass: 'refugio123', label: 'Refugio Popayán' },
  { usuario: 'admin', pass: 'admin123', label: 'Administrador' },
]

function setDemoUser(user) {
  form.usuario = user.usuario
  form.password = user.pass
  localValidation.value = null
}

async function handleLogin() {
  localValidation.value = null

  if (!form.usuario.trim()) {
    localValidation.value = 'Por favor ingresa tu usuario.'
    return
  }
  if (!form.password) {
    localValidation.value = 'Por favor ingresa tu contraseña.'
    return
  }

  const result = await authStore.login(form.usuario.trim(), form.password)
  if (result.success) {
    const rol = result.user?.rol
    if (rol === 'admin') {
      router.push('/admin')
    } else if (rol === 'refugio') {
      router.push('/refugio')
    } else {
      router.push('/app')
    }
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card-wrapper">
      <!-- Botón para volver al inicio -->
      <button class="back-link" @click="router.push('/')" title="Volver a la página principal">
        <ArrowLeft :size="16" />
        <span>Volver al inicio</span>
      </button>

      <div class="login-form-panel">
        <div class="form-container">
          <!-- Encabezado con logo amigable -->
          <div class="form-header">
            <div class="logo-circle">
              <PawPrint :size="26" class="logo-paw" />
            </div>
            <h1 class="login-title">Bienvenido de nuevo</h1>
            <p class="login-sub">
              Ingresa tus credenciales para acceder a la plataforma Huellitas Felices.
            </p>
          </div>

          <!-- Mensajes de Error (Validación o Credenciales inválidas) -->
          <div v-if="localValidation || authStore.error" class="error-banner">
            <AlertCircle :size="18" class="error-icon" />
            <span>{{ localValidation || authStore.error }}</span>
          </div>

          <!-- Formulario de inicio de sesión -->
          <form @submit.prevent="handleLogin" class="auth-form">
            <div class="input-group">
              <label class="input-label" for="usuario">Usuario o Correo Electrónico</label>
              <div class="input-field-wrap">
                <User :size="18" class="field-icon" />
                <input
                  id="usuario"
                  type="text"
                  v-model="form.usuario"
                  placeholder="Ej: carlos o admin"
                  class="text-input"
                  autocomplete="username"
                  required
                />
              </div>
            </div>

            <div class="input-group">
              <label class="input-label" for="password">Contraseña</label>
              <div class="input-field-wrap">
                <Lock :size="18" class="field-icon" />
                <input
                  id="password"
                  :type="showPassword ? 'text' : 'password'"
                  v-model="form.password"
                  placeholder="Tu contraseña secreta"
                  class="text-input"
                  autocomplete="current-password"
                  required
                />
                <button
                  type="button"
                  class="toggle-eye"
                  @click="showPassword = !showPassword"
                  title="Mostrar / ocultar contraseña"
                >
                  <Eye v-if="!showPassword" :size="18" />
                  <EyeOff v-else :size="18" />
                </button>
              </div>
            </div>

            <!-- Botón de Inicio de Sesión Tipo Huellita -->
            <button
              type="submit"
              class="btn-huellita submit-btn"
              :disabled="authStore.loading"
            >
              <span class="huellita-pad">
                <PawPrint :size="20" class="paw-icon" :class="{ 'paw-spin': authStore.loading }" />
              </span>
              <span class="huellita-text" v-if="!authStore.loading">Iniciar Sesión</span>
              <span class="huellita-text" v-else>Verificando credenciales...</span>
            </button>
          </form>

          <!-- Acceso Rápido con Cuentas de Prueba -->
          <div class="demo-section">
            <span class="demo-title">Cuentas de prueba para evaluar:</span>
            <div class="demo-pills">
              <button
                v-for="u in demoUsers"
                :key="u.usuario"
                type="button"
                class="demo-chip"
                @click="setDemoUser(u)"
                title="Hacer clic para autocompletar este usuario"
              >
                {{ u.label }}
              </button>
            </div>
          </div>

          <!-- Enlace de Registro -->
          <div class="form-bottom">
            <span>¿Aún no tienes una cuenta?</span>
            <button type="button" class="link-btn" @click="router.push('/register')">
              Crear una cuenta nueva
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  background: radial-gradient(circle at 10% 20%, #fef8f4 0%, #f4ede2 90%);
  font-family: var(--font-body);
}

.login-card-wrapper {
  width: 100%;
  max-width: 520px;
  background-color: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: 0 25px 60px -15px rgba(45, 49, 66, 0.12);
  border: 1px solid var(--color-border);
  padding: 2.2rem 2.4rem;
  box-sizing: border-box;
  position: relative;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 0.86rem;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 1.2rem;
  padding: 0.35rem 0.6rem;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.back-link:hover {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
  transform: translateX(-2px);
}

.login-form-panel {
  display: flex;
  justify-content: center;
}

.form-container {
  width: 100%;
}

.form-header {
  text-align: center;
  margin-bottom: 1.6rem;
}

.logo-circle {
  width: 58px;
  height: 58px;
  margin: 0 auto 0.8rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), #f4a261);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 6px 16px rgba(224, 122, 95, 0.35);
}

.logo-paw {
  animation: floatPaw 3s ease-in-out infinite;
}

@keyframes floatPaw {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-3px) rotate(6deg); }
}

.login-title {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 0.35rem;
  letter-spacing: -0.4px;
}

.login-sub {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  line-height: 1.45;
  margin: 0;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  color: #b91c1c;
  padding: 0.8rem 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.2rem;
  font-size: 0.88rem;
  font-weight: 500;
}

.error-icon {
  flex-shrink: 0;
  color: #dc2626;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.input-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-text);
}

.input-field-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.field-icon {
  position: absolute;
  left: 14px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.text-input {
  width: 100%;
  padding: 0.8rem 2.8rem 0.8rem 2.7rem;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  background-color: var(--color-cream);
  color: var(--color-text);
  font-size: 0.95rem;
  outline: none;
  transition: all var(--transition-fast);
  box-sizing: border-box;
}

.text-input:focus {
  border-color: var(--color-primary);
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(224, 122, 95, 0.15);
}

.toggle-eye {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: var(--color-text-muted);
  padding: 0.3rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 🐾 BOTÓN TIPO HUELLITA 🐾 */
.btn-huellita {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
  width: 100%;
  padding: 0.72rem 1.4rem;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, var(--color-primary), #e76f51);
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(224, 122, 95, 0.35);
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  margin-top: 0.4rem;
}

.btn-huellita:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 10px 24px rgba(224, 122, 95, 0.45);
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
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #ffffff;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.btn-huellita:hover:not(:disabled) .huellita-pad {
  transform: rotate(-18deg) scale(1.1);
}

.huellita-text {
  letter-spacing: -0.2px;
}

.huellita-trail {
  opacity: 0.8;
  transition: transform 0.3s ease;
}

.btn-huellita:hover:not(:disabled) .huellita-trail {
  transform: translateX(4px) rotate(12deg);
  opacity: 1;
}

.paw-spin {
  animation: pawSpinAnim 1.2s linear infinite;
}

@keyframes pawSpinAnim {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.demo-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: var(--color-beige);
  padding: 0.85rem;
  border-radius: var(--radius-md);
  border: 1px dashed var(--color-border);
  margin-top: 1.3rem;
}

.demo-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.demo-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.demo-chip {
  background: #ffffff;
  border: 1px solid var(--color-border);
  padding: 0.35rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.demo-chip:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.form-bottom {
  text-align: center;
  margin-top: 1.4rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
}

.link-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  font-weight: 700;
  cursor: pointer;
  padding: 0;
  font-size: 0.9rem;
}

.link-btn:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .login-card-wrapper {
    padding: 1.8rem 1.4rem;
    border-radius: var(--radius-lg);
  }
}
</style>
