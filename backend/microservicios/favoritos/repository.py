from utils.database import get_cursor, serialize_rows

PET_COLUMNS = """
    m.id,
    m.refugio_id,
    m.nombre,
    m.tipo,
    m.edad,
    m.sexo,
    m.tamano,
    m.raza,
    m.ciudad,
    m.descripcion,
    m.personalidad,
    m.nivel_energia,
    m.compatible_ninos,
    m.compatible_mascotas,
    m.vacunado,
    m.desparasitado,
    m.esterilizado,
    m.estado,
    m.foto_url,
    r.nombre AS refugio_nombre
"""


def get_user_favorites(usuario_id):
    query = f"""
        SELECT
            f.id AS favorito_id,
            {PET_COLUMNS}
        FROM favoritos f
        INNER JOIN mascotas m ON f.mascota_id = m.id
        LEFT JOIN refugios r ON m.refugio_id = r.id
        WHERE f.usuario_id = %s
        ORDER BY f.id DESC
    """
    with get_cursor() as cursor:
        cursor.execute(query, (usuario_id,))
        return serialize_rows(cursor.fetchall())


def get_user_favorite_ids(usuario_id):
    with get_cursor() as cursor:
        cursor.execute("SELECT mascota_id FROM favoritos WHERE usuario_id = %s", (usuario_id,))
        return [row["mascota_id"] for row in cursor.fetchall()]


def add_favorite(usuario_id, mascota_id):
    with get_cursor(commit=True) as cursor:
        cursor.execute("SELECT id FROM mascotas WHERE id = %s", (mascota_id,))
        if not cursor.fetchone():
            return False, "La mascota no existe"

        cursor.execute(
            """
            INSERT IGNORE INTO favoritos (usuario_id, mascota_id)
            VALUES (%s, %s)
            """,
            (usuario_id, mascota_id),
        )
        return True, "Agregado a favoritos"


def remove_favorite(usuario_id, mascota_id):
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM favoritos WHERE usuario_id = %s AND mascota_id = %s",
            (usuario_id, mascota_id),
        )
        return cursor.rowcount > 0
