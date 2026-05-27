"""
modules/history.py  —  Visor del historial de acciones (app.log).
"""

from config import LOG_FILE
from utils  import log, warn, info, prompt, press_enter, separator, C

_COLORS = {
    "CREATE":   C.GREEN,
    "UPDATE":   C.YELLOW,
    "DELETE":   C.RED,
    "BACKUP":   C.CYAN,
    "ROLLBACK": C.MAGENTA,
    "TRUNCATE": C.RED,
    "INIT":     C.BLUE,
    "POOL":     C.GRAY,
    "DB":       C.GRAY,
    "SYSTEM":   C.GRAY,
}


def run():
    separator("HISTORIAL DE ACCIONES")

    if not LOG_FILE.exists():
        warn("No se encontró el archivo de log."); press_enter(); return

    lineas = LOG_FILE.read_text(encoding="utf-8").splitlines()
    if not lineas:
        warn("El historial está vacío."); press_enter(); return

    print(f"  Total entradas: {C.CYAN}{len(lineas)}{C.RESET}\n")
    print(f"  Filtros: {C.YELLOW}CREATE  READ  UPDATE  DELETE  BACKUP  ROLLBACK  TRUNCATE{C.RESET}")
    filtro = prompt("  Filtrar por acción [vacío=todos]:").upper().strip()
    n_s    = prompt("  Últimas N entradas [50]:", "50")

    try: n = int(n_s)
    except ValueError: n = 50

    resultado = [l for l in lineas if (filtro in l if filtro else True)][-n:]

    if not resultado:
        warn(f"Sin entradas para el filtro '{filtro}'."); press_enter(); return

    print()
    for linea in resultado:
        color = next((c for act, c in _COLORS.items() if f"[{act}]" in linea), C.GRAY)
        print(f"  {color}{linea}{C.RESET}")

    separator()
    info(f"Mostrando {len(resultado)} de {len(lineas)} entradas.")
    log("READ", f"Historial consultado — últimas {n} (filtro: {filtro or 'ninguno'})")
    press_enter()
