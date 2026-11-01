import sys
import tempfile
from pathlib import Path
from unittest import mock

from test_export_constantes import RAIZ  # noqa: F401  (configura sys.path y SDL)

import generar_proyecto_nativo as gen
import integrar_assets_gdevelop as integ


def probar_error_de_integracion_se_propaga():
    with tempfile.TemporaryDirectory() as tmp, \
            mock.patch.object(gen, "OUT", Path(tmp)), \
            mock.patch.object(gen, "ASSETS", Path(tmp) / "assets"), \
            mock.patch.object(gen, "generar_assets", lambda escenas: None), \
            mock.patch.object(gen, "construir_proyecto",
                              lambda escenas: {"layouts": [], "resources": {"resources": []}, "variables": []}), \
            mock.patch.object(gen, "limpiar_assets", lambda proyecto: []), \
            mock.patch.object(integ, "generar_todos_los_assets", side_effect=RuntimeError("PNG faltante")):
        try:
            gen.main()
        except RuntimeError:
            print("PASS probar_error_de_integracion_se_propaga")
            return
    print("FAIL probar_error_de_integracion_se_propaga: main() no propag\u00f3 el error")
    sys.exit(1)


if __name__ == "__main__":
    probar_error_de_integracion_se_propaga()
