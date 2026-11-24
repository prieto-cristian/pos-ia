from django.urls import path

from .views import AgregarAlCarritoView, PosView, RegistrarVentaView


urlpatterns = [
    path("pos/", PosView.as_view(), name="pos"),
    path(
        "pos/agregar/",
        AgregarAlCarritoView.as_view(),
        name="agregar_al_carrito",
    ),
    path(
        "pos/registrar/",
        RegistrarVentaView.as_view(),
        name="registrar_venta",
    ),
]
