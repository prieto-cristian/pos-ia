from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .services import FalloIA, consultar_ia


class ChatView(View):
    def _contexto(self, hilo, **extra):
        contexto = {
            "nav_activo": "chat",
            "hilo": hilo[-3:],
        }
        contexto.update(extra)
        return contexto

    def get(self, request):
        return render(
            request,
            "chat/chat.html",
            self._contexto(request.session.get("hilo", [])),
        )

    def post(self, request):
        if request.POST.get("accion") == "nueva":
            request.session["hilo"] = []
            return redirect(reverse("chat"))

        consulta = request.POST.get("consulta", "").strip()
        if not consulta:
            return render(
                request,
                "chat/chat.html",
                self._contexto(
                    request.session.get("hilo", []),
                    error="Escribí una consulta.",
                ),
            )
        hilo = request.session.get("hilo", [])
        try:
            respuesta = consultar_ia(consulta, hilo)
        except FalloIA:
            return render(
                request,
                "chat/chat.html",
                self._contexto(
                    hilo,
                    error=(
                        "La IA no respondió. Tu consulta sigue escrita "
                        "para reintentar."
                    ),
                    consulta=consulta,
                ),
            )
        hilo = (hilo + [{"pregunta": consulta, "respuesta": respuesta}])[-3:]
        request.session["hilo"] = hilo
        return render(
            request,
            "chat/chat.html",
            self._contexto(hilo),
        )
