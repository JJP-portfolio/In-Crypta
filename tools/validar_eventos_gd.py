"""Valida los eventos del export contra la API real de GDevelop 5.6.

El IDE marca en rojo los parámetros que no coinciden con la declaración de la
acción o de la condición. Para no depender de que alguien abra el IDE, este
script contrasta cada evento del export con la tabla de declaraciones de
GDevelop 5.6 y además verifica que cada objeto usado en los eventos exista en
la escena.

La tabla **no está escrita a mano**: sale del core real de GDevelop
compilado a WebAssembly (ver ``tools/exportador/extraer_metadatos.js``) y vive
en ``tools/exportador/datos/metadatos_gdevelop_5_6.json``. Por eso cuenta
correctamente los parámetros *code-only* (``objectsContext``, ``currentScene``,
``conditionInverted``), que GDevelop serializa en el JSON como cadenas vacías
en su posición exacta: omitirlos deja todos los parámetros siguientes
desplazados.

Uso:

    .venv/bin/python tools/validar_eventos_gd.py

Salida: `EVENTOS_OK` si no hay ningún error.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROYECTO = ROOT / "export" / "gdevelop_nativo" / "IN_CRYPTA_NATIVO.json"

sys.path.insert(0, str(ROOT / "tools"))

from exportador import metadatos  # noqa: E402

# Expresiones que se usan en los parámetros y cómo se escriben.
EXPRESIONES = {
    "sin": 1,
    "cos": 1,
    "TimeFromStart": 0,
    "TimeDelta": 0,
    "RandomInRange": 2,
    "min": 2,
    "max": 2,
}


def _eventos_de(evento: dict):
    """Yield (clase, instrucción) de un evento y sus subeventos."""
    if not isinstance(evento, dict):
        return
    for clave, clase in (("actions", "action"), ("conditions", "condition")):
        valor = evento.get(clave)
        if isinstance(valor, list):
            for instruccion in valor:
                yield clase, instruccion
    for clave in ("events", "subInstructions", "subevents"):
        valor = evento.get(clave)
        if isinstance(valor, list):
            for subevento in valor:
                yield from _eventos_de(subevento)


def _parece_expresion(valor: str) -> bool:
    return any(ch in valor for ch in "()+-*/ ") or valor.startswith('"')


def _objetos_de_la_escena(escena: dict) -> set[str]:
    return {objeto["name"] for objeto in escena.get("objects", [])}


def _parametros_de_objeto(metadatos_accion: list[dict]) -> list[int]:
    """Índices de los parámetros que son objetos de la escena."""
    indices = []
    for indice, parametro in enumerate(metadatos_accion):
        if parametro["c"]:
            continue
        if parametro["t"] in (
            "object",
            "objectList",
            "objectPtr",
            "objectListOrEmptyIfJustDeclared",
        ):
            indices.append(indice)
    return indices


def validar(proyecto: dict) -> list[str]:
    errores: list[str] = []
    for escena in proyecto.get("layouts", []):
        objetos = _objetos_de_la_escena(escena)
        for evento in escena.get("events", []):
            for clase, instruccion in _eventos_de(evento):
                nombre = instruccion.get("type", {}).get("value", "")
                parametros = instruccion.get("parameters", []) or []

                if not metadatos.existe(nombre, clase):
                    # La misma instrucción puede existir como acción y como
                    # condición (ej. "CameraCenterX"): se avisa sólo si no
                    # existe en ninguna clase.
                    if not metadatos.clases_disponibles(nombre):
                        errores.append(
                            f'{escena["name"]}: {clase} desconocida "{nombre}"'
                        )
                        continue
                    errores.append(
                        f'{escena["name"]}: "{nombre}" no existe como {clase} '
                        f'(existe como: {", ".join(metadatos.clases_disponibles(nombre))})'
                    )
                    continue

                firma = metadatos.parametros(nombre, clase)
                if len(parametros) != len(firma):
                    errores.append(
                        f'{escena["name"]}: "{nombre}" tiene {len(parametros)} '
                        f"parámetros y GDevelop 5.6 espera {len(firma)} "
                        f"({', '.join(p['t'] for p in firma)})"
                    )
                    continue

                for indice in _parametros_de_objeto(firma):
                    if indice >= len(parametros):
                        continue
                    valor = parametros[indice]
                    if not isinstance(valor, str) or _parece_expresion(valor):
                        continue
                    if valor not in objetos:
                        errores.append(
                            f'{escena["name"]}: "{nombre}" usa el objeto '
                            f'"{valor}", que no existe en la escena'
                        )
    return errores


def main() -> int:
    if not PROYECTO.exists():
        print(f"No existe {PROYECTO}: primero corré el generador.")
        return 1
    proyecto = json.loads(PROYECTO.read_text(encoding="utf-8"))
    errores = validar(proyecto)
    if errores:
        print(f"{len(errores)} error(es) de eventos:")
        for error in errores:
            print("  -", error)
        return 1
    print(
        "EVENTOS_OK: los eventos matchean la API de GDevelop 5.6 "
        f"({sum(metadatos.resumen().values())} metadatos reales)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
