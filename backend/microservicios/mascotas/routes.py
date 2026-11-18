from flask import Blueprint, jsonify, request

from microservicios.mascotas import repository
from utils.auth import token_required, roles_required, admin_required

mascotas_bp = Blueprint("mascotas", __name__, url_prefix="/api/mascotas")


@mascotas_bp.get("")
def listar_mascotas():
    """Consulta todas las mascotas registradas con filtros opcionales."""
    tipo = request.args.get("tipo")
    ciudad = request.args.get("ciudad")
    estado = request.args.get("estado")
    sexo = request.args.get("sexo")
    tamano = request.args.get("tamano")
    raza = request.args.get("raza")
    min_age = request.args.get("edad_min", type=int)
    max_age = request.args.get("edad_max", type=int)
    refugio_id = request.args.get("refugio_id", type=int)
    search = request.args.get("q") or request.args.get("search")

    pets = repository.get_all_pets(
        pet_type=tipo,
        city=ciudad,
        status=estado,
        sex=sexo,
        size=tamano,
        breed=raza,
        min_age=min_age,
        max_age=max_age,
        refugio_id=refugio_id,
        search=search,
    )
    return jsonify({
        "total": len(pets),
        "mascotas": pets,
    })


@mascotas_bp.get("/refugio/mis-mascotas")
@roles_required("refugio", "admin")
def mis_mascotas_refugio():
    """Consulta las mascotas pertenecientes al refugio autenticado."""
    user = getattr(request, "user", {})
    refugio_id = user.get("refugio_id")
    if not refugio_id:
        # Si es admin o no tiene refugio_id asignado, permitir pasar por query param
        refugio_id = request.args.get("refugio_id", type=int)

    pets = repository.get_all_pets(refugio_id=refugio_id)
    return jsonify({
        "total": len(pets),
        "mascotas": pets,
    })


@mascotas_bp.post("")
@roles_required("admin", "refugio")
def registrar_mascota():
    """Registra una nueva mascota en la plataforma (Admin o Refugio)."""
    data = request.get_json(silent=True) or {}

    nombre = data.get("nombre")
    tipo = data.get("tipo")
    edad = data.get("edad")

    if not nombre or not tipo or edad is None:
        return jsonify({
            "error": "Los campos 'nombre', 'tipo' y 'edad' son obligatorios"
        }), 400

    # Si es usuario refugio, forzar a su propio refugio_id
    user = getattr(request, "user", {})
    if user.get("rol") == "refugio" and user.get("refugio_id"):
        data["refugio_id"] = user.get("refugio_id")

    try:
        pet_id = repository.create_pet(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Error al registrar la mascota: {str(exc)}"}), 500

    profile = repository.get_pet_profile(pet_id)
    return jsonify({
        "mensaje": "Mascota registrada exitosamente",
        "id": pet_id,
        "mascota": profile["mascota"] if profile else {"id": pet_id, "nombre": nombre},
    }), 201


@mascotas_bp.put("/<int:mascota_id>")
@roles_required("admin", "refugio")
def editar_mascota(mascota_id):
    """Edita una mascota existente."""
    data = request.get_json(silent=True) or {}
    
    # Validar que si es refugio, la mascota pertenezca a su refugio
    user = getattr(request, "user", {})
    if user.get("rol") == "refugio":
        profile = repository.get_pet_profile(mascota_id)
        if not profile or profile["mascota"].get("refugio_id") != user.get("refugio_id"):
            return jsonify({"error": "No tienes permiso para modificar esta mascota"}), 403

    updated = repository.update_pet(mascota_id, data)
    if not updated:
        return jsonify({"error": f"No se pudo actualizar la mascota con ID {mascota_id}"}), 400

    profile = repository.get_pet_profile(mascota_id)
    return jsonify({
        "mensaje": "Mascota actualizada exitosamente",
        "mascota": profile["mascota"] if profile else None,
    })


@mascotas_bp.patch("/<int:mascota_id>/estado")
@roles_required("admin", "refugio")
def cambiar_estado_mascota(mascota_id):
    """Cambia el estado de disponibilidad de una mascota."""
    data = request.get_json(silent=True) or {}
    nuevo_estado = data.get("estado")
    if not nuevo_estado:
        return jsonify({"error": "El campo estado es obligatorio"}), 400

    updated = repository.update_pet_status(mascota_id, nuevo_estado)
    if not updated:
        return jsonify({"error": f"No se pudo actualizar el estado de la mascota {mascota_id}"}), 400

    return jsonify({
        "mensaje": "Estado de la mascota actualizado",
        "id": mascota_id,
        "estado": nuevo_estado,
    })


@mascotas_bp.delete("/<int:mascota_id>")
@admin_required
def eliminar_mascota(mascota_id):
    """Elimina una mascota de la plataforma (solo Administrador)."""
    success = repository.delete_pet(mascota_id)
    if not success:
        return jsonify({"error": f"No se pudo eliminar la mascota {mascota_id}"}), 400
    return jsonify({"mensaje": f"Mascota {mascota_id} eliminada correctamente"})


@mascotas_bp.get("/disponibles")
@token_required
def mascotas_disponibles():
    ciudad = request.args.get("ciudad")
    if not ciudad:
        return jsonify({"error": "El parámetro ciudad es obligatorio"}), 400

    pets = repository.search_available_by_city(ciudad)
    return jsonify({
        "ciudad": ciudad,
        "total": len(pets),
        "mascotas": pets,
    })


@mascotas_bp.get("/filtrar")
@token_required
def mascotas_filtrar():
    tipo = request.args.get("tipo")
    edad_min = request.args.get("edad_min", type=int)
    edad_max = request.args.get("edad_max", type=int)

    if not tipo or edad_min is None or edad_max is None:
        return jsonify({
            "error": "Los parámetros tipo, edad_min y edad_max son obligatorios"
        }), 400

    pets = repository.filter_by_type_and_age(tipo, edad_min, edad_max)
    return jsonify({
        "filtros": {
            "tipo": tipo,
            "edad_min": edad_min,
            "edad_max": edad_max,
        },
        "total": len(pets),
        "mascotas": pets,
    })


@mascotas_bp.post("/compatibles")
@token_required
def mascotas_compatibles():
    data = request.get_json(silent=True) or {}
    has_children = bool(data.get("tiene_ninos", False))
    has_other_pets = bool(data.get("tiene_otras_mascotas", False))
    preferred_size = data.get("tamano_hogar") or data.get("tamano")

    if not preferred_size:
        return jsonify({
            "error": "El campo tamano_hogar es obligatorio (Pequeno, Mediano o Grande)"
        }), 400

    pets = repository.find_compatible_pets(
        has_children,
        has_other_pets,
        preferred_size,
    )
    return jsonify({
        "criterios": {
            "tiene_ninos": has_children,
            "tiene_otras_mascotas": has_other_pets,
            "tamano_hogar": preferred_size,
        },
        "total": len(pets),
        "mascotas": pets,
    })


@mascotas_bp.post("/recomendaciones")
@token_required
def mascotas_recomendaciones():
    data = request.get_json(silent=True) or {}

    preferred_type = data.get("tipo", "")
    preferred_size = data.get("tamano", "")
    min_age = data.get("edad_min", 0)
    max_age = data.get("edad_max", 20)
    accepts_children = bool(data.get("acepta_ninos", False))
    accepts_other_pets = bool(data.get("acepta_otras_mascotas", False))

    pets = repository.recommend_pets(
        preferred_type,
        preferred_size,
        int(min_age),
        int(max_age),
        accepts_children,
        accepts_other_pets,
    )
    return jsonify({
        "preferencias": {
            "tipo": preferred_type,
            "tamano": preferred_size,
            "edad_min": min_age,
            "edad_max": max_age,
            "acepta_ninos": accepts_children,
            "acepta_otras_mascotas": accepts_other_pets,
        },
        "total": len(pets),
        "recomendaciones": pets,
    })


@mascotas_bp.get("/estadisticas")
@token_required
def mascotas_estadisticas():
    stats = repository.get_pet_statistics()
    return jsonify(stats)


@mascotas_bp.get("/<int:mascota_id>/perfil")
def mascota_perfil(mascota_id):
    profile = repository.get_pet_profile(mascota_id)
    if not profile:
        return jsonify({"error": f"No existe la mascota con ID {mascota_id}"}), 404
    resp = dict(profile["mascota"])
    resp["mascota"] = profile["mascota"]
    resp["refugio"] = profile["refugio"]
    resp["historial"] = profile["historial"]
    return jsonify(resp)


@mascotas_bp.get("/<int:mascota_id>")
def mascota_detalle(mascota_id):
    profile = repository.get_pet_profile(mascota_id)
    if not profile:
        return jsonify({"error": f"No existe la mascota con ID {mascota_id}"}), 404
    resp = dict(profile["mascota"])
    resp["mascota"] = profile["mascota"]
    resp["refugio"] = profile["refugio"]
    resp["historial"] = profile["historial"]
    return jsonify(resp)
