"""Puebla la base con un almacén de barrio de demostración.

Genera un catálogo, compras y ventas distribuidas en el tiempo para que el
asistente comercial tenga datos reales con los que responder consultas por
período. El resultado es determinista para una misma semilla.
"""

import random
from collections import defaultdict
from datetime import datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from compras.models import Compra, DetalleCompra
from productos.models import Categoria, Producto, Proveedor
from ventas.models import DetalleVenta, Pago, Venta

CENTAVO = Decimal("0.01")
TASA_PRECIO_MENSUAL = Decimal("0.020")
TASA_COSTO_MENSUAL = Decimal("0.017")

CATEGORIAS = (
    "Almacén",
    "Bebidas",
    "Golosinas",
    "Lácteos",
    "Panadería",
    "Fiambrería",
    "Limpieza",
    "Perfumería",
    "Congelados",
)

PROVEEDORES = {
    "esquina": (
        "Distribuidora La Esquina SRL",
        "La Esquina",
        "11-4455-1200",
        "30712345678",
    ),
    "molinos": (
        "Molinos del Plata S.A.",
        "Molinos del Plata",
        "11-4455-2301",
        "30723456781",
    ),
    "bebidas": (
        "Bebidas del Sur SRL",
        "Bebidas del Sur",
        "11-4455-3402",
        "30734567892",
    ),
    "lacteos": (
        "Lácteos San Antonio S.A.",
        "San Antonio",
        "11-4455-4503",
        "30745678903",
    ),
    "fiambres": (
        "Fiambres y Quesos Don Pedro",
        "Don Pedro",
        "11-4455-5604",
        "30756789014",
    ),
    "limpieza": (
        "Limpieza Total S.A.",
        "Limpieza Total",
        "11-4455-6705",
        "30767890125",
    ),
    "dulces": (
        "Dulces Argentinos SRL",
        "Dulces Argentinos",
        "11-4455-7806",
        "30778901236",
    ),
    "congelados": (
        "Congelados del Río S.A.",
        "Congelados del Río",
        "11-4455-8907",
        "30789012347",
    ),
}

# (nombre, categorías, proveedor, costo, margen, stock mínimo, peso, activo)
# El peso define la popularidad en las ventas; 0 significa que no se vende.
PRODUCTOS = (
    ("Yerba mate 1 kg", ("Almacén",), "molinos", 3800, 0.32, 12, 10, True),
    ("Yerba mate 500 g", ("Almacén",), "molinos", 2100, 0.32, 10, 7, True),
    ("Café molido 250 g", ("Almacén",), "molinos", 3200, 0.35, 8, 5, True),
    ("Azúcar 1 kg", ("Almacén",), "molinos", 1300, 0.28, 12, 7, True),
    ("Arroz largo fino 1 kg", ("Almacén",), "molinos", 1500, 0.30, 10, 6, True),
    ("Fideos tallarín 500 g", ("Almacén",), "molinos", 950, 0.32, 15, 8, True),
    ("Fideos moño 500 g", ("Almacén",), "molinos", 980, 0.32, 10, 5, True),
    ("Aceite de girasol 1,5 L", ("Almacén",), "molinos", 3600, 0.25, 10, 8, True),
    ("Harina 000 1 kg", ("Almacén",), "molinos", 1100, 0.30, 8, 4, True),
    ("Sal fina 500 g", ("Almacén",), "molinos", 450, 0.35, 10, 0, True),
    ("Polenta 500 g", ("Almacén",), "molinos", 900, 0.32, 6, 2, True),
    ("Lentejas 500 g", ("Almacén",), "molinos", 1400, 0.33, 6, 2, True),
    ("Puré de tomate 520 g", ("Almacén",), "molinos", 850, 0.35, 12, 5, True),
    ("Atún al natural 170 g", ("Almacén",), "molinos", 2200, 0.30, 8, 3, True),
    ("Galletitas de agua 300 g", ("Almacén",), "dulces", 1200, 0.35, 10, 6, True),
    ("Galletitas dulces 400 g", ("Almacén",), "dulces", 1500, 0.35, 10, 5, True),
    ("Gaseosa cola 2,25 L", ("Bebidas",), "bebidas", 2400, 0.35, 12, 12, True),
    ("Gaseosa lima-limón 2,25 L", ("Bebidas",), "bebidas", 2300, 0.35, 10, 9, True),
    ("Gaseosa cola 500 ml", ("Bebidas",), "bebidas", 1000, 0.40, 18, 8, True),
    ("Agua mineral 2 L", ("Bebidas",), "bebidas", 800, 0.40, 12, 7, True),
    ("Cerveza rubia 1 L", ("Bebidas",), "bebidas", 2600, 0.30, 12, 8, True),
    ("Cerveza lata 473 ml", ("Bebidas",), "bebidas", 1400, 0.35, 18, 6, True),
    ("Jugo de naranja 1 L", ("Bebidas",), "bebidas", 1700, 0.32, 8, 4, True),
    ("Bebida isotónica 500 ml", ("Bebidas",), "bebidas", 1300, 0.35, 10, 0, True),
    ("Alfajor triple", ("Golosinas",), "dulces", 800, 0.45, 20, 12, True),
    ("Chocolate en barra 100 g", ("Golosinas",), "dulces", 1200, 0.40, 15, 7, True),
    ("Caramelos masticables 30 g", ("Golosinas",), "dulces", 350, 0.50, 25, 8, True),
    ("Chicles 10 g", ("Golosinas",), "dulces", 300, 0.55, 20, 6, True),
    ("Galletitas surtidas 500 g", ("Golosinas",), "dulces", 2000, 0.35, 8, 5, True),
    ("Turrón 25 g", ("Golosinas",), "dulces", 250, 0.50, 20, 0, True),
    ("Leche entera 1 L", ("Lácteos",), "lacteos", 1400, 0.25, 20, 12, True),
    ("Leche descremada 1 L", ("Lácteos",), "lacteos", 1450, 0.25, 10, 5, True),
    ("Yogur bebible 900 g", ("Lácteos",), "lacteos", 1800, 0.30, 10, 6, True),
    ("Queso crema 300 g", ("Lácteos",), "lacteos", 2100, 0.32, 8, 4, True),
    ("Mantequilla 200 g", ("Lácteos",), "lacteos", 2400, 0.30, 6, 0, True),
    ("Dulce de leche 400 g", ("Lácteos",), "lacteos", 1900, 0.35, 8, 5, True),
    ("Pan francés 1 kg", ("Panadería",), "esquina", 1600, 0.40, 10, 10, True),
    ("Pan lactal 500 g", ("Panadería",), "esquina", 1700, 0.30, 8, 5, True),
    ("Facturas 6 unidades", ("Panadería",), "esquina", 1500, 0.45, 8, 7, True),
    ("Bizcochos 500 g", ("Panadería",), "esquina", 1800, 0.40, 6, 3, True),
    ("Jamón cocido 100 g", ("Fiambrería",), "fiambres", 1500, 0.35, 8, 5, True),
    ("Queso fresco 500 g", ("Fiambrería",), "fiambres", 3200, 0.30, 6, 4, True),
    ("Queso tybo 100 g", ("Fiambrería",), "fiambres", 1800, 0.32, 8, 3, True),
    ("Salame 100 g", ("Fiambrería",), "fiambres", 1400, 0.35, 8, 4, True),
    ("Mortadela 100 g", ("Fiambrería",), "fiambres", 900, 0.38, 8, 3, True),
    ("Detergente 500 ml", ("Limpieza",), "limpieza", 1400, 0.35, 12, 6, True),
    ("Lavandina 1 L", ("Limpieza",), "limpieza", 900, 0.40, 10, 5, True),
    ("Jabón en polvo 500 g", ("Limpieza",), "limpieza", 1600, 0.32, 8, 4, True),
    ("Papel higiénico 4 rollos", ("Limpieza",), "limpieza", 2200, 0.30, 10, 7, True),
    ("Rollo de cocina 2 unidades", ("Limpieza",), "limpieza", 1800, 0.32, 8, 4, True),
    ("Limpiador pisos 900 ml", ("Limpieza",), "limpieza", 1500, 0.35, 6, 3, True),
    ("Shampoo 400 ml", ("Perfumería",), "limpieza", 2800, 0.35, 6, 3, True),
    ("Jabón de tocador 3 unidades", ("Perfumería",), "limpieza", 1200, 0.38, 10, 4, True),
    ("Pasta dental 90 g", ("Perfumería",), "limpieza", 1900, 0.35, 8, 4, True),
    ("Desodorante aerosol 150 ml", ("Perfumería",), "limpieza", 2500, 0.35, 6, 3, True),
    ("Papas fritas congeladas 1 kg", ("Congelados",), "congelados", 2600, 0.30, 6, 4, True),
    ("Hamburguesas 4 unidades", ("Congelados",), "congelados", 2800, 0.32, 6, 5, True),
    ("Helado 1 L", ("Congelados",), "congelados", 3500, 0.35, 4, 3, True),
    ("Milanesas de pollo 500 g", ("Congelados",), "congelados", 3200, 0.32, 5, 4, True),
    ("Verdura congelada 500 g", ("Congelados",), "congelados", 1800, 0.35, 5, 0, True),
    ("Vino tinto 750 ml", ("Almacén",), "esquina", 2200, 0.35, 6, 0, False),
    ("Fernet 750 ml", ("Bebidas",), "bebidas", 5000, 0.30, 4, 0, False),
    ("Pañales 8 unidades", ("Perfumería",), "limpieza", 3500, 0.30, 4, 0, False),
    ("Bebida energizante 500 ml", ("Bebidas",), "bebidas", 1600, 0.38, 6, 0, False),
)

# Productos de baja rotación que no se reponen en los últimos meses. Sirven
# para que la consulta de stock bajo tenga casos reales al final del período.
CONTROLADOS = {
    "Polenta 500 g",
    "Lentejas 500 g",
    "Jugo de naranja 1 L",
    "Queso tybo 100 g",
    "Salame 100 g",
    "Mortadela 100 g",
    "Jabón en polvo 500 g",
    "Limpiador pisos 900 ml",
}

# Distribución de tickets por día de la semana y por mes.
FACTOR_SEMANA = (0.85, 0.90, 0.95, 1.00, 1.25, 1.35, 0.55)
FACTOR_MES = {
    1: 1.15,
    2: 0.95,
    3: 1.00,
    4: 0.95,
    5: 0.95,
    6: 1.00,
    7: 1.05,
    8: 0.95,
    9: 0.95,
    10: 1.00,
    11: 1.00,
    12: 1.25,
}

MEDIOS_PAGO = (
    ("EFECTIVO", 0.42),
    ("TARJETA", 0.24),
    ("QR", 0.24),
    ("TRANSFERENCIA", 0.10),
)

HORAS_VENTA = tuple(range(9, 21))
PESOS_HORA = (3, 5, 7, 6, 4, 3, 4, 6, 8, 7, 4, 2)

TAMANOS_TICKET = (1, 2, 3, 4, 5, 6)
PESOS_TICKET = (0.32, 0.30, 0.18, 0.11, 0.06, 0.03)


def _redondear_a(valor, paso):
    paso = Decimal(str(paso))
    return (
        (valor / paso).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * paso
    )


def _factor_historico(fecha, hoy, tasa_mensual):
    meses = (hoy.year - fecha.year) * 12 + hoy.month - fecha.month
    if meses <= 0:
        return Decimal("1")

    factor = (Decimal("1") - tasa_mensual) ** meses
    return max(Decimal("0.70"), factor)


def _precio_historico(producto, fecha, hoy):
    factor = _factor_historico(fecha, hoy, TASA_PRECIO_MENSUAL)
    return max(
        Decimal("1.00"),
        _redondear_a(producto.precio_venta * factor, 10),
    )


def _costo_historico(producto, fecha, hoy):
    factor = _factor_historico(fecha, hoy, TASA_COSTO_MENSUAL)
    return max(
        Decimal("1.00"),
        _redondear_a(producto.costo * factor, 10),
    )


def _ean13(base12):
    suma = 0
    for posicion, digito in enumerate(base12, start=1):
        suma += int(digito) * (1 if posicion % 2 else 3)
    control = (10 - suma % 10) % 10
    return f"{base12}{control}"


def _fecha_consciente(fecha, hora=8):
    zona = timezone.get_current_timezone()
    return timezone.make_aware(
        datetime.combine(fecha, time(hora, 0)),
        zona,
    )


class Command(BaseCommand):
    help = (
        "Genera un almacén de barrio de demostración con catálogo, compras "
        "y ventas de los últimos meses."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help=(
                "Elimina productos, ventas y compras existentes antes de "
                "generar los datos. No borra usuarios ni sesiones."
            ),
        )
        parser.add_argument(
            "--ventas",
            type=int,
            default=700,
            help="Cantidad de tickets a generar (por defecto: 700).",
        )
        parser.add_argument(
            "--dias",
            type=int,
            default=365,
            help="Días de historial hacia atrás (por defecto: 365).",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=20261125,
            help="Semilla para que la generación sea reproducible.",
        )

    def handle(self, *args, **options):
        if options["ventas"] < 1:
            raise CommandError("--ventas debe ser mayor que cero.")

        if options["dias"] < 30:
            raise CommandError("--dias debe ser al menos 30.")

        if not options["reset"] and Producto.objects.exists():
            raise CommandError(
                "Ya hay productos cargados. Usá --reset para reemplazar los "
                "datos existentes."
            )

        with transaction.atomic():
            if options["reset"]:
                self._borrar_datos()

            resumen = self._poblar(
                cantidad_ventas=options["ventas"],
                dias=options["dias"],
                semilla=options["seed"],
            )

            self._validar(resumen)

        self._imprimir_resumen(resumen)

    def _borrar_datos(self):
        self.stdout.write("Borrando datos anteriores...")
        Pago.objects.all().delete()
        DetalleVenta.objects.all().delete()
        Venta.objects.all().delete()
        DetalleCompra.objects.all().delete()
        Compra.objects.all().delete()
        Producto.objects.all().delete()
        Categoria.objects.all().delete()
        Proveedor.objects.all().delete()

    def _poblar(self, cantidad_ventas, dias, semilla):
        rng = random.Random(semilla)
        hoy = timezone.localdate()
        inicio = hoy - timedelta(days=dias - 1)

        categorias = {
            nombre: Categoria.objects.create(nombre=nombre)
            for nombre in CATEGORIAS
        }

        proveedores = {}
        for clave, datos in PROVEEDORES.items():
            razon_social, nombre, telefono, cuit = datos
            proveedores[clave] = Proveedor.objects.create(
                razon_social=razon_social,
                nombre=nombre,
                telefono=telefono,
                cuit=cuit,
            )

        productos = []
        pesos = {}
        for indice, fila in enumerate(PRODUCTOS, start=1):
            (
                nombre,
                categorias_producto,
                clave_proveedor,
                costo,
                margen,
                stock_minimo,
                peso,
                activo,
            ) = fila

            costo_decimal = Decimal(str(costo))
            precio = max(
                Decimal("1.00"),
                _redondear_a(
                    costo_decimal * (1 + Decimal(str(margen))),
                    10,
                ),
            )

            producto = Producto.objects.create(
                nombre=nombre,
                stock=0,
                stock_minimo=stock_minimo,
                precio_venta=precio,
                costo=costo_decimal,
                codigo_barras=_ean13(f"779{indice:09d}"),
                proveedor=proveedores[clave_proveedor],
                activo=activo,
            )
            producto.categorias.set(
                [categorias[nombre_categoria]
                 for nombre_categoria in categorias_producto]
            )

            productos.append(producto)
            pesos[producto.pk] = peso

        stock = {producto.pk: 0 for producto in productos}
        proveedores_por_id = {
            producto.proveedor_id: producto.proveedor
            for producto in productos
        }

        self._compras_de_apertura(
            rng, productos, stock, proveedores_por_id, inicio, hoy
        )

        ventas, unidades_vendidas = self._simular_ventas(
            rng,
            productos,
            pesos,
            stock,
            proveedores_por_id,
            inicio,
            hoy,
            cantidad_ventas,
        )

        bajos = self._ajustar_stock_final(productos, stock, pesos, rng)

        no_vendidos = [
            producto
            for producto in productos
            if producto.activo
            and pesos[producto.pk] == 0
            and stock[producto.pk] > 0
        ]

        for producto in productos:
            producto.stock = stock[producto.pk]

        Producto.objects.bulk_update(productos, ["stock", "stock_minimo"])

        return {
            "categorias": len(categorias),
            "proveedores": len(proveedores),
            "productos": len(productos),
            "activos": sum(1 for producto in productos if producto.activo),
            "inactivos": sum(1 for producto in productos if not producto.activo),
            "compras": Compra.objects.count(),
            "ventas": ventas,
            "unidades_vendidas": unidades_vendidas,
            "stock_bajo": len(bajos),
            "sin_ventas": len(no_vendidos),
            "stock_total": sum(stock.values()),
            "dias": dias,
            "semilla": semilla,
        }

    def _compras_de_apertura(
        self,
        rng,
        productos,
        stock,
        proveedores_por_id,
        inicio,
        hoy,
    ):
        fecha = inicio - timedelta(days=3)
        pedidos = defaultdict(list)

        for producto in productos:
            if not producto.activo:
                continue

            if producto.nombre in CONTROLADOS:
                objetivo = max(producto.stock_minimo * 2, 12)
            else:
                objetivo = max(producto.stock_minimo * 3, 18)

            cantidad = objetivo + rng.randint(0, max(producto.stock_minimo, 4))
            costo = _costo_historico(producto, fecha, hoy)
            pedidos[producto.proveedor_id].append(
                (producto, cantidad, costo)
            )

        for proveedor_id, items in pedidos.items():
            self._crear_compra(
                proveedores_por_id[proveedor_id],
                fecha,
                items,
                stock,
            )

    def _simular_ventas(
        self,
        rng,
        productos,
        pesos,
        stock,
        proveedores_por_id,
        inicio,
        hoy,
        cantidad_ventas,
    ):
        fechas = []
        for desplazamiento in range((hoy - inicio).days + 1):
            fecha = inicio + timedelta(days=desplazamiento)
            fechas.append(fecha)

        fechas_elegidas = rng.choices(
            fechas,
            weights=[
                FACTOR_SEMANA[fecha.weekday()] * FACTOR_MES[fecha.month]
                for fecha in fechas
            ],
            k=cantidad_ventas,
        )
        fechas_elegidas.sort()

        # La última venta siempre queda en el día de hoy.
        fechas_elegidas[-1] = hoy

        tickets = []
        for fecha in fechas_elegidas:
            hora = rng.choices(HORAS_VENTA, weights=PESOS_HORA, k=1)[0]
            tickets.append(
                (
                    fecha,
                    timezone.make_aware(
                        datetime.combine(
                            fecha,
                            time(hora, rng.randint(0, 59), rng.randint(0, 59)),
                        ),
                        timezone.get_current_timezone(),
                    ),
                )
            )

        tickets.sort(key=lambda ticket: ticket[1])
        por_dia = defaultdict(list)
        for fecha, momento in tickets:
            por_dia[fecha].append(momento)

        vendibles = [
            producto
            for producto in productos
            if producto.activo and pesos[producto.pk] > 0
        ]

        total_ventas = 0
        total_unidades = 0

        for desplazamiento in range((hoy - inicio).days + 1):
            fecha = inicio + timedelta(days=desplazamiento)

            if fecha.weekday() == 0:
                self._reponer(
                    rng,
                    productos,
                    pesos,
                    stock,
                    proveedores_por_id,
                    fecha,
                    hoy,
                )

            for momento in por_dia.get(fecha, []):
                items = self._armar_ticket(
                    rng, vendibles, pesos, stock, fecha, hoy
                )

                if not items:
                    continue

                total = sum(
                    (precio * cantidad for _, cantidad, precio, _ in items),
                    Decimal("0.00"),
                )
                pagos = self._armar_pagos(rng, total)

                venta = Venta.objects.create()
                DetalleVenta.objects.bulk_create([
                    DetalleVenta(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio,
                        costo_unitario=costo,
                    )
                    for producto, cantidad, precio, costo in items
                ])
                Pago.objects.bulk_create([
                    Pago(venta=venta, medio_pago=medio, importe=importe)
                    for medio, importe in pagos
                ])
                Venta.objects.filter(pk=venta.pk).update(fecha=momento)

                total_ventas += 1
                total_unidades += sum(
                    cantidad for _, cantidad, _, _ in items
                )

        return total_ventas, total_unidades

    def _reponer(
        self,
        rng,
        productos,
        pesos,
        stock,
        proveedores_por_id,
        fecha,
        hoy,
    ):
        pedidos = defaultdict(list)

        for producto in productos:
            if not producto.activo or pesos[producto.pk] == 0:
                continue

            if producto.nombre in CONTROLADOS and (
                hoy - fecha
            ).days < 120:
                continue

            if stock[producto.pk] > producto.stock_minimo:
                continue

            if producto.nombre in CONTROLADOS:
                objetivo = max(producto.stock_minimo * 2, 12)
            else:
                objetivo = max(producto.stock_minimo * 4, 20)

            cantidad = (
                objetivo
                - stock[producto.pk]
                + rng.randint(0, max(producto.stock_minimo, 2))
            )
            if cantidad <= 0:
                continue

            costo = _costo_historico(producto, fecha, hoy)
            pedidos[producto.proveedor_id].append(
                (producto, cantidad, costo)
            )

        for proveedor_id, items in pedidos.items():
            self._crear_compra(
                proveedores_por_id[proveedor_id],
                fecha,
                items,
                stock,
            )

    def _crear_compra(self, proveedor, fecha, items, stock):
        compra = Compra.objects.create(proveedor=proveedor)
        DetalleCompra.objects.bulk_create([
            DetalleCompra(
                compra=compra,
                producto=producto,
                cantidad=cantidad,
                costo_unitario=costo,
            )
            for producto, cantidad, costo in items
        ])
        Compra.objects.filter(pk=compra.pk).update(
            fecha=_fecha_consciente(fecha)
        )

        for producto, cantidad, _ in items:
            stock[producto.pk] += cantidad

    def _armar_ticket(self, rng, vendibles, pesos, stock, fecha, hoy):
        cantidad_items = rng.choices(
            TAMANOS_TICKET,
            weights=PESOS_TICKET,
            k=1,
        )[0]

        items = []
        elegidos = set()

        while len(items) < cantidad_items:
            disponibles = [
                producto
                for producto in vendibles
                if stock[producto.pk] > 0 and producto.pk not in elegidos
            ]
            if not disponibles:
                break

            producto = rng.choices(
                disponibles,
                weights=[pesos[producto.pk] for producto in disponibles],
                k=1,
            )[0]

            cantidad = self._cantidad_item(rng, pesos[producto.pk])
            cantidad = min(cantidad, stock[producto.pk])

            items.append(
                (
                    producto,
                    cantidad,
                    _precio_historico(producto, fecha, hoy),
                    _costo_historico(producto, fecha, hoy),
                )
            )
            elegidos.add(producto.pk)
            stock[producto.pk] -= cantidad

        if items:
            return items

        # Garantiza que el ticket no quede vacío.
        disponibles = [
            producto for producto in vendibles if stock[producto.pk] > 0
        ]
        if not disponibles:
            return []

        producto = rng.choice(disponibles)
        stock[producto.pk] -= 1
        return [
            (
                producto,
                1,
                _precio_historico(producto, fecha, hoy),
                _costo_historico(producto, fecha, hoy),
            )
        ]

    @staticmethod
    def _cantidad_item(rng, peso):
        if peso >= 7:
            return rng.choices((1, 2, 3), weights=(0.55, 0.35, 0.10), k=1)[0]
        return rng.choices((1, 2), weights=(0.80, 0.20), k=1)[0]

    @staticmethod
    def _armar_pagos(rng, total):
        medios = [medio for medio, _ in MEDIOS_PAGO]
        pesos_medios = [peso for _, peso in MEDIOS_PAGO]

        if rng.random() < 0.05:
            fraccion = Decimal(str(round(rng.uniform(0.50, 0.90), 2)))
            importe = max(
                CENTAVO,
                (total * fraccion).quantize(CENTAVO),
            )
            importe = min(importe, total)
            return [
                (
                    rng.choices(medios, weights=pesos_medios, k=1)[0],
                    importe,
                )
            ]

        if rng.random() < 0.15:
            fraccion = Decimal(str(round(rng.uniform(0.35, 0.65), 2)))
            primero = max(CENTAVO, (total * fraccion).quantize(CENTAVO))
            segundo = total - primero
            elegidos = rng.sample(medios, 2)
            return [(elegidos[0], primero), (elegidos[1], segundo)]

        return [
            (
                rng.choices(medios, weights=pesos_medios, k=1)[0],
                total,
            )
        ]

    def _ajustar_stock_final(self, productos, stock, pesos, rng):
        activos = [producto for producto in productos if producto.activo]
        bajos = [
            producto
            for producto in activos
            if stock[producto.pk] <= producto.stock_minimo
        ]

        if len(bajos) >= 6:
            return bajos

        candidatos = sorted(
            (
                producto
                for producto in activos
                if 0 < stock[producto.pk] <= 35
                and pesos[producto.pk] > 0
            ),
            key=lambda producto: stock[producto.pk],
        )

        for producto in candidatos:
            if len(bajos) >= 6:
                break
            if producto in bajos:
                continue

            producto.stock_minimo = min(
                stock[producto.pk] + rng.randint(1, 3),
                40,
            )
            bajos.append(producto)

        if not bajos:
            candidatos = sorted(
                (
                    producto
                    for producto in activos
                    if stock[producto.pk] > 0
                ),
                key=lambda producto: stock[producto.pk],
            )
            if candidatos:
                candidatos[0].stock_minimo = stock[candidatos[0].pk] + 1
                bajos.append(candidatos[0])

        return bajos

    def _validar(self, resumen):
        errores = []

        if Producto.objects.filter(stock__lt=0).exists():
            errores.append("Hay productos con stock negativo.")

        if not Venta.objects.exists():
            errores.append("No se generó ninguna venta.")

        if resumen["stock_bajo"] < 1:
            errores.append("No hay productos con stock bajo.")

        if resumen["sin_ventas"] < 1:
            errores.append("No hay productos activos sin ventas.")

        totales = DetalleVenta.objects.aggregate(
            unidades=Sum("cantidad"),
            importe=Sum(F("precio_unitario") * F("cantidad")),
        )
        cobrado = (
            Pago.objects.aggregate(total=Sum("importe"))["total"]
            or Decimal("0.00")
        )
        importe = totales["importe"] or Decimal("0.00")

        if cobrado > importe:
            errores.append(
                "Los pagos superan el importe vendido: "
                f"{cobrado} > {importe}."
            )

        if totales["unidades"] != resumen["unidades_vendidas"]:
            errores.append("Las unidades vendidas no coinciden con los items.")

        if errores:
            raise CommandError(" ".join(errores))

    def _imprimir_resumen(self, resumen):
        totales = DetalleVenta.objects.aggregate(
            unidades=Sum("cantidad"),
            importe=Sum(F("precio_unitario") * F("cantidad")),
        )
        cobrado = (
            Pago.objects.aggregate(total=Sum("importe"))["total"]
            or Decimal("0.00")
        )
        importe = totales["importe"] or Decimal("0.00")
        pendiente = importe - cobrado
        ultima = (
            Venta.objects.order_by("-fecha")
            .values_list("fecha", flat=True)
            .first()
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Base poblada correctamente."))
        self.stdout.write(
            f"Catálogo: {resumen['categorias']} categorías, "
            f"{resumen['proveedores']} proveedores y "
            f"{resumen['productos']} productos "
            f"({resumen['activos']} activos, "
            f"{resumen['inactivos']} inactivos)."
        )
        self.stdout.write(
            f"Historial: {resumen['dias']} días, semilla {resumen['semilla']}."
        )
        self.stdout.write(
            f"Compras: {resumen['compras']} compras registradas."
        )
        self.stdout.write(
            f"Ventas: {resumen['ventas']} tickets, "
            f"{resumen['unidades_vendidas']} unidades."
        )
        self.stdout.write(
            f"Facturación: $ {importe:,.2f} | "
            f"Cobrado: $ {cobrado:,.2f} | "
            f"Pendiente: $ {pendiente:,.2f}."
        )
        self.stdout.write(
            f"Stock final: {resumen['stock_total']} unidades | "
            f"Stock bajo: {resumen['stock_bajo']} productos | "
            f"Sin ventas: {resumen['sin_ventas']} productos."
        )
        if ultima:
            self.stdout.write(f"Última venta: {ultima:%Y-%m-%d %H:%M}.")
