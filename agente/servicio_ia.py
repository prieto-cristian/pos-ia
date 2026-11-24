from django.conf import settings
from google import genai
from google.genai import types

from .herramientas import listar_productos_stock_bajo


INSTRUCCIONES = """
Sos el asistente comercial de PosIA, un sistema para un comercio pequeño.

Respondé en español y de forma clara. Para preguntas sobre productos con poco
stock, consultá la herramienta disponible. Basá la respuesta en los datos
devueltos; si la consulta no permite responder, decilo claramente.

No inventes productos, cantidades ni datos comerciales.
"""


def responder(pregunta):
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("Falta configurar GEMINI_API_KEY.")

    cliente = genai.Client(api_key=settings.GEMINI_API_KEY)

    chat = cliente.chats.create(
        model=settings.GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCCIONES,
            tools=[listar_productos_stock_bajo],
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