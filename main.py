#---- Importamos librerias y modulos ----#
import os
import sys
from pathlib import Path
import warnings

# Silenciamos advertencias de librerias
warnings.filterwarnings("ignore", category=UserWarning)

# Seteamos el directorio base del proyecto
RAIZ = Path(__file__).resolve().parent
os.chdir(RAIZ)
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# Si esta el entorno virtual local lo usamos directamente
venv_python = RAIZ / ".venv" / "bin" / "python"
if venv_python.exists() and sys.executable != str(venv_python) and not os.environ.get("_IN_CRYPTA_VENV_ACTIVE"):
    os.environ["_IN_CRYPTA_VENV_ACTIVE"] = "1"
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)

from juego import Juego


#---- Punto de entrada ----#
def main():
    """Inicializa el entorno, procesa argumentos CLI y ejecuta el juego."""
    nivel_inicio = None
    iniciar_tut = False
    args = [a for a in sys.argv[1:] if a not in ("--fullscreen", "-f")]
    pantalla_completa = len(args) != len(sys.argv[1:])

    # Leemos argumentos si los pasaron por consola
    if len(args) >= 1 and args[0] in ("--tutorial", "-t"):
        iniciar_tut = True
    elif len(args) >= 2 and args[0] in ("--nivel", "-n"):
        try:
            val = int(args[1])
            if val == 0:
                iniciar_tut = True
            elif 1 <= val <= 3:
                nivel_inicio = val - 1
        except ValueError:
            pass

    # Creamos la instancia del juego y arrancamos
    juego = Juego()
    if pantalla_completa:
        juego.alternar_pantalla_completa()
    if iniciar_tut:
        juego.iniciar_tutorial()
    elif nivel_inicio is not None:
        juego.seleccionar_nivel(nivel_inicio)

    juego.run()


if __name__ == "__main__":
    main()
