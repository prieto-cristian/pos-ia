import json
import unicodedata
from decimal import Decimal

from django.db import transaction
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from productos.models import Producto

from .models import DetalleVenta, Pago, Venta


def _lineas_del_carrito(items):
    lineas = []
    total = Decimal("0")
    for item in items:
        producto = Producto.objects.get(pk=item["producto_id"])
        subtotal = producto.precio_venta * item["cantidad"]
        total += subtotal
        lineas.append({
            "producto": producto,
            "cantidad": item["cantidad"],
            "subtotal": subtotal,
        })
    return lineas, total


def _contexto_pos(items):
    lineas, total = _lineas_del_carrito(items)
    return {
        "medios_pago": Pago.MedioPago.choices,
        "items": json.dumps(items),
        "lineas": lineas,
        "total": total,
    }


def _normalizar(texto):
    sin_tildes = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caracter)
    )
    return sin_tildes.casefold()


def _agregar_al_carrito(items, producto):
    for item in items:
        if item["producto_id"] == producto.pk:
            item["cantidad"] += 1
            break
    else:
        items.append({"producto_id": producto.pk, "cantidad": 1})


def _resultados_de_busqueda(termino):
    if not termino:
        return []
    return [
        producto
        for producto in Producto.objects.filter(activo=True)
        if termino in _normalizar(producto.nombre)
    ]


class PosView(TemplateView):
    template_name = "ventas/pos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_contexto_pos([]))
        return context


class AgregarAlCarritoView(View):
    def post(self, request):
        items = json.loads(request.POST.get("items") or "[]")
        try:
            producto = Producto.objects.get(
                codigo_barras=request.POST["codigo_barras"],
                activo=True,
            )
        except Producto.DoesNotExist:
            contexto = _contexto_pos(items)
            contexto["error"] = "Producto no encontrado."
            return render(request, "ventas/pos.html", contexto)

        _agregar_al_carrito(items, producto)

        return render(request, "ventas/pos.html", _contexto_pos(items))


class AgregarDesdeResultadosView(View):
    def post(self, request):
        items = json.loads(request.POST.get("items") or "[]")
        producto = Producto.objects.get(
            pk=request.POST["producto_id"],
            activo=True,
        )
        _agregar_al_carrito(items, producto)

        termino = _normalizar(request.POST.get("nombre", "")).strip()
        contexto = _contexto_pos(items)
        resultados = _resultados_de_busqueda(termino)
        contexto["resultados"] = resultados
        contexto["sin_resultados"] = bool(termino) and not resultados
        contexto["nombre"] = termino
        return render(request, "ventas/pos.html", contexto)


class BuscarProductosView(View):
    def post(self, request):
        items = json.loads(request.POST.get("items") or "[]")
        termino = _normalizar(request.POST.get("nombre", "")).strip()
        contexto = _contexto_pos(items)
        contexto["nombre"] = termino
        resultados = _resultados_de_busqueda(termino)
        contexto["resultados"] = resultados
        contexto["sin_resultados"] = bool(termino) and not resultados
        return render(request, "ventas/pos.html", contexto)


class RegistrarVentaView(View):
    def post(self, request):
        items = json.loads(request.POST.get("items") or "[]")
        lineas, total = _lineas_del_carrito(items)
        if not lineas:
            contexto = _contexto_pos([])
            contexto["error"] = "Agregá al menos un producto."
            return render(request, "ventas/pos.html", contexto)

        medio_pago = request.POST.get("medio_pago")
        if not medio_pago:
            contexto = _contexto_pos(items)
            contexto["error"] = "Elegí un medio de pago."
            return render(request, "ventas/pos.html", contexto)

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
            Pago.objects.create(
                venta=venta,
                medio_pago=medio_pago,
                importe=total,
            )

        contexto = _contexto_pos([])
        contexto["venta"] = venta
        return render(request, "ventas/pos.html", contexto)
