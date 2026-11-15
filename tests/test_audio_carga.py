#---- Pruebas de carga y sintesis de audio ----#
import os
import sys
import wave
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pygame
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

import audio

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


#---- Comprobacion de claves de sintesis ----#
def test_claves_de_sintesis_completas():
    a = audio.Audio()
    assert a.activo
    claves = set(a.sonidos.keys())
    assert ESPERADAS_SFX <= claves, f"Faltan claves de sonido: {ESPERADAS_SFX - claves}"
    assert "dron_catacumbas" in claves
    assert "corazon_latido" in claves


#---- Carga desde archivo WAV ----#
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


def test_wav_de_prueba_en_assets_audio_sfx_se_carga():
    prueba = DIR_SFX_REAL / "salto_prueba.wav"
    try:
        _escribir_wav(prueba)
        audio.Audio.DIR_SFX_WAV = DIR_SFX_REAL
        instancia = audio.Audio.__new__(audio.Audio)
        assert instancia._cargar_sfx("salto_prueba") is not None
    finally:
        audio.Audio.DIR_SFX_WAV = DIR_SFX_REAL
        prueba.unlink(missing_ok=True)
