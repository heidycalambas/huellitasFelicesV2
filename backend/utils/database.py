
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config


def get_connection():
    """
    Establece una conexión con PostgreSQL de Supabase.
    """
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        dbname=Config.DB_NAME,
        sslmode=Config.DB_SSLMODE,
        cursor_factory=RealDictCursor,
        connect_timeout=10,
    )


@contextmanager
def get_cursor(commit: bool = False):
    """
    Abre una conexión y un cursor para ejecutar consultas.

    Si commit=True, confirma los cambios realizados.
    Si ocurre un error, revierte la transacción.
    """
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            yield cursor

        if commit:
            conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def serialize_value(value):
    """
    Convierte valores de PostgreSQL a formatos compatibles con JSON.
    """

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, time):
        return value.strftime("%H:%M:%S")

    if isinstance(value, timedelta):
        total = int(value.total_seconds())
        hours, rem = divmod(total, 3600)
        minutes, seconds = divmod(rem, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, memoryview):
        return value.tobytes().decode("utf-8", errors="ignore")

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")

    return value


def serialize_row(row):
    """
    Convierte una fila de PostgreSQL en un diccionario serializable.
    """
    if row is None:
        return None

    return {
        key: serialize_value(value)
        for key, value in row.items()
    }


def serialize_rows(rows):
    """
    Convierte varias filas de PostgreSQL en una lista de diccionarios.
    """
    return [serialize_row(row) for row in rows]
