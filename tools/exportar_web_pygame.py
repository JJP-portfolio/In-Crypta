#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/exportar_web_pygame.py
============================
Prepara, limpia y compila la versión WebAssembly de IN CRYPTA usando Pygbag.
Asegura paridad de código, assets limpios (sin dependencias ML / Torch),
compatibilidad estricta con nombres ASCII y presencia de .nojekyll para GitHub Pages.

Además:
  - Verifica que main.py declare pygame-ce en bloque PEP 723 (sin esto, Pygbag
    no descarga el wheel y el juego queda en pantalla gris).
  - Reemplaza el aviso #infobox de Pygbag por un botón de inicio gótico.
  - Reduce el peso de la build: no copia WAV que tengan versión OGG y recodifica
    el audio a OGG Vorbis (con ffmpeg) solo cuando el resultado es más liviano.
    Los originales no se tocan.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

RAIZ = Path(__file__).resolve().parent.parent
DIR_WEB = RAIZ / "export" / "web_pygame"
DIR_BUILD_WEB = DIR_WEB / "build" / "web"

ARCHIVOS_CORE = (
    "main.py",
    "juego.py",
    "config.py",
    "audio.py",
    "camara.py",
    "efectos.py",
    "entidades.py",
    "hud.py",
    "nivel.py",
    "niveles.py",
    "niveles_redisenados.py",
    "particulas.py",
    "requirements.txt",
)

MARCADOR_INICIO = "<!-- incrypta:inicio-gotico -->"

BLOQUE_INICIO = """
<!-- incrypta:inicio-gotico -->
<style>
  /* Eliminar estilo gris y bordes por defecto de Pygbag */
  html, body {
    background-color: #080504 !important;
    color: #e5c158;
    margin: 0;
    padding: 0;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: Georgia, "Times New Roman", serif;
  }
  .framed {
    border: none !important;
    top: 0 !important;
    right: 0 !important;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.95), 0 0 2px #e5c158 !important;
    max-width: 100vw;
    max-height: 100vh;
  }
  #infobox { display: none !important; }
  #transfer {
    position: fixed;
    bottom: 20px;
    z-index: 10001;
    color: #e5c158;
    font-family: Georgia, serif;
    font-size: 13px;
  }
  #transfer progress {
    accent-color: #e5c158;
  }

  /* Overlay gótico de presentación y carga fluida */
  #incrypta-inicio {
    position: fixed;
    inset: 0;
    z-index: 99999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle at center, rgba(22, 14, 12, 0.97) 0%, rgba(6, 4, 3, 0.99) 100%);
    transition: opacity 0.6s ease;
  }
  #incrypta-inicio.desvanecer {
    opacity: 0;
    pointer-events: none;
  }
  .incrypta-titulo {
    font-size: clamp(32px, 6vw, 64px);
    font-weight: bold;
    letter-spacing: 0.15em;
    color: #e5c158;
    text-shadow: 0 0 20px rgba(229, 193, 88, 0.45), 0 4px 10px rgba(0, 0, 0, 0.9);
    margin-bottom: 6px;
    text-transform: uppercase;
  }
  .incrypta-subtitulo {
    font-size: clamp(14px, 2.2vw, 20px);
    font-style: italic;
    color: #a3957a;
    margin-bottom: 32px;
    letter-spacing: 0.06em;
  }
  #incrypta-inicio-btn {
    cursor: pointer;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(16px, 2.5vw, 24px);
    letter-spacing: 0.1em;
    color: #e5c158;
    background: #140d0a;
    border: 2px solid #e5c158;
    border-radius: 4px;
    padding: 16px 40px;
    box-shadow: 0 0 0 3px #140d0a, 0 0 0 5px #6b5024, 0 0 30px rgba(229, 193, 88, 0.35);
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  #incrypta-inicio-btn:hover {
    transform: scale(1.04);
    box-shadow: 0 0 0 3px #140d0a, 0 0 0 5px #997433, 0 0 45px rgba(229, 193, 88, 0.65);
    background: #1f1410;
  }
  .incrypta-estado {
    margin-top: 18px;
    font-family: monospace;
    font-size: 13px;
    color: #8c826e;
    min-height: 20px;
    text-align: center;
  }
  .incrypta-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #3d301c;
    border-top: 2px solid #e5c158;
    border-radius: 50%;
    animation: incrypta-spin 0.8s linear infinite;
    display: inline-block;
    vertical-align: middle;
  }
  @keyframes incrypta-spin {
    to { transform: rotate(360deg); }
  }
</style>
<div id="incrypta-inicio">
  <div class="incrypta-titulo">IN CRYPTA</div>
  <div class="incrypta-subtitulo">El sepulturero de la cripta</div>
  <button type="button" id="incrypta-inicio-btn">
    <span>&#9876;&#65039; INICIAR JUEGO &#9876;&#65039;</span>
  </button>
  <div id="incrypta-estado" class="incrypta-estado"></div>
</div>
<script>
  (function () {
    var overlay = document.getElementById("incrypta-inicio");
    var boton = document.getElementById("incrypta-inicio-btn");
    var estado = document.getElementById("incrypta-estado");
    if (!overlay || !boton) return;

    var inicioPulsado = false;

    function esperarCanvasYDesvanecer() {
      var chequeo = setInterval(function () {
        var canvas = document.querySelector("canvas");
        if (canvas && canvas.width === 1280 && canvas.height === 720) {
          clearInterval(chequeo);
          overlay.classList.add("desvanecer");
          setTimeout(function () { overlay.remove(); }, 600);
        }
      }, 100);
    }

    boton.addEventListener("click", function () {
      if (inicioPulsado) return;
      inicioPulsado = true;
      boton.innerHTML = '<span class="incrypta-spinner"></span> <span>Cargando la cripta...</span>';
      boton.style.cursor = "default";
      if (estado) estado.innerText = "Iniciando WebAssembly y audio...";
      esperarCanvasYDesvanecer();
    });
  })();
</script>
"""


# --- Optimización de peso (solo para la copia web) ---
# Escala de ffmpeg/libvorbis (-q:a): 3 ≈ 112 kbps y 5 ≈ 160 kbps estéreo aprox.
CALIDAD_VORBIS_MUSICA = 3
CALIDAD_VORBIS_SFX = 5
# Cloudflare Pages rechaza archivos estáticos de más de 25 MiB.
LIMITE_ARCHIVO_CLOUDFLARE = 25 * 1024 * 1024


def _ffmpeg_disponible():
    return shutil.which("ffmpeg") is not None


def optimizar_a_ogg(origen, destino, calidad):
    """Codifica origen como OGG Vorbis en destino. Devuelve True si salió bien."""
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(origen),
        "-vn", "-c:a", "libvorbis", "-q:a", str(calidad), str(destino),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and destino.exists()


def copiar_audio_web(origen, carpeta_destino, calidad, optimizar):
    """Copia un audio a la build web y devuelve la ruta final.

    Con optimizar=True intenta recodificar a OGG y conserva la versión nueva solo
    si pesa menos que el original; si no, copia el original tal cual.
    """
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    if optimizar:
        destino = carpeta_destino / (origen.stem + ".ogg")
        tmp = carpeta_destino / (origen.stem + ".tmp.ogg")
        if optimizar_a_ogg(origen, tmp, calidad) and tmp.stat().st_size < origen.stat().st_size:
            tmp.replace(destino)
            return destino
        if tmp.exists():
            tmp.unlink()
    destino = carpeta_destino / origen.name
    shutil.copy2(origen, destino)
    return destino


def reporte_tamanos(carpeta, titulo, excluir_build=False, top=8):
    """Imprime el peso total y los archivos más pesados de una carpeta."""
    archivos = []
    for p in carpeta.rglob("*"):
        if not p.is_file():
            continue
        if excluir_build and "build" in p.relative_to(carpeta).parts:
            continue
        archivos.append(p)
    if not archivos:
        print(f"  [AVISO] {titulo}: no hay archivos para medir en {carpeta}")
        return
    total = sum(p.stat().st_size for p in archivos)
    print(f"\n📦 {titulo}: {total / 1024 / 1024:.2f} MiB en {len(archivos)} archivos")
    for p in sorted(archivos, key=lambda x: x.stat().st_size, reverse=True)[:top]:
        tam = p.stat().st_size
        aviso = "  ⚠ supera 25 MiB (límite de Cloudflare Pages)" if tam > LIMITE_ARCHIVO_CLOUDFLARE else ""
        print(f"   {tam / 1024 / 1024:8.2f} MiB  {p.relative_to(carpeta)}{aviso}")


def verificar_main_pep723():
    """Corta antes de compilar si main.py perdió la declaración que Pygbag necesita."""
    texto = (RAIZ / "main.py").read_text(encoding="utf-8")
    if "# /// script" not in texto or '"pygame-ce"' not in texto:
        print(
            "✘ main.py no declara pygame-ce en un bloque PEP 723. "
            "Pygbag no descargaría el wheel y el juego quedaría en pantalla gris.",
            file=sys.stderr,
        )
        sys.exit(1)
    if not re.search(r"^import pygame\b", texto, re.M):
        print("✘ main.py necesita 'import pygame' a nivel módulo.", file=sys.stderr)
        sys.exit(1)
    print("✔ main.py declara pygame-ce (PEP 723) e importa pygame.")


def sincronizar_archivos(optimizar_audio=False):
    """Copia los archivos fuente limpios hacia export/web_pygame/."""
    DIR_WEB.mkdir(parents=True, exist_ok=True)

    # 1. Copiar scripts Python core
    for nombre in ARCHIVOS_CORE:
        origen = RAIZ / nombre
        destino = DIR_WEB / nombre
        if origen.exists():
            shutil.copy2(origen, destino)
        else:
            print(f"  [AVISO] No se encontró {origen}")

    # 2. Copiar assets/
    dir_assets_origen = RAIZ / "assets"
    dir_assets_dest = DIR_WEB / "assets"
    if dir_assets_origen.exists():
        if dir_assets_dest.exists():
            shutil.rmtree(dir_assets_dest)
        shutil.copytree(dir_assets_origen, dir_assets_dest, ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))

    # 3. Copiar assets_pixelart/
    dir_px_origen = RAIZ / "assets_pixelart"
    dir_px_dest = DIR_WEB / "assets_pixelart"
    if dir_px_origen.exists():
        if dir_px_dest.exists():
            shutil.rmtree(dir_px_dest)
        shutil.copytree(dir_px_origen, dir_px_dest, ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))

    # 4. Copiar audio desde assets_in_crypta/entrega/ (excluyendo ML, logs, work y wavs pesados redundantes)
    dir_audio_origen = RAIZ / "assets_in_crypta" / "entrega"
    dir_audio_dest = DIR_WEB / "assets_in_crypta" / "entrega"
    # Se vacía la carpeta de audio: evita arrastrar copias viejas de builds anteriores.
    if dir_audio_dest.exists():
        shutil.rmtree(dir_audio_dest)
    if dir_audio_origen.exists():
        dir_audio_dest.mkdir(parents=True, exist_ok=True)

        # Manifiesto
        manifiesto = dir_audio_origen / "manifest_entrega.json"
        if manifiesto.exists():
            shutil.copy2(manifiesto, dir_audio_dest / "manifest_entrega.json")

        # Música (.ogg)
        musica_orig = dir_audio_origen / "musica"
        if musica_orig.exists():
            for f in musica_orig.glob("*.ogg"):
                if not f.name.endswith("-pygbag.ogg"):
                    copiar_audio_web(f, dir_audio_dest / "musica", CALIDAD_VORBIS_MUSICA, optimizar_audio)

        # SFX (.ogg y .wav). Un .wav con .ogg hermano no se copia: audio.py ya prefiere el .ogg.
        sfx_orig = dir_audio_origen / "sfx"
        if sfx_orig.exists():
            ogg_sfx = {f.stem for f in sfx_orig.glob("*.ogg") if not f.name.endswith("-pygbag.ogg")}
            for f in sfx_orig.glob("*.*"):
                if f.name.endswith("-pygbag.ogg") or f.suffix not in (".wav", ".ogg"):
                    continue
                if f.name == "dron_catacumbas.wav":
                    continue  # usar dron_catacumbas.ogg
                if f.suffix == ".wav" and f.stem in ogg_sfx:
                    continue  # versión OGG ya presente
                copiar_audio_web(f, dir_audio_dest / "sfx", CALIDAD_VORBIS_SFX, optimizar_audio)

    # 5. Limpieza de archivos obsoletos o conflictivos
    for basura in (
        DIR_WEB / "pipeline_in_crypta.py",
        DIR_WEB / "pipeline_in_crypta-pygbag.py",
        DIR_WEB / "audio-pygbag.py",
        DIR_WEB / "niveles_rediseñados.py",
    ):
        if basura.exists():
            basura.unlink()

    # Eliminar posibles __pycache__ dentro de DIR_WEB
    for pyc in DIR_WEB.rglob("__pycache__"):
        if "build" not in str(pyc):
            shutil.rmtree(pyc, ignore_errors=True)

    print(f"✔ Sincronización limpia completada en: {DIR_WEB}")


def personalizar_index_html():
    """Reemplaza el aviso #infobox de Pygbag por un botón de inicio gótico y elimina el fondo gris."""
    index = DIR_BUILD_WEB / "index.html"
    if not index.exists():
        print(f"✘ No se encontró {index} para personalizar.", file=sys.stderr)
        sys.exit(1)

    html = index.read_text(encoding="utf-8")

    # 1. Eliminar fondo gris (#7f7f7f), powderblue y bordes de Pygbag
    html = html.replace('platform.document.body.style.background = "#7f7f7f"', 'platform.document.body.style.background = "#080504"')
    html = html.replace('background-color: powderblue;', 'background-color: #080504;')
    html = html.replace('border: 1px solid black;', 'border: none;')

    if MARCADOR_INICIO in html:
        print("✔ index.html ya contenía el botón de inicio gótico.")
        index.write_text(html, encoding="utf-8")
        return

    if "</body>" not in html:
        print("✘ index.html no contiene </body>; no se puede insertar el botón.", file=sys.stderr)
        sys.exit(1)

    html = html.replace("</body>", BLOQUE_INICIO + "\n</body>", 1)
    index.write_text(html, encoding="utf-8")
    print(f"✔ Interfaz gótica y personalización aplicadas en: {index}")


def compilar_pygbag():
    """Ejecuta pygbag --build sobre export/web_pygame/ y asegura dependencias autónomas."""
    cmd = [sys.executable, "-m", "pygbag", "--build", "--disable-sound-format-error", str(DIR_WEB)]
    print(f"▶ Compilando WebAssembly con Pygbag: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("✘ Error al compilar con Pygbag.", file=sys.stderr)
        sys.exit(res.returncode)

    # Asegurar .nojekyll en la carpeta compilada
    DIR_BUILD_WEB.mkdir(parents=True, exist_ok=True)
    nojekyll = DIR_BUILD_WEB / ".nojekyll"
    nojekyll.touch()
    print(f"✔ Archivo .nojekyll verificado en: {nojekyll}")

    # Suministro autónomo del wheel para evitar 404 al solicitar /cdn/cp312/
    dir_cdn_whl = DIR_BUILD_WEB / "cdn" / "cp312"
    dir_cdn_whl.mkdir(parents=True, exist_ok=True)
    whl_name = "pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl"
    dest_whl = dir_cdn_whl / whl_name
    src_whl = RAIZ / "tools" / "wheels" / whl_name
    if src_whl.exists():
        shutil.copy2(src_whl, dest_whl)
        print(f"✔ Wheel local pygame-ce copiado desde {src_whl} a {dest_whl}")
    else:
        url_whl = f"https://pygame-web.github.io/cdn/cp312/{whl_name}"
        print(f"⬇ Descargando wheel autónomo desde {url_whl}...")
        import urllib.request
        urllib.request.urlretrieve(url_whl, dest_whl)
        src_whl.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest_whl, src_whl)
        print(f"✔ Wheel descargado y guardado en {dest_whl}")

    personalizar_index_html()


def main():
    parser = argparse.ArgumentParser(description="Pipeline de preparación y compilación web Pygbag")
    parser.add_argument("--sync-only", action="store_true", help="Solo sincroniza archivos sin compilar")
    parser.add_argument("--build", action="store_true", help="Sincroniza y compila con Pygbag")
    parser.add_argument(
        "--sin-optimizar-audio",
        action="store_true",
        help="Copia el audio tal cual, sin recodificar a OGG (más pesado, mismo sonido base)",
    )
    args = parser.parse_args()

    verificar_main_pep723()

    optimizar = not args.sin_optimizar_audio
    if optimizar and not _ffmpeg_disponible():
        print("⚠ ffmpeg no está instalado: el audio se copia sin recodificar.")
        optimizar = False

    sincronizar_archivos(optimizar_audio=optimizar)
    reporte_tamanos(DIR_WEB, "Fuentes web (sin build/)", excluir_build=True)

    if args.build or not args.sync_only:
        compilar_pygbag()
        reporte_tamanos(DIR_BUILD_WEB, "Build final (lo que se publica)")


if __name__ == "__main__":
    main()
