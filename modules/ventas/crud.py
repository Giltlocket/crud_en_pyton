"""
modules/ventas/crud.py  —  DRUD completo de Ventas.
"""

from db    import execute
from utils import (log, ok, err, warn, info, prompt,
                   press_enter, separator, print_table, C,
                   validate_int, validate_decimal)

TABLE = "ventas"
COLS  = [
    ("id",              "ID",        5,  "r"),
    ("cliente",         "Cliente",  22,  "l"),
    ("producto",        "Producto", 22,  "l"),
    ("cantidad",        "Cant.",     6,  "r"),
    ("precio_unitario", "P.Unit.",   9,  "r"),
    ("total",           "Total",    10,  "r"),
    ("fecha",           "Fecha",    19,  "l"),
]

_JOIN = (
    "SELECT v.id, c.nombre AS cliente, p.nombre AS producto, "
    "v.cantidad, v.precio_unitario, v.total, v.fecha "
    "FROM ventas v "
    "JOIN clientes c ON c.id = v.cliente_id "
    "JOIN productos p ON p.id = v.producto_id "
)


def _fmt(rows):
    for r in rows:
        r["precio_unitario"] = f"${float(r['precio_unitario']):,.2f}"
        r["total"]           = f"${float(r['total']):,.2f}"
        r["fecha"]           = str(r["fecha"])[:19]
    return rows


def listar():
    separator("VENTAS — LISTAR")
    try:
        rows = execute(_JOIN + "ORDER BY v.id DESC", fetch="all")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not rows: warn("Sin ventas registradas.")
    else:
        print_table(_fmt(rows), COLS)
        totales = sum(float(str(r["total"]).replace("$","").replace(",","")) for r in rows)
        info(f"Total: {len(rows)} venta(s)  |  Suma: ${totales:,.2f}")
        log("READ", f"ventas — {len(rows)} registros")
    press_enter()


def buscar():
    separator("VENTAS — BUSCAR")
    t = prompt("ID de venta, cliente o producto:")
    if not t: press_enter(); return
    try:
        rows = execute(
            _JOIN + "WHERE v.id=%s OR c.nombre LIKE %s OR p.nombre LIKE %s ORDER BY v.id DESC",
            (t if t.isdigit() else 0, f"%{t}%", f"%{t}%"), fetch="all")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not rows: warn(f"Sin resultados para '{t}'.")
    else: print_table(_fmt(rows), COLS)
    log("READ", f"ventas buscar '{t}' — {len(rows)} resultado(s)")
    press_enter()


def crear():
    separator("VENTAS — CREAR")

    # Mostrar clientes disponibles
    try:
        clientes  = execute("SELECT id, nombre FROM clientes WHERE activo=1 ORDER BY id", fetch="all")
        productos = execute("SELECT id, nombre, precio, stock FROM productos WHERE activo=1 AND stock>0 ORDER BY id", fetch="all")
    except Exception as e:
        err(str(e)); press_enter(); return

    if not clientes:  warn("No hay clientes activos. Crea uno primero."); press_enter(); return
    if not productos: warn("No hay productos con stock. Agrega stock primero."); press_enter(); return

    print(f"\n  {C.BOLD}Clientes disponibles:{C.RESET}")
    for c in clientes: print(f"    {C.CYAN}{c['id']}{C.RESET} — {c['nombre']}")

    print(f"\n  {C.BOLD}Productos disponibles:{C.RESET}")
    for p in productos:
        print(f"    {C.CYAN}{p['id']}{C.RESET} — {p['nombre']}  {C.GREEN}${float(p['precio']):,.2f}{C.RESET}  stock:{p['stock']}")

    cliente_s  = prompt("\n  ID cliente  :")
    producto_s = prompt("  ID producto :")
    cantidad_s = prompt("  Cantidad    :", "1")

    errors = []
    ok1, m1 = validate_int(cliente_s,  "ID cliente",  1); not ok1 and errors.append(m1)
    ok2, m2 = validate_int(producto_s, "ID producto", 1); not ok2 and errors.append(m2)
    ok3, m3 = validate_int(cantidad_s, "Cantidad",    1); not ok3 and errors.append(m3)
    if errors: [err(e) for e in errors]; press_enter(); return

    _, cli_id = validate_int(cliente_s,  "ID cliente")
    _, pro_id = validate_int(producto_s, "ID producto")
    _, cant   = validate_int(cantidad_s, "Cantidad")

    # Verificar IDs existen
    cli = next((c for c in clientes  if c["id"] == cli_id), None)
    pro = next((p for p in productos if p["id"] == pro_id), None)
    if not cli: err(f"Cliente ID {cli_id} no encontrado o inactivo."); press_enter(); return
    if not pro: err(f"Producto ID {pro_id} no encontrado o sin stock."); press_enter(); return
    if cant > pro["stock"]:
        err(f"Stock insuficiente. Disponible: {pro['stock']}"); press_enter(); return

    precio = float(pro["precio"])
    total  = cant * precio
    print(f"\n  {C.YELLOW}Resumen:{C.RESET}  {cli['nombre']}  ·  {pro['nombre']}  "
          f"x{cant}  ·  Total: {C.GREEN}${total:,.2f}{C.RESET}")
    conf = prompt("  ¿Confirmar venta? (s/N):").lower()
    if conf != "s": warn("Cancelado."); press_enter(); return

    try:
        new_id = execute(
            f"INSERT INTO {TABLE} (cliente_id, producto_id, cantidad, precio_unitario) VALUES (%s,%s,%s,%s)",
            (cli_id, pro_id, cant, precio))
        # descontar stock
        execute("UPDATE productos SET stock = stock - %s WHERE id=%s", (cant, pro_id))
        ok(f"Venta registrada — ID {new_id}  |  Total: ${total:,.2f}")
        log("CREATE", f"ventas | ID={new_id} | cliente={cli['nombre']} | producto={pro['nombre']} | cant={cant} | total=${total:.2f}")
    except Exception as e:
        err(str(e))
    press_enter()


def eliminar():
    separator("VENTAS — ELIMINAR")
    id_s = prompt("ID de la venta a eliminar:")
    if not id_s.isdigit(): err("ID inválido."); press_enter(); return
    try:
        row = execute(
            _JOIN + "WHERE v.id=%s", (int(id_s),), fetch="one")
    except Exception as e:
        err(str(e)); press_enter(); return
    if not row: err(f"Venta ID {id_s} no encontrada."); press_enter(); return

    print(f"\n  {C.RED}Eliminando venta ID={row['id']} | {row['cliente']} | {row['producto']} | ${row['total']}{C.RESET}")
    conf = prompt("¿Confirmar eliminación? (s/N):").lower()
    if conf != "s": warn("Cancelado."); press_enter(); return

    try:
        # recuperar datos originales para devolver stock
        orig = execute("SELECT producto_id, cantidad FROM ventas WHERE id=%s", (int(id_s),), fetch="one")
        execute(f"DELETE FROM {TABLE} WHERE id=%s", (int(id_s),))
        execute("UPDATE productos SET stock = stock + %s WHERE id=%s", (orig["cantidad"], orig["producto_id"]))
        ok(f"Venta ID {id_s} eliminada y stock reintegrado.")
        log("DELETE", f"ventas | ID={id_s} | {row['cliente']} | {row['producto']}")
    except Exception as e:
        err(str(e))
    press_enter()


def menu():
    opciones = [("1","Listar",listar),("2","Buscar",buscar),
                ("3","Registrar venta",crear),("4","Eliminar venta",eliminar),
                ("0","Volver",None)]
    while True:
        separator("MENÚ — VENTAS")
        for k,label,_ in opciones:
            print(f"  {C.YELLOW}[{k}]{C.RESET}  {label}")
        op = prompt("\n  Opción:")
        if op == "0": break
        fn = next((f for k,_,f in opciones if k==op and f), None)
        if fn: fn()
        else: warn("Opción inválida.")
