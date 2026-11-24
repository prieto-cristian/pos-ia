from django.db.models import F

from productos.models import Producto


def productos_con_stock_bajo(limite=10):
    """Devuelve productos activos con stock igual o menor al mínimo."""
    limite = max(1, min(int(limite), 50))

    productos = (
        Producto.objects
        .filter(activo=True, stock__lte=F("stock_minimo"))
        .order_by("stock", "nombre")
        .values("id", "nombre", "stock", "stock_minimo")[:limite]
    )

    return list(productos)