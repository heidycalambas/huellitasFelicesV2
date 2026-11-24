from datetime import date

from utils.database import get_cursor, serialize_row, serialize_rows


def pet_exists(mascota_id):
    with get_cursor() as cursor:
        cursor.execute("SELECT id FROM mascotas WHERE id = %s", (mascota_id,))
        return cursor.fetchone() is not None


def get_veterinary_history(mascota_id):
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                h.id,
                h.mascota_id,
                m.nombre AS mascota_nombre,
                h.tipo,
                h.descripcion,
                h.fecha,
                h.proxima_fecha,
                h.veterinario,
                h.observaciones
            FROM historial_veterinario h
            INNER JOIN mascotas m ON h.mascota_id = m.id
            WHERE h.mascota_id = %s
            ORDER BY h.fecha DESC, h.id DESC
            """,
            (mascota_id,),
        )
        return serialize_rows(cursor.fetchall())


def register_control(
    mascota_id,
    tipo,
    descripcion,
    fecha,
    proxima_fecha,
    veterinario,
    observaciones,
):
    with get_cursor(commit=True) as cursor:
        cursor.execute("SELECT id FROM mascotas WHERE id = %s", (mascota_id,))
        if not cursor.fetchone():
            return None

        cursor.execute(
            """
            INSERT INTO historial_veterinario (
                mascota_id,
                tipo,
                descripcion,
                fecha,
                proxima_fecha,
                veterinario,
                observaciones
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                mascota_id,
                tipo,
                descripcion,
                fecha,
                proxima_fecha,
                veterinario,
                observaciones,
            ),
        )
        control_id = cursor.lastrowid

        tipo_lower = tipo.lower()
        if "vacuna" in tipo_lower:
            cursor.execute(
                "UPDATE mascotas SET vacunado = 1 WHERE id = %s",
                (mascota_id,),
            )
        if "desparasit" in tipo_lower:
            cursor.execute(
                "UPDATE mascotas SET desparasitado = 1 WHERE id = %s",
                (mascota_id,),
            )
        if "esteril" in tipo_lower:
            cursor.execute(
                "UPDATE mascotas SET esterilizado = 1 WHERE id = %s",
                (mascota_id,),
            )

        return control_id


def get_pending_vaccines_and_care():
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                m.id AS mascota_id,
                m.nombre,
                m.tipo,
                m.ciudad,
                m.estado,
                m.vacunado,
                m.desparasitado,
                m.esterilizado,
                CASE
                    WHEN m.vacunado = 0 THEN 'Vacunación pendiente'
                    WHEN EXISTS (
                        SELECT 1
                        FROM historial_veterinario h
                        WHERE h.mascota_id = m.id
                          AND h.tipo LIKE '%Vacuna%'
                          AND h.proxima_fecha IS NOT NULL
                          AND h.proxima_fecha <= CURDATE()
                    ) THEN 'Refuerzo de vacuna vencido'
                    WHEN m.desparasitado = 0 THEN 'Desparasitación pendiente'
                    WHEN m.esterilizado = 0 THEN 'Esterilización pendiente'
                    ELSE 'Revisión de cuidados'
                END AS cuidado_pendiente
            FROM mascotas m
            WHERE m.vacunado = 0
               OR m.desparasitado = 0
               OR m.esterilizado = 0
               OR EXISTS (
                    SELECT 1
                    FROM historial_veterinario h
                    WHERE h.mascota_id = m.id
                      AND h.tipo LIKE '%Vacuna%'
                      AND h.proxima_fecha IS NOT NULL
                      AND h.proxima_fecha <= CURDATE()
               )
            ORDER BY m.nombre ASC
            """
        )
        return serialize_rows(cursor.fetchall())


def get_upcoming_controls(days=30):
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                h.id,
                h.mascota_id,
                m.nombre AS mascota_nombre,
                m.tipo AS mascota_tipo,
                h.tipo,
                h.descripcion,
                h.fecha,
                h.proxima_fecha,
                h.veterinario,
                h.observaciones,
                DATEDIFF(h.proxima_fecha, CURDATE()) AS dias_restantes
            FROM historial_veterinario h
            INNER JOIN mascotas m ON h.mascota_id = m.id
            WHERE h.proxima_fecha IS NOT NULL
              AND h.proxima_fecha BETWEEN CURDATE()
                  AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY h.proxima_fecha ASC
            """,
            (days,),
        )
        return serialize_rows(cursor.fetchall())


def get_tracking_summary(mascota_id):
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                nombre,
                tipo,
                edad,
                ciudad,
                estado,
                vacunado,
                desparasitado,
                esterilizado
            FROM mascotas
            WHERE id = %s
            """,
            (mascota_id,),
        )
        pet = cursor.fetchone()
        if not pet:
            return None

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM historial_veterinario
            WHERE mascota_id = %s
            """,
            (mascota_id,),
        )
        total_registros = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT
                id,
                tipo,
                descripcion,
                fecha,
                proxima_fecha,
                veterinario
            FROM historial_veterinario
            WHERE mascota_id = %s
            ORDER BY fecha DESC, id DESC
            LIMIT 1
            """,
            (mascota_id,),
        )
        ultimo = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                id,
                tipo,
                descripcion,
                fecha,
                proxima_fecha,
                veterinario
            FROM historial_veterinario
            WHERE mascota_id = %s
              AND proxima_fecha IS NOT NULL
              AND proxima_fecha >= CURDATE()
            ORDER BY proxima_fecha ASC
            LIMIT 1
            """,
            (mascota_id,),
        )
        proximo = cursor.fetchone()

        cursor.execute(
            """
            SELECT tipo, COUNT(*) AS cantidad
            FROM historial_veterinario
            WHERE mascota_id = %s
            GROUP BY tipo
            ORDER BY tipo
            """,
            (mascota_id,),
        )
        por_tipo = cursor.fetchall()

        pendientes = []
        if not pet["vacunado"]:
            pendientes.append("Vacunación")
        if not pet["desparasitado"]:
            pendientes.append("Desparasitación")
        if not pet["esterilizado"]:
            pendientes.append("Esterilización")

        return {
            "mascota": serialize_row(pet),
            "total_registros": total_registros,
            "ultimo_control": serialize_row(ultimo),
            "proximo_control": serialize_row(proximo),
            "registros_por_tipo": serialize_rows(por_tipo),
            "cuidados_pendientes": pendientes,
            "estado_salud": (
                "Al día" if not pendientes else "Requiere atención"
            ),
            "fecha_consulta": date.today().isoformat(),
        }


def get_health_indicators():
    with get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM mascotas")
        total_mascotas = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM mascotas WHERE vacunado = 1"
        )
        vacunadas = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM mascotas WHERE desparasitado = 1"
        )
        desparasitadas = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM mascotas WHERE esterilizado = 1"
        )
        esterilizadas = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM mascotas
            WHERE vacunado = 0 OR desparasitado = 0 OR esterilizado = 0
            """
        )
        con_cuidados_pendientes = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM historial_veterinario
            WHERE proxima_fecha BETWEEN CURDATE()
              AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            """
        )
        controles_proximos_30 = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM historial_veterinario
            WHERE proxima_fecha IS NOT NULL
              AND proxima_fecha < CURDATE()
            """
        )
        controles_vencidos = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT tipo, COUNT(*) AS cantidad
            FROM historial_veterinario
            GROUP BY tipo
            ORDER BY cantidad DESC
            """
        )
        por_tipo_control = serialize_rows(cursor.fetchall())

        def porcentaje(parte):
            if total_mascotas == 0:
                return 0
            return round((parte / total_mascotas) * 100, 2)

        return {
            "total_mascotas": total_mascotas,
            "vacunadas": vacunadas,
            "porcentaje_vacunadas": porcentaje(vacunadas),
            "desparasitadas": desparasitadas,
            "porcentaje_desparasitadas": porcentaje(desparasitadas),
            "esterilizadas": esterilizadas,
            "porcentaje_esterilizadas": porcentaje(esterilizadas),
            "con_cuidados_pendientes": con_cuidados_pendientes,
            "controles_proximos_30_dias": controles_proximos_30,
            "controles_vencidos": controles_vencidos,
            "controles_por_tipo": por_tipo_control,
        }


def get_all_veterinary_records(refugio_id=None):
    """Consulta todos los registros veterinarios con información de mascota y refugio."""
    query = """
        SELECT
            h.id,
            h.mascota_id,
            m.nombre AS mascota_nombre,
            m.tipo AS mascota_tipo,
            m.foto_url AS mascota_foto_url,
            m.refugio_id,
            r.nombre AS refugio_nombre,
            h.tipo,
            h.descripcion,
            h.fecha,
            h.proxima_fecha,
            h.veterinario,
            h.observaciones
        FROM historial_veterinario h
        INNER JOIN mascotas m ON h.mascota_id = m.id
        LEFT JOIN refugios r ON m.refugio_id = r.id
        WHERE 1=1
    """
    params = []
    if refugio_id:
        query += " AND m.refugio_id = %s"
        params.append(refugio_id)

    query += " ORDER BY h.fecha DESC, h.id DESC"

    with get_cursor() as cursor:
        cursor.execute(query, tuple(params))
        return serialize_rows(cursor.fetchall())


def update_control(control_id, data):
    fields = []
    params = []
    for key in ["tipo", "descripcion", "fecha", "proxima_fecha", "veterinario", "observaciones"]:
        if key in data:
            fields.append(f"{key} = %s")
            params.append(data[key])

    if not fields:
        return False

    params.append(control_id)
    query = f"UPDATE historial_veterinario SET {', '.join(fields)} WHERE id = %s"

    with get_cursor(commit=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.rowcount > 0


def delete_control(control_id):
    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM historial_veterinario WHERE id = %s", (control_id,))
        return cursor.rowcount > 0
