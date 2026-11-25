from django.urls import path

from . import views


app_name = "agente"

urlpatterns = [
    path("", views.chat, name="chat"),
]