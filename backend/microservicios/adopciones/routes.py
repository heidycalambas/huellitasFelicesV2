from datetime import date
from flask import Blueprint, jsonify, request

from microservicios.adopciones import repository
from utils.auth import token_required, roles_required, admin_required

adopciones_bp = Blueprint("adopciones", __name__, url_prefix="/api/adopciones")
entrevistas_bp = Blueprint("entrevistas", __name__, url_prefix="/api/entrevistas")


@adopciones_bp.get("")
@token_required
def listar_adopciones():
    """Consulta todas las solicitudes de adopción con filtros según el rol del usuario."""
    user = getattr(request, "user", {})
    user_role = user.get("rol")
    user_id = int(user.get("id") or user.get("sub") or 0)
    refugio_id_user = user.get("refugio_id")

    req_usuario_id = request.args.get("usuario_id", type=int)
    req_refugio_id = request.args.get("refugio_id", type=int)
    req_mascota_id = request.args.get("mascota_id", type=int)
    estado = request.args.get("estado")

    # Control de acceso seguro por rol
    if user_role == "adoptante":
        # Un adoptante solo puede consultar sus propias solicitudes
        final_usuario_id = user_id
        final_refugio_id = None
    elif user_role == "refugio":
        # Un refugio solo consulta las solicitudes de sus mascotas
        final_usuario_id = req_usuario_id
        final_refugio_id = refugio_id_user or req_refugio_id
    else:
        # Administrador puede consultar todo o filtrar libremente
        final_usuario_id = req_usuario_id
        final_refugio_id = req_refugio_id

    adoptions = repository.get_all_adoptions(
        usuario_id=final_usuario_id,
        refugio_id=final_refugio_id,
        estado=estado,
        mascota_id=req_mascota_id,
    )
    return jsonify({
        "total": len(adoptions),
        "adopciones": adoptions,
    })


@adopciones_bp.get("/pendientes")
@roles_required("admin", "refugio")
def adopciones_pendientes():
    user = getattr(request, "user", {})
    refugio_id = user.get("refugio_id") if user.get("rol") == "refugio" else None
    adoptions = repository.get_pending_adoptions(refugio_id=refugio_id)
    return jsonify({
        "total": len(adoptions),
        "adopciones": adoptions,
    })


@adopciones_bp.get("/<int:adopcion_id>")
@token_required
def adopcion_detalle(adopcion_id):
    adoption = repository.get_adoption_by_id(adopcion_id)
    if not adoption:
        return jsonify({"error": f"No existe la adopción con ID {adopcion_id}"}), 404

    # Verificar que el usuario tenga permiso de ver esta solicitud
    user = getattr(request, "user", {})
    if user.get("rol") == "adoptante" and adoption["usuario_id"] != int(user.get("id") or user.get("sub")):
        return jsonify({"error": "No tienes permiso para ver esta solicitud"}), 403
    if user.get("rol") == "refugio" and user.get("refugio_id") and adoption["refugio_id"] != user.get("refugio_id"):
        return jsonify({"error": "Esta solicitud no corresponde a tu refugio"}), 403

    return jsonify(adoption)


@adopciones_bp.post("")
@token_required
def crear_adopcion():
    data = request.get_json(silent=True) or {}
    user = getattr(request, "user", {})

    usuario_id = user.get("id") or user.get("sub")
    responsable = (data.get("responsable") or user.get("nombre") or user.get("usuario") or "").strip()

    data["usuario_id"] = usuario_id
    data["responsable"] = responsable

    required = [
        "usuario_id",
        "mascota_id",
        "motivo",
        "lugar_mascota",
        "personas_casa",
        "experiencia",
        "responsable",
    ]
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        return jsonify({
            "error": f"Campos obligatorios faltantes: {', '.join(missing)}"
        }), 400

    fecha_solicitud = data.get("fecha_solicitud") or date.today().isoformat()

    try:
        adoption_id = repository.create_adoption(
            int(usuario_id),
            int(data["mascota_id"]),
            fecha_solicitud,
            data["motivo"].strip(),
            data["lugar_mascota"].strip(),
            int(data["personas_casa"]),
            bool(data.get("tiene_otras_mascotas", False)),
            data["experiencia"].strip(),
            responsable,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Error al crear la solicitud: {str(exc)}"}), 500

    return jsonify({
        "mensaje": "Solicitud de adopción creada correctamente",
        "id": adoption_id,
        "estado": "En revisión",
    }), 201


@adopciones_bp.patch("/<int:adopcion_id>/estado")
@roles_required("admin", "refugio")
def actualizar_estado(adopcion_id):
    data = request.get_json(silent=True) or {}
    nuevo_estado = data.get("estado")

    if not nuevo_estado:
        return jsonify({"error": "El campo estado es obligatorio"}), 400

    # Si es refugio, verificar pertenencia
    user = getattr(request, "user", {})
    if user.get("rol") == "refugio":
        adoption = repository.get_adoption_by_id(adopcion_id)
        if not adoption or adoption.get("refugio_id") != user.get("refugio_id"):
            return jsonify({"error": "No tienes permiso para gestionar esta solicitud"}), 403

    try:
        updated = repository.update_adoption_status(adopcion_id, nuevo_estado)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updated:
        return jsonify({"error": f"No existe la adopción con ID {adopcion_id}"}), 404

    return jsonify({
        "mensaje": "Estado actualizado correctamente",
        "id": adopcion_id,
        "estado": nuevo_estado,
    })


@adopciones_bp.post("/<int:adopcion_id>/entrevista")
@roles_required("admin", "refugio")
def programar_entrevista(adopcion_id):
    data = request.get_json(silent=True) or {}

    fecha = data.get("fecha")
    hora = data.get("hora")
    modalidad = data.get("modalidad") or "Virtual"
    observaciones = data.get("observaciones", "")

    if not fecha or not hora:
        return jsonify({
            "error": "Los campos fecha y hora son obligatorios"
        }), 400

    interview_id = repository.schedule_interview(
        adopcion_id,
        fecha,
        hora,
        modalidad,
        observaciones,
    )

    if interview_id is None:
        return jsonify({"error": f"No existe la adopción con ID {adopcion_id}"}), 404

    return jsonify({
        "mensaje": "Entrevista programada correctamente",
        "entrevista_id": interview_id,
        "adopcion_id": adopcion_id,
        "fecha": fecha,
        "hora": hora,
        "modalidad": modalidad,
    }), 201


@entrevistas_bp.get("")
@token_required
def listar_todas_entrevistas():
    """Lista entrevistas según permisos del usuario autenticado."""
    user = getattr(request, "user", {})
    user_role = user.get("rol")
    user_id = int(user.get("id") or user.get("sub") or 0)
    refugio_id_user = user.get("refugio_id")

    req_usuario_id = request.args.get("usuario_id", type=int)
    req_refugio_id = request.args.get("refugio_id", type=int)
    req_adopcion_id = request.args.get("adopcion_id", type=int)
    estado = request.args.get("estado")

    if user_role == "adoptante":
        final_usuario_id = user_id
        final_refugio_id = None
    elif user_role == "refugio":
        final_usuario_id = req_usuario_id
        final_refugio_id = refugio_id_user or req_refugio_id
    else:
        final_usuario_id = req_usuario_id
        final_refugio_id = req_refugio_id

    interviews = repository.get_interviews(
        usuario_id=final_usuario_id,
        refugio_id=final_refugio_id,
        adopcion_id=req_adopcion_id,
        estado=estado,
    )
    return jsonify({
        "total": len(interviews),
        "entrevistas": interviews,
    })


@entrevistas_bp.patch("/<int:entrevista_id>")
@roles_required("admin", "refugio")
def actualizar_entrevista(entrevista_id):
    """Actualiza una entrevista (estado, observaciones, fecha, hora)."""
    data = request.get_json(silent=True) or {}
    success = repository.update_interview(entrevista_id, data)
    if not success:
        return jsonify({"error": f"No se pudo actualizar la entrevista con ID {entrevista_id}"}), 400

    return jsonify({
        "mensaje": "Entrevista actualizada correctamente",
        "id": entrevista_id,
    })


@entrevistas_bp.get("/proximas")
@token_required
def entrevistas_proximas():
    interviews = repository.get_interviews(estado="Programada")
    return jsonify({
        "total": len(interviews),
        "entrevistas": interviews,
    })
