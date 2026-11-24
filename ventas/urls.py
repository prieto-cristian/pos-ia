from django.urls import path

from .views import (
    ActualizarCantidadView,
    AgregarAlCarritoView,
    AgregarDesdeResultadosView,
    BuscarProductosView,
    PosView,
    QuitarDelCarritoView,
    RegistrarVentaView,
)


urlpatterns = [
    path("pos/", PosView.as_view(), name="pos"),
    path(
        "pos/buscar/",
        BuscarProductosView.as_view(),
        name="buscar_productos",
    ),
    path(
        "pos/agregar/",
        AgregarAlCarritoView.as_view(),
        name="agregar_al_carrito",
    ),
    path(
        "pos/agregar-desde-resultados/",
        AgregarDesdeResultadosView.as_view(),
        name="agregar_desde_resultados",
    ),
    path(
        "pos/actualizar/",
        ActualizarCantidadView.as_view(),
        name="actualizar_cantidad",
    ),
    path(
        "pos/quitar/",
        QuitarDelCarritoView.as_view(),
        name="quitar_del_carrito",
    ),
    path(
        "pos/registrar/",
        RegistrarVentaView.as_view(),
        name="registrar_venta",
    ),
]
