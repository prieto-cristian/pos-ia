from django.shortcuts import render
from django.views import View

from .services import FalloIA, consultar_ia


class ChatView(View):
    def get(self, request):
        return render(
            request,
            "chat/chat.html",
            {"hilo": request.session.get("hilo", [])[-3:]},
        )

    def post(self, request):
        consulta = request.POST.get("consulta", "").strip()
        if not consulta:
            return render(
                request,
                "chat/chat.html",
                {
                    "error": "Escribí una consulta.",
                    "hilo": request.session.get("hilo", []),
                },
            )
        hilo = request.session.get("hilo", [])
        try:
            respuesta = consultar_ia(consulta, hilo)
        except FalloIA:
            return render(
                request,
                "chat/chat.html",
                {
                    "error": "La IA no respondió. Tu consulta sigue escrita para reintentar.",
                    "hilo": hilo,
                    "consulta": consulta,
                },
            )
        hilo = (hilo + [{"pregunta": consulta, "respuesta": respuesta}])[-3:]
        request.session["hilo"] = hilo
        return render(request, "chat/chat.html", {"hilo": hilo})
