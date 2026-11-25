from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from compras.models import Compra
from ventas.models import Venta

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


class PoblarDemoTests(TestCase):
    def test_poblar_demo_genera_datos_consistentes(self):
        salida = StringIO()

        call_command(
            "poblar_demo",
            "--reset",
            "--ventas",
            "40",
            "--dias",
            "60",
            "--seed",
            "7",
            stdout=salida,
        )

        self.assertEqual(Producto.objects.count(), 64)
        self.assertTrue(Compra.objects.exists())
        self.assertTrue(Venta.objects.exists())
        self.assertFalse(Producto.objects.filter(stock__lt=0).exists())

        for venta in Venta.objects.prefetch_related("detalles", "pagos"):
            self.assertLessEqual(venta.total_pagado, venta.monto_total)
