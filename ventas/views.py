import json
from collections import Counter
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views import View
from django.views.generic import TemplateView

from productos.models import Producto

from .models import DetalleVenta, Pago, Venta


class _ImportesNoCoinciden(Exception):
    pass


MEDIOS_PAGO = [
    (Pago.MedioPago.EFECTIVO.value, "Efectivo"),
    (Pago.MedioPago.TARJETA.value, "Tarjeta"),
    (Pago.MedioPago.QR.value, "QR"),
    (Pago.MedioPago.TRANSFERENCIA.value, "Transferencia"),
]

PAGOS_CORTOS = {"Transferencia": "Transf."}


def _total_de_ventas(ventas):
    expresion = ExpressionWrapper(
        F("detalles__precio_unitario") * F("detalles__cantidad"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    return ventas.aggregate(total=Sum(expresion))["total"] or Decimal("0")


def _catalogo():
    productos = list(
        Producto.objects.filter(activo=True)
        .prefetch_related("categorias")
        .order_by("nombre")
    )
    conteos = Counter()
    catalogo = []

    for producto in productos:
        categorias = list(producto.categorias.all())
        if categorias:
            principal = categorias[0]
            categoria_slug = slugify(principal.nombre)
            categoria_nombre = principal.nombre
            for categoria in categorias:
                conteos[categoria.nombre] += 1
        else:
            categoria_slug = "otros"
            categoria_nombre = "Sin categoría"
            conteos[categoria_nombre] += 1

        catalogo.append(
            {
                "id": producto.pk,
                "nombre": producto.nombre,
                "precio": str(producto.precio_venta),
                "stock": producto.stock,
                "stock_minimo": producto.stock_minimo,
                "codigo": producto.codigo_barras or "",
                "categoria": categoria_nombre,
                "categoria_slug": categoria_slug,
                "categorias": [
                    slugify(categoria.nombre) for categoria in categorias
                ],
            }
        )

    categorias = [
        {
            "nombre": nombre,
            "slug": slugify(nombre),
            "cuenta": cuenta,
        }
        for nombre, cuenta in sorted(conteos.items())
    ]
    return catalogo, categorias


def _lineas_del_carrito(items):
    lineas = []
    total = Decimal("0")
    for item in items:
        producto = (
            Producto.objects.prefetch_related("categorias")
            .get(pk=item["producto_id"])
        )
        subtotal = producto.precio_venta * item["cantidad"]
        total += subtotal
        categorias = list(producto.categorias.all())
        lineas.append(
            {
                "producto": producto,
                "cantidad": item["cantidad"],
                "precio_unitario": producto.precio_venta,
                "subtotal": subtotal,
                "categoria_slug": (
                    slugify(categorias[0].nombre) if categorias else "otros"
                ),
            }
        )
    return lineas, total


def _ventas_recientes():
    ventas = list(
        Venta.objects.prefetch_related("detalles__producto", "pagos")
        .order_by("-fecha")[:3]
    )
    hoy = timezone.localdate()
    tarjetas = []

    for venta in ventas:
        detalles = list(venta.detalles.all())
        pagos = list(venta.pagos.all())
        nombres = [detalle.producto.nombre for detalle in detalles]
        resumen = nombres[0] if nombres else "Venta sin detalle"
        if len(nombres) > 1:
            resumen = f"{resumen} +{len(nombres) - 1}\u00a0más"

        etiquetas_pago = [
            pago.get_medio_pago_display() for pago in pagos
        ]
        tarjetas.append(
            {
                "pk": venta.pk,
                "resumen": resumen,
                "unidades": sum(detalle.cantidad for detalle in detalles),
                "total": venta.monto_total,
                "fecha": venta.fecha,
                "es_hoy": timezone.localtime(venta.fecha).date() == hoy,
                "pagos": etiquetas_pago,
                "pagos_corto": " · ".join(
                    PAGOS_CORTOS.get(etiqueta, etiqueta)
                    for etiqueta in etiquetas_pago
                ),
                "url": reverse(
                    "admin:ventas_venta_change", args=[venta.pk]
                ),
            }
        )
    return tarjetas


def _resumen_hoy():
    ventas = Venta.objects.filter(fecha__date=timezone.localdate())
    return {
        "cantidad": ventas.count(),
        "total": _total_de_ventas(ventas),
    }


def _contexto_pos(items, **extra):
    catalogo, categorias = _catalogo()
    lineas, total = _lineas_del_carrito(items)
    contexto = {
        "nav_activo": "caja",
        "medios_pago": MEDIOS_PAGO,
        "items": json.dumps(items),
        "initial_items": items,
        "lineas": lineas,
        "total": total,
        "total_unidades": sum(linea["cantidad"] for linea in lineas),
        "catalogo": catalogo,
        "categorias": categorias,
        "total_productos": len(catalogo),
        "ventas_recientes": _ventas_recientes(),
        "resumen_hoy": _resumen_hoy(),
        "hoy": timezone.localdate(),
    }
    contexto.update(extra)
    return contexto


class PosView(TemplateView):
    template_name = "ventas/pos.html"

    def get_context_data(self, **kwargs):
        error = ""
        items = []
        pendiente = self.request.session.pop("pos_error", None)
        if pendiente:
            items = pendiente.get("items", [])
            error = pendiente.get("error", "")

        context = super().get_context_data(**kwargs)
        context.update(_contexto_pos(items))
        if error:
            context["error"] = error

        venta_id = self.request.session.pop("venta_cobrada", None)
        if venta_id:
            venta = (
                Venta.objects.prefetch_related(
                    "pagos", "detalles__producto"
                )
                .filter(pk=venta_id)
                .first()
            )
            if venta:
                detalles = list(venta.detalles.all())
                context["venta"] = venta
                context["venta_pagos"] = list(venta.pagos.all())
                context["venta_unidades"] = sum(
                    detalle.cantidad for detalle in detalles
                )
                context["venta_lineas"] = [
                    {
                        "nombre": detalle.producto.nombre,
                        "cantidad": detalle.cantidad,
                        "subtotal": (
                            detalle.precio_unitario * detalle.cantidad
                        ),
                    }
                    for detalle in detalles
                ]
        return context


class RegistrarVentaView(View):
    def _volver(self, request, items, error):
        request.session["pos_error"] = {"items": items, "error": error}
        return redirect("pos")

    def post(self, request):
        items = json.loads(request.POST.get("items") or "[]")
        lineas, total = _lineas_del_carrito(items)
        if not lineas:
            return self._volver(
                request, [], "Agregá al menos un producto."
            )

        medios_pago = request.POST.getlist("medio_pago")
        if not medios_pago:
            return self._volver(request, items, "Elegí un medio de pago.")

        try:
            with transaction.atomic():
                venta = Venta.objects.create()
                for linea in lineas:
                    producto = linea["producto"]
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=linea["cantidad"],
                        precio_unitario=producto.precio_venta,
                        costo_unitario=producto.costo,
                    )
                    producto.descontar_stock(linea["cantidad"])
                for medio_pago in medios_pago:
                    valor = request.POST.get(f"importe_{medio_pago}")
                    if valor is None:
                        importe = total
                    else:
                        try:
                            importe = Decimal(valor or "0")
                        except InvalidOperation:
                            importe = Decimal("0")
                    Pago.objects.create(
                        venta=venta,
                        medio_pago=medio_pago,
                        importe=importe,
                    )
                if venta.monto_restante != Decimal("0"):
                    raise _ImportesNoCoinciden
        except _ImportesNoCoinciden:
            return self._volver(
                request,
                items,
                "Los importes deben sumar exactamente el total de la venta.",
            )

        request.session["venta_cobrada"] = venta.pk
        return redirect("pos")
