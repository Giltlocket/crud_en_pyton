"""
utils/display.py  —  Presentación: colores, tablas, prompts.
"""

import os


class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner(app_name: str, version: str):
    w = 56
    print(f"\n{C.CYAN}{C.BOLD}╔{'═'*w}╗")
    print(f"║{app_name.center(w)}║")
    print(f"║{'Pool MySQL · 3 Tablas · Log · Backup · Rollback'.center(w)}║")
    print(f"║{('v' + version).center(w)}║")
    print(f"╚{'═'*w}╝{C.RESET}\n")


def separator(title: str = ""):
    width = 56
    if title:
        pad = max((width - len(title) - 2) // 2, 1)
        print(f"\n{C.GRAY}{'─'*pad} {C.YELLOW}{title}{C.GRAY} {'─'*pad}{C.RESET}\n")
    else:
        print(f"  {C.GRAY}{'─'*width}{C.RESET}")


def ok(msg):    print(f"  {C.GREEN}✔  {msg}{C.RESET}")
def err(msg):   print(f"  {C.RED}✘  {msg}{C.RESET}")
def info(msg):  print(f"  {C.CYAN}ℹ  {msg}{C.RESET}")
def warn(msg):  print(f"  {C.YELLOW}⚠  {msg}{C.RESET}")


def press_enter():
    input(f"\n{C.GRAY}  Presiona Enter para continuar...{C.RESET}")


def prompt(msg: str, default: str = "") -> str:
    val = input(f"  {C.WHITE}{msg}{C.RESET} ").strip()
    return val if val else default


def print_table(rows: list[dict], columns: list[tuple]):
    """
    columns = [(key, header, width, align), ...]
    align: 'l' | 'r'
    """
    _HIGHLIGHT = {"id": C.CYAN, "total": C.GREEN, "precio": C.GREEN,
                  "precio_unitario": C.GREEN, "stock": C.YELLOW}
    # cabecera
    header = "  "
    for _, head, width, align in columns:
        fmt = f"{C.BOLD}{head:<{width}}{C.RESET}  " if align == "l" \
         else f"{C.BOLD}{head:>{width}}{C.RESET}  "
        header += fmt
    print(header)
    separator()
    # filas
    for row in rows:
        line = "  "
        for key, _, width, align in columns:
            val   = str(row.get(key, ""))
            color = _HIGHLIGHT.get(key, C.WHITE)
            line += f"{color}{val:<{width}}{C.RESET}  " if align == "l" \
               else f"{color}{val:>{width}}{C.RESET}  "
        print(line)
    separator()
