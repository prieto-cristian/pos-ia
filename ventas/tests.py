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


class _FormulariosParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.formularios = []
        self._actual = None
        self._en_boton = False
        self._formaction_boton = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self._actual = {
                "action": attrs.get("action"),
                "campos": {},
                "botones": [],
                "formactions": {},
            }
            self.formularios.append(self._actual)
        elif tag == "input" and self._actual is not None:
            nombre = attrs.get("name")
            if nombre:
                self._actual["campos"][nombre] = attrs.get("value")
        elif tag == "button" and self._actual is not None:
            self._en_boton = True
            self._formaction_boton = attrs.get("formaction")

    def handle_data(self, data):
        if self._en_boton and self._actual is not None and data.strip():
            texto = data.strip()
            self._actual["botones"].append(texto)
            if self._formaction_boton:
                self._actual["formactions"][texto] = self._formaction_boton

    def handle_endtag(self, tag):
        if tag == "button":
            self._en_boton = False
            self._formaction_boton = None
        elif tag == "form":
            self._actual = None
            self._en_boton = False


class _FilasCarritoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.filas = {}
        self._producto_id = None
        self._celda = None
        self._en_formulario = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr" and attrs.get("data-producto-id"):
            self._producto_id = attrs["data-producto-id"]
            self.filas[self._producto_id] = []
        elif tag == "td" and self._producto_id is not None:
            self._celda = []
        elif tag == "form":
            self._en_formulario = True
        elif tag == "input" and self._celda is not None:
            if attrs.get("name") == "cantidad":
                self._celda.append(attrs.get("value", ""))

    def handle_data(self, data):
        if self._celda is not None and not self._en_formulario:
            self._celda.append(data)

    def handle_endtag(self, tag):
        if tag == "form":
            self._en_formulario = False
        elif tag == "td" and self._celda is not None:
            self.filas[self._producto_id].append(
                " ".join("".join(self._celda).split())
            )
            self._celda = None
        elif tag == "tr" and self._producto_id is not None:
            self._producto_id = None


class _CamposDePagoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.medios = set()
        self.importes = set()

    def handle_starttag(self, tag, attrs):
        if tag != "input":
            return
        attrs = dict(attrs)
        if (
            attrs.get("type") == "checkbox"
            and attrs.get("name") == "medio_pago"
        ):
            self.medios.add(attrs.get("value"))
        if attrs.get("name", "").startswith("importe_"):
            self.importes.add(attrs["name"])


def items_enviados(response):
    parser = _ItemsParser()
    parser.feed(response.content.decode())
    return json.loads(parser.value)


def filas_del_carrito(response):
    parser = _FilasCarritoParser()
    parser.feed(response.content.decode())
    return parser.filas


def formularios_de_alta_desde_resultados(response):
    parser = _FormulariosParser()
    parser.feed(response.content.decode())
    return [
        formulario
        for formulario in parser.formularios
        if formulario["action"] == reverse("agregar_desde_resultados")
    ]


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

    def test_registrar_venta_con_varios_medios_guarda_un_pago_por_medio_con_su_importe(
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
                "medio_pago": [
                    Pago.MedioPago.EFECTIVO,
                    Pago.MedioPago.TARJETA,
                ],
                "importe_EFECTIVO": "3000.00",
                "importe_TARJETA": "2500.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 1)
        venta = Venta.objects.get()
        self.assertEqual(
            {
                pago.medio_pago: pago.importe
                for pago in venta.pagos.all()
            },
            {
                Pago.MedioPago.EFECTIVO: Decimal("3000.00"),
                Pago.MedioPago.TARJETA: Decimal("2500.00"),
            },
        )
        self.assertEqual(venta.total_pagado, Decimal("5500.00"))
        self.assertEqual(venta.monto_restante, Decimal("0.00"))

    def test_registrar_venta_con_importes_que_no_suman_el_total_avisa_y_no_registra_nada(
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
                "medio_pago": [
                    Pago.MedioPago.EFECTIVO,
                    Pago.MedioPago.TARJETA,
                ],
                "importe_EFECTIVO": "3000.00",
                "importe_TARJETA": "2000.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Los importes deben sumar exactamente el total de la venta",
        )
        self.assertEqual(Venta.objects.count(), 0)
        self.assertEqual(DetalleVenta.objects.count(), 0)
        self.assertEqual(Pago.objects.count(), 0)
        self.producto.refresh_from_db()
        self.otro_producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(self.otro_producto.stock, 8)

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


class CarritoEnPantallaTests(TestCase):
    def setUp(self):
        proveedor = Proveedor.objects.create(
            razon_social="Distribuidora SA",
            cuit="30-12345678-9",
        )
        self.yerba = Producto.objects.create(
            nombre="Yerba mate",
            stock=10,
            precio_venta=Decimal("1500.00"),
            costo=Decimal("1000.00"),
            codigo_barras="7791234567890",
            proveedor=proveedor,
        )
        self.cafe = Producto.objects.create(
            nombre="Café molido",
            stock=8,
            precio_venta=Decimal("2500.00"),
            costo=Decimal("1800.00"),
            codigo_barras="7791234567891",
            proveedor=proveedor,
        )

    def test_carrito_muestra_nombre_cantidad_precio_unitario_e_importe_de_cada_linea(
        self,
    ):
        items = [
            {"producto_id": self.yerba.pk, "cantidad": 2},
            {"producto_id": self.cafe.pk, "cantidad": 3},
        ]

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "", "items": json.dumps(items)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Precio unitario")
        self.assertContains(response, "Importe")
        self.assertEqual(
            filas_del_carrito(response),
            {
                str(self.yerba.pk): [
                    "Yerba mate",
                    "2",
                    "$ 1500,00",
                    "$ 3000,00",
                ],
                str(self.cafe.pk): [
                    "Café molido",
                    "3",
                    "$ 2500,00",
                    "$ 7500,00",
                ],
            },
        )

    def test_total_del_carrito_es_la_suma_de_los_importes_de_las_lineas(
        self,
    ):
        items = [
            {"producto_id": self.yerba.pk, "cantidad": 2},
            {"producto_id": self.cafe.pk, "cantidad": 3},
        ]

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "", "items": json.dumps(items)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total: $ 10500,00")

    def test_actualizar_cantidad_recalcula_el_importe_de_la_linea_y_el_total(
        self,
    ):
        items = [
            {"producto_id": self.yerba.pk, "cantidad": 2},
            {"producto_id": self.cafe.pk, "cantidad": 1},
        ]

        response = self.client.post(
            reverse("actualizar_cantidad"),
            {
                "items": json.dumps(items),
                "producto_id": self.yerba.pk,
                "cantidad": 3,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            items_enviados(response),
            [
                {"producto_id": self.yerba.pk, "cantidad": 3},
                {"producto_id": self.cafe.pk, "cantidad": 1},
            ],
        )
        self.assertContains(response, 'data-cantidad="3"')
        self.assertContains(response, 'data-cantidad="1"')
        self.assertContains(response, "$ 4500,00")
        self.assertContains(response, "$ 2500,00")
        self.assertContains(response, "Total: $ 7000,00")

    def test_quitar_un_producto_elimina_su_linea_y_recalcula_el_total(self):
        items = [
            {"producto_id": self.yerba.pk, "cantidad": 2},
            {"producto_id": self.cafe.pk, "cantidad": 1},
        ]

        response = self.client.post(
            reverse("quitar_del_carrito"),
            {
                "items": json.dumps(items),
                "producto_id": self.yerba.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            items_enviados(response),
            [{"producto_id": self.cafe.pk, "cantidad": 1}],
        )
        self.assertNotContains(
            response,
            f'data-producto-id="{self.yerba.pk}"',
        )
        self.assertContains(
            response,
            f'data-producto-id="{self.cafe.pk}"',
        )
        self.assertContains(response, "Total: $ 2500,00")

    def test_quitar_el_unico_producto_muestra_el_carrito_vacio(self):
        items = [{"producto_id": self.cafe.pk, "cantidad": 1}]

        response = self.client.post(
            reverse("quitar_del_carrito"),
            {
                "items": json.dumps(items),
                "producto_id": self.cafe.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(items_enviados(response), [])
        self.assertContains(response, "Carrito vacío")
        self.assertNotContains(
            response,
            f'data-producto-id="{self.cafe.pk}"',
        )
        self.assertNotContains(response, "Total")

    def test_actualizar_cantidad_por_encima_del_stock_se_acepta(self):
        self.yerba.stock = 1
        self.yerba.save(update_fields=["stock"])
        items = [{"producto_id": self.yerba.pk, "cantidad": 2}]

        response = self.client.post(
            reverse("actualizar_cantidad"),
            {
                "items": json.dumps(items),
                "producto_id": self.yerba.pk,
                "cantidad": 5,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            items_enviados(response),
            [{"producto_id": self.yerba.pk, "cantidad": 5}],
        )
        self.assertContains(response, 'data-cantidad="5"')
        self.assertContains(response, "Total: $ 7500,00")

    def test_cada_linea_del_carrito_ofrece_cantidad_y_acciones_de_actualizar_y_quitar(
        self,
    ):
        items = [
            {"producto_id": self.yerba.pk, "cantidad": 2},
            {"producto_id": self.cafe.pk, "cantidad": 3},
        ]

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "", "items": json.dumps(items)},
        )

        parser = _FormulariosParser()
        parser.feed(response.content.decode())
        formularios = [
            formulario
            for formulario in parser.formularios
            if formulario["action"] == reverse("actualizar_cantidad")
        ]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(formularios), 2)
        self.assertEqual(
            {
                formulario["campos"]["producto_id"]: formulario["campos"][
                    "cantidad"
                ]
                for formulario in formularios
            },
            {
                str(self.yerba.pk): "2",
                str(self.cafe.pk): "3",
            },
        )
        for formulario in formularios:
            self.assertEqual(
                json.loads(formulario["campos"]["items"]),
                items,
            )
            self.assertIn("Actualizar", formulario["botones"])
            self.assertIn("Quitar", formulario["botones"])
            self.assertEqual(
                formulario["formactions"]["Quitar"],
                reverse("quitar_del_carrito"),
            )

    def test_carrito_vacio_no_muestra_lineas_ni_total(self):
        response = self.client.get(reverse("pos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carrito vacío")
        self.assertNotContains(response, "<table")
        self.assertNotContains(response, "Total")

    def test_pos_muestra_casillas_y_un_importe_por_medio_de_pago(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 2}]

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "", "items": json.dumps(items)},
        )

        parser = _CamposDePagoParser()
        parser.feed(response.content.decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            parser.medios,
            {medio.value for medio in Pago.MedioPago},
        )
        self.assertEqual(
            parser.importes,
            {f"importe_{medio.value}" for medio in Pago.MedioPago},
        )


class BusquedaDeProductosTests(TestCase):
    def setUp(self):
        proveedor = Proveedor.objects.create(
            razon_social="Distribuidora SA",
            cuit="30-12345678-9",
        )
        self.yerba = Producto.objects.create(
            nombre="Yerba mate",
            stock=10,
            precio_venta=Decimal("1500.00"),
            costo=Decimal("1000.00"),
            codigo_barras="7791234567890",
            proveedor=proveedor,
        )
        self.cafe = Producto.objects.create(
            nombre="Café molido",
            stock=8,
            precio_venta=Decimal("2500.00"),
            costo=Decimal("1800.00"),
            codigo_barras="7791234567891",
            proveedor=proveedor,
        )

    def test_busqueda_por_parte_del_nombre_muestra_coincidencias_con_precio(
        self,
    ):
        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "yer", "items": "[]"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="nombre"')
        self.assertContains(response, self.yerba.nombre)
        self.assertRegex(response.content.decode(), r"1500[.,]00")
        self.assertNotContains(response, self.cafe.nombre)

    def test_busqueda_ignora_mayusculas_y_tildes(self):
        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "CAFE", "items": "[]"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cafe.nombre)
        self.assertNotContains(response, self.yerba.nombre)

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "YÉRBA", "items": "[]"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.yerba.nombre)
        self.assertNotContains(response, self.cafe.nombre)

    def test_busqueda_no_muestra_productos_inactivos(self):
        inactivo = Producto.objects.create(
            nombre="Yerba mate descartada",
            stock=5,
            precio_venta=Decimal("100.00"),
            costo=Decimal("50.00"),
            codigo_barras="7790000000002",
            proveedor=self.yerba.proveedor,
            activo=False,
        )

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "yerba", "items": "[]"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.yerba.nombre)
        self.assertNotContains(response, inactivo.nombre)

    def test_busqueda_conserva_el_carrito_y_el_total(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 2}]

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "cafe", "items": json.dumps(items)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(items_enviados(response), items)
        self.assertContains(response, f'data-producto-id="{self.yerba.pk}"')
        self.assertContains(response, 'data-cantidad="2"')
        self.assertRegex(response.content.decode(), r"Total: \$ 3000[.,]00")

    def test_resultados_muestran_un_boton_agregar_por_producto(self):
        items = [{"producto_id": self.cafe.pk, "cantidad": 2}]

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "a", "items": json.dumps(items)},
        )

        self.assertEqual(response.status_code, 200)
        formularios = formularios_de_alta_desde_resultados(response)
        self.assertEqual(len(formularios), 2)
        self.assertEqual(
            {formulario["campos"]["producto_id"] for formulario in formularios},
            {str(self.yerba.pk), str(self.cafe.pk)},
        )
        for formulario in formularios:
            self.assertEqual(
                json.loads(formulario["campos"]["items"]),
                items,
            )
            self.assertEqual(formulario["campos"]["nombre"], "a")
            self.assertIn("Agregar", formulario["botones"])

    def test_busqueda_sin_resultados_avisa_y_conserva_el_carrito(self):
        items = [{"producto_id": self.yerba.pk, "cantidad": 1}]

        response = self.client.post(
            reverse("buscar_productos"),
            {"nombre": "zzz", "items": json.dumps(items)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No se encontraron productos")
        self.assertEqual(items_enviados(response), items)
        self.assertContains(response, f'data-producto-id="{self.yerba.pk}"')
        self.assertRegex(response.content.decode(), r"Total: \$ 1500[.,]00")

    def test_busqueda_vacia_no_muestra_aviso_ni_resultados(self):
        for termino in ("", "   "):
            response = self.client.post(
                reverse("buscar_productos"),
                {"nombre": termino, "items": "[]"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "No se encontraron productos")
            self.assertNotContains(response, "Resultados")
            self.assertNotContains(response, self.yerba.nombre)
            self.assertNotContains(response, self.cafe.nombre)


class AgregarDesdeResultadosTests(TestCase):
    def setUp(self):
        proveedor = Proveedor.objects.create(
            razon_social="Distribuidora SA",
            cuit="30-12345678-9",
        )
        self.yerba = Producto.objects.create(
            nombre="Yerba mate",
            stock=10,
            precio_venta=Decimal("1500.00"),
            costo=Decimal("1000.00"),
            codigo_barras="7791234567890",
            proveedor=proveedor,
        )
        self.cafe = Producto.objects.create(
            nombre="Café molido",
            stock=8,
            precio_venta=Decimal("2500.00"),
            costo=Decimal("1800.00"),
            codigo_barras="7791234567891",
            proveedor=proveedor,
        )

    def test_agregar_desde_resultados_agrega_el_producto_con_cantidad_uno_y_actualiza_el_total(
        self,
    ):
        response = self.client.post(
            reverse("agregar_desde_resultados"),
            {
                "producto_id": self.yerba.pk,
                "items": "[]",
                "nombre": "yer",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            items_enviados(response),
            [{"producto_id": self.yerba.pk, "cantidad": 1}],
        )
        self.assertContains(response, f'data-producto-id="{self.yerba.pk}"')
        self.assertContains(response, 'data-cantidad="1"')
        self.assertRegex(response.content.decode(), r"Total: \$ 1500[.,]00")

    def test_agregar_desde_resultados_suma_una_unidad_sin_duplicar_la_linea(
        self,
    ):
        primera = self.client.post(
            reverse("agregar_desde_resultados"),
            {
                "producto_id": self.yerba.pk,
                "items": "[]",
                "nombre": "yer",
            },
        )
        items = items_enviados(primera)

        response = self.client.post(
            reverse("agregar_desde_resultados"),
            {
                "producto_id": self.yerba.pk,
                "items": json.dumps(items),
                "nombre": "yer",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            items_enviados(response),
            [{"producto_id": self.yerba.pk, "cantidad": 2}],
        )
        self.assertContains(response, 'data-cantidad="2"')
        self.assertEqual(
            response.content.decode().count(
                f'data-producto-id="{self.yerba.pk}"'
            ),
            1,
        )
        self.assertRegex(response.content.decode(), r"Total: \$ 3000[.,]00")

    def test_agregar_desde_resultados_conserva_los_resultados_y_el_resto_del_carrito(
        self,
    ):
        items = [{"producto_id": self.cafe.pk, "cantidad": 2}]

        response = self.client.post(
            reverse("agregar_desde_resultados"),
            {
                "producto_id": self.yerba.pk,
                "items": json.dumps(items),
                "nombre": "yer",
            },
        )

        items_esperados = [
            {"producto_id": self.cafe.pk, "cantidad": 2},
            {"producto_id": self.yerba.pk, "cantidad": 1},
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(items_enviados(response), items_esperados)
        self.assertContains(response, f'data-producto-id="{self.cafe.pk}"')
        self.assertContains(response, 'data-cantidad="2"')
        self.assertContains(response, f'data-producto-id="{self.yerba.pk}"')
        self.assertContains(response, 'data-cantidad="1"')
        self.assertRegex(response.content.decode(), r"Total: \$ 6500[.,]00")

        formularios = formularios_de_alta_desde_resultados(response)
        self.assertEqual(len(formularios), 1)
        self.assertEqual(
            formularios[0]["campos"]["producto_id"],
            str(self.yerba.pk),
        )
        self.assertEqual(formularios[0]["campos"]["nombre"], "yer")
        self.assertEqual(
            json.loads(formularios[0]["campos"]["items"]),
            items_esperados,
        )


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
