from decimal import Decimal

from django.test import TestCase

from .models import Producto, Proveedor


class DescuentoDeStockTests(TestCase):
    def setUp(self):
        proveedor = Proveedor.objects.create(
            razon_social="Distribuidora SA",
            cuit="30-12345678-9",
        )
        self.producto = Producto.objects.create(
            nombre="Yerba mate",
            stock=5,
            precio_venta=Decimal("1500.00"),
            costo=Decimal("1000.00"),
            codigo_barras="7791234567890",
            proveedor=proveedor,
        )

    def test_descontar_stock_descuenta_y_no_baja_de_cero(self):
        self.producto.descontar_stock(2)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)

        self.producto.descontar_stock(5)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)
