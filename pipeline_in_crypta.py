#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_in_crypta.py
=====================

Pipeline reproducible de generación y validación de assets para IN CRYPTA.

Genera en ``assets_in_crypta/entrega/``:

  * ``sfx/``     20 SFX one-shot en WAV PCM 16-bit, 44100 Hz, estéreo,
                 con duración exacta, más ``dron_catacumbas.wav`` y
                 ``dron_catacumbas.ogg`` (bucle continuo de 20 s).
  * ``musica/``  10 pistas OGG Vorbis 44100 Hz estéreo, normalizadas a
                 -16 LUFS integrados, con duración exacta y bucles
                 continuos (stingers de 8 s y 6 s sin loop).
  * ``sprites/`` 12 tiras horizontales RGBA de pixel art, con el número
                 de cuadros y el tamaño de cuadro exactos, paleta estricta
                 de 8 colores, contorno de 1 px #09080D, fondo transparente
                 y baseline de pies compartido.

Backends
--------
``auto`` (por defecto)
    Intenta primero los modelos pedidos y, si no están disponibles o
    fallan, usa el backend determinista. Los archivos finales siempre se
    generan y se validan.

``ml``
    Exige los modelos:
      - ``facebook/audiogen-medium`` vía ``audiocraft`` para los SFX.
      - ``facebook/musicgen-medium`` vía ``audiocraft`` para la música.
      - ``stable-diffusion-v1-5/stable-diffusion-v1-5`` + LoRA
        ``PixelArtRedmond15V-PixelArt-PIXARFK`` vía ``diffusers`` para los
        sprites.

``procedural``
    No importa torch ni descarga modelos. Sintetiza audio con DSP
    (numpy/scipy) y post-procesa los sprites de referencia con Pillow.

La ruta ML requiere Python 3.11 y el stack fijado en
``requirements-assets-crypta.txt``. Ver ``--check-deps``.

Uso
---
    ./pipeline_in_crypta.py --list
    ./pipeline_in_crypta.py --backend auto
    ./pipeline_in_crypta.py --only salto,mus_titulo
    ./pipeline_in_crypta.py --skip-ml --force
    ./pipeline_in_crypta.py --validate
    ./pipeline_in_crypta.py --check-deps

El manifiesto de entrega se escribe en
``assets_in_crypta/entrega/manifest_entrega.json`` e incluye metadatos,
hashes SHA-256 y el resultado de todas las comprobaciones.

Notas de producción
--------------------
- Los modelos AudioGen/MusicGen son CC-BY-NC 4.0; Stable Diffusion 1.5
  usa CreativeML OpenRAIL-M. Revisar licencias antes de distribuir.
- El pipeline no modifica el código del juego ni los assets existentes.
- El pipeline es idempotente: sin ``--force`` conserva los archivos que ya
  existen y sólo regenera los ausentes.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

# ---------------------------------------------------------------------------
# Rutas y constantes globales
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
DELIVERY = ROOT / "assets_in_crypta" / "entrega"
SFX_DIR = DELIVERY / "sfx"
MUSIC_DIR = DELIVERY / "musica"
SPRITE_DIR = DELIVERY / "sprites"
WORK_DIR = DELIVERY / ".work"
MANIFEST_PATH = DELIVERY / "manifest_entrega.json"
LOG_PATH = DELIVERY / "pipeline.log"

SR = 44100
CHANNELS = 2
PALETTE_HEX: tuple[str, ...] = (
    "#09080D",
    "#D7CFB8",
    "#701622",
    "#5CBEAE",
    "#C69C3E",
    "#4B284B",
    "#B5B9C2",
    "#F0C45A",
)
PALETTE_RGB: tuple[tuple[int, int, int], ...] = tuple(
    tuple(int(h[i : i + 2], 16) for i in (1, 3, 5)) for h in PALETTE_HEX
)
OUTLINE_RGB = PALETTE_RGB[0]
PALETTE_IMAGE = None  # se construye perezosamente (Pillow es opcional en --list)

STYLE_BLOCK = (
    "pixel art, PixArFK, hard pixels, 8-color palette, white background. "
    "{subject}. {action}. {frames} frames, same design."
)

NEGATIVE_PROMPT = (
    "blurry, soft shading, gradients, antialiasing, smooth vector art, 3d "
    "render, photorealistic, extra limbs, deformed anatomy, duplicate "
    "character, multiple characters, text, watermark, signature, frame, "
    "border, scenery, detailed background, cropped, out of frame, low contrast"
)

MODEL_IDS = {
    "sfx": "facebook/audiogen-medium",
    "musica": "facebook/musicgen-medium",
    "sprites_base": "stable-diffusion-v1-5/stable-diffusion-v1-5",
    "sprites_lora": "artificialguybr/pixelartredmond-1-5v-pixel-art-loras-for-sd-1-5",
    "sprites_lora_file": "PixelArtRedmond15V-PixelArt-PIXARFK.safetensors",
}

LICENSES = {
    "facebook/audiogen-medium": "CC-BY-NC-4.0",
    "facebook/musicgen-medium": "CC-BY-NC-4.0",
    "stable-diffusion-v1-5/stable-diffusion-v1-5": "CreativeML-OpenRAIL-M",
    "artificialguybr/pixelartredmond-1-5v-pixel-art-loras-for-sd-1-5": (
        "Bespoke LoRA license (allow derivatives, no credit required)"
    ),
}

# ---------------------------------------------------------------------------
# Especificaciones: fuente única del pipeline
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SfxSpec:
    id: str
    file: str
    duration: float
    prompt: str
    recipe: str
    loop: bool = False
    window: str = "onset"  # onset | peak | full
    tune_hz: float | None = None
    extra_files: tuple[tuple[str, str], ...] = ()  # (ruta relativa, formato)
    peak_db: float = -3.0


@dataclass(frozen=True)
class MusicSpec:
    id: str
    file: str
    duration: float
    prompt: str
    loop: bool
    bpm: int
    progression: tuple[tuple[str, str, float], ...]
    style: str
    seed: int
    pad_instrument: str
    bass_instrument: str
    arp_instrument: str
    melody_instrument: str
    percussion: str = "none"
    ambience: str = "none"


@dataclass(frozen=True)
class SpriteSpec:
    id: str
    file: str
    subject: str
    action: str
    frames: int
    width: int
    height: int
    ref_prefix: str
    ref_count: int
    gen_scale: int = 4


SFX_SPECS: tuple[SfxSpec, ...] = (
    SfxSpec(
        "salto",
        "sfx/salto.wav",
        0.14,
        "soft rising whoosh of cloth, a quick airy hop, dusty crypt air",
        "salto",
        window="onset",
    ),
    SfxSpec(
        "dash",
        "sfx/dash.wav",
        0.18,
        "fast shadowy dash, eerie spectral swoosh with a breath of wind",
        "dash",
        window="onset",
    ),
    SfxSpec(
        "ataque",
        "sfx/ataque.wav",
        0.11,
        "short shovel swing through air, thin metal hiss",
        "ataque",
        window="peak",
    ),
    SfxSpec(
        "pala",
        "sfx/pala.wav",
        0.20,
        "heavy iron shovel hitting stone, dull metallic thud with gravel",
        "pala",
        window="peak",
    ),
    SfxSpec(
        "stomp",
        "sfx/stomp.wav",
        0.18,
        "heavy stomp on a bone-dust floor, muffled crunch of bones",
        "stomp",
        window="peak",
    ),
    SfxSpec(
        "alma_ref",
        "sfx/alma_ref.wav",
        0.22,
        "single soft glass-like bell chime, pure tone at A5 (880 Hz)",
        "alma_ref",
        window="onset",
        tune_hz=880.0,
    ),
    SfxSpec(
        "onda",
        "sfx/onda.wav",
        0.40,
        "deep rumbling shockwave of dust and bones, subsonic boom",
        "onda",
        window="peak",
    ),
    SfxSpec(
        "jefe_aviso",
        "sfx/jefe_aviso.wav",
        0.28,
        "ominous warning toll, low bell with a dissonant undertone",
        "jefe_aviso",
        window="onset",
    ),
    SfxSpec(
        "jefe_fase",
        "sfx/jefe_fase.wav",
        0.55,
        "sinister phase change, deep choir-like drone swelling and cutting off",
        "jefe_fase",
        window="onset",
    ),
    SfxSpec(
        "pala_recoger",
        "sfx/pala_recoger.wav",
        0.25,
        "metal tool pickup, short clink and bright shimmer",
        "pala_recoger",
        window="peak",
    ),
    SfxSpec(
        "dash_recoger",
        "sfx/dash_recoger.wav",
        0.28,
        "shadow amulet pickup, soft whooshing chime",
        "dash_recoger",
        window="onset",
    ),
    SfxSpec(
        "checkpoint",
        "sfx/checkpoint.wav",
        0.32,
        "lantern lighting up, warm chime with a small flicker",
        "checkpoint",
        window="onset",
    ),
    SfxSpec(
        "vida_extra",
        "sfx/vida_extra.wav",
        0.44,
        "extra life, warm reverent chord rising, no voices",
        "vida_extra",
        window="onset",
    ),
    SfxSpec(
        "ui",
        "sfx/ui.wav",
        0.06,
        "tiny dry wooden click for menus",
        "ui",
        window="peak",
    ),
    SfxSpec(
        "dano",
        "sfx/dano.wav",
        0.26,
        "low ghostly impact, short thud with a breath of pain, no human voice",
        "dano",
        window="peak",
    ),
    SfxSpec(
        "muerte",
        "sfx/muerte.wav",
        0.65,
        "gravedigger's death, descending drone fading into one bell toll",
        "muerte",
        window="onset",
    ),
    SfxSpec(
        "meta",
        "sfx/meta.wav",
        0.55,
        "heavy stone gate opening, grinding stone, rising bell resolution",
        "meta",
        window="onset",
    ),
    SfxSpec(
        "rebote_pala",
        "sfx/rebote_pala.wav",
        0.16,
        "shovel clang bouncing off iron armor, metallic ring, short tail",
        "rebote_pala",
        window="peak",
    ),
    SfxSpec(
        "corazon_latido",
        "sfx/corazon_latido.wav",
        1.0,
        "single heartbeat, lub-dub, deep and wet, no room tone",
        "corazon_latido",
        window="peak",
    ),
    SfxSpec(
        "dron_catacumbas",
        "sfx/dron_catacumbas.wav",
        20.0,
        "dark funeral drone, low sustained cello-like tone with slow beating, seamless loop, no melody",
        "dron",
        loop=True,
        window="full",
        extra_files=(("sfx/dron_catacumbas.ogg", "ogg"),),
        peak_db=-3.0,
    ),
)


def _prog(*items: tuple[str, str, float]) -> tuple[tuple[str, str, float], ...]:
    return tuple(items)


MUSIC_SPECS: tuple[MusicSpec, ...] = (
    MusicSpec(
        "mus_titulo",
        "musica/titulo.ogg",
        60.0,
        "solemn church organ and low strings, 70 BPM, melancholic title theme for a gothic crypt platformer",
        True,
        70,
        _prog(("D", "min", 15.0), ("Bb", "maj", 15.0), ("G", "min", 15.0), ("A", "maj", 15.0)),
        "titulo",
        101,
        "organ",
        "strings",
        "organ",
        "strings",
    ),
    MusicSpec(
        "mus_camposanto",
        "musica/camposanto.ogg",
        90.0,
        "graveyard exploration, sparse plucked strings, distant bell, 90 BPM, eerie but calm",
        True,
        90,
        _prog(("A", "min", 22.5), ("F", "maj", 22.5), ("C", "maj", 22.5), ("G", "maj", 22.5)),
        "camposanto",
        102,
        "strings",
        "cello",
        "pluck",
        "pluck",
        ambience="wind_bell",
    ),
    MusicSpec(
        "mus_cripta",
        "musica/cripta.ogg",
        90.0,
        "underground crypt, dripping water textures, low cello ostinato, 85 BPM, dark ambient",
        True,
        85,
        _prog(("D", "min", 22.5), ("Bb", "maj", 22.5), ("G", "min", 22.5), ("A", "min", 22.5)),
        "cripta",
        103,
        "strings",
        "cello",
        "cello",
        "cello",
        ambience="drips",
    ),
    MusicSpec(
        "mus_osario",
        "musica/osario.ogg",
        90.0,
        "ossuary, rhythmic bone percussion, dissonant brass hints, tense, 100 BPM",
        True,
        100,
        _prog(("E", "min", 22.5), ("C", "maj", 22.5), ("G", "maj", 22.5), ("B", "dim", 22.5)),
        "osario",
        104,
        "strings",
        "cello",
        "pluck",
        "organ",
        percussion="bones",
        ambience="dust",
    ),
    MusicSpec(
        "mus_carcelero",
        "musica/carcelero.ogg",
        60.0,
        "mini-boss battle, driving percussion, chain rattles, low string ostinato, 120 BPM",
        True,
        120,
        _prog(("D", "min", 15.0), ("Bb", "maj", 15.0), ("G", "min", 15.0), ("A", "maj", 15.0)),
        "carcelero",
        105,
        "strings",
        "cello",
        "cello",
        "strings",
        percussion="chains",
    ),
    MusicSpec(
        "mus_custodio_f1",
        "musica/custodio_f1.ogg",
        60.0,
        "final boss phase one, grand gothic choir-like pads, heavy drums, 110 BPM, dramatic",
        True,
        110,
        _prog(("D", "min", 15.0), ("Bb", "maj", 15.0), ("G", "min", 15.0), ("A", "maj", 15.0)),
        "custodio_f1",
        106,
        "choir",
        "cello",
        "strings",
        "choir",
        percussion="heavy",
    ),
    MusicSpec(
        "mus_custodio_f2",
        "musica/custodio_f2.ogg",
        60.0,
        "final boss phase two, same theme as phase one but faster and more desperate, 130 BPM, distorted strings",
        True,
        130,
        _prog(("D", "min", 15.0), ("Bb", "maj", 15.0), ("G", "min", 15.0), ("A", "maj", 15.0)),
        "custodio_f2",
        107,
        "distorted",
        "cello",
        "distorted",
        "distorted",
        percussion="heavy_fast",
    ),
    MusicSpec(
        "mus_victoria",
        "musica/victoria.ogg",
        8.0,
        "short triumphant but mournful stinger, bells and organ resolve",
        False,
        60,
        _prog(("D", "min", 2.0), ("Bb", "maj", 2.0), ("F", "maj", 2.0), ("D", "maj", 2.0)),
        "victoria",
        108,
        "organ",
        "strings",
        "bell",
        "bell",
        ambience="bell",
    ),
    MusicSpec(
        "mus_derrota",
        "musica/derrota.ogg",
        6.0,
        "short defeat stinger, descending strings and one toll",
        False,
        60,
        _prog(("D", "min", 2.0), ("Bb", "maj", 2.0), ("G", "min", 2.0)),
        "derrota",
        109,
        "strings",
        "cello",
        "cello",
        "strings",
        ambience="toll",
    ),
    MusicSpec(
        "mus_creditos",
        "musica/creditos.ogg",
        90.0,
        "reflective slow piano and strings, minor resolving to major",
        True,
        70,
        _prog(("C", "min", 22.5), ("Ab", "maj", 22.5), ("Eb", "maj", 22.5), ("Bb", "maj", 22.5)),
        "creditos",
        110,
        "strings",
        "cello",
        "piano",
        "piano",
    ),
)


SPRITE_SPECS: tuple[SpriteSpec, ...] = (
    SpriteSpec(
        "jugador_con_pala_idle",
        "sprites/jugador_con_pala_idle.png",
        "gaunt gravedigger in a wide black hat, crimson scarf, long dark coat, glowing pale eyes, iron shovel resting on his shoulder",
        "idle breathing, subtle bob, shovel on shoulder",
        4,
        32,
        32,
        "assets_pixelart/jugador/jugador_idle",
        4,
    ),
    SpriteSpec(
        "jugador_con_pala_run",
        "sprites/jugador_con_pala_run.png",
        "gaunt gravedigger in a wide black hat, crimson scarf, long dark coat, glowing pale eyes, iron shovel resting on his shoulder",
        "full run cycle, alternating legs, coat and scarf swaying",
        6,
        32,
        32,
        "assets_pixelart/jugador/jugador_run",
        6,
    ),
    SpriteSpec(
        "jugador_con_pala_jump",
        "sprites/jugador_con_pala_jump.png",
        "gaunt gravedigger in a wide black hat, crimson scarf, long dark coat, glowing pale eyes, iron shovel resting on his shoulder",
        "crouch and launch, then apex of the jump",
        2,
        32,
        32,
        "assets_pixelart/jugador/jugador_jump",
        2,
    ),
    SpriteSpec(
        "jugador_con_pala_caida",
        "sprites/jugador_con_pala_caida.png",
        "gaunt gravedigger in a wide black hat, crimson scarf, long dark coat, glowing pale eyes, iron shovel resting on his shoulder",
        "falling, coat lifted by the air, arms out for balance",
        2,
        32,
        32,
        "assets_pixelart/jugador/jugador_caida",
        2,
    ),
    SpriteSpec(
        "jugador_con_pala_dash",
        "sprites/jugador_con_pala_dash.png",
        "gaunt gravedigger in a wide black hat, crimson scarf, long dark coat, glowing pale eyes, iron shovel resting on his shoulder",
        "shadow dash lunge with trailing afterimages",
        3,
        32,
        32,
        "assets_pixelart/jugador/jugador_dash",
        3,
    ),
    SpriteSpec(
        "jugador_con_pala_ataque",
        "sprites/jugador_con_pala_ataque.png",
        "gaunt gravedigger in a wide black hat, crimson scarf, long dark coat, glowing pale eyes, iron shovel resting on his shoulder",
        "shovel attack: windup, impact, recovery",
        3,
        32,
        32,
        "assets_pixelart/jugador/jugador_ataque",
        3,
    ),
    SpriteSpec(
        "jugador_sin_pala_idle",
        "sprites/jugador_sin_pala_idle.png",
        "gaunt gravedigger in a wide black hat, crimson scarf, long dark coat, glowing pale eyes, empty hands",
        "idle breathing, empty hands",
        4,
        32,
        32,
        "assets_pixelart/jugador/jugador_idle_sin_pala",
        4,
    ),
    SpriteSpec(
        "jugador_sin_pala_run",
        "sprites/jugador_sin_pala_run.png",
        "gaunt gravedigger in a wide black hat, crimson scarf, long dark coat, glowing pale eyes, empty hands",
        "full run cycle, alternating legs, coat and scarf swaying",
        6,
        32,
        32,
        "assets_pixelart/jugador/jugador_run_sin_pala",
        6,
    ),
    SpriteSpec(
        "morador_walk",
        "sprites/morador_walk.png",
        "floating skeletal wraith with a bone-white skull, glowing crimson eyes and a tattered dark green shroud",
        "floating walk, tattered shroud drifting",
        4,
        26,
        26,
        "assets_pixelart/enemigos/enemy_walk",
        4,
    ),
    SpriteSpec(
        "guardia_walk",
        "sprites/guardia_walk.png",
        "heavy armored crypt guard with a bone-white skull, crimson eyes, dark green tabard and an iron sword",
        "heavy walk, sword at his side",
        4,
        26,
        26,
        "assets_pixelart/enemigos/enemymelee_walk",
        4,
    ),
    SpriteSpec(
        "carcelero_walk",
        "sprites/carcelero_walk.png",
        "hulking jailer of the ossuary, bone mask, dark robes, heavy chains and a ring of keys",
        "heavy walk dragging a chain",
        4,
        36,
        48,
        "assets_pixelart/enemigos/minijefe_walk",
        4,
    ),
    SpriteSpec(
        "custodio_walk",
        "sprites/custodio_walk.png",
        "colossal ossuary custodian, crowned skull, bone armor, gold medallion, dark violet robe and a star-shaped flail",
        "heavy walk, bone armor and flail",
        4,
        48,
        64,
        "assets_pixelart/enemigos/jefe_walk",
        4,
    ),
)

SFX_BY_ID = {s.id: s for s in SFX_SPECS}
MUSIC_BY_ID = {s.id: s for s in MUSIC_SPECS}
SPRITE_BY_ID = {s.id: s for s in SPRITE_SPECS}
ALL_BY_ID = {**SFX_BY_ID, **MUSIC_BY_ID, **SPRITE_BY_ID}


# ---------------------------------------------------------------------------
# Utilidades generales
# ---------------------------------------------------------------------------


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_dirs() -> None:
    for path in (DELIVERY, SFX_DIR, MUSIC_DIR, SPRITE_DIR, WORK_DIR):
        path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def setup_logging(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("incrypta.assets")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    try:
        ensure_dirs()
        fh = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except OSError:
        pass
    return logger


def run_cmd(cmd: Sequence[str], logger: logging.Logger, check: bool = True) -> subprocess.CompletedProcess:
    logger.debug("$ %s", " ".join(str(c) for c in cmd))
    proc = subprocess.run(
        [str(c) for c in cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"Comando falló ({proc.returncode}): {' '.join(str(c) for c in cmd)}\n"
            f"STDERR:\n{proc.stderr[-4000:]}"
        )
    return proc


def which(tool: str) -> str | None:
    return shutil.which(tool)


def ffprobe_json(path: Path, logger: logging.Logger | None = None) -> dict[str, Any]:
    if not which("ffprobe"):
        raise RuntimeError("ffprobe no está instalado")
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,size,bit_rate:stream=index,codec_name,codec_type,sample_rate,channels,channel_layout,bits_per_sample,duration",
        "-of",
        "json",
        str(path),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe falló para {path}: {proc.stderr.strip()}")
    return json.loads(proc.stdout or "{}")


def ffmpeg_measure_lufs(path: Path) -> dict[str, float]:
    """Mide loudness integrada y true peak con ebur128 (estable en audios cortos)."""
    if not which("ffmpeg"):
        raise RuntimeError("ffmpeg no está instalado")
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i",
        str(path),
        "-af",
        "ebur128=peak=true",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    text = proc.stdout + "\n" + proc.stderr
    # El resumen final de ebur128 tiene líneas "I: -16.0 LUFS" y "Peak: -1.2 dBFS".
    matches = re.findall(r"I:\s*(-?(?:\d+(?:\.\d+)?|inf))\s*LUFS", text)
    peaks = re.findall(r"Peak:\s*(-?(?:\d+(?:\.\d+)?|inf))\s*dBFS", text)
    if not matches:
        # Fallback con loudnorm.
        cmd2 = [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ]
        proc2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        text2 = proc2.stderr
        blocks = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", text2, re.S)
        if blocks:
            data = json.loads(blocks[-1])
            lu = float(data.get("input_i", "nan"))
            tp = float(data.get("input_tp", "nan"))
            return {"lufs": lu, "true_peak_db": tp, "method": "loudnorm"}
        raise RuntimeError(f"No se pudo medir loudness de {path}")
    lu = float(matches[-1]) if matches[-1] not in ("inf", "-inf") else float("nan")
    tp = float(peaks[-1]) if peaks and peaks[-1] not in ("inf", "-inf") else float("nan")
    return {"lufs": lu, "true_peak_db": tp, "method": "ebur128"}


# ---------------------------------------------------------------------------
# Audio: E/S y utilidades DSP
# ---------------------------------------------------------------------------

try:
    import numpy as np
except Exception as exc:  # pragma: no cover - se informa en --check-deps
    np = None  # type: ignore[assignment]
    _NUMPY_IMPORT_ERROR = exc
else:
    _NUMPY_IMPORT_ERROR = None

try:
    import soundfile as sf
except Exception:  # pragma: no cover
    sf = None  # type: ignore[assignment]


def _require_numpy() -> None:
    if np is None:
        raise RuntimeError(
            "numpy es obligatorio para el pipeline. Instalá las dependencias con "
            "--check-deps y el stack de requirements-assets-crypta.txt."
        )


def read_wav(path: Path) -> tuple["np.ndarray", int]:
    _require_numpy()
    if sf is not None:
        data, sr = sf.read(str(path), dtype="float64", always_2d=True)
        return data, int(sr)
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())
    if width != 2:
        raise RuntimeError(f"WAV no PCM16: {path}")
    data = np.frombuffer(raw, dtype="<i2").astype("float64") / 32768.0
    data = data.reshape(-1, channels)
    return data, int(sr)


def write_wav(path: Path, data: "np.ndarray", sr: int = SR, subtype: str = "PCM_16") -> None:
    _require_numpy()
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = np.asarray(data, dtype="float64")
    if arr.ndim == 1:
        arr = np.column_stack([arr, arr])
    if arr.shape[1] != CHANNELS:
        raise ValueError(f"Se esperaban {CHANNELS} canales, llegaron {arr.shape[1]}")
    arr = np.clip(arr, -1.0, 1.0)
    if sf is not None:
        sf.write(str(path), arr, sr, subtype=subtype, format="WAV")
        return
    pcm = np.round(arr * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def make_stereo(mono: "np.ndarray", width_ms: float = 0.0) -> "np.ndarray":
    """Convierte mono a estéreo; width_ms>0 añade una decorrelación Haas sutil."""
    _require_numpy()
    mono = np.asarray(mono, dtype="float64").reshape(-1)
    if width_ms <= 0:
        return np.column_stack([mono, mono])
    delay = max(1, int(SR * width_ms / 1000.0))
    right = np.concatenate([np.zeros(delay, dtype="float64"), mono[:-delay]]) if delay < len(mono) else mono.copy()
    return np.column_stack([mono, right])


def normalize_peak(data: "np.ndarray", peak_db: float = -3.0) -> "np.ndarray":
    _require_numpy()
    peak = float(np.max(np.abs(data))) if data.size else 0.0
    if peak < 1e-12:
        return data.astype("float64")
    gain = (10.0 ** (peak_db / 20.0)) / peak
    return np.clip(data.astype("float64") * gain, -1.0, 1.0)


def _soft_limit(data: "np.ndarray", ceiling: float = 0.891, knee: float = 0.75) -> "np.ndarray":
    """Limitador sample-wise para loops: no introduce discontinuidad de borde."""
    _require_numpy()
    x = np.asarray(data, dtype="float64")
    absx = np.abs(x)
    knee_val = ceiling * knee
    out = x.copy()
    over = absx > knee_val
    if np.any(over):
        span = max(1e-9, ceiling - knee_val)
        out[over] = np.sign(x[over]) * (
            knee_val + span * np.tanh((absx[over] - knee_val) / span)
        )
    return out


def rms_db(data: "np.ndarray") -> float:
    _require_numpy()
    if data.size == 0:
        return -120.0
    rms = float(np.sqrt(np.mean(np.square(data.astype("float64")))))
    return 20.0 * math.log10(max(rms, 1e-12))


def fade_edges(data: "np.ndarray", fade_in_s: float = 0.002, fade_out_s: float = 0.01) -> "np.ndarray":
    _require_numpy()
    out = data.astype("float64").copy()
    n = out.shape[0]
    ni = min(n, max(0, int(fade_in_s * SR)))
    no = min(n, max(0, int(fade_out_s * SR)))
    if ni > 0:
        out[:ni] *= np.linspace(0.0, 1.0, ni)[:, None]
    if no > 0:
        out[-no:] *= np.linspace(1.0, 0.0, no)[:, None]
    return out


def _t(n: int) -> "np.ndarray":
    return np.arange(n, dtype="float64") / float(SR)


def _sine(freq: float, n: int, phase: float = 0.0) -> "np.ndarray":
    return np.sin(2.0 * math.pi * freq * _t(n) + phase)


def _saw(freq: float, n: int, detune: float = 0.0) -> "np.ndarray":
    t = _t(n)
    return 2.0 * np.mod((freq * (1.0 + detune)) * t, 1.0) - 1.0


def _sweep(f0: float, f1: float, n: int, curve: str = "exp") -> "np.ndarray":
    if n <= 0:
        return np.zeros(0, dtype="float64")
    if curve == "exp" and f0 > 0 and f1 > 0:
        freqs = np.geomspace(f0, f1, n)
    else:
        freqs = np.linspace(f0, f1, n)
    phase = 2.0 * math.pi * np.cumsum(freqs) / float(SR)
    return np.sin(phase)


def _exp_env(n: int, tau: float) -> "np.ndarray":
    return np.exp(-_t(n) / max(1e-6, tau))


def _adsr_env(n: int, attack: float, release: float, curve: float = 3.0) -> "np.ndarray":
    if n <= 0:
        return np.zeros(0, dtype="float64")
    na = min(n, max(1, int(attack * SR)))
    nr = min(n - na, max(1, int(release * SR))) if n > na else 0
    env = np.ones(n, dtype="float64")
    if na > 0:
        env[:na] = np.linspace(0.0, 1.0, na) ** (1.0 / curve)
    if nr > 0:
        env[-nr:] *= np.linspace(1.0, 0.0, nr) ** curve
    return env


def _filter(x: "np.ndarray", kind: str, cutoff: float | tuple[float, float], order: int = 2) -> "np.ndarray":
    """Filtro Butterworth; si scipy no está, devuelve x sin filtrar."""
    _require_numpy()
    try:
        from scipy.signal import butter, sosfilt
    except Exception:
        return x
    nyq = SR / 2.0
    if isinstance(cutoff, tuple):
        lo, hi = cutoff
        wn = [max(1e-4, min(0.999, lo / nyq)), max(1e-4, min(0.999, hi / nyq))]
        sos = butter(order, wn, btype="band", output="sos")
    else:
        wn = max(1e-4, min(0.999, cutoff / nyq))
        sos = butter(order, wn, btype=kind, output="sos")
    return sosfilt(sos, x)


def _lowpass(x: "np.ndarray", cutoff: float, order: int = 2) -> "np.ndarray":
    return _filter(x, "low", cutoff, order)


def _highpass(x: "np.ndarray", cutoff: float, order: int = 2) -> "np.ndarray":
    return _filter(x, "high", cutoff, order)


def _bandpass(x: "np.ndarray", lo: float, hi: float, order: int = 2) -> "np.ndarray":
    return _filter(x, "band", (lo, hi), order)


def _noise(n: int, rng: "np.random.Generator") -> "np.ndarray":
    return rng.standard_normal(n)


def _circular_lowpass_noise(n: int, rng: "np.random.Generator", cutoff: float = 300.0) -> "np.ndarray":
    """Ruido periódico de longitud n (loop exacto) con caída espectral suave."""
    noise = rng.standard_normal(n)
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    spec *= 1.0 / (1.0 + (freqs / max(1.0, cutoff)) ** 4)
    out = np.fft.irfft(spec, n)
    peak = float(np.max(np.abs(out))) if out.size else 0.0
    if peak > 1e-12:
        out /= peak
    return out


def _bell(
    freq: float,
    n: int,
    decay: float = 0.2,
    ratios: Sequence[float] = (1.0, 2.01, 2.76, 5.4, 8.93),
    amps: Sequence[float] = (1.0, 0.5, 0.35, 0.2, 0.12),
    phase: float = 0.3,
) -> "np.ndarray":
    t = _t(n)
    out = np.zeros(n, dtype="float64")
    for idx, (ratio, amp) in enumerate(zip(ratios, amps)):
        d = decay / (1.0 + 0.35 * idx)
        out += amp * np.sin(2.0 * math.pi * freq * ratio * t + phase * idx) * np.exp(-t / max(1e-5, d))
    return out


def _metal(freqs: Sequence[float], n: int, decay: float = 0.15, amps: Sequence[float] | None = None) -> "np.ndarray":
    t = _t(n)
    out = np.zeros(n, dtype="float64")
    if amps is None:
        amps = tuple(1.0 / (1.0 + i) for i in range(len(freqs)))
    for idx, (freq, amp) in enumerate(zip(freqs, amps)):
        out += amp * np.sin(2.0 * math.pi * freq * t + idx * 0.7) * np.exp(-t / max(1e-5, decay / (1.0 + 0.2 * idx)))
    return out


def _place(dest: "np.ndarray", src: "np.ndarray", start_s: float) -> "np.ndarray":
    start = max(0, int(start_s * SR))
    if start >= len(dest):
        return dest
    end = min(len(dest), start + len(src))
    dest[start:end] += src[: end - start]
    return dest


def _soft_clip(x: "np.ndarray", drive: float = 1.0) -> "np.ndarray":
    return np.tanh(x * drive) / math.tanh(drive) if drive > 0 else x


def _reverb(
    data: "np.ndarray",
    decay_s: float = 1.2,
    mix: float = 0.18,
    seed: int = 0,
    circular: bool = False,
) -> "np.ndarray":
    """Reverb por convolución con IR sintética; si circular, envuelve la cola."""
    _require_numpy()
    try:
        from scipy.signal import fftconvolve
    except Exception:
        return data
    n = data.shape[0]
    if n == 0:
        return data
    ir_n = max(8, min(int(decay_s * SR), n))
    rng = np.random.default_rng(seed)
    t = np.arange(ir_n, dtype="float64") / SR
    wet = np.zeros_like(data, dtype="float64")
    for ch in range(data.shape[1]):
        ir = rng.standard_normal(ir_n) * np.exp(-t / max(1e-4, decay_s / 3.0))
        ir[: max(1, int(0.005 * SR))] *= np.linspace(0.0, 1.0, max(1, int(0.005 * SR)))
        ir /= max(1e-9, float(np.sqrt(np.sum(ir * ir))))
        full = fftconvolve(data[:, ch], ir, mode="full")
        y = full[:n].copy()
        if circular and len(full) > n:
            tail = full[n:]
            m = min(len(tail), n)
            y[:m] += tail[:m]
        wet[:, ch] = y
    out = (1.0 - mix) * data + mix * wet
    peak = float(np.max(np.abs(out))) if out.size else 0.0
    if peak > 1.0:
        out /= peak
    return out


def _loop_fix(data: "np.ndarray", crossfade_s: float = 0.05) -> "np.ndarray":
    """Fuerza continuidad del empalme final->inicio (crossfade + sello)."""
    _require_numpy()
    # _loop_seal está definida más abajo; a esta función sólo se la llama en
    # tiempo de ejecución, cuando el módulo ya está completamente cargado.
    return _loop_seal(data, xf_s=crossfade_s, seal_ms=4.0)


def loop_seam_metrics(data: "np.ndarray") -> dict[str, float]:
    """Mide discontinuidad en el empalme circular (valores bajos = continuo)."""
    _require_numpy()
    if data.shape[0] < 4:
        return {"sample_jump": 0.0, "slope_error": 0.0}
    x = data.astype("float64")
    jump = float(np.max(np.abs(x[0] - x[-1])))
    d_before = x[-1] - x[-2]
    d_after = x[1] - x[0]
    slope = float(np.max(np.abs(d_before - d_after)))
    return {"sample_jump": jump, "slope_error": slope}


# ---------------------------------------------------------------------------
# Sintetizador procedural de SFX
# ---------------------------------------------------------------------------


def _sfx_salto(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    env = np.minimum(1.0, t / 0.008) * np.exp(-t / 0.055)
    cloth = _bandpass(_noise(n, rng), 450.0, 3200.0) * env
    air = _sweep(220.0, 520.0, n) * env * 0.35
    return cloth * 0.9 + air


def _sfx_dash(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    env = np.minimum(1.0, t / 0.005) * np.exp(-t / 0.07)
    wind = _bandpass(_noise(n, rng), 700.0, 5200.0) * env
    breath = _sweep(520.0, 130.0, n) * env * 0.45
    return wind * 0.85 + breath


def _sfx_ataque(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    env = np.minimum(1.0, t / 0.003) * np.exp(-t / 0.035)
    air = _highpass(_noise(n, rng), 1800.0) * env
    metal = _sine(1750.0, n) * np.exp(-t / 0.02) * 0.35
    return air * 0.8 + metal


def _sfx_pala(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    thud = _sweep(105.0, 52.0, n) * np.exp(-t / 0.055) * 1.0
    metal = _metal((310.0, 780.0, 1290.0, 2140.0), n, decay=0.07) * 0.45
    gravel = _bandpass(_noise(n, rng), 300.0, 2400.0) * np.exp(-t / 0.045) * 0.5
    return thud + metal + gravel


def _sfx_stomp(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    thump = _sweep(80.0, 38.0, n) * np.exp(-t / 0.075)
    crunch = np.zeros(n, dtype="float64")
    for i, start in enumerate((0.0, 0.035, 0.075, 0.115)):
        m = max(8, int(0.035 * SR))
        burst = _bandpass(_noise(m, rng), 500.0, 4200.0) * np.exp(-_t(m) / 0.012) * (0.45 - i * 0.07)
        _place(crunch, burst, start)
    return thump * 0.9 + crunch


def _sfx_alma_ref(n: int, rng: "np.random.Generator") -> "np.ndarray":
    return _bell(880.0, n, decay=0.16, ratios=(1.0, 2.0, 3.01, 4.98, 7.02), amps=(1.0, 0.3, 0.12, 0.06, 0.03))


def _sfx_onda(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    sub = _sweep(58.0, 24.0, n) * np.exp(-t / 0.18)
    rumble = _lowpass(_noise(n, rng), 170.0) * np.exp(-t / 0.13) * 0.75
    dust = _bandpass(_noise(n, rng), 250.0, 1800.0) * np.exp(-t / 0.07) * 0.22
    return sub + rumble + dust


def _sfx_jefe_aviso(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    bell = _bell(110.0, n, decay=0.2, ratios=(1.0, 2.03, 3.1, 5.2), amps=(1.0, 0.45, 0.25, 0.12))
    dissonant = _bell(116.5, n, decay=0.22, ratios=(1.0, 2.2, 3.7), amps=(0.6, 0.25, 0.12))
    return bell + dissonant * 0.75


def _sfx_jefe_fase(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    swell = np.minimum(1.0, t / 0.18) * np.minimum(1.0, (n / SR - t) / 0.06)
    freqs = (82.4, 110.0, 164.8, 220.0, 246.9)
    out = np.zeros(n, dtype="float64")
    for idx, f in enumerate(freqs):
        out += _saw(f, n, detune=(idx - 2) * 0.0015) * (0.28 / (1.0 + idx * 0.35))
    out = _lowpass(out, 1600.0) * swell
    return out + _lowpass(_noise(n, rng), 500.0) * swell * 0.12


def _sfx_pala_recoger(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    clink = _metal((1620.0, 2480.0, 3720.0, 5100.0), n, decay=0.09) * 0.8
    shimmer = _bell(2860.0, n, decay=0.1, ratios=(1.0, 1.5, 2.2), amps=(0.35, 0.2, 0.1))
    return clink + shimmer * np.exp(-t / 0.12)


def _sfx_dash_recoger(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    whoosh = _bandpass(_noise(n, rng), 500.0, 4500.0) * np.minimum(1.0, t / 0.01) * np.exp(-t / 0.09)
    chime = _bell(740.0, n, decay=0.13, ratios=(1.0, 2.0, 3.0), amps=(0.5, 0.2, 0.1))
    return whoosh * 0.7 + chime * 0.8


def _sfx_checkpoint(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    warm = _bell(523.25, n, decay=0.18, ratios=(1.0, 2.0, 3.0, 4.0), amps=(0.6, 0.3, 0.15, 0.08))
    warm += _bell(659.25, n, decay=0.16, ratios=(1.0, 2.0, 3.0), amps=(0.3, 0.15, 0.07))
    flicker = _bandpass(_noise(n, rng), 900.0, 3800.0) * (0.05 + 0.05 * np.sin(2.0 * math.pi * 23.0 * t)) * np.exp(-t / 0.15)
    return warm + flicker


def _sfx_vida_extra(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    out = np.zeros(n, dtype="float64")
    for idx, f in enumerate((261.63, 329.63, 392.0, 523.25)):
        start = idx * 0.055
        seg = _adsr_env(n, 0.02, 0.2) * (np.sin(2.0 * math.pi * f * t) + 0.35 * np.sin(4.0 * math.pi * f * t))
        _place(out, seg, start)
    out *= np.minimum(1.0, t / 0.01) * np.exp(-np.maximum(0.0, t - 0.18) / 0.16)
    return out * 0.7 + _bell(1046.5, n, decay=0.16, ratios=(1.0, 2.0, 3.0), amps=(0.25, 0.1, 0.05))


def _sfx_ui(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    click = _bandpass(_noise(n, rng), 700.0, 5000.0) * np.exp(-t / 0.006)
    wood = _sine(870.0, n) * np.exp(-t / 0.012) * 0.55
    return click * 0.8 + wood


def _sfx_dano(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    thud = _sweep(95.0, 55.0, n) * np.exp(-t / 0.08)
    breath = _bandpass(_noise(n, rng), 350.0, 2500.0) * np.minimum(1.0, t / 0.03) * np.exp(-t / 0.11) * 0.45
    ghost = _sine(220.0, n) * np.exp(-t / 0.1) * 0.18
    return thud + breath + ghost


def _sfx_muerte(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    drone = _sweep(220.0, 55.0, n) * np.exp(-t / 0.35)
    drone += _saw(110.0, n) * np.exp(-t / 0.28) * 0.18
    out = drone * 0.55
    toll = _bell(196.0, max(8, int(0.24 * SR)), decay=0.22, ratios=(1.0, 2.0, 2.76, 5.4), amps=(0.6, 0.3, 0.15, 0.07))
    _place(out, toll, 0.38)
    return out


def _sfx_meta(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    grind = _lowpass(_noise(n, rng), 900.0) * (0.35 + 0.3 * np.sin(2.0 * math.pi * 13.0 * t)) * np.exp(-t / 0.3)
    rising = np.zeros(n, dtype="float64")
    for idx, f in enumerate((220.0, 277.18, 329.63, 440.0)):
        _place(rising, _bell(f, max(8, int(0.3 * SR)), decay=0.2, ratios=(1.0, 2.0, 3.0), amps=(0.35, 0.15, 0.07)), 0.12 + idx * 0.06)
    return grind * 0.7 + rising * 0.8


def _sfx_rebote_pala(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    clang = _metal((1240.0, 1860.0, 2490.0, 3170.0, 4420.0), n, decay=0.1, amps=(1.0, 0.7, 0.5, 0.3, 0.15))
    ring = _sine(2480.0, n) * np.exp(-t / 0.075) * 0.18
    return clang + ring


def _sfx_corazon_latido(n: int, rng: "np.random.Generator") -> "np.ndarray":
    t = _t(n)
    out = np.zeros(n, dtype="float64")
    for start, freq, amp in ((0.0, 55.0, 1.0), (0.13, 48.0, 0.8)):
        k = max(8, int(0.2 * SR))
        tk = _t(k)
        beat = np.sin(2.0 * math.pi * freq * tk) * np.exp(-tk / 0.055) * amp
        wet = _lowpass(_noise(k, rng), 180.0) * np.exp(-tk / 0.035) * 0.18 * amp
        _place(out, beat + wet, start)
    # Sin cola de sala: silencio tras el segundo latido.
    out *= np.minimum(1.0, t / 0.004)
    out[t > 0.42] *= np.exp(-(t[t > 0.42] - 0.42) / 0.06)
    return out


def _sfx_dron(n: int, rng: "np.random.Generator") -> "np.ndarray":
    """Dron de 20 s periódico exacto: frecuencias múltiplos de 1/20 Hz."""
    t = _t(n)
    period = n / SR
    base = 55.0
    # Frecuencias periódicas sobre la ventana completa.
    f_beat = base + 1.0 / period
    tonal = (
        0.55 * np.sin(2.0 * math.pi * base * t)
        + 0.38 * np.sin(2.0 * math.pi * f_beat * t + 0.7)
        + 0.22 * np.sin(2.0 * math.pi * 110.0 * t + 0.2)
        + 0.12 * np.sin(2.0 * math.pi * 164.8 * t + 1.1)
        + 0.07 * np.sin(2.0 * math.pi * 220.0 * t + 2.0)
    )
    lfo = 0.62 + 0.38 * np.sin(2.0 * math.pi * (1.0 / period) * t)
    noise = _circular_lowpass_noise(n, rng, cutoff=260.0) * (0.22 + 0.08 * np.sin(2.0 * math.pi * (2.0 / period) * t))
    cello = _saw(base * 2.0, n, detune=0.0009) * 0.05
    out = tonal * lfo + noise * 0.35 + cello
    return _lowpass(out, 1800.0)


_SFX_RECIPES = {
    "salto": _sfx_salto,
    "dash": _sfx_dash,
    "ataque": _sfx_ataque,
    "pala": _sfx_pala,
    "stomp": _sfx_stomp,
    "alma_ref": _sfx_alma_ref,
    "onda": _sfx_onda,
    "jefe_aviso": _sfx_jefe_aviso,
    "jefe_fase": _sfx_jefe_fase,
    "pala_recoger": _sfx_pala_recoger,
    "dash_recoger": _sfx_dash_recoger,
    "checkpoint": _sfx_checkpoint,
    "vida_extra": _sfx_vida_extra,
    "ui": _sfx_ui,
    "dano": _sfx_dano,
    "muerte": _sfx_muerte,
    "meta": _sfx_meta,
    "rebote_pala": _sfx_rebote_pala,
    "corazon_latido": _sfx_corazon_latido,
    "dron": _sfx_dron,
}


def synth_sfx_procedural(spec: SfxSpec) -> "np.ndarray":
    _require_numpy()
    n = int(round(spec.duration * SR))
    rng = np.random.default_rng(0xC0FFEE + sum(ord(c) for c in spec.id))
    mono = _SFX_RECIPES[spec.recipe](n, rng)
    mono = np.asarray(mono, dtype="float64")[:n]
    if len(mono) < n:
        mono = np.pad(mono, (0, n - len(mono)))
    if spec.id == "alma_ref":
        # Refuerza la fundamental A5 para que la validación espectral sea inequívoca.
        t = _t(n)
        ref = np.sin(2.0 * math.pi * 880.0 * t) * np.exp(-t / 0.16)
        mono = 0.55 * mono / max(1e-9, np.max(np.abs(mono))) + 0.45 * ref
    stereo = make_stereo(mono)
    if spec.loop:
        stereo = _reverb(stereo, decay_s=1.2, mix=0.12, seed=7, circular=True)
        stereo = _loop_fix(stereo, crossfade_s=0.03)
    else:
        stereo = fade_edges(stereo, 0.002, min(0.02, spec.duration * 0.2))
        if spec.id != "corazon_latido":
            stereo = _reverb(stereo, decay_s=0.45, mix=0.08, seed=7)
    return normalize_peak(stereo, spec.peak_db)


# ---------------------------------------------------------------------------
# Música procedural determinista
# ---------------------------------------------------------------------------

NOTE_PC = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

CHORD_INTERVALS = {
    "min": (0, 3, 7, 10),
    "maj": (0, 4, 7, 11),
    "dim": (0, 3, 6, 9),
    "aug": (0, 4, 8, 11),
    "sus": (0, 5, 7, 10),
}


def midi_to_freq(midi: float) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def _chord_midi(root: str, quality: str, octave: int) -> list[int]:
    pc = NOTE_PC[root]
    base = 12 * (octave + 1) + pc
    return [base + i for i in CHORD_INTERVALS.get(quality, CHORD_INTERVALS["min"])]


def _instrument(inst: str, freq: float, n: int, seed: int = 0) -> "np.ndarray":
    """Renderiza una nota mono con envolvente y timbre deterministas."""
    _require_numpy()
    if n <= 0:
        return np.zeros(0, dtype="float64")
    t = _t(n)
    rng = np.random.default_rng(seed)
    inst = inst.lower()
    dur = n / SR

    def env(attack: float, release: float, curve: float = 2.0) -> "np.ndarray":
        return _adsr_env(n, min(attack, dur * 0.45), min(release, dur * 0.55), curve)

    if inst == "organ":
        x = (
            np.sin(2 * math.pi * freq * t)
            + 0.55 * np.sin(2 * math.pi * 2 * freq * t + 0.2)
            + 0.35 * np.sin(2 * math.pi * 3 * freq * t + 0.4)
            + 0.22 * np.sin(2 * math.pi * 4 * freq * t + 0.1)
            + 0.12 * np.sin(2 * math.pi * 6 * freq * t + 0.6)
        )
        x *= 1.0 + 0.04 * np.sin(2 * math.pi * 4.5 * t)
        return x * env(0.06, 0.25, 1.6) * 0.5

    if inst in ("strings", "distorted"):
        x = (
            _saw(freq, n, detune=-0.003)
            + _saw(freq, n, detune=0.0)
            + _saw(freq, n, detune=0.003)
        ) / 3.0
        x *= 1.0 + 0.03 * np.sin(2 * math.pi * 5.0 * t)
        x = _lowpass(x, 2200.0)
        if inst == "distorted":
            x = _soft_clip(x * 2.4, 1.1)
            x = _lowpass(x, 3200.0)
        return x * env(0.18, 0.35, 1.8) * 0.38

    if inst == "cello":
        x = _saw(freq, n, detune=-0.0015) * 0.7 + _saw(freq, n, detune=0.0015) * 0.3
        x *= 1.0 + 0.035 * np.sin(2 * math.pi * 4.6 * t)
        x = _lowpass(x, 1100.0)
        return x * env(0.1, 0.25, 1.5) * 0.45

    if inst == "choir":
        x = np.zeros(n, dtype="float64")
        for mult, amp in ((1.0, 0.5), (2.0, 0.22), (3.0, 0.12), (4.0, 0.07)):
            f = freq * mult
            # Tres formantes vocales aproximados (sin voces reales).
            for formant, fw, fa in ((700.0, 180.0, 1.0), (1220.0, 260.0, 0.65), (2600.0, 500.0, 0.3)):
                if f < formant + 3 * fw:
                    x += amp * fa * np.sin(2 * math.pi * f * t + 0.3 * mult) * math.exp(
                        -((f - formant) ** 2) / (2 * fw * fw)
                    )
        x *= 1.0 + 0.03 * np.sin(2 * math.pi * 3.7 * t)
        return x * env(0.35, 0.5, 1.5) * 0.7

    if inst == "pluck":
        x = np.zeros(n, dtype="float64")
        for k in range(1, 8):
            if freq * k > 9000:
                break
            x += (1.0 / (k ** 1.25)) * np.sin(2 * math.pi * freq * k * t + k * 0.3) * np.exp(-t / (0.55 / k ** 0.7))
        x += _lowpass(_noise(n, rng), 3000.0) * np.exp(-t / 0.02) * 0.08
        return x * env(0.003, 0.15, 2.0) * 0.45

    if inst == "bell":
        return _bell(freq, n, decay=0.9, ratios=(1.0, 2.0, 2.76, 5.4, 8.9), amps=(0.55, 0.25, 0.15, 0.08, 0.04)) * env(
            0.002, 0.7, 2.0
        )

    if inst == "piano":
        x = np.zeros(n, dtype="float64")
        for k in range(1, 7):
            if freq * k > 12000:
                break
            x += (1.0 / (k ** 1.15)) * np.sin(2 * math.pi * freq * k * t + k * 0.15) * np.exp(-t / (1.3 / k ** 0.5))
        x += 0.35 * np.sin(2 * math.pi * freq * 1.002 * t) * np.exp(-t / 1.1)
        return x * env(0.004, 0.35, 2.2) * 0.42

    if inst == "kick":
        x = _sweep(125.0, 42.0, n) * np.exp(-t / 0.12)
        x += _lowpass(_noise(n, rng), 180.0) * np.exp(-t / 0.02) * 0.2
        return x * 0.9

    if inst == "drum_low":
        x = _sweep(85.0, 50.0, n) * np.exp(-t / 0.32)
        return x * 0.8

    if inst == "snare":
        x = _bandpass(_noise(n, rng), 1200.0, 7000.0) * np.exp(-t / 0.07)
        x += 0.25 * np.sin(2 * math.pi * 185.0 * t) * np.exp(-t / 0.05)
        return x * 0.55

    if inst == "bone":
        x = _bandpass(_noise(n, rng), 350.0, 5000.0) * np.exp(-t / 0.025)
        x += 0.3 * np.sin(2 * math.pi * 820.0 * t) * np.exp(-t / 0.035)
        return x * 0.5

    if inst == "chain":
        x = _highpass(_noise(n, rng), 1800.0) * np.exp(-t / 0.09)
        x += _metal((2350.0, 3470.0, 4810.0), n, decay=0.12) * 0.35
        return x * 0.45

    if inst == "drip":
        x = _sweep(1500.0, 650.0, n) * np.exp(-t / 0.06)
        x += _bandpass(_noise(n, rng), 1500.0, 6000.0) * np.exp(-t / 0.012) * 0.2
        return x * 0.35

    if inst == "toll":
        return _bell(98.0, n, decay=1.4, ratios=(1.0, 2.0, 2.76, 5.4), amps=(0.8, 0.35, 0.18, 0.08)) * env(
            0.002, min(1.0, dur * 0.7), 2.0
        )

    # Fallback: seno suave.
    return np.sin(2 * math.pi * freq * t) * env(0.02, 0.2) * 0.3


class ProceduralMusic:
    """Compositor determinista con loop circular exacto."""

    def __init__(self, spec: MusicSpec):
        _require_numpy()
        self.spec = spec
        self.n = int(round(spec.duration * SR))
        self.buf = np.zeros((self.n, 2), dtype="float64")
        self.rng = np.random.default_rng(spec.seed)
        self.bar = 240.0 / float(spec.bpm)
        self.total_seg = sum(seg[2] for seg in spec.progression)
        if abs(self.total_seg - spec.duration) > 1e-6:
            raise ValueError(
                f"{spec.id}: la progresión suma {self.total_seg}s, se esperaban {spec.duration}s"
            )

    def add_note(
        self,
        start_s: float,
        dur_s: float,
        midi: float,
        inst: str,
        vel: float = 0.3,
        pan: float = 0.0,
        seed: int = 0,
    ) -> None:
        if dur_s <= 0.01:
            return
        n = max(8, int(dur_s * SR))
        freq = midi_to_freq(midi)
        mono = _instrument(inst, freq, n, seed=seed)
        mono = np.asarray(mono, dtype="float64")[:n]
        if len(mono) < n:
            mono = np.pad(mono, (0, n - len(mono)))
        # Paneo de potencia constante.
        theta = (max(-1.0, min(1.0, pan)) + 1.0) * math.pi / 4.0
        left = mono * vel * math.cos(theta)
        right = mono * vel * math.sin(theta)
        start = int(round(start_s * SR))
        # Wrap circular: las notas que cruzan el fin reaparecen al inicio.
        offset = 0
        while offset < n:
            idx = (start + offset) % self.n
            take = min(n - offset, self.n - idx)
            self.buf[idx : idx + take, 0] += left[offset : offset + take]
            self.buf[idx : idx + take, 1] += right[offset : offset + take]
            offset += take

    def _segments(self) -> list[tuple[float, float, str, str]]:
        out: list[tuple[float, float, str, str]] = []
        cursor = 0.0
        for root, quality, dur in self.spec.progression:
            out.append((cursor, float(dur), root, quality))
            cursor += float(dur)
        return out

    def _add_ambience(self) -> None:
        spec = self.spec
        if spec.ambience == "none":
            return
        if spec.ambience in ("wind_bell", "dust"):
            cut = 180.0 if spec.ambience == "dust" else 500.0
            wind = _circular_lowpass_noise(self.n, self.rng, cutoff=cut)
            wind = wind * (0.03 + 0.012 * np.sin(2.0 * math.pi * (4.0 / spec.duration) * _t(self.n)))
            self.buf[:, 0] += wind
            self.buf[:, 1] += np.roll(wind, 137)
            if spec.ambience == "wind_bell":
                for start in (7.5, 30.0, 52.5, 75.0):
                    self.add_note(start, 3.5, 74, "bell", vel=0.16, pan=0.3, seed=spec.seed + 1)
        elif spec.ambience == "drips":
            for i in range(10):
                start = (i * 8.7 + 2.3) % max(1.0, spec.duration - 0.5)
                self.add_note(start, 0.35, 96 + (i % 5), "drip", vel=0.18, pan=-0.45 + (i % 3) * 0.45, seed=spec.seed + i)
            drone = np.sin(2.0 * math.pi * 41.2 * _t(self.n)) * 0.035
            self.buf[:, 0] += drone
            self.buf[:, 1] += np.roll(drone, 211)
        elif spec.ambience == "bell":
            self.add_note(0.4, 2.0, 74, "bell", vel=0.28, pan=0.0, seed=spec.seed)
            self.add_note(3.8, 2.6, 62, "bell", vel=0.2, pan=-0.2, seed=spec.seed + 1)
        elif spec.ambience == "toll":
            self.add_note(4.0, 1.9, 38, "toll", vel=0.35, pan=0.0, seed=spec.seed)

    def _add_percussion(self) -> None:
        spec = self.spec
        if spec.percussion == "none":
            return
        bar = self.bar
        beat = bar / 4.0
        n_bars = int(math.ceil(spec.duration / bar))
        for b in range(n_bars):
            base = b * bar
            if spec.percussion == "bones":
                for k in range(8):
                    self.add_note(base + k * beat / 2.0, 0.12, 72, "bone", vel=0.12 + 0.03 * (k % 3), pan=-0.3 + 0.2 * (k % 3), seed=spec.seed + b * 11 + k)
                self.add_note(base, 0.5, 48, "drum_low", vel=0.3, pan=0.0, seed=spec.seed + b)
                self.add_note(base + 2 * beat, 0.5, 48, "drum_low", vel=0.24, pan=0.0, seed=spec.seed + b + 1)
            elif spec.percussion == "chains":
                self.add_note(base, 0.4, 45, "kick", vel=0.45, pan=0.0, seed=spec.seed + b)
                self.add_note(base + 2 * beat, 0.4, 45, "kick", vel=0.4, pan=0.0, seed=spec.seed + b + 1)
                self.add_note(base + beat, 0.25, 60, "snare", vel=0.32, pan=0.2, seed=spec.seed + b + 2)
                self.add_note(base + 3 * beat, 0.25, 60, "snare", vel=0.3, pan=-0.2, seed=spec.seed + b + 3)
                for k in range(4):
                    self.add_note(base + k * beat + 0.25, 0.2, 84, "chain", vel=0.16, pan=-0.5 + k * 0.3, seed=spec.seed + b * 7 + k)
            elif spec.percussion in ("heavy", "heavy_fast"):
                self.add_note(base, 0.5, 41, "drum_low", vel=0.5, pan=0.0, seed=spec.seed + b)
                self.add_note(base + 2 * beat, 0.5, 41, "drum_low", vel=0.42, pan=0.0, seed=spec.seed + b + 1)
                self.add_note(base + beat, 0.3, 60, "snare", vel=0.34, pan=0.2, seed=spec.seed + b + 2)
                self.add_note(base + 3 * beat, 0.3, 60, "snare", vel=0.32, pan=-0.2, seed=spec.seed + b + 3)
                if spec.percussion == "heavy_fast":
                    for k in range(8):
                        self.add_note(base + k * beat / 2.0, 0.12, 72, "bone", vel=0.08, pan=-0.3 + 0.1 * (k % 3), seed=spec.seed + b * 13 + k)

    def _add_melody(self) -> None:
        spec = self.spec
        if spec.style not in ("titulo", "creditos", "custodio_f1", "custodio_f2", "victoria", "derrota"):
            return
        # Motivo determinista sobre la escala de cada acorde.
        scale_min = (0, 2, 3, 5, 7, 8, 10)
        scale_maj = (0, 2, 4, 5, 7, 9, 11)
        cursor = 0.0
        motif_idx = 0
        for root, quality, dur in spec.progression:
            scale = scale_maj if quality == "maj" else scale_min
            base_pc = NOTE_PC[root]
            # Dos o tres notas largas por segmento, con silencios.
            count = 3 if spec.style in ("titulo", "creditos") else 2
            for k in range(count):
                frac = (k + 0.5) / count
                start = cursor + dur * frac * 0.82
                step = (motif_idx * 3 + k * 2 + spec.seed) % len(scale)
                midi = 12 * 5 + ((base_pc + scale[step]) % 12)
                length = min(dur * 0.35, 3.2)
                self.add_note(start, length, midi, spec.melody_instrument, vel=0.2 + 0.02 * (k % 2), pan=0.15, seed=spec.seed + motif_idx * 5 + k)
                motif_idx += 1
            cursor += dur
        if spec.style == "creditos":
            # Picardy third: resolución mayor al final del loop.
            last_start = spec.duration - 8.0
            for midi in (60, 64, 67, 72):
                self.add_note(last_start, 7.5, midi, "organ", vel=0.2, pan=0.0, seed=spec.seed + midi)

    def render(self) -> "np.ndarray":
        spec = self.spec
        segments = self._segments()
        # Pads, bajo y arpegios.
        for seg_idx, (start, dur, root, quality) in enumerate(segments):
            chord = _chord_midi(root, quality, 3)
            for n_idx, midi in enumerate(chord):
                self.add_note(start, dur * 0.98, midi, spec.pad_instrument, vel=0.2 - 0.015 * n_idx, pan=-0.25 + 0.17 * n_idx, seed=spec.seed + seg_idx * 7 + n_idx)
            # Bajo: raíz cada dos tiempos.
            steps = max(1, int(dur / (self.bar / 2.0)))
            for k in range(steps):
                midi = chord[0] - 12
                self.add_note(start + k * (self.bar / 2.0), self.bar * 0.45, midi, spec.bass_instrument, vel=0.28, pan=0.0, seed=spec.seed + seg_idx * 13 + k)
            # Arpegio.
            pattern = (0, 1, 2, 3, 2, 1) if quality != "dim" else (0, 1, 2, 1, 0, 2)
            step = 60.0 / spec.bpm / 2.0
            total_steps = max(1, int(dur / step))
            for k in range(total_steps):
                midi = chord[pattern[k % len(pattern)]] + 12
                self.add_note(start + k * step, step * 0.8, midi, spec.arp_instrument, vel=0.13 + 0.02 * (k % 4 == 0), pan=-0.35 + 0.1 * (k % 7), seed=spec.seed + seg_idx * 100 + k)
        self._add_melody()
        self._add_percussion()
        self._add_ambience()
        # Reverb: circular para loops, normal para stingers.
        self.buf = _reverb(self.buf, decay_s=1.6, mix=0.2, seed=spec.seed, circular=spec.loop)
        if spec.loop:
            self.buf = _loop_fix(self.buf, crossfade_s=0.02)
        else:
            self.buf = fade_edges(self.buf, 0.01, min(0.8, spec.duration * 0.12))
        return normalize_peak(self.buf, -1.0)


def synth_music_procedural(spec: MusicSpec) -> "np.ndarray":
    return ProceduralMusic(spec).render()


# ---------------------------------------------------------------------------
# Dependencias y backend ML
# ---------------------------------------------------------------------------


def dependency_report() -> list[dict[str, Any]]:
    modules = [
        ("numpy", "numpy"),
        ("PIL", "Pillow"),
        ("soundfile", "soundfile"),
        ("scipy", "scipy"),
        ("torch", "torch"),
        ("torchaudio", "torchaudio"),
        ("audiocraft", "audiocraft"),
        ("diffusers", "diffusers"),
        ("transformers", "transformers"),
        ("accelerate", "accelerate"),
        ("peft", "peft"),
        ("pydub", "pydub"),
    ]
    report = []
    for mod, label in modules:
        try:
            m = __import__(mod)
            version = getattr(m, "__version__", "?")
            report.append({"module": label, "ok": True, "version": str(version)})
        except Exception as exc:
            report.append({"module": label, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
    report.append({"module": "ffmpeg", "ok": which("ffmpeg") is not None, "version": (which("ffmpeg") or "")})
    report.append({"module": "ffprobe", "ok": which("ffprobe") is not None, "version": (which("ffprobe") or "")})
    return report


def check_dependencies(require_ml: bool = False) -> tuple[bool, list[dict[str, Any]]]:
    report = dependency_report()
    core = {"numpy", "Pillow", "ffmpeg", "ffprobe", "soundfile"}
    ml = {"torch", "torchaudio", "audiocraft", "diffusers", "transformers", "accelerate", "peft"}
    ok = all(item["ok"] for item in report if item["module"] in core)
    if require_ml:
        ok = ok and all(item["ok"] for item in report if item["module"] in ml)
    return ok, report


def _torch_device(requested: str) -> str:
    import torch

    if requested == "cpu":
        return "cpu"
    if requested in ("auto", "cuda"):
        if torch.cuda.is_available():
            return "cuda"
        if requested == "cuda":
            raise RuntimeError("Se pidió --device cuda pero torch.cuda.is_available() es False")
    return "cpu"


def _resample(x: "np.ndarray", sr_in: int, sr_out: int = SR) -> "np.ndarray":
    _require_numpy()
    x = np.asarray(x, dtype="float64")
    if sr_in == sr_out:
        return x
    try:
        from scipy.signal import resample_poly

        g = math.gcd(int(sr_in), int(sr_out))
        return resample_poly(x, sr_out // g, sr_in // g)
    except Exception:
        n_out = int(round(len(x) * sr_out / sr_in))
        if n_out <= 1:
            return x
        return np.interp(np.linspace(0, len(x) - 1, n_out), np.arange(len(x)), x)


def _audio_tensor_to_numpy(wav: Any) -> tuple["np.ndarray", int]:
    """Convierte la salida de audiocraft a (canales, muestras) float64."""
    _require_numpy()
    arr = wav
    try:
        arr = arr.detach().cpu().float().numpy()
    except Exception:
        arr = np.asarray(arr, dtype="float64")
    arr = np.asarray(arr, dtype="float64")
    if arr.ndim == 1:
        arr = arr[None, :]
    elif arr.ndim > 2:
        arr = arr.reshape(arr.shape[0], -1)
    return arr, 0


class AudioGenBackend:
    def __init__(self, device: str, cache_dir: Path, logger: logging.Logger):
        self.device = device
        self.cache_dir = cache_dir
        self.logger = logger
        self.model: Any = None
        self.torch: Any = None

    def load(self) -> None:
        import torch
        from audiocraft.models import AudioGen

        self.torch = torch
        os.environ.setdefault("AUDIOCRAFT_CACHE_DIR", str(self.cache_dir / "audiocraft"))
        self.logger.info("Cargando AudioGen medium (%s) en %s", MODEL_IDS["sfx"], self.device)
        self.model = AudioGen.get_pretrained(MODEL_IDS["sfx"], device=self.device)

    def generate(self, prompt: str, duration: float, seed: int) -> tuple["np.ndarray", int]:
        assert self.model is not None
        self.torch.manual_seed(seed)
        if self.torch.cuda.is_available():
            self.torch.cuda.manual_seed_all(seed)
        self.model.set_generation_params(
            duration=float(duration),
            use_sampling=True,
            top_k=250,
            top_p=0.0,
            temperature=1.0,
            cfg_coef=3.0,
            two_step_cfg=False,
            extend_stride=min(2.0, max(0.5, duration / 10.0)),
        )
        with self.torch.inference_mode():
            wav = self.model.generate([prompt], progress=False)[0]
        arr, _ = _audio_tensor_to_numpy(wav)
        sr = int(getattr(self.model, "sample_rate", 16000))
        return arr, sr

    def close(self) -> None:
        self.model = None
        try:
            import torch

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass


class MusicGenBackend:
    def __init__(self, device: str, cache_dir: Path, logger: logging.Logger):
        self.device = device
        self.cache_dir = cache_dir
        self.logger = logger
        self.model: Any = None
        self.torch: Any = None

    def load(self) -> None:
        import torch
        from audiocraft.models import MusicGen

        self.torch = torch
        os.environ.setdefault("AUDIOCRAFT_CACHE_DIR", str(self.cache_dir / "audiocraft"))
        self.logger.info("Cargando MusicGen medium (%s) en %s", MODEL_IDS["musica"], self.device)
        self.model = MusicGen.get_pretrained(MODEL_IDS["musica"], device=self.device)

    def generate(self, prompt: str, duration: float, seed: int) -> tuple["np.ndarray", int]:
        assert self.model is not None
        self.torch.manual_seed(seed)
        if self.torch.cuda.is_available():
            self.torch.cuda.manual_seed_all(seed)
        self.model.set_generation_params(
            duration=float(duration),
            use_sampling=True,
            top_k=250,
            top_p=0.0,
            temperature=1.0,
            cfg_coef=3.0,
            two_step_cfg=False,
            extend_stride=min(18.0, max(2.0, duration / 3.0)),
        )
        with self.torch.inference_mode():
            wav = self.model.generate([prompt], progress=False)[0]
        arr, _ = _audio_tensor_to_numpy(wav)
        sr = int(getattr(self.model, "sample_rate", 32000))
        return arr, sr

    def close(self) -> None:
        self.model = None
        try:
            import torch

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass


def _ml_generate_window(
    arr: "np.ndarray",
    sr_in: int,
    n: int,
    mode: str,
    rng: "np.random.Generator",
) -> "np.ndarray":
    """Remuestrea y elige la ventana de n muestras más adecuada."""
    _require_numpy()
    # Mezcla a mono para la selección, pero conserva canales si los hay.
    mono = arr.mean(axis=0) if arr.shape[0] > 1 else arr[0]
    mono = _resample(mono, sr_in, SR)
    if len(mono) < 8:
        raise RuntimeError("El modelo devolvió audio vacío")
    if mode == "full":
        start = 0
    elif mode == "peak":
        start = int(np.argmax(np.abs(mono))) - n // 5
    else:  # onset
        env = np.abs(mono)
        win = max(1, int(0.004 * SR))
        env = np.convolve(env, np.ones(win) / win, mode="same")
        thresh = 0.18 * float(np.max(env))
        idxs = np.flatnonzero(env >= thresh)
        start = int(idxs[0]) - int(0.004 * SR) if len(idxs) else 0
    start = max(0, min(len(mono) - 1, start))
    end = start + n
    if end > len(mono):
        start = max(0, len(mono) - n)
        end = start + n
    window = mono[start:end]
    if len(window) < n:
        window = np.pad(window, (0, n - len(window)))
    return window


def _enforce_tone(mono: "np.ndarray", freq: float) -> "np.ndarray":
    _require_numpy()
    n = len(mono)
    t = _t(n)
    ref = _bell(freq, n, decay=0.16, ratios=(1.0, 2.0, 3.01, 4.98), amps=(1.0, 0.35, 0.15, 0.06))
    base = mono / max(1e-9, float(np.max(np.abs(mono))))
    return 0.45 * base + 0.55 * ref


def _enforce_heartbeat(mono: "np.ndarray") -> "np.ndarray":
    _require_numpy()
    n = len(mono)
    t = _t(n)
    out = np.zeros(n, dtype="float64")
    for start, freq, amp in ((0.0, 55.0, 1.0), (0.13, 48.0, 0.8)):
        k = max(8, int(0.2 * SR))
        tk = _t(k)
        beat = np.sin(2.0 * math.pi * freq * tk) * np.exp(-tk / 0.055) * amp
        _place(out, beat, start)
    base = mono / max(1e-9, float(np.max(np.abs(mono))))
    return 0.45 * base + 0.55 * out


def _tile_with_crossfade(x: "np.ndarray", n: int, xf_s: float = 1.5) -> "np.ndarray":
    """Repite x con crossfades equal-power hasta cubrir n muestras."""
    _require_numpy()
    x = np.asarray(x, dtype="float64")
    if x.shape[0] == 0:
        return np.zeros((n, 2), dtype="float64")
    if len(x) >= n:
        return x[:n].copy()
    xf = max(8, int(xf_s * SR))
    out = x.copy()
    while len(out) < n:
        m = min(xf, len(x), len(out))
        fade_in = np.sin(np.linspace(0, math.pi / 2, m))[:, None]
        fade_out = np.cos(np.linspace(0, math.pi / 2, m))[:, None]
        head = x[:m] * fade_in
        out[-m:] = out[-m:] * fade_out + head
        out = np.vstack([out, x[m:]])
    return out[:n].copy()


def _loop_seal(x: "np.ndarray", xf_s: float = 1.5, seal_ms: float = 4.0) -> "np.ndarray":
    """Crossfade final->inicio + sello de 4 ms para discontinuidad cero."""
    _require_numpy()
    out = x.copy()
    n = out.shape[0]
    xf = min(n // 2, max(8, int(xf_s * SR)))
    if xf > 0:
        fade = np.linspace(0.0, 1.0, xf)[:, None]
        out[-xf:] = out[-xf:] * (1.0 - fade) + out[:xf] * fade
    seal = min(n, max(2, int(seal_ms * SR / 1000.0)))
    fade2 = np.linspace(0.0, 1.0, seal)[:, None]
    out[-seal:] = out[-seal:] * (1.0 - fade2) + out[0] * fade2
    out[-1] = out[0]
    return out


def postprocess_ml_sfx(spec: SfxSpec, arr: "np.ndarray", sr_in: int, seed: int) -> "np.ndarray":
    _require_numpy()
    n = int(round(spec.duration * SR))
    rng = np.random.default_rng(seed)
    if spec.loop:
        # Para el dron tomamos los primeros 20 s y forzamos el loop.
        channels = []
        for ch in range(arr.shape[0]):
            y = _resample(arr[ch], sr_in, SR)
            if len(y) < n:
                y = np.tile(y, int(math.ceil(n / max(1, len(y)))))
            channels.append(y[:n])
        mono = np.mean(np.column_stack(channels), axis=1) if channels else np.zeros(n)
        mono = _lowpass(mono, 2000.0)
        mono = mono / max(1e-9, float(np.max(np.abs(mono))))
        stereo = make_stereo(mono)
        stereo = _loop_seal(stereo, xf_s=2.0, seal_ms=5.0)
        return normalize_peak(stereo, spec.peak_db)
    mono = _ml_generate_window(arr, sr_in, n, spec.window, rng)
    if spec.tune_hz:
        mono = _enforce_tone(mono, spec.tune_hz)
    if spec.id == "corazon_latido":
        mono = _enforce_heartbeat(mono)
    stereo = make_stereo(mono, width_ms=0.0)
    stereo = fade_edges(stereo, 0.0015, min(0.02, spec.duration * 0.25))
    # Un toque de reverb corto para integrar la fuente; no para el latido.
    if spec.id not in ("corazon_latido", "ui"):
        stereo = _reverb(stereo, decay_s=0.35, mix=0.06, seed=seed)
    return normalize_peak(stereo, spec.peak_db)


def _spectral_flatness(x: "np.ndarray") -> float:
    _require_numpy()
    if len(x) < 1024:
        return 0.0
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)))) + 1e-9
    return float(np.exp(np.mean(np.log(spec))) / np.mean(spec))


def postprocess_ml_music(spec: MusicSpec, arr: "np.ndarray", sr_in: int, seed: int) -> "np.ndarray":
    _require_numpy()
    n = int(round(spec.duration * SR))
    # Convierte a estéreo 44.1k.
    chans = []
    for ch in range(min(2, arr.shape[0])):
        chans.append(_resample(arr[ch], sr_in, SR))
    if not chans:
        raise RuntimeError("MusicGen devolvió audio vacío")
    if len(chans) == 1:
        stereo = make_stereo(chans[0])
    else:
        m = min(len(chans[0]), len(chans[1]))
        stereo = np.column_stack([chans[0][:m], chans[1][:m]])
    if stereo.shape[0] < n:
        stereo = _tile_with_crossfade(stereo, n, xf_s=1.5)
    else:
        stereo = stereo[:n].copy()
    if spec.loop:
        stereo = _loop_seal(stereo, xf_s=1.5, seal_ms=5.0)
    else:
        stereo = fade_edges(stereo, 0.01, min(0.9, spec.duration * 0.12))
    stereo = normalize_peak(stereo, -1.0)
    flat = _spectral_flatness(stereo.mean(axis=1))
    if flat > 0.82:
        raise RuntimeError(f"Salida de MusicGen demasiado plana/no musical (flatness={flat:.2f})")
    return stereo


# ---------------------------------------------------------------------------
# Codificación OGG y normalización de loudness
# ---------------------------------------------------------------------------


def encode_ogg(src_wav: Path, dst_ogg: Path, logger: logging.Logger, quality: int = 6) -> None:
    if not which("ffmpeg"):
        raise RuntimeError("ffmpeg no está instalado")
    dst_ogg.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(src_wav),
        "-ar",
        str(SR),
        "-ac",
        str(CHANNELS),
        "-c:a",
        "libvorbis",
        "-q:a",
        str(quality),
        str(dst_ogg),
    ]
    run_cmd(cmd, logger)


def normalize_ogg_to_lufs(
    src_wav: Path,
    dst_ogg: Path,
    logger: logging.Logger,
    target_lufs: float = -16.0,
    tolerance: float = 0.25,
    max_iters: int = 4,
    loop: bool = False,
) -> dict[str, Any]:
    """Codifica y ajusta ganancia midiendo el OGG final (no el WAV fuente).

    Para loops se aplica ganancia y limitación suave *antes* de codificar, en
    el dominio PCM.  Así el empalme circular no pasa por el lookahead del
    limitador de FFmpeg, que desplaza las muestras del borde y rompe el loop.
    """
    if not which("ffmpeg"):
        raise RuntimeError("ffmpeg no está instalado")
    dst_ogg.parent.mkdir(parents=True, exist_ok=True)
    gain_db = 0.0
    history: list[dict[str, Any]] = []
    norm_wav = WORK_DIR / f"norm_{dst_ogg.stem}.wav"
    for attempt in range(1, max_iters + 1):
        af: str
        if loop:
            data, _ = read_wav(src_wav)
            data = _soft_limit(data * (10.0 ** (gain_db / 20.0)))
            write_wav(norm_wav, data, SR)
            af = "anull"
            input_path = norm_wav
        else:
            filters = []
            if abs(gain_db) > 1e-3:
                filters.append(f"volume={gain_db:.4f}dB")
            # level=false evita que FFmpeg re-normalice automáticamente y
            # destruya el ajuste en LUFS.
            filters.append("alimiter=limit=0.891:level=false:attack=5:release=50")
            af = ",".join(filters)
            input_path = src_wav
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-af",
            af,
            "-ar",
            str(SR),
            "-ac",
            str(CHANNELS),
            "-c:a",
            "libvorbis",
            "-q:a",
            "6",
            str(dst_ogg),
        ]
        run_cmd(cmd, logger)
        measured = ffmpeg_measure_lufs(dst_ogg)
        lufs = measured["lufs"]
        history.append(
            {
                "attempt": attempt,
                "gain_db": round(gain_db, 4),
                "loop": loop,
                **measured,
            }
        )
        if not math.isfinite(lufs):
            # Si no se puede medir, al menos verificamos que hay señal.
            data, _ = read_wav(src_wav)
            if rms_db(data) < -60:
                break
            break
        delta = target_lufs - lufs
        if abs(delta) <= tolerance:
            return {"ok": True, "lufs": lufs, "gain_db": gain_db, "attempts": attempt, "history": history}
        gain_db += delta
    measured = ffmpeg_measure_lufs(dst_ogg)
    return {
        "ok": math.isfinite(measured["lufs"]) and abs(measured["lufs"] - target_lufs) <= 0.5,
        "lufs": measured["lufs"],
        "gain_db": gain_db,
        "attempts": len(history),
        "history": history,
    }


# ---------------------------------------------------------------------------
# Sprites: carga de referencias, cuantización, contorno y composición
# ---------------------------------------------------------------------------

SIDE_MARGIN = 1  # píxeles libres para que el contorno no toque los bordes
TOP_MARGIN = 2  # 1 px de contorno + 1 px de aire superior
BOTTOM_MARGIN = 1  # el contorno ocupa la última fila: baseline = height - 1


def _palette_image() -> Any:
    global PALETTE_IMAGE
    if PALETTE_IMAGE is None:
        from PIL import Image

        img = Image.new("P", (1, 1))
        pal: list[int] = []
        for rgb in PALETTE_RGB:
            pal.extend(rgb)
        pal.extend([0] * (768 - len(pal)))
        img.putpalette(pal)
        PALETTE_IMAGE = img
    return PALETTE_IMAGE


def _binarize_alpha(img: Any) -> Any:
    from PIL import Image

    rgba = img.convert("RGBA")
    arr = np.array(rgba)
    arr[..., 3] = np.where(arr[..., 3] >= 128, 255, 0).astype("uint8")
    arr[arr[..., 3] == 0] = 0
    return Image.fromarray(arr, "RGBA")


def load_reference_frames(spec: SpriteSpec, logger: logging.Logger) -> list[Any]:
    from PIL import Image

    frames = []
    prefix = ROOT / spec.ref_prefix
    for i in range(1, spec.ref_count + 1):
        path = Path(f"{prefix}_{i}.png")
        if not path.exists():
            logger.warning("Falta la referencia %s", safe_rel(path))
            return []
        img = Image.open(path).convert("RGBA")
        frames.append(_binarize_alpha(img))
    if len(frames) != spec.frames:
        logger.warning(
            "La referencia %s tiene %d cuadros; se esperaban %d",
            spec.ref_prefix,
            len(frames),
            spec.frames,
        )
        return []
    return frames


def remove_background(img: Any, tolerance: float = 48.0) -> Any:
    """Quita un fondo uniforme conectado al borde, preservando interiores."""
    rgba = _binarize_alpha(img)
    arr = np.array(rgba)
    alpha = arr[..., 3]
    if float(np.mean(alpha < 128)) > 0.02:
        return rgba
    h, w = alpha.shape
    border = np.zeros((h, w), dtype=bool)
    border[0, :] = True
    border[-1, :] = True
    border[:, 0] = True
    border[:, -1] = True
    rgb = arr[..., :3].astype("float64")
    border_rgb = rgb[border]
    if len(border_rgb) == 0:
        return rgba
    median = np.median(border_rgb, axis=0)
    # Si el borde no es razonablemente uniforme, no arriesgamos un keying agresivo.
    spread = float(np.mean(np.std(border_rgb, axis=0)))
    if spread > 38.0:
        return rgba
    dist = np.sqrt(np.sum((rgb - median) ** 2, axis=2))
    bg_like = dist <= tolerance
    seed = border & bg_like
    if not np.any(seed):
        return rgba
    try:
        from scipy.ndimage import binary_propagation

        connected = binary_propagation(seed, mask=bg_like)
    except Exception:
        # Flood fill BFS de respaldo.
        from collections import deque

        connected = np.zeros_like(seed)
        q: deque[tuple[int, int]] = deque()
        for y, x in zip(*np.where(seed)):
            connected[y, x] = True
            q.append((int(y), int(x)))
        while q:
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and bg_like[ny, nx] and not connected[ny, nx]:
                    connected[ny, nx] = True
                    q.append((ny, nx))
    if int(np.sum(connected)) >= int(h * w * 0.98):
        return rgba
    arr[connected] = 0
    out = _binarize_alpha(__import__("PIL.Image", fromlist=["Image"]).fromarray(arr, "RGBA"))
    if float(np.mean(np.array(out)[..., 3] == 255)) < 0.005:
        return rgba
    return out


def quantize_rgba(img: Any) -> Any:
    from PIL import Image

    rgba = _binarize_alpha(img)
    arr = np.array(rgba)
    alpha = arr[..., 3]
    rgb = arr[..., :3].astype("int32")
    palette = np.asarray(PALETTE_RGB, dtype="int32")
    # Distancia euclídea directa contra los 8 colores.  No usamos
    # Image.quantize(palette=...) porque en Pillow los píxeles negros
    # interpolados pueden terminar como (0,0,0), fuera de la paleta.
    dist = ((rgb[:, :, None, :] - palette[None, None, :, :]) ** 2).sum(axis=-1)
    idx = dist.argmin(axis=-1)
    out = palette[idx].astype("uint8")
    out[alpha == 0] = (0, 0, 0)
    alpha2 = np.where(alpha >= 128, 255, 0).astype("uint8")
    return Image.fromarray(np.dstack([out, alpha2]), "RGBA")


def add_outline(img: Any) -> Any:
    from PIL import Image

    rgba = _binarize_alpha(img)
    arr = np.array(rgba)
    alpha = arr[..., 3] > 127
    h, w = alpha.shape
    dil = np.zeros((h, w), dtype=bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            shifted = np.zeros((h, w), dtype=bool)
            ys = slice(max(0, dy), h + min(0, dy))
            xs = slice(max(0, dx), w + min(0, dx))
            ys2 = slice(max(0, -dy), h + min(0, -dy))
            xs2 = slice(max(0, -dx), w + min(0, -dx))
            shifted[ys, xs] = alpha[ys2, xs2]
            dil |= shifted
    outline = dil & ~alpha
    arr[outline] = (*OUTLINE_RGB, 255)
    arr[~alpha & ~outline] = (0, 0, 0, 0)
    return Image.fromarray(arr, "RGBA")


def _resize_rgba(img: Any, size: tuple[int, int], resample: Any = None) -> Any:
    from PIL import Image

    if resample is None:
        resample = Image.LANCZOS
    out = img.convert("RGBA").resize(size, resample)
    return _binarize_alpha(out)


def process_strip(frames: list[Any], spec: SpriteSpec) -> tuple[Any, dict[str, Any]]:
    """Escala de forma compartida, cuantiza, contornea y compone la tira."""
    from PIL import Image

    if not frames:
        raise RuntimeError(f"{spec.id}: no hay cuadros para procesar")
    if len(frames) != spec.frames:
        raise RuntimeError(f"{spec.id}: {len(frames)} cuadros, se esperaban {spec.frames}")
    frames = [_binarize_alpha(f) for f in frames]
    w, h = spec.width, spec.height
    # Canvas común de entrada: conserva cada cuadro y lo centra si llegó con
    # otro tamaño; nunca descarta el contenido original.
    cw = max(f.width for f in frames)
    ch = max(f.height for f in frames)
    normalized = []
    for f in frames:
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        canvas.alpha_composite(f, ((cw - f.width) // 2, (ch - f.height) // 2))
        normalized.append(_binarize_alpha(canvas))
    frames = normalized

    boxes = [f.getchannel("A").getbbox() for f in frames]
    boxes_valid = [b for b in boxes if b is not None]
    if not boxes_valid:
        raise RuntimeError(f"{spec.id}: todos los cuadros están vacíos")
    ux0 = min(b[0] for b in boxes_valid)
    uy0 = min(b[1] for b in boxes_valid)
    ux1 = max(b[2] for b in boxes_valid)
    uy1 = max(b[3] for b in boxes_valid)
    uw, uh = max(1, ux1 - ux0), max(1, uy1 - uy0)
    avail_w = max(1, w - 2 * SIDE_MARGIN)
    avail_h = max(1, h - TOP_MARGIN - BOTTOM_MARGIN)
    scale = min(avail_w / float(uw), avail_h / float(uh), 1.0)
    sw, sh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))
    resample = Image.LANCZOS if scale < 0.999 else Image.NEAREST
    scaled = [_resize_rgba(f, (sw, sh), resample) for f in frames]
    sboxes = [f.getchannel("A").getbbox() for f in scaled]
    sboxes_valid = [b for b in sboxes if b is not None]
    if not sboxes_valid:
        raise RuntimeError(f"{spec.id}: los cuadros quedaron vacíos tras escalar")
    sux0 = min(b[0] for b in sboxes_valid)
    suy0 = min(b[1] for b in sboxes_valid)
    sux1 = max(b[2] for b in sboxes_valid)
    suy1 = max(b[3] for b in sboxes_valid)
    suw, suh = max(1, sux1 - sux0), max(1, suy1 - suy0)
    off_x = (w - suw) // 2 - sux0
    off_y = h - BOTTOM_MARGIN - suh - suy0
    final_frames = []
    frame_meta = []
    for idx, frame in enumerate(scaled):
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.alpha_composite(frame, (off_x, off_y))
        canvas = add_outline(quantize_rgba(canvas))
        final_frames.append(canvas)
        bbox = canvas.getchannel("A").getbbox()
        frame_meta.append(
            {
                "frame": idx + 1,
                "bbox": list(bbox) if bbox else None,
                "bottom": (bbox[3] - 1) if bbox else None,
            }
        )
    strip = Image.new("RGBA", (w * spec.frames, h), (0, 0, 0, 0))
    for idx, frame in enumerate(final_frames):
        strip.alpha_composite(frame, (idx * w, 0))
    meta = {
        "frames": spec.frames,
        "frame_w": w,
        "frame_h": h,
        "generation_scale": spec.gen_scale,
        "input_canvas": [cw, ch],
        "scale": round(scale, 6),
        "union_bbox": [ux0, uy0, ux1, uy1],
        "baseline": h - 1,
        "frame_meta": frame_meta,
    }
    return strip, meta


def reference_sprite(spec: SpriteSpec, logger: logging.Logger) -> tuple[Any, dict[str, Any]]:
    frames = load_reference_frames(spec, logger)
    if not frames:
        raise RuntimeError(
            f"{spec.id}: no hay referencias completas en {spec.ref_prefix}_*.png "
            "y el backend ML no está disponible"
        )
    strip, meta = process_strip(frames, spec)
    meta["source"] = "reference-postprocess"
    return strip, meta


class SDSpritesBackend:
    """Stable Diffusion 1.5 + LoRA pixel art, img2img sobre las referencias."""

    def __init__(self, device: str, cache_dir: Path, logger: logging.Logger):
        self.device = device
        self.cache_dir = cache_dir
        self.logger = logger
        self.pipe: Any = None
        self.torch: Any = None
        self.strength = 0.55

    def load(self) -> None:
        import torch
        from diffusers import DPMSolverMultistepScheduler, StableDiffusionImg2ImgPipeline

        self.torch = torch
        os.environ.setdefault("HF_HOME", str(self.cache_dir))
        self.logger.info("Cargando Stable Diffusion 1.5 + LoRA pixel art en %s", self.device)
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            MODEL_IDS["sprites_base"],
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None,
            requires_safety_checker=False,
            cache_dir=str(self.cache_dir),
        )
        try:
            pipe.load_lora_weights(
                MODEL_IDS["sprites_lora"],
                weight_name=MODEL_IDS["sprites_lora_file"],
                adapter_name="pixelart",
                cache_dir=str(self.cache_dir),
            )
            pipe.set_adapters(["pixelart"], adapter_weights=[0.85])
            self.logger.info("LoRA pixel art cargada")
        except Exception as exc:
            self.logger.warning("No se pudo cargar la LoRA pixel art (%s); sigo con SD1.5 base", exc)
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe.to(self.device)
        try:
            pipe.set_progress_bar_config(disable=True)
            pipe.enable_vae_slicing()
            pipe.enable_attention_slicing()
        except Exception:
            pass
        self.pipe = pipe

    def _canvas(self, spec: SpriteSpec) -> tuple[int, int]:
        # Generamos a 512 (o 512x768 para personajes altos): el postproceso
        # reduce a 4x el tamaño final y luego al tamaño final exacto.
        if spec.height > spec.width:
            return 512, 768
        return 512, 512

    def _prompt(self, spec: SpriteSpec, frame_idx: int) -> str:
        base = STYLE_BLOCK.format(
            subject=spec.subject,
            frames=spec.frames,
            action=spec.action,
        )
        return f"{base} Full-body, centered."

    def generate_frame(
        self,
        spec: SpriteSpec,
        frame_idx: int,
        init_img: Any | None,
        seed: int,
    ) -> Any:
        from PIL import Image

        assert self.pipe is not None
        cw, ch = self._canvas(spec)
        if init_img is not None:
            init = Image.new("RGB", (cw, ch), (255, 255, 255))
            ref = init_img.convert("RGBA").resize((cw, ch), Image.NEAREST)
            init.paste(ref, (0, 0), ref)
            strength = self.strength
        else:
            init = Image.new("RGB", (cw, ch), (255, 255, 255))
            strength = 0.99
        gen = self.torch.Generator(device=self.device).manual_seed(seed)
        result = self.pipe(
            prompt=self._prompt(spec, frame_idx),
            negative_prompt=NEGATIVE_PROMPT,
            image=init,
            strength=strength,
            num_inference_steps=26,
            guidance_scale=7.0,
            generator=gen,
            width=cw,
            height=ch,
        )
        out = result.images[0].convert("RGBA")
        if init_img is not None:
            # La silueta de referencia manda: transparencia limpia y encuadre estable.
            alpha = init_img.convert("RGBA").resize((cw, ch), Image.NEAREST).getchannel("A")
            alpha = alpha.point(lambda a: 255 if a >= 128 else 0)
            out.putalpha(alpha)
        else:
            out = remove_background(out)
        return _binarize_alpha(out)

    def close(self) -> None:
        self.pipe = None
        try:
            import torch

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Validación de la entrega
# ---------------------------------------------------------------------------


def _wav_spec(path: Path) -> dict[str, Any]:
    with wave.open(str(path), "rb") as wf:
        return {
            "channels": wf.getnchannels(),
            "sample_width_bytes": wf.getsampwidth(),
            "sample_rate": wf.getframerate(),
            "frames": wf.getnframes(),
            "compression": wf.getcomptype(),
            "duration": wf.getnframes() / float(wf.getframerate()) if wf.getframerate() else 0.0,
        }


def validate_sfx_wav(path: Path, spec: SfxSpec) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    expected_frames = int(round(spec.duration * SR))
    info = _wav_spec(path)
    checks["exists"] = path.exists()
    checks["wave"] = info
    checks["channels_ok"] = info["channels"] == 2
    checks["sample_rate_ok"] = info["sample_rate"] == SR
    checks["bit_depth_ok"] = info["sample_width_bytes"] == 2
    checks["pcm_ok"] = info["compression"] == "NONE"
    checks["frames_ok"] = info["frames"] == expected_frames
    data, sr = read_wav(path)
    checks["shape"] = list(data.shape)
    checks["rms_db"] = round(rms_db(data), 2)
    checks["peak"] = round(float(np.max(np.abs(data))), 5) if data.size else 0.0
    checks["silence_ok"] = checks["rms_db"] > -60.0 and checks["peak"] > 0.001
    if spec.loop:
        seam = loop_seam_metrics(data)
        checks["loop_seam"] = {k: round(v, 6) for k, v in seam.items()}
        checks["loop_ok"] = seam["sample_jump"] <= 0.01 and seam["slope_error"] <= 0.08
    else:
        checks["loop_ok"] = True
    ok = all(
        checks[k]
        for k in (
            "exists",
            "channels_ok",
            "sample_rate_ok",
            "bit_depth_ok",
            "pcm_ok",
            "frames_ok",
            "silence_ok",
            "loop_ok",
        )
    )
    checks["ok"] = bool(ok)
    return checks


def _decode_ogg_to_wav(src: Path, dst: Path, logger: logging.Logger) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(src),
        "-ar",
        str(SR),
        "-ac",
        str(CHANNELS),
        "-c:a",
        "pcm_s16le",
        str(dst),
    ]
    run_cmd(cmd, logger)


def validate_ogg_asset(
    path: Path,
    expected_duration: float,
    loop: bool,
    logger: logging.Logger,
    check_lufs: bool = True,
) -> dict[str, Any]:
    checks: dict[str, Any] = {"exists": path.exists()}
    if not path.exists():
        checks["ok"] = False
        return checks
    probe = ffprobe_json(path, logger)
    streams = [s for s in probe.get("streams", []) if s.get("codec_type") == "audio"]
    stream = streams[0] if streams else {}
    fmt = probe.get("format", {})
    checks["codec"] = stream.get("codec_name")
    checks["sample_rate"] = stream.get("sample_rate")
    checks["channels"] = stream.get("channels")
    checks["duration_s"] = float(fmt.get("duration", 0.0) or 0.0)
    checks["codec_ok"] = stream.get("codec_name") == "vorbis"
    checks["sample_rate_ok"] = str(stream.get("sample_rate")) == str(SR)
    checks["channels_ok"] = int(stream.get("channels") or 0) == 2
    checks["duration_ok"] = abs(checks["duration_s"] - expected_duration) <= 0.02
    if check_lufs:
        loud = ffmpeg_measure_lufs(path)
        checks["lufs"] = round(loud["lufs"], 3) if math.isfinite(loud["lufs"]) else loud["lufs"]
        checks["true_peak_db"] = round(loud["true_peak_db"], 3) if math.isfinite(loud["true_peak_db"]) else loud["true_peak_db"]
        checks["lufs_ok"] = math.isfinite(loud["lufs"]) and abs(loud["lufs"] + 16.0) <= 0.5
    else:
        checks["lufs_ok"] = True
    if loop:
        decoded = WORK_DIR / f"validate_{path.stem}.wav"
        try:
            _decode_ogg_to_wav(path, decoded, logger)
            data, _ = read_wav(decoded)
            seam = loop_seam_metrics(data)
            checks["loop_seam"] = {k: round(v, 6) for k, v in seam.items()}
            checks["loop_ok"] = seam["sample_jump"] <= 0.01 and seam["slope_error"] <= 0.08
        except Exception as exc:
            checks["loop_error"] = str(exc)
            checks["loop_ok"] = False
        finally:
            try:
                decoded.unlink(missing_ok=True)
            except Exception:
                pass
    else:
        checks["loop_ok"] = True
    ok = all(
        checks[k]
        for k in ("exists", "codec_ok", "sample_rate_ok", "channels_ok", "duration_ok", "lufs_ok", "loop_ok")
    )
    checks["ok"] = bool(ok)
    return checks


def validate_sprite_png(path: Path, spec: SpriteSpec) -> dict[str, Any]:
    from PIL import Image

    checks: dict[str, Any] = {"exists": path.exists()}
    if not path.exists():
        checks["ok"] = False
        return checks
    img = Image.open(path)
    checks["mode"] = img.mode
    checks["size"] = list(img.size)
    checks["rgba_ok"] = img.mode == "RGBA"
    checks["size_ok"] = img.size == (spec.width * spec.frames, spec.height)
    rgba = img.convert("RGBA")
    arr = np.array(rgba)
    checks["palette"] = [f"#{r:02X}{g:02X}{b:02X}" for r, g, b in PALETTE_RGB]
    palette_set = set(PALETTE_RGB)
    all_ok = True
    frame_checks = []
    bottoms = []
    for idx in range(spec.frames):
        cell = arr[:, idx * spec.width : (idx + 1) * spec.width, :]
        alpha = cell[..., 3]
        opaque = alpha == 255
        transparent = alpha == 0
        semi = int(np.sum((alpha > 0) & (alpha < 255)))
        colors = {tuple(int(v) for v in c) for c in np.unique(cell[opaque][:, :3], axis=0)} if np.any(opaque) else set()
        # Frontera del silueto: todo píxel opaco con un vecino transparente/fuera.
        h, w = opaque.shape
        boundary = np.zeros_like(opaque)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                shifted = np.zeros_like(opaque)
                ys = slice(max(0, dy), h + min(0, dy))
                xs = slice(max(0, dx), w + min(0, dx))
                ys2 = slice(max(0, -dy), h + min(0, -dy))
                xs2 = slice(max(0, -dx), w + min(0, -dx))
                shifted[ys, xs] = opaque[ys2, xs2]
                boundary |= opaque & ~shifted
        boundary_colors = (
            {tuple(int(v) for v in c) for c in np.unique(cell[boundary][:, :3], axis=0)}
            if np.any(boundary)
            else set()
        )
        bbox = rgba.crop((idx * spec.width, 0, (idx + 1) * spec.width, spec.height)).getchannel("A").getbbox()
        bottom = (bbox[3] - 1) if bbox else None
        if bottom is not None:
            bottoms.append(bottom)
        outline_ok = bool(boundary_colors) and boundary_colors == {OUTLINE_RGB}
        palette_ok = colors.issubset(palette_set) and len(colors) <= 8
        frame_ok = (
            semi == 0
            and bool(colors)
            and palette_ok
            and outline_ok
            and bool(np.any(transparent))
        )
        all_ok = all_ok and frame_ok
        frame_checks.append(
            {
                "frame": idx + 1,
                "colors": len(colors),
                "semi_alpha_px": semi,
                "transparent_px": int(np.sum(transparent)),
                "outline_boundary_ok": outline_ok,
                "palette_ok": palette_ok,
                "bbox": list(bbox) if bbox else None,
                "bottom": bottom,
                "ok": frame_ok,
            }
        )
    baseline_ok = bool(bottoms) and max(bottoms) == spec.height - 1
    # Centro horizontal del conjunto de cuadros.
    union_bbox = rgba.getchannel("A").getbbox()
    center_ok = True
    if union_bbox:
        center = (union_bbox[0] + union_bbox[2]) / 2.0
        center_ok = abs(center - (spec.width * spec.frames) / 2.0) <= max(
            2.0, spec.width * 0.1
        )
    checks["frames"] = frame_checks
    checks["baseline"] = spec.height - 1
    checks["bottoms"] = bottoms
    checks["baseline_ok"] = bool(baseline_ok)
    checks["center_ok"] = bool(center_ok)
    checks["ok"] = bool(checks["rgba_ok"] and checks["size_ok"] and all_ok and baseline_ok and center_ok)
    return checks


# ---------------------------------------------------------------------------
# Generación y metadatos
# ---------------------------------------------------------------------------


def _previous_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {}
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _previous_asset_meta() -> dict[str, dict[str, Any]]:
    prev = _previous_manifest()
    out: dict[str, dict[str, Any]] = {}
    for entry in prev.get("assets", []):
        if isinstance(entry, dict) and entry.get("file"):
            out[str(entry["file"])] = entry
    return out


def _sfx_seed(spec: SfxSpec) -> int:
    return 0x5F000 + sum(ord(c) for c in spec.id)


def _music_seed(spec: MusicSpec) -> int:
    return spec.seed


def _sprite_seed(spec: SpriteSpec) -> int:
    return 0x5A000 + sum(ord(c) for c in spec.id)


def _write_extra_ogg(spec: SfxSpec, wav_path: Path, logger: logging.Logger) -> dict[str, Any]:
    results = {}
    for rel, fmt in spec.extra_files:
        if fmt != "ogg":
            continue
        dst = DELIVERY / rel
        res = normalize_ogg_to_lufs(wav_path, dst, logger, target_lufs=-16.0, loop=spec.loop)
        results[rel] = res
        if not res.get("ok"):
            logger.error("Loudness fuera de tolerancia para %s: %s LUFS", rel, res.get("lufs"))
    return results


def generate_sfx(
    specs: Sequence[SfxSpec],
    backend: str,
    force: bool,
    logger: logging.Logger,
    model_cache: Path,
    device: str,
    seed_offset: int = 0,
) -> dict[str, dict[str, Any]]:
    meta: dict[str, dict[str, Any]] = {}
    prev = _previous_asset_meta()
    gen: AudioGenBackend | None = None
    if backend in ("auto", "ml") and specs:
        try:
            gen = AudioGenBackend(_torch_device(device), model_cache, logger)
            gen.load()
        except Exception as exc:
            if backend == "ml":
                raise
            logger.warning("AudioGen no disponible (%s). SFX por DSP determinista.", exc)
            gen = None
    try:
        for spec in specs:
            out = DELIVERY / spec.file
            extras = [DELIVERY / rel for rel, _ in spec.extra_files]
            if out.exists() and all(p.exists() for p in extras) and not force:
                logger.info("SFX %-18s ya existe, se conserva", spec.id)
                meta[spec.id] = prev.get(spec.file, {"backend": "existing"})
                continue
            backend_used = "procedural-dsp"
            model_used = None
            note = ""
            stereo = None
            if gen is not None:
                try:
                    gen_dur = 20.0 if spec.loop else max(2.0, min(10.0, spec.duration * 3.2))
                    t0 = time.time()
                    arr, sr_in = gen.generate(spec.prompt, gen_dur, _sfx_seed(spec) + seed_offset)
                    stereo = postprocess_ml_sfx(spec, arr, sr_in, _sfx_seed(spec) + seed_offset)
                    backend_used = "audiogen-medium"
                    model_used = MODEL_IDS["sfx"]
                    logger.info("SFX %-18s AudioGen %.1fs -> %.3fs", spec.id, time.time() - t0, spec.duration)
                except Exception as exc:
                    if backend == "ml":
                        raise
                    note = f"AudioGen falló: {type(exc).__name__}: {exc}"
                    logger.warning("SFX %-18s: %s; fallback DSP", spec.id, note)
                    stereo = None
            if stereo is None:
                stereo = synth_sfx_procedural(spec)
                if spec.loop:
                    logger.info("SFX %-18s dron procedural (loop exacto)", spec.id)
            write_wav(out, stereo, SR)
            extra_res = _write_extra_ogg(spec, out, logger)
            meta[spec.id] = {
                "backend": backend_used,
                "model": model_used,
                "seed": _sfx_seed(spec) + seed_offset,
                "note": note,
                "extra": extra_res,
            }
    finally:
        if gen is not None:
            gen.close()
    return meta


def generate_music(
    specs: Sequence[MusicSpec],
    backend: str,
    force: bool,
    logger: logging.Logger,
    model_cache: Path,
    device: str,
    seed_offset: int = 0,
) -> dict[str, dict[str, Any]]:
    meta: dict[str, dict[str, Any]] = {}
    prev = _previous_asset_meta()
    gen: MusicGenBackend | None = None
    if backend in ("auto", "ml") and specs:
        try:
            gen = MusicGenBackend(_torch_device(device), model_cache, logger)
            gen.load()
        except Exception as exc:
            if backend == "ml":
                raise
            logger.warning("MusicGen no disponible (%s). Música por compositor determinista.", exc)
            gen = None
    try:
        for spec in specs:
            out = DELIVERY / spec.file
            if out.exists() and not force:
                logger.info("Música %-18s ya existe, se conserva", spec.id)
                meta[spec.id] = prev.get(spec.file, {"backend": "existing"})
                continue
            backend_used = "procedural-composer"
            model_used = None
            note = ""
            stereo = None
            if gen is not None:
                try:
                    gen_dur = 10.0 if not spec.loop else 30.0
                    t0 = time.time()
                    arr, sr_in = gen.generate(spec.prompt, gen_dur, _music_seed(spec) + seed_offset)
                    stereo = postprocess_ml_music(spec, arr, sr_in, _music_seed(spec) + seed_offset)
                    backend_used = "musicgen-medium"
                    model_used = MODEL_IDS["musica"]
                    logger.info("Música %-18s MusicGen %.1fs -> %.1fs", spec.id, time.time() - t0, spec.duration)
                except Exception as exc:
                    if backend == "ml":
                        raise
                    note = f"MusicGen falló: {type(exc).__name__}: {exc}"
                    logger.warning("Música %-18s: %s; fallback compositor", spec.id, note)
                    stereo = None
            if stereo is None:
                stereo = synth_music_procedural(spec)
                logger.info("Música %-18s compositor determinista", spec.id)
            src = WORK_DIR / f"{spec.id}.wav"
            write_wav(src, stereo, SR)
            loud = normalize_ogg_to_lufs(src, out, logger, target_lufs=-16.0, loop=spec.loop)
            if not loud.get("ok"):
                logger.error("Música %-18s loudness no conforme: %s LUFS", spec.id, loud.get("lufs"))
            meta[spec.id] = {
                "backend": backend_used,
                "model": model_used,
                "seed": _music_seed(spec) + seed_offset,
                "note": note,
                "loudness": loud,
                "source_wav": safe_rel(src),
            }
    finally:
        if gen is not None:
            gen.close()
    return meta


def generate_sprites(
    specs: Sequence[SpriteSpec],
    backend: str,
    force: bool,
    logger: logging.Logger,
    model_cache: Path,
    device: str,
    seed_offset: int = 0,
) -> dict[str, dict[str, Any]]:
    meta: dict[str, dict[str, Any]] = {}
    prev = _previous_asset_meta()
    sd: SDSpritesBackend | None = None
    if backend in ("auto", "ml") and specs:
        try:
            sd = SDSpritesBackend(_torch_device(device), model_cache, logger)
            sd.load()
        except Exception as exc:
            if backend == "ml":
                raise
            logger.warning("Stable Diffusion no disponible (%s). Sprites por postproceso de referencias.", exc)
            sd = None
    try:
        for spec in specs:
            out = DELIVERY / spec.file
            if out.exists() and not force:
                logger.info("Sprite %-24s ya existe, se conserva", spec.id)
                meta[spec.id] = prev.get(spec.file, {"backend": "existing"})
                continue
            refs = load_reference_frames(spec, logger)
            frames = []
            backend_used = "reference-postprocess"
            model_used = None
            note = ""
            if sd is not None:
                try:
                    t0 = time.time()
                    for idx in range(spec.frames):
                        init = refs[idx] if len(refs) == spec.frames else None
                        frame = sd.generate_frame(spec, idx, init, _sprite_seed(spec) + seed_offset + idx)
                        frames.append(frame)
                    backend_used = "sd15-pixelart-lora"
                    model_used = f"{MODEL_IDS['sprites_base']} + {MODEL_IDS['sprites_lora']}"
                    logger.info("Sprite %-24s SD+LoRA %.1fs", spec.id, time.time() - t0)
                except Exception as exc:
                    if backend == "ml":
                        raise
                    note = f"SD falló: {type(exc).__name__}: {exc}"
                    logger.warning("Sprite %-24s: %s; fallback referencias", spec.id, note)
                    frames = []
            if not frames:
                if not refs:
                    raise RuntimeError(f"{spec.id}: sin frames ML ni referencias completas")
                frames = refs
            strip, pmeta = process_strip(frames, spec)
            strip.save(out, "PNG", optimize=True)
            meta[spec.id] = {
                "backend": backend_used,
                "model": model_used,
                "seed": _sprite_seed(spec) + seed_offset,
                "note": note,
                **pmeta,
            }
    finally:
        if sd is not None:
            sd.close()
    return meta


def write_sprites_index(logger: logging.Logger) -> None:
    entries: dict[str, Any] = {}
    for spec in SPRITE_SPECS:
        path = DELIVERY / spec.file
        if not path.exists():
            continue
        entries[spec.id] = {
            "file": spec.file,
            "frames": spec.frames,
            "frame_w": spec.width,
            "frame_h": spec.height,
            "sheet_w": spec.width * spec.frames,
            "sheet_h": spec.height,
            "baseline": spec.height - 1,
            "rects": [
                {"i": i + 1, "x": i * spec.width, "y": 0, "w": spec.width, "h": spec.height}
                for i in range(spec.frames)
            ],
        }
    index_path = SPRITE_DIR / "sprites_manifest.json"
    index_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info("Índice de sprites: %s", safe_rel(index_path))


# ---------------------------------------------------------------------------
# Manifiesto de entrega y verificación final
# ---------------------------------------------------------------------------


def validate_delivery(
    logger: logging.Logger,
    only: set[str] | None = None,
    generation_meta: dict[str, dict[str, Any]] | None = None,
    write: bool = True,
) -> tuple[bool, dict[str, Any]]:
    ensure_dirs()
    previous = _previous_asset_meta()
    generation_meta = generation_meta or {}
    assets: list[dict[str, Any]] = []

    def _merge_meta(spec: Any) -> dict[str, Any]:
        meta = generation_meta.get(spec.id) or previous.get(spec.file) or {"backend": "unknown"}
        out = dict(meta)
        source = out.get("source_wav")
        if source and not (ROOT / source).exists():
            out.pop("source_wav", None)
        return out

    def _selected(asset_id: str) -> bool:
        return only is None or asset_id in only or ("sfx" in only and asset_id in SFX_BY_ID) or (
            "musica" in only and asset_id in MUSIC_BY_ID
        ) or ("sprites" in only and asset_id in SPRITE_BY_ID)

    for spec in SFX_SPECS:
        if not _selected(spec.id):
            continue
        path = DELIVERY / spec.file
        checks = validate_sfx_wav(path, spec) if path.exists() else {"exists": False, "ok": False}
        entry = {
            "id": spec.id,
            "category": "sfx",
            "file": spec.file,
            "spec": {
                "duration_s": spec.duration,
                "channels": 2,
                "sample_rate": SR,
                "bit_depth": 16,
                "loop": spec.loop,
                "prompt": spec.prompt,
            },
            "sha256": sha256_file(path) if path.exists() else None,
            "size_bytes": path.stat().st_size if path.exists() else None,
            "checks": checks,
            "ok": bool(checks.get("ok")),
            **_merge_meta(spec),
        }
        assets.append(entry)
        for rel, fmt in spec.extra_files:
            if fmt != "ogg":
                continue
            extra_path = DELIVERY / rel
            echecks = (
                validate_ogg_asset(extra_path, spec.duration, spec.loop, logger)
                if extra_path.exists()
                else {"exists": False, "ok": False}
            )
            assets.append(
                {
                    "id": spec.id + "_ogg",
                    "category": "sfx",
                    "file": rel,
                    "spec": {
                        "duration_s": spec.duration,
                        "codec": "vorbis",
                        "channels": 2,
                        "sample_rate": SR,
                        "lufs": -16.0,
                        "loop": spec.loop,
                        "prompt": spec.prompt,
                    },
                    "sha256": sha256_file(extra_path) if extra_path.exists() else None,
                    "size_bytes": extra_path.stat().st_size if extra_path.exists() else None,
                    "checks": echecks,
                    "ok": bool(echecks.get("ok")),
                    "backend": "procedural-dsp" if not path.exists() else "shared-wav",
                }
            )

    for spec in MUSIC_SPECS:
        if not _selected(spec.id):
            continue
        path = DELIVERY / spec.file
        checks = (
            validate_ogg_asset(path, spec.duration, spec.loop, logger)
            if path.exists()
            else {"exists": False, "ok": False}
        )
        entry = {
            "id": spec.id,
            "category": "musica",
            "file": spec.file,
            "spec": {
                "duration_s": spec.duration,
                "codec": "vorbis",
                "channels": 2,
                "sample_rate": SR,
                "lufs": -16.0,
                "loop": spec.loop,
                "bpm": spec.bpm,
                "prompt": spec.prompt,
            },
            "sha256": sha256_file(path) if path.exists() else None,
            "size_bytes": path.stat().st_size if path.exists() else None,
            "checks": checks,
            "ok": bool(checks.get("ok")),
            **_merge_meta(spec),
        }
        assets.append(entry)

    for spec in SPRITE_SPECS:
        if not _selected(spec.id):
            continue
        path = DELIVERY / spec.file
        checks = validate_sprite_png(path, spec) if path.exists() else {"exists": False, "ok": False}
        entry = {
            "id": spec.id,
            "category": "sprites",
            "file": spec.file,
            "spec": {
                "frames": spec.frames,
                "frame_w": spec.width,
                "frame_h": spec.height,
                "sheet_w": spec.width * spec.frames,
                "sheet_h": spec.height,
                "palette": list(PALETTE_HEX),
                "outline": PALETTE_HEX[0],
                "transparent_background": True,
                "baseline": spec.height - 1,
                "prompt_subject": spec.subject,
                "prompt_action": spec.action,
            },
            "sha256": sha256_file(path) if path.exists() else None,
            "size_bytes": path.stat().st_size if path.exists() else None,
            "checks": checks,
            "ok": bool(checks.get("ok")),
            **_merge_meta(spec),
        }
        assets.append(entry)

    passed = sum(1 for a in assets if a.get("ok"))
    failed = [a for a in assets if not a.get("ok")]
    summary = {
        "assets_total": len(assets),
        "assets_ok": passed,
        "assets_failed": len(failed),
        "sfx": sum(1 for a in assets if a["category"] == "sfx"),
        "musica": sum(1 for a in assets if a["category"] == "musica"),
        "sprites": sum(1 for a in assets if a["category"] == "sprites"),
        "failed_ids": [a["id"] for a in failed],
        "all_ok": len(failed) == 0 and len(assets) > 0,
    }
    manifest = {
        "proyecto": "IN CRYPTA",
        "pipeline": "pipeline_in_crypta.py",
        "pipeline_version": "1.0.0",
        "generated_at": utc_now(),
        "root": str(ROOT),
        "delivery": safe_rel(DELIVERY),
        "palette": list(PALETTE_HEX),
        "formats": {
            "sfx": "WAV PCM 16-bit, 44100 Hz, 2 canales",
            "musica": "OGG Vorbis 44100 Hz, 2 canales, -16 LUFS integrados",
            "sprites": "PNG RGBA, tiras horizontales, cuadros finales exactos",
        },
        "models": MODEL_IDS,
        "licenses": LICENSES,
        "summary": summary,
        "assets": assets,
    }
    if write:
        MANIFEST_PATH.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        logger.info("Manifiesto escrito: %s", safe_rel(MANIFEST_PATH))
    return summary["all_ok"], manifest


def print_validation_summary(manifest: dict[str, Any]) -> None:
    summary = manifest.get("summary", {})
    print()
    print("=" * 78)
    print("ENTREGA IN CRYPTA — RESUMEN DE VALIDACIÓN")
    print("=" * 78)
    print(
        f"Assets: {summary.get('assets_ok', 0)}/{summary.get('assets_total', 0)} OK | "
        f"SFX: {summary.get('sfx', 0)} | Música: {summary.get('musica', 0)} | "
        f"Sprites: {summary.get('sprites', 0)}"
    )
    for asset in manifest.get("assets", []):
        mark = "OK  " if asset.get("ok") else "FAIL"
        checks = asset.get("checks", {})
        extra = ""
        if asset["category"] == "sfx":
            if "duration_s" in checks:
                extra = f"{checks.get('duration_s', '?')}s {checks.get('lufs', '?')} LUFS"
            else:
                extra = f"{checks.get('wave', {}).get('duration', '?')}s"
        elif asset["category"] == "musica":
            extra = f"{checks.get('duration_s', '?')}s {checks.get('lufs', '?')} LUFS"
        elif asset["category"] == "sprites":
            extra = f"{checks.get('size', '?')}"
        print(f"  [{mark}] {asset['id']:<28} {asset['file']:<42} {extra}")
    failed = summary.get("failed_ids", [])
    if failed:
        print(f"\nFallaron: {', '.join(failed)}")
    print("=" * 78)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _candidate_python() -> str | None:
    candidates = [
        ROOT / ".venv_assets" / "bin" / "python",
        Path("/media/backup/incrypta_assets/venv/bin/python"),
    ]
    current = Path(sys.executable).resolve()
    for candidate in candidates:
        try:
            if candidate.exists() and candidate.resolve() != current:
                return str(candidate)
        except OSError:
            continue
    return None


def _maybe_reexec() -> None:
    """Si existe el venv de assets, re-ejecuta con él para tener torch/Pillow."""
    if os.environ.get("INCRYPTA_PIPELINE_REEXEC") == "1":
        return
    candidate = _candidate_python()
    if not candidate:
        return
    os.environ["INCRYPTA_PIPELINE_REEXEC"] = "1"
    os.execv(candidate, [candidate, str(Path(__file__).resolve()), *sys.argv[1:]])


def parse_only(value: str | None) -> set[str] | None:
    if not value:
        return None
    out: set[str] = set()
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if token in ("sfx", "musica", "sprites", "all"):
            if token == "sfx":
                out.update(SFX_BY_ID)
            elif token == "musica":
                out.update(MUSIC_BY_ID)
            elif token == "sprites":
                out.update(SPRITE_BY_ID)
            else:
                out.update(ALL_BY_ID)
            continue
        if token not in ALL_BY_ID:
            raise SystemExit(f"ID desconocido: {token!r}. Usá --list.")
        out.add(token)
    return out or None


def cmd_list() -> int:
    print(f"{'ID':<30} {'CAT':<8} {'ARCHIVO':<44} ESPECIFICACIÓN")
    print("-" * 110)
    for spec in SFX_SPECS:
        print(f"{spec.id:<30} {'sfx':<8} {spec.file:<44} {spec.duration:.2f}s {'loop' if spec.loop else ''}")
        for rel, fmt in spec.extra_files:
            print(f"{spec.id + '_' + fmt:<30} {'sfx':<8} {rel:<44} {spec.duration:.2f}s loop")
    for spec in MUSIC_SPECS:
        print(
            f"{spec.id:<30} {'musica':<8} {spec.file:<44} {spec.duration:.0f}s "
            f"{spec.bpm} BPM {'loop' if spec.loop else 'stinger'}"
        )
    for spec in SPRITE_SPECS:
        print(
            f"{spec.id:<30} {'sprites':<8} {spec.file:<44} {spec.frames} x "
            f"{spec.width}x{spec.height}"
        )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genera y valida los assets de IN CRYPTA.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--list", action="store_true", help="Lista los assets y sus especificaciones")
    parser.add_argument("--validate", action="store_true", help="Valida la entrega existente y escribe el manifiesto")
    parser.add_argument("--check-deps", action="store_true", help="Comprueba dependencias")
    parser.add_argument("--require-ml", action="store_true", help="Con --check-deps, exige torch/audiocraft/diffusers")
    parser.add_argument(
        "--backend",
        choices=("auto", "ml", "procedural"),
        default="auto",
        help="auto intenta modelos y cae a determinista; ml exige modelos; procedural no usa GPU",
    )
    parser.add_argument("--skip-ml", action="store_true", help="Atajo de --backend procedural")
    parser.add_argument("--only", default=None, help="IDs separados por coma o categorías: sfx,musica,sprites")
    parser.add_argument("--force", action="store_true", help="Regenera aunque el archivo exista")
    parser.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    parser.add_argument(
        "--model-cache",
        default=os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface")),
        help="Directorio de caché de modelos",
    )
    parser.add_argument("--offline", action="store_true", help="No descargar modelos; usar sólo caché")
    parser.add_argument("--seed", type=int, default=0, help="Offset de semilla")
    parser.add_argument("--keep-work", action="store_true", help="Conserva WAVs temporales en .work")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--version", action="version", version="pipeline_in_crypta 1.0.0")
    args = parser.parse_args(argv)

    _maybe_reexec()
    ensure_dirs()
    logger = setup_logging(args.verbose)
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["AUDIOCRAFT_CACHE_DIR"] = str(Path(args.model_cache) / "audiocraft")
    else:
        os.environ.setdefault("HF_HOME", str(Path(args.model_cache)))
        os.environ.setdefault("AUDIOCRAFT_CACHE_DIR", str(Path(args.model_cache) / "audiocraft"))

    if args.list:
        return cmd_list()

    if args.check_deps:
        ok, report = check_dependencies(require_ml=args.require_ml)
        print(f"{'MÓDULO':<16} {'ESTADO':<8} VERSIÓN")
        print("-" * 60)
        for item in report:
            print(f"{item['module']:<16} {'OK' if item['ok'] else 'FALTA':<8} {item.get('version', item.get('error', ''))}")
        print("-" * 60)
        print("dependencias:", "OK" if ok else "INCOMPLETAS")
        return 0 if ok else 2

    backend = "procedural" if args.skip_ml else args.backend
    only = parse_only(args.only)

    if args.validate:
        ok, manifest = validate_delivery(logger, only=only)
        print_validation_summary(manifest)
        return 0 if ok else 1

    targets = only or set(ALL_BY_ID)
    sfx_specs = [s for s in SFX_SPECS if s.id in targets]
    music_specs = [s for s in MUSIC_SPECS if s.id in targets]
    sprite_specs = [s for s in SPRITE_SPECS if s.id in targets]
    model_cache = Path(args.model_cache).expanduser().resolve()
    model_cache.mkdir(parents=True, exist_ok=True)

    generation_meta: dict[str, dict[str, Any]] = {}
    started = time.time()
    logger.info(
        "Backend=%s, device=%s, targets=%d (%d SFX, %d música, %d sprites)",
        backend,
        args.device,
        len(targets),
        len(sfx_specs),
        len(music_specs),
        len(sprite_specs),
    )
    try:
        if sfx_specs:
            generation_meta.update(
                generate_sfx(sfx_specs, backend, args.force, logger, model_cache, args.device, args.seed)
            )
        if music_specs:
            generation_meta.update(
                generate_music(music_specs, backend, args.force, logger, model_cache, args.device, args.seed)
            )
        if sprite_specs:
            generation_meta.update(
                generate_sprites(sprite_specs, backend, args.force, logger, model_cache, args.device, args.seed)
            )
        write_sprites_index(logger)
    except Exception as exc:
        logger.error("Generación interrumpida: %s", exc, exc_info=args.verbose)
        # Aun así validamos lo que exista para dejar un manifiesto útil.
        ok, manifest = validate_delivery(logger, only=only, generation_meta=generation_meta)
        print_validation_summary(manifest)
        return 1

    ok, manifest = validate_delivery(logger, only=only, generation_meta=generation_meta)
    print_validation_summary(manifest)
    elapsed = time.time() - started
    logger.info("Generación terminada en %.1fs", elapsed)
    logger.info("%s", "ENTREGA OK" if ok else "ENTREGA CON FALLAS")
    if not args.keep_work:
        try:
            shutil.rmtree(WORK_DIR, ignore_errors=True)
        except Exception:
            pass
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())


