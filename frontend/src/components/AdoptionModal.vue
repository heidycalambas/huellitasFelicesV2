<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useAdopcionesStore } from '@/stores/adopcionesStore'
import { X, Heart, AlertCircle, CheckCircle2, Home, Users, HelpCircle } from 'lucide-vue-next'

const props = defineProps({
  mascota: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'adopcionCompletada'])

const authStore = useAuthStore()
const adopcionesStore = useAdopcionesStore()

const formData = reactive({
  motivo: '',
  lugar_mascota: authStore.user?.tipo_vivienda ? `${authStore.user.tipo_vivienda} en ${authStore.user.ciudad || 'la ciudad'}` : '',
  personas_casa: 2,
  tiene_otras_mascotas: false,
  experiencia: authStore.user?.experiencia || '',
  responsable: authStore.user?.nombre || authStore.user?.usuario || '',
})

const localError = ref(null)
const successDone = ref(false)

onMounted(() => {
  adopcionesStore.limpiarMensajes()
})

async function submitAdopcion() {
  localError.value = null

  if (!formData.motivo.trim()) {
    localError.value = 'Por favor, indícanos el motivo por el cual deseas adoptar.'
    return
  }
  if (!formData.lugar_mascota.trim()) {
    localError.value = 'Por favor, describe las condiciones del lugar donde vivirá la mascota.'
    return
  }
  if (formData.personas_casa < 1) {
    localError.value = 'El número de personas en casa debe ser al menos 1.'
    return
  }
  if (!formData.experiencia.trim()) {
    localError.value = 'Por favor, cuéntanos si tienes experiencia previa con animales.'
    return
  }

  const payload = {
    usuario_id: authStore.user?.id,
    mascota_id: props.mascota.id,
    motivo: formData.motivo,
    lugar_mascota: formData.lugar_mascota,
    personas_casa: formData.personas_casa,
    tiene_otras_mascotas: formData.tiene_otras_mascotas,
    experiencia: formData.experiencia,
    responsable: formData.responsable,
  }

  const res = await adopcionesStore.crearSolicitud(payload)
  if (res.success) {
    successDone.value = true
    emit('adopcionCompletada')
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content form-modal">
      <button class="close-btn" @click="emit('close')" title="Cerrar">
        <X :size="20" />
      </button>

      <div class="modal-header">
        <div class="header-icon">
          <Heart :size="24" />
        </div>
        <div>
          <h2 class="title">Solicitud de Adopción</h2>
          <p class="subtitle">Estás iniciando el proceso para adoptar a <strong>{{ mascota.nombre }}</strong> ({{ mascota.tipo }} - {{ mascota.raza || 'Criollo' }})</p>
        </div>
      </div>

      <!-- Pantalla de Éxito -->
      <div v-if="successDone" class="success-screen">
        <CheckCircle2 :size="56" class="success-icon" />
        <h3 class="success-title">¡Solicitud Registrada con Éxito!</h3>
        <p class="success-text">
          Tu solicitud de adopción para <strong>{{ mascota.nombre }}</strong> fue enviada al refugio y actualmente se encuentra <strong>En revisión</strong>.
        </p>
        <p class="success-sub">
          El equipo del refugio se pondrá en contacto contigo para coordinar una entrevista y continuar el proceso. Puedes hacer seguimiento desde la sección <em>"Mis solicitudes"</em>.
        </p>
        <button class="btn btn-primary" @click="emit('close')">
          Entendido, volver al inicio
        </button>
      </div>

      <!-- Formulario de Registro de Adopción -->
      <form v-else @submit.prevent="submitAdopcion" class="form-body">
        <!-- Alertas de Error -->
        <div v-if="localError || adopcionesStore.error" class="alert-error">
          <AlertCircle :size="18" />
          <span>{{ localError || adopcionesStore.error }}</span>
        </div>

        <div class="form-grid">
          <div class="form-group full-width">
            <label class="label">Responsable Principal</label>
            <input
              type="text"
              v-model="formData.responsable"
              class="input"
              required
              placeholder="Nombre completo del solicitante"
            />
          </div>

          <div class="form-group full-width">
            <label class="label">¿Por qué deseas adoptar a {{ mascota.nombre }}? *</label>
            <textarea
              v-model="formData.motivo"
              class="input textarea"
              rows="2"
              required
              placeholder="Cuéntanos tus motivaciones y el compromiso con la mascota..."
            ></textarea>
          </div>

          <div class="form-group full-width">
            <label class="label">Condiciones de vivienda *</label>
            <input
              type="text"
              v-model="formData.lugar_mascota"
              class="input"
              required
              placeholder="Ejemplo: Casa con patio cerrado en Popayán"
            />
          </div>

          <div class="form-group">
            <label class="label">Personas en el hogar</label>
            <input
              type="number"
              v-model.number="formData.personas_casa"
              min="1"
              max="20"
              class="input"
              required
            />
          </div>

          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="formData.tiene_otras_mascotas"
                class="checkbox"
              />
              <span>¿Actualmente convives con otras mascotas?</span>
            </label>
          </div>

          <div class="form-group full-width">
            <label class="label">Experiencia previa con animales *</label>
            <textarea
              v-model="formData.experiencia"
              class="input textarea"
              rows="2"
              required
              placeholder="¿Has tenido perros/gatos antes? Cuéntanos brevemente..."
            ></textarea>
          </div>
        </div>

        <div class="form-footer">
          <button type="button" class="btn btn-outline" @click="emit('close')">
            Cancelar
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="adopcionesStore.submitting"
          >
            <Heart :size="17" />
            <span>{{ adopcionesStore.submitting ? 'Enviando solicitud...' : 'Confirmar y Enviar Solicitud' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.form-modal {
  max-width: 620px;
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
  margin-top: 0.2rem;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.alert-error {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  font-size: 0.88rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.full-width {
  grid-column: span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.label {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--color-text);
}

.input {
  width: 100%;
  padding: 0.7rem 0.95rem;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  background-color: var(--color-cream);
  color: var(--color-text);
  outline: none;
  transition: all var(--transition-fast);
}

.input:focus {
  border-color: var(--color-primary);
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(224, 122, 95, 0.15);
}

.textarea {
  resize: vertical;
}

.checkbox-group {
  justify-content: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
  cursor: pointer;
}

.checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
  cursor: pointer;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.85rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.success-screen {
  text-align: center;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.success-icon {
  color: var(--color-secondary);
}

.success-title {
  font-size: 1.45rem;
  color: var(--color-text);
}

.success-text {
  font-size: 0.95rem;
  color: var(--color-text);
  max-width: 480px;
}

.success-sub {
  font-size: 0.86rem;
  color: var(--color-text-muted);
  max-width: 460px;
}
</style>
