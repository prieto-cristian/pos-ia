from django.db import models
from django.core.validators import MinValueValidator
from productos.models import Producto

# Create your models here.
class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta N°{self.pk}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha"]


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, 
                                 related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, 
                                    related_name="detalles")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Item {self.pk} de la venta {self.venta.pk}"

    class Meta:
        verbose_name = "Item de venta"
        verbose_name_plural = "Items de venta"


class Pago(models.Model):
    class MedioPago(models.TextChoices):
        TARJETA = "TARJETA", "Tarjeta"
        QR = "QR", "QR"
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
    
    medio_pago = models.CharField(max_length=50, choices=MedioPago.choices)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, 
                              related_name="pagos")
    importe = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.medio_pago}"

    class Meta:
        verbose_name = "Pago"                
        verbose_name_plural = "Pagos"
        