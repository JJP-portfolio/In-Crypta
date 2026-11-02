#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/exportar_web_pygame.py
============================
Prepara, limpia y compila la versión WebAssembly de IN CRYPTA usando Pygbag.
Asegura paridad de código, assets limpios (sin dependencias ML / Torch),
compatibilidad estricta con nombres ASCII y presencia de .nojekyll para GitHub Pages.
"""

import argparse
import os
from pathlib import Path
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
    "assets_loader.py",
    "requirements.txt",
)


def sincronizar_archivos():
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
    if dir_audio_origen.exists():
        dir_audio_dest.mkdir(parents=True, exist_ok=True)

        # Manifiesto
        manifiesto = dir_audio_origen / "manifest_entrega.json"
        if manifiesto.exists():
            shutil.copy2(manifiesto, dir_audio_dest / "manifest_entrega.json")

        # Música (.ogg)
        musica_orig = dir_audio_origen / "musica"
        musica_dest = dir_audio_dest / "musica"
        if musica_orig.exists():
            musica_dest.mkdir(parents=True, exist_ok=True)
            for f in musica_orig.glob("*.ogg"):
                if not f.name.endswith("-pygbag.ogg"):
                    shutil.copy2(f, musica_dest / f.name)

        # SFX (.ogg y .wav, omitiendo dron_catacumbas.wav de 3.5MB por su version .ogg ligera)
        sfx_orig = dir_audio_origen / "sfx"
        sfx_dest = dir_audio_dest / "sfx"
        if sfx_orig.exists():
            sfx_dest.mkdir(parents=True, exist_ok=True)
            for f in sfx_orig.glob("*.*"):
                if f.name.endswith("-pygbag.ogg") or f.suffix not in (".wav", ".ogg"):
                    continue
                if f.name == "dron_catacumbas.wav":
                    continue  # usar dron_catacumbas.ogg
                shutil.copy2(f, sfx_dest / f.name)

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


def compilar_pygbag():
    """Ejecuta pygbag --build sobre export/web_pygame/."""
    cmd = [sys.executable, "-m", "pygbag", "--build", str(DIR_WEB)]
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


def main():
    parser = argparse.ArgumentParser(description="Pipeline de preparación y compilación web Pygbag")
    parser.add_argument("--sync-only", action="store_true", help="Solo sincroniza archivos sin compilar")
    parser.add_argument("--build", action="store_true", help="Sincroniza y compila con Pygbag")
    args = parser.parse_args()

    sincronizar_archivos()

    if args.build or not args.sync_only:
        compilar_pygbag()


if __name__ == "__main__":
    main()
