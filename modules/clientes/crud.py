"""
modules/clientes/crud.py  —  DRUD completo de Clientes.
"""

from db    import execute
from utils import (log, ok, err, warn, info, prompt,
                   press_enter, separator, print_table, C,
                   validate_str, validate_email, validate_phone)

TABLE = "clientes"
COLS  = [
    ("id",       "ID",      5,  "r"),
    ("nombre",   "Nombre", 22,  "l"),
    ("email",    "Email",  28,  "l"),
    ("telefono", "Tel.",   14,  "l"),
    ("ciudad",   "Ciudad", 14,  "l"),
    ("activo",   "Activo",  6,  "l"),
]


def _fmt(rows):
    for r in rows:
        r["activo"] = "Sí" if r["activo"] else "No"
    return rows


def listar():
    separator("CLIENTES — LISTAR")
    try:
        rows = execute(f"SELECT id,nombre,email,telefono,ciudad,activo FROM {TABLE} ORDER BY id", fetch="all")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not rows: warn("Sin registros.")
    else:
        print_table(_fmt(rows), COLS)
        info(f"Total: {len(rows)}")
        log("READ", f"clientes — {len(rows)} registros")
    press_enter()


def buscar():
    separator("CLIENTES — BUSCAR")
    t = prompt("Nombre, email, ciudad o ID:")
    if not t: press_enter(); return
    try:
        rows = execute(
            f"SELECT id,nombre,email,telefono,ciudad,activo FROM {TABLE} "
            f"WHERE id=%s OR nombre LIKE %s OR email LIKE %s OR ciudad LIKE %s",
            (t if t.isdigit() else 0, f"%{t}%", f"%{t}%", f"%{t}%"), fetch="all")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not rows: warn(f"Sin resultados para '{t}'.")
    else: print_table(_fmt(rows), COLS)
    log("READ", f"clientes buscar '{t}' — {len(rows)} resultado(s)")
    press_enter()


def crear():
    separator("CLIENTES — CREAR")
    nombre   = prompt("Nombre   :")
    email    = prompt("Email    :")
    telefono = prompt("Teléfono (opcional) :", "")
    ciudad   = prompt("Ciudad   (opcional) :", "")

    errors = []
    ok1, m1 = validate_str(nombre, "Nombre"); not ok1 and errors.append(m1)
    ok2, m2 = validate_email(email);          not ok2 and errors.append(m2)
    if telefono:
        ok3, m3 = validate_phone(telefono);   not ok3 and errors.append(m3)
    if errors: [err(e) for e in errors]; press_enter(); return

    try:
        new_id = execute(
            f"INSERT INTO {TABLE} (nombre,email,telefono,ciudad) VALUES (%s,%s,%s,%s)",
            (nombre.strip(), email.strip().lower(),
             telefono.strip() or None, ciudad.strip() or None))
        ok(f"Cliente creado — ID {new_id}")
        log("CREATE", f"clientes | ID={new_id} | {nombre} | {email}")
    except Exception as e:
        err(str(e))
    press_enter()


def actualizar():
    separator("CLIENTES — ACTUALIZAR")
    id_s = prompt("ID del cliente:")
    if not id_s.isdigit(): err("ID inválido."); press_enter(); return
    try:
        row = execute(f"SELECT * FROM {TABLE} WHERE id=%s", (int(id_s),), fetch="one")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not row: err(f"ID {id_s} no encontrado."); press_enter(); return

    print(f"\n  {C.BOLD}Registro actual:{C.RESET}")
    for k, v in row.items(): print(f"    {C.GRAY}{k:<12}{C.RESET} {C.CYAN}{v}{C.RESET}")
    info("Deja en blanco para conservar.\n")

    nombre   = prompt(f"Nombre   [{row['nombre']}]   :") or row["nombre"]
    email    = prompt(f"Email    [{row['email']}]    :") or row["email"]
    telefono = prompt(f"Teléfono [{row['telefono']}] :") or (row["telefono"] or "")
    ciudad   = prompt(f"Ciudad   [{row['ciudad']}]   :") or (row["ciudad"] or "")

    errors = []
    ok1, m1 = validate_str(nombre,"Nombre");  not ok1 and errors.append(m1)
    ok2, m2 = validate_email(email);          not ok2 and errors.append(m2)
    if telefono:
        ok3, m3 = validate_phone(telefono);   not ok3 and errors.append(m3)
    if errors: [err(e) for e in errors]; press_enter(); return

    conf = prompt("¿Confirmar cambios? (s/N):").lower()
    if conf != "s": warn("Cancelado."); press_enter(); return

    try:
        execute(f"UPDATE {TABLE} SET nombre=%s,email=%s,telefono=%s,ciudad=%s WHERE id=%s",
                (nombre.strip(), email.strip().lower(),
                 telefono.strip() or None, ciudad.strip() or None, int(id_s)))
        ok(f"Cliente ID {id_s} actualizado.")
        log("UPDATE", f"clientes | ID={id_s} | {row['nombre']}→{nombre} | {row['email']}→{email}")
    except Exception as e:
        err(str(e))
    press_enter()


def eliminar():
    separator("CLIENTES — ELIMINAR")
    id_s = prompt("ID del cliente:")
    if not id_s.isdigit(): err("ID inválido."); press_enter(); return
    try:
        row = execute(f"SELECT * FROM {TABLE} WHERE id=%s", (int(id_s),), fetch="one")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not row: err(f"ID {id_s} no encontrado."); press_enter(); return

    print(f"\n  {C.RED}Eliminando: ID={row['id']} | {row['nombre']} | {row['email']}{C.RESET}")
    conf = prompt("Escribe el EMAIL para confirmar:").strip()
    if conf != row["email"]: warn("Email incorrecto. Cancelado."); press_enter(); return

    try:
        execute(f"DELETE FROM {TABLE} WHERE id=%s", (int(id_s),))
        ok(f"Cliente '{row['nombre']}' eliminado.")
        log("DELETE", f"clientes | ID={id_s} | {row['nombre']} | {row['email']}")
    except Exception as e:
        err(str(e))
    press_enter()


def menu():
    opciones = [("1","Listar",listar),("2","Buscar",buscar),
                ("3","Crear",crear),("4","Actualizar",actualizar),
                ("5","Eliminar",eliminar),("0","Volver",None)]
    while True:
        separator("MENÚ — CLIENTES")
        for k,label,_ in opciones:
            print(f"  {C.YELLOW}[{k}]{C.RESET}  {label}")
        op = prompt("\n  Opción:")
        if op == "0": break
        fn = next((f for k,_,f in opciones if k==op and f), None)
        if fn: fn()
        else: warn("Opción inválida.")
