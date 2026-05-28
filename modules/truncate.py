"""
modules/truncate.py  —  Truncar tablas con confirmación.
Ofrece un respaldo automático antes de truncar.
"""

from db     import execute
from config import TABLES
from utils  import log, ok, err, warn, info, prompt, press_enter, separator, C


def _tabla_tiene_dependencias(table: str) -> bool:
    """Indica si una tabla padre tiene registros relacionados en ventas."""
    if table == "clientes":
        row = execute("SELECT COUNT(*) AS n FROM ventas v JOIN clientes c ON c.id = v.cliente_id", fetch="one")
        return bool(row and row["n"] > 0)

    if table == "productos":
        row = execute("SELECT COUNT(*) AS n FROM ventas v JOIN productos p ON p.id = v.producto_id", fetch="one")
        return bool(row and row["n"] > 0)

    return False


def _vaciar_table(table: str):
    """
    Vacía una tabla sin usar TRUNCATE.

    DELETE evita el error 1701 de MySQL/MariaDB cuando una tabla está
    referenciada por una foreign key.
    """
    if _tabla_tiene_dependencias(table):
        raise RuntimeError(
            f"No se puede vaciar '{table}' porque tiene ventas relacionadas. "
            "Primero vacía ventas o usa la opción de vaciar todas las tablas."
        )

    execute(f"DELETE FROM {table}")
    execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")


def run():
    separator("TRUNCAR TABLA")

    print(f"  {C.BOLD}Tablas disponibles:{C.RESET}")
    for i, t in enumerate(TABLES, 1):
        try:
            count = execute(f"SELECT COUNT(*) AS n FROM {t}", fetch="one")["n"]
        except Exception:
            count = "?"
        print(f"  {C.YELLOW}[{i}]{C.RESET}  {t:<20} {C.GRAY}({count} registros){C.RESET}")
    print(f"  {C.YELLOW}[A]{C.RESET}  Truncar TODAS las tablas")
    print(f"  {C.YELLOW}[0]{C.RESET}  Cancelar")

    op = prompt("\n  Selección:").upper()

    if op == "0":
        warn("Cancelado."); press_enter(); return

    targets = []
    if op == "A":
        targets = ["ventas", "productos", "clientes"]
    elif op.isdigit() and 1 <= int(op) <= len(TABLES):
        targets = [TABLES[int(op) - 1]]
    else:
        err("Opción inválida."); press_enter(); return

    # ── Oferta de respaldo ────────────────────────────────────
    print(f"\n  {C.RED}{C.BOLD}⚠  TRUNCAR eliminará TODOS los registros de: {', '.join(targets)}{C.RESET}")
    hacer_bk = prompt("  ¿Hacer respaldo JSON antes de truncar? (S/n):").lower()
    if hacer_bk != "n":
        from modules.backup import exportar_tabla
        for t in targets:
            exportar_tabla(t, tag="pre_truncate")

    # ── Confirmación final ────────────────────────────────────
    conf = prompt(f"\n  Escribe {C.RED}TRUNCAR{C.RESET} para confirmar:")
    if conf != "TRUNCAR":
        warn("Texto incorrecto. Operación cancelada.")
        log("TRUNCATE", f"Cancelado por el usuario (tablas: {targets})")
        press_enter(); return

    for t in targets:
        try:
            _vaciar_table(t)
            ok(f"Tabla '{t}' truncada.")
            log("TRUNCATE", f"Tabla '{t}' truncada correctamente.")
        except Exception as e:
            err(f"Error truncando '{t}': {e}")
            log("TRUNCATE_ERROR", str(e), level="error")

    press_enter()
