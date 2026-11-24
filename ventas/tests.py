import json
from decimal import Decimal
from html.parser import HTMLParser

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from productos.models import Producto, Proveedor
from .models import DetalleVenta, Pago, Venta


class _ItemsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.value = None

    def handle_starttag(self, tag, attrs):
        if tag != "input":
            return
        attrs = dict(attrs)
        if attrs.get("name") == "items":
            self.value = attrs.get("value")


def items_enviados(response):
    parser = _ItemsParser()
    parser.feed(response.content.decode())
    return json.loads(parser.value)


class PuntoDeVentaTests(TestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            razon_social="Distribuidora SA",
            cuit="30-12345678-9",
        )
        self.producto = Producto.objects.create(
            nombre="Yerba mate",
            stock=10,
            precio_venta=Decimal("1500.00"),
            costo=Decimal("1000.00"),
            codigo_barras="7791234567890",
            proveedor=self.proveedor,
        )
        self.otro_producto = Producto.objects.create(
            nombre="Café molido",
            stock=8,
            precio_venta=Decimal("2500.00"),
            costo=Decimal("1800.00"),
            codigo_barras="7791234567891",
            proveedor=self.proveedor,
        )

    def test_pos_muestra_codigo_de_barras_carrito_vacio_y_medio_de_pago(self):
        response = self.client.get(reverse("pos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="codigo_barras"')
        self.assertContains(response, 'name="items"')
        self.assertContains(response, 'value="[]"')
        self.assertContains(response, "Carrito vacío")
        self.assertContains(response, 'name="medio_pago"')
        for medio in Pago.MedioPago:
            self.assertContains(response, f'value="{medio.value}"')

    def test_agregar_codigo_exacto_suma_el_producto_al_carrito(self):
        response = self.client.post(
            reverse("agregar_al_carrito"),
            {
                "codigo_barras": self.producto.codigo_barras,
                "items": "[]",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.producto.nombre)
        self.assertContains(response, f'data-producto-id="{self.producto.pk}"')
        self.assertContains(response, 'data-cantidad="1"')
        self.assertRegex(response.content.decode(), r"Total: \$ 1500[.,]00")
        self.assertContains(response, 'name="codigo_barras"')
        self.assertEqual(
            items_enviados(response),
            [{"producto_id": self.producto.pk, "cantidad": 1}],
        )

    def test_agregar_el_mismo_producto_lo_acumula_en_una_sola_linea(self):
        primera = self.client.post(
            reverse("agregar_al_carrito"),
            {
                "codigo_barras": self.producto.codigo_barras,
                "items": "[]",
            },
        )
        items = items_enviados(primera)

        response = self.client.post(
            reverse("agregar_al_carrito"),
            {
                "codigo_barras": self.producto.codigo_barras,
                "items": json.dumps(items),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            items_enviados(response),
            [{"producto_id": self.producto.pk, "cantidad": 2}],
        )
        self.assertContains(response, 'data-cantidad="2"')
        self.assertEqual(
            response.content.decode().count(
                f'data-producto-id="{self.producto.pk}"'
            ),
            1,
        )
        self.assertRegex(response.content.decode(), r"Total: \$ 3000[.,]00")

    def test_codigo_desconocido_muestra_no_encontrado_y_no_toca_el_carrito(
        self,
    ):
        primera = self.client.post(
            reverse("agregar_al_carrito"),
            {
                "codigo_barras": self.producto.codigo_barras,
                "items": "[]",
            },
        )
        items = items_enviados(primera)

        response = self.client.post(
            reverse("agregar_al_carrito"),
            {
                "codigo_barras": "0000000000000",
                "items": json.dumps(items),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Producto no encontrado")
        self.assertContains(response, 'name="codigo_barras"')
        self.assertEqual(items_enviados(response), items)
        self.assertContains(response, 'data-cantidad="1"')
        self.assertRegex(response.content.decode(), r"Total: \$ 1500[.,]00")

    def test_codigo_de_producto_inactivo_muestra_no_encontrado_y_no_toca_el_carrito(
        self,
    ):
        inactivo = Producto.objects.create(
            nombre="Producto discontinuado",
            stock=5,
            precio_venta=Decimal("800.00"),
            costo=Decimal("500.00"),
            codigo_barras="7790000000001",
            proveedor=self.proveedor,
            activo=False,
        )
        primera = self.client.post(
            reverse("agregar_al_carrito"),
            {
                "codigo_barras": self.producto.codigo_barras,
                "items": "[]",
            },
        )
        items = items_enviados(primera)

        response = self.client.post(
            reverse("agregar_al_carrito"),
            {
                "codigo_barras": inactivo.codigo_barras,
                "items": json.dumps(items),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Producto no encontrado")
        self.assertNotContains(response, inactivo.nombre)
        self.assertEqual(items_enviados(response), items)
        self.assertContains(response, 'data-cantidad="1"')
        self.assertRegex(response.content.decode(), r"Total: \$ 1500[.,]00")

    def test_registrar_venta_crea_venta_detalles_y_un_pago_por_el_total(
        self,
    ):
        items = [
            {"producto_id": self.producto.pk, "cantidad": 2},
            {"producto_id": self.otro_producto.pk, "cantidad": 1},
        ]

        response = self.client.post(
            reverse("registrar_venta"),
            {
                "items": json.dumps(items),
                "medio_pago": Pago.MedioPago.EFECTIVO,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 1)
        venta = Venta.objects.get()
        self.assertEqual(venta.detalles.count(), 2)

        detalle_yerba = venta.detalles.get(producto=self.producto)
        self.assertEqual(detalle_yerba.cantidad, 2)
        self.assertEqual(detalle_yerba.precio_unitario, Decimal("1500.00"))
        self.assertEqual(detalle_yerba.costo_unitario, Decimal("1000.00"))

        detalle_cafe = venta.detalles.get(producto=self.otro_producto)
        self.assertEqual(detalle_cafe.cantidad, 1)
        self.assertEqual(detalle_cafe.precio_unitario, Decimal("2500.00"))
        self.assertEqual(detalle_cafe.costo_unitario, Decimal("1800.00"))

        self.assertEqual(venta.pagos.count(), 1)
        pago = venta.pagos.get()
        self.assertEqual(pago.medio_pago, Pago.MedioPago.EFECTIVO)
        self.assertEqual(pago.importe, Decimal("5500.00"))
        self.assertEqual(venta.monto_total, Decimal("5500.00"))

    def test_registrar_venta_descuenta_el_stock_de_cada_producto(self):
        items = [
            {"producto_id": self.producto.pk, "cantidad": 2},
            {"producto_id": self.otro_producto.pk, "cantidad": 1},
        ]

        response = self.client.post(
            reverse("registrar_venta"),
            {
                "items": json.dumps(items),
                "medio_pago": Pago.MedioPago.TARJETA,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.producto.refresh_from_db()
        self.otro_producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 8)
        self.assertEqual(self.otro_producto.stock, 7)

    def test_registrar_venta_deja_stock_en_cero_si_la_cantidad_supera_el_disponible(
        self,
    ):
        self.producto.stock = 1
        self.producto.save(update_fields=["stock"])
        items = [{"producto_id": self.producto.pk, "cantidad": 3}]

        response = self.client.post(
            reverse("registrar_venta"),
            {
                "items": json.dumps(items),
                "medio_pago": Pago.MedioPago.QR,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)

        venta = Venta.objects.get()
        detalle = venta.detalles.get()
        self.assertEqual(detalle.cantidad, 3)

    def test_registrar_venta_muestra_el_numero_y_deja_el_carrito_vacio(self):
        items = [{"producto_id": self.producto.pk, "cantidad": 1}]

        response = self.client.post(
            reverse("registrar_venta"),
            {
                "items": json.dumps(items),
                "medio_pago": Pago.MedioPago.EFECTIVO,
            },
        )

        venta = Venta.objects.get()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Venta N°{venta.pk}")
        self.assertContains(response, "Carrito vacío")
        self.assertEqual(items_enviados(response), [])
        self.assertNotContains(response, self.producto.nombre)
        self.assertContains(response, 'name="codigo_barras"')

    def test_registrar_sin_productos_avisa_y_no_crea_venta(self):
        response = self.client.post(
            reverse("registrar_venta"),
            {
                "items": "[]",
                "medio_pago": Pago.MedioPago.EFECTIVO,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Agregá al menos un producto")
        self.assertContains(response, "Carrito vacío")
        self.assertEqual(Venta.objects.count(), 0)
        self.assertEqual(Pago.objects.count(), 0)

    def test_registrar_sin_medio_de_pago_avisa_y_no_crea_venta(self):
        items = [{"producto_id": self.producto.pk, "cantidad": 1}]

        response = self.client.post(
            reverse("registrar_venta"),
            {"items": json.dumps(items)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Elegí un medio de pago")
        self.assertEqual(Venta.objects.count(), 0)
        self.assertEqual(Pago.objects.count(), 0)


class DetalleVentaAdminTests(TestCase):
    def setUp(self):
        proveedor = Proveedor.objects.create(
            razon_social="Distribuidora SA",
            cuit="30-12345678-9",
        )
        self.producto = Producto.objects.create(
            nombre="Yerba mate",
            stock=1,
            precio_venta=Decimal("1500.00"),
            costo=Decimal("1000.00"),
            codigo_barras="7791234567890",
            proveedor=proveedor,
        )
        self.venta = Venta.objects.create()
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        self.client.force_login(self.user)

    def test_admin_alta_de_detalle_usa_el_descuento_con_piso_en_cero(self):
        response = self.client.post(
            reverse("admin:ventas_detalleventa_add"),
            {
                "venta": self.venta.pk,
                "producto": self.producto.pk,
                "cantidad": 3,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)

        detalle = DetalleVenta.objects.get()
        self.assertEqual(detalle.cantidad, 3)
        self.assertEqual(detalle.precio_unitario, Decimal("1500.00"))
        self.assertEqual(detalle.costo_unitario, Decimal("1000.00"))
