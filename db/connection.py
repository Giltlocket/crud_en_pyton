"""
db/connection.py  —  Pool de conexiones MySQL.

Usa mysql.connector.pooling para mantener N conexiones
abiertas y reutilizarlas sin abrir/cerrar en cada operación.
"""

import mysql.connector
from mysql.connector import pooling, Error as MySQLError
from config import DB_CONFIG
from utils.logger import log

# ── Pool global ─────────────────────────────────────────────
_pool: pooling.MySQLConnectionPool | None = None


def init_pool() -> None:
    """Inicializa el pool. Llamar una vez al arrancar."""
    global _pool
    try:
        _pool = pooling.MySQLConnectionPool(**DB_CONFIG)
        log("POOL", f"Pool '{DB_CONFIG['pool_name']}' iniciado "
                    f"(size={DB_CONFIG['pool_size']}).")
    except MySQLError as e:
        log("POOL_ERROR", str(e), level="error")
        raise ConnectionError(f"No se pudo crear el pool MySQL: {e}")


def get_connection():
    """Obtiene una conexión del pool (se devuelve al hacer .close())."""
    global _pool
    if _pool is None:
        init_pool()
    try:
        return _pool.get_connection()
    except MySQLError as e:
        log("POOL_ERROR", str(e), level="error")
        raise ConnectionError(f"Sin conexiones disponibles en el pool: {e}")


def execute(sql: str, params: tuple = (), fetch: str = None):
    """
    Ejecuta SQL usando una conexión del pool.
    fetch: 'one' | 'all' | None (para INSERT/UPDATE/DELETE → lastrowid)
    La conexión se devuelve al pool automáticamente.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        if fetch == "one":
            return cursor.fetchone()
        elif fetch == "all":
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.lastrowid
    except MySQLError as e:
        try: conn.rollback()
        except Exception: pass
        log("QUERY_ERROR", f"SQL={sql[:80]} | params={params} | err={e}", level="error")
        raise
    finally:
        cursor.close()
        conn.close()   # devuelve al pool, no cierra físicamente
