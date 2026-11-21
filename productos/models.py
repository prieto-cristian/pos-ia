from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]


class Proveedor(models.Model):
    razon_social = models.CharField(max_length=150)
    nombre = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    cuit = models.CharField(max_length=13, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.razon_social

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["razon_social"]


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    codigo_barras = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="productos"
    )

    categorias = models.ManyToManyField(
        Categoria,
        related_name="productos"
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]
