"""
db/init_db.py  —  Crea las 3 tablas si no existen.
Tablas: productos, clientes, ventas
"""

from db.connection import execute
from utils.logger  import log


def init_database():
    # ── Tabla 1: productos ───────────────────────────────────
    execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            nombre      VARCHAR(120)  NOT NULL,
            categoria   VARCHAR(80)   NOT NULL,
            precio      DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
            stock       INT           NOT NULL DEFAULT 0 CHECK (stock >= 0),
            activo      TINYINT(1)    NOT NULL DEFAULT 1,
            creado_en   DATETIME      DEFAULT CURRENT_TIMESTAMP,
            actualizado DATETIME      DEFAULT CURRENT_TIMESTAMP
                                      ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # ── Tabla 2: clientes ────────────────────────────────────
    execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            nombre      VARCHAR(120)  NOT NULL,
            email       VARCHAR(160)  NOT NULL UNIQUE,
            telefono    VARCHAR(20),
            ciudad      VARCHAR(80),
            activo      TINYINT(1)    NOT NULL DEFAULT 1,
            creado_en   DATETIME      DEFAULT CURRENT_TIMESTAMP,
            actualizado DATETIME      DEFAULT CURRENT_TIMESTAMP
                                      ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # ── Tabla 3: ventas ──────────────────────────────────────
    execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id      INT           NOT NULL,
            producto_id     INT           NOT NULL,
            cantidad        INT           NOT NULL DEFAULT 1 CHECK (cantidad > 0),
            precio_unitario DECIMAL(10,2) NOT NULL,
            total           DECIMAL(12,2) GENERATED ALWAYS AS
                                (cantidad * precio_unitario) STORED,
            fecha           DATETIME      DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id)  REFERENCES clientes(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    log("INIT", "3 tablas verificadas/creadas: productos, clientes, ventas.")
