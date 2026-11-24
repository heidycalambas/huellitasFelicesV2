import os
import uuid
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import Config
from utils.auth import authenticate_user, create_token, token_required, hash_password
from utils.database import get_cursor

# Configuración de carpeta para subida local de archivos de mascotas
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Importar Blueprints de los microservicios
from microservicios.mascotas.routes import mascotas_bp
from microservicios.adopciones.routes import adopciones_bp, entrevistas_bp
from microservicios.veterinario.routes import (
    veterinario_mascotas_bp,
    seguimiento_bp,
)
from microservicios.favoritos.routes import favoritos_bp
from microservicios.refugios.routes import refugios_bp
from microservicios.usuarios.routes import usuarios_bp, admin_bp

app = Flask(__name__)

# Configuración de CORS permitiendo peticiones desde el frontend (puerto 5174 y otros)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "X-API-KEY", "x-api-key"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)


@app.get("/")
def health():
    return jsonify({
        "plataforma": "Huellitas Felices — Plataforma Web de Adopción de Mascotas",
        "servicios": [
            "Gestión y Búsqueda de Mascotas",
            "Gestión de Adopciones y Entrevistas",
            "Seguimiento Veterinario",
            "Favoritos de Usuarios",
            "Gestión de Refugios",
            "Administración del Sistema",
        ],
        "puerto": Config.SERVER_PORT,
        "estado": "activo",
    })


@app.post("/api/upload")
def subir_archivo():
    """Permite subir una fotografía de mascota localmente desde el dispositivo."""
    if "file" not in request.files and "foto" not in request.files:
        return jsonify({"error": "No se envió ningún archivo en la petición"}), 400

    file = request.files.get("file") or request.files.get("foto")
    if not file or file.filename == "":
        return jsonify({"error": "Nombre de archivo inválido o vacío"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Formato de archivo no permitido. Use imágenes JPG, JPEG, PNG, WEBP o GIF"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"mascota_{uuid.uuid4().hex[:12]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # URL completa accesible por el frontend
    base_url = request.host_url.rstrip("/")
    url = f"{base_url}/uploads/{filename}"

    return jsonify({
        "mensaje": "Fotografía subida exitosamente",
        "url": url,
        "filename": filename,
    }), 201


@app.get("/uploads/<filename>")
def servir_archivo_subido(filename):
    """Sirve los archivos locales subidos para mostrarlos en el frontend."""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.post("/auth/login")
@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    usuario = (data.get("usuario") or "").strip()
    password = data.get("password") or ""

    if not usuario or not password:
        return jsonify({"error": "usuario y password son obligatorios"}), 400

    user = authenticate_user(usuario, password)
    if not user:
        return jsonify({"error": "Credenciales inválidas"}), 401

    if user.get("activo") is False or user.get("activo") == 0:
        return jsonify({"error": "Esta cuenta de usuario ha sido desactivada. Comunícate con el administrador."}), 403

    token = create_token(user)
    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "token": token,
        "usuario": {
            "id": user["id"],
            "nombre": user["nombre"],
            "usuario": user["usuario"],
            "rol": user["rol"],
            "ciudad": user.get("ciudad"),
            "experiencia": user.get("experiencia"),
            "tipo_vivienda": user.get("tipo_vivienda"),
            "refugio_id": user.get("refugio_id"),
            "refugio_nombre": user.get("refugio_nombre"),
        },
    })


@app.post("/auth/register")
@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    usuario = (data.get("usuario") or "").strip()
    password = data.get("password") or ""
    ciudad = (data.get("ciudad") or "Popayán").strip()
    edad = int(data.get("edad") or 25)

    tipo_vivienda = data.get("tipo_vivienda") or "Casa"
    tiene_patio = 1 if bool(data.get("tiene_patio", False)) else 0
    otras_mascotas = 1 if bool(data.get("otras_mascotas", False)) else 0
    tiempo_disponible = data.get("tiempo_disponible") or "Medio"
    experiencia = (data.get("experiencia") or "Amante de los animales").strip()
    preferencia_tipo = data.get("preferencia_tipo") or "Todos"
    preferencia_tamano = data.get("preferencia_tamano") or "Mediano"
    preferencia_edad = data.get("preferencia_edad") or "Joven"

    if not nombre or not usuario or not password:
        return jsonify({"error": "nombre, usuario y password son obligatorios"}), 400

    try:
        with get_cursor(commit=True) as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
            if cursor.fetchone():
                return jsonify({"error": "El nombre de usuario ya se encuentra registrado"}), 409

            
            cursor.execute(
                """
                INSERT INTO usuarios (
                    nombre, usuario, password, edad, ciudad, tipo_vivienda,
                    tiene_patio, otras_mascotas, tiempo_disponible, experiencia,
                    preferencia_tipo, preferencia_tamano, preferencia_edad, rol, activo
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, 'adoptante', TRUE
                )
                RETURNING id
                """,
                (
                    nombre,
                    usuario,
                    hash_password(password),
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
                ),
            )

            nuevo_id = cursor.fetchone()["id"]

            cursor.execute(
                """
                SELECT id, nombre, usuario, rol, ciudad, tipo_vivienda, tiene_patio,
                       otras_mascotas, tiempo_disponible, experiencia, preferencia_tipo,
                       preferencia_tamano, preferencia_edad
                FROM usuarios WHERE id = %s
                """,
                (nuevo_id,),
            )
            nuevo_usuario = cursor.fetchone()

        return jsonify({
            "mensaje": "Usuario adoptante registrado exitosamente",
            "usuario": nuevo_usuario,
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar usuario: {str(e)}"}), 500


@app.get("/auth/me")
@app.get("/api/auth/me")
@token_required
def me():
    """Endpoint para verificar sesión y obtener información del usuario actual."""
    user = getattr(request, "user", {})
    # Refrescar info completa desde DB
    with get_cursor() as cursor:
        cursor.execute("SELECT id, nombre, usuario, rol, ciudad, edad, activo FROM usuarios WHERE id = %s", (user.get("id"),))
        db_user = cursor.fetchone()

    return jsonify({
        "usuario": db_user or user,
        "valido": True,
    })


# Registrar Blueprints
app.register_blueprint(mascotas_bp)
app.register_blueprint(adopciones_bp)
app.register_blueprint(entrevistas_bp)
app.register_blueprint(veterinario_mascotas_bp)
app.register_blueprint(seguimiento_bp)
app.register_blueprint(favoritos_bp)
app.register_blueprint(refugios_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(admin_bp)


if __name__ == "__main__":
    port = Config.SERVER_PORT
    print("==================================================")
    print("  HUELLITAS FELICES — BACKEND UNIFICADO (FLASK)")
    print("==================================================")
    print(f"  Servidor corriendo en: http://localhost:{port}")
    print(f"  Microservicio Mascotas: http://localhost:{port}/api/mascotas")
    print(f"  Microservicio Adopciones: http://localhost:{port}/api/adopciones")
    print(f"  Microservicio Veterinario: http://localhost:{port}/api/seguimiento")
    print(f"  Microservicio Favoritos: http://localhost:{port}/api/favoritos")
    print(f"  Microservicio Refugios: http://localhost:{port}/api/refugios")
    print(f"  Microservicio Usuarios y Admin: http://localhost:{port}/api/usuarios")
    print("==================================================")
    app.run(
        host=Config.SERVER_HOST,
        port=port,
        debug=True,
    )
