from django.shortcuts import render
from django.views import View

from .services import consultar_ia


class ChatView(View):
    def get(self, request):
        return render(request, "chat/chat.html")

    def post(self, request):
        consulta = request.POST.get("consulta", "").strip()
        if not consulta:
            return render(
                request,
                "chat/chat.html",
                {"error": "Escribí una consulta."},
            )
        respuesta = consultar_ia(consulta)
        return render(request, "chat/chat.html", {"respuesta": respuesta})
