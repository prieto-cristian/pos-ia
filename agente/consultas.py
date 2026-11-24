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

def _unidades_por_producto(ventas_qs):
    detalles = DetalleVenta.objects.filter(venta__in=ventas_qs)

    filas = (
        detalles
        .values("producto_id", "producto__nombre")
        .annotate(unidades=Sum("cantidad"))
    )

    return {
        fila["producto_id"]: {
            "nombre": fila["producto__nombre"],
            "unidades": fila["unidades"],
        }
        for fila in filas
    }


def calcular_comparacion_ventas(
    desde_actual,
    hasta_actual,
    desde_comparacion,
    hasta_comparacion,
    limite=5,
):
    limite = max(1, min(int(limite), 20))

    ventas_actuales, _, _ = _ventas_en_periodo(
        desde_actual,
        hasta_actual,
    )
    ventas_comparacion, _, _ = _ventas_en_periodo(
        desde_comparacion,
        hasta_comparacion,
    )

    actuales = _unidades_por_producto(ventas_actuales)
    anteriores = _unidades_por_producto(ventas_comparacion)

    total_unidades_actuales = sum(
        producto["unidades"] for producto in actuales.values()
    )
    total_unidades_anteriores = sum(
        producto["unidades"] for producto in anteriores.values()
    )

    diferencia_total = total_unidades_actuales - total_unidades_anteriores

    variacion_total_porcentual = None
    if total_unidades_anteriores:
        variacion_total_porcentual = format(
            Decimal(diferencia_total) * Decimal("100")
            / Decimal(total_unidades_anteriores),
            ".1f",
        )

    productos = []

    for producto_id in actuales.keys() | anteriores.keys():
        actual = actuales.get(producto_id)
        anterior = anteriores.get(producto_id)
        producto = actual or anterior

        unidades_actuales = actual["unidades"] if actual else 0
        unidades_anteriores = anterior["unidades"] if anterior else 0
        diferencia = unidades_actuales - unidades_anteriores

        porcentaje = None
        if unidades_anteriores:
            porcentaje = format(
                Decimal(diferencia) * Decimal("100")
                / Decimal(unidades_anteriores),
                ".1f",
            )

        productos.append({
            "producto_id": producto_id,
            "nombre": producto["nombre"],
            "unidades_actuales": unidades_actuales,
            "unidades_periodo_anterior": unidades_anteriores,
            "diferencia_unidades": diferencia,
            "variacion_porcentual": porcentaje,
            "sin_base_anterior": unidades_anteriores == 0,
        })

    aumentos = sorted(
        (p for p in productos if p["diferencia_unidades"] > 0),
        key=lambda p: p["diferencia_unidades"],
        reverse=True,
    )[:limite]

    caidas = sorted(
        (p for p in productos if p["diferencia_unidades"] < 0),
        key=lambda p: p["diferencia_unidades"],
    )[:limite]

    return {
        "periodo_actual": {
            "desde": desde_actual,
            "hasta": hasta_actual,
        },
        "periodo_comparacion": {
            "desde": desde_comparacion,
            "hasta": hasta_comparacion,
        },
        "mayores_aumentos": aumentos,
        "mayores_caidas": caidas,
        "totales": {
            "unidades_actuales": total_unidades_actuales,
            "unidades_periodo_anterior": total_unidades_anteriores,
            "diferencia_unidades": diferencia_total,
            "variacion_porcentual": variacion_total_porcentual,
        },
    }

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