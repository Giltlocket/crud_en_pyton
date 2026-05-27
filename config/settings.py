"""
config/settings.py  —  Configuración central.
Edita DB_CONFIG con tus credenciales MySQL.
"""

from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
LOG_DIR    = BASE_DIR / "logs"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

# ── MySQL Pool ──────────────────────────────────────────────
DB_CONFIG = {
    "host":             "localhost",
    "port":             3306,
    "user":             "root",
    "password":         "tu_password",
    "database":         "crud_drud",
    "charset":          "utf8mb4",
    "pool_name":        "crud_pool",
    "pool_size":        5,          # conexiones simultáneas en el pool
    "pool_reset_session": True,
}

# ── Archivos ────────────────────────────────────────────────
LOG_FILE = LOG_DIR / "app.log"

# ── Tablas gestionadas ──────────────────────────────────────
TABLES = ["productos", "clientes", "ventas"]

# ── App ─────────────────────────────────────────────────────
APP_NAME    = "DRUD Manager Pro"
APP_VERSION = "2.0.0"
