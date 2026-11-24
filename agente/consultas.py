from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone

from productos.models import Producto
from ventas.models import DetalleVenta, Pago, Venta


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

def _ventas_en_periodo(desde=None, hasta=None):
    ventas = Venta.objects.all()

    if desde is None and hasta is None:
        return ventas, None, None

    if desde is None or hasta is None:
        raise ValueError(
            "Para consultar un período, se necesitan desde y hasta."
        )

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

    ventas = ventas.filter(
        fecha__gte=inicio,
        fecha__lt=fin_exclusivo,
    )

    return ventas, fecha_desde, fecha_hasta

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

def productos_mas_vendidos(desde=None, hasta=None, limite=10):
    limite = max(1, min(int(limite), 50))

    ventas, fecha_desde, fecha_hasta = _ventas_en_periodo(desde, hasta)
    detalles = DetalleVenta.objects.filter(venta__in=ventas)

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

def resumen_ventas(desde=None, hasta=None):
    ventas_qs, fecha_desde, fecha_hasta = _ventas_en_periodo(
        desde,
        hasta,
    )
    detalles = DetalleVenta.objects.filter(venta__in=ventas_qs)

    totales_detalles = detalles.aggregate(
        unidades=Sum("cantidad"),
        importe=Sum(F("precio_unitario") * F("cantidad")),
    )

    importe_vendido = totales_detalles["importe"] or Decimal("0.00")
    unidades_vendidas = totales_detalles["unidades"] or 0

    importe_cobrado = (
        Pago.objects
        .filter(venta__in=ventas_qs)
        .aggregate(total=Sum("importe"))["total"]
        or Decimal("0.00")
    )

    saldo_pendiente = importe_vendido - importe_cobrado

    return {
        "desde": fecha_desde.isoformat() if fecha_desde else None,
        "hasta": fecha_hasta.isoformat() if fecha_hasta else None,
        "periodo": (
            "historial_completo"
            if fecha_desde is None
            else "rango_especificado"
        ),
        "cantidad_ventas": ventas_qs.count(),
        "unidades_vendidas": unidades_vendidas,
        "importe_vendido": format(importe_vendido, ".2f"),
        "importe_cobrado": format(importe_cobrado, ".2f"),
        "saldo_pendiente": format(saldo_pendiente, ".2f"),
    }