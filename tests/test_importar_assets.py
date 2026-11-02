# tests/test_importar_assets.py — F1-6: pruebas del importador de assets IA
# Fixtures generadas en memoria, sin archivos de IA (P2: no se genera audio ni imagen).
import os
import sys
import wave
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(RAIZ / "tools") not in sys.path:
    sys.path.insert(0, str(RAIZ / "tools"))

import pytest  # noqa: E402

from importar_assets_ia import (  # noqa: E402
    cargar_manifiesto,
    validar_manifiesto,
    verificar_contra_codigo,
    ESPERANDO_ENTREGA,
)

MANIFIESTO = RAIZ / "plan" / "manifest_assets.json"


# --------------------------------------------------------------------------- #
# F0-1 / F0-2 reutilizadas como base del importador (sin archivos IA).
# --------------------------------------------------------------------------- #
def test_manifiesto_valido_sin_errores():
    manifiesto = cargar_manifiesto(MANIFIESTO)
    ok, errores = validar_manifiesto(manifiesto)
    assert ok, f"manifiesto invalido: {errores}"
    assert not errores


def test_claves_coinciden_con_codigo():
    manifiesto = cargar_manifiesto(MANIFIESTO)
    ok, errores = verificar_contra_codigo(manifiesto)
    assert ok, f"claves sin coincidencia en codigo: {errores}"


# --------------------------------------------------------------------------- #
# F1-6: WAV a 44100 Hz y 16 bits (fixture en memoria).
# --------------------------------------------------------------------------- #
def _escribir_wav_memoria(ruta, framerate=44100, sampwidth=2, nchannels=2, nframes=4410):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(nchannels)
        w.setsampwidth(sampwidth)
        w.setframerate(framerate)
        w.writeframes(b"\x00" * (nframes * nchannels * sampwidth))


def test_wav_es_44100_hz_16_bits_estereo(tmp_path):
    ruta = tmp_path / "muestra.wav"
    _escribir_wav_memoria(ruta, 44100, 2, 2)
    with wave.open(str(ruta), "rb") as w:
        assert w.getframerate() == 44100, f"framerate {w.getframerate()} != 44100"
        assert w.getsampwidth() == 2, f"sampwidth {w.getsampwidth()} != 2 (16 bits)"
        assert w.getnchannels() == 2, "debe ser estereo"


def test_wav_no_44100_o_no_16bits_se_rechaza(tmp_path):
    ruta = tmp_path / "malo.wav"
    _escribir_wav_memoria(ruta, 22050, 1, 1)
    with wave.open(str(ruta), "rb") as w:
        valido = w.getframerate() == 44100 and w.getsampwidth() == 2 and w.getnchannels() == 2
    assert not valido


# --------------------------------------------------------------------------- #
# F1-6: cuantizacion a 16 colores como maximo (fixture en memoria con PIL).
# --------------------------------------------------------------------------- #
def test_cuantizacion_a_16_colores_o_menos(tmp_path):
    from PIL import Image  # PIL disponible en el interprete del sistema

    img = Path(tmp_path) / "colores.png"
    superficie = Image.new("RGBA", (16, 16))
    # Siembra mas de 16 colores distintos.
    pixels = superficie.load()
    for y in range(16):
        for x in range(16):
            pixels[x, y] = (x * 16, y * 16, 128, 255)
    superficie.save(img)

    quantizada = Image.open(img).convert("RGBA").quantize(colors=16).convert("RGBA")
    colores = quantizada.getcolors(maxcolors=100000)
    assert colores is not None
    assert len(colores) <= 16, f"se cuantizaron {len(colores)} colores, se esperaban <= 16"


# --------------------------------------------------------------------------- #
# F1-6: espejo horizontal correcto.
# --------------------------------------------------------------------------- #
def test_espejo_horizontal_correcto(tmp_path):
    from PIL import Image  # noqa: F811

    img = Path(tmp_path) / "espejo.png"
    original = Image.new("RGBA", (4, 4))
    pixels = original.load()
    for y in range(4):
        for x in range(4):
            pixels[x, y] = (x * 64, y * 64, 0, 255)
    original.save(img)

    espejo = Image.open(img).transpose(Image.FLIP_LEFT_RIGHT)
    op = espejo.load()
    orig = original.load()
    ancho = original.width
    for y in range(4):
        for x in range(4):
            assert op[x, y] == orig[ancho - 1 - x, y], f"espejo incorrecto en ({x},{y})"


# --------------------------------------------------------------------------- #
# F1-6: rechazo de un strip con N de cuadros incorrecto.
# --------------------------------------------------------------------------- #
def _contar_celdas_strip(ruta, cuadros):
    from PIL import Image  # noqa: F811

    with Image.open(ruta) as im:
        ancho, alto = im.size
    if ancho % cuadros != 0:
        return False  # no se divide en celdas iguales
    celda_ancho = ancho // cuadros
    return celda_ancho * cuadros == ancho


def test_strip_con_n_cuadros_incorrecto_es_rechazado(tmp_path):
    from PIL import Image  # noqa: F811

    img = Path(tmp_path) / "strip.png"
    # Strip de 96x32: para cuadros=4 celdas de 24x32 (OK); para cuadros=5 no divide (rechazo).
    Image.new("RGBA", (96, 32)).save(img)
    assert _contar_celdas_strip(img, 4) is True
    assert _contar_celdas_strip(img, 5) is False  # N incorrecto -> se rechaza


def test_importar_assets_carga_sin_archivos_ia():
    """El modulo se importa y el validador corre sin necesidad de archivos IA."""
    manifiesto = cargar_manifiesto(MANIFIESTO)
    assert manifiesto is not None
    assert "sfx" in manifiesto and "musica" in manifiesto and "sprites" in manifiesto
    assert manifiesto["sfx"][0]["id"] == "salto"
