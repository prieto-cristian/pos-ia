from django.urls import path

from .views import (
    AgregarAlCarritoView,
    AgregarDesdeResultadosView,
    BuscarProductosView,
    PosView,
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
        "pos/registrar/",
        RegistrarVentaView.as_view(),
        name="registrar_venta",
    ),
]
