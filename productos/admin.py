from django.contrib import admin
from .models import Categoria, Proveedor, Producto

class BajaLogicaAdmin(admin.ModelAdmin):
    actions = ["dar_de_baja", "reactivar"]

    @admin.action(description="Dar de baja los registros seleccionados")
    def dar_de_baja(self, request, queryset):
        cantidad = queryset.filter(activo=True).update(activo=False)
        self.message_user(
            request,
            f"{cantidad} registro(s) dado(s) de baja."
        )

    @admin.action(description="Reactivar los registros seleccionados")
    def reactivar(self, request, queryset):
        cantidad = queryset.filter(activo=False).update(activo=True)
        self.message_user(
            request,
            f"{cantidad} registro(s) reactivado(s)."
        )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Categoria)
class CategoriaAdmin(BajaLogicaAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    ordering = ("nombre",)

@admin.register(Proveedor)
class ProveedorAdmin(BajaLogicaAdmin):
    list_display = ("razon_social", "nombre", "telefono", "cuit", "activo")
    list_filter = ("activo",)
    search_fields = ("razon_social", "nombre", "cuit")
    ordering = ("nombre",)

@admin.register(Producto)
class ProductoAdmin(BajaLogicaAdmin):
    list_display = (
        "nombre",
        "stock",
        "stock_minimo",
        "precio_venta",
        "costo",
        "codigo_barras",
        "proveedor",
        "mostrar_categorias",
        "activo"
    )

    list_filter = ("activo", "categorias", "proveedor")
    search_fields = ("nombre", "codigo_barras")
    ordering = ("nombre",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "proveedor":
            kwargs["queryset"] = Proveedor.objects.filter(activo=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "categorias":
            kwargs["queryset"] = Categoria.objects.filter(activo=True)

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    @admin.display(description="Categorías")
    def mostrar_categorias(self, obj):
        return ", ".join(
            categoria.nombre for categoria in obj.categorias.all()
        )