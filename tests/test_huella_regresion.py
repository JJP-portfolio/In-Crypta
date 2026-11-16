#---- Test de huella de regresion de comportamiento ----#
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from tools.huella_regresion import RUTA_BASE, capturar_huella


def test_huella_comportamiento_identica_a_linea_base():
    """Compara la simulacion determinista de cada nivel contra la huella base."""
    assert RUTA_BASE.exists(), f"falta el archivo base de huella: {RUTA_BASE}"
    esperado = json.loads(RUTA_BASE.read_text(encoding="utf-8"))
    actual = capturar_huella(incluir_pixeles=False)
    assert actual == esperado
