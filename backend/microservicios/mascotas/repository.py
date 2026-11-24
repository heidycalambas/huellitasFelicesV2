from utils.database import get_cursor, serialize_row, serialize_rows

PET_COLUMNS = """
    id,
    refugio_id,
    nombre,
    tipo,
    edad,
    sexo,
    tamano,
    raza,
    ciudad,
    descripcion,
    personalidad,
    nivel_energia,
    compatible_ninos,
    compatible_mascotas,
    vacunado,
    desparasitado,
    esterilizado,
    estado,
    foto_url
"""


def get_all_pets(
    pet_type=None,
    city=None,
    status=None,
    sex=None,
    size=None,
    breed=None,
    min_age=None,
    max_age=None,
    refugio_id=None,
    search=None,
):
    """Consulta todas las mascotas registradas con filtros opcionales."""
    query = f"SELECT {PET_COLUMNS} FROM mascotas WHERE 1=1"
    params = []

    if pet_type and pet_type.lower() != "todos":
        query += " AND LOWER(tipo) = LOWER(%s)"
        params.append(pet_type)
    if city and city.lower() != "todas":
        query += " AND LOWER(ciudad) LIKE LOWER(%s)"
        params.append(f"%{city}%")
    if status and status.lower() != "todos":
        query += " AND LOWER(estado) = LOWER(%s)"
        params.append(status)
    if sex and sex.lower() != "todos":
        query += " AND LOWER(sexo) = LOWER(%s)"
        params.append(sex)
    if size and size.lower() != "todos":
        query += " AND LOWER(tamano) = LOWER(%s)"
        params.append(size)
    if breed and breed.strip():
        query += " AND LOWER(raza) LIKE LOWER(%s)"
        params.append(f"%{breed.strip()}%")
    if min_age is not None:
        query += " AND edad >= %s"
        params.append(min_age)
    if max_age is not None:
        query += " AND edad <= %s"
        params.append(max_age)
    if refugio_id:
        query += " AND refugio_id = %s"
        params.append(refugio_id)
    if search and search.strip():
        query += " AND (LOWER(nombre) LIKE LOWER(%s) OR LOWER(raza) LIKE LOWER(%s) OR LOWER(descripcion) LIKE LOWER(%s))"
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    query += " ORDER BY id DESC"

    with get_cursor() as cursor:
        cursor.execute(query, tuple(params))
        return serialize_rows(cursor.fetchall())


def create_pet(data):
    """Registra una nueva mascota en la base de datos."""
    nombre = (data.get("nombre") or "").strip()
    tipo = (data.get("tipo") or "").strip()
    edad = data.get("edad")

    if not nombre or not tipo or edad is None:
        raise ValueError("Los campos nombre, tipo y edad son obligatorios")

    refugio_id = data.get("refugio_id")
    if refugio_id:
        with get_cursor() as cursor:
            cursor.execute("SELECT id FROM refugios WHERE id = %s", (refugio_id,))
            if not cursor.fetchone():
                refugio_id = 1
    else:
        refugio_id = 1

    sexo = data.get("sexo", "Macho")
    tamano = data.get("tamano", "Mediano")
    raza = data.get("raza", "Criollo")
    ciudad = data.get("ciudad", "Popayan")
    descripcion = data.get("descripcion", "")
    personalidad = data.get("personalidad", "Amigable")
    nivel_energia = data.get("nivel_energia", "Media")
    compatible_ninos = bool(data.get("compatible_ninos", False))
    compatible_mascotas = bool(data.get("compatible_mascotas", False))
    vacunado = bool(data.get("vacunado", False))
    desparasitado = bool(data.get("desparasitado", False))
    esterilizado = bool(data.get("esterilizado", False))
    estado = data.get("estado", "Disponible")
    foto_url = data.get("foto_url") or None

    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO mascotas (
                refugio_id, nombre, tipo, edad, sexo, tamano, raza, ciudad,
                descripcion, personalidad, nivel_energia, compatible_ninos,
                compatible_mascotas, vacunado, desparasitado, esterilizado, estado,
                foto_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (
                refugio_id,
                nombre,
                tipo,
                int(edad),
                sexo,
                tamano,
                raza,
                ciudad,
                descripcion,
                personalidad,
                nivel_energia,
                int(compatible_ninos),
                int(compatible_mascotas),
                int(vacunado),
                int(desparasitado),
                int(esterilizado),
                estado,
                foto_url,
            ),
        )
        nuevo_id = cursor.fetchone()["id"]
        return nuevo_id


def update_pet(pet_id, data):
    """Actualiza la información de una mascota existente."""
    fields = []
    params = []

    updatable = [
        "nombre", "tipo", "edad", "sexo", "tamano", "raza", "ciudad",
        "descripcion", "personalidad", "nivel_energia", "compatible_ninos",
        "compatible_mascotas", "vacunado", "desparasitado", "esterilizado",
        "estado", "foto_url", "refugio_id"
    ]

    for key in updatable:
        if key in data:
            val = data[key]
            if key in ["compatible_ninos", "compatible_mascotas", "vacunado", "desparasitado", "esterilizado"]:
                val = 1 if bool(val) else 0
            elif key == "edad" and val is not None:
                val = int(val)
            fields.append(f"{key} = %s")
            params.append(val)

    if not fields:
        return False

    params.append(pet_id)
    query = f"UPDATE mascotas SET {', '.join(fields)} WHERE id = %s"

    with get_cursor(commit=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.rowcount > 0


def update_pet_status(pet_id, new_status):
    with get_cursor(commit=True) as cursor:
        cursor.execute("UPDATE mascotas SET estado = %s WHERE id = %s", (new_status, pet_id))
        return cursor.rowcount > 0


def delete_pet(pet_id):
    with get_cursor(commit=True) as cursor:
        # Eliminar historial y favoritos primero para evitar violación de FK
        cursor.execute("DELETE FROM favoritos WHERE mascota_id = %s", (pet_id,))
        cursor.execute("DELETE FROM historial_veterinario WHERE mascota_id = %s", (pet_id,))
        cursor.execute("DELETE FROM mascotas WHERE id = %s", (pet_id,))
        return cursor.rowcount > 0


def search_available_by_city(city):
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {PET_COLUMNS}
            FROM mascotas
            WHERE ciudad = %s
              AND estado = 'Disponible'
            ORDER BY nombre ASC
            """,
            (city,),
        )
        return serialize_rows(cursor.fetchall())


def filter_by_type_and_age(pet_type, min_age, max_age):
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {PET_COLUMNS}
            FROM mascotas
            WHERE tipo = %s
              AND edad BETWEEN %s AND %s
              AND estado = 'Disponible'
            ORDER BY edad ASC
            """,
            (pet_type, min_age, max_age),
        )
        return serialize_rows(cursor.fetchall())


def find_compatible_pets(has_children, has_other_pets, preferred_size):
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {PET_COLUMNS}
            FROM mascotas
            WHERE estado = 'Disponible'
              AND tamano = %s
              AND (%s = 0 OR compatible_ninos = 1)
              AND (%s = 0 OR compatible_mascotas = 1)
            ORDER BY nombre ASC
            """,
            (
                preferred_size,
                int(has_children),
                int(has_other_pets),
            ),
        )
        return serialize_rows(cursor.fetchall())


def recommend_pets(
    preferred_type,
    preferred_size,
    min_age,
    max_age,
    accepts_children,
    accepts_other_pets,
):
    with get_cursor() as cursor:
        query = f"""
            SELECT {PET_COLUMNS}
            FROM mascotas
            WHERE estado = 'Disponible'
        """
        params = []
        if preferred_type and preferred_type.lower() not in ("todos", "ambos"):
            query += " AND LOWER(tipo) = LOWER(%s)"
            params.append(preferred_type)
        if preferred_size and preferred_size.lower() not in ("todos", "cualquiera"):
            query += " AND LOWER(tamano) = LOWER(%s)"
            params.append(preferred_size)
        if min_age is not None and max_age is not None:
            query += " AND edad BETWEEN %s AND %s"
            params.extend([int(min_age), int(max_age)])
        if accepts_children:
            query += " AND compatible_ninos = 1"
        if accepts_other_pets:
            query += " AND compatible_mascotas = 1"

        query += " ORDER BY id DESC LIMIT 6"
        cursor.execute(query, tuple(params))
        res = cursor.fetchall()
        if not res:
            # Fallback a mascotas disponibles generales si no hay coincidencias estrictas
            cursor.execute(f"SELECT {PET_COLUMNS} FROM mascotas WHERE estado = 'Disponible' ORDER BY id DESC LIMIT 6")
            res = cursor.fetchall()
        return serialize_rows(res)


def get_pet_statistics():
    with get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM mascotas")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE estado = 'Disponible'")
        available = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE estado = 'Adoptada'")
        adopted = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE tipo = 'Perro'")
        dogs = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE tipo = 'Gato'")
        cats = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT tipo, COUNT(*) AS cantidad
            FROM mascotas
            GROUP BY tipo
            ORDER BY tipo
        """)
        by_type = serialize_rows(cursor.fetchall())

        cursor.execute("""
            SELECT estado, COUNT(*) AS cantidad
            FROM mascotas
            GROUP BY estado
            ORDER BY estado
        """)
        by_status = serialize_rows(cursor.fetchall())

        cursor.execute("""
            SELECT ciudad, COUNT(*) AS cantidad
            FROM mascotas
            GROUP BY ciudad
            ORDER BY cantidad DESC
        """)
        by_city = serialize_rows(cursor.fetchall())

        return {
            "total": total,
            "disponibles": available,
            "adoptadas": adopted,
            "perros": dogs,
            "gatos": cats,
            "por_tipo": by_type,
            "por_estado": by_status,
            "por_ciudad": by_city,
        }


def get_pet_profile(pet_id):
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                m.id,
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
                r.id AS refugio_id,
                r.nombre AS refugio_nombre,
                r.ciudad AS refugio_ciudad,
                r.direccion AS refugio_direccion,
                r.telefono AS refugio_telefono,
                r.email AS refugio_email
            FROM mascotas m
            LEFT JOIN refugios r ON m.refugio_id = r.id
            WHERE m.id = %s
            """,
            (pet_id,),
        )
        row = cursor.fetchone()

        if not row:
            return None

        data = serialize_row(row)

        # Consultar historial veterinario ordenado cronológicamente
        cursor.execute(
            """
            SELECT id, tipo, descripcion, fecha, proxima_fecha, veterinario, observaciones
            FROM historial_veterinario
            WHERE mascota_id = %s
            ORDER BY fecha DESC, id DESC
            """,
            (pet_id,),
        )
        history = serialize_rows(cursor.fetchall())

    return {
        "mascota": {
            "id": data["id"],
            "nombre": data["nombre"],
            "tipo": data["tipo"],
            "edad": data["edad"],
            "sexo": data["sexo"],
            "tamano": data["tamano"],
            "raza": data["raza"],
            "ciudad": data["ciudad"],
            "descripcion": data["descripcion"],
            "personalidad": data["personalidad"],
            "nivel_energia": data["nivel_energia"],
            "compatible_ninos": data["compatible_ninos"],
            "compatible_mascotas": data["compatible_mascotas"],
            "vacunado": data["vacunado"],
            "desparasitado": data["desparasitado"],
            "esterilizado": data["esterilizado"],
            "estado": data["estado"],
            "foto_url": data.get("foto_url"),
            "refugio_id": data["refugio_id"],
        },
        "refugio": {
            "id": data["refugio_id"],
            "nombre": data["refugio_nombre"],
            "ciudad": data["refugio_ciudad"],
            "direccion": data["refugio_direccion"],
            "telefono": data["refugio_telefono"],
            "email": data["refugio_email"],
        },
        "historial": history,
    }
