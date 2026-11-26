import html as html_module
import json
import re
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from productos.models import Categoria, Producto, Proveedor
from ventas.templatetags.formato import pesos

from .models import DetalleVenta, Pago, Venta


def _json_script(response, element_id):
    html = response.content.decode()
    patron = (
        rf'<script id="{element_id}" type="application/json">(.*?)</script>'
    )
    coincidencia = re.search(patron, html, re.S)
    return json.loads(coincidencia.group(1)) if coincidencia else None


def catalogo_enviado(response):
    return _json_script(response, "pos-catalogo")


def items_iniciales(response):
    return _json_script(response, "pos-initial-items")


def items_enviados(response):
    html = response.content.decode()
    coincidencia = re.search(
        r'id="items-input"\s+value="([^"]*)"', html, re.S
    )
    if not coincidencia:
        return None
    return json.loads(html_module.unescape(coincidencia.group(1)))


class CajaBaseTests(TestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            razon_social="Distribuidora SA",
            cuit="30-12345678-9",
        )
        self.almacen = Categoria.objects.create(nombre="Almacén")
        self.bebidas = Categoria.objects.create(nombre="Bebidas")
        self.yerba = Producto.objects.create(
            nombre="Yerba mate",
            stock=10,
            stock_minimo=2,
            precio_venta=Decimal("1500.00"),
            costo=Decimal("1000.00"),
            codigo_barras="7791234567890",
            proveedor=self.proveedor,
        )
        self.yerba.categorias.add(self.almacen)
        self.cafe = Producto.objects.create(
            nombre="Café molido",
            stock=8,
            stock_minimo=2,
            precio_venta=Decimal("2500.00"),
            costo=Decimal("1800.00"),
            codigo_barras="7791234567891",
            proveedor=self.proveedor,
        )
        self.cafe.categorias.add(self.bebidas)

    def datos_de_venta(self, items, pagos=()):
        datos = {"items": json.dumps(items)}
        if pagos:
            datos["medio_pago"] = [medio for medio, _ in pagos]
            for medio, importe in pagos:
                datos[f"importe_{medio}"] = str(importe)
        return datos


class RaizTests(TestCase):
    def test_la_raiz_lleva_a_la_caja(self):
        response = self.client.get("/")

        self.assertRedirects(response, reverse("pos"))


class FormatoPesosTests(TestCase):
    def test_formatea_miles_y_centavos_en_pesos(self):
        self.assertEqual(pesos(Decimal("10540")), "$ 10.540")
        self.assertEqual(pesos(Decimal("10540.50")), "$ 10.540,50")
        self.assertEqual(pesos(Decimal("0")), "$ 0")
        self.assertEqual(pesos(Decimal("-1234.50")), "-$ 1.234,50")


class CajaTests(CajaBaseTests):
    def test_caja_muestra_buscador_carrito_vacio_y_medios_de_pago(self):
        response = self.client.get(reverse("pos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="busqueda"')
        self.assertContains(response, 'id="items-input"')
        self.assertEqual(items_enviados(response), [])
        self.assertEqual(items_iniciales(response), [])
        self.assertContains(response, "Carrito vacío")
        self.assertContains(response, 'id="form-pago"')

        medios = re.findall(
            r'data-method="([A-Z]+)"', response.content.decode()
        )
        self.assertEqual(
            medios,
            [
                Pago.MedioPago.EFECTIVO.value,
                Pago.MedioPago.TARJETA.value,
                Pago.MedioPago.QR.value,
                Pago.MedioPago.TRANSFERENCIA.value,
            ],
        )

    def test_caja_incluye_el_catalogo_activo_y_excluye_inactivos(self):
        inactivo = Producto.objects.create(
            nombre="Producto discontinuado",
            stock=5,
            precio_venta=Decimal("800.00"),
            costo=Decimal("500.00"),
            codigo_barras="7790000000001",
            proveedor=self.proveedor,
            activo=False,
        )

        response = self.client.get(reverse("pos"))
        catalogo = catalogo_enviado(response)

        self.assertEqual(
            {producto["nombre"] for producto in catalogo},
            {"Yerba mate", "Café molido"},
        )
        yerba = next(
            producto
            for producto in catalogo
            if producto["id"] == self.yerba.pk
        )
        self.assertEqual(yerba["precio"], "1500.00")
        self.assertEqual(yerba["stock"], 10)
        self.assertEqual(yerba["categoria_slug"], "almacen")
        self.assertEqual(yerba["codigo"], self.yerba.codigo_barras)

        html = response.content.decode()
        self.assertIn(f'data-product-id="{self.yerba.pk}"', html)
        self.assertIn(f'data-product-id="{self.cafe.pk}"', html)
        self.assertNotIn(f'data-product-id="{inactivo.pk}"', html)
        self.assertNotIn("Producto discontinuado", html)

    def test_caja_muestra_conteo_por_categoria_y_total(self):
        response = self.client.get(reverse("pos"))
        html = response.content.decode()

        self.assertContains(response, 'data-cat="almacen"')
        self.assertContains(response, 'data-cat="bebidas"')
        self.assertRegex(
            html,
            r'data-cat="almacen"[\s\S]*?<span class="tab-count">1</span>',
        )
        self.assertRegex(
            html,
            r'data-cat="bebidas"[\s\S]*?<span class="tab-count">1</span>',
        )
        self.assertContains(response, ">2</span>")
        self.assertContains(response, "Activá JavaScript")

    def test_caja_muestra_el_precio_y_la_etiqueta_de_cada_producto(self):
        response = self.client.get(reverse("pos"))

        self.assertContains(response, pesos(self.yerba.precio_venta))
        self.assertContains(response, pesos(self.cafe.precio_venta))
        self.assertContains(
            response,
            f'aria-label="Agregar {self.yerba.nombre} al carrito"',
        )
        self.assertContains(response, 'title="Stock disponible: 10 unidades"')

    def test_caja_incluye_la_barra_compacta_de_carrito(self):
        response = self.client.get(reverse("pos"))

        self.assertContains(response, 'id="mobile-cart-bar"')
        self.assertContains(response, 'href="#carrito"')
        self.assertContains(response, 'id="carrito"')


class RegistrarVentaTests(CajaBaseTests):
    def test_registrar_venta_crea_detalles_y_un_pago_por_el_total(self):
        items = [
            {"producto_id": self.yerba.pk, "cantidad": 2},
            {"producto_id": self.cafe.pk, "cantidad": 1},
        ]

        response = self.client.post(
            reverse("registrar_venta"),
            self.datos_de_venta(
                items, [(Pago.MedioPago.EFECTIVO, "5500.00")]
            ),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("pos"))
        self.assertEqual(Venta.objects.count(), 1)

        venta = Venta.objects.get()
        self.assertEqual(venta.detalles.count(), 2)
        detalle_yerba = venta.detalles.get(producto=self.yerba)
        self.assertEqual(detalle_yerba.cantidad, 2)
        self.assertEqual(detalle_yerba.precio_unitario, Decimal("1500.00"))
        self.assertEqual(detalle_yerba.costo_unitario, Decimal("1000.00"))
        detalle_cafe = venta.detalles.get(producto=self.cafe)
        self.assertEqual(detalle_cafe.cantidad, 1)
        self.assertEqual(detalle_cafe.precio_unitario, Decimal("2500.00"))
        self.assertEqual(detalle_cafe.costo_unitario, Decimal("1800.00"))

        self.assertEqual(venta.pagos.count(), 1)
        pago = venta.pagos.get()
        self.assertEqual(pago.medio_pago, Pago.MedioPago.EFECTIVO)
        self.assertEqual(pago.importe, Decimal("5500.00"))
        self.assertEqual(venta.total_pagado, Decimal("5500.00"))

        self.yerba.refresh_from_db()
        self.cafe.refresh_from_db()
        self.assertEqual(self.yerba.stock, 8)
        self.assertEqual(self.cafe.stock, 7)

        page = self.client.get(reverse("pos"))
        self.assertContains(page, f"Venta N°{venta.pk}")
        self.assertContains(page, 'id="sale-success"')
        self.assertContains(page, "Cobrada")
        self.assertContains(page, pesos(Decimal("5500.00")))
        self.assertContains(page, "Efectivo")
        self.assertContains(page, 'class="success-lines"')
        self.assertContains(page, "2×")
        self.assertContains(page, "1×")
        self.assertContains(page, pesos(Decimal("3000.00")))
        self.assertEqual(items_enviados(page), [])

    def test_registrar_venta_con_varios_medios_guarda_cada_importe(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 2}]

        response = self.client.post(
            reverse("registrar_venta"),
            self.datos_de_venta(
                items,
                [
                    (Pago.MedioPago.EFECTIVO, "2000.00"),
                    (Pago.MedioPago.TARJETA, "1000.00"),
                ],
            ),
        )

        self.assertEqual(response.status_code, 302)
        venta = Venta.objects.get()
        self.assertEqual(
            {
                pago.medio_pago: pago.importe
                for pago in venta.pagos.all()
            },
            {
                Pago.MedioPago.EFECTIVO: Decimal("2000.00"),
                Pago.MedioPago.TARJETA: Decimal("1000.00"),
            },
        )
        self.assertEqual(venta.monto_restante, Decimal("0.00"))

        page = self.client.get(reverse("pos"))
        self.assertContains(page, "Efectivo")
        self.assertContains(page, "Tarjeta")
        self.assertContains(page, pesos(Decimal("2000.00")))
        self.assertContains(page, pesos(Decimal("1000.00")))

    def test_el_ticket_abrevia_transferencia_sin_perder_la_etiqueta(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 1}]

        self.client.post(
            reverse("registrar_venta"),
            self.datos_de_venta(
                items, [(Pago.MedioPago.TRANSFERENCIA, "1500.00")]
            ),
        )
        page = self.client.get(reverse("pos"))

        self.assertContains(page, "Transf.")
        self.assertContains(page, "Pagos: Transferencia")

    def test_registrar_venta_sin_importe_asigna_el_total_al_unico_medio(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 1}]
        datos = {
            "items": json.dumps(items),
            "medio_pago": Pago.MedioPago.QR.value,
        }

        response = self.client.post(reverse("registrar_venta"), datos)

        self.assertEqual(response.status_code, 302)
        pago = Pago.objects.get()
        self.assertEqual(pago.importe, Decimal("1500.00"))

    def test_importes_que_no_suman_el_total_no_registran_nada(self):
        items = [
            {"producto_id": self.yerba.pk, "cantidad": 2},
            {"producto_id": self.cafe.pk, "cantidad": 1},
        ]

        response = self.client.post(
            reverse("registrar_venta"),
            self.datos_de_venta(
                items,
                [
                    (Pago.MedioPago.EFECTIVO, "3000.00"),
                    (Pago.MedioPago.TARJETA, "2000.00"),
                ],
            ),
        )

        self.assertEqual(response.status_code, 302)
        page = self.client.get(reverse("pos"))
        self.assertContains(
            page,
            "Los importes deben sumar exactamente el total de la venta",
        )
        self.assertEqual(items_enviados(page), items)
        self.assertEqual(Venta.objects.count(), 0)
        self.assertEqual(DetalleVenta.objects.count(), 0)
        self.assertEqual(Pago.objects.count(), 0)

        self.yerba.refresh_from_db()
        self.cafe.refresh_from_db()
        self.assertEqual(self.yerba.stock, 10)
        self.assertEqual(self.cafe.stock, 8)

    def test_registrar_sin_productos_avisa_y_no_crea_venta(self):
        response = self.client.post(
            reverse("registrar_venta"),
            {
                "items": "[]",
                "medio_pago": Pago.MedioPago.EFECTIVO.value,
            },
        )

        self.assertEqual(response.status_code, 302)
        page = self.client.get(reverse("pos"))
        self.assertContains(page, "Agregá al menos un producto")
        self.assertContains(page, "Carrito vacío")
        self.assertEqual(Venta.objects.count(), 0)
        self.assertEqual(Pago.objects.count(), 0)

    def test_registrar_sin_medio_de_pago_avisa_y_conserva_el_carrito(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 1}]

        response = self.client.post(
            reverse("registrar_venta"),
            {"items": json.dumps(items)},
        )

        self.assertEqual(response.status_code, 302)
        page = self.client.get(reverse("pos"))
        self.assertContains(page, "Elegí un medio de pago")
        self.assertEqual(items_enviados(page), items)
        self.assertEqual(Venta.objects.count(), 0)
        self.assertEqual(Pago.objects.count(), 0)

    def test_registrar_venta_deja_stock_en_cero_si_supera_el_disponible(
        self,
    ):
        self.yerba.stock = 1
        self.yerba.save(update_fields=["stock"])
        items = [{"producto_id": self.yerba.pk, "cantidad": 3}]

        response = self.client.post(
            reverse("registrar_venta"),
            self.datos_de_venta(
                items, [(Pago.MedioPago.EFECTIVO, "4500.00")]
            ),
        )

        self.assertEqual(response.status_code, 302)
        self.yerba.refresh_from_db()
        self.assertEqual(self.yerba.stock, 0)
        self.assertEqual(Venta.objects.get().detalles.get().cantidad, 3)

    def test_la_confirmacion_se_muestra_una_sola_vez(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 1}]
        self.client.post(
            reverse("registrar_venta"),
            self.datos_de_venta(
                items, [(Pago.MedioPago.EFECTIVO, "1500.00")]
            ),
        )
        venta = Venta.objects.get()

        primera = self.client.get(reverse("pos"))
        segunda = self.client.get(reverse("pos"))

        self.assertContains(primera, f"Venta N°{venta.pk}")
        self.assertNotContains(segunda, f"Venta N°{venta.pk}")
        self.assertEqual(Venta.objects.count(), 1)


class CarritoRestauradoTests(CajaBaseTests):
    def test_un_error_devuelve_las_lineas_y_los_totales_del_carrito(self):
        items = [
            {"producto_id": self.yerba.pk, "cantidad": 2},
            {"producto_id": self.cafe.pk, "cantidad": 1},
        ]

        response = self.client.post(
            reverse("registrar_venta"),
            self.datos_de_venta(items),
        )

        self.assertEqual(response.status_code, 302)
        page = self.client.get(reverse("pos"))

        self.assertContains(page, "Elegí un medio de pago")
        self.assertEqual(items_enviados(page), items)
        self.assertEqual(items_iniciales(page), items)
        self.assertContains(page, f'data-producto-id="{self.yerba.pk}"')
        self.assertContains(page, f'data-producto-id="{self.cafe.pk}"')
        self.assertContains(page, 'data-cantidad="2"')
        self.assertContains(page, 'data-cantidad="1"')
        self.assertContains(page, f"{pesos(Decimal('1500.00'))} c/u")
        self.assertContains(page, pesos(Decimal("3000.00")))
        self.assertContains(page, pesos(Decimal("2500.00")))
        self.assertContains(page, pesos(Decimal("5500.00")))
        self.assertContains(
            page,
            "Escaneá un código o elegí un producto del catálogo",
            count=None,
        )

    def test_el_aviso_de_error_se_muestra_una_sola_vez(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 1}]
        self.client.post(
            reverse("registrar_venta"),
            {"items": json.dumps(items)},
        )

        primera = self.client.get(reverse("pos"))
        segunda = self.client.get(reverse("pos"))

        self.assertContains(primera, "Elegí un medio de pago")
        self.assertNotContains(segunda, "Elegí un medio de pago")
        self.assertEqual(items_enviados(segunda), [])


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
