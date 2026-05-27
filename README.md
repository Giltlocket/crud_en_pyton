# DRUD Manager Pro v2.0

Aplicación de terminal modular para gestión de base de datos **MySQL** con:
pool de conexiones · 3 tablas · DRUD completo · validaciones · log · respaldos JSON · rollback · truncar tablas.

---

## Instalación

```bash
pip install mysql-connector-python

# Crear la base de datos en MySQL
CREATE DATABASE IF NOT EXISTS crud_drud CHARACTER SET utf8mb4;

# Editar credenciales
# → config/settings.py  →  DB_CONFIG

python main.py
```

---

## Estructura del proyecto

```
drud_manager/
│
├── main.py                        ← Punto de entrada
│
├── config/
│   ├── __init__.py
│   └── settings.py                ← 🔧 Credenciales MySQL y configuración
│
├── db/
│   ├── __init__.py
│   ├── connection.py              ← Pool de conexiones MySQL (pool_size=5)
│   └── init_db.py                 ← Crea las 3 tablas automáticamente
│
├── modules/
│   ├── __init__.py
│   ├── productos/
│   │   ├── __init__.py
│   │   └── crud.py                ← DRUD: listar, buscar, crear, actualizar, eliminar
│   ├── clientes/
│   │   ├── __init__.py
│   │   └── crud.py                ← DRUD: listar, buscar, crear, actualizar, eliminar
│   ├── ventas/
│   │   ├── __init__.py
│   │   └── crud.py                ← DRUD: listar, buscar, registrar, eliminar (+stock)
│   ├── history.py                 ← Visor de historial con filtros
│   ├── backup.py                  ← Exportar JSON + Rollback por tabla
│   └── truncate.py                ← Truncar tablas con confirmación
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                  ← Logger centralizado → logs/app.log
│   ├── display.py                 ← Colores ANSI, tablas, prompts
│   └── validators.py              ← Validaciones: str, email, teléfono, decimal, int
│
├── logs/
│   └── app.log                    ← Generado automáticamente
│
├── backups/                       ← Respaldos JSON por tabla
│   └── {tabla}_{timestamp}_{tag}.json
│
└── requirements.txt
```

---

## Tablas

### productos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT AUTO_INCREMENT | PK |
| nombre | VARCHAR(120) | Nombre del producto |
| categoria | VARCHAR(80) | Categoría |
| precio | DECIMAL(10,2) | Precio (≥ 0) |
| stock | INT | Cantidad disponible |
| activo | TINYINT | 1=activo, 0=inactivo |
| creado_en | DATETIME | Fecha de creación |
| actualizado | DATETIME | Última modificación |

### clientes
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT AUTO_INCREMENT | PK |
| nombre | VARCHAR(120) | Nombre completo |
| email | VARCHAR(160) UNIQUE | Correo electrónico |
| telefono | VARCHAR(20) | Teléfono (opcional) |
| ciudad | VARCHAR(80) | Ciudad (opcional) |
| activo | TINYINT | 1=activo |

### ventas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT AUTO_INCREMENT | PK |
| cliente_id | INT FK | Referencia a clientes |
| producto_id | INT FK | Referencia a productos |
| cantidad | INT | Unidades vendidas |
| precio_unitario | DECIMAL | Precio al momento de venta |
| total | DECIMAL GENERATED | cantidad × precio_unitario |
| fecha | DATETIME | Fecha de la venta |

---

## Pool de conexiones

Configurado en `config/settings.py`:
```python
"pool_name":  "crud_pool",
"pool_size":  5,            # conexiones simultáneas
```
Cada operación obtiene una conexión del pool y la devuelve automáticamente al terminar.

---

## Checklist de requisitos

| Requisito | Cubierto |
|-----------|----------|
| Conexión a base de datos | ✅ MySQL |
| Pool de conexiones | ✅ `mysql.connector.pooling` |
| Funciones DRUD | ✅ Display, Read, Update, Delete en 3 tablas |
| Mínimo 3 tablas | ✅ productos, clientes, ventas |
| Menú de funciones | ✅ Menú principal + submenús por tabla |
| Validación de información | ✅ `utils/validators.py` |
| Opción de truncar tablas | ✅ `modules/truncate.py` |
| Historial de cambios (.log) | ✅ `logs/app.log` con filtros |
| Apartado para revisar historial | ✅ Opción 4 del menú |
| Respaldo en JSON | ✅ Por tabla o todas, con etiqueta |
| Restauración desde JSON | ✅ Rollback con modo reemplazar/agregar |
