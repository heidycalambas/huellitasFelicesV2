import hashlib
from utils.database import get_cursor, serialize_row, serialize_rows


def get_user_profile(user_id):
    query = """
        SELECT
            id, nombre, usuario, edad, ciudad, tipo_vivienda, tiene_patio,
            otras_mascotas, tiempo_disponible, experiencia, preferencia_tipo,
            preferencia_tamano, preferencia_edad, rol, activo
        FROM usuarios
        WHERE id = %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (user_id,))
        return serialize_row(cursor.fetchone())


def update_user_profile(user_id, data):
    fields = []
    params = []

    updatable = [
        "nombre", "edad", "ciudad", "tipo_vivienda", "tiene_patio",
        "otras_mascotas", "tiempo_disponible", "experiencia",
        "preferencia_tipo", "preferencia_tamano", "preferencia_edad"
    ]

    for key in updatable:
        if key in data:
            val = data[key]
            if key in ["tiene_patio", "otras_mascotas"]:
                val = 1 if bool(val) else 0
            elif key == "edad" and val is not None:
                val = int(val)
            fields.append(f"{key} = %s")
            params.append(val)

    # Si se envía nueva contraseña
    if data.get("password") and data.get("password").strip():
        new_hash = hashlib.sha256(data["password"].strip().encode("utf-8")).hexdigest()
        fields.append("password = %s")
        params.append(new_hash)

    if not fields:
        return False

    params.append(user_id)
    query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"

    with get_cursor(commit=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.rowcount > 0


def get_all_users(role=None, search=None):
    query = """
        SELECT
            id, nombre, usuario, edad, ciudad, rol, activo,
            tipo_vivienda, tiene_patio, otras_mascotas, tiempo_disponible,
            experiencia, preferencia_tipo, preferencia_tamano, preferencia_edad
        FROM usuarios
        WHERE 1=1
    """
    params = []

    if role and role.lower() != "todos":
        query += " AND LOWER(rol) = LOWER(%s)"
        params.append(role)

    if search and search.strip():
        query += " AND (LOWER(nombre) LIKE LOWER(%s) OR LOWER(usuario) LIKE LOWER(%s) OR LOWER(ciudad) LIKE LOWER(%s))"
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    query += " ORDER BY id DESC"

    with get_cursor() as cursor:
        cursor.execute(query, tuple(params))
        return serialize_rows(cursor.fetchall())


def update_user_admin(user_id, data):
    fields = []
    params = []

    for key in ["nombre", "usuario", "edad", "ciudad", "rol", "activo"]:
        if key in data:
            val = data[key]
            if key == "activo":
                val = 1 if bool(val) else 0
            elif key == "edad" and val is not None:
                val = int(val)
            fields.append(f"{key} = %s")
            params.append(val)

    if data.get("password") and data.get("password").strip():
        new_hash = hashlib.sha256(data["password"].strip().encode("utf-8")).hexdigest()
        fields.append("password = %s")
        params.append(new_hash)

    if not fields:
        return False

    params.append(user_id)
    query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"

    with get_cursor(commit=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.rowcount > 0


def toggle_user_status(user_id):
    with get_cursor(commit=True) as cursor:
        cursor.execute("SELECT activo FROM usuarios WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        current = bool(row["activo"])
        new_status = 0 if current else 1
        cursor.execute("UPDATE usuarios SET activo = %s WHERE id = %s", (new_status, user_id))
        return bool(new_status)


def get_admin_dashboard_stats():
    with get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
        total_usuarios = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE rol = 'adoptante'")
        total_adoptantes = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM refugios")
        total_refugios = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas")
        total_mascotas = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE estado = 'Disponible'")
        mascotas_disponibles = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE estado = 'Adoptada'")
        mascotas_adoptadas = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE tipo = 'Perro'")
        perros = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE tipo = 'Gato'")
        gatos = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM adopciones")
        solicitudes_recibidas = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM adopciones WHERE estado IN ('En revisión', 'Entrevista')")
        solicitudes_pendientes = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM adopciones WHERE estado = 'Aprobada'")
        adopciones_realizadas = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM entrevistas WHERE estado = 'Programada'")
        entrevistas_programadas = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT estado, COUNT(*) AS cantidad
            FROM adopciones
            GROUP BY estado
        """)
        solicitudes_por_estado = serialize_rows(cursor.fetchall())

        cursor.execute("""
            SELECT ciudad, COUNT(*) AS cantidad
            FROM mascotas
            GROUP BY ciudad
            ORDER BY cantidad DESC
        """)
        mascotas_por_ciudad = serialize_rows(cursor.fetchall())

        cursor.execute("""
            SELECT DATE_FORMAT(fecha_solicitud, '%Y-%m') AS mes, COUNT(*) AS cantidad
            FROM adopciones
            WHERE estado = 'Aprobada'
            GROUP BY mes
            ORDER BY mes ASC
            LIMIT 12
        """)
        adopciones_por_mes = serialize_rows(cursor.fetchall())

        return {
            "total_usuarios": total_usuarios,
            "total_adoptantes": total_adoptantes,
            "total_refugios": total_refugios,
            "total_mascotas": total_mascotas,
            "mascotas_disponibles": mascotas_disponibles,
            "mascotas_adoptadas": mascotas_adoptadas,
            "perros": perros,
            "gatos": gatos,
            "solicitudes_recibidas": solicitudes_recibidas,
            "solicitudes_pendientes": solicitudes_pendientes,
            "adopciones_realizadas": adopciones_realizadas,
            "entrevistas_programadas": entrevistas_programadas,
            "solicitudes_por_estado": solicitudes_por_estado,
            "mascotas_por_ciudad": mascotas_por_ciudad,
            "adopciones_por_mes": adopciones_por_mes,
        }


def get_admin_recent_activity():
    with get_cursor() as cursor:
        # Últimas solicitudes de adopción
        cursor.execute("""
            SELECT
                'adopcion' AS tipo_actividad,
                a.id,
                a.fecha_solicitud AS fecha,
                CONCAT(u.nombre, ' solicitó adoptar a ', m.nombre) AS descripcion,
                a.estado
            FROM adopciones a
            JOIN usuarios u ON a.usuario_id = u.id
            JOIN mascotas m ON a.mascota_id = m.id
            ORDER BY a.id DESC
            LIMIT 6
        """)
        recent_adoptions = cursor.fetchall()

        # Últimas entrevistas
        cursor.execute("""
            SELECT
                'entrevista' AS tipo_actividad,
                e.id,
                e.fecha,
                CONCAT('Entrevista ', e.modalidad, ' para ', m.nombre, ' con ', u.nombre) AS descripcion,
                e.estado
            FROM entrevistas e
            JOIN adopciones a ON e.adopcion_id = a.id
            JOIN usuarios u ON a.usuario_id = u.id
            JOIN mascotas m ON a.mascota_id = m.id
            ORDER BY e.id DESC
            LIMIT 6
        """)
        recent_interviews = cursor.fetchall()

        all_act = serialize_rows(recent_adoptions + recent_interviews)
        all_act.sort(key=lambda x: str(x.get("fecha")), reverse=True)
        return all_act[:8]
