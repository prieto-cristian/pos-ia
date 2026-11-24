from .consultas import productos_con_stock_bajo


def listar_productos_stock_bajo(limite: int = 10):
    """Lista productos activos cuyo stock es igual o menor al stock mínimo.

    Args:
        limite: Cantidad máxima de productos a devolver. Debe estar entre 1 y 50.
    """
    return productos_con_stock_bajo(limite=limite)