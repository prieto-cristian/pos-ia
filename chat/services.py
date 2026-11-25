import subprocess

from django.conf import settings


def consultar_ia(consulta, hilo=None):
    """Devuelve la respuesta de la IA para la consulta, con el hilo previo como contexto."""
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
    )
    return resultado.stdout.strip()


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
