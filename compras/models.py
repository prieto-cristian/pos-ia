from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum

from productos.models import Producto, Proveedor


class Compra(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="compras",
    )

    @property
    def monto_total(self):
        return self.detalles.aggregate(
            total=Sum(F("costo_unitario") * F("cantidad"))
        )["total"] or Decimal("0")

    def __str__(self):
        return f"Compra N°{self.pk}"

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-fecha"]


class DetalleCompra(models.Model):
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles_compra",
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    def __str__(self):
        return f"Item {self.pk} de la compra {self.compra.pk}"

    class Meta:
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"