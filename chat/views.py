from django.shortcuts import render
from django.views import View

from .services import consultar_ia


class ChatView(View):
    def get(self, request):
        return render(
            request,
            "chat/chat.html",
            {"hilo": request.session.get("hilo", [])},
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
        respuesta = consultar_ia(consulta)
        hilo = request.session.get("hilo", [])
        hilo.append({"pregunta": consulta, "respuesta": respuesta})
        request.session["hilo"] = hilo
        return render(request, "chat/chat.html", {"hilo": hilo})
