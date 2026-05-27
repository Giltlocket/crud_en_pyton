"""
utils/validators.py  —  Validaciones reutilizables.
"""

import re


def validate_str(value: str, field: str, min_len=2, max_len=120) -> tuple[bool, str]:
    if not value or not value.strip():
        return False, f"{field} no puede estar vacío."
    if len(value.strip()) < min_len:
        return False, f"{field} debe tener al menos {min_len} caracteres."
    if len(value.strip()) > max_len:
        return False, f"{field} no puede superar {max_len} caracteres."
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        return False, "Email con formato inválido (ejemplo: user@dominio.com)."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    clean = re.sub(r"[\s\-\(\)\+]", "", phone)
    if not clean.isdigit():
        return False, "Teléfono solo debe contener dígitos (y +, -, espacios)."
    if not (7 <= len(clean) <= 15):
        return False, "Teléfono debe tener entre 7 y 15 dígitos."
    return True, ""


def validate_decimal(value: str, field: str, min_val=0.0) -> tuple[bool, float | str]:
    try:
        n = float(value.replace(",", "."))
    except ValueError:
        return False, f"{field} debe ser un número decimal (ej. 99.90)."
    if n < min_val:
        return False, f"{field} no puede ser menor a {min_val}."
    return True, n


def validate_int(value: str, field: str, min_val=0) -> tuple[bool, int | str]:
    try:
        n = int(value)
    except ValueError:
        return False, f"{field} debe ser un número entero."
    if n < min_val:
        return False, f"{field} no puede ser menor a {min_val}."
    return True, n
