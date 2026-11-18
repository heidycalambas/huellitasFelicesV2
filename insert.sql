USE huellitas_felices;

-- Contraseñas (SHA-256):
-- admin / admin123
-- carlos / adoptante123
-- maria / adoptante123
-- juan / adoptante123
-- laura / adoptante123

INSERT INTO refugios
(nombre, ciudad, direccion, telefono, email)
VALUES
('Huellitas Popayan', 'Popayan', 'Carrera 6 # 10-25', '3001112233', 'huellitas.popayan@gmail.com'),
('Refugio Patitas Felices', 'Popayan', 'Calle 12 # 5-40', '3002223344', 'patitasfelices@gmail.com'),
('Fundacion Amigos Peludos', 'Cali', 'Carrera 20 # 15-30', '3003334455', 'amigospeludos@gmail.com');

INSERT INTO usuarios
(
    nombre,
    usuario,
    password,
    edad,
    ciudad,
    tipo_vivienda,
    tiene_patio,
    otras_mascotas,
    tiempo_disponible,
    experiencia,
    preferencia_tipo,
    preferencia_tamano,
    preferencia_edad,
    rol
)
VALUES
(
    'Administrador Sistema',
    'admin',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    30,
    'Popayan',
    'Casa',
    1,
    0,
    'Alta',
    'Administrador del sistema',
    NULL,
    NULL,
    NULL,
    'admin'
),
(
    'Carlos Perez',
    'carlos',
    'c8775dee4a4e7db87c6a9fb1d30067ef0835f0b717d86d7f4fefb91ff6960f40',
    25,
    'Popayan',
    'Casa',
    1,
    0,
    'Alta',
    'Tiene experiencia cuidando perros',
    'Perro',
    'Mediano',
    'Joven',
    'adoptante'
),
(
    'Maria Gomez',
    'maria',
    'c8775dee4a4e7db87c6a9fb1d30067ef0835f0b717d86d7f4fefb91ff6960f40',
    30,
    'Popayan',
    'Apartamento',
    0,
    1,
    'Media',
    'Tiene experiencia con gatos',
    'Gato',
    'Pequeno',
    'Joven',
    'adoptante'
),
(
    'Juan Rodriguez',
    'juan',
    'c8775dee4a4e7db87c6a9fb1d30067ef0835f0b717d86d7f4fefb91ff6960f40',
    28,
    'Cali',
    'Casa',
    1,
    1,
    'Alta',
    'Experiencia con perros y gatos',
    'Perro',
    'Mediano',
    'Adulto',
    'adoptante'
),
(
    'Laura Sanchez',
    'laura',
    'c8775dee4a4e7db87c6a9fb1d30067ef0835f0b717d86d7f4fefb91ff6960f40',
    35,
    'Popayan',
    'Casa',
    1,
    0,
    'Media',
    'Primera vez teniendo mascota',
    'Perro',
    'Pequeno',
    'Joven',
    'adoptante'
);


INSERT INTO mascotas
(
    refugio_id,
    nombre,
    tipo,
    edad,
    sexo,
    tamano,
    raza,
    ciudad,
    descripcion,
    personalidad,
    nivel_energia,
    compatible_ninos,
    compatible_mascotas,
    vacunado,
    desparasitado,
    esterilizado,
    estado
)
VALUES
(
    1,
    'Luna',
    'Perro',
    2,
    'Hembra',
    'Mediano',
    'Labrador',
    'Popayan',
    'Perra joven, cariñosa y sociable.',
    'Amigable',
    'Alta',
    1,
    1,
    1,
    1,
    1,
    'Disponible'
),
(
    1,
    'Max',
    'Perro',
    5,
    'Macho',
    'Grande',
    'Pastor Aleman',
    'Popayan',
    'Perro tranquilo y protector.',
    'Leal',
    'Media',
    1,
    0,
    1,
    1,
    1,
    'Disponible'
),
(
    2,
    'Michi',
    'Gato',
    1,
    'Hembra',
    'Pequeno',
    'Criollo',
    'Popayan',
    'Gata pequena y juguetona.',
    'Juguetona',
    'Alta',
    1,
    1,
    0,
    1,
    0,
    'Disponible'
),
(
    2,
    'Simba',
    'Gato',
    4,
    'Macho',
    'Mediano',
    'Criollo',
    'Cali',
    'Gato tranquilo y cariñoso.',
    'Cariñoso',
    'Media',
    1,
    0,
    1,
    1,
    1,
    'Disponible'
),
(
    3,
    'Rocky',
    'Perro',
    8,
    'Macho',
    'Mediano',
    'Beagle',
    'Cali',
    'Perro adulto y tranquilo.',
    'Tranquilo',
    'Baja',
    1,
    1,
    1,
    1,
    1,
    'Adoptada'
),
(
    3,
    'Nala',
    'Perro',
    3,
    'Hembra',
    'Pequeno',
    'Criollo',
    'Bogota',
    'Perra pequena y activa.',
    'Juguetona',
    'Alta',
    0,
    1,
    0,
    0,
    0,
    'Disponible'
);

INSERT INTO adopciones
(
    usuario_id,
    mascota_id,
    fecha_solicitud,
    motivo,
    lugar_mascota,
    personas_casa,
    tiene_otras_mascotas,
    experiencia,
    responsable,
    estado
)
VALUES
(
    2,
    1,
    '2026-09-01',
    'Desea adoptar una mascota para compañía y cuenta con espacio suficiente.',
    'Casa con patio en Popayan',
    3,
    0,
    'Tiene experiencia cuidando perros.',
    'Carlos Perez',
    'En revisión'
),
(
    3,
    3,
    '2026-09-02',
    'Desea adoptar un gato joven para compañía.',
    'Apartamento en Popayan',
    2,
    1,
    'Tiene experiencia cuidando gatos.',
    'Maria Gomez',
    'Entrevista'
),
(
    4,
    4,
    '2026-09-03',
    'Desea adoptar una mascota para su familia.',
    'Casa con patio en Cali',
    4,
    1,
    'Tiene experiencia con perros y gatos.',
    'Juan Rodriguez',
    'Aprobada'
),
(
    5,
    6,
    '2026-09-04',
    'Busca una mascota pequeña para compañía.',
    'Casa con patio en Popayan',
    2,
    0,
    'No tiene experiencia previa.',
    'Laura Sanchez',
    'En revisión'
);


INSERT INTO entrevistas
(
    adopcion_id,
    fecha,
    hora,
    modalidad,
    observaciones,
    estado
)
VALUES
(
    1,
    '2026-10-20',
    '10:00:00',
    'Virtual',
    'Verificar condiciones de vivienda y disponibilidad de tiempo.',
    'Programada'
),
(
    2,
    '2026-10-22',
    '15:00:00',
    'Presencial',
    'Revisar compatibilidad con otras mascotas.',
    'Programada'
),
(
    3,
    '2026-09-08',
    '09:00:00',
    'Presencial',
    'Entrevista realizada satisfactoriamente.',
    'Realizada'
);


INSERT INTO historial_veterinario
(
    mascota_id,
    tipo,
    descripcion,
    fecha,
    proxima_fecha,
    veterinario,
    observaciones
)
VALUES
(
    1,
    'Vacuna',
    'Vacuna antirrábica aplicada',
    '2026-08-01',
    '2027-08-01',
    'Dra. Ana Ruiz',
    'Sin reacciones adversas'
),
(
    1,
    'Control',
    'Control general de peso y estado físico',
    '2026-09-15',
    '2026-10-15',
    'Dra. Ana Ruiz',
    'Estado de salud óptimo'
),
(
    2,
    'Vacuna',
    'Vacuna múltiple (moquillo, parvovirus)',
    '2026-07-10',
    '2026-10-10',
    'Dr. Pedro López',
    'Próxima dosis de refuerzo'
),
(
    2,
    'Desparasitación',
    'Desparasitación interna y externa',
    '2026-09-01',
    '2026-12-01',
    'Dr. Pedro López',
    NULL
),
(
    3,
    'Control',
    'Revisión inicial al ingreso al refugio',
    '2026-09-20',
    '2026-10-20',
    'Dra. Ana Ruiz',
    'Pendiente esquema de vacunación'
),
(
    4,
    'Vacuna',
    'Vacuna triple felina',
    '2026-06-15',
    '2027-06-15',
    'Dra. Carmen Díaz',
    'Completo'
),
(
    5,
    'Control',
    'Control post-adopción',
    '2026-08-20',
    '2026-11-20',
    'Dr. Pedro López',
    'Mascota adaptada correctamente'
),
(
    6,
    'Desparasitación',
    'Primera desparasitación',
    '2026-09-25',
    '2026-10-25',
    'Dra. Carmen Díaz',
    'Pendiente vacunación y esterilización'
);
