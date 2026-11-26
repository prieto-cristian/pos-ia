# DatIA

Aplicación Django para administrar productos, ventas y compras, y consultar información comercial mediante un asistente conectado a Gemini.

## Funcionalidades

### Punto de venta

La caja está en `/ventas/pos/` y la raíz `/` redirige ahí. Es una pantalla de mostrador pensada para escritorio con lector de códigos:

- Buscar por nombre o escanear un código de barras. El lector puede escribir directo en el buscador y confirmar con Enter.
- Agregar productos al carrito, ajustar cantidades y quitarlos sin recargar la página. El catálogo se filtra por categoría y por texto en el navegador.
- Ver el stock disponible de cada producto y el aviso de stock bajo o sin stock.
- Cobrar con efectivo, tarjeta, QR o transferencia. Se admite pago dividido entre varios medios; los importes deben sumar exactamente el total.
- Confirmar la venta con el número, el total, los productos vendidos y el detalle de pagos. El stock se descuenta en el servidor y la venta queda registrada.
- Atajos de teclado: `F2` enfoca el buscador, `F4` lleva al cobro y `Esc` limpia la búsqueda.
- En pantallas compactas, una barra fija muestra la cantidad y el total del carrito y lleva a la sección de cobro.

El carrito y los filtros se resuelven en el navegador; el registro de la venta y la validación de importes se hacen siempre en el servidor. Si el navegador recarga la página, el carrito se recupera de la sesión de la pestaña. No están modelados cliente, mesa, turno, propina, descuentos, promociones ni impuestos desglosados: la caja no inventa esos datos.

### Administración

El catálogo, las ventas y las compras se gestionan desde Django Admin (`/admin/`).

- **Productos:** nombre, stock, stock mínimo, precio, costo, proveedor, categorías y código de barras.
- **Proveedores y categorías:** administración y baja lógica mediante el campo `activo`.
- **Ventas:** encabezado, detalles y pagos. Los medios de pago disponibles son efectivo, tarjeta, QR y transferencia.
- **Compras:** encabezado, proveedor y detalles con cantidad y costo unitario.

Al crear un detalle de venta desde el administrador, se guardan el precio y el costo vigentes del producto como valores históricos, y se descuenta el stock. Si la cantidad vendida supera el stock registrado, este queda en cero. Al modificar o eliminar detalles se ajusta el stock correspondiente.

Al registrar, modificar o eliminar un detalle de compra, se ajusta el stock. El costo cargado en el detalle queda registrado en la compra, pero no actualiza automáticamente el costo vigente del producto.

### Asistente comercial

La página del asistente está en `/agente/`. Se envía una consulta al presionar el botón del formulario; cargar la página por sí solo no consulta a Gemini. La pregunta puede tener hasta 1000 caracteres.

El agente dispone de estas consultas:

- **Stock bajo:** productos activos cuyo stock es igual o menor al mínimo.
- **Productos más vendidos:** ranking por unidades vendidas. Sin período indicado, usa el historial completo.
- **Resumen de ventas:** cantidad de ventas, unidades, importe vendido, importe cobrado y saldo pendiente. Sin período indicado, usa el historial completo.
- **Comparación de ventas por producto:** compara unidades del período con las del período comparable anterior. Sin período indicado, compara el mes actual con el tramo equivalente del mes anterior.
- **Rotación y cobertura de stock:** productos con stock que no tuvieron ventas en el período y productos con más días estimados de cobertura. Sin período indicado, considera los últimos 30 días. La cobertura es una estimación basada en el stock actual y las ventas del período.
- **Rentabilidad de ventas:** ingresos, costo de los productos, ganancia bruta y margen bruto, en total y por producto. Sin período indicado, usa el historial completo. No calcula ganancia neta ni descuenta gastos del comercio.

Los períodos disponibles incluyen semana, mes, año y trimestre actuales o anteriores, trimestre específico, últimos N días y rango explícito de fechas. Si no se indica un período, el valor predeterminado depende de la consulta, como se describe arriba.

La API de Gemini requiere una clave válida y puede responder con errores de disponibilidad o de cuota.

## Requisitos

- Python instalado.
- Una clave de API de Gemini para utilizar el asistente.

Las dependencias de Python están en `requirements.txt`.

## Puesta en marcha local

Cloná la rama `feat/agente` y entrá en la carpeta del proyecto:

```bash
git clone --branch feat/agente --single-branch https://github.com/prieto-cristian/pos-ia.git
cd pos-ia
```

Creá y activá un entorno virtual.

**Windows PowerShell:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux o macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalá las dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Configuración de Gemini

Creá un archivo `.env` en la carpeta raíz del proyecto, junto a `manage.py`:

```env
GEMINI_API_KEY=tu_clave_de_gemini
GEMINI_MODEL=gemini-3.8-flash
```

`GEMINI_MODEL` es opcional: si no se define, Django usa el modelo configurado por defecto en `PosIA/settings.py`. El archivo `.env` está excluido de Git.

### Base de datos y usuario administrador

Aplicá las migraciones:

```bash
python manage.py migrate
```

Creá un usuario para ingresar a Django Admin:

```bash
python manage.py createsuperuser
```

### Iniciar el servidor

```bash
python manage.py runserver
```

Abrí estas direcciones en el navegador:

- Caja: http://127.0.0.1:8000/ventas/pos/ (la raíz `/` redirige acá)
- Asistente: http://127.0.0.1:8000/agente/
- Chat: http://127.0.0.1:8000/chat/
- Administración: http://127.0.0.1:8000/admin/

La base de datos local se guarda en `db.sqlite3`.

## Consultas de ejemplo

- ¿Qué productos tienen stock bajo?
- ¿Cuáles fueron los productos más vendidos este mes?
- ¿Cuánto vendí y cuánto cobré esta semana?
- ¿Cómo variaron las unidades vendidas este mes?
- ¿Qué productos tienen más días estimados de cobertura?
- ¿Qué productos me dejaron más ganancia bruta?