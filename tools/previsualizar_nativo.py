"""Previsualiza el export nativo de GDevelop en el runtime real (headless).

El IDE de GDevelop no se puede automatizar (no hay herramientas de input), pero
el runtime GDJS sí: se arma una carpeta con el runtime + los assets + el
proyecto como ``data.js`` y se la abre en Chromium con chromedriver. Sirve para

* ver el juego (captura) sin abrir el IDE,
* leer la consola del navegador (si una acción o expresión no existe en
  GDevelop 5.6, el runtime lo avisa por ahí).

Uso::

    .venv/bin/python tools/previsualizar_nativo.py [--escena "Nivel 1"] [--salida /tmp/x.png]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROYECTO = ROOT / "export" / "gdevelop_nativo" / "IN_CRYPTA_NATIVO.json"
ASSETS = ROOT / "export" / "gdevelop_nativo" / "assets"
BUILD_OLD = ROOT / "export" / "gdevelop_nativo" / "build"
RUNTIME = (
    Path.home()
    / ".local/share/flatpak/app/io.gdevelop.ide/current/active/files/GDevelop"
    / "resources/GDJS/Runtime"
)
DESTINO = Path("/tmp/opencode/preview_nativo")
PUERTO_HTTP = 8931
PUERTO_WEBDRIVER = 9516
COMPILADOR = ROOT / "tools" / "compilar_proyecto_gd.js"


def _libre(puerto: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", puerto)) != 0


def _http(url: str, datos=None, metodo="GET"):
    cuerpo = None
    cabeceras = {"Content-Type": "application/json"}
    if datos is not None:
        cuerpo = json.dumps(datos).encode("utf-8")
    peticion = urllib.request.Request(url, data=cuerpo, headers=cabeceras, method=metodo)
    with urllib.request.urlopen(peticion, timeout=60) as respuesta:
        crudo = respuesta.read().decode("utf-8")
    return json.loads(crudo) if crudo else {}


def preparar_escena(escena: str | None) -> Path:
    """Arma la carpeta de previsualización y devuelve la ruta del index."""
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)
    for item in RUNTIME.iterdir():
        destino = DESTINO / item.name
        if item.is_dir():
            shutil.copytree(item, destino)
        else:
            shutil.copy2(item, destino)
    if BUILD_OLD.exists():
        for item in BUILD_OLD.iterdir():
            if item.name in ("index.html", "data.js") or item.name.startswith("code"):
                destino = DESTINO / item.name
                if not destino.exists():
                    shutil.copy2(item, destino)

    proyecto = json.loads(PROYECTO.read_text(encoding="utf-8"))
    if escena:
        proyecto["firstLayout"] = escena
    # El IDE recalcula "usedResources" al guardar; el runtime lo necesita.
    nombres = [r["name"] for r in proyecto["resources"]["resources"]]
    for layout in proyecto["layouts"]:
        layout.setdefault("usedResources", [{"name": n} for n in nombres])
    shutil.copytree(ASSETS, DESTINO / "assets", dirs_exist_ok=True)

    # Se compila el proyecto con el core real de GDevelop (sin IDE) para que
    # el preview ejecute los eventos de verdad. Los code*.js viejos que dejó
    # el IDE se descartan: si no, se correría la lógica de una versión
    # anterior del export.
    for item in DESTINO.glob("code*.js"):
        item.unlink()
    proyecto_primero = DESTINO / "_proyecto_preview.json"
    proyecto_primero.write_text(
        json.dumps(proyecto, ensure_ascii=False), encoding="utf-8"
    )
    compilacion = subprocess.run(
        ["node", str(COMPILADOR), str(proyecto_primero), str(DESTINO)],
        capture_output=True,
        text=True,
    )
    proyecto_primero.unlink()
    if compilacion.returncode != 0:
        raise RuntimeError(
            "Falló la compilación del proyecto:\n"
            + compilacion.stdout
            + compilacion.stderr
        )
    print("--- compilación ---")
    print(compilacion.stdout.strip())
    return DESTINO


def _index_html(destino: Path) -> None:
    """El index del runtime viene con placeholders: se arma la lista de scripts.

    El index del runtime de GDJS es una plantilla (no incluye gd.js ni data.js).
    Se usa como base el index de un build anterior, que ya trae la lista
    completa de scripts del runtime, y se le agregan los ``code*.js`` del
    proyecto actual.
    """
    plantilla = BUILD_OLD / "index.html"
    if plantilla.exists():
        html = plantilla.read_text(encoding="utf-8")
    else:
        html = (RUNTIME / "index.html").read_text(encoding="utf-8")

    # Quita cualquier etiqueta <script> de code*.js previa (del build viejo).
    html = re.sub(
        r'\s*<script src="code\d+\.js"[^>]*></script>\n?', "", html
    )
    # Inserta las etiquetas <script> de todos los code*.js del proyecto,
    # justo antes de data.js (o antes de </head> si no hay data.js).
    scripts = "\n".join(
        f'\t<script src="{p.name}" crossorigin="anonymous"></script>'
        for p in sorted(destino.glob("code*.js"))
    ) + "\n"
    if "data.js" in html:
        html = html.replace(
            '<script src="data.js" crossorigin="anonymous"></script>',
            scripts + '<script src="data.js" crossorigin="anonymous"></script>',
        )
    else:
        html = html.replace(
            "</head>", scripts + '\t<script src="data.js" crossorigin="anonymous"></script>\n</head>'
        )
    html = html.replace(
        "var game = new gdjs.RuntimeGame",
        "var game = window.runtimeGame = new gdjs.RuntimeGame"
    )
    (destino / "index.html").write_text(html, encoding="utf-8")


def ejecutar(escena: str | None, salida: Path | None, espera: float) -> int:
    destino = preparar_escena(escena)
    _index_html(destino)

    servidor = subprocess.Popen(
        ["python3", "-m", "http.server", str(PUERTO_HTTP), "--bind", "127.0.0.1"],
        cwd=destino,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    driver = subprocess.Popen(
        ["chromedriver", f"--port={PUERTO_WEBDRIVER}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    sesion = None
    try:
        for _ in range(60):
            if not _libre(PUERTO_WEBDRIVER) and not _libre(PUERTO_HTTP):
                break
            time.sleep(0.25)
        base = f"http://127.0.0.1:{PUERTO_WEBDRIVER}"
        for _ in range(40):
            try:
                _http(f"{base}/status")
                break
            except urllib.error.URLError:
                time.sleep(0.25)
        respuesta = _http(
            f"{base}/session",
            {
                "capabilities": {
                    "alwaysMatch": {
                        "browserName": "chrome",
                        "goog:chromeOptions": {
                            "args": [
                                "--headless=new",
                                "--no-sandbox",
                                "--disable-gpu",
                                "--window-size=1920,1080",
                                "--autoplay-policy=no-user-gesture-required",
                            ]
                        },
                    }
                }
            },
            metodo="POST",
        )
        sesion = respuesta["value"]["sessionId"]
        _http(
            f"{base}/session/{sesion}/url",
            {"url": f"http://127.0.0.1:{PUERTO_HTTP}/index.html"},
            metodo="POST",
        )
        time.sleep(espera)

        registros = _http(
            f"{base}/session/{sesion}/log", {"type": "browser"}, metodo="POST"
        )
        entradas = registros.get("value", [])
        print(f"--- consola del navegador ({len(entradas)} entradas) ---")
        for entrada in entradas[-40:]:
            print(f"[{entrada.get('level')}] {entrada.get('message')[:300]}")

        if salida:
            captura = _http(f"{base}/session/{sesion}/screenshot")
            import base64

            salida.write_bytes(base64.b64decode(captura["value"]))
            print(f"captura: {salida}")
        return 0
    finally:
        if sesion:
            try:
                _http(f"http://127.0.0.1:{PUERTO_WEBDRIVER}/session/{sesion}", metodo="DELETE")
            except Exception:
                pass
        driver.terminate()
        servidor.terminate()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--escena", default="Nivel 1", help="escena a abrir (firstLayout)")
    parser.add_argument("--salida", default="/tmp/opencode/preview_nativo.png")
    parser.add_argument("--espera", type=float, default=6.0)
    args = parser.parse_args()
    return ejecutar(args.escena, Path(args.salida), args.espera)


if __name__ == "__main__":
    raise SystemExit(main())
