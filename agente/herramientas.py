from .periodos import (
    resolver_periodo,
    resolver_periodos_comparables,
)
from .consultas import (
    productos_con_stock_bajo,
    productos_mas_vendidos,
    resumen_ventas,
    calcular_comparacion_ventas,
    calcular_rotacion_stock,
)

def _fechas_de_periodo(
    tipo_periodo,
    anio=0,
    trimestre=0,
    dias=0,
    desde="",
    hasta="",
):
    return resolver_periodo(
        tipo_periodo=tipo_periodo,
        anio=anio,
        trimestre=trimestre,
        dias=dias,
        desde=desde,
        hasta=hasta,
    )

def listar_productos_stock_bajo(limite: int = 10):
    """Lista productos activos cuyo stock es igual o menor al mínimo.

    Args:
        limite: Cantidad máxima de productos a devolver. Debe estar entre 1 y 50.
    """
    return productos_con_stock_bajo(limite=limite)

def obtener_productos_mas_vendidos(
    tipo_periodo: str,
    anio: int = 0,
    trimestre: int = 0,
    dias: int = 0,
    desde: str = "",
    hasta: str = "",
    limite: int = 10,
):
    """Obtiene el ranking por unidades vendidas para un período.

    Args:
        tipo_periodo: Uno de los tipos definidos en las instrucciones del
            asistente, por ejemplo mes_actual, trimestre_especifico,
            ultimos_n_dias, rango_explicito o historial_completo.
        anio: Año para trimestre_especifico. Si se omite, se usa el actual.
        trimestre: Número de trimestre, del 1 al 4.
        dias: Cantidad de días para ultimos_n_dias.
        desde: Fecha inicial YYYY-MM-DD para rango_explicito.
        hasta: Fecha final YYYY-MM-DD para rango_explicito.
        limite: Cantidad máxima de productos, entre 1 y 50.
    """
    fecha_desde, fecha_hasta = _fechas_de_periodo(
        tipo_periodo=tipo_periodo,
        anio=anio,
        trimestre=trimestre,
        dias=dias,
        desde=desde,
        hasta=hasta,
    )

    return productos_mas_vendidos(
        desde=fecha_desde.isoformat() if fecha_desde else None,
        hasta=fecha_hasta.isoformat() if fecha_hasta else None,
        limite=limite,
    )

def resumir_ventas(
    tipo_periodo: str,
    anio: int = 0,
    trimestre: int = 0,
    dias: int = 0,
    desde: str = "",
    hasta: str = "",
):
    """Resume las ventas y los pagos de un período.

    Si no se indica período, usa todo el historial disponible.

    Args:
        tipo_periodo: Tipo de período definido en las instrucciones.
        anio: Año para trimestre_especifico.
        trimestre: Número de trimestre, del 1 al 4.
        dias: Cantidad de días para ultimos_n_dias.
        desde: Fecha inicial YYYY-MM-DD para rango_explicito.
        hasta: Fecha final YYYY-MM-DD para rango_explicito.
    """
    fecha_desde, fecha_hasta = _fechas_de_periodo(
        tipo_periodo=tipo_periodo,
        anio=anio,
        trimestre=trimestre,
        dias=dias,
        desde=desde,
        hasta=hasta,
    )

    return resumen_ventas(
        desde=fecha_desde.isoformat() if fecha_desde else None,
        hasta=fecha_hasta.isoformat() if fecha_hasta else None,
    )

def comparar_ventas_por_producto(
    tipo_periodo: str,
    anio: int = 0,
    trimestre: int = 0,
    dias: int = 0,
    desde: str = "",
    hasta: str = "",
    limite: int = 5,
):
    """Compara unidades vendidas por producto entre dos períodos equivalentes.

    Si el usuario no indica período, usa el mes actual contra el mes anterior.
    No calcula ingresos ni rentabilidad.

    Args:
        tipo_periodo: Tipo de período definido en las instrucciones.
        anio: Año para trimestre_especifico.
        trimestre: Número de trimestre, del 1 al 4.
        dias: Cantidad de días para ultimos_n_dias.
        desde: Fecha inicial YYYY-MM-DD para rango_explicito.
        hasta: Fecha final YYYY-MM-DD para rango_explicito.
        limite: Cantidad máxima de aumentos y caídas a devolver.
    """
    if not tipo_periodo:
        tipo_periodo = "mes_actual"

    rangos = resolver_periodos_comparables(
        tipo_periodo=tipo_periodo,
        anio=anio,
        trimestre=trimestre,
        dias=dias,
        desde=desde,
        hasta=hasta,
    )

    actual_desde, actual_hasta, anterior_desde, anterior_hasta = rangos

    return calcular_comparacion_ventas(
        desde_actual=actual_desde.isoformat(),
        hasta_actual=actual_hasta.isoformat(),
        desde_comparacion=anterior_desde.isoformat(),
        hasta_comparacion=anterior_hasta.isoformat(),
        limite=limite,
    )

def analizar_rotacion_stock(
    tipo_periodo: str = "ultimos_n_dias",
    anio: int = 0,
    trimestre: int = 0,
    dias: int = 30,
    desde: str = "",
    hasta: str = "",
    limite: int = 10,
):
    """Analiza las ventas recientes frente al stock actual.

    Devuelve productos activos con stock que no tuvieron ventas en el período
    y productos ordenados por días estimados de cobertura.
    """

    fecha_desde, fecha_hasta = resolver_periodo(
        tipo_periodo=tipo_periodo,
        anio=anio,
        trimestre=trimestre,
        dias=dias,
        desde=desde,
        hasta=hasta,
    )

    if fecha_desde is None or fecha_hasta is None:
        raise ValueError(
            "Para analizar la rotación del stock se necesita un período "
            "con fecha de inicio y fin."
        )

    return calcular_rotacion_stock(
        desde=fecha_desde.isoformat(),
        hasta=fecha_hasta.isoformat(),
        limite=limite,
    )