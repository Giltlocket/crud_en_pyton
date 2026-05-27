#!/usr/bin/env python3
"""
main.py  —  DRUD Manager Pro.
Ejecuta: python main.py
"""

import sys
from db      import init_pool, init_database
from modules import (menu_productos, menu_clientes, menu_ventas,
                     history, backup, truncate)
from utils   import clear, banner, separator, ok, warn, err, prompt, log, C
from config  import APP_NAME, APP_VERSION


def menu_principal():
    secciones = [
        ("─", "── TABLAS ──────────────────────────", None),
        ("1",  "Productos",                           menu_productos),
        ("2",  "Clientes",                            menu_clientes),
        ("3",  "Ventas",                              menu_ventas),
        ("─", "── HERRAMIENTAS ────────────────────", None),
        ("4",  "Historial de acciones",               history.run),
        ("5",  "Respaldos & Rollback",                backup.menu),
        ("6",  "Truncar tabla",                       truncate.run),
        ("─", "────────────────────────────────────", None),
        ("0",  "Salir",                               None),
    ]

    while True:
        clear()
        banner(APP_NAME, APP_VERSION)
        separator("MENÚ PRINCIPAL")
        for k, label, _ in secciones:
            if k == "─":
                print(f"  {C.GRAY}  {label}{C.RESET}")
            else:
                print(f"  {C.YELLOW}[{k}]{C.RESET}  {label}")

        op = prompt("\n  Opción:")

        if op == "0":
            log("SYSTEM", "Aplicación cerrada.")
            print(f"\n  {C.CYAN}¡Hasta luego!{C.RESET}\n")
            break

        fn = next((f for k, _, f in secciones if k == op and f), None)
        if fn:
            fn()
        else:
            warn("Opción no válida.")


if __name__ == "__main__":
    try:
        init_pool()
        init_database()
        log("SYSTEM", f"{APP_NAME} v{APP_VERSION} iniciado.")
        menu_principal()
    except ConnectionError as e:
        err(str(e))
        print(f"\n  {C.GRAY}→ Verifica tus credenciales en config/settings.py{C.RESET}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}Interrumpido por teclado.{C.RESET}\n")
        log("SYSTEM", "Interrumpido por teclado.")
