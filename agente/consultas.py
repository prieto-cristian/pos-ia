from datetime import date, datetime, time, timedelta

from django.db.models import F, Sum
from django.utils import timezone

from productos.models import Producto
from ventas.models import DetalleVenta


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


def _leer_fecha(valor, nombre_parametro):
    if not isinstance(valor, str):
        raise ValueError(f"{nombre_parametro} debe tener formato YYYY-MM-DD.")

    try:
        fecha = date.fromisoformat(valor)
    except ValueError as error:
        raise ValueError(
            f"{nombre_parametro} debe tener formato YYYY-MM-DD."
        ) from error

    if fecha.isoformat() != valor:
        raise ValueError(f"{nombre_parametro} debe tener formato YYYY-MM-DD.")

    return fecha


def productos_mas_vendidos(desde=None, hasta=None, limite=10):
    limite = max(1, min(int(limite), 50))

    detalles = DetalleVenta.objects.all()

    if desde is None and hasta is None:
        fecha_desde = None
        fecha_hasta = None

    elif desde is None or hasta is None:
        raise ValueError(
            "Para consultar un período, se necesitan desde y hasta."
        )

    else:
        fecha_desde = _leer_fecha(desde, "desde")
        fecha_hasta = _leer_fecha(hasta, "hasta")

        if fecha_desde > fecha_hasta:
            raise ValueError("'desde' no puede ser posterior a 'hasta'.")

        zona_horaria = timezone.get_current_timezone()
        inicio = timezone.make_aware(
            datetime.combine(fecha_desde, time.min),
            zona_horaria,
        )
        fin_exclusivo = timezone.make_aware(
            datetime.combine(fecha_hasta + timedelta(days=1), time.min),
            zona_horaria,
        )

        detalles = detalles.filter(
            venta__fecha__gte=inicio,
            venta__fecha__lt=fin_exclusivo,
        )

    resultados = (
        detalles
        .values("producto_id", "producto__nombre")
        .annotate(unidades_vendidas=Sum("cantidad"))
        .order_by("-unidades_vendidas", "producto__nombre")[:limite]
    )

    return {
        "desde": fecha_desde.isoformat() if fecha_desde else None,
        "hasta": fecha_hasta.isoformat() if fecha_hasta else None,
        "periodo": (
            "historial_completo"
            if fecha_desde is None
            else "rango_especificado"
        ),
        "resultados": list(resultados),
    }