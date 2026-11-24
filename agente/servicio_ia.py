from django.conf import settings
from google import genai
from google.genai import types
from django.utils import timezone

from .herramientas import (
    listar_productos_stock_bajo,
    obtener_productos_mas_vendidos,
)


INSTRUCCIONES = """
Sos el asistente comercial de PosIA, un sistema para un comercio pequeño.

Respondé en español y de forma clara. Para preguntas sobre productos con poco
stock, consultá la herramienta disponible. Basá la respuesta en los datos
devueltos; si la consulta no permite responder, decilo claramente.

No inventes productos, cantidades ni datos comerciales.

Para preguntas sobre los productos más vendidos, usa
obtener_productos_mas_vendidos. Si el usuario no especifica un período,
considera todo el historial de ventas disponible. Si sí especifica un
período, limita la consulta a ese período. El ranking se basa en unidades
vendidas, no en importe ni rentabilidad. No pidas fechas cuando no se
indicó un período.
"""


def responder(pregunta):
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("Falta configurar GEMINI_API_KEY.")

    cliente = genai.Client(api_key=settings.GEMINI_API_KEY)
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)

    instrucciones = f"""
    {INSTRUCCIONES}

    La fecha local de hoy es {hoy.isoformat()}.
    Para "este mes", usa desde {inicio_mes.isoformat()} hasta {hoy.isoformat()},
    ambos inclusive.
    """

    chat = cliente.chats.create(
        model=settings.GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=instrucciones,
            tools=[
                listar_productos_stock_bajo,
                obtener_productos_mas_vendidos,
            ],
            thinking_config=types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.MINIMAL,
            ),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=2,
            ),
        ),
    )


    respuesta = chat.send_message(pregunta)
    return respuesta.text or "No pude generar una respuesta."