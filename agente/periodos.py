import calendar
from datetime import date, timedelta

from django.utils import timezone


REGLAS_PERIODOS = """
Interpretá los períodos temporales usando exclusivamente estos tipos:

- historial_completo: todas las ventas disponibles. Usalo si no se menciona
  ningún período.
- semana_actual: desde el lunes de esta semana hasta hoy.
- semana_anterior: desde el lunes hasta el domingo de la semana pasada.
- mes_actual: desde el día 1 del mes actual hasta hoy.
- mes_anterior: el mes calendario anterior completo.
- anio_actual: desde el 1 de enero hasta hoy.
- anio_anterior: el año calendario anterior completo.
- trimestre_actual: desde el inicio del trimestre actual hasta hoy.
- trimestre_anterior: el trimestre calendario anterior completo.
- trimestre_especifico: requiere trimestre y año. Si no se menciona año,
  usa el año actual.
- ultimos_n_dias: requiere dias. Incluye hoy y los días anteriores.
- rango_explicito: requiere desde y hasta, ambas fechas inclusivas.

Si la frase del usuario no permite elegir un período con claridad, pedí una
aclaración. No reemplaces un período no entendido por historial_completo.
"""


def _primer_dia_mes(anio, mes):
    return date(anio, mes, 1)


def _ultimo_dia_mes(anio, mes):
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, ultimo_dia)


def _leer_fecha_iso(valor, nombre):
    try:
        fecha = date.fromisoformat(valor)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{nombre} debe tener formato YYYY-MM-DD."
        ) from error

    if fecha.isoformat() != valor:
        raise ValueError(f"{nombre} debe tener formato YYYY-MM-DD.")

    return fecha


def _fechas_trimestre(anio, trimestre, hoy):
    if trimestre not in (1, 2, 3, 4):
        raise ValueError("El trimestre debe ser 1, 2, 3 o 4.")

    mes_inicio = (trimestre - 1) * 3 + 1
    mes_fin = mes_inicio + 2

    desde = date(anio, mes_inicio, 1)
    hasta = _ultimo_dia_mes(anio, mes_fin)

    trimestre_actual = (hoy.month - 1) // 3 + 1
    if anio == hoy.year and trimestre == trimestre_actual:
        hasta = min(hasta, hoy)

    return desde, hasta


def resolver_periodo(
    tipo_periodo,
    anio=0,
    trimestre=0,
    dias=0,
    desde="",
    hasta="",
):
    """Devuelve fechas inicial y final inclusivas; None, None significa todo."""
    hoy = timezone.localdate()

    if tipo_periodo == "historial_completo":
        return None, None

    if tipo_periodo == "semana_actual":
        return hoy - timedelta(days=hoy.weekday()), hoy

    if tipo_periodo == "semana_anterior":
        lunes_actual = hoy - timedelta(days=hoy.weekday())
        domingo_anterior = lunes_actual - timedelta(days=1)
        lunes_anterior = domingo_anterior - timedelta(days=6)
        return lunes_anterior, domingo_anterior

    if tipo_periodo == "mes_actual":
        return _primer_dia_mes(hoy.year, hoy.month), hoy

    if tipo_periodo == "mes_anterior":
        if hoy.month == 1:
            anio_anterior, mes_anterior = hoy.year - 1, 12
        else:
            anio_anterior, mes_anterior = hoy.year, hoy.month - 1

        return (
            _primer_dia_mes(anio_anterior, mes_anterior),
            _ultimo_dia_mes(anio_anterior, mes_anterior),
        )

    if tipo_periodo == "anio_actual":
        return date(hoy.year, 1, 1), hoy

    if tipo_periodo == "anio_anterior":
        return date(hoy.year - 1, 1, 1), date(hoy.year - 1, 12, 31)

    if tipo_periodo == "trimestre_actual":
        trimestre_actual = (hoy.month - 1) // 3 + 1
        return _fechas_trimestre(hoy.year, trimestre_actual, hoy)

    if tipo_periodo == "trimestre_anterior":
        trimestre_actual = (hoy.month - 1) // 3 + 1
        if trimestre_actual == 1:
            anio_anterior, trimestre_anterior = hoy.year - 1, 4
        else:
            anio_anterior = hoy.year
            trimestre_anterior = trimestre_actual - 1

        return _fechas_trimestre(
            anio_anterior,
            trimestre_anterior,
            hoy,
        )

    if tipo_periodo == "trimestre_especifico":
        anio = int(anio or hoy.year)
        trimestre = int(trimestre)
        return _fechas_trimestre(anio, trimestre, hoy)

    if tipo_periodo == "ultimos_n_dias":
        dias = int(dias)
        if not 1 <= dias <= 3650:
            raise ValueError("dias debe estar entre 1 y 3650.")

        return hoy - timedelta(days=dias - 1), hoy

    if tipo_periodo == "rango_explicito":
        fecha_desde = _leer_fecha_iso(desde, "desde")
        fecha_hasta = _leer_fecha_iso(hasta, "hasta")

        if fecha_desde > fecha_hasta:
            raise ValueError("'desde' no puede ser posterior a 'hasta'.")

        return fecha_desde, fecha_hasta

    raise ValueError(f"Tipo de período no reconocido: {tipo_periodo}")

def _sumar_meses(fecha, cantidad):
    indice_mes = fecha.year * 12 + fecha.month - 1 + cantidad
    anio, mes_cero = divmod(indice_mes, 12)
    mes = mes_cero + 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def resolver_periodos_comparables(
    tipo_periodo,
    anio=0,
    trimestre=0,
    dias=0,
    desde="",
    hasta="",
):
    hoy = timezone.localdate()

    actual_desde, actual_hasta = resolver_periodo(
        tipo_periodo=tipo_periodo,
        anio=anio,
        trimestre=trimestre,
        dias=dias,
        desde=desde,
        hasta=hasta,
    )

    if actual_desde is None or actual_hasta is None:
        raise ValueError(
            "Para comparar ventas se necesita un período, "
            "no el historial completo."
        )

    if tipo_periodo == "mes_actual":
        comparacion_desde = _sumar_meses(actual_desde, -1).replace(day=1)
        comparacion_hasta = _sumar_meses(actual_hasta, -1)

    elif tipo_periodo == "mes_anterior":
        comparacion_hasta = _sumar_meses(actual_hasta, -1)
        comparacion_desde = comparacion_hasta.replace(day=1)

    elif tipo_periodo == "anio_actual":
        comparacion_desde = date(actual_desde.year - 1, 1, 1)
        comparacion_hasta = _sumar_meses(actual_hasta, -12)

    elif tipo_periodo == "anio_anterior":
        comparacion_desde = date(actual_desde.year - 1, 1, 1)
        comparacion_hasta = date(actual_hasta.year - 1, 12, 31)

    elif tipo_periodo in ("semana_actual", "semana_anterior"):
        comparacion_desde = actual_desde - timedelta(days=7)
        comparacion_hasta = actual_hasta - timedelta(days=7)

    elif tipo_periodo == "trimestre_actual":
        comparacion_desde = _sumar_meses(actual_desde, -3)
        comparacion_hasta = _sumar_meses(actual_hasta, -3)

    elif tipo_periodo in ("trimestre_anterior", "trimestre_especifico"):
        comparacion_hasta = _sumar_meses(actual_desde, -1)
        comparacion_hasta = comparacion_hasta.replace(day=1) - timedelta(days=1)
        comparacion_desde = comparacion_hasta.replace(
            month=((comparacion_hasta.month - 1) // 3) * 3 + 1,
            day=1,
        )

    else:
        duracion = (actual_hasta - actual_desde).days + 1
        comparacion_hasta = actual_desde - timedelta(days=1)
        comparacion_desde = comparacion_hasta - timedelta(days=duracion - 1)

    return (
        actual_desde,
        actual_hasta,
        comparacion_desde,
        comparacion_hasta,
    )