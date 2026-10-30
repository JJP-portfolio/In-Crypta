#!/usr/bin/env python3
"""Instala el JSON de IN CRYPTA y el runtime jugable en un proyecto GDevelop."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
JS_POR_DEFECTO = RAIZ / "export" / "gdevelop" / "runtime_gdevelop.js"
DATOS_POR_DEFECTO = RAIZ / "export" / "gdevelop" / "game_data.json"
MARCADORES = ("INCRYPTA_GDEVELOP_RUNTIME_V1", "LUMEN_GDEVELOP_RUNTIME_V1")
FORMATO_DATOS = "incrypta.gdevelop-levels"


def _leer_json(ruta):
    with ruta.open(encoding="utf-8") as archivo:
        return json.load(archivo)


def _backup(ruta):
    sello = datetime.now().strftime("%Y%m%d-%H%M%S")
    destino = ruta.with_name(f"{ruta.name}.bak-{sello}")
    shutil.copy2(ruta, destino)
    return destino


def _buscar_layout(proyecto, nombre):
    layouts = proyecto.get("layouts") or []
    if not layouts:
        raise ValueError(
            "El proyecto no tiene escenas. Abrí GDevelop, creá una escena y guardá."
        )
    if nombre is None:
        return layouts[0]
    for layout in layouts:
        if layout.get("name") == nombre:
            return layout
    raise ValueError(f"No existe la escena {nombre!r}")


def _evento_existente(events):
    for evento in events:
        if not isinstance(evento, dict):
            continue
        inline = evento.get("inlineCode")
        if isinstance(inline, list) and any(
            marcador in linea for linea in inline for marcador in MARCADORES
        ):
            return evento
        for clave in ("events", "subEvents"):
            hijos = evento.get(clave)
            if isinstance(hijos, list):
                encontrado = _evento_existente(hijos)
                if encontrado is not None:
                    return encontrado
    return None


def _nuevo_evento(lineas):
    return {
        "type": "BuiltinCommonInstructions::JsCode",
        "inlineCode": lineas,
        "parameterObjects": "",
        "useStrict": True,
        "eventsSheetExpanded": True,
    }


def _agregar_recurso(proyecto, nombre, archivo):
    recursos = proyecto.setdefault("resources", {}).setdefault("resources", [])
    for recurso in recursos:
        if recurso.get("name") == nombre:
            recurso.update(
                {
                    "disablePreload": False,
                    "file": archivo,
                    "kind": "json",
                    "metadata": "",
                    "name": nombre,
                    "userAdded": True,
                }
            )
            return recurso
    recurso = {
        "disablePreload": False,
        "file": archivo,
        "kind": "json",
        "metadata": "",
        "name": nombre,
        "userAdded": True,
    }
    recursos.append(recurso)
    return recurso


def instalar(proyecto, lineas_js, nombre_recurso, archivo_recurso, layout_nombre):
    layout = _buscar_layout(proyecto, layout_nombre)
    eventos = layout.setdefault("events", [])
    evento = _evento_existente(eventos)
    if evento is None:
        evento = _nuevo_evento(lineas_js)
        eventos.insert(0, evento)
    else:
        evento.clear()
        evento.update(_nuevo_evento(lineas_js))

    recurso = _agregar_recurso(proyecto, nombre_recurso, archivo_recurso)

    if not proyecto.get("firstLayout"):
        proyecto["firstLayout"] = layout.get("name", "")

    return layout, recurso


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proyecto", type=Path)
    parser.add_argument("--data", type=Path, default=DATOS_POR_DEFECTO)
    parser.add_argument("--js", type=Path, default=JS_POR_DEFECTO)
    parser.add_argument("--recurso", default="game_data")
    parser.add_argument("--layout", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    proyecto_path = args.proyecto.expanduser().resolve()
    datos_path = args.data.expanduser().resolve()
    js_path = args.js.expanduser().resolve()

    if not proyecto_path.is_file():
        raise SystemExit(f"No existe el proyecto: {proyecto_path}")
    if not datos_path.is_file():
        raise SystemExit(f"No existe el JSON: {datos_path}. Corré export_gdevelop.py.")
    if not js_path.is_file():
        raise SystemExit(f"No existe el runtime JS: {js_path}")

    datos = _leer_json(datos_path)
    if datos.get("format") != FORMATO_DATOS or not datos.get("levels"):
        raise SystemExit(f"JSON inesperado: {datos_path}")

    proyecto = _leer_json(proyecto_path)
    lineas_js = js_path.read_text(encoding="utf-8").splitlines()
    archivo_relativo = "game_data.json"

    layout, recurso = instalar(
        proyecto,
        lineas_js,
        args.recurso,
        archivo_relativo,
        args.layout,
    )
    print(f"Escena: {layout.get('name')}")
    print(f"Recurso: {recurso.get('name')} -> {recurso.get('file')}")

    if args.dry_run:
        print("DRY_RUN_OK")
        return

    destino_datos = proyecto_path.parent / archivo_relativo
    if destino_datos.resolve() != datos_path:
        if destino_datos.exists():
            print(f"Backup JSON: {_backup(destino_datos)}")
        shutil.copy2(datos_path, destino_datos)

    backup = _backup(proyecto_path)
    with proyecto_path.open("w", encoding="utf-8") as archivo:
        json.dump(proyecto, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")

    print(f"Backup proyecto: {backup}")
    print(f"Datos: {destino_datos}")
    print("INSTALL_OK")


if __name__ == "__main__":
    main()
