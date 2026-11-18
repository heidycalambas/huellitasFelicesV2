from datetime import date
from flask import Blueprint, jsonify, request

from microservicios.veterinario import repository
from utils.auth import token_required

veterinario_mascotas_bp = Blueprint("veterinario_mascotas", __name__, url_prefix="/api/mascotas")
seguimiento_bp = Blueprint("seguimiento", __name__, url_prefix="/api/seguimiento")


@veterinario_mascotas_bp.get("/<int:mascota_id>/historial-veterinario")
@token_required
def historial_veterinario(mascota_id):
    if not repository.pet_exists(mascota_id):
        return jsonify({"error": f"No existe la mascota con ID {mascota_id}"}), 404

    history = repository.get_veterinary_history(mascota_id)
    return jsonify({
        "mascota_id": mascota_id,
        "total": len(history),
        "historial": history,
    })


@veterinario_mascotas_bp.post("/<int:mascota_id>/controles")
@token_required
def registrar_control(mascota_id):
    data = request.get_json(silent=True) or {}

    tipo = data.get("tipo")
    descripcion = data.get("descripcion")
    fecha = data.get("fecha") or date.today().isoformat()
    proxima_fecha = data.get("proxima_fecha")
    veterinario = data.get("veterinario")
    observaciones = data.get("observaciones")

    if not tipo or not descripcion:
        return jsonify({
            "error": "Los campos tipo y descripcion son obligatorios"
        }), 400

    control_id = repository.register_control(
        mascota_id,
        tipo,
        descripcion,
        fecha,
        proxima_fecha,
        veterinario,
        observaciones,
    )

    if control_id is None:
        return jsonify({"error": f"No existe la mascota con ID {mascota_id}"}), 404

    return jsonify({
        "mensaje": "Control veterinario registrado correctamente",
        "id": control_id,
        "mascota_id": mascota_id,
        "tipo": tipo,
        "fecha": fecha,
        "proxima_fecha": proxima_fecha,
    }), 201


@seguimiento_bp.get("/vacunas-pendientes")
@token_required
def vacunas_pendientes():
    items = repository.get_pending_vaccines_and_care()
    return jsonify({
        "total": len(items),
        "mascotas": items,
    })


@seguimiento_bp.get("/proximos-controles")
@token_required
def proximos_controles():
    dias = request.args.get("dias", default=30, type=int)
    if dias < 1:
        return jsonify({"error": "El parámetro dias debe ser mayor a 0"}), 400

    controls = repository.get_upcoming_controls(dias)
    return jsonify({
        "dias": dias,
        "total": len(controls),
        "controles": controls,
    })


@seguimiento_bp.get("/resumen/<int:mascota_id>")
@token_required
def resumen_seguimiento(mascota_id):
    summary = repository.get_tracking_summary(mascota_id)
    if not summary:
        return jsonify({"error": f"No existe la mascota con ID {mascota_id}"}), 404
    return jsonify(summary)


@seguimiento_bp.get("/indicadores")
@token_required
def indicadores():
    return jsonify(repository.get_health_indicators())


@seguimiento_bp.get("/todos")
@token_required
def todos_los_controles():
    user = getattr(request, "user", {})
    refugio_id = user.get("refugio_id") if user.get("rol") == "refugio" else request.args.get("refugio_id", type=int)
    records = repository.get_all_veterinary_records(refugio_id=refugio_id)
    return jsonify({
        "total": len(records),
        "historial": records,
    })


@seguimiento_bp.put("/controles/<int:control_id>")
@token_required
def actualizar_control(control_id):
    data = request.get_json(silent=True) or {}
    success = repository.update_control(control_id, data)
    if not success:
        return jsonify({"error": f"No se pudo actualizar el control veterinario {control_id}"}), 400
    return jsonify({"mensaje": "Control veterinario actualizado correctamente", "id": control_id})


@seguimiento_bp.delete("/controles/<int:control_id>")
@token_required
def eliminar_control(control_id):
    user = getattr(request, "user", {})
    if user.get("rol") != "admin":
        return jsonify({"error": "Solo el administrador puede eliminar registros médicos"}), 403

    success = repository.delete_control(control_id)
    if not success:
        return jsonify({"error": f"No se pudo eliminar el control veterinario {control_id}"}), 400
    return jsonify({"mensaje": f"Control veterinario {control_id} eliminado correctamente"})
