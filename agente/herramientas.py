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
    desde: str = "",
    hasta: str = "",
    limite: int = 10,
):
    """Obtiene el ranking de productos por unidades vendidas.

    Si no se indican fechas, usa todo el historial disponible.
    Si se indica un período, desde y hasta deben tener formato YYYY-MM-DD
    y ambas fechas son inclusivas.

    Args:
        desde: Fecha inicial opcional, formato YYYY-MM-DD.
        hasta: Fecha final opcional, formato YYYY-MM-DD.
        limite: Cantidad máxima de productos a devolver. Entre 1 y 50.
    """
    return productos_mas_vendidos(
        desde=desde or None,
        hasta=hasta or None,
        limite=limite,
    )