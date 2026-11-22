from django.contrib import admin
from .models import Venta, DetalleVenta, Pago
# Register your models here.

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha")
    ordering = ("-fecha",)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unitario",
                    "costo_unitario")
    list_filter = ("precio_unitario", "costo_unitario")
    list_select_related = ("venta", "producto")
    search_fields = ("producto__nombre",)
    ordering = ("-venta__fecha",)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("medio_pago", "venta__id", "importe")
    list_filter = ("medio_pago",)
    list_select_related = ("venta",)
    ordering = ("-venta__id",)