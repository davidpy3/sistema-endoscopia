def calcular_edad(fecha_nacimiento, fecha_referencia):
    """Edad en años cumplidos a la fecha del procedimiento."""
    if not fecha_nacimiento or not fecha_referencia:
        return None
    years = fecha_referencia.year - fecha_nacimiento.year
    if (fecha_referencia.month, fecha_referencia.day) < (
        fecha_nacimiento.month,
        fecha_nacimiento.day,
    ):
        years -= 1
    return years


def yn(value):
    """Replica yn() del prototipo JS: True->Sí, False->No, None->—"""
    if value is None:
        return "—"
    return "Sí" if value else "No"


def dash(value):
    """Replica el patrón `${x||'—'}` del prototipo, sin ocultar ceros."""
    if value is None:
        return "—"
    if isinstance(value, str):
        return value if value else "—"
    return value
