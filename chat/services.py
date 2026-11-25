import subprocess

from django.conf import settings


class FalloIA(Exception):
    """La IA no pudo responder la consulta."""


def consultar_ia(consulta, hilo=None):
    """Devuelve la respuesta de la IA para la consulta, con el hilo previo como contexto."""
    try:
        resultado = subprocess.run(
            [
                "opencode",
                "run",
                "--model",
                "opencode-go/deepseek-v4.1-flash#low",
                _armar_prompt(consulta, hilo or []),
            ],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError as error:
        raise FalloIA from error
    except subprocess.TimeoutExpired as error:
        raise FalloIA from error
    try:
        resultado.check_returncode()
    except subprocess.CalledProcessError as error:
        raise FalloIA from error
    respuesta = resultado.stdout.strip()
    if not respuesta:
        raise FalloIA
    return respuesta


def _armar_prompt(consulta, hilo):
    if not hilo:
        return consulta
    lineas = ["Conversación previa:"]
    for intercambio in hilo:
        lineas.append(f"Vos: {intercambio['pregunta']}")
        lineas.append(f"IA: {intercambio['respuesta']}")
    lineas.append("")
    lineas.append(f"Consulta actual: {consulta}")
    return "\n".join(lineas)
