# tests/test_audio_carga.py — F2-3: carga de SFX desde disco con síntesis de respaldo
# Sin archivos de IA la síntesis no cambia; con un WAV de prueba en assets/audio/sfx se carga.
import os
import sys
import wave
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pygame  # noqa: E402
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

import audio  # noqa: E402

DIR_SFX_REAL = RAIZ / "assets" / "audio" / "sfx"

ESPERADAS_SFX = {
    "salto", "dash", "ataque", "pala", "stomp", "onda", "jefe_aviso", "jefe_fase",
    "pala_recoger", "dash_recoger", "checkpoint", "vida_extra", "ui", "daño", "muerte",
    "meta", "rebote_pala", "corazon_latido", "corazon", "dron_catacumbas", "alma",
} | {f"alma_{i}" for i in range(1, 7)}


def _escribir_wav(ruta, framerate=44100, sampwidth=2, nchannels=2, nframes=1000):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(nchannels)
        w.setsampwidth(sampwidth)
        w.setframerate(framerate)
        w.writeframes(b"\x00" * (nframes * nchannels * sampwidth))


# --------------------------------------------------------------------------- #
# F2-3: sin archivos IA la síntesis no cambia (mismo conteo y mismas claves).
# --------------------------------------------------------------------------- #
def test_sin_archivos_ia_la_sintesis_no_cambia():
    a = audio.Audio()
    assert a.activo
    claves = set(a.sonidos.keys())
    assert ESPERADAS_SFX <= claves, f"faltan claves de síntesis: {ESPERADAS_SFX - claves}"
    # El dron y el corazon no deben perderse.
    assert "dron_catacumbas" in claves
    assert "corazon_latido" in claves


# --------------------------------------------------------------------------- #
# F2-1 / F2-3: _cargar_sfx devuelve None sin archivo y carga el WAV si existe.
# --------------------------------------------------------------------------- #
def test_cargar_sfx_devuelve_none_sin_archivo(tmp_path, monkeypatch):
    monkeypatch.setattr(audio.Audio, "DIR_SFX_WAV", tmp_path / "sfx", raising=False)
    (tmp_path / "sfx").mkdir(parents=True, exist_ok=True)
    instancia = audio.Audio.__new__(audio.Audio)
    assert instancia._cargar_sfx("salto") is None


def test_cargar_sfx_carga_wav_si_existe(tmp_path, monkeypatch):
    monkeypatch.setattr(audio.Audio, "DIR_SFX_WAV", tmp_path / "sfx", raising=False)
    sfx_dir = tmp_path / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    _escribir_wav(sfx_dir / "salto.wav")
    instancia = audio.Audio.__new__(audio.Audio)
    cargado = instancia._cargar_sfx("salto")
    assert cargado is not None
    assert isinstance(cargado, pygame.mixer.Sound)


# --------------------------------------------------------------------------- #
# F2-3: con un WAV de prueba en assets/audio/sfx se carga ese archivo.
# (Se valida contra el directorio real, luego se limpia el archivo de prueba.)
# --------------------------------------------------------------------------- #
def test_wav_de_prueba_en_assets_audio_sfx_se_carga():
    prueba = DIR_SFX_REAL / "salto_prueba.wav"
    try:
        _escribir_wav(prueba)
        monkeypatch = None
        # Forzar a Audio a usar el directorio real donde acaba de escribirse el WAV.
        audio.Audio.DIR_SFX_WAV = DIR_SFX_REAL
        instancia = audio.Audio.__new__(audio.Audio)
        assert instancia._cargar_sfx("salto_prueba") is not None
    finally:
        audio.Audio.DIR_SFX_WAV = DIR_SFX_REAL  # restaurar valor por defecto
        prueba.unlink(missing_ok=True)
