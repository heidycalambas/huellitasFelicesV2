from flask import Blueprint, jsonify, request

from microservicios.usuarios import repository
from utils.auth import token_required, admin_required

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@usuarios_bp.get("/perfil")
@token_required
def obtener_perfil():
    user = getattr(request, "user", {})
    user_id = int(user.get("id") or user.get("sub"))
    profile = repository.get_user_profile(user_id)
    if not profile:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(profile)


@usuarios_bp.put("/perfil")
@token_required
def actualizar_perfil():
    user = getattr(request, "user", {})
    user_id = int(user.get("id") or user.get("sub"))
    data = request.get_json(silent=True) or {}
    success = repository.update_user_profile(user_id, data)
    profile = repository.get_user_profile(user_id)
    return jsonify({
        "mensaje": "Perfil actualizado exitosamente",
        "usuario": profile,
        "actualizado": success,
    })


@usuarios_bp.get("")
@admin_required
def listar_usuarios():
    role = request.args.get("rol")
    search = request.args.get("q") or request.args.get("search")
    users = repository.get_all_users(role=role, search=search)
    return jsonify({
        "total": len(users),
        "usuarios": users,
    })


@usuarios_bp.get("/<int:user_id>")
@admin_required
def obtener_usuario_admin(user_id):
    profile = repository.get_user_profile(user_id)
    if not profile:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(profile)


@usuarios_bp.put("/<int:user_id>")
@admin_required
def editar_usuario_admin(user_id):
    data = request.get_json(silent=True) or {}
    success = repository.update_user_admin(user_id, data)
    profile = repository.get_user_profile(user_id)
    return jsonify({
        "mensaje": "Usuario actualizado exitosamente por el administrador",
        "usuario": profile,
        "actualizado": success,
    })


@usuarios_bp.patch("/<int:user_id>/estado")
@admin_required
def cambiar_estado_usuario(user_id):
    new_status = repository.toggle_user_status(user_id)
    if new_status is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    estado_texto = "activada" if new_status else "desactivada"
    return jsonify({
        "mensaje": f"Cuenta de usuario {estado_texto} correctamente",
        "id": user_id,
        "activo": new_status,
    })


@admin_bp.get("/estadisticas")
@admin_required
def estadisticas_admin():
    stats = repository.get_admin_dashboard_stats()
    return jsonify(stats)


@admin_bp.get("/actividad")
@admin_required
def actividad_reciente_admin():
    activity = repository.get_admin_recent_activity()
    return jsonify({
        "total": len(activity),
        "actividad": activity,
    })
