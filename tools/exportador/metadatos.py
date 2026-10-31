"""Metadatos reales de las instrucciones de GDevelop 5.6.

La tabla vive en ``datos/metadatos_gdevelop_5_6.json`` y se extrae del core
real de GDevelop (compilado a WebAssembly) con
``extraer_metadatos.js``. No es una lista escrita a mano: si el IDE se actualiza,
la tabla se regenera y el exportador sigue hablando el idioma correcto.

Lo importante de esta tabla es que distingue los parámetros *code-only*
(``objectsContext``, ``currentScene``, ``conditionInverted``). GDevelop los
serializa en el JSON del proyecto como cadenas vacías, **en su posición
exacta**. Omitirlos hace que el IDE lea todos los parámetros siguientes
desplazados: la acción ``Delete`` recibe el objeto donde espera la escena,
``PlaySound`` recibe el volumen donde espera el archivo, etc.
"""

from __future__ import annotations

import json
from pathlib import Path

RUTA_TABLA = Path(__file__).with_name("datos") / "metadatos_gdevelop_5_6.json"

with RUTA_TABLA.open(encoding="utf-8") as archivo:
    _TABLA: dict[str, dict] = json.load(archivo)


def _clave(tipo: str, clase: str) -> str:
    return f"{clase}:{tipo}"


def existe(tipo: str, clase: str = "action") -> bool:
    """¿El IDE conoce esta instrucción en esa clase (acción o condición)?"""
    return _clave(tipo, clase) in _TABLA


def parametros(tipo: str, clase: str = "action") -> list[dict]:
    """Firma de la instrucción: lista de ``{"t": tipo, "c": code_only}``."""
    entrada = _TABLA.get(_clave(tipo, clase))
    if entrada is None:
        return []
    return entrada["params"]


def cantidad_parametros(tipo: str, clase: str = "action") -> int:
    return len(parametros(tipo, clase))


def indices_code_only(tipo: str, clase: str = "action") -> list[int]:
    """Posiciones de los parámetros que el IDE espera pero noFilled por el usuario."""
    return [
        indice
        for indice, parametro in enumerate(parametros(tipo, clase))
        if parametro["c"]
    ]


def completar(tipo: str, valores: list[str], clase: str = "action") -> list[str]:
    """Rellena los huecos *code-only* de una lista de valores ya escrita.

    ``valores`` trae los parámetros que el usuario ve (los no code-only), en
    orden. Esta función los intercala con las cadenas vacías que el IDE espera
    en las posiciones code-only, devolviendo la lista completa y ordenada.
    """
    firma = parametros(tipo, clase)
    if not firma:
        return list(valores)

    posiciones_code_only = [i for i, p in enumerate(firma) if p["c"]]
    if not posiciones_code_only:
        return list(valores)

    # Los valores del usuario corresponden a los parámetros NO code-only.
    completada: list[str] = []
    indice_valor = 0
    for i, parametro in enumerate(firma):
        if parametro["c"]:
            completada.append("")
        else:
            completada.append(
                valores[indice_valor] if indice_valor < len(valores) else ""
            )
            indice_valor += 1
    return completada


def clases_disponibles(tipo: str) -> list[str]:
    """Clases (action/condition/expression) donde existe la instrucción."""
    return [
        clase
        for clase in ("action", "condition", "expression", "strExpression")
        if _clave(tipo, clase) in _TABLA
    ]


def function_name(tipo: str, clase: str = "action") -> str:
    entrada = _TABLA.get(_clave(tipo, clase))
    return entrada["fn"] if entrada else ""


def resumen() -> dict[str, int]:
    conteo: dict[str, int] = {}
    for clave in _TABLA:
        clase = clave.split(":", 1)[0]
        conteo[clase] = conteo.get(clase, 0) + 1
    return conteo
