import hashlib
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import jsonify, request

from config import Config
from utils.database import get_cursor, serialize_row


def hash_password(password: str) -> str:
    """Genera hash SHA-256 para contraseñas, 100% compatible con los datos iniciales de prueba."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_token(user: dict) -> str:
    payload = {
        "sub": str(user["id"]),
        "id": user["id"],
        "usuario": user["usuario"],
        "nombre": user.get("nombre", ""),
        "rol": user["rol"],
        "ciudad": user.get("ciudad", ""),
        "refugio_id": user.get("refugio_id"),
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRES_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        Config.JWT_SECRET,
        algorithms=["HS256"],
        options={"verify_sub": False},
    )


def authenticate_user(usuario: str, password: str):
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nombre, usuario, password, edad, ciudad, tipo_vivienda,
                   tiene_patio, otras_mascotas, tiempo_disponible, experiencia,
                   preferencia_tipo, preferencia_tamano, preferencia_edad, rol,
                   activo
            FROM usuarios
            WHERE usuario = %s
            """,
            (usuario,),
        )
        user = cursor.fetchone()

    if not user:
        return None

    if user["password"] != hash_password(password):
        return None

    # Si es refugio, asociar el ID del refugio si existe
    user_serialized = serialize_row(user)
    if user_serialized.get("rol") == "refugio":
        with get_cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre FROM refugios WHERE usuario_id = %s LIMIT 1",
                (user_serialized["id"],),
            )
            refugio = cursor.fetchone()
            if refugio:
                user_serialized["refugio_id"] = refugio["id"]
                user_serialized["refugio_nombre"] = refugio["nombre"]

    return user_serialized


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verificar API Key si se envía o si está configurada obligatoriamente
        api_key_header = request.headers.get("X-API-KEY")
        if Config.API_KEY and api_key_header:
            if api_key_header != Config.API_KEY:
                return jsonify({"error": "X-API-KEY inválida"}), 403

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token no proporcionado"}), 401

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        request.user = payload
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*roles):
    """Decorador para autorizar roles específicos en el backend."""
    def decorator(fn):
        @wraps(fn)
        @token_required
        def wrapper(*args, **kwargs):
            user_role = getattr(request, "user", {}).get("rol")
            if user_role not in roles and user_role != "admin":
                return jsonify({"error": f"Acceso no autorizado para el rol '{user_role}'"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    return roles_required("admin")(fn)


def api_key_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            return jsonify({"error": "Encabezado X-API-KEY no proporcionado"}), 401
        if Config.API_KEY and api_key != Config.API_KEY:
            return jsonify({"error": "X-API-KEY inválida"}), 403
        return fn(*args, **kwargs)

    return wrapper
