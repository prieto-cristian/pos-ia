import logging

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from google.genai.errors import ClientError, ServerError

from .servicio_ia import responder


logger = logging.getLogger(__name__)

CONSULTAS = [
    {
        "icono": "i-alert",
        "titulo": "Stock bajo",
        "pregunta": "¿Qué productos tienen stock bajo?",
    },
    {
        "icono": "i-trend",
        "titulo": "Más vendidos",
        "pregunta": "¿Cuáles fueron los productos más vendidos este mes?",
    },
    {
        "icono": "i-cash",
        "titulo": "Ventas y cobros",
        "pregunta": "¿Cuánto vendí y cuánto cobré esta semana?",
    },
    {
        "icono": "i-compare",
        "titulo": "Comparación",
        "pregunta": "¿Cómo variaron las unidades vendidas este mes?",
    },
    {
        "icono": "i-clock",
        "titulo": "Cobertura de stock",
        "pregunta": "¿Qué productos tienen más días estimados de cobertura?",
    },
    {
        "icono": "i-chart",
        "titulo": "Rentabilidad",
        "pregunta": "¿Qué productos me dejaron más ganancia bruta?",
    },
]


@require_http_methods(["GET", "POST"])
def chat(request):
    pregunta = ""
    pregunta_respondida = ""
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
                pregunta_respondida = pregunta
                pregunta = ""

            except ServerError as exc:
                logger.exception("Error del servidor de Gemini")

                if exc.code == 503:
                    error = (
                        "Gemini no está disponible en este momento. "
                        "Esperá un poco y volvé a intentar."
                    )
                else:
                    error = "Gemini tuvo un problema temporal. Volvé a intentar."

            except ClientError as exc:
                logger.exception("Error de solicitud a Gemini")

                if exc.code == 429:
                    error = (
                        "Se alcanzó el límite de uso de Gemini para este modelo. "
                        "Revisá la cuota o volvé a intentarlo cuando se restablezca."
                    )
                else:
                    error = (
                        "Gemini rechazó la solicitud. "
                        "Revisá la configuración y volvé a intentar."
                    )

            except Exception:
                logger.exception("Error inesperado al consultar el agente")
                error = (
                    "No se pudo consultar el asistente. "
                    "Revisá la configuración y volvé a intentar."
                )

    return render(
        request,
        "agente/chat.html",
        {
            "nav_activo": "asistente",
            "consultas": CONSULTAS,
            "pregunta": pregunta,
            "pregunta_respondida": pregunta_respondida,
            "respuesta": respuesta,
            "error": error,
        },
    )
