import logging

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .servicio_ia import responder


logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def chat(request):
    pregunta = ""
    respuesta = ""
    error = ""

    if request.method == "POST":
        pregunta = request.POST.get("pregunta", "").strip()

        if not pregunta:
            error = "Escribí una pregunta."
        elif len(pregunta) > 1000:
            error = "La pregunta no puede superar los 1000 caracteres."
        else:
            try:
                respuesta = responder(pregunta)
            except Exception:
                logger.exception("Error al consultar el agente")
                error = (
                    "No se pudo consultar el asistente. "
                    "Revisá la configuración y volvé a intentar."
                )

    return render(
        request,
        "agente/chat.html",
        {
            "pregunta": pregunta,
            "respuesta": respuesta,
            "error": error,
        },
    )