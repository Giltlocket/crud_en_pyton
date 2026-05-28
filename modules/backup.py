"""
modules/backup.py  —  Respaldo JSON por tabla y restauración (rollback).
"""

import json
import datetime
from decimal import Decimal

from db     import execute
from config import TABLES, BACKUP_DIR
from utils  import (log, ok, err, warn, info,
                    prompt, press_enter, separator, C)


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def _json_safe_value(value):
    """Convierte valores de MySQL/Python a tipos compatibles con JSON."""
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()

    return value


def _rows_to_json(table: str) -> list[dict]:
    rows = execute(f"SELECT * FROM {table} ORDER BY id", fetch="all")
    clean = []
    for r in rows:
        row = {}
        for k, v in r.items():
            row[k] = _json_safe_value(v)
        clean.append(row)
    return clean


def _save_file(table: str, rows: list, tag: str = "") -> tuple[bool, str]:
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{table}_{ts}{'_' + tag if tag else ''}.json"
    path = BACKUP_DIR / name
    payload = {
        "tabla":       table,
        "generado_en": datetime.datetime.now().isoformat(),
        "total":       len(rows),
        "tag":         tag,
        "registros":   rows,
    }
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True, str(path)
    except Exception as e:
        return False, str(e)


def _list_files(table: str = "") -> list:
    pattern = f"{table}_*.json" if table else "*.json"
    return sorted(BACKUP_DIR.glob(pattern), reverse=True)


def _tabla_tiene_dependencias(table: str) -> bool:
    """Indica si la tabla padre tiene registros usados en ventas."""
    if table == "clientes":
        row = execute("SELECT COUNT(*) AS n FROM ventas v JOIN clientes c ON c.id = v.cliente_id", fetch="one")
        return bool(row and row["n"] > 0)

    if table == "productos":
        row = execute("SELECT COUNT(*) AS n FROM ventas v JOIN productos p ON p.id = v.producto_id", fetch="one")
        return bool(row and row["n"] > 0)

    return False


def _vaciar_tabla_seguro(table: str) -> None:
    """
    Vacía una tabla sin usar TRUNCATE.

    TRUNCATE falla en tablas referenciadas por foreign keys aunque no tengan registros.
    DELETE respeta las relaciones y permite limpiar clientes/productos cuando no hay ventas asociadas.
    """
    if _tabla_tiene_dependencias(table):
        raise RuntimeError(
            f"No se puede reemplazar '{table}' porque hay ventas relacionadas. "
            "Primero respalda/restaura ventas o elimina esas ventas."
        )

    execute(f"DELETE FROM {table}")
    execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")


# ─────────────────────────────────────────────────────────────
#  EXPORTAR (una tabla o todas)
# ─────────────────────────────────────────────────────────────

def exportar_tabla(table: str, tag: str = "") -> bool:
    """Exporta una tabla específica. Retorna True si tuvo éxito."""
    try:
        rows = _rows_to_json(table)
        s_ok, path = _save_file(table, rows, tag=tag)
        if s_ok:
            log("BACKUP", f"Exportación OK — {table} | {len(rows)} reg. → {path} (tag={tag or '—'})")
            return True
        else:
            log("BACKUP_ERROR", path, level="error")
            return False
    except Exception as e:
        log("BACKUP_ERROR", str(e), level="error")
        return False


def exportar():
    separator("EXPORTAR RESPALDO")

    print(f"  {C.BOLD}¿Qué tabla exportar?{C.RESET}")
    for i, t in enumerate(TABLES, 1):
        print(f"  {C.YELLOW}[{i}]{C.RESET}  {t}")
    print(f"  {C.YELLOW}[A]{C.RESET}  Todas")
    print(f"  {C.YELLOW}[0]{C.RESET}  Cancelar")

    op  = prompt("\n  Selección:").upper()
    tag = prompt("  Etiqueta opcional (p.ej. 'v1') [vacío=sin etiqueta]:")

    targets = []
    if op == "0":
        warn("Cancelado."); press_enter(); return
    elif op == "A":
        targets = list(TABLES)
    elif op.isdigit() and 1 <= int(op) <= len(TABLES):
        targets = [TABLES[int(op) - 1]]
    else:
        err("Opción inválida."); press_enter(); return

    for t in targets:
        success = exportar_tabla(t, tag=tag)
        if success: ok(f"'{t}' exportada correctamente.")
        else:       err(f"Error al exportar '{t}'.")

    press_enter()


# ─────────────────────────────────────────────────────────────
#  VER RESPALDOS
# ─────────────────────────────────────────────────────────────

def listar_respaldos():
    separator("RESPALDOS DISPONIBLES")

    print(f"  Filtrar por tabla:")
    for i, t in enumerate(TABLES, 1):
        print(f"  {C.YELLOW}[{i}]{C.RESET}  {t}")
    print(f"  {C.YELLOW}[A]{C.RESET}  Todos")

    op = prompt("\n  Selección:", "A").upper()
    if op.isdigit() and 1 <= int(op) <= len(TABLES):
        filtro_tabla = TABLES[int(op) - 1]
    else:
        filtro_tabla = ""

    archivos = _list_files(filtro_tabla)
    if not archivos:
        warn("No hay respaldos disponibles."); press_enter(); return

    print(f"\n  {'#':<4} {'Archivo':<45} {'Reg':>5}  {'Generado':<19}  {'Tag'}")
    print(f"  {C.GRAY}{'─'*85}{C.RESET}")
    for i, f in enumerate(archivos, 1):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            total = d.get("total", "?")
            gen   = d.get("generado_en", "")[:19]
            tag   = d.get("tag") or "—"
        except Exception:
            total, gen, tag = "?", "?", "?"
        print(f"  {C.YELLOW}{i:<4}{C.RESET}{f.name:<45} "
              f"{C.GREEN}{total:>5}{C.RESET}  {C.GRAY}{gen:<19}{C.RESET}  {C.CYAN}{tag}{C.RESET}")

    info(f"Total: {len(archivos)} archivo(s).")
    press_enter()


# ─────────────────────────────────────────────────────────────
#  ROLLBACK (RESTAURAR)
# ─────────────────────────────────────────────────────────────

def rollback():
    separator("ROLLBACK — RESTAURAR RESPALDO")

    archivos = _list_files()
    if not archivos:
        warn("No hay respaldos para restaurar."); press_enter(); return

    print(f"  {'#':<4} {'Archivo':<45} {'Reg':>5}  {'Generado':<19}")
    print(f"  {C.GRAY}{'─'*75}{C.RESET}")
    for i, f in enumerate(archivos, 1):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            total = d.get("total", "?")
            gen   = d.get("generado_en", "")[:19]
            tag   = d.get("tag") or ""
        except Exception:
            total, gen, tag = "?", "?", ""
        print(f"  {C.YELLOW}{i:<4}{C.RESET}{f.name:<45} "
              f"{C.GREEN}{total:>5}{C.RESET}  {C.GRAY}{gen:<19}{C.RESET}  {C.CYAN}{tag}{C.RESET}")

    idx_s = prompt("\n  Número de respaldo a restaurar [0=cancelar]:", "0")
    if not idx_s.isdigit() or int(idx_s) == 0:
        warn("Cancelado."); press_enter(); return
    idx = int(idx_s)
    if not (1 <= idx <= len(archivos)):
        err("Fuera de rango."); press_enter(); return

    chosen = archivos[idx - 1]
    try:
        payload   = json.loads(chosen.read_text(encoding="utf-8"))
        registros = payload.get("registros", [])
        table     = payload.get("tabla", "")
    except Exception as e:
        err(f"Error al leer el respaldo: {e}"); press_enter(); return

    if table not in TABLES:
        err(f"Tabla '{table}' no reconocida."); press_enter(); return

    print(f"\n  {C.YELLOW}Restaurar {len(registros)} registros en '{table}' desde:{C.RESET}")
    print(f"  {C.CYAN}{chosen.name}{C.RESET}")

    # ── Backup previo ─────────────────────────────────────────
    hacer_bk = prompt("\n  ¿Respaldar estado actual antes de restaurar? (S/n):").lower()
    if hacer_bk != "n":
        exportar_tabla(table, tag="pre_rollback")
        ok("Respaldo de seguridad creado.")

    # ── Modo ──────────────────────────────────────────────────
    print(f"\n  {C.YELLOW}[r]{C.RESET} Reemplazar todo  {C.GRAY}(truncar + reimportar){C.RESET}")
    print(f"  {C.YELLOW}[a]{C.RESET} Agregar          {C.GRAY}(no borra lo existente){C.RESET}")
    modo = prompt("\n  Modo [r/a]:", "r").lower()
    if modo not in ("r", "a"): modo = "r"

    # ── Confirmación ──────────────────────────────────────────
    conf = prompt(f"\n  Escribe '{table}' para confirmar rollback:")
    if conf != table:
        warn("Nombre incorrecto. Cancelado.")
        log("ROLLBACK", f"Cancelado — tabla={table}")
        press_enter(); return

    # ── Ejecutar ──────────────────────────────────────────────
    try:
        if modo == "r":
            _vaciar_tabla_seguro(table)

        insertados = 0
        for rec in registros:
            # Excluir solo campos generados por la BD.
            # Conservamos el id para que ventas.cliente_id y ventas.producto_id sigan apuntando bien.
            skip = {"total"}
            cols = [k for k in rec if k not in skip]
            vals = [rec[k] for k in cols]
            ph   = ", ".join(["%s"] * len(cols))
            sql  = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({ph})"
            try:
                execute(sql, tuple(vals))
                insertados += 1
            except Exception as e:
                warn(f"Registro omitido: {e}")

        ok(f"Rollback completado — {insertados}/{len(registros)} registros en '{table}'.")
        log("ROLLBACK",
            f"tabla={table} | archivo={chosen.name} | modo={modo} | restaurados={insertados}/{len(registros)}")
    except Exception as e:
        err(f"Error durante el rollback: {e}")
        log("ROLLBACK_ERROR", str(e), level="error")

    press_enter()


# ─────────────────────────────────────────────────────────────
#  MENÚ
# ─────────────────────────────────────────────────────────────

def menu():
    from utils import clear, banner
    from config import APP_NAME, APP_VERSION

    while True:
        clear(); banner(APP_NAME, APP_VERSION)
        separator("RESPALDOS & ROLLBACK")
        opciones = [
            ("1", "Exportar tabla(s) → JSON",  exportar),
            ("2", "Ver respaldos disponibles", listar_respaldos),
            ("3", "Rollback — restaurar",       rollback),
            ("0", "Volver al menú principal",   None),
        ]
        for k, label, _ in opciones:
            print(f"  {C.YELLOW}[{k}]{C.RESET}  {label}")
        op = prompt("\n  Opción:")
        if op == "0": break
        fn = next((f for k, _, f in opciones if k == op and f), None)
        if fn: fn()
        else: warn("Opción inválida.")
