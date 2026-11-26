from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def pesos(valor):
    """Formatea un importe en pesos con puntos de miles y coma decimal."""
    try:
        numero = Decimal(valor)
    except (InvalidOperation, TypeError, ValueError):
        return "$ 0"

    negativo = numero < 0
    numero = abs(numero)
    entero = int(numero)
    centavos = int((numero - entero) * 100)
    texto = f"{entero:,}".replace(",", ".")
    if centavos:
        texto = f"{texto},{centavos:02d}"
    return f"{'-' if negativo else ''}$ {texto}"
