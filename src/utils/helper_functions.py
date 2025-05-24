import re
from datetime import datetime

def validate_date(fecha_str):
    # Unifica separadores a "/"
    fecha_normalizada = re.sub(r"[- ]", "/", fecha_str.strip())

    # Patrón que permite 1 o 2 dígitos para día/mes y 2 o 4 dígitos para año
    patron = r"^(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})$"

    match = re.match(patron, fecha_normalizada)
    if not match:
        return False

    dia, mes, anio = match.groups()

    try:
        # Si el año es de 2 dígitos, usar %y; si es de 4, usar %Y
        formato = "%d/%m/%y" if len(anio) == 2 else "%d/%m/%Y"
        datetime.strptime(fecha_normalizada, formato)
        return True
    except ValueError:
        return False

def format_date(fecha_str):
    """
    Convierte una fecha válida a formato dd/mm/yyyy.
    Retorna None si la fecha no es válida.
    """
    if not validate_date(fecha_str):
        return None

    fecha_normalizada = re.sub(r"[- ]", "/", fecha_str)

    if len(fecha_normalizada.split('/')[-1]) == 2:
        fecha_obj = datetime.strptime(fecha_normalizada, "%d/%m/%y")
    else:
        fecha_obj = datetime.strptime(fecha_normalizada, "%d/%m/%Y")

    return fecha_obj.strftime("%d/%m/%Y")
