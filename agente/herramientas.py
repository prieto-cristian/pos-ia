from .periodos import resolver_periodo
from .consultas import (
    productos_con_stock_bajo,
    productos_mas_vendidos,
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
    fecha_desde, fecha_hasta = resolver_periodo(
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