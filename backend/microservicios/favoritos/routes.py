from flask import Blueprint, jsonify, request

from microservicios.favoritos import repository
from utils.auth import token_required

favoritos_bp = Blueprint("favoritos", __name__, url_prefix="/api/favoritos")


@favoritos_bp.get("")
@token_required
def listar_favoritos():
    user = getattr(request, "user", {})
    usuario_id = int(user.get("id") or user.get("sub"))
    favs = repository.get_user_favorites(usuario_id)
    return jsonify({
        "total": len(favs),
        "favoritos": favs,
    })


@favoritos_bp.get("/ids")
@token_required
def listar_ids_favoritos():
    user = getattr(request, "user", {})
    usuario_id = int(user.get("id") or user.get("sub"))
    ids = repository.get_user_favorite_ids(usuario_id)
    return jsonify({
        "ids": ids,
    })


@favoritos_bp.post("/<int:mascota_id>")
@token_required
def agregar_favorito(mascota_id):
    user = getattr(request, "user", {})
    usuario_id = int(user.get("id") or user.get("sub"))
    ok, msg = repository.add_favorite(usuario_id, mascota_id)
    if not ok:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg, "mascota_id": mascota_id}), 201


@favoritos_bp.delete("/<int:mascota_id>")
@token_required
def eliminar_favorito(mascota_id):
    user = getattr(request, "user", {})
    usuario_id = int(user.get("id") or user.get("sub"))
    deleted = repository.remove_favorite(usuario_id, mascota_id)
    return jsonify({"mensaje": "Eliminado de favoritos", "mascota_id": mascota_id, "eliminado": deleted})
