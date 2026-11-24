<script setup>
import { reactive, ref } from 'vue'
import { useMascotasStore } from '@/stores/mascotasStore'
import { X, PlusCircle, AlertCircle, CheckCircle2 } from 'lucide-vue-next'

const emit = defineEmits(['close', 'mascotaCreada'])
const mascotasStore = useMascotasStore()

const formData = reactive({
  nombre: '',
  tipo: 'Perro',
  edad: 2,
  sexo: 'Macho',
  tamano: 'Mediano',
  raza: '',
  ciudad: 'Popayan',
  descripcion: '',
  personalidad: 'Cariñoso y juguetón',
  nivel_energia: 'Media',
  compatible_ninos: true,
  compatible_mascotas: true,
  vacunado: true,
  desparasitado: true,
  esterilizado: false,
  refugio_id: 1,
})

const submitting = ref(false)
const errorMessage = ref(null)
const successMessage = ref(null)

async function submitMascota() {
  errorMessage.value = null
  successMessage.value = null

  if (!formData.nombre.trim()) {
    errorMessage.value = 'El nombre de la mascota es obligatorio.'
    return
  }
  if (!formData.tipo) {
    errorMessage.value = 'El tipo de mascota es obligatorio.'
    return
  }
  if (formData.edad === null || formData.edad < 0) {
    errorMessage.value = 'La edad debe ser un número mayor o igual a 0.'
    return
  }

  submitting.value = true
  const res = await mascotasStore.registrarMascota({ ...formData })
  submitting.value = false

  if (res.success) {
    successMessage.value = `¡${formData.nombre} fue registrado con éxito y ya aparece en el catálogo!`
    emit('mascotaCreada')
    setTimeout(() => {
      emit('close')
    }, 1800)
  } else {
    errorMessage.value = res.error
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
          <PlusCircle :size="24" />
        </div>
        <div>
          <h2 class="title">Registrar Nueva Mascota</h2>
          <p class="subtitle">Ingresa la información requerida para publicar una mascota en adopción.</p>
        </div>
      </div>

      <!-- Alertas -->
      <div v-if="successMessage" class="alert-success">
        <CheckCircle2 :size="18" />
        <span>{{ successMessage }}</span>
      </div>
      <div v-if="errorMessage" class="alert-error">
        <AlertCircle :size="18" />
        <span>{{ errorMessage }}</span>
      </div>

      <form @submit.prevent="submitMascota" class="form-body">
        <div class="form-grid">
          <div class="form-group">
            <label class="label">Nombre *</label>
            <input
              type="text"
              v-model="formData.nombre"
              class="input"
              placeholder="Ejemplo: Toby"
              required
            />
          </div>

          <div class="form-group">
            <label class="label">Tipo de Animal *</label>
            <select v-model="formData.tipo" class="input" required>
              <option value="Perro">Perro</option>
              <option value="Gato">Gato</option>
              <option value="Otro">Otro</option>
            </select>
          </div>

          <div class="form-group">
            <label class="label">Edad (en años) *</label>
            <input
              type="number"
              v-model.number="formData.edad"
              min="0"
              max="25"
              class="input"
              required
            />
          </div>

          <div class="form-group">
            <label class="label">Sexo</label>
            <select v-model="formData.sexo" class="input">
              <option value="Macho">Macho</option>
              <option value="Hembra">Hembra</option>
            </select>
          </div>

          <div class="form-group">
            <label class="label">Tamaño</label>
            <select v-model="formData.tamano" class="input">
              <option value="Pequeno">Pequeño</option>
              <option value="Mediano">Mediano</option>
              <option value="Grande">Grande</option>
            </select>
          </div>

          <div class="form-group">
            <label class="label">Raza</label>
            <input
              type="text"
              v-model="formData.raza"
              class="input"
              placeholder="Ejemplo: Criollo, Labrador..."
            />
          </div>

          <div class="form-group">
            <label class="label">Ciudad</label>
            <input
              type="text"
              v-model="formData.ciudad"
              class="input"
              placeholder="Popayan, Cali..."
            />
          </div>

          <div class="form-group">
            <label class="label">Nivel de Energía</label>
            <select v-model="formData.nivel_energia" class="input">
              <option value="Baja">Baja</option>
              <option value="Media">Media</option>
              <option value="Alta">Alta</option>
            </select>
          </div>

          <div class="form-group full-width">
            <label class="label">Personalidad</label>
            <input
              type="text"
              v-model="formData.personalidad"
              class="input"
              placeholder="Ej: Amigable, tranquilo, protector..."
            />
          </div>

          <div class="form-group full-width">
            <label class="label">Descripción</label>
            <textarea
              v-model="formData.descripcion"
              class="input textarea"
              rows="2"
              placeholder="Detalles sobre su historia o características..."
            ></textarea>
          </div>

          <!-- Cuidados y Compatibilidad -->
          <div class="form-group full-width">
            <label class="label">Cuidados y Compatibilidad</label>
            <div class="checkbox-row">
              <label class="chk-item">
                <input type="checkbox" v-model="formData.compatible_ninos" />
                <span>Compatible con niños</span>
              </label>
              <label class="chk-item">
                <input type="checkbox" v-model="formData.compatible_mascotas" />
                <span>Compatible con mascotas</span>
              </label>
              <label class="chk-item">
                <input type="checkbox" v-model="formData.vacunado" />
                <span>Vacunado</span>
              </label>
              <label class="chk-item">
                <input type="checkbox" v-model="formData.desparasitado" />
                <span>Desparasitado</span>
              </label>
              <label class="chk-item">
                <input type="checkbox" v-model="formData.esterilizado" />
                <span>Esterilizado</span>
              </label>
            </div>
          </div>
        </div>

        <div class="form-footer">
          <button type="button" class="btn btn-outline" @click="emit('close')">
            Cancelar
          </button>
          <button type="submit" class="btn btn-secondary" :disabled="submitting">
            <PlusCircle :size="17" />
            <span>{{ submitting ? 'Guardando en base de datos...' : 'Guardar Mascota' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.form-modal {
  max-width: 650px;
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
  margin-bottom: 1.25rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background-color: var(--color-secondary-light);
  color: var(--color-secondary);
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

.alert-success {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  background-color: #dcfce7;
  border: 1px solid #bbf7d0;
  color: #15803d;
  font-size: 0.88rem;
  margin-bottom: 1rem;
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
  margin-bottom: 1rem;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.full-width {
  grid-column: span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.label {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--color-text);
}

.input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  background-color: var(--color-cream);
  color: var(--color-text);
  outline: none;
}

.input:focus {
  border-color: var(--color-secondary);
  background-color: #ffffff;
}

.textarea {
  resize: vertical;
}

.checkbox-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem;
  background: var(--color-cream);
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.chk-item {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.chk-item input {
  accent-color: var(--color-secondary);
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.85rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
</style>
