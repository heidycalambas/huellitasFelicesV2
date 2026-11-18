-- huellitas_felices_clean.sql
-- Archivo único de la base de datos con todas las tablas necesarias.
-- Se incluyen DROP IF EXISTS para evitar colisiones al volver a importar.

DROP DATABASE IF EXISTS huellitas_felices;
CREATE DATABASE huellitas_felices CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE huellitas_felices;

-- =====================================================
-- Tabla: usuarios
-- =====================================================
DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    edad INT NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    tipo_vivienda VARCHAR(50),
    tiene_patio BOOLEAN DEFAULT FALSE,
    otras_mascotas BOOLEAN DEFAULT FALSE,
    tiempo_disponible VARCHAR(50),
    experiencia VARCHAR(255),
    preferencia_tipo VARCHAR(20),
    preferencia_tamano VARCHAR(30),
    preferencia_edad VARCHAR(30),
    rol VARCHAR(30) DEFAULT 'adoptante'
) ENGINE=InnoDB;

-- =====================================================
-- Tabla: refugios
-- =====================================================
DROP TABLE IF EXISTS refugios;
CREATE TABLE refugios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    telefono VARCHAR(30),
    email VARCHAR(100)
) ENGINE=InnoDB;

-- =====================================================
-- Tabla: mascotas
-- =====================================================
DROP TABLE IF EXISTS mascotas;
CREATE TABLE mascotas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    refugio_id INT,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    edad INT NOT NULL,
    sexo VARCHAR(20),
    tamano VARCHAR(30),
    raza VARCHAR(100),
    ciudad VARCHAR(100),
    descripcion VARCHAR(500),
    personalidad VARCHAR(500),
    nivel_energia VARCHAR(30),
    compatible_ninos BOOLEAN DEFAULT FALSE,
    compatible_mascotas BOOLEAN DEFAULT FALSE,
    vacunado BOOLEAN DEFAULT FALSE,
    desparasitado BOOLEAN DEFAULT FALSE,
    esterilizado BOOLEAN DEFAULT FALSE,
    estado VARCHAR(30) DEFAULT 'Disponible',
    FOREIGN KEY (refugio_id) REFERENCES refugios(id)
) ENGINE=InnoDB;

-- =====================================================
-- Tabla: favoritos
-- =====================================================
DROP TABLE IF EXISTS favoritos;
CREATE TABLE favoritos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    mascota_id INT NOT NULL,
    UNIQUE (usuario_id, mascota_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (mascota_id) REFERENCES mascotas(id)
) ENGINE=InnoDB;

-- =====================================================
-- Tabla: adopciones
-- =====================================================
DROP TABLE IF EXISTS adopciones;
CREATE TABLE adopciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    mascota_id INT NOT NULL,
    fecha_solicitud DATE NOT NULL,
    motivo VARCHAR(500),
    lugar_mascota VARCHAR(255),
    personas_casa INT,
    tiene_otras_mascotas BOOLEAN DEFAULT FALSE,
    experiencia VARCHAR(500),
    responsable VARCHAR(100),
    estado VARCHAR(30) DEFAULT 'En revisión',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (mascota_id) REFERENCES mascotas(id)
) ENGINE=InnoDB;

-- =====================================================
-- Tabla: entrevistas
-- =====================================================
DROP TABLE IF EXISTS entrevistas;
CREATE TABLE entrevistas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    adopcion_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    modalidad VARCHAR(30),
    observaciones VARCHAR(500),
    estado VARCHAR(30) DEFAULT 'Programada',
    FOREIGN KEY (adopcion_id) REFERENCES adopciones(id)
) ENGINE=InnoDB;

-- =====================================================
-- Tabla: historial_veterinario
-- =====================================================
DROP TABLE IF EXISTS historial_veterinario;
CREATE TABLE historial_veterinario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mascota_id INT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descripcion VARCHAR(500),
    fecha DATE NOT NULL,
    proxima_fecha DATE,
    veterinario VARCHAR(100),
    observaciones VARCHAR(500),
    FOREIGN KEY (mascota_id) REFERENCES mascotas(id)
) ENGINE=InnoDB;

-- =====================================================
-- Fin del script
-- =====================================================