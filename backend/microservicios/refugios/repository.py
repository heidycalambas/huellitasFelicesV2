from utils.database import get_cursor, serialize_row, serialize_rows


def get_all_shelters():
    query = """
        SELECT
            r.id,
            r.nombre,
            r.ciudad,
            r.direccion,
            r.telefono,
            r.email,
            r.usuario_id,
            u.usuario AS usuario_username,
            u.nombre AS usuario_nombre,
            COUNT(DISTINCT m.id) AS total_mascotas,
            SUM(CASE WHEN m.estado = 'Disponible' THEN 1 ELSE 0 END) AS mascotas_disponibles,
            SUM(CASE WHEN m.estado = 'Adoptada' THEN 1 ELSE 0 END) AS mascotas_adoptadas
        FROM refugios r
        LEFT JOIN usuarios u ON r.usuario_id = u.id
        LEFT JOIN mascotas m ON m.refugio_id = r.id
        GROUP BY r.id
        ORDER BY r.id ASC
    """
    with get_cursor() as cursor:
        cursor.execute(query)
        return serialize_rows(cursor.fetchall())


def get_shelter_by_id(refugio_id):
    query = """
        SELECT
            r.id,
            r.nombre,
            r.ciudad,
            r.direccion,
            r.telefono,
            r.email,
            r.usuario_id,
            u.usuario AS usuario_username,
            u.nombre AS usuario_nombre
        FROM refugios r
        LEFT JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.id = %s
    """
    with get_cursor() as cursor:
        cursor.execute(query, (refugio_id,))
        return serialize_row(cursor.fetchone())


def get_shelter_by_user_id(usuario_id):
    query = """
        SELECT
            r.id,
            r.nombre,
            r.ciudad,
            r.direccion,
            r.telefono,
            r.email,
            r.usuario_id
        FROM refugios r
        WHERE r.usuario_id = %s
        LIMIT 1
    """
    with get_cursor() as cursor:
        cursor.execute(query, (usuario_id,))
        return serialize_row(cursor.fetchone())


def create_shelter(data):
    nombre = (data.get("nombre") or "").strip()
    ciudad = (data.get("ciudad") or "").strip()
    direccion = data.get("direccion", "")
    telefono = data.get("telefono", "")
    email = data.get("email", "")
    usuario_id = data.get("usuario_id") or None

    if not nombre or not ciudad:
        raise ValueError("El nombre y la ciudad del refugio son obligatorios")

    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO refugios (nombre, ciudad, direccion, telefono, email, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nombre, ciudad, direccion, telefono, email, usuario_id),
        )
        return cursor.lastrowid


def update_shelter(refugio_id, data):
    fields = []
    params = []
    for key in ["nombre", "ciudad", "direccion", "telefono", "email", "usuario_id"]:
        if key in data:
            fields.append(f"{key} = %s")
            params.append(data[key])

    if not fields:
        return False

    params.append(refugio_id)
    query = f"UPDATE refugios SET {', '.join(fields)} WHERE id = %s"

    with get_cursor(commit=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.rowcount > 0


def get_shelter_dashboard(refugio_id):
    with get_cursor() as cursor:
        # Mascotas del refugio
        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE refugio_id = %s", (refugio_id,))
        total_mascotas = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE refugio_id = %s AND estado = 'Disponible'", (refugio_id,))
        disponibles = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE refugio_id = %s AND estado = 'Adoptada'", (refugio_id,))
        adoptadas = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE refugio_id = %s AND estado IN ('En revisión', 'Entrevista', 'Proceso')", (refugio_id,))
        en_proceso = cursor.fetchone()["total"]

        # Solicitudes pendientes de mascotas de este refugio
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM adopciones a
            JOIN mascotas m ON a.mascota_id = m.id
            WHERE m.refugio_id = %s AND a.estado IN ('En revisión', 'Entrevista')
        """, (refugio_id,))
        solicitudes_pendientes = cursor.fetchone()["total"]

        # Entrevistas programadas para este refugio
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM entrevistas e
            JOIN adopciones a ON e.adopcion_id = a.id
            JOIN mascotas m ON a.mascota_id = m.id
            WHERE m.refugio_id = %s AND e.estado = 'Programada'
        """, (refugio_id,))
        entrevistas_programadas = cursor.fetchone()["total"]

        # Distribución por tipo
        cursor.execute("""
            SELECT tipo, COUNT(*) AS cantidad
            FROM mascotas
            WHERE refugio_id = %s
            GROUP BY tipo
        """, (refugio_id,))
        por_tipo = serialize_rows(cursor.fetchall())

        return {
            "mascotas_registradas": total_mascotas,
            "mascotas_disponibles": disponibles,
            "mascotas_en_proceso": en_proceso,
            "mascotas_adoptadas": adoptadas,
            "solicitudes_pendientes": solicitudes_pendientes,
            "entrevistas_programadas": entrevistas_programadas,
            "por_tipo": por_tipo,
        }
