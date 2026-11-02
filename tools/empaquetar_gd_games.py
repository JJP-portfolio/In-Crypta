#!/usr/bin/env python3
"""Compila y empaqueta el proyecto nativo de GDevelop 5.6 a HTML5 (gd.games / web).

Localiza la instalacion local de GDevelop 5.6 (Flatpak o GDEVELOP_RUNTIME_DIR),
compila ``export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`` usando el core oficial
WebAssembly (``tools/compilar_proyecto_gd.js``) y el runtime ``GDJS/Runtime``
hacia ``export/gdevelop_nativo/build/``, y genera el paquete listo para
publicar en ``export/IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip`` con ``index.html`` en
la raiz del archivo ZIP.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROYECTO_JSON = ROOT / "export" / "gdevelop_nativo" / "IN_CRYPTA_NATIVO.json"
ASSETS_DIR = ROOT / "export" / "gdevelop_nativo" / "assets"
BUILD_DIR = ROOT / "export" / "gdevelop_nativo" / "build"
ZIP_SALIDA = ROOT / "export" / "IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip"
COMPILADOR_JS = ROOT / "tools" / "compilar_proyecto_gd.js"

# Carpetas del runtime GDJS necesarias para el build HTML5
CARPETAS_RUNTIME = (
    "libs",
    "events-tools",
    "splash",
    "pixi-renderers",
    "howler-sound-manager",
    "fontfaceobserver-font-manager",
    "object-capabilities",
)

# Extensiones GDJS empleadas por IN CRYPTA
EXTENSIONES_RUNTIME = (
    "PlatformBehavior",
    "TextObject",
    "TiledSpriteObject",
)

# Orden canonico de scripts base del runtime GDJS 5.6
SCRIPTS_RUNTIME_BASE = (
    "libs/jshashtable.js",
    "logger.js",
    "gd.js",
    "libs/rbush.js",
    "AsyncTasksManager.js",
    "inputmanager.js",
    "jsonmanager.js",
    "Model3DManager.js",
    "ResourceLoader.js",
    "ResourceCache.js",
    "timemanager.js",
    "polygon.js",
    "runtimeobject.js",
    "profiler.js",
    "RuntimeInstanceContainer.js",
    "runtimescene.js",
    "scenestack.js",
    "force.js",
    "RuntimeLayer.js",
    "layer.js",
    "RuntimeCustomObjectLayer.js",
    "timer.js",
    "runtimewatermark.js",
    "named-easings-manager.js",
    "runtimegame.js",
    "variable.js",
    "variablescontainer.js",
    "oncetriggers.js",
    "runtimebehavior.js",
    "SpriteAnimator.js",
    "spriteruntimeobject.js",
    "affinetransformation.js",
    "CustomRuntimeObjectInstanceContainer.js",
    "CustomRuntimeObject.js",
    "CustomRuntimeObject2D.js",
    "indexeddb.js",
    "events-tools/commontools.js",
    "events-tools/variabletools.js",
    "events-tools/runtimescenetools.js",
    "events-tools/inputtools.js",
    "events-tools/objecttools.js",
    "events-tools/cameratools.js",
    "events-tools/soundtools.js",
    "events-tools/storagetools.js",
    "events-tools/stringtools.js",
    "events-tools/windowtools.js",
    "events-tools/networktools.js",
    "splash/gd-logo-light.js",
    "pixi-renderers/pixi.js",
    "pixi-renderers/pixi-filters-tools.js",
    "pixi-renderers/runtimegame-pixi-renderer.js",
    "pixi-renderers/runtimescene-pixi-renderer.js",
    "pixi-renderers/layer-pixi-renderer.js",
    "pixi-renderers/pixi-image-manager.js",
    "pixi-renderers/pixi-bitmapfont-manager.js",
    "pixi-renderers/spriteruntimeobject-pixi-renderer.js",
    "pixi-renderers/CustomRuntimeObject2DPixiRenderer.js",
    "pixi-renderers/DebuggerPixiRenderer.js",
    "pixi-renderers/loadingscreen-pixi-renderer.js",
    "pixi-renderers/pixi-effects-manager.js",
    "howler-sound-manager/howler.min.js",
    "howler-sound-manager/howler-sound-manager.js",
    "fontfaceobserver-font-manager/fontfaceobserver.js",
    "fontfaceobserver-font-manager/fontfaceobserver-font-manager.js",
    "Extensions/PlatformBehavior/platformerobjectruntimebehavior.js",
    "Extensions/PlatformBehavior/platformruntimebehavior.js",
    "Extensions/PlatformBehavior/platformtools.js",
    "Extensions/TextObject/textruntimeobject-pixi-renderer.js",
    "Extensions/TextObject/textruntimeobject.js",
    "Extensions/TiledSpriteObject/tiledspriteruntimeobject-pixi-renderer.js",
    "Extensions/TiledSpriteObject/tiledspriteruntimeobject.js",
    "object-capabilities/AnimatableBehavior.js",
    "object-capabilities/EffectBehavior.js",
    "object-capabilities/FlippableBehavior.js",
    "object-capabilities/OpacityBehavior.js",
    "object-capabilities/ResizableBehavior.js",
    "object-capabilities/ScalableBehavior.js",
    "object-capabilities/TextContainerBehavior.js",
)


def localizar_gdevelop_resources() -> Path:
    """Localiza el directorio ``resources`` de GDevelop 5.6 en el sistema."""
    candidatos: list[Path] = []
    env_dir = os.environ.get("GDEVELOP_RUNTIME_DIR")
    if env_dir:
        base_env = Path(env_dir).expanduser()
        candidatos.extend(
            [
                base_env,
                base_env / "resources",
                base_env
                / ".local/share/flatpak/app/io.gdevelop.ide/current/active/files/GDevelop/resources",
            ]
        )

    candidatos.extend(
        [
            Path.home()
            / ".local/share/flatpak/app/io.gdevelop.ide/current/active/files/GDevelop/resources",
            Path(
                "/var/lib/flatpak/app/io.gdevelop.ide/current/active/files/GDevelop/resources"
            ),
            Path("/opt/GDevelop/resources"),
            Path("/usr/lib/gdevelop/resources"),
        ]
    )

    for ruta in candidatos:
        if (ruta / "GDJS" / "Runtime").is_dir() and (ruta / "app.asar").is_file():
            return ruta.resolve()

    raise FileNotFoundError(
        "No se encontro la instalacion de GDevelop 5.6 (GDJS/Runtime + app.asar). "
        "Defina GDEVELOP_RUNTIME_DIR o instale el Flatpak io.gdevelop.ide."
    )


def _ignorar_mapas(_dir: str, nombres: list[str]) -> set[str]:
    return {n for n in nombres if n.endswith(".map")}


def sincronizar_runtime(runtime_dir: Path, destino: Path) -> None:
    """Copia el runtime oficial GDJS y las extensiones requeridas hacia ``destino``."""
    destino.mkdir(parents=True, exist_ok=True)

    # Limpiar archivos antiguos en la raiz de build/ (ej. code*.js previos o png sueltos)
    for item in destino.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Copiar archivos sueltos de la raiz de GDJS/Runtime (sin .map)
    for item in runtime_dir.iterdir():
        if item.is_file() and not item.name.endswith(".map"):
            shutil.copy2(item, destino / item.name)

    # Copiar carpetas principales del runtime
    for nombre_carpeta in CARPETAS_RUNTIME:
        origen = runtime_dir / nombre_carpeta
        if origen.is_dir():
            shutil.copytree(
                origen,
                destino / nombre_carpeta,
                ignore=_ignorar_mapas,
                dirs_exist_ok=True,
            )

    # Copiar extensiones utilizadas por el proyecto
    ext_destino = destino / "Extensions"
    ext_destino.mkdir(parents=True, exist_ok=True)
    for ext in EXTENSIONES_RUNTIME:
        origen_ext = runtime_dir / "Extensions" / ext
        if origen_ext.is_dir():
            shutil.copytree(
                origen_ext,
                ext_destino / ext,
                ignore=_ignorar_mapas,
                dirs_exist_ok=True,
            )


def compilar_proyecto(resources_dir: Path, destino: Path) -> str:
    """Compila ``IN_CRYPTA_NATIVO.json`` hacia ``destino`` usando ``compilar_proyecto_gd.js``."""
    if not PROYECTO_JSON.is_file():
        raise FileNotFoundError(f"No existe el proyecto nativo: {PROYECTO_JSON}")
    if not ASSETS_DIR.is_dir():
        raise FileNotFoundError(f"No existe el directorio de assets: {ASSETS_DIR}")

    proyecto = json.loads(PROYECTO_JSON.read_text(encoding="utf-8"))
    nombres_recursos = [r["name"] for r in proyecto.get("resources", {}).get("resources", [])]
    for layout in proyecto.get("layouts", []):
        layout.setdefault("usedResources", [{"name": n} for n in nombres_recursos])

    # Copiar todos los assets actualizados a build/assets/
    shutil.copytree(ASSETS_DIR, destino / "assets", dirs_exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", encoding="utf-8", delete=False
    ) as tmp:
        json.dump(proyecto, tmp, ensure_ascii=False)
        tmp_path = Path(tmp.name)

    env = os.environ.copy()
    env["GDEVELOP_RUNTIME_DIR"] = str(Path.home())
    ruta_asar = resources_dir / "app.asar"

    try:
        resultado = subprocess.run(
            [
                "node",
                str(COMPILADOR_JS),
                str(tmp_path),
                str(destino),
                str(ruta_asar),
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    if resultado.returncode != 0:
        raise RuntimeError(
            "Error al compilar IN_CRYPTA_NATIVO.json con libGD.js:\n"
            + resultado.stdout
            + "\n"
            + resultado.stderr
        )

    return resultado.stdout.strip()


def _orden_code_js(ruta: Path) -> int:
    coincidencia = re.search(r"code(\d+)\.js$", ruta.name)
    return int(coincidencia.group(1)) if coincidencia else 9999


def generar_index_html(destino: Path) -> None:
    """Genera ``index.html`` completo con todos los scripts del runtime, ``code*.js`` y ``data.js``."""
    archivos_code = sorted(destino.glob("code*.js"), key=_orden_code_js)
    if not archivos_code:
        raise RuntimeError(f"No se generaron archivos code*.js en {destino}")

    etiquetas_scripts = [
        f'\t<script src="{ruta}" crossorigin="anonymous"></script>'
        for ruta in SCRIPTS_RUNTIME_BASE
    ]
    for code_js in archivos_code:
        etiquetas_scripts.append(
            f'\t<script src="{code_js.name}" crossorigin="anonymous"></script>'
        )
    etiquetas_scripts.append('\t<script src="data.js" crossorigin="anonymous"></script>')
    bloque_scripts = "\n".join(etiquetas_scripts)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"/>
    <title>IN CRYPTA — GDevelop 5.6</title>
    <link rel="manifest" href="manifest.webmanifest">

    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

    <meta name="theme-color" content="#000000" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />

\t<style>
\t\tbody {{
\t\t\tmargin: 0;
\t\t\tpadding: 0;
\t\t\tbackground-color: #000000;
            overflow: hidden;
\t\t}}
        #canvasArea {{
            margin-left: auto;
            margin-right: auto;
            overflow: hidden;
        }}
\t</style>
    <!-- Libs and GDJS core files : -->
{bloque_scripts}
</head>
<body>
\t<script>
    (function() {{
        //Check the game files were all loaded (in a preview, they can be exported
        //again while this page is still loading them).
        if (!gdjs.projectData) {{
            throw new Error(
                "The game data was not loaded: some files of the game are missing or could not be read."
            );
        }}

        //Initialization
        var game = new gdjs.RuntimeGame(gdjs.projectData, gdjs.runtimeGameOptions || {{}});
        window.runtimeGame = game;

        //Create a renderer
        game.getRenderer().createStandardCanvas(document.body);

        //Bind keyboards/mouse/touch events
        game.getRenderer().bindStandardEvents(game.getInputManager(), window, document);

        //Load all assets and start the game
        game.loadAllAssets(function() {{
            game.startGameLoop();
        }});
    }})();
\t</script>
</body>
</html>
"""
    (destino / "index.html").write_text(html, encoding="utf-8")


def verificar_integridad_build(destino: Path) -> None:
    """Verifica que todos los scripts y recursos referenciados existan en ``destino``."""
    for carpeta in (
        "assets",
        "pixi-renderers",
        "Extensions",
        "howler-sound-manager",
        "fontfaceobserver-font-manager",
    ):
        if not (destino / carpeta).is_dir():
            raise RuntimeError(f"Falta carpeta obligatoria en build/: {carpeta}")

    for script_rel in SCRIPTS_RUNTIME_BASE:
        if not (destino / script_rel).is_file():
            raise RuntimeError(f"Falta script del runtime en build/: {script_rel}")

    if not (destino / "index.html").is_file() or not (destino / "data.js").is_file():
        raise RuntimeError("Faltan index.html o data.js en build/")

    proyecto = json.loads(PROYECTO_JSON.read_text(encoding="utf-8"))
    for recurso in proyecto.get("resources", {}).get("resources", []):
        archivo_rel = recurso.get("file", "")
        if archivo_rel and not (destino / archivo_rel).is_file():
            raise RuntimeError(f"Falta recurso del proyecto en build/: {archivo_rel}")


def empaquetar_zip(origen: Path, zip_destino: Path) -> tuple[int, int, str]:
    """Empaqueta el contenido de ``origen`` con ``index.html`` en la raiz del ZIP."""
    zip_destino.parent.mkdir(parents=True, exist_ok=True)
    if zip_destino.exists():
        zip_destino.unlink()

    archivos = sorted(p for p in origen.rglob("*") if p.is_file())
    with zipfile.ZipFile(
        zip_destino,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=False,
    ) as zf:
        for archivo in archivos:
            arcname = archivo.relative_to(origen).as_posix()
            zf.write(archivo, arcname=arcname)

    with zipfile.ZipFile(zip_destino, mode="r") as zf:
        nombres = set(zf.namelist())
        if "index.html" not in nombres or "data.js" not in nombres:
            raise RuntimeError(
                "El ZIP generado no contiene index.html o data.js en la raiz."
            )

    tamano = zip_destino.stat().st_size
    sha256 = hashlib.sha256(zip_destino.read_bytes()).hexdigest()
    return len(archivos), tamano, sha256


def main() -> int:
    resources_dir = localizar_gdevelop_resources()
    runtime_dir = resources_dir / "GDJS" / "Runtime"
    print(f"[1/4] Runtime GDevelop 5.6 detectado en: {runtime_dir}")

    print(f"[2/4] Sincronizando GDJS/Runtime hacia: {BUILD_DIR}")
    sincronizar_runtime(runtime_dir, BUILD_DIR)

    print(f"[3/4] Compilando {PROYECTO_JSON.name} con libGD.js...")
    resumen_compilacion = compilar_proyecto(resources_dir, BUILD_DIR)
    for linea in resumen_compilacion.splitlines():
        if "Compiladas" in linea or "libGD.js" in linea:
            print(f"      {linea}")
    generar_index_html(BUILD_DIR)
    verificar_integridad_build(BUILD_DIR)

    print(f"[4/4] Empaquetando build HTML5 en: {ZIP_SALIDA}")
    cantidad, tamano_bytes, sha256 = empaquetar_zip(BUILD_DIR, ZIP_SALIDA)
    tamano_mb = tamano_bytes / (1024 * 1024)

    print("\n=== RESUMEN DE EMPAQUETADO HTML5 / GD.GAMES ===")
    print(f"Proyecto origen : {PROYECTO_JSON}")
    print(f"Carpeta build   : {BUILD_DIR}")
    print(f"Archivo ZIP     : {ZIP_SALIDA}")
    print(f"Archivos en ZIP : {cantidad}")
    print(f"Tamano del ZIP  : {tamano_bytes:,} bytes ({tamano_mb:.2f} MB)")
    print(f"SHA-256         : {sha256}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
