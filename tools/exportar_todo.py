#!/usr/bin/env python3
"""exportar_todo.py — Script maestro que sincroniza AMBAS versiones de IN CRYPTA.

Corre los dos exportadores (JSON para JS runtime + proyecto GDevelop nativo)
y verifica que el resultado sea paridad completa con el juego pygame.

Uso:
    python tools/exportar_todo.py           # export normal
    python tools/exportar_todo.py --check   # solo verifica, no escribe
    python tools/exportar_todo.py --solo-json     # solo JSON para JS runtime
    python tools/exportar_todo.py --solo-nativo   # solo proyecto GDevelop nativo
    python tools/exportar_todo.py --solo-paridad  # solo verifica paridad del nativo
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

ENV = {
    **os.environ,
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
    "PYTHONPATH": str(ROOT),
}

SEPARADOR = "─" * 60


def correr(comando: list[str], descripcion: str) -> tuple[bool, str]:
    """Corre un comando y devuelve (éxito, salida)."""
    print(f"\n{SEPARADOR}")
    print(f"▶  {descripcion}")
    print(SEPARADOR)
    inicio = time.time()
    resultado = subprocess.run(
        comando,
        env=ENV,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    duracion = time.time() - inicio
    salida = resultado.stdout.strip()
    error = resultado.stderr.strip()
    if salida:
        print(salida)
    if error and resultado.returncode != 0:
        print(f"STDERR:\n{error}", file=sys.stderr)
    elif error:
        # pygame imprime su versión en stderr, lo mostramos solo con -v
        pass
    print(f"  ({duracion:.1f}s) {'✔ OK' if resultado.returncode == 0 else '✘ FALLO'}")
    return resultado.returncode == 0, salida


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="no escribe archivos, solo valida")
    parser.add_argument("--solo-nativo", action="store_true", help="solo genera el proyecto GDevelop nativo")
    parser.add_argument("--solo-paridad", action="store_true", help="solo verifica la paridad del proyecto nativo")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("  IN CRYPTA — Exportador maestro")
    print(f"{'='*60}")
    print(f"  Python: {PYTHON}")
    print(f"  Raíz:   {ROOT}")

    fallos: list[str] = []
    inicio_total = time.time()

    # ── Paso 2: Proyecto GDevelop nativo ─────────────────────────────
    if not args.solo_paridad:
        cmd = [PYTHON, str(TOOLS / "generar_proyecto_nativo.py")]
        ok, salida = correr(cmd, "Generando proyecto GDevelop nativo (IN_CRYPTA_NATIVO.json)")
        if not ok:
            fallos.append("generar_proyecto_nativo.py falló")
        elif "Proyecto:" not in salida:
            fallos.append("generar_proyecto_nativo.py no reportó 'Proyecto:'")

    if args.solo_nativo:
        _imprimir_resultado(fallos, inicio_total)
        return 1 if fallos else 0

    # ── Paso 3: Suite de certificación ──────────────────────────────
    # validar_eventos_gd contrasta la forma de los eventos con el núcleo real de GDevelop.
    cmd = [PYTHON, str(TOOLS / "validar_eventos_gd.py")]
    ok, salida = correr(cmd, "Validando eventos GDevelop 5.6 contra el núcleo real")
    if not ok:
        fallos.append("validar_eventos_gd.py falló")
    elif "EVENTOS_OK" not in salida:
        fallos.append("validar_eventos_gd.py no reportó EVENTOS_OK")

    # Pruebas unitarias de lógica y física Pygame (headless)
    cmd = [PYTHON, str(ROOT / "tests" / "test_logica.py")]
    ok, salida = correr(cmd, "Pruebas unitarias de lógica y física Pygame")
    if not ok:
        fallos.append("tests/test_logica.py falló")

    # Pruebas unitarias del HUD de 4 capas (headless)
    cmd = [PYTHON, str(ROOT / "tests" / "test_hud.py")]
    ok, salida = correr(cmd, "Pruebas unitarias del HUD de 4 capas")
    if not ok:
        fallos.append("tests/test_hud.py falló")

    # ── Paso 4: Verificar paridad ──────────────────────────────────────
    cmd = [PYTHON, str(TOOLS / "verificar_paridad.py")]
    ok, salida = correr(cmd, "Verificando paridad Pygame ↔ GDevelop nativo")
    if not ok:
        fallos.append("verificar_paridad.py reportó diferencias")
    elif "PARIDAD_OK" not in salida:
        fallos.append("verificar_paridad.py no reportó PARIDAD_OK")

    _imprimir_resultado(fallos, inicio_total)
    return 1 if fallos else 0


def _imprimir_resultado(fallos: list[str], inicio: float) -> None:
    duracion = time.time() - inicio
    print(f"\n{'='*60}")
    if fallos:
        print(f"  ✘ EXPORT FALLIDO ({duracion:.1f}s)")
        for f in fallos:
            print(f"    • {f}")
    else:
        print(f"  ✔ EXPORT COMPLETO ({duracion:.1f}s)")
        print("  Ambas versiones de IN CRYPTA están sincronizadas.")
        print()
        print("  export/gdevelop_nativo/IN_CRYPTA_NATIVO.json → proyecto nativo")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    raise SystemExit(main())
