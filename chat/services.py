import subprocess

from django.conf import settings


def consultar_ia(consulta):
    """Devuelve la respuesta de la IA para la consulta."""
    resultado = subprocess.run(
        ["opencode", "run", "--model", "opencode/deepseek-v4.1-flash-free", consulta],
        cwd=settings.BASE_DIR,
        capture_output=True,
        text=True,
    )
    return resultado.stdout.strip()
