# ============================================================
# generar_proyecto_nativo.py — IN CRYPTA como proyecto GDevelop
# ============================================================
# Genera un proyecto GDevelop nativo (JSON + PNGs) a partir de
# los mismos mapas y entidades del juego Pygame. No usa el runtime
# JavaScript: el movimiento, las colisiones y los eventos viven en
# el proyecto de GDevelop.
#
# La geometría, las texturas y el orden de las escenas salen del
# juego y del manifiesto declarativo (tools/exportador/); este
# archivo aporta las reglas de juego expressed como eventos.
# ============================================================

from __future__ import annotations

import array
import json
import math
import os
import random
import shutil
import struct
import sys
import textwrap
import uuid
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from config import (
    ALMAS_POR_VIDA,
    CAMARA_SUAVIZADO,
    ALTO,
    AMARILLO,
    ANCHO,
    CREMA,
    DASH_DURACION,
    DASH_VELOCIDAD,
    GRAVEDAD,
    HUESO,
    JEFE_ALTO,
    JEFE_ANCHO,
    JEFE_ONDA_VELOCIDAD,
    MAX_CAIDA,
    NIEBLA,
    ORO,
    ROJO,
    SACUDIDA_DURACION,
    SALTO,
    SANGRE,
    TURQUESA,
    VELOCIDAD,
    VELOCIDAD_ENEMIGO,
    VIDAS_INICIALES,
    VIDAS_MAXIMAS,
)
from entidades import Alma, Custodio, Enemigo, Jugador, OndaCustodio, PalaRecogible
from exportador import sprites as sprites_export
from exportador.adaptadores import ADAPTADORES, adaptador, variables_instancia
from exportador.manifiesto import escenas_campaña, escenas_salas
from exportador.modelo import Escena, leer_escena
from exportador.pipeline import (
    KINDS_SIEMPRE,
    instancias_entidades,
    nombre_objeto,
    nombre_textura,
    objetos_entidades,
)
from exportador.reglas import reglas_escena
from exportador.gdevelop import (
    _animacion,
    accion,
    capa_base,
    capa_ui,
    comportamiento_enemigo,
    comportamiento_jugador,
    comportamiento_plataforma,
    cond,
    cond_or,
    escena,
    escena_mangled,
    evento,
    instancia,
    objeto_golpe,
    objeto_jefe,
    objeto_jugador,
    objeto_onda,
    objeto_onda_der,
    objeto_pala,
    objeto_plataforma,
    objeto_sprite,
    objeto_texto,
    objeto_tiled,
    recurso_audio,
    recurso_fuente,
    recurso_imagen,
    uid,
    variables_enemigo,
    variables_jefe,
    variables_jugador,
    variables_onda,
    variables_plataforma,
)
from nivel import Nivel, DECORACIONES
from niveles import NIVELES, SALAS_PRUEBA


OUT = ROOT / "export" / "gdevelop_nativo"
ASSETS = OUT / "assets"
PROJECT_NAME = "IN_CRYPTA_NATIVO.json"
BASE_PROJECT_DEFAULT = (
    Path.home()
    / "Documentos"
    / "GDevelop projects"
    / "My project"
    / "Cryptus - Copy.json"
)
BASE_PROJECT = (
    BASE_PROJECT_DEFAULT
    if BASE_PROJECT_DEFAULT.exists()
    else (OUT / "In_Crypta_V0.9.9.json")
)
FONT_SOURCE_DEFAULT = Path("/usr/share/fonts/noto/NotoSerifDisplay-Bold.ttf")
FONT_SOURCE = (
    FONT_SOURCE_DEFAULT
    if FONT_SOURCE_DEFAULT.exists()
    else (ASSETS / "NotoSerifDisplay-Bold.ttf")
)
FONT_RESOURCE = "FuenteHUD"
FONT_FILE = "assets/NotoSerifDisplay-Bold.ttf"

GAME_W = ANCHO
GAME_H = ALTO
RENDER_W = 1920
RENDER_H = 1080
# El zoom se deriva de la resolución: el mundo visible tiene que ser
# exactamente ANCHO x ALTO como en el Pygame (si no, la cámara recorta
# el nivel y el HUD inferior queda fuera de pantalla).
GAME_ZOOM = RENDER_W / ANCHO

# Sacudida de cámara: la intensidad cae linealmente durante la duración
# (camara.py::Camara.actualizar_sacudida) y el offset es aleatorio.
_INTENSIDAD = f"sacudida_f * max(0, sacudida_t) / {SACUDIDA_DURACION}"
SACUDIDA_EXPRESION_X = f"RandomInRange(-({_INTENSIDAD}), ({_INTENSIDAD}))"
SACUDIDA_EXPRESION_Y = f"RandomInRange(-({_INTENSIDAD}), ({_INTENSIDAD}))"
ASSET_SCALE = 2
TILE = 32
PLAYER_W = 32
PLAYER_H = 32
ENEMY_SPRITE_H = 32
SOUL_SPRITE = 24
GATE_W = 42
GATE_H = 58
PINCHOS_W = 24
PINCHOS_H = 20
ONDA_W = 20
ONDA_H = 22


# ------------------------------------------------------------
# Utilidades de GDevelop
# ------------------------------------------------------------


# ------------------------------------------------------------
# Cámara y fondos
# ------------------------------------------------------------
class CamaraCompleta:
    x = 0.0
    y = 0.0
    offset_x = 0.0
    offset_y = 0.0

    def is_on_screen(self, rect, margen=64):
        return True

    def aplicar_rect(self, rect):
        return pygame.Rect(rect)

    def aplicar_x(self, x):
        return x

    def aplicar_y(self, y):
        return y


def _gradiente(surface: pygame.Surface, arriba, abajo):
    alto = surface.get_height()
    for y in range(alto):
        t = y / max(1, alto - 1)
        color = tuple(int(arriba[i] + (abajo[i] - arriba[i]) * t) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


def _estrellas(surface: pygame.Surface, semilla: int, cantidad: int, color, zona=0.8):
    rnd = random.Random(semilla)
    ancho, alto = surface.get_size()
    for _ in range(cantidad):
        x = rnd.randrange(ancho)
        y = rnd.randrange(max(1, int(alto * zona)))
        r = rnd.choice((1, 1, 1, 2))
        pygame.draw.circle(surface, color, (x, y), r)


def _luna(surface: pygame.Surface, x: int, y: int, radio: int, color, brillo):
    pygame.draw.circle(surface, color, (x, y), radio)
    pygame.draw.circle(surface, brillo, (x - radio // 5, y - radio // 5), max(3, radio // 3))


def _colinas(surface, alto_base, semilla, color):
    ancho = surface.get_width()
    alto = surface.get_height()
    rnd = random.Random(semilla)
    puntos = [(0, alto)]
    x = 0
    base = alto_base
    while x <= ancho:
        base += rnd.randint(-8, 8)
        base = max(alto_base - 26, min(alto_base + 18, base))
        puntos.append((x, base))
        x += 42
    puntos.extend([(ancho, alto)])
    pygame.draw.polygon(surface, color, puntos)


def _niebla(surface, color, y_inicio, y_fin, alfa):
    capa = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    alto = y_fin - y_inicio
    for i in range(alto):
        a = int(alfa * (1 - i / max(1, alto - 1)))
        pygame.draw.line(capa, (*color, a), (0, y_inicio + i), (surface.get_width(), y_inicio + i))
    surface.blit(capa, (0, 0))


def generar_fondo_nivel(nivel: Nivel) -> pygame.Surface:
    surface = pygame.Surface((nivel.ancho, nivel.alto))
    tema = nivel.tema

    if tema == "cripta":
        _gradiente(surface, (8, 8, 14), (22, 20, 28))
        _estrellas(surface, 202, 90, (50, 52, 66), 0.55)
        for x in range(30, nivel.ancho, 280):
            pygame.draw.rect(surface, (20, 19, 28), (x, 160, 190, 260))
            pygame.draw.rect(surface, (37, 35, 48), (x + 9, 169, 172, 242), 4)
            pygame.draw.arc(surface, (43, 40, 56), (x - 14, 102, 218, 214), 0.08, 3.06, 8)
            pygame.draw.line(surface, (54, 48, 58), (x + 21, 210), (x + 21, 410), 3)
            pygame.draw.line(surface, (54, 48, 58), (x + 169, 210), (x + 169, 410), 3)
        for x in range(120, nivel.ancho, 410):
            pygame.draw.circle(surface, (80, 54, 24), (x, 290), 18)
            pygame.draw.circle(surface, (150, 99, 36), (x, 290), 9)
            pygame.draw.rect(surface, (186, 176, 148), (x - 3, 297, 6, 30), border_radius=2)
            pygame.draw.polygon(surface, (214, 174, 82), [(x, 276), (x + 5, 288), (x, 296), (x - 5, 288)])
    elif tema == "osario":
        _gradiente(surface, (13, 8, 12), (33, 18, 22))
        _estrellas(surface, 303, 80, (68, 42, 48), 0.6)
        _luna(surface, int(nivel.ancho * 0.52), 88, 54, (62, 28, 34), (146, 60, 54))
        for x in range(-80, nivel.ancho, 360):
            pygame.draw.arc(surface, (56, 36, 38), (x, 150, 340, 330), math.pi * 0.05, math.pi * 0.95, 9)
            pygame.draw.arc(surface, (39, 24, 27), (x + 30, 190, 280, 260), math.pi * 0.08, math.pi * 0.92, 4)
            pygame.draw.line(surface, (70, 45, 44), (x + 25, 270), (x + 25, 430), 6)
            pygame.draw.line(surface, (70, 45, 44), (x + 315, 270), (x + 315, 430), 6)
        for x in range(60, nivel.ancho, 220):
            pygame.draw.line(surface, (72, 54, 50), (x, 400), (x + 42, 420), 2)
            pygame.draw.circle(surface, (92, 76, 68), (x, 400), 3)
    else:
        _gradiente(surface, (8, 12, 20), (25, 32, 29))
        _estrellas(surface, 101, 130, (62, 74, 84), 0.7)
        _luna(surface, int(nivel.ancho * 0.82), 92, 46, (70, 74, 78), (116, 120, 116))
        _colinas(surface, nivel.alto - 120, 7, (17, 25, 24))
        _colinas(surface, nivel.alto - 76, 11, (12, 18, 18))

    # Decoración estática del nivel, dibujada sobre el fondo lejano.
    camara = CamaraCompleta()
    nivel.dibujar_solidos(surface, camara)
    nivel.dibujar_decoraciones(surface, camara)

    if tema == "cripta":
        _niebla(surface, (104, 122, 130), nivel.alto - 110, nivel.alto, 24)
    elif tema == "osario":
        _niebla(surface, (130, 72, 70), nivel.alto - 100, nivel.alto, 18)
    else:
        _niebla(surface, (104, 122, 130), nivel.alto - 100, nivel.alto, 30)
    return surface


def generar_fondo_victoria() -> pygame.Surface:
    surface = pygame.Surface((GAME_W, GAME_H))
    _gradiente(surface, (8, 8, 14), (24, 17, 26))
    _estrellas(surface, 909, 110, (62, 54, 78), 0.72)
    _luna(surface, 720, 118, 62, (46, 36, 54), (98, 78, 112))
    _colinas(surface, GAME_H - 105, 17, (12, 12, 19))
    _niebla(surface, (104, 92, 122), GAME_H - 150, GAME_H, 26)

    # Un portón lejano, como cierre visual.
    x = GAME_W // 2
    pygame.draw.circle(surface, (42, 34, 22), (x, 316), 64)
    pygame.draw.rect(surface, (7, 6, 10), (x - 50, 300, 100, 128))
    pygame.draw.circle(surface, (7, 6, 10), (x, 300), 50)
    pygame.draw.rect(surface, (72, 55, 38), (x - 56, 300, 6, 128))
    pygame.draw.rect(surface, (72, 55, 38), (x + 50, 300, 6, 128))
    pygame.draw.arc(surface, (72, 55, 38), (x - 60, 246, 120, 70), 0.08, 3.06, 6)
    pygame.draw.rect(surface, ORO, (x - 4, 326, 8, 44))
    pygame.draw.circle(surface, AMARILLO, (x, 312), 5)
    return surface


# ------------------------------------------------------------
# Sprites
# ------------------------------------------------------------
def guardar_2x(surface: pygame.Surface, nombre: str, destino_dir: Path | None = None) -> None:
    directorio = destino_dir or ASSETS
    destino = pygame.transform.smoothscale(
        surface,
        (surface.get_width() * ASSET_SCALE, surface.get_height() * ASSET_SCALE),
    )
    pygame.image.save(destino, directorio / nombre)


def _jugador_pose(
    nombre: str,
    pose: str | None,
    direccion: int = 1,
    con_pala: bool = True,
    destino_dir: Path | None = None,
) -> None:
    surface = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
    jugador = Jugador(4, 1)
    jugador.direccion = direccion
    jugador.en_suelo = pose is None
    jugador.vx = VELOCIDAD if pose is None else 0
    jugador.tiempo_animacion = 0.35
    jugador.dibujar(surface, CamaraCompleta(), 0.0, pose=pose, con_pala=con_pala)
    guardar_2x(surface, nombre, destino_dir)


def guardar_jugador(destino_dir: Path | None = None) -> None:
    _jugador_pose("jugador.png", None, destino_dir=destino_dir)
    _jugador_pose("jugador_caida_1.png", "caida", destino_dir=destino_dir)
    _jugador_pose("jugador_caida_2.png", "caida2", destino_dir=destino_dir)
    _jugador_pose("jugador_ataque_1.png", "ataque1", con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_ataque_2.png", "ataque2", con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_ataque_3.png", "ataque3", con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_izq.png", None, -1, destino_dir=destino_dir)
    _jugador_pose("jugador_caida_izq_1.png", "caida", -1, destino_dir=destino_dir)
    _jugador_pose("jugador_caida_izq_2.png", "caida2", -1, destino_dir=destino_dir)
    _jugador_pose("jugador_ataque_izq_1.png", "ataque1", -1, con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_ataque_izq_2.png", "ataque2", -1, con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_ataque_izq_3.png", "ataque3", -1, con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_sin_pala.png", None, con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_caida_sin_pala_1.png", "caida", con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_caida_sin_pala_2.png", "caida2", con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_izq_sin_pala.png", None, -1, con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_caida_izq_sin_pala_1.png", "caida", -1, con_pala=False, destino_dir=destino_dir)
    _jugador_pose("jugador_caida_izq_sin_pala_2.png", "caida2", -1, con_pala=False, destino_dir=destino_dir)


def guardar_puerta(destino_dir: Path | None = None) -> None:
    surface = pygame.Surface((GATE_W, GATE_H), pygame.SRCALPHA)
    dummy = object.__new__(Nivel)
    dummy.meta = pygame.Rect(11, GATE_H - 30, 20, 30)
    dummy.dibujar_meta(surface, CamaraCompleta())
    guardar_2x(surface, "puerta.png", destino_dir)


def guardar_solido(destino_dir: Path | None = None) -> None:
    # La textura del sólido debe ser opaca: GDevelop calcula la máscara de
    # colisión del comportamiento Platform a partir del alfa de la textura.
    # Si queda casi transparente (alfa 1), la máscara se pierde y el jugador
    # atraviesa el suelo ("cosas pisadas" / colisiones rotas).
    directorio = destino_dir or ASSETS
    surface = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surface.fill((68, 62, 70, 255))
    pygame.image.save(surface, directorio / "solido.png")


def guardar_golpe(destino_dir: Path | None = None) -> None:
    directorio = destino_dir or ASSETS
    for viejo in ("golpe.png", "golpe_izq.png"):
        (directorio / viejo).unlink(missing_ok=True)

    for indice in range(1, 4):
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        inclinacion = (indice - 2) * 0.10

        pygame.draw.arc(
            surface,
            (180, 190, 202, 34),
            (3, 3, 26, 26),
            -1.25 + inclinacion,
            1.12 + inclinacion,
            3,
        )
        pygame.draw.arc(
            surface,
            (145, 153, 166, 165),
            (7, 4, 21, 24),
            -1.10 + inclinacion,
            0.98 + inclinacion,
            2,
        )
        pygame.draw.arc(
            surface,
            (226, 234, 242, 225),
            (10, 7, 16, 18),
            -0.92 + inclinacion,
            0.78 + inclinacion,
            1,
        )
        for y, x0, x1 in ((8, 9, 15), (12, 8, 18), (21, 9, 17), (25, 12, 18)):
            pygame.draw.line(
                surface,
                (205, 214, 225, 105),
                (x0 + indice - 2, y),
                (x1 + indice - 2, y),
                1,
            )
        pygame.draw.polygon(
            surface,
            (185, 194, 205),
            [(5, 25), (8, 22), (10, 25), (8, 28)],
        )
        pygame.draw.line(
            surface,
            (244, 248, 252),
            (7, 24),
            (8, 27),
            1,
        )

        pygame.image.save(surface, directorio / f"golpe_der_{indice}.png")
        pygame.image.save(
            pygame.transform.flip(surface, True, False),
            directorio / f"golpe_izq_{indice}.png",
        )


def guardar_jefe(destino_dir: Path | None = None) -> None:
    surface = pygame.Surface((JEFE_ANCHO, JEFE_ALTO), pygame.SRCALPHA)
    jefe = Custodio(pygame.Rect(0, 0, JEFE_ANCHO, JEFE_ALTO), -1000, 1000)
    jefe.dibujar(surface, CamaraCompleta(), 0.0)
    guardar_2x(surface, "jefe.png", destino_dir)


def guardar_onda(destino_dir: Path | None = None) -> None:
    surface = pygame.Surface((ONDA_W, ONDA_H), pygame.SRCALPHA)
    onda = OndaCustodio(ONDA_W // 2, ONDA_H, 1, 0)
    onda.dibujar(surface, CamaraCompleta(), 0.0)
    guardar_2x(surface, "onda_jefe.png", destino_dir)


def _audio_pcm_stereo(freq_inicio, freq_fin, duracion, volumen, tipo="sine", ruido=0.0):
    tasa = 44100
    total = max(1, int(tasa * duracion))
    fase = 0.0
    muestras = array.array("h")
    for i in range(total):
        progreso = i / max(1, total - 1)
        frecuencia = freq_inicio + (freq_fin - freq_inicio) * progreso
        fase += 2 * math.pi * frecuencia / tasa
        if tipo == "square":
            onda = 1.0 if math.sin(fase) >= 0 else -1.0
        elif tipo == "saw":
            onda = 2.0 * ((fase / (2 * math.pi)) % 1.0) - 1.0
        elif tipo == "bell":
            onda = math.sin(fase) + 0.28 * math.sin(fase * 2) + 0.12 * math.sin(fase * 3)
        elif tipo == "ruido":
            onda = random.uniform(-1.0, 1.0)
        else:
            onda = math.sin(fase)
        if ruido:
            onda = onda * (1.0 - ruido) + random.uniform(-1.0, 1.0) * ruido
        ataque = min(1.0, (i / tasa) / 0.012)
        caida = max(0.0, 1.0 - (progreso ** 1.6))
        valor = int(32767 * volumen * ataque * caida * onda)
        clamped = max(-32768, min(32767, valor))
        muestras.append(clamped)
        muestras.append(clamped)
    return muestras.tobytes()


def _guardar_wav(nombre: str, pcm_bytes: bytes, destino_dir: Path | None = None) -> None:
    directorio = destino_dir or ASSETS
    with wave.open(str(directorio / nombre), "wb") as archivo:
        archivo.setnchannels(2)
        archivo.setsampwidth(2)
        archivo.setframerate(44100)
        archivo.writeframes(pcm_bytes)


def guardar_audio(destino_dir: Path | None = None) -> None:
    _guardar_wav("sfx_salto.wav", _audio_pcm_stereo(340, 620, 0.14, 0.24), destino_dir)
    _guardar_wav("sfx_alma.wav", _audio_pcm_stereo(700, 980, 0.20, 0.22, "bell"), destino_dir)
    _guardar_wav("sfx_dash.wav", _audio_pcm_stereo(150, 70, 0.12, 0.20, "saw", 0.10), destino_dir)
    _guardar_wav("sfx_pala.wav", _audio_pcm_stereo(820, 220, 0.13, 0.18, "saw", 0.18), destino_dir)
    _guardar_wav("sfx_pala_recoger.wav", _audio_pcm_stereo(620, 800, 0.18, 0.18, "bell"), destino_dir)
    _guardar_wav("sfx_golpe.wav", _audio_pcm_stereo(130, 55, 0.16, 0.24, "square"), destino_dir)
    _guardar_wav("sfx_dano.wav", _audio_pcm_stereo(240, 70, 0.28, 0.22, "saw", 0.08), destino_dir)
    _guardar_wav("sfx_ui.wav", _audio_pcm_stereo(520, 380, 0.06, 0.14, "square"), destino_dir)

    vida = b"".join(
        _audio_pcm_stereo(frecuencia, frecuencia * 1.01, duracion, 0.20, "bell")
        for frecuencia, duracion in ((659, 0.10), (784, 0.10), (1046, 0.24))
    )
    _guardar_wav("sfx_vida.wav", vida, destino_dir)

    meta = b"".join(
        _audio_pcm_stereo(frecuencia, frecuencia * 1.01, duracion, 0.20, "bell")
        for frecuencia, duracion in ((392, 0.10), (523, 0.12), (659, 0.14), (784, 0.30))
    )
    _guardar_wav("sfx_meta.wav", meta, destino_dir)


def guardar_barras(destino_dir: Path | None = None) -> None:
    barra = pygame.Surface((GAME_W, 52), pygame.SRCALPHA)
    barra.fill((5, 5, 9, 205))
    pygame.draw.line(barra, (*ORO, 255), (0, 51), (GAME_W, 51), 1)
    guardar_2x(barra, "barra_hud.png", destino_dir)

    pista = pygame.Surface((GAME_W, 58), pygame.SRCALPHA)
    pista.fill((5, 5, 9, 215))
    pygame.draw.line(pista, (*ORO, 255), (0, 0), (GAME_W, 0), 1)
    guardar_2x(pista, "barra_pista.png", destino_dir)


def generar_fondo_pausa() -> pygame.Surface:
    surface = pygame.Surface((GAME_W, GAME_H))
    _gradiente(surface, (5, 5, 9), (22, 16, 25))
    _estrellas(surface, 707, 70, (54, 42, 62), 0.65)
    pygame.draw.rect(surface, (8, 7, 12), (210, 88, 540, 364))
    pygame.draw.rect(surface, ORO, (210, 88, 540, 364), 2)
    pygame.draw.line(surface, SANGRE, (290, 200), (670, 200), 1)
    pygame.draw.line(surface, SANGRE, (290, 444), (670, 444), 1)
    return surface


def generar_assets(escenas: list[Escena], directorio_assets: Path | None = None) -> None:
    directorio = directorio_assets or ASSETS
    directorio.mkdir(parents=True, exist_ok=True)
    titulo = pygame.image.load(str(ROOT / "capturas" / "titulo.png"))
    pygame.image.save(
        pygame.transform.smoothscale(titulo, (RENDER_W, RENDER_H)),
        directorio / "titulo.png",
    )
    if FONT_SOURCE.exists() and FONT_SOURCE.resolve() != (directorio / FONT_SOURCE.name).resolve():
        shutil.copy2(FONT_SOURCE, directorio / FONT_SOURCE.name)

    guardar_jugador(directorio)
    guardar_puerta(directorio)
    guardar_solido(directorio)
    guardar_golpe(directorio)
    guardar_jefe(directorio)
    guardar_onda(directorio)
    guardar_audio(directorio)
    guardar_barras(directorio)

    # Las texturas de las entidades se dibujan con el código del propio juego
    # y en el tamaño exacto de su rect: así no hay deformación en GDevelop.
    vistas: set[str] = set()
    for escena_modelo in escenas:
        for entidad in escena_modelo.entidades:
            adapt = adaptador(entidad.kind)
            if adapt.en_fondo:
                continue
            nombre = nombre_textura(adapt, entidad)
            if nombre in vistas:
                continue
            vistas.add(nombre)
            if adapt.sprite:
                ancho, alto = adapt.sprite
            else:
                ancho, alto = entidad.rect.width, entidad.rect.height
            sprites_export.guardar(entidad.kind, ancho, alto, directorio / f"{nombre.lower()}.png")

    # Las texturas de los tipos que siempre existen, aunque ningún mapa los
    # tenga, para que el objeto quede con su recurso y no con uno roto.
    for kind in KINDS_SIEMPRE:
        adapt = adaptador(kind)
        ancho, alto = adapt.sprite or (32, 32)
        sprites_export.guardar(kind, ancho, alto, directorio / f"{adapt.textura.lower()}.png")

    for escena_modelo in escenas:
        pygame.image.save(
            generar_fondo_nivel(escena_modelo.nivel),
            directorio / f"fondo_{escena_modelo.spec.clave}.png",
        )
    guardar_2x(generar_fondo_victoria(), "victoria.png", directorio)
    guardar_2x(generar_fondo_pausa(), "pausa.png", directorio)


# ------------------------------------------------------------
# Eventos compartidos
# ------------------------------------------------------------
def accion_sonido(nombre: str) -> dict:
    return accion("PlaySound", [f"SFX_{nombre}", "no", "100", "1"])


def acciones_sacudida(fuerza: float, duracion: float) -> list[dict]:
    """Sacudida de cámara (camara.py::Camara.sacudir)."""
    return [
        accion("SetNumberVariable", ["sacudida_f", "=", str(fuerza)]),
        accion("SetNumberVariable", ["sacudida_t", "=", str(duracion)]),
    ]


def eventos_dano(alto: int, destino_muerte: str = "Titulo") -> list[dict]:
    subeventos = [
        evento(
            [cond("NumberVariable", ["vidas", ">", "0"])],
            [
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("Scene", ["CurrentSceneName()", "no"]),
            ],
        ),
        evento(
            [cond("NumberVariable", ["vidas", "<=", "0"])],
            [
                accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["almas_totales", "=", "0"]),
                accion("Scene", [f'"{destino_muerte}"', "no"]),
            ],
        ),
    ]
    return [
        evento(
            [cond("CollisionNP", ["Jugador", "Pinchos", "no"])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                *acciones_sacudida(9.0, 0.22),
            ],
            subeventos,
        ),
        evento(
            [cond("PosY", ["Jugador", ">", str(alto + 120)])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                *acciones_sacudida(9.0, 0.22),
            ],
            subeventos,
        ),
    ]


PISTAS_NATIVAS = {
    1: "FLECHAS: MOVERTE. ARRIBA: SALTAR. SHIFT: DASH. CRUZA EL PRIMER HUECO CON LA PLATAFORMA. LAS ALMAS DEL SALTO DE 3 BLOQUES MARCAN EL SALTO + DASH. EL POZO DE 7 NECESITA SHIFT EN EL AIRE. EN EL GRAN ABISMO SUBI EL ESCALON Y LA CORNISA, Y DASHEA DESDE ARRIBA.",
    2: "PRIMER ABISMO: SALTA Y USA SHIFT EN EL AIRE. LA PALA ESTA EN LA CORNISA. CRUZA EL HUECO GRANDE CON LA PLATAFORMA Y SUS ALMAS. EL ASCENSOR VERTICAL TE SUBE AL MURO. 10 ALMAS = 1 VIDA EXTRA.",
    3: "EL CUSTODIO TE PERSIGUE. ATACA SOLO CUANDO BRILLA EN ROJO. BUSCA LAS ALMAS Y ABRE EL PORTON.",
}


def acciones_camara_inicial(centro_x: int | str | None = None, centro_y: int | str | None = None) -> list[dict]:
    if centro_x is None:
        centro_x = GAME_W // 2
    if centro_y is None:
        centro_y = GAME_H // 2
    centro_x = str(centro_x)
    centro_y = str(centro_y)
    return [
        accion("SetNumberVariable", ["cam_x", "=", centro_x]),
        accion("SetNumberVariable", ["cam_y", "=", centro_y]),
        accion("SetNumberVariable", ["sacudida_f", "=", "0"]),
        accion("SetNumberVariable", ["sacudida_t", "=", "0"]),
        # La capa base muestra el mundo con el zoom del juego (1280x720
        # visibles) y sigue al jugador; la capa UI dibuja el HUD en pixels de
        # pantalla (zoom 1) y su cámara queda en el centro.
        #
        # Ojo: la acción que mueve el centro de la cámara se llama
        # "SetCameraCenterX/Y" ("Set" + nombre). "CameraCenterX/Y" a secas es
        # la condición/expresión que *consulta* la posición del centro.
        accion("ZoomCamera", [str(GAME_ZOOM), '""', "0"]),
        accion("SetCameraCenterX", ["=", centro_x, '""', "0"]),
        accion("SetCameraCenterY", ["=", centro_y, '""', "0"]),
        accion("ZoomCamera", ["1", '"UI"', "0"]),
        accion("SetCameraCenterX", ["=", str(GAME_W // 2), '"UI"', "0"]),
        accion("SetCameraCenterY", ["=", str(GAME_H // 2), '"UI"', "0"]),
    ]


def eventos_jefe(siguiente: str) -> list[dict]:
    """Eventos del jefe Custodio: patrulla, carga (telegrafía), disparo de ondas,
    ventana de vulnerabilidad, fases por vida y derrota."""
    return [
        # --- Temporizador del jefe: cuenta atrás entre ataques ---
        evento(
            [cond("NumberObjectVariable", ["Jefe", "timer", ">", "0"])],
            [accion("SetNumberObjectVariable", ["Jefe", "timer", "-", "TimeDelta()"])],
        ),

        # --- Estado 0 (patrulla) → Estado 1 (carga/telegrafía) ---
        evento(
            [
                cond("NumberObjectVariable", ["Jefe", "timer", "<=", "0"]),
                cond("NumberObjectVariable", ["Jefe", "estado", "=", "0"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "0.8"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
            ],
        ),

        # --- Estado 1 (carga) → Estado 2 (disparo): crear ondas ---
        evento(
            [
                cond("NumberObjectVariable", ["Jefe", "timer", "<=", "0"]),
                cond("NumberObjectVariable", ["Jefe", "estado", "=", "1"]),
            ],
            [
                accion_sonido("Golpe"),
                *acciones_sacudida(8.0, 0.20),
                accion(
                            "Create",
                            ["OndaIzq",
                        "Jefe.X()",
                        "Jefe.Y() + Jefe.Height() / 2",
                        '""',
                    ],
                ),
                accion(
                            "Create",
                            ["OndaDer",
                        "Jefe.X() + Jefe.Width()",
                        "Jefe.Y() + Jefe.Height() / 2",
                        '""',
                    ],
                ),
                accion(
                    "SetNumberObjectVariable",
                    ["OndaIzq", "velocidad", "=",
                     f"int({JEFE_ONDA_VELOCIDAD} * (0.7 + Jefe.Variable(fase) * 0.2))"],
                ),
                accion(
                    "SetNumberObjectVariable",
                    ["OndaDer", "velocidad", "=",
                     f"int({JEFE_ONDA_VELOCIDAD} * (0.7 + Jefe.Variable(fase) * 0.2))"],
                ),
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "2"]),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "0.3"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
            ],
        ),

        # --- Estado 2 (disparo) → Estado 3 (vulnerable) ---
        evento(
            [
                cond("NumberObjectVariable", ["Jefe", "timer", "<=", "0"]),
                cond("NumberObjectVariable", ["Jefe", "estado", "=", "2"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "3"]),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "1.5"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "1"]),
            ],
        ),

        # --- Estado 3 (vulnerable) → Estado 0 (patrulla) ---
        evento(
            [
                cond("NumberObjectVariable", ["Jefe", "timer", "<=", "0"]),
                cond("NumberObjectVariable", ["Jefe", "estado", "=", "3"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                accion(
                    "SetNumberObjectVariable",
                    ["Jefe", "timer", "=", "2.0 - Jefe.Variable(fase) * 0.4"],
                ),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
            ],
        ),

        # --- Patrulla del jefe (estado 0) ---
        evento(
            [
                cond("NumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                cond("NumberObjectVariable", ["Jefe", "dir", "=", "1"]),
                cond("PosX", ["Jefe", ">=", "Jefe.Variable(max_x)"]),
            ],
            [accion("SetNumberObjectVariable", ["Jefe", "dir", "=", "-1"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                cond("NumberObjectVariable", ["Jefe", "dir", "=", "-1"]),
                cond("PosX", ["Jefe", "<=", "Jefe.Variable(min_x)"]),
            ],
            [accion("SetNumberObjectVariable", ["Jefe", "dir", "=", "1"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jefe", "estado", "=", "0"]),
            ],
            [
                accion(
                    "SetX",
                    [
                        "Jefe",
                        "=",
                        "Jefe.X() + Jefe.Variable(dir) * "
                        + str(int(JEFE_ONDA_VELOCIDAD * 0.4)) + " * TimeDelta()",
                    ],
                ),
            ],
        ),

        # --- Movimiento de ondas ---
        evento(
            [],
            [
                accion(
                    "SetX",
                    ["OndaIzq", "=", "OndaIzq.X() - OndaIzq.Variable(velocidad) * TimeDelta()"],
                ),
                accion(
                    "SetX",
                    ["OndaDer", "=", "OndaDer.X() + OndaDer.Variable(velocidad) * TimeDelta()"],
                ),
            ],
        ),
        evento(
            [cond("PosX", ["OndaIzq", "<", "Jefe.X() - 1400"])],
            [accion("Delete", ["OndaIzq"])],
        ),
        evento(
            [cond("PosX", ["OndaDer", ">", "Jefe.X() + 1400"])],
            [accion("Delete", ["OndaDer"])],
        ),

        # --- Ondas dañan al jugador ---
        evento(
            [cond("CollisionNP", ["Jugador", "OndaIzq", "no"])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                accion("Delete", ["OndaIzq"]),
                accion("Scene", ["CurrentSceneName()", "no"]),
            ],
        ),
        evento(
            [cond("CollisionNP", ["Jugador", "OndaDer", "no"])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                accion("Delete", ["OndaDer"]),
                accion("Scene", ["CurrentSceneName()", "no"]),
            ],
        ),

        # --- Contacto con jefe (daño si NO es vulnerable) ---
        evento(
            [
                cond("CollisionNP", ["Jugador", "Jefe", "no"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
            ],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                accion("Scene", ["CurrentSceneName()", "no"]),
            ],
        ),

        # --- Golpe al jefe cuando es vulnerable ---
        evento(
            [
                cond("CollisionNP", ["GolpePala", "Jefe", "no"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "1"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "vida", "-", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "golpes_fase", "+", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "2.0"]),
                accion_sonido("Golpe"),
                accion("Delete", ["GolpePala"]),
            ],
        ),

        # --- Pisotón al jefe cuando es vulnerable ---
        evento(
            [
                cond("CollisionNP", ["Jugador", "Jefe", "no"]),
                cond("PosY", ["Jugador", "<", "Jefe.Y() - 10"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "1"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "vida", "-", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "golpes_fase", "+", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "2.0"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion_sonido("Golpe"),
                *acciones_sacudida(8.0, 0.20),
            ],
        ),

        # --- En fase 2, golpear al jefe con pala sin que sea vulnerable rebota al jugador ---
        evento(
            [
                cond("CollisionNP", ["GolpePala", "Jefe", "no"]),
                cond("NumberObjectVariable", ["Jefe", "fase", ">=", "2"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
            ],
            [
                accion_sonido("Golpe"),
                *acciones_sacudida(6.0, 0.14),
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed",
                    ["Jugador", "PlatformerObject", "=", "Jugador.Variable(dir) * -380"],
                ),
                accion("Delete", ["GolpePala"]),
            ],
        ),

        # --- Transición de fase por vida ---
        evento(
            [
                cond("NumberObjectVariable", ["Jefe", "vida", "<=", "Jefe.Variable(fase) * 2"]),
                cond("NumberObjectVariable", ["Jefe", "fase", "<", "3"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "fase", "+", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "golpes_fase", "=", "0"]),
                *acciones_sacudida(11.0, 0.26),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "1.0"]),
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
            ],
        ),

        # --- Jefe derrotado: se abre el portón de salida ---
        # No cambiamos de escena acá: el jugador tiene que cruzar el portón.
        # Eso convierte el combate en "escapar de la sala sellada".
        evento(
            [cond("NumberObjectVariable", ["Jefe", "vida", "<=", "0"])],
            [
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "4"]),
                accion("Delete", ["Jefe"]),
                *acciones_sacudida(8.0, 0.18),
                accion("Delete", ["OndaIzq"]),
                accion("Delete", ["OndaDer"]),
                accion_sonido("Meta"),
                accion("SetNumberVariable", ["almas_totales", "+", "almas"]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["jefe_derrotado", "=", "1"]),
                accion("TextObject::String", ["HUD_Aviso", "=", '"¡SALIDA ABIERTA!"']),
            ],
        ),
    ]


def eventos_nivel(
    nivel: Nivel,
    indice: int,
    total: int,
    *,
    siguiente: str | None = None,
    pala_inicial: bool | None = None,
    texto_dash_sin_pala: str | None = None,
    destino_muerte: str = "Titulo",
    reiniciar_vidas: bool = False,
) -> list[dict]:
    # La cámara se controla por su centro. Si el nivel es más grande que la
    # pantalla, el centro sigue al jugador entre los bordes; si es más chico,
    # el nivel queda centrado (igual que camara.py de la versión pygame).
    if nivel.ancho >= GAME_W:
        centro_x = GAME_W // 2
        max_cam_x = nivel.ancho - GAME_W // 2
    else:
        centro_x = max_cam_x = nivel.ancho // 2
    if nivel.alto >= GAME_H:
        centro_y = GAME_H // 2
        max_cam_y = nivel.alto - GAME_H // 2
    else:
        centro_y = max_cam_y = nivel.alto // 2
    objetivo_x = min(max(nivel.spawn[0] + PLAYER_W // 2, centro_x), max_cam_x)
    objetivo_y = min(max(nivel.spawn[1] + PLAYER_H // 2, centro_y), max_cam_y)
    if siguiente is None:
        siguiente = "Victoria" if indice == total else f"Nivel {indice + 1}"
    if pala_inicial is None:
        pala_inicial = indice == 3
    if texto_dash_sin_pala is None:
        texto_dash_sin_pala = (
            '"ESPACIO: SALTO · SHIFT: DASH · BUSCÁ LA PALA"'
            if indice == 2
            else '"ESPACIO: SALTO · SHIFT: DASH"'
        )

    dash_input = cond_or(
        cond("KeyFromTextJustPressed", ['"LShift"']),
        cond("KeyFromTextJustPressed", ['"RShift"']),
        cond("KeyFromTextJustPressed", ['"x"']),
        cond("KeyFromTextJustPressed", ['"X"']),
    )
    ataque_input = cond_or(
        cond("KeyFromTextJustPressed", ['"a"']),
        cond("KeyFromTextJustPressed", ['"A"']),
        cond("KeyFromTextJustPressed", ['"z"']),
        cond("KeyFromTextJustPressed", ['"Z"']),
        cond("KeyFromTextJustPressed", ['"c"']),
        cond("KeyFromTextJustPressed", ['"C"']),
        cond("KeyFromTextJustPressed", ['"j"']),
        cond("KeyFromTextJustPressed", ['"J"']),
    )
    pausa_input = cond_or(
        cond("KeyFromTextJustPressed", ['"Escape"']),
        cond("KeyFromTextJustPressed", ['"p"']),
        cond("KeyFromTextJustPressed", ['"P"']),
    )
    salto_justo = cond_or(
        cond("KeyFromTextJustPressed", ['"Space"']),
        cond("KeyFromTextJustPressed", ['"Up"']),
        cond("KeyFromTextJustPressed", ['"W"']),
        cond("KeyFromTextJustPressed", ['"w"']),
    )
    salto_presionado = cond_or(
        cond("KeyFromTextPressed", ['"Space"']),
        cond("KeyFromTextPressed", ['"Up"']),
        cond("KeyFromTextPressed", ['"W"']),
        cond("KeyFromTextPressed", ['"w"']),
    )
    salto_suelto = cond_or(
        cond("KeyFromTextReleased", ['"Space"']),
        cond("KeyFromTextReleased", ['"Up"']),
        cond("KeyFromTextReleased", ['"W"']),
        cond("KeyFromTextReleased", ['"w"']),
    )
    buffer_salto = cond("NumberObjectVariable", ["Jugador", "buffer_salto", ">", "0"])
    en_suelo_o_coyote = cond_or(
        cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
        cond("NumberObjectVariable", ["Jugador", "coyote", ">", "0"]),
    )

    eventos = [
        # Reinicio pedido desde el menú de pausa.
        evento(
            [cond("VarGlobal", ["reiniciar", "=", "1"])],
            [
                accion("ModVarGlobal", ["reiniciar", "=", "0"]),
                accion("Scene", ["CurrentSceneName()", "no"]),
            ],
        ),

        # La escena se dibuja a 1920x1080 con la cámara al doble de zoom.
        evento(
            [cond("SceneJustBegins", [""])],
            [
                accion(
                    "SetNumberObjectVariable",
                    ["Jugador", "tiene_pala", "=", "1" if pala_inicial else "0"],
                ),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                *(
                    [accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)])]
                    if (reiniciar_vidas or indice == 1)
                    else []
                ),
                *acciones_camara_inicial(objetivo_x, objetivo_y),
            ],
        ),

        # El portón arranca sellado en los niveles con jefe.
        *(
            [
                evento(
                    [cond("SceneJustBegins", [""])],
                    [accion("SetNumberVariable", ["jefe_derrotado", "=", "0"])],
                )
            ]
            if nivel.jefes
            else []
        ),

        # Pausa.
        evento(
            [pausa_input],
            [
                accion_sonido("UI"),
                accion("PushScene", ['"Pausa"']),
            ],
        ),

        # Dirección horizontal: flechas, A y D.
        evento(
            [
                cond_or(
                    cond("KeyFromTextPressed", ['"Left"']),
                    cond("KeyFromTextPressed", ['"a"']),
                    cond("KeyFromTextPressed", ['"A"']),
                )
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
                accion("PlatformBehavior::SimulateLeftKey", ["Jugador", "PlatformerObject"]),
            ],
        ),
        evento(
            [
                cond_or(
                    cond("KeyFromTextPressed", ['"Right"']),
                    cond("KeyFromTextPressed", ['"d"']),
                    cond("KeyFromTextPressed", ['"D"']),
                )
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dir", "=", "1"]),
                accion("PlatformBehavior::SimulateRightKey", ["Jugador", "PlatformerObject"]),
            ],
        ),

        # Salto con buffer y coyote time: ESPACIO, ↑ o W.
        evento(
            [salto_justo],
            [accion("SetNumberObjectVariable", ["Jugador", "buffer_salto", "=", "0.15"])],
        ),
        evento(
            [cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"])],
            [accion("SetNumberObjectVariable", ["Jugador", "coyote", "=", "0.18"])],
        ),
        evento(
            [cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True)],
            [accion("SetNumberObjectVariable", ["Jugador", "coyote", "-", "TimeDelta()"])],
        ),
        evento(
            [buffer_salto],
            [accion("SetNumberObjectVariable", ["Jugador", "buffer_salto", "-", "TimeDelta()"])],
        ),
        evento(
            [buffer_salto, en_suelo_o_coyote],
            [
                accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                accion_sonido("Salto"),
                accion("SetNumberObjectVariable", ["Jugador", "buffer_salto", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jugador", "coyote", "=", "0"]),
            ],
        ),
        evento(
            [
                salto_presionado,
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"]),
            ],
            [accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"])],
        ),

        # Corte de salto: si se suelta la tecla mientras el jugador sube, el
        # salto se aborta (equivalente al CORTE_SALTO de la versión pygame).
        evento(
            [
                salto_suelto,
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"]),
            ],
            [
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::AbortJump",
                    ["Jugador", "PlatformerObject"],
                ),
            ],
        ),

        # Ataque con pala: A.
        evento(
            [
                ataque_input,
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "ataque_cd", "<=", "0"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "atacando", "=", "1"]),
                accion_sonido("Pala"),
                accion("SetNumberObjectVariable", ["Jugador", "ataque_time", "=", "0.18"]),
                accion("SetNumberObjectVariable", ["Jugador", "ataque_cd", "=", "0.40"]),
            ],
            [
                evento(
                    [cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"])],
                    [
                        accion("ChangeAnimation", ["Jugador", "=", "2"]),
                        accion(
                            "Create",
                            ["GolpePala", "Jugador.X() + 24", "Jugador.Y() + 2", '""'],
                        ),
                    ],
                ),
                evento(
                    [cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"])],
                    [
                        accion("ChangeAnimation", ["Jugador", "=", "5"]),
                        accion(
                            "Create",
                            ["GolpePala", "Jugador.X() - 24", "Jugador.Y() + 2", '""'],
                        ),
                        accion("ChangeAnimation", ["GolpePala", "=", "3"]),
                    ],
                ),
            ],
        ),
        evento(
            [cond("NumberObjectVariable", ["Jugador", "atacando", "=", "1"])],
            [accion("SetNumberObjectVariable", ["Jugador", "ataque_time", "-", "TimeDelta()"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "ataque_time", "<=", "0.12"]),
                cond("NumberObjectVariable", ["Jugador", "ataque_time", ">", "0.06"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["GolpePala", "=", "1"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "ataque_time", "<=", "0.06"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["GolpePala", "=", "2"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "ataque_time", "<=", "0.12"]),
                cond("NumberObjectVariable", ["Jugador", "ataque_time", ">", "0.06"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["GolpePala", "=", "4"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "ataque_time", "<=", "0.06"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["GolpePala", "=", "5"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "ataque_time", "<=", "0"]),
            ],
            [accion("SetNumberObjectVariable", ["Jugador", "atacando", "=", "0"])],
        ),
        evento(
            [cond("NumberObjectVariable", ["Jugador", "ataque_cd", ">", "0"])],
            [accion("SetNumberObjectVariable", ["Jugador", "ataque_cd", "-", "TimeDelta()"])],
        ),

        # La pala golpea a los moradores.
        evento(
            [cond("CollisionNP", ["GolpePala", "Enemy", "no"])],
            [
                accion("Delete", ["Enemy"]),
                accion("Delete", ["GolpePala"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                *acciones_sacudida(5.0, 0.12),
            ],
        ),
        evento(
            [cond("CollisionNP", ["GolpePala", "EnemyMelee", "no"])],
            [
                accion("Delete", ["EnemyMelee"]),
                accion("Delete", ["GolpePala"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                *acciones_sacudida(5.0, 0.12),
            ],
        ),
        evento(
            [cond("NumberObjectVariable", ["GolpePala", "vida", ">", "0"])],
            [accion("SetNumberObjectVariable", ["GolpePala", "vida", "-", "TimeDelta()"])],
        ),
        evento(
            [cond("NumberObjectVariable", ["GolpePala", "vida", "<=", "0"])],
            [accion("Delete", ["GolpePala"])],
        ),

        # Animación: ataque, caída o idle; también cambia de lado.
        # Los índices 0-5 llevan pala y los índices 6-9 son las poses sin pala.
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "0"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "6"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "3"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "8"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "1"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "7"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "4"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "9"])],
        ),

        # Dash desde el suelo: Shift.
        evento(
            [
                dash_input,
                cond("NumberObjectVariable", ["Jugador", "dash_cd", "<=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                accion_sonido("Dash"),
                *acciones_sacudida(3.5, 0.10),
                accion("SetNumberObjectVariable", ["Jugador", "dash_time", "=", str(DASH_DURACION)]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0.60"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("PlatformBehavior::Gravity", ["Jugador", "PlatformerObject", "=", "0"]),
                accion(
                    "PlatformBehavior::MaxSpeed",
                    ["Jugador", "PlatformerObject", "=", str(DASH_VELOCIDAD)],
                ),
                accion(
                    "PlatformBehavior::MaxFallingSpeed",
                    ["Jugador", "PlatformerObject", "=", "0", "no"],
                ),
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed",
                    ["Jugador", "PlatformerObject", "=", "Jugador.Variable(dir) * " + str(DASH_VELOCIDAD)],
                ),
            ],
        ),

        # Dash aéreo: un uso hasta volver al suelo.
        evento(
            [
                dash_input,
                cond("NumberObjectVariable", ["Jugador", "dash_cd", "<=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "dash_aire", ">", "0"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                accion_sonido("Dash"),
                *acciones_sacudida(3.5, 0.10),
                accion("SetNumberObjectVariable", ["Jugador", "dash_time", "=", str(DASH_DURACION)]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0.60"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "0"]),
                accion("PlatformBehavior::Gravity", ["Jugador", "PlatformerObject", "=", "0"]),
                accion(
                    "PlatformBehavior::MaxSpeed",
                    ["Jugador", "PlatformerObject", "=", str(DASH_VELOCIDAD)],
                ),
                accion(
                    "PlatformBehavior::MaxFallingSpeed",
                    ["Jugador", "PlatformerObject", "=", "0", "no"],
                ),
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed",
                    ["Jugador", "PlatformerObject", "=", "Jugador.Variable(dir) * " + str(DASH_VELOCIDAD)],
                ),
            ],
        ),

        # Mientras dura el dash.
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dash_time", ">", "0"]),
            ],
            [
                accion("PlatformBehavior::Gravity", ["Jugador", "PlatformerObject", "=", "0"]),
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed",
                    ["Jugador", "PlatformerObject", "=", "Jugador.Variable(dir) * " + str(DASH_VELOCIDAD)],
                ),
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentFallSpeed",
                    ["Jugador", "PlatformerObject", "=", "0"],
                ),
                accion("SetNumberObjectVariable", ["Jugador", "dash_time", "-", "TimeDelta()"]),
            ],
        ),

        # Fin del dash: restaurar la física normal.
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dash_time", "<=", "0"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                accion(
                    "PlatformBehavior::Gravity",
                    ["Jugador", "PlatformerObject", "=", str(int(GRAVEDAD))],
                ),
                accion(
                    "PlatformBehavior::MaxSpeed",
                    ["Jugador", "PlatformerObject", "=", str(int(VELOCIDAD))],
                ),
                accion(
                    "PlatformBehavior::MaxFallingSpeed",
                    ["Jugador", "PlatformerObject", "=", str(int(MAX_CAIDA)), "no"],
                ),
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed",
                    ["Jugador", "PlatformerObject", "=", "0"],
                ),
            ],
        ),

        # Recarga del dash.
        evento([], [accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "-", "TimeDelta()"])]),
        evento(
            [cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"])],
            [accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"])],
        ),

        # Cámara: sigue al jugador con suavizado y sacudida, igual que camara.py.
        evento(
            [],
            [
                accion("SetNumberVariable", ["sacudida_t", "-", "TimeDelta()"]),
                accion(
                    "SetNumberVariable",
                    [
                        "cam_x",
                        "=",
                        f"cam_x + (min(max(Jugador.X() + {PLAYER_W // 2}, {centro_x}), {max_cam_x}) - cam_x)"
                        f" * min(1, {CAMARA_SUAVIZADO} * TimeDelta())",
                    ],
                ),
                accion(
                    "SetNumberVariable",
                    [
                        "cam_y",
                        "=",
                        f"cam_y + (min(max(Jugador.Y() + {PLAYER_H // 2}, {centro_y}), {max_cam_y}) - cam_y)"
                        f" * min(1, {CAMARA_SUAVIZADO} * TimeDelta())",
                    ],
                ),
                accion("SetCameraCenterX", ["=", f"cam_x + {SACUDIDA_EXPRESION_X}", '""', "0"]),
                accion("SetCameraCenterY", ["=", f"cam_y + {SACUDIDA_EXPRESION_Y}", '""', "0"]),
            ],
        ),

        # Patrulla de los moradores.
        evento(
            [
                cond("NumberObjectVariable", ["Enemy", "dir", "=", "1"]),
                cond("PosX", ["Enemy", ">=", "Enemy.Variable(max_x)"]),
            ],
            [accion("SetNumberObjectVariable", ["Enemy", "dir", "=", "-1"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Enemy", "dir", "=", "-1"]),
                cond("PosX", ["Enemy", "<=", "Enemy.Variable(min_x)"]),
            ],
            [accion("SetNumberObjectVariable", ["Enemy", "dir", "=", "1"])],
        ),
        evento(
            [],
            [
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed",
                    ["Enemy", "PlatformerObject", "=", "Enemy.Variable(dir) * " + str(int(VELOCIDAD_ENEMIGO))],
                )
            ],
        ),

        # Patrulla de los moradores melee.
        evento(
            [
                cond("NumberObjectVariable", ["EnemyMelee", "dir", "=", "1"]),
                cond("PosX", ["EnemyMelee", ">=", "EnemyMelee.Variable(max_x)"]),
            ],
            [accion("SetNumberObjectVariable", ["EnemyMelee", "dir", "=", "-1"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["EnemyMelee", "dir", "=", "-1"]),
                cond("PosX", ["EnemyMelee", "<=", "EnemyMelee.Variable(min_x)"]),
            ],
            [accion("SetNumberObjectVariable", ["EnemyMelee", "dir", "=", "1"])],
        ),
        evento(
            [],
            [
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed",
                    ["EnemyMelee", "PlatformerObject", "=", "EnemyMelee.Variable(dir) * " + str(int(VELOCIDAD_ENEMIGO))],
                )
            ],
        ),

        # Almas.
        evento(
            [cond("CollisionNP", ["Jugador", "Alma", "no"])],
            [
                accion("Delete", ["Alma"]),
                accion("SetNumberVariable", ["almas", "+", "1"]),
                accion("SetNumberVariable", ["almas_para_vida", "+", "1"]),
                accion_sonido("Alma"),
            ],
            [
                evento(
                    [cond("NumberVariable", ["almas_para_vida", ">=", str(ALMAS_POR_VIDA)])],
                    [accion("SetNumberVariable", ["almas_para_vida", "=", "0"])],
                    [
                        evento(
                            [cond("NumberVariable", ["vidas", "<", str(VIDAS_MAXIMAS)])],
                            [
                                accion("SetNumberVariable", ["vidas", "+", "1"]),
                                accion_sonido("Vida"),
                            ],
                        )
                    ],
                )
            ],
        ),

        # Pala recogible.
        evento(
            [cond("CollisionNP", ["Jugador", "PalaRecogible", "no"])],
            [
                accion("Delete", ["PalaRecogible"]),
                accion("SetNumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                accion_sonido("PalaRecoger"),
            ],
        ),

        # Power-up de rango (Guadaña).
        evento(
            [cond("CollisionNP", ["Jugador", "PowerUpRango", "no"])],
            [
                accion("Delete", ["PowerUpRango"]),
                accion("SetNumberObjectVariable", ["Jugador", "tiene_powerup", "=", "1"]),
                accion_sonido("PalaRecoger"),
                *acciones_sacudida(5.0, 0.15),
            ],
        ),

        # Pisotón: el jugador viene desde arriba (funciona siempre, incluso sin pala).
        evento(
            [
                cond("CollisionNP", ["Jugador", "Enemy", "no"]),
                cond("PosY", ["Jugador", "<", "Enemy.Y() - 10"]),
            ],
            [
                accion("Delete", ["Enemy"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                accion_sonido("Golpe"),
            ],
        ),
        evento(
            [
                cond("CollisionNP", ["Jugador", "EnemyMelee", "no"]),
                cond("PosY", ["Jugador", "<", "EnemyMelee.Y() - 10"]),
            ],
            [
                accion("Delete", ["EnemyMelee"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                accion_sonido("Golpe"),
            ],
        ),

        # Daño por enemigo: contacto lateral o sin pala.
        evento(
            [
                cond("CollisionNP", ["Jugador", "Enemy", "no"]),
                cond("PosY", ["Jugador", ">=", "Enemy.Y() - 10"]),
            ],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
            ],
            [
                evento(
                    [cond("NumberVariable", ["vidas", ">", "0"])],
                    [accion("Scene", ["CurrentSceneName()", "no"])],
                ),
                evento(
                    [cond("NumberVariable", ["vidas", "<=", "0"])],
                    [
                        accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                        accion("SetNumberVariable", ["almas", "=", "0"]),
                        accion("Scene", [f'"{destino_muerte}"', "no"]),
                    ],
                ),
            ],
        ),
        evento(
            [
                cond("CollisionNP", ["Jugador", "EnemyMelee", "no"]),
                cond("PosY", ["Jugador", ">=", "EnemyMelee.Y() - 10"]),
            ],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
            ],
            [
                evento(
                    [cond("NumberVariable", ["vidas", ">", "0"])],
                    [accion("Scene", ["CurrentSceneName()", "no"])],
                ),
                evento(
                    [cond("NumberVariable", ["vidas", "<=", "0"])],
                    [
                        accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                        accion("SetNumberVariable", ["almas", "=", "0"]),
                        accion("Scene", [f'"{destino_muerte}"', "no"]),
                    ],
                ),
            ],
        ),

        # Pinchos y caída al vacío.
        *eventos_dano(nivel.alto, destino_muerte=destino_muerte),

        # Portón. En niveles con jefe el portón está sellado hasta vencerlo.
        evento(
            (
                [cond("CollisionNP", ["Jugador", "Puerta", "no"])]
                + (
                    [cond("NumberVariable", ["jefe_derrotado", "=", "1"])]
                    if nivel.jefes
                    else []
                )
            ),
            [
                accion_sonido("Meta"),
                accion("SetNumberVariable", ["almas_totales", "+", "almas"]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("Scene", [f'"{siguiente}"', "no"]),
            ],
        ),

        # HUD.
        evento(
            [],
            [
                accion(
                    "TextObject::String",
                    [
                        "HUD_Almas",
                        "=",
                        '"ALMAS " + ToString(GlobalVariable(almas)) '
                        '+ " · VIDA +" + ToString(GlobalVariable(almas_para_vida)) + "/10"',
                    ],
                ),
                accion(
                    "TextObject::String",
                    [
                        "HUD_Vidas",
                        "=",
                        '"VIDAS " + ToString(GlobalVariable(vidas)) + "/5"',
                    ],
                ),
            ],
        ),
        evento(
            [cond("NumberVariable", ["vidas", "<=", "1"])],
            [
                accion(
                    "TextObject::String",
                    ["HUD_Aviso", "=", '"¡ÚLTIMA VIDA!"'],
                ),
            ],
        ),
        evento(
            [cond("NumberVariable", ["vidas", ">", "1"])],
            [accion("TextObject::String", ["HUD_Aviso", "=", '""'])],
        ),
        *(
            [
                evento(
                    [
                        cond("NumberVariable", ["jefe_derrotado", "=", "0"]),
                        cond("NumberVariable", ["vidas", ">", "1"]),
                    ],
                    [
                        accion(
                            "TextObject::String",
                            [
                                "HUD_Aviso",
                                "=",
                                '"CUSTODIO: " + ToString(Jefe.Variable(vida)) + "/6 HP"',
                            ],
                        ),
                    ],
                )
            ]
            if nivel.jefes
            else []
        ),
        evento(
            [cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"])],
            [
                accion(
                    "TextObject::String",
                    ["HUD_Dash", "=", '"ESPACIO: SALTO · SHIFT: DASH · A: PALA"'],
                ),
            ],
        ),
        evento(
            [cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"])],
            [
                accion(
                    "TextObject::String",
                    [
                        "HUD_Dash",
                        "=",
                        texto_dash_sin_pala,
                    ],
                ),
            ],
        ),
    ]
    if nivel.jefes:
        eventos.extend(eventos_jefe(siguiente))
    return eventos


# ------------------------------------------------------------
# Construcción de escenas
# ------------------------------------------------------------
def objetos_y_instancias_escena(escena_modelo: Escena) -> tuple[list[dict], list[dict]]:
    """Objetos e instancias de una escena, a partir del modelo del juego.

    Lo que depende del mapa (sólidos, entidades, portón, jugador) sale del
    modelo uniforme; el HUD se arma acá. No hay un caso por nivel.
    """
    nivel = escena_modelo.nivel
    spec = escena_modelo.spec
    objetos = [
        objeto_sprite("Fondo", spec.fondo),
        objeto_tiled("Solido", "TexturaSolido", TILE, TILE, [comportamiento_plataforma()]),
        objeto_jugador(),
        objeto_sprite("Puerta", "Puerta"),
        objeto_sprite("HUD_Barra", "BarraHUD"),
        objeto_sprite("HUD_BarraInferior", "BarraPista"),
        objeto_texto("HUD_Nivel", spec.titulo, 20, HUESO, "center"),
        objeto_texto("HUD_Almas", "ALMAS 0 · VIDA +0/10", 18, AMARILLO),
        objeto_texto("HUD_Vidas", "VIDAS 3/5", 18, ROJO),
        objeto_texto("HUD_Aviso", "", 12, ROJO),
        objeto_texto("HUD_Dash", spec.hud, 12, TURQUESA),
        objeto_texto("HUD_Pista", "\n".join(textwrap.wrap(spec.pista, width=84)), 15, CREMA, "center"),
        objeto_jefe(),
        objeto_onda(),
        objeto_onda_der(),
        objeto_golpe(),
    ]
    objetos.extend(objetos_entidades(escena_modelo))

    instancias = [
        instancia("Fondo", 0, 0, 0, tam=(nivel.ancho, nivel.alto)),
    ]
    for solido in nivel.solidos:
        instancias.append(
            instancia("Solido", solido.x, solido.y, 1, tam=(solido.width, solido.height))
        )
    instancias.append(
        instancia(
            "Puerta",
            nivel.meta.centerx - GATE_W // 2,
            nivel.meta.bottom - GATE_H,
            4,
            tam=(GATE_W, GATE_H),
        )
    )
    # El jugador aparece exactamente donde el juego lo pone.
    instancias.append(
        instancia("Jugador", nivel.spawn[0], nivel.spawn[1], 6, tam=(PLAYER_W, PLAYER_H))
    )
    instancias.extend(instancias_entidades(escena_modelo))
    instancias.extend(instancias_hud())
    return objetos, instancias


def instancias_hud() -> list[dict]:
    """Instancias del HUD (capa UI, tamaño de la vista del juego: 1280x720)."""
    return [
        instancia("HUD_Barra", 0, 0, 0, capa="UI", tam=(GAME_W, 52)),
        instancia("HUD_BarraInferior", 0, GAME_H - 58, 0, capa="UI", tam=(GAME_W, 58)),
        instancia("HUD_Nivel", 173, 12, 1, capa="UI", tam=(933, 40)),
        instancia("HUD_Almas", 24, 19, 1, capa="UI"),
        instancia("HUD_Vidas", GAME_W - 133, 19, 1, capa="UI"),
        instancia("HUD_Aviso", 827, 45, 1, capa="UI"),
        instancia("HUD_Dash", 24, 47, 1, capa="UI"),
        instancia("HUD_Pista", 27, GAME_H - 69, 1, capa="UI", tam=(1227, 61)),
    ]


def escena_titulo() -> dict:
    objetos = [objeto_sprite("FondoTitulo", "FondoTitulo")]
    instancias = [instancia("FondoTitulo", 0, 0, 0, tam=(GAME_W, GAME_H))]
    eventos = [
        evento(
            [cond("SceneJustBegins", [""])],
            [
                accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["almas_totales", "=", "0"]),
                *acciones_camara_inicial(),
            ],
        ),
        evento(
            [
                cond_or(
                    cond("KeyFromTextJustPressed", ['"Return"']),
                    cond("KeyFromTextJustPressed", ['"Space"']),
                    cond("MouseButtonReleased", ["Left"]),
                )
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Nivel 1"', "no"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ['"t"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Salas"', "no"]),
            ],
        ),
    ]
    return escena("Titulo", objetos, instancias, eventos)


def escena_victoria() -> dict:
    objetos = [
        objeto_sprite("FondoVictoria", "FondoVictoria"),
        objeto_texto("Victoria_Titulo", "¡ESCAPASTE DE LA CRIPTA!", 44, ORO, "center"),
        objeto_texto("Victoria_Stats", "ALMAS RECOLECTADAS: 0", 24, HUESO, "center"),
        objeto_texto("Victoria_Prompt", "ENTER PARA VOLVER AL TÍTULO", 19, TURQUESA, "center"),
    ]
    instancias = [
        instancia("FondoVictoria", 0, 0, 0, tam=(GAME_W, GAME_H)),
        instancia("Victoria_Titulo", 0, 118, 2, tam=(GAME_W, 60)),
        instancia("Victoria_Stats", 0, 254, 2, tam=(GAME_W, 40)),
        instancia("Victoria_Prompt", 0, GAME_H - 76, 2, tam=(GAME_W, 32)),
    ]
    eventos = [
        evento(
            [cond("SceneJustBegins", [""])],
            [
                *acciones_camara_inicial(),
                accion(
                    "TextObject::String",
                    ["Victoria_Stats", "=", '"ALMAS RECOLECTADAS: " + ToString(GlobalVariable(almas_totales))'],
                ),
            ],
        ),
        evento(
            [
                cond_or(
                    cond("KeyFromTextJustPressed", ['"Return"']),
                    cond("KeyFromTextJustPressed", ['"Space"']),
                    cond("MouseButtonReleased", ["Left"]),
                )
            ],
            [
                accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["almas_totales", "=", "0"]),
                accion_sonido("UI"),
                accion("Scene", ['"Titulo"', "no"]),
            ],
        ),
    ]
    return escena("Victoria", objetos, instancias, eventos)


def escena_pausa() -> dict:
    objetos = [
        objeto_sprite("FondoPausa", "FondoPausa"),
        objeto_texto("Pausa_Titulo", "PAUSA", 54, ORO, "center"),
        objeto_texto("Pausa_Sub", "LA CRIPTA ESPERA", 18, NIEBLA, "center"),
        objeto_texto("Pausa_Opcion1", "» CONTINUAR", 28, HUESO, "center"),
        objeto_texto("Pausa_Opcion2", "REINICIAR NIVEL", 28, HUESO, "center"),
        objeto_texto("Pausa_Opcion3", "VOLVER AL TÍTULO", 28, HUESO, "center"),
        objeto_texto("Pausa_Ayuda", "FLECHAS: ELEGIR · ENTER: CONFIRMAR · ESC: VOLVER", 14, NIEBLA, "center"),
    ]
    instancias = [
        instancia("FondoPausa", 0, 0, 0, tam=(GAME_W, GAME_H)),
        instancia("Pausa_Titulo", 0, 128, 2, "UI", tam=(GAME_W, 70)),
        instancia("Pausa_Sub", 0, 214, 2, "UI", tam=(GAME_W, 30)),
        instancia("Pausa_Opcion1", 0, 280, 3, "UI", tam=(GAME_W, 40)),
        instancia("Pausa_Opcion2", 0, 338, 3, "UI", tam=(GAME_W, 40)),
        instancia("Pausa_Opcion3", 0, 396, 3, "UI", tam=(GAME_W, 40)),
        instancia("Pausa_Ayuda", 0, 486, 3, "UI", tam=(GAME_W, 26)),
    ]
    opcion_1 = [
        accion("TextObject::String", ["Pausa_Opcion1", "=", '">> CONTINUAR <<"']),
        accion("TextObject::String", ["Pausa_Opcion2", "=", '"REINICIAR NIVEL"']),
        accion("TextObject::String", ["Pausa_Opcion3", "=", '"VOLVER AL TÍTULO"']),
    ]
    opcion_2 = [
        accion("TextObject::String", ["Pausa_Opcion1", "=", '"CONTINUAR"']),
        accion("TextObject::String", ["Pausa_Opcion2", "=", '">> REINICIAR NIVEL <<"']),
        accion("TextObject::String", ["Pausa_Opcion3", "=", '"VOLVER AL TÍTULO"']),
    ]
    opcion_3 = [
        accion("TextObject::String", ["Pausa_Opcion1", "=", '"CONTINUAR"']),
        accion("TextObject::String", ["Pausa_Opcion2", "=", '"REINICIAR NIVEL"']),
        accion("TextObject::String", ["Pausa_Opcion3", "=", '">> VOLVER AL TÍTULO <<"']),
    ]
    tecla_arriba = cond_or(
        cond("KeyFromTextJustPressed", ['"Up"']),
        cond("KeyFromTextJustPressed", ['"w"']),
    )
    tecla_abajo = cond_or(
        cond("KeyFromTextJustPressed", ['"Down"']),
        cond("KeyFromTextJustPressed", ['"s"']),
    )
    tecla_confirmar = cond_or(
        cond("KeyFromTextJustPressed", ['"Return"']),
        cond("KeyFromTextJustPressed", ['"Space"']),
    )
    eventos = [
        evento(
            [cond("SceneJustBegins", [""])],
            [
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
                *acciones_camara_inicial(),
            ],
        ),
        evento(
            [cond("NumberVariable", ["menu_opcion", "=", "1"])],
            opcion_1,
        ),
        evento(
            [cond("NumberVariable", ["menu_opcion", "=", "2"])],
            opcion_2,
        ),
        evento(
            [cond("NumberVariable", ["menu_opcion", "=", "3"])],
            opcion_3,
        ),
        evento(
            [
                tecla_arriba,
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "3"]),
            ],
        ),
        evento(
            [
                tecla_arriba,
                cond("NumberVariable", ["menu_opcion", ">", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "-", "1"]),
            ],
        ),
        evento(
            [
                tecla_abajo,
                cond("NumberVariable", ["menu_opcion", "=", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
            ],
        ),
        evento(
            [
                tecla_abajo,
                cond("NumberVariable", ["menu_opcion", "<", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "+", "1"]),
            ],
        ),
        evento(
            [
                tecla_confirmar,
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("PopScene", []),
            ],
        ),
        evento(
            [
                tecla_confirmar,
                cond("NumberVariable", ["menu_opcion", "=", "2"]),
            ],
            [
                accion_sonido("UI"),
                accion("ModVarGlobal", ["reiniciar", "=", "1"]),
                accion("PopScene", []),
            ],
        ),
        evento(
            [
                tecla_confirmar,
                cond("NumberVariable", ["menu_opcion", "=", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Titulo"', "yes"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ['"Escape"'])],
            [
                accion_sonido("UI"),
                accion("PopScene", []),
            ],
        ),
    ]
    pausa = escena("Pausa", objetos, instancias, eventos)
    pausa["variables"] = [{"name": "menu_opcion", "type": "number", "value": 1}]
    return pausa


def escena_salas() -> dict:
    objetos = [
        objeto_sprite("FondoSalas", "FondoPausa"),
        objeto_texto("Salas_Titulo", "SALAS DE PRUEBA", 46, ORO, "center"),
        objeto_texto("Salas_Sub", "MECÁNICAS AISLADAS PARA EVALUACIÓN", 17, NIEBLA, "center"),
        objeto_texto("Salas_Opcion1", "", 24, HUESO, "center"),
        objeto_texto("Salas_Opcion2", "", 24, HUESO, "center"),
        objeto_texto("Salas_Opcion3", "", 24, HUESO, "center"),
        objeto_texto("Salas_Desc1", "", 15, CREMA, "center"),
        objeto_texto("Salas_Desc2", "", 15, CREMA, "center"),
        objeto_texto(
            "Salas_Ayuda",
            "FLECHAS: ELEGIR · ENTER: ENTRAR · 1/2/3: DIRECTO · ESC: VOLVER",
            14,
            NIEBLA,
            "center",
        ),
    ]
    instancias = [
        instancia("FondoSalas", 0, 0, 0, tam=(GAME_W, GAME_H)),
        instancia("Salas_Titulo", 0, 74, 2, "UI", tam=(GAME_W, 60)),
        instancia("Salas_Sub", 0, 132, 2, "UI", tam=(GAME_W, 30)),
        instancia("Salas_Opcion1", 0, 214, 3, "UI", tam=(GAME_W, 40)),
        instancia("Salas_Opcion2", 0, 274, 3, "UI", tam=(GAME_W, 40)),
        instancia("Salas_Opcion3", 0, 334, 3, "UI", tam=(GAME_W, 40)),
        instancia("Salas_Desc1", 0, 404, 3, "UI", tam=(GAME_W, 24)),
        instancia("Salas_Desc2", 0, 428, 3, "UI", tam=(GAME_W, 24)),
        instancia("Salas_Ayuda", 0, 494, 3, "UI", tam=(GAME_W, 26)),
    ]
    opcion_1 = [
        accion("TextObject::String", ["Salas_Opcion1", "=", '">> 1 · SALA 1 · MOVIMIENTO <<"']),
        accion("TextObject::String", ["Salas_Opcion2", "=", '"2 · SALA 2 · PALA Y ATAQUE"']),
        accion("TextObject::String", ["Salas_Opcion3", "=", '"3 · SALA 3 · CUSTODIO"']),
        accion(
            "TextObject::String",
            [
                "Salas_Desc1",
                "=",
                '"MOVIMIENTO, SALTO Y DASH. SIN PALA: ESQUIVÁ PINCHOS Y MORADORES."',
            ],
        ),
        accion(
            "TextObject::String",
            ["Salas_Desc2", "=", '"EL SEGUNDO ABISMO PIDE SALTO + SHIFT."'],
        ),
    ]
    opcion_2 = [
        accion("TextObject::String", ["Salas_Opcion1", "=", '"1 · SALA 1 · MOVIMIENTO"']),
        accion("TextObject::String", ["Salas_Opcion2", "=", '">> 2 · SALA 2 · PALA Y ATAQUE <<"']),
        accion("TextObject::String", ["Salas_Opcion3", "=", '"3 · SALA 3 · CUSTODIO"']),
        accion(
            "TextObject::String",
            [
                "Salas_Desc1",
                "=",
                '"RECOGÉ LA PALA, ATACÁ CON A Y CRUZÁ LAS PLATAFORMAS."',
            ],
        ),
        accion(
            "TextObject::String",
            [
                "Salas_Desc2",
                "=",
                '"EL GOLPE RECARGA EL DASH AÉREO: PROBÁ DASH + A + DASH."',
            ],
        ),
    ]
    opcion_3 = [
        accion("TextObject::String", ["Salas_Opcion1", "=", '"1 · SALA 1 · MOVIMIENTO"']),
        accion("TextObject::String", ["Salas_Opcion2", "=", '"2 · SALA 2 · PALA Y ATAQUE"']),
        accion("TextObject::String", ["Salas_Opcion3", "=", '">> 3 · SALA 3 · CUSTODIO <<"']),
        accion(
            "TextObject::String",
            [
                "Salas_Desc1",
                "=",
                '"TENÉS LA PALA. SALTÁ LAS ONDAS DEL CUSTODIO Y GOLPEALO"',
            ],
        ),
        accion(
            "TextObject::String",
            [
                "Salas_Desc2",
                "=",
                '"CUANDO SE ARRODILLA. LA SALIDA SE ABRE AL VENCERLO."',
            ],
        ),
    ]
    arriba = cond_or(
        cond("KeyFromTextJustPressed", ['"Up"']),
        cond("KeyFromTextJustPressed", ['"w"']),
    )
    abajo = cond_or(
        cond("KeyFromTextJustPressed", ['"Down"']),
        cond("KeyFromTextJustPressed", ['"s"']),
    )
    volver = cond_or(
        cond("KeyFromTextJustPressed", ['"Escape"']),
        cond("KeyFromTextJustPressed", ['"t"']),
    )
    confirmar = cond_or(
        cond("KeyFromTextJustPressed", ['"Return"']),
        cond("KeyFromTextJustPressed", ['"Space"']),
    )
    eventos = [
        evento(
            [cond("SceneJustBegins", [""])],
            [
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
                *acciones_camara_inicial(),
            ],
        ),
        evento([cond("NumberVariable", ["menu_opcion", "=", "1"])], opcion_1),
        evento([cond("NumberVariable", ["menu_opcion", "=", "2"])], opcion_2),
        evento([cond("NumberVariable", ["menu_opcion", "=", "3"])], opcion_3),
        evento(
            [
                arriba,
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "3"]),
            ],
        ),
        evento(
            [
                arriba,
                cond("NumberVariable", ["menu_opcion", ">", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "-", "1"]),
            ],
        ),
        evento(
            [
                abajo,
                cond("NumberVariable", ["menu_opcion", "=", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
            ],
        ),
        evento(
            [
                abajo,
                cond("NumberVariable", ["menu_opcion", "<", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "+", "1"]),
            ],
        ),
        evento(
            [
                confirmar,
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Sala 1"', "no"]),
            ],
        ),
        evento(
            [
                confirmar,
                cond("NumberVariable", ["menu_opcion", "=", "2"]),
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Sala 2"', "no"]),
            ],
        ),
        evento(
            [
                confirmar,
                cond("NumberVariable", ["menu_opcion", "=", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Sala 3"', "no"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ['"1"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Sala 1"', "no"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ['"2"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Sala 2"', "no"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ['"3"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Sala 3"', "no"]),
            ],
        ),
        evento(
            [volver],
            [
                accion_sonido("UI"),
                accion("Scene", ['"Titulo"', "no"]),
            ],
        ),
    ]
    salas = escena("Salas", objetos, instancias, eventos)
    salas["variables"] = [{"name": "menu_opcion", "type": "number", "value": 1}]
    return salas

def escena_sala(escena_modelo: Escena) -> dict:
    """Sala de prueba: se construye igual que un nivel y vuelve al menú."""
    spec = escena_modelo.spec
    objetos, instancias = objetos_y_instancias_escena(escena_modelo)
    eventos = eventos_nivel(
        escena_modelo.nivel,
        1,
        1,
        siguiente=spec.siguiente,
        pala_inicial=spec.pala_inicial,
        texto_dash_sin_pala=f'"{spec.hud_sin_pala}"',
        destino_muerte=spec.destino_muerte,
        reiniciar_vidas=spec.reiniciar_vidas,
    )
    eventos.extend(reglas_escena(escena_modelo))
    return escena(spec.nombre, objetos, instancias, eventos)


# ------------------------------------------------------------
# Proyecto
# ------------------------------------------------------------
def construir_proyecto(escenas: list[Escena], prefijo_recursos: str = "assets") -> dict:
    base = json.loads(BASE_PROJECT.read_text(encoding="utf-8"))

    recursos = [
        recurso_imagen("FondoTitulo", f"{prefijo_recursos}/titulo.png"),
        recurso_imagen("FondoVictoria", f"{prefijo_recursos}/victoria.png"),
        recurso_imagen("FondoPausa", f"{prefijo_recursos}/pausa.png"),
        recurso_imagen("Jugador", f"{prefijo_recursos}/jugador.png"),
        recurso_imagen("JugadorCaida1", f"{prefijo_recursos}/jugador_caida_1.png"),
        recurso_imagen("JugadorCaida2", f"{prefijo_recursos}/jugador_caida_2.png"),
        recurso_imagen("JugadorAtaque1", f"{prefijo_recursos}/jugador_ataque_1.png"),
        recurso_imagen("JugadorAtaque2", f"{prefijo_recursos}/jugador_ataque_2.png"),
        recurso_imagen("JugadorAtaque3", f"{prefijo_recursos}/jugador_ataque_3.png"),
        recurso_imagen("JugadorIzq", f"{prefijo_recursos}/jugador_izq.png"),
        recurso_imagen("JugadorCaidaIzq1", f"{prefijo_recursos}/jugador_caida_izq_1.png"),
        recurso_imagen("JugadorCaidaIzq2", f"{prefijo_recursos}/jugador_caida_izq_2.png"),
        recurso_imagen("JugadorAtaqueIzq1", f"{prefijo_recursos}/jugador_ataque_izq_1.png"),
        recurso_imagen("JugadorAtaqueIzq2", f"{prefijo_recursos}/jugador_ataque_izq_2.png"),
        recurso_imagen("JugadorAtaqueIzq3", f"{prefijo_recursos}/jugador_ataque_izq_3.png"),
        recurso_imagen("JugadorSinPala", f"{prefijo_recursos}/jugador_sin_pala.png"),
        recurso_imagen("JugadorCaidaSinPala1", f"{prefijo_recursos}/jugador_caida_sin_pala_1.png"),
        recurso_imagen("JugadorCaidaSinPala2", f"{prefijo_recursos}/jugador_caida_sin_pala_2.png"),
        recurso_imagen("JugadorIzqSinPala", f"{prefijo_recursos}/jugador_izq_sin_pala.png"),
        recurso_imagen("JugadorCaidaIzqSinPala1", f"{prefijo_recursos}/jugador_caida_izq_sin_pala_1.png"),
        recurso_imagen("JugadorCaidaIzqSinPala2", f"{prefijo_recursos}/jugador_caida_izq_sin_pala_2.png"),
        recurso_imagen("Pala", f"{prefijo_recursos}/pala.png"),
        recurso_imagen("Puerta", f"{prefijo_recursos}/puerta.png"),
        recurso_imagen("Jefe", f"{prefijo_recursos}/jefe.png"),
        recurso_imagen("OndaJefe", f"{prefijo_recursos}/onda_jefe.png"),
        recurso_imagen("TexturaSolido", f"{prefijo_recursos}/solido.png"),
        recurso_imagen("BarraHUD", f"{prefijo_recursos}/barra_hud.png"),
        recurso_imagen("BarraPista", f"{prefijo_recursos}/barra_pista.png"),
        recurso_imagen("GolpeDer1", f"{prefijo_recursos}/golpe_der_1.png"),
        recurso_imagen("GolpeDer2", f"{prefijo_recursos}/golpe_der_2.png"),
        recurso_imagen("GolpeDer3", f"{prefijo_recursos}/golpe_der_3.png"),
        recurso_imagen("GolpeIzq1", f"{prefijo_recursos}/golpe_izq_1.png"),
        recurso_imagen("GolpeIzq2", f"{prefijo_recursos}/golpe_izq_2.png"),
        recurso_imagen("GolpeIzq3", f"{prefijo_recursos}/golpe_izq_3.png"),
        recurso_fuente(FONT_RESOURCE, f"{prefijo_recursos}/NotoSerifDisplay-Bold.ttf"),
        recurso_audio("SFX_Salto", f"{prefijo_recursos}/sfx_salto.wav"),
        recurso_audio("SFX_Alma", f"{prefijo_recursos}/sfx_alma.wav"),
        recurso_audio("SFX_Dash", f"{prefijo_recursos}/sfx_dash.wav"),
        recurso_audio("SFX_Pala", f"{prefijo_recursos}/sfx_pala.wav"),
        recurso_audio("SFX_PalaRecoger", f"{prefijo_recursos}/sfx_pala_recoger.wav"),
        recurso_audio("SFX_Golpe", f"{prefijo_recursos}/sfx_golpe.wav"),
        recurso_audio("SFX_Dano", f"{prefijo_recursos}/sfx_dano.wav"),
        recurso_audio("SFX_Meta", f"{prefijo_recursos}/sfx_meta.wav"),
        recurso_audio("SFX_Vida", f"{prefijo_recursos}/sfx_vida.wav"),
        recurso_audio("SFX_UI", f"{prefijo_recursos}/sfx_ui.wav"),
    ]
    ya_en_recursos = {r["name"] for r in recursos}
    for escena_modelo in escenas:
        for entidad in escena_modelo.entidades:
            adapt = adaptador(entidad.kind)
            if adapt.en_fondo:
                continue
            nombre = nombre_textura(adapt, entidad)
            if nombre in ya_en_recursos:
                continue
            ya_en_recursos.add(nombre)
            recursos.append(recurso_imagen(nombre, f"{prefijo_recursos}/{nombre.lower()}.png"))
    for escena_modelo in escenas:
        recursos.append(
            recurso_imagen(
                escena_modelo.spec.fondo,
                f"{prefijo_recursos}/fondo_{escena_modelo.spec.clave}.png",
            )
        )

    base["properties"].update(
        {
            "name": "IN CRYPTA - Nativo",
            "description": "Proyecto GDevelop nativo generado desde el Pygame de IN CRYPTA.",
            "author": "Equipo 6",
            "packageName": "com.equipo6.incrypta",
            "windowWidth": RENDER_W,
            "windowHeight": RENDER_H,
            "sizeOnStartupMode": "adaptWidth",
            "orientation": "landscape",
            "scaleMode": "linear",
            "pixelsRounding": True,
            "adaptGameResolutionAtRuntime": False,
            "projectUuid": uid(),
            "version": "1.0.0",
        }
    )
    base["properties"].pop("latestCompilationDirectory", None)
    base["properties"].setdefault("loadingScreen", {}).update(
        {
            "backgroundImageResourceName": "FondoTitulo",
            "backgroundColor": 0,
            "showGDevelopSplash": True,
            "minDuration": 0.8,
        }
    )
    base["properties"].setdefault("watermark", {}).update(
        {
            "placement": "bottom-left",
            "showWatermark": False,
        }
    )
    base["firstLayout"] = "Titulo"
    base["resources"] = {"resources": recursos}
    base["objects"] = []
    base["objectsGroups"] = []
    base["variables"] = [
        {"name": "vidas", "type": "number", "value": VIDAS_INICIALES},
        {"name": "almas", "type": "number", "value": 0},
        {"name": "almas_totales", "type": "number", "value": 0},
        {"name": "almas_para_vida", "type": "number", "value": 0},
        {"name": "reiniciar", "type": "number", "value": 0},
        {"name": "jefe_derrotado", "type": "number", "value": 0},
        {"name": "cam_x", "type": "number", "value": GAME_W // 2},
        {"name": "cam_y", "type": "number", "value": GAME_H // 2},
        {"name": "sacudida_f", "type": "number", "value": 0},
        {"name": "sacudida_t", "type": "number", "value": 0},
    ]
    base["layouts"] = [escena_titulo(), escena_pausa(), escena_victoria(), escena_salas()]
    total_campana = sum(1 for e in escenas if not e.spec.es_sala)
    indice = 0
    for escena_modelo in escenas:
        spec = escena_modelo.spec
        if spec.es_sala:
            base["layouts"].append(escena_sala(escena_modelo))
            continue
        indice += 1
        objetos, instancias = objetos_y_instancias_escena(escena_modelo)
        eventos = eventos_nivel(
            escena_modelo.nivel,
            indice,
            total_campana,
            siguiente=spec.siguiente,
            pala_inicial=spec.pala_inicial,
            texto_dash_sin_pala=f'"{spec.hud_sin_pala}"',
            destino_muerte=spec.destino_muerte,
            reiniciar_vidas=spec.reiniciar_vidas,
        )
        eventos.extend(reglas_escena(escena_modelo))
        base["layouts"].append(escena(spec.nombre, objetos, instancias, eventos))
    base["usedResources"] = [
        {"name": "SFX_Salto"},
        {"name": "SFX_Alma"},
        {"name": "SFX_Dash"},
        {"name": "SFX_Pala"},
        {"name": "SFX_PalaRecoger"},
        {"name": "SFX_Golpe"},
        {"name": "SFX_Dano"},
        {"name": "SFX_Meta"},
        {"name": "SFX_Vida"},
        {"name": "SFX_UI"},
    ]
    base["externalEvents"] = []
    base["externalLayouts"] = []
    return base


def limpiar_assets(proyecto: dict, directorio_assets: Path | None = None) -> list[str]:
    """Borra los archivos de assets que el proyecto ya no referencia.

    Sin esto se acumulan texturas y sonidos viejos (los que el generador
    cambió de nombre o dejó de generar) que confunden al abrir el proyecto.
    """
    directorio = directorio_assets or ASSETS
    usados = {
        Path(recurso.get("file", "")).name
        for recurso in proyecto["resources"]["resources"]
        if recurso.get("file")
    }
    borrados = []
    if directorio.exists():
        for archivo in sorted(directorio.iterdir()):
            if archivo.is_file() and archivo.name not in usados:
                archivo.unlink()
                borrados.append(archivo.name)
    return borrados


def main() -> int:
    pygame.init()
    OUT.mkdir(parents=True, exist_ok=True)
    specs = escenas_campaña() + escenas_salas()
    escenas = [leer_escena(spec) for spec in specs]

    generar_assets(escenas)
    proyecto = construir_proyecto(escenas)
    borrados = limpiar_assets(proyecto)
    destino = OUT / PROJECT_NAME
    destino.write_text(json.dumps(proyecto, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Proyecto: {destino}")
    print(f"Resolución: {RENDER_W}x{RENDER_H} (zoom {GAME_ZOOM})")
    print(f"Escenas: {[l['name'] for l in proyecto['layouts']]}")
    print(
        "Datos: "
        + ", ".join(
            f"{e.spec.nombre} {e.ancho}x{e.alto} ({len(e.solidos)} sólidos, "
            f"{len(e.de_kind('alma'))} almas, {len(e.de_kind('enemigo'))} enemigos, "
            f"{len(e.de_kind('peligro'))} peligros)"
            for e in escenas
        )
    )
    print(f"Recursos: {len(proyecto['resources']['resources'])}")
    if borrados:
        print(f"Assets obsoletos borrados: {len(borrados)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
