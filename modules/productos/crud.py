"""
modules/productos/crud.py  —  DRUD completo de Productos.
"""

from db    import execute
from utils import (log, ok, err, warn, info, prompt,
                   press_enter, separator, print_table, C,
                   validate_str, validate_decimal, validate_int)

TABLE = "productos"
COLS  = [
    ("id",         "ID",        5,  "r"),
    ("nombre",     "Nombre",   22,  "l"),
    ("categoria",  "Categoría",14,  "l"),
    ("precio",     "Precio",    9,  "r"),
    ("stock",      "Stock",     6,  "r"),
    ("activo",     "Activo",    6,  "l"),
]


# ── Display ───────────────────────────────────────────────────
def _fmt(rows):
    for r in rows:
        r["precio"] = f"${float(r['precio']):,.2f}"
        r["activo"] = "Sí" if r["activo"] else "No"
    return rows


# ── Display todos ─────────────────────────────────────────────
def listar():
    separator("PRODUCTOS — LISTAR")
    try:
        rows = execute(f"SELECT id,nombre,categoria,precio,stock,activo FROM {TABLE} ORDER BY id", fetch="all")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not rows: warn("Sin registros.")
    else:
        print_table(_fmt(rows), COLS)
        info(f"Total: {len(rows)}")
        log("READ", f"productos — {len(rows)} registros")
    press_enter()


# ── Buscar ────────────────────────────────────────────────────
def buscar():
    separator("PRODUCTOS — BUSCAR")
    t = prompt("Nombre, categoría o ID:")
    if not t: press_enter(); return
    try:
        rows = execute(
            f"SELECT id,nombre,categoria,precio,stock,activo FROM {TABLE} WHERE id=%s OR nombre LIKE %s OR categoria LIKE %s",
            (t if t.isdigit() else 0, f"%{t}%", f"%{t}%"), fetch="all")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not rows: warn(f"Sin resultados para '{t}'.")
    else: print_table(_fmt(rows), COLS)
    log("READ", f"productos buscar '{t}' — {len(rows)} resultado(s)")
    press_enter()


# ── Crear ─────────────────────────────────────────────────────
def crear():
    separator("PRODUCTOS — CREAR")
    nombre    = prompt("Nombre    :")
    categoria = prompt("Categoría :")
    precio_s  = prompt("Precio    :")
    stock_s   = prompt("Stock     :", "0")

    for ok_v, msg in [validate_str(nombre,"Nombre"), validate_str(categoria,"Categoría"),
                      validate_decimal(precio_s,"Precio",0), validate_int(stock_s,"Stock",0)]:
        if not ok_v: err(msg); press_enter(); return

    _, precio = validate_decimal(precio_s, "Precio")
    _, stock  = validate_int(stock_s, "Stock")

    try:
        new_id = execute(f"INSERT INTO {TABLE} (nombre,categoria,precio,stock) VALUES (%s,%s,%s,%s)",
                         (nombre.strip(), categoria.strip(), precio, stock))
        ok(f"Producto creado — ID {new_id}")
        log("CREATE", f"productos | ID={new_id} | {nombre} | {categoria} | ${precio} | stock={stock}")
    except Exception as e:
        err(str(e))
    press_enter()


# ── Actualizar ────────────────────────────────────────────────
def actualizar():
    separator("PRODUCTOS — ACTUALIZAR")
    id_s = prompt("ID del producto:")
    if not id_s.isdigit(): err("ID inválido."); press_enter(); return
    try:
        row = execute(f"SELECT * FROM {TABLE} WHERE id=%s", (int(id_s),), fetch="one")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not row: err(f"ID {id_s} no encontrado."); press_enter(); return

    print(f"\n  {C.BOLD}Registro actual:{C.RESET}")
    for k,v in row.items(): print(f"    {C.GRAY}{k:<12}{C.RESET} {C.CYAN}{v}{C.RESET}")
    info("Deja en blanco para conservar.\n")

    nombre    = prompt(f"Nombre    [{row['nombre']}]   :") or row["nombre"]
    categoria = prompt(f"Categoría [{row['categoria']}] :") or row["categoria"]
    precio_s  = prompt(f"Precio    [{row['precio']}]   :") or str(row["precio"])
    stock_s   = prompt(f"Stock     [{row['stock']}]    :") or str(row["stock"])

    errs = []
    ok1, r1 = validate_str(nombre,"Nombre"); not ok1 and errs.append(r1)
    ok2, r2 = validate_decimal(precio_s,"Precio"); not ok2 and errs.append(r2)
    ok3, r3 = validate_int(stock_s,"Stock",0); not ok3 and errs.append(r3)
    if errs: [err(e) for e in errs]; press_enter(); return

    _, precio = validate_decimal(precio_s, "Precio")
    _, stock  = validate_int(stock_s, "Stock")

    conf = prompt("¿Confirmar cambios? (s/N):").lower()
    if conf != "s": warn("Cancelado."); press_enter(); return

    try:
        execute(f"UPDATE {TABLE} SET nombre=%s,categoria=%s,precio=%s,stock=%s WHERE id=%s",
                (nombre.strip(), categoria.strip(), precio, stock, int(id_s)))
        ok(f"Producto ID {id_s} actualizado.")
        log("UPDATE", f"productos | ID={id_s} | {row['nombre']}→{nombre} | ${row['precio']}→${precio} | stock:{row['stock']}→{stock}")
    except Exception as e:
        err(str(e))
    press_enter()


# ── Eliminar ──────────────────────────────────────────────────
def eliminar():
    separator("PRODUCTOS — ELIMINAR")
    id_s = prompt("ID del producto:")
    if not id_s.isdigit(): err("ID inválido."); press_enter(); return
    try:
        row = execute(f"SELECT * FROM {TABLE} WHERE id=%s", (int(id_s),), fetch="one")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not row: err(f"ID {id_s} no encontrado."); press_enter(); return

    print(f"\n  {C.RED}Eliminando: ID={row['id']} | {row['nombre']} | ${row['precio']}{C.RESET}")
    conf = prompt("Escribe el NOMBRE para confirmar:").strip()
    if conf != row["nombre"]: warn("Nombre incorrecto. Cancelado."); press_enter(); return

    try:
        execute(f"DELETE FROM {TABLE} WHERE id=%s", (int(id_s),))
        ok(f"'{row['nombre']}' eliminado.")
        log("DELETE", f"productos | ID={id_s} | {row['nombre']}")
    except Exception as e:
        err(str(e))
    press_enter()


# ── Menú ──────────────────────────────────────────────────────
def menu():
    opciones = [("1","Listar",listar),("2","Buscar",buscar),
                ("3","Crear",crear),("4","Actualizar",actualizar),
                ("5","Eliminar",eliminar),("0","Volver",None)]
    while True:
        separator("MENÚ — PRODUCTOS")
        for k,label,_ in opciones:
            print(f"  {C.YELLOW}[{k}]{C.RESET}  {label}")
        op = prompt("\n  Opción:")
        if op == "0": break
        fn = next((f for k,_,f in opciones if k==op and f), None)
        if fn: fn()
        else: warn("Opción inválida.")
