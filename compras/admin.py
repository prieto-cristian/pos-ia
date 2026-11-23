from django.contrib import admin

from .models import Compra, DetalleCompra


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "proveedor", "monto_total")
    ordering = ("-fecha",)


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = (
        "compra",
        "producto",
        "cantidad",
        "costo_unitario",
    )
    list_filter = ("costo_unitario",)
    list_select_related = ("compra", "producto")
    search_fields = ("producto__nombre",)
    ordering = ("-compra__fecha",)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ("compra", "producto", "cantidad", "costo_unitario")
        return super().get_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if change:
            cantidad_anterior = DetalleCompra.objects.get(
                pk=obj.pk
            ).cantidad
            obj.producto.stock += obj.cantidad - cantidad_anterior
        else:
            obj.producto.stock += obj.cantidad

        obj.producto.save(update_fields=["stock"])
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        obj.producto.stock -= obj.cantidad
        obj.producto.save(update_fields=["stock"])
        super().delete_model(request, obj)