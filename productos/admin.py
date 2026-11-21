from django.contrib import admin
from .models import Categoria, Proveedor, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    ordering = ("nombre",)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "nombre", "telefono", "cuit", "activo")
    list_filter = ("activo",)
    search_fields = ("razon_social", "nombre", "cuit")
    ordering = ("nombre",)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):  
    list_display = ("nombre", "stock", "stock_minimo", "precio_venta", "costo", "codigo_barras", "proveedor", "categoria", "activo")
    list_filter = ("activo", "categoria", "proveedor")
    search_fields = ("nombre", "codigo_barras")
    ordering = ("nombre",)