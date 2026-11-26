# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Cajero o cajera de un almacén de barrio en Argentina, de pie o sentado en el mostrador, con una computadora de escritorio, mouse y lector de códigos de barras. En hora pico necesita cobrar rápido sin perder de vista el nombre, el precio unitario y el total de cada línea. El dueño o encargado usa la misma aplicación para consultar stock, ventas y rentabilidad, y para administrar el catálogo, las ventas y las compras desde Django Admin.

## Product Purpose

Registrar ventas de mostrador contra el catálogo y el stock reales, y convertir los datos del comercio en respuestas comerciales legibles. El éxito es una venta cobrada sin errores en pocos segundos y una consulta respondida con datos que el comercio puede verificar.

## Positioning

Un punto de venta y un asistente comercial en la misma aplicación: el asistente responde únicamente con consultas de solo lectura sobre la base del POS, sin internet ni datos inventados. La caja y el asistente comparten el mismo catálogo y el mismo vocabulario de mostrador.

## Operating Context

- Mostrador de almacén minorista, luz fluorescente, monitor de escritorio y lector de códigos.
- Español rioplatense, importes en pesos argentinos, zona horaria America/Argentina/Buenos_Aires.
- Flujo de caja: escanear o buscar, ajustar cantidades, elegir uno o varios medios de pago, verificar el saldo y registrar la venta.
- Flujo de consulta: preguntar en lenguaje natural sobre stock, ventas, rotación, cobertura y rentabilidad.
- La administración de productos, proveedores, categorías, ventas y compras vive en Django Admin (`/admin/`).
- No hay autenticación en la caja ni en el asistente; el acceso al admin usa el usuario de Django.

## Capabilities and Constraints

- Productos con nombre, stock, stock mínimo, precio de venta, costo, proveedor, categorías y código de barras opcional. 64 productos activos en la base de demostración.
- Carrito de una sola venta en curso: agregar por código de barras o por nombre, actualizar cantidades y quitar líneas.
- Medios de pago: efectivo, tarjeta, QR y transferencia. Se admite pago dividido; los importes deben sumar exactamente el total o la venta no se registra.
- Al registrar la venta se guardan precio y costo históricos y se descuenta stock; el stock nunca baja de cero.
- El asistente tiene seis consultas autorizadas: stock bajo, productos más vendidos, resumen de ventas, comparación de ventas por producto, rotación y cobertura de stock, y rentabilidad de ventas.
- Restricciones del asistente: solo lectura, sin SQL arbitrario, sin internet ni archivos del proyecto, sin crear ni modificar datos, sin inventar información.
- No están modelados: cliente, mesa, salón, turno de caja, propina, descuentos, promociones, impuestos desglosados ni impresión de tickets.
- No hay fotos de productos ni un logo provisto por el cliente. El sitio usa un mark de PosIA dibujado para la ocasión; no reproduce el logo de la referencia. No hay testimonios ni casos de éxito. Los datos de la base local son de demostración.
- La aplicación es Django 6.1 con templates del lado del servidor; no hay build de frontend.

## Brand Commitments

- El producto se llama PosIA. El repositorio y la documentación usan también el nombre DatIA.
- La voz es directa, operativa y rioplatense: "Agregá", "Cobrá", "Revisá", sin adornos.
- La referencia visual vinculante es la imagen de un POS de restaurante compartida por el usuario: shell claro con sidebar, tarjetas blancas, rojo de acción, verde de cobro y rail de carrito a la derecha. El contenido debe ser el almacén real, no un restaurante.

## Evidence on Hand

- Catálogo y ventas reales en `db.sqlite3`; comando `poblar_demo --reset` para regenerar 12 meses de historial sintético.
- Consultas y períodos documentados en `README.md`; restricciones del asistente en `RESTRICCIONES.md`.
- Rutas existentes: `/ventas/pos/`, `/agente/`, `/chat/`, `/admin/`.
- Ausencias que no deben fabricarse: fotos de producto, logo original, clientes, reseñas, métricas de negocio, descuentos o impuestos.

## Product Principles

1. El mostrador manda: cada decisión se mide por segundos y por errores de cobro, no por ornamentación.
2. Datos verificables: la interfaz muestra lo que existe en la base y no completa huecos con ficción.
3. Teclado y lector primero: escanear, buscar, cobrar y volver al escáner sin mouse.
4. Una sola casa: caja, asistente y chat comparten shell, navegación y lenguaje.
5. El dinero se lee de un vistazo: total, saldo y estado de cobro siempre visibles.

## Accessibility & Inclusion

- Operación completa por teclado, foco visible, etiquetas asociadas y contraste ≥4.5:1 en texto.
- Objetivos de puntero de al menos 32 px en las acciones principales y 24 px como mínimo en los controles densos de la caja.
- No se estableció un estándar formal de accesibilidad; se toma WCAG 2.2 AA como piso de trabajo.
