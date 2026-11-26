from django.urls import path

from .views import PosView, RegistrarVentaView


urlpatterns = [
    path("pos/", PosView.as_view(), name="pos"),
    path(
        "pos/registrar/",
        RegistrarVentaView.as_view(),
        name="registrar_venta",
    ),
]
