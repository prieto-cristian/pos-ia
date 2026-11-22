from django.contrib import admin
from .models import Venta, DetalleVenta, Pago
# Register your models here.

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "monto_total", "total_pagado")
    ordering = ("-fecha",)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unitario",
                    "costo_unitario")
    list_filter = ("precio_unitario", "costo_unitario")
    list_select_related = ("venta", "producto")
    search_fields = ("producto__nombre",)
    ordering = ("-venta__fecha",)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ("venta", "producto", "cantidad")
        return super().get_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.precio_unitario = obj.producto.precio_venta
            obj.costo_unitario = obj.producto.costo
        super().save_model(request, obj, form, change)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("medio_pago", "venta__id", "importe")
    list_filter = ("medio_pago",)
    list_select_related = ("venta",)
    ordering = ("-venta__id",)