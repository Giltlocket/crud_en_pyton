"""
modules/truncate.py  —  Truncar tablas con confirmación.
Ofrece un respaldo automático antes de truncar.
"""

from db     import execute
from config import TABLES
from utils  import log, ok, err, warn, info, prompt, press_enter, separator, C


def _truncate_table(table: str):
    """Trunca una tabla deshabilitando FK temporalmente."""
    execute("SET FOREIGN_KEY_CHECKS = 0")
    execute(f"TRUNCATE TABLE {table}")
    execute("SET FOREIGN_KEY_CHECKS = 1")


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
        targets = list(TABLES)
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
            _truncate_table(t)
            ok(f"Tabla '{t}' truncada.")
            log("TRUNCATE", f"Tabla '{t}' truncada correctamente.")
        except Exception as e:
            err(f"Error truncando '{t}': {e}")
            log("TRUNCATE_ERROR", str(e), level="error")

    press_enter()
