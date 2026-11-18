from flask import Blueprint, jsonify, request

from microservicios.refugios import repository
from utils.auth import token_required, roles_required, admin_required

refugios_bp = Blueprint("refugios", __name__, url_prefix="/api/refugios")


@refugios_bp.get("")
@token_required
def listar_refugios():
    shelters = repository.get_all_shelters()
    return jsonify({
        "total": len(shelters),
        "refugios": shelters,
    })


@refugios_bp.get("/mi-refugio")
@roles_required("refugio", "admin")
def obtener_mi_refugio():
    user = getattr(request, "user", {})
    refugio_id = user.get("refugio_id")
    usuario_id = int(user.get("id") or user.get("sub"))

    if refugio_id:
        shelter = repository.get_shelter_by_id(refugio_id)
    else:
        shelter = repository.get_shelter_by_user_id(usuario_id)

    if not shelter:
        return jsonify({"error": "No se encontró un refugio asociado a esta cuenta"}), 404

    dashboard = repository.get_shelter_dashboard(shelter["id"])
    return jsonify({
        "refugio": shelter,
        "metricas": dashboard,
    })


@refugios_bp.put("/mi-refugio")
@roles_required("refugio", "admin")
def actualizar_mi_refugio():
    user = getattr(request, "user", {})
    refugio_id = user.get("refugio_id")
    usuario_id = int(user.get("id") or user.get("sub"))

    if not refugio_id:
        shelter = repository.get_shelter_by_user_id(usuario_id)
        if shelter:
            refugio_id = shelter["id"]

    if not refugio_id:
        return jsonify({"error": "No se encontró un refugio asociado a esta cuenta"}), 404

    data = request.get_json(silent=True) or {}
    success = repository.update_shelter(refugio_id, data)
    return jsonify({"mensaje": "Datos del refugio actualizados correctamente", "actualizado": success})


@refugios_bp.get("/<int:refugio_id>")
@token_required
def detalle_refugio(refugio_id):
    shelter = repository.get_shelter_by_id(refugio_id)
    if not shelter:
        return jsonify({"error": f"No existe el refugio con ID {refugio_id}"}), 404
    return jsonify(shelter)


@refugios_bp.post("")
@admin_required
def crear_refugio():
    data = request.get_json(silent=True) or {}
    try:
        new_id = repository.create_shelter(data)
        shelter = repository.get_shelter_by_id(new_id)
        return jsonify({
            "mensaje": "Refugio registrado exitosamente",
            "refugio": shelter,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al crear refugio: {str(e)}"}), 500


@refugios_bp.put("/<int:refugio_id>")
@admin_required
def editar_refugio(refugio_id):
    data = request.get_json(silent=True) or {}
    success = repository.update_shelter(refugio_id, data)
    if not success:
        return jsonify({"error": f"No se pudo actualizar el refugio {refugio_id}"}), 400
    return jsonify({"mensaje": "Refugio actualizado correctamente"})
