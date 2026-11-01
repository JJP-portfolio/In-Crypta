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
    ATAQUE_COOLDOWN,
    ATAQUE_DURACION,
    CAMARA_SUAVIZADO,
    CAMARA_ZOOM,
    ALTO,
    AMARILLO,
    ANCHO,
    CREMA,
    APEX_GRAVEDAD_FACTOR,
    APEX_VY_UMBRAL,
    CORTE_SALTO,
    COYOTE_TIME,
    DASH_COOLDOWN,
    DASH_DURACION,
    DASH_JUMP_IMPULSO_X,
    DASH_VELOCIDAD,
    GRAVEDAD,
    HUESO,
    JEFE_ALTO,
    JEFE_ANCHO,
    JEFE_ONDA_VELOCIDAD,
    JUMP_BUFFER,
    MAX_CAIDA,
    MINIJEFE_TIMER_EMBESTIDA,
    NIEBLA,
    ORO,
    POST_DASH_DURACION,
    POST_DASH_GRAVEDAD_FACTOR,
    REBOTE_ENEMIGO,
    ROJO,
    SACUDIDA_DURACION,
    SALTO,
    SANGRE,
    TURQUESA,
    VELOCIDAD,
    VELOCIDAD_ENEMIGO,
    VIDAS_INICIALES,
    VIDAS_MAXIMAS,
    VIRTUAL_ALTO,
    VIRTUAL_ANCHO,
)
from entidades import Alma, Custodio, Enemigo, Jugador, OndaCustodio, PalaRecogible
from exportador import sprites as sprites_export
from exportador.adaptadores import ADAPTADORES, adaptador, variables_instancia
from exportador.manifiesto import escena_tutorial, escenas_campaña, escenas_salas
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
FONT_SOURCE = Path("/usr/share/fonts/noto/NotoSerifDisplay-Bold.ttf")
FONT_RESOURCE = "FuenteHUD"
FONT_FILE = "assets/NotoSerifDisplay-Bold.ttf"

GAME_W = ANCHO
GAME_H = ALTO
RENDER_W = ANCHO
RENDER_H = ALTO
# Con resolución 1280x720 y zoom 1.25, el área visible del mundo es exactamente
# 1024x576 (VIRTUAL_ANCHO x VIRTUAL_ALTO), igual que en Pygame.
GAME_ZOOM = CAMARA_ZOOM

# Sacudida de cámara: la intensidad cae linealmente durante la duración
# (camara.py::Camara.actualizar_sacudida) y el offset es aleatorio.
# Respeta la opción de accesibilidad F1 (reducir_movimiento = 1 suprime sacudida).
_INTENSIDAD = f"(1 - GlobalVariable(reducir_movimiento)) * (sacudida_f * max(0, sacudida_t) / {SACUDIDA_DURACION})"
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
            halo = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.circle(halo, (255, 175, 55, 28), (22, 22), 18)
            pygame.draw.circle(halo, (255, 205, 95, 50), (22, 22), 9)
            surface.blit(halo, (x - 22, 290 - 22), special_flags=pygame.BLEND_RGBA_ADD)
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

    # Un portón lejano, como cierre visual con halo suave.
    x = GAME_W // 2
    halo_v = pygame.Surface((130, 130), pygame.SRCALPHA)
    pygame.draw.circle(halo_v, (255, 195, 75, 28), (65, 65), 60)
    pygame.draw.circle(halo_v, (255, 220, 110, 48), (65, 65), 35)
    surface.blit(halo_v, (x - 65, 316 - 65), special_flags=pygame.BLEND_RGBA_ADD)
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
def guardar_2x(surface: pygame.Surface, nombre: str) -> None:
    destino = pygame.transform.smoothscale(
        surface,
        (surface.get_width() * ASSET_SCALE, surface.get_height() * ASSET_SCALE),
    )
    pygame.image.save(destino, ASSETS / nombre)


def _jugador_pose(
    nombre: str,
    pose: str | None,
    direccion: int = 1,
    con_pala: bool = True,
) -> None:
    surface = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
    jugador = Jugador(4, 1)
    jugador.direccion = direccion
    jugador.en_suelo = pose is None
    jugador.vx = VELOCIDAD if pose is None else 0
    jugador.tiempo_animacion = 0.35
    jugador.dibujar(surface, CamaraCompleta(), 0.0, pose=pose, con_pala=con_pala)
    guardar_2x(surface, nombre)


def guardar_jugador() -> None:
    _jugador_pose("jugador.png", None)
    _jugador_pose("jugador_caida_1.png", "caida")
    _jugador_pose("jugador_caida_2.png", "caida2")
    _jugador_pose("jugador_ataque_1.png", "ataque1", con_pala=False)
    _jugador_pose("jugador_ataque_2.png", "ataque2", con_pala=False)
    _jugador_pose("jugador_ataque_3.png", "ataque3", con_pala=False)
    _jugador_pose("jugador_izq.png", None, -1)
    _jugador_pose("jugador_caida_izq_1.png", "caida", -1)
    _jugador_pose("jugador_caida_izq_2.png", "caida2", -1)
    _jugador_pose("jugador_ataque_izq_1.png", "ataque1", -1, con_pala=False)
    _jugador_pose("jugador_ataque_izq_2.png", "ataque2", -1, con_pala=False)
    _jugador_pose("jugador_ataque_izq_3.png", "ataque3", -1, con_pala=False)
    _jugador_pose("jugador_sin_pala.png", None, con_pala=False)
    _jugador_pose("jugador_caida_sin_pala_1.png", "caida", con_pala=False)
    _jugador_pose("jugador_caida_sin_pala_2.png", "caida2", con_pala=False)
    _jugador_pose("jugador_izq_sin_pala.png", None, -1, con_pala=False)
    _jugador_pose("jugador_caida_izq_sin_pala_1.png", "caida", -1, con_pala=False)
    _jugador_pose("jugador_caida_izq_sin_pala_2.png", "caida2", -1, con_pala=False)


def guardar_puerta() -> None:
    surface = pygame.Surface((GATE_W, GATE_H), pygame.SRCALPHA)
    dummy = object.__new__(Nivel)
    dummy.meta = pygame.Rect(11, GATE_H - 30, 20, 30)
    dummy.dibujar_meta(surface, CamaraCompleta())
    guardar_2x(surface, "puerta.png")


def guardar_solido() -> None:
    # La textura del sólido debe ser opaca: GDevelop calcula la máscara de
    # colisión del comportamiento Platform a partir del alfa de la textura.
    # Si queda casi transparente (alfa 1), la máscara se pierde y el jugador
    # atraviesa el suelo ("cosas pisadas" / colisiones rotas).
    surface = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surface.fill((68, 62, 70, 255))
    pygame.image.save(surface, ASSETS / "solido.png")


def guardar_golpe() -> None:
    for viejo in ("golpe.png", "golpe_izq.png"):
        (ASSETS / viejo).unlink(missing_ok=True)

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

        pygame.image.save(surface, ASSETS / f"golpe_der_{indice}.png")
        pygame.image.save(
            pygame.transform.flip(surface, True, False),
            ASSETS / f"golpe_izq_{indice}.png",
        )

def guardar_jefe() -> None:
    surface = pygame.Surface((JEFE_ANCHO, JEFE_ALTO), pygame.SRCALPHA)
    jefe = Custodio(pygame.Rect(0, 0, JEFE_ANCHO, JEFE_ALTO), -1000, 1000)
    jefe.dibujar(surface, CamaraCompleta(), 0.0)
    guardar_2x(surface, "jefe.png")


def guardar_onda() -> None:
    surface = pygame.Surface((ONDA_W, ONDA_H), pygame.SRCALPHA)
    onda = OndaCustodio(ONDA_W // 2, ONDA_H, 1, 0)
    onda.dibujar(surface, CamaraCompleta(), 0.0)
    guardar_2x(surface, "onda_jefe.png")


def _wav_muestras(freq_inicio, freq_fin, duracion, volumen, tipo="sine", ruido=0.0):
    tasa = 22050
    total = max(1, int(tasa * duracion))
    fase = 0.0
    muestras = []
    for i in range(total):
        t = i / tasa
        frecuencia = freq_inicio + (freq_fin - freq_inicio) * (t / duracion)
        fase += 2 * math.pi * frecuencia / tasa
        if tipo == "square":
            onda = 1.0 if math.sin(fase) >= 0 else -1.0
        elif tipo == "saw":
            onda = 2.0 * ((fase / (2 * math.pi)) % 1.0) - 1.0
        elif tipo == "bell":
            onda = math.sin(fase) + 0.28 * math.sin(fase * 2) + 0.12 * math.sin(fase * 3)
        else:
            onda = math.sin(fase)
        if ruido:
            onda = onda * (1.0 - ruido) + random.uniform(-1.0, 1.0) * ruido
        ataque = min(1.0, t / 0.012)
        caida = max(0.0, 1.0 - (t / duracion) ** 1.6)
        muestras.append(int(32767 * volumen * ataque * caida * onda))
    return muestras


def _guardar_wav(nombre: str, muestras: list[int]) -> None:
    with wave.open(str(ASSETS / nombre), "wb") as archivo:
        archivo.setnchannels(1)
        archivo.setsampwidth(2)
        archivo.setframerate(22050)
        archivo.writeframes(b"".join(struct.pack("<h", muestra) for muestra in muestras))


def guardar_audio() -> None:
    _guardar_wav("sfx_salto.wav", _wav_muestras(340, 620, 0.14, 0.24))
    _guardar_wav("sfx_alma.wav", _wav_muestras(700, 980, 0.20, 0.22, "bell"))
    _guardar_wav("sfx_dash.wav", _wav_muestras(150, 70, 0.12, 0.20, "saw", 0.10))
    _guardar_wav("sfx_pala.wav", _wav_muestras(820, 220, 0.13, 0.18, "saw", 0.18))
    _guardar_wav("sfx_pala_recoger.wav", _wav_muestras(620, 800, 0.18, 0.18, "bell"))
    _guardar_wav("sfx_golpe.wav", _wav_muestras(130, 55, 0.16, 0.24, "square"))
    _guardar_wav("sfx_dano.wav", _wav_muestras(240, 70, 0.28, 0.22, "saw", 0.08))
    _guardar_wav("sfx_ui.wav", _wav_muestras(520, 380, 0.06, 0.14, "square"))

    vida = []
    for frecuencia, duracion in ((659, 0.10), (784, 0.10), (1046, 0.24)):
        vida.extend(_wav_muestras(frecuencia, frecuencia * 1.01, duracion, 0.20, "bell"))
    _guardar_wav("sfx_vida.wav", vida)

    meta = []
    for frecuencia, duracion in ((392, 0.10), (523, 0.12), (659, 0.14), (784, 0.30)):
        meta.extend(_wav_muestras(frecuencia, frecuencia * 1.01, duracion, 0.20, "bell"))
    _guardar_wav("sfx_meta.wav", meta)

    # --- Nuevos sonidos (paridad con audio.py commit 020b19c) ---
    # Pisotón: golpe percusivo grave con ruido
    _guardar_wav("sfx_stomp.wav", _wav_muestras(80, 30, 0.18, 0.28, "square", 0.30))
    # Muerte/derrota: barrido descendente disonante
    muerte = []
    for frecuencia, duracion in ((340, 0.10), (240, 0.10), (160, 0.12), (90, 0.26)):
        muerte.extend(_wav_muestras(frecuencia, frecuencia * 0.7, duracion, 0.28, "saw", 0.06))
    _guardar_wav("sfx_muerte.wav", muerte)
    # Combo de almas: 6 tonos ascendentes (cada recolección consecutiva sube un semitono)
    # Frecuencias: Do5 → Re5 → Mi5 → Sol5 → La5 → Do6 (escala pentatónica)
    _COMBO_FREQS = [523, 587, 659, 784, 880, 1046]
    for i, freq in enumerate(_COMBO_FREQS, start=1):
        _guardar_wav(
            f"sfx_alma_{i}.wav",
            _wav_muestras(freq, freq * 1.02, 0.18 + i * 0.01, 0.22, "bell"),
        )


def guardar_barras() -> None:
    barra = pygame.Surface((GAME_W, 52), pygame.SRCALPHA)
    barra.fill((5, 5, 9, 205))
    pygame.draw.line(barra, (*ORO, 255), (0, 51), (GAME_W, 51), 1)
    guardar_2x(barra, "barra_hud.png")

    pista = pygame.Surface((GAME_W, 58), pygame.SRCALPHA)
    pista.fill((5, 5, 9, 215))
    pygame.draw.line(pista, (*ORO, 255), (0, 0), (GAME_W, 0), 1)
    guardar_2x(pista, "barra_pista.png")


def generar_fondo_pausa() -> pygame.Surface:
    surface = pygame.Surface((GAME_W, GAME_H))
    _gradiente(surface, (5, 5, 9), (22, 16, 25))
    _estrellas(surface, 707, 70, (54, 42, 62), 0.65)
    pygame.draw.rect(surface, (8, 7, 12), (210, 88, 540, 364))
    pygame.draw.rect(surface, ORO, (210, 88, 540, 364), 2)
    pygame.draw.line(surface, SANGRE, (290, 200), (670, 200), 1)
    pygame.draw.line(surface, SANGRE, (290, 444), (670, 444), 1)
    return surface


def generar_fondo_derrota() -> pygame.Surface:
    surface = pygame.Surface((GAME_W, GAME_H))
    _gradiente(surface, (10, 4, 6), (28, 10, 14))
    _estrellas(surface, 666, 60, (70, 20, 25), 0.65)
    pw, ph = 680, 440
    px = (GAME_W - pw) // 2
    py = (GAME_H - ph) // 2
    pygame.draw.rect(surface, (18, 10, 14), (px, py, pw, ph), border_radius=14)
    pygame.draw.rect(surface, (160, 40, 50), (px, py, pw, ph), 2, border_radius=14)
    pygame.draw.line(surface, ORO, (px + 20, py + 1), (px + pw - 20, py + 1), 1)
    pygame.draw.line(surface, ORO, (px + 20, py + ph - 1), (px + pw - 20, py + ph - 1), 1)
    return surface


def guardar_fondo_titulo() -> None:
    """Genera un fondo limpio gótico de alta resolución para el Menú Principal."""
    surf = pygame.Surface((RENDER_W, RENDER_H))
    from juego import Juego
    j = Juego()
    j.dibujar_fondo(surf)
    j.dibujar_arbol_muerto(surf, 90, RENDER_H - 54, 1.5)
    j.dibujar_arbol_muerto(surf, 1100, RENDER_H - 40, 1.1)
    j.dibujar_tumba_lejana(surf, 950, RENDER_H - 54, 1.3)
    j.dibujar_tumba_lejana(surf, 1020, RENDER_H - 44, 0.9)
    surf.blit(j.vineta, (0, 0))
    velo = pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)
    velo.fill((5, 4, 10, 165))
    surf.blit(velo, (0, 0))
    pygame.image.save(surf, ASSETS / "titulo.png")


def generar_assets(escenas: list[Escena]) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    guardar_fondo_titulo()
    shutil.copy2(FONT_SOURCE, ASSETS / FONT_SOURCE.name)

    guardar_jugador()
    guardar_puerta()
    guardar_solido()
    guardar_golpe()
    guardar_jefe()
    guardar_onda()
    guardar_audio()
    guardar_barras()

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
            sprites_export.guardar(entidad.kind, ancho, alto, ASSETS / f"{nombre.lower()}.png")

    # Las texturas de los tipos que siempre existen, aunque ningún mapa los
    # tenga, para que el objeto quede con su recurso y no con uno roto.
    for kind in KINDS_SIEMPRE:
        adapt = adaptador(kind)
        ancho, alto = adapt.sprite or (32, 32)
        sprites_export.guardar(kind, ancho, alto, ASSETS / f"{adapt.textura.lower()}.png")

    for escena_modelo in escenas:
        pygame.image.save(
            generar_fondo_nivel(escena_modelo.nivel),
            ASSETS / f"fondo_{escena_modelo.spec.clave}.png",
        )
    guardar_2x(generar_fondo_victoria(), "victoria.png")
    guardar_2x(generar_fondo_pausa(), "pausa.png")
    guardar_2x(generar_fondo_derrota(), "derrota.png")

    # Assets Pixel-Art góticos y animaciones multipose (Prioridad 5)
    import integrar_assets_gdevelop
    integrar_assets_gdevelop.generar_todos_los_assets()


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


def subeventos_reintento(destino_muerte: str = "Derrota") -> list[dict]:
    return [
        evento(
            [
                cond("NumberVariable", ["vidas", ">", "0"]),
                cond("NumberVariable", ["checkpoint_activo", "=", "1"]),
            ],
            [
                accion("SetX", ["Jugador", "=", "GlobalVariable(checkpoint_x)"]),
                accion("SetY", ["Jugador", "=", "GlobalVariable(checkpoint_y)"]),
                accion("PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed", ["Jugador", "PlatformerObject", "=", "0"]),
                accion("PlatformBehavior::PlatformerObjectBehavior::SetCurrentFallSpeed", ["Jugador", "PlatformerObject", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_time", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                accion("TextObject::String", ["HUD_Aviso", "=", '"¡REGRESO AL FAROL DE REPOSO!"']),
            ],
        ),
        evento(
            [
                cond("NumberVariable", ["vidas", ">", "0"]),
                cond("NumberVariable", ["checkpoint_activo", "=", "0"]),
            ],
            [
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["combo_almas", "=", "0"]),
                accion("SetNumberVariable", ["combo_timer", "=", "0"]),
                accion("SetNumberVariable", ["rango_mejorado", "=", "0"]),
                accion("Scene", ["CurrentSceneName()", "no"]),
            ],
        ),
        evento(
            [cond("NumberVariable", ["vidas", "<=", "0"])],
            [
                accion("SetNumberVariable", ["muertes_totales", "+", "1"]),
                accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["almas_totales", "=", "0"]),
                accion("SetNumberVariable", ["combo_almas", "=", "0"]),
                accion("SetNumberVariable", ["combo_timer", "=", "0"]),
                accion("SetNumberVariable", ["rango_mejorado", "=", "0"]),
                accion("SetNumberVariable", ["checkpoint_activo", "=", "0"]),
                accion_sonido("Muerte"),
                accion("Scene", [f'"{destino_muerte}"', "no"]),
            ],
        ),
    ]


def eventos_dano(alto: int, destino_muerte: str = "Derrota", tiene_pinchos: bool = True) -> list[dict]:
    subeventos = subeventos_reintento(destino_muerte)
    evs = []
    if tiene_pinchos:
        evs.append(
            evento(
                [cond("CollisionNP", ["Jugador", "Pinchos", "no"])],
                [],
                [
                    evento(
                        [cond("VarGlobal", ["escudo_farol", "=", "1"])],
                        [
                            accion("ModVarGlobal", ["escudo_farol", "=", "0"]),
                            accion_sonido("UI"),
                            *acciones_sacudida(5.0, 0.15),
                            accion("TextObject::String", ["HUD_Aviso", "=", '"¡MANTO DEL FAROL ABSORBIÓ EL IMPACTO!"']),
                        ],
                    ),
                    evento(
                        [cond("VarGlobal", ["escudo_farol", "=", "0"])],
                        [
                            accion("SetNumberVariable", ["vidas", "-", "1"]),
                            accion_sonido("Dano"),
                            *acciones_sacudida(9.0, 0.22),
                        ],
                        subeventos,
                    ),
                ],
            )
        )
    evs.append(
        evento(
            [cond("PosY", ["Jugador", ">", str(alto + 120)])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                *acciones_sacudida(9.0, 0.22),
            ],
            subeventos,
        )
    )
    return evs


PISTAS_NATIVAS = {
    1: "FLECHAS: MOVERTE. ARRIBA: SALTAR. SHIFT: DASH. CRUZA EL PRIMER HUECO CON LA PLATAFORMA. LAS ALMAS DEL SALTO DE 3 BLOQUES MARCAN EL SALTO + DASH. EL POZO DE 7 NECESITA SHIFT EN EL AIRE. EN EL GRAN ABISMO SUBI EL ESCALON Y LA CORNISA, Y DASHEA DESDE ARRIBA.",
    2: "PRIMER ABISMO: SALTA Y USA SHIFT EN EL AIRE. LA PALA ESTA EN LA CORNISA. CRUZA EL HUECO GRANDE CON LA PLATAFORMA Y SUS ALMAS. EL ASCENSOR VERTICAL TE SUBE AL MURO. 10 ALMAS = 1 VIDA EXTRA.",
    3: "EL CUSTODIO TE PERSIGUE. ATACA SOLO CUANDO BRILLA EN ROJO. BUSCA LAS ALMAS Y ABRE EL PORTON.",
}


def acciones_camara_inicial(centro_x: int | str | None = None, centro_y: int | str | None = None) -> list[dict]:
    if centro_x is None:
        centro_x = VIRTUAL_ANCHO // 2
    if centro_y is None:
        centro_y = VIRTUAL_ALTO // 2
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
            [cond("PosX", ["OndaIzq", "<", "0"])],
            [accion("Delete", ["OndaIzq"])],
        ),
        evento(
            [cond("PosX", ["OndaDer", ">", str(GAME_W)])],
            [accion("Delete", ["OndaDer"])],
        ),

        # --- Ondas dañan al jugador ---
        evento(
            [cond("CollisionNP", ["Jugador", "OndaIzq", "no"])],
            [],
            [
                evento(
                    [cond("VarGlobal", ["escudo_farol", "=", "1"])],
                    [
                        accion("ModVarGlobal", ["escudo_farol", "=", "0"]),
                        accion("Delete", ["OndaIzq"]),
                        accion_sonido("UI"),
                        *acciones_sacudida(5.0, 0.15),
                        accion("TextObject::String", ["HUD_Aviso", "=", '"¡MANTO DEL FAROL ABSORBIÓ EL IMPACTO!"']),
                    ],
                ),
                evento(
                    [cond("VarGlobal", ["escudo_farol", "=", "0"])],
                    [
                        accion("SetNumberVariable", ["vidas", "-", "1"]),
                        accion_sonido("Dano"),
                        accion("Delete", ["OndaIzq"]),
                        accion("Scene", ["CurrentSceneName()", "no"]),
                    ],
                ),
            ],
        ),
        evento(
            [cond("CollisionNP", ["Jugador", "OndaDer", "no"])],
            [],
            [
                evento(
                    [cond("VarGlobal", ["escudo_farol", "=", "1"])],
                    [
                        accion("ModVarGlobal", ["escudo_farol", "=", "0"]),
                        accion("Delete", ["OndaDer"]),
                        accion_sonido("UI"),
                        *acciones_sacudida(5.0, 0.15),
                        accion("TextObject::String", ["HUD_Aviso", "=", '"¡MANTO DEL FAROL ABSORBIÓ EL IMPACTO!"']),
                    ],
                ),
                evento(
                    [cond("VarGlobal", ["escudo_farol", "=", "0"])],
                    [
                        accion("SetNumberVariable", ["vidas", "-", "1"]),
                        accion_sonido("Dano"),
                        accion("Delete", ["OndaDer"]),
                        accion("Scene", ["CurrentSceneName()", "no"]),
                    ],
                ),
            ],
        ),

        # --- Contacto con jefe (daño si NO es vulnerable) ---
        evento(
            [
                cond("CollisionNP", ["Jugador", "Jefe", "no"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
            ],
            [],
            [
                evento(
                    [cond("VarGlobal", ["escudo_farol", "=", "1"])],
                    [
                        accion("ModVarGlobal", ["escudo_farol", "=", "0"]),
                        accion_sonido("UI"),
                        *acciones_sacudida(5.0, 0.15),
                        accion("TextObject::String", ["HUD_Aviso", "=", '"¡MANTO DEL FAROL ABSORBIÓ EL IMPACTO!"']),
                    ],
                ),
                evento(
                    [cond("VarGlobal", ["escudo_farol", "=", "0"])],
                    [
                        accion("SetNumberVariable", ["vidas", "-", "1"]),
                        accion_sonido("Dano"),
                        accion("Scene", ["CurrentSceneName()", "no"]),
                    ],
                ),
            ],
        ),

        # --- Golpe al jefe en Fase 1 (vulnerable) ---
        evento(
            [
                cond("CollisionNP", ["GolpePala", "Jefe", "no"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "1"]),
                cond("NumberObjectVariable", ["Jefe", "fase", "<", "2"]),
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

        # --- Golpe al jefe en Fase 2 (requiere Guadaña X) ---
        evento(
            [
                cond("CollisionNP", ["GolpePala", "Jefe", "no"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "1"]),
                cond("NumberObjectVariable", ["Jefe", "fase", ">=", "2"]),
                cond("NumberVariable", ["rango_mejorado", "=", "1"]),
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

        # --- Golpe rebotado en Fase 2 sin Guadaña X ---
        evento(
            [
                cond("CollisionNP", ["GolpePala", "Jefe", "no"]),
                cond("NumberObjectVariable", ["Jefe", "fase", ">=", "2"]),
                cond("NumberVariable", ["rango_mejorado", "=", "0"]),
            ],
            [
                accion_sonido("Golpe"),
                accion("Delete", ["GolpePala"]),
                *acciones_sacudida(4.0, 0.12),
                accion("TextObject::String", ["HUD_Aviso", "=", '"¡CORAZA CARMESÍ! Necesitas la Guadaña (X)"']),
            ],
        ),

        # --- FlipX horizontal del Jefe según dirección ---
        evento(
            [cond("NumberObjectVariable", ["Jefe", "dir", "=", "-1"])],
            [accion("FlipX", ["Jefe", "yes"])],
        ),
        evento(
            [cond("NumberObjectVariable", ["Jefe", "dir", "=", "1"])],
            [accion("FlipX", ["Jefe", "no"])],
        ),

        # --- Pisotón al jefe en Fase 1 ---
        evento(
            [
                cond("CollisionNP", ["Jugador", "Jefe", "no"]),
                cond("PosY", ["Jugador", "<", "Jefe.Y() - 10"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "1"]),
                cond("NumberObjectVariable", ["Jefe", "fase", "<", "2"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "vida", "-", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "2.0"]),
                accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", str(int(REBOTE_ENEMIGO))]),
                accion("PlatformBehavior::SetCanJump", ["Jugador", "PlatformerObject"]),
                accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                accion_sonido("Stomp"),
                *acciones_sacudida(6.0, 0.18),
            ],
        ),

        # --- Pisotón al jefe en Fase 2 (requiere Guadaña X) ---
        evento(
            [
                cond("CollisionNP", ["Jugador", "Jefe", "no"]),
                cond("PosY", ["Jugador", "<", "Jefe.Y() - 10"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "1"]),
                cond("NumberObjectVariable", ["Jefe", "fase", ">=", "2"]),
                cond("NumberVariable", ["rango_mejorado", "=", "1"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "vida", "-", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "2.0"]),
                accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", str(int(REBOTE_ENEMIGO))]),
                accion("PlatformBehavior::SetCanJump", ["Jugador", "PlatformerObject"]),
                accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                accion_sonido("Stomp"),
                *acciones_sacudida(6.0, 0.18),
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
    destino_muerte: str = "Derrota",
    reiniciar_vidas: bool = False,
    nombres_objetos: set[str] | None = None,
)     -> list[dict]:
    if nombres_objetos is None:
        nombres_objetos = {"Jugador", "Enemy", "Alma", "Pinchos", "Puerta", "GolpePala"}
    # La cámara se controla por su centro. Si el nivel es más grande que el
    # viewport visible (1024x576 con GAME_ZOOM=1.25), el centro sigue al
    # jugador entre los bordes; si es más chico, queda centrado.
    if nivel.ancho >= VIRTUAL_ANCHO:
        centro_x = VIRTUAL_ANCHO // 2
        max_cam_x = nivel.ancho - VIRTUAL_ANCHO // 2
    else:
        centro_x = max_cam_x = nivel.ancho // 2
    if nivel.alto >= VIRTUAL_ALTO:
        centro_y = VIRTUAL_ALTO // 2
        max_cam_y = nivel.alto - VIRTUAL_ALTO // 2
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
        cond("KeyFromTextJustPressed", ['"j"']),
        cond("KeyFromTextJustPressed", ['"J"']),
        cond("KeyFromTextJustPressed", ['"z"']),
        cond("KeyFromTextJustPressed", ['"Z"']),
        cond("KeyFromTextJustPressed", ['"k"']),
        cond("KeyFromTextJustPressed", ['"K"']),
        cond("KeyFromTextJustPressed", ['"c"']),
        cond("KeyFromTextJustPressed", ['"C"']),
        cond("MouseButtonPressed", ['"Left"']),
    )
    pausa_input = cond_or(
        cond("KeyFromTextJustPressed", ['"Escape"']),
        cond("KeyFromTextJustPressed", ['"p"']),
        cond("KeyFromTextJustPressed", ['"P"']),
    )
    salto_justo = cond_or(
        cond("KeyFromTextJustPressed", ['"Space"']),
        cond("KeyFromTextJustPressed", ['"Up"']),
        cond("KeyFromTextJustPressed", ['"w"']),
        cond("KeyFromTextJustPressed", ['"W"']),
        cond("KeyFromTextJustPressed", ['"z"']),
        cond("KeyFromTextJustPressed", ['"Z"']),
    )
    salto_presionado = cond_or(
        cond("KeyFromTextPressed", ['"Space"']),
        cond("KeyFromTextPressed", ['"Up"']),
        cond("KeyFromTextPressed", ['"w"']),
        cond("KeyFromTextPressed", ['"W"']),
        cond("KeyFromTextPressed", ['"z"']),
        cond("KeyFromTextPressed", ['"Z"']),
    )
    buffer_salto = cond("NumberObjectVariable", ["Jugador", "buffer_salto", ">", "0"])
    en_suelo_o_coyote = cond_or(
        cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
        cond("NumberObjectVariable", ["Jugador", "coyote", ">", "0"]),
    )

    # Corte de salto variable 1:1 con Pygame: si el jugador suelta el botón en pleno salto,
    # abortar el impulso ascendente inmediatamente.
    evento(
        [
            cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"]),
            cond("KeyFromTextPressed", ['"Space"'], invertida=True),
            cond("KeyFromTextPressed", ['"Up"'], invertida=True),
            cond("KeyFromTextPressed", ['"w"'], invertida=True),
            cond("KeyFromTextPressed", ['"W"'], invertida=True),
            cond("KeyFromTextPressed", ['"z"'], invertida=True),
            cond("KeyFromTextPressed", ['"Z"'], invertida=True),
        ],
        [accion("PlatformBehavior::PlatformerObjectBehavior::AbortJump", ["Jugador", "PlatformerObject"])],
    ),
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
                accion("SetNumberVariable", ["nivel_actual", "=", str(indice)]),
                accion(
                    "SetNumberObjectVariable",
                    ["Jugador", "tiene_pala", "=", "1" if pala_inicial else "0"],
                ),
                accion(
                    "SetNumberObjectVariable",
                    ["Jugador", "tiene_dash", "=", "1" if (indice >= 2) else "0"],
                ),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["combo_almas", "=", "0"]),
                accion("SetNumberVariable", ["combo_timer", "=", "0"]),
                accion("SetNumberVariable", ["rango_mejorado", "=", "0"]),
                *(
                    [accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)])]
                    if reiniciar_vidas
                    else []
                ),
                *acciones_camara_inicial(objetivo_x, objetivo_y),
            ],
        ),

        # Al iniciar la escena: reubicar en checkpoint si está activo en esta escena
        evento(
            [
                cond("SceneJustBegins", [""]),
                cond("NumberVariable", ["checkpoint_activo", "=", "1"]),
                cond("StringVariable", ["checkpoint_escena", "=", "CurrentSceneName()"]),
            ],
            [
                accion("SetX", ["Jugador", "=", "GlobalVariable(checkpoint_x)"]),
                accion("SetY", ["Jugador", "=", "GlobalVariable(checkpoint_y)"]),
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

        # Accesibilidad F1: alternar reducir_movimiento (paridad con juego.py commit 020b19c).
        evento(
            [cond("KeyFromTextJustPressed", ['"F1"'])],
            [
                accion(
                    "SetNumberVariable",
                    ["reducir_movimiento", "=", "1 - GlobalVariable(reducir_movimiento)"],
                ),
                accion_sonido("UI"),
            ],
        ),

        # Pausa.
        evento(
            [pausa_input],
            [
                accion_sonido("UI"),
                accion("PushScene", ['"Pausa"']),
            ],
        ),

        # Dirección horizontal: Controles duales (Flechas + WASD).
        # Bloqueado durante el dash para no competir con la velocidad de impulso.
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond_or(
                    cond("KeyFromTextPressed", ['"Left"']),
                    cond("KeyFromTextPressed", ['"a"']),
                    cond("KeyFromTextPressed", ['"A"']),
                ),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
                accion("PlatformBehavior::SimulateLeftKey", ["Jugador", "PlatformerObject"]),
            ],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond_or(
                    cond("KeyFromTextPressed", ['"Right"']),
                    cond("KeyFromTextPressed", ['"d"']),
                    cond("KeyFromTextPressed", ['"D"']),
                ),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dir", "=", "1"]),
                accion("PlatformBehavior::SimulateRightKey", ["Jugador", "PlatformerObject"]),
            ],
        ),

        # Salto con buffer y coyote time: ESPACIO, ↑, W o Z.
        evento(
            [salto_justo],
            [accion("SetNumberObjectVariable", ["Jugador", "buffer_salto", "=", str(JUMP_BUFFER)])],
        ),
        evento(
            [cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"])],
            [
                accion("SetNumberObjectVariable", ["Jugador", "coyote", "=", str(COYOTE_TIME)]),
                accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", str(int(-SALTO))]),
            ],
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
                accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", str(int(-SALTO))]),
                accion("PlatformBehavior::SetCanJump", ["Jugador", "PlatformerObject"]),
                accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                accion_sonido("Salto"),
                accion("SetNumberObjectVariable", ["Jugador", "buffer_salto", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jugador", "coyote", "=", "0"]),
            ],
        ),

        # Corte de salto variable 1:1 con Pygame: si el jugador suelta el botón en pleno salto,
        # abortar el impulso ascendente inmediatamente.
        evento(
            [
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"]),
                cond("KeyFromTextPressed", ['"Space"'], invertida=True),
                cond("KeyFromTextPressed", ['"Up"'], invertida=True),
                cond("KeyFromTextPressed", ['"w"'], invertida=True),
                cond("KeyFromTextPressed", ['"W"'], invertida=True),
                cond("KeyFromTextPressed", ['"z"'], invertida=True),
                cond("KeyFromTextPressed", ['"Z"'], invertida=True),
            ],
            [accion("PlatformBehavior::PlatformerObjectBehavior::AbortJump", ["Jugador", "PlatformerObject"])],
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
                accion("SetNumberObjectVariable", ["Jugador", "ataque_time", "=", str(ATAQUE_DURACION)]),
                accion("SetNumberObjectVariable", ["Jugador", "ataque_cd", "=", str(ATAQUE_COOLDOWN)]),
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

        # La pala golpea a los moradores y enemigos vulnerables.
        *[
            evento(
                [cond("CollisionNP", ["GolpePala", enemigo_tipo, "no"])],
                [
                    accion("Delete", [enemigo_tipo]),
                    accion("Delete", ["GolpePala"]),
                    accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                    accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                    accion_sonido("Golpe"),
                    *acciones_sacudida(5.0, 0.12),
                ],
            )
            for enemigo_tipo in ("Enemy", "EnemyMelee", "Polilla", "Arana")
            if enemigo_tipo in nombres_objetos
        ],
        evento(
            [cond("NumberObjectVariable", ["GolpePala", "vida", ">", "0"])],
            [accion("SetNumberObjectVariable", ["GolpePala", "vida", "-", "TimeDelta()"])],
        ),
        evento(
            [cond("NumberObjectVariable", ["GolpePala", "vida", "<=", "0"])],
            [accion("Delete", ["GolpePala"])],
        ),

        # Animación de Jugador (16 animaciones completas multipose):
        # 14/15: Dash, 2/5: Ataque, 12/13: Salto, 1/4/7/9: Caída, 10/11: Run, 0/3/6/8: Idle.
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "14"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "15"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "2"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "5"])],
        ),
        # Aire: Salto (ascenso)
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "12"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "13"])],
        ),
        # Aire: Caída (descenso con pala o sin pala)
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "1"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "7"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "4"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True),
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "9"])],
        ),
        # Suelo: Corriendo (Run)
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle", ["Jugador", "PlatformerObject"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "10"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle", ["Jugador", "PlatformerObject"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "11"])],
        ),
        # Suelo: Quieto (Idle)
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "0"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "6"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "3"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "atacando", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
                cond("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle", ["Jugador", "PlatformerObject"], invertida=True),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
            ],
            [accion("ChangeAnimation", ["Jugador", "=", "8"])],
        ),

        # Dash-Jump: Salto impulsado desde el dash en el suelo
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                en_suelo_o_coyote,
                cond_or(salto_justo, buffer_salto),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jugador", "post_dash", "=", str(POST_DASH_DURACION)]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_time", "=", "0"]),
                accion("PlatformBehavior::MaxSpeed", ["Jugador", "PlatformerObject", "=", str(int(VELOCIDAD * DASH_JUMP_IMPULSO_X))]),
                accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", str(int(-SALTO))]),
                accion("PlatformBehavior::SetCanJump", ["Jugador", "PlatformerObject"]),
                accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                accion("PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed", ["Jugador", "PlatformerObject", "=", "Jugador.Variable(dir) * " + str(int(VELOCIDAD * DASH_JUMP_IMPULSO_X))]),
                accion("SetNumberObjectVariable", ["Jugador", "buffer_salto", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jugador", "coyote", "=", "0"]),
                accion_sonido("Salto"),
            ],
        ),

        # Dash desde el suelo: Shift o X.
        evento(
            [
                dash_input,
                cond("NumberObjectVariable", ["Jugador", "tiene_dash", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dash_cd", "<=", "0"]),
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                accion_sonido("Dash"),
                *acciones_sacudida(3.5, 0.10),
                accion("SetNumberObjectVariable", ["Jugador", "dash_time", "=", str(DASH_DURACION)]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", str(DASH_COOLDOWN)]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
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
                cond("NumberObjectVariable", ["Jugador", "tiene_dash", "=", "1"]),
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
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", str(DASH_COOLDOWN)]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "0"]),
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

        # Fin del dash: restaurar la física normal conservando el impulso horizontal (250 px/s)
        evento(
            [
                cond("NumberObjectVariable", ["Jugador", "dashing", "=", "1"]),
                cond("NumberObjectVariable", ["Jugador", "dash_time", "<=", "0"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dashing", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jugador", "post_dash", "=", str(POST_DASH_DURACION)]),
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
                    ["Jugador", "PlatformerObject", "=", "Jugador.Variable(dir) * " + str(int(VELOCIDAD))],
                ),
            ],
        evento(
            [cond("NumberObjectVariable", ["Jugador", "post_dash", ">", "0"])],
            [accion("SetNumberObjectVariable", ["Jugador", "post_dash", "-", "TimeDelta()"])]),
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

        # Almas con sistema de combo (paridad audio.py commit 020b19c).
        # ventana_combo = 1.3 s; combo_almas se incrementa por cada alma
        # consecutiva y selecciona sfx_alma_N (N de 1 a 6 toneado por semitono).
        # Si pasa 1.3 s sin recoger otra alma, combo_almas se resetea a 0.
        evento(
            [cond("CollisionNP", ["Jugador", "Alma", "no"])],
            [
                accion("Delete", ["Alma"]),
                accion("SetNumberVariable", ["almas", "+", "1"]),
                accion("SetNumberVariable", ["almas_para_vida", "+", "1"]),
                # Avanzar combo (capped en 6)
                accion("SetNumberVariable", ["combo_almas", "+", "1"]),
                accion("SetNumberVariable", ["combo_timer", "=", "1.3"]),
            ],
            [
                # Capear combo en 6
                evento(
                    [cond("NumberVariable", ["combo_almas", ">", "6"])],
                    [accion("SetNumberVariable", ["combo_almas", "=", "6"])],
                ),
                # Reproducir el tono del combo (alma_1 … alma_6)
                *[
                    evento(
                        [cond("NumberVariable", ["combo_almas", "=", str(n)])],
                        [accion_sonido(f"Alma{n}")],
                    )
                    for n in range(1, 7)
                ],
                # Vida extra si se acumularon ALMAS_POR_VIDA
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
                ),
            ],
        ),
        # Temporizador de combo: resetear combo_almas si pasa 1.3 s sin alma.
        evento(
            [cond("NumberVariable", ["combo_timer", ">", "0"])],
            [accion("SetNumberVariable", ["combo_timer", "-", "TimeDelta()"])],
            [
                evento(
                    [cond("NumberVariable", ["combo_timer", "<=", "0"])],
                    [accion("SetNumberVariable", ["combo_almas", "=", "0"])],
                )
            ],
        ),

        # Pala recogible.
        *([
            evento(
                [cond("CollisionNP", ["Jugador", "PalaRecogible", "no"])],
                [
                    accion("Delete", ["PalaRecogible"]),
                    accion("SetNumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                    accion_sonido("PalaRecoger"),
                ],
            )
        ] if "PalaRecogible" in nombres_objetos else []),

        # Power-up de rango de ataque (paridad con Pygame 'X').
        # Si el MiniJefe (Carcelero) está vivo en la escena, el altar está sellado.
        *([
            evento(
                [
                    cond("CollisionNP", ["Jugador", "PowerUpRango", "no"]),
                    cond("SceneInstancesCount", ["MiniJefe", ">", "0"]),
                ],
                [
                    accion("TextObject::String", ["HUD_Aviso", "=", '"¡ALTAR SELLADO! Derrota al Carcelero"']),
                ],
            ),
            evento(
                [
                    cond("CollisionNP", ["Jugador", "PowerUpRango", "no"]),
                    cond("SceneInstancesCount", ["MiniJefe", "<=", "0"]),
                ],
                [
                    accion("Delete", ["PowerUpRango"]),
                    accion("SetNumberVariable", ["rango_mejorado", "=", "1"]),
                    accion_sonido("Meta"),
                    *acciones_sacudida(4.0, 0.12),
                    accion("TextObject::String", ["HUD_Aviso", "=", '"¡ALCANCE DE PALA MEJORADO!"']),
                ],
            ),
        ] if "PowerUpRango" in nombres_objetos and "MiniJefe" in nombres_objetos else [
            evento(
                [cond("CollisionNP", ["Jugador", "PowerUpRango", "no"])],
                [
                    accion("Delete", ["PowerUpRango"]),
                    accion("SetNumberVariable", ["rango_mejorado", "=", "1"]),
                    accion_sonido("Meta"),
                    *acciones_sacudida(4.0, 0.12),
                    accion("TextObject::String", ["HUD_Aviso", "=", '"¡ALCANCE DE PALA MEJORADO!"']),
                ],
            ),
        ] if "PowerUpRango" in nombres_objetos else []),

        # Power-up de dash espectral (paridad con Pygame 'D').
        *([
            evento(
                [cond("CollisionNP", ["Jugador", "PowerUpDash", "no"])],
                [
                    accion("Delete", ["PowerUpDash"]),
                    accion("SetNumberObjectVariable", ["Jugador", "tiene_dash", "=", "1"]),
                    accion_sonido("Dash"),
                    *acciones_sacudida(4.0, 0.12),
                    accion("TextObject::String", ["HUD_Aviso", "=", '"¡AMULETO DE SOMBRAS: DASH EN EL AIRE!"']),
                ],
            )
        ] if "PowerUpDash" in nombres_objetos else []),

        # Checkpoint diegético (paridad con Pygame 'F').
        *([
            evento(
                [
                    cond("CollisionNP", ["Jugador", "FarolCheckpoint", "no"]),
                    cond("NumberObjectVariable", ["FarolCheckpoint", "activo", "=", "0"]),
                ],
                [
                    accion("SetNumberObjectVariable", ["FarolCheckpoint", "activo", "=", "1"]),
                    accion("ChangeAnimation", ["FarolCheckpoint", "=", "1"]),
                    accion("SetNumberVariable", ["checkpoint_activo", "=", "1"]),
                    accion("SetNumberVariable", ["checkpoint_x", "=", "FarolCheckpoint.X()"]),
                    accion("SetNumberVariable", ["checkpoint_y", "=", "FarolCheckpoint.Y()"]),
                    accion("SetStringVariable", ["checkpoint_escena", "=", "CurrentSceneName()"]),
                    accion_sonido("Alma"),
                    accion("TextObject::String", ["HUD_Aviso", "=", '"¡PUNTO DE CONTROL ALCANZADO!"']),
                ],
                [
                    evento(
                        [cond("VarGlobal", ["vidas", "<", "3"])],
                        [accion("ModVarGlobal", ["vidas", "+", "1"])],
                    ),
                    evento(
                        [cond("VarGlobal", ["almas", ">=", "GlobalVariable(almas_consagradas) + 5"])],
                        [
                            accion("ModVarGlobal", ["escudo_farol", "=", "1"]),
                            accion("TextObject::String", ["HUD_Aviso", "=", '"¡MANTO DEL FAROL OBTENIDO (+ESCUDO)!"']),
                        ],
                    ),
                    evento(
                        [],
                        [accion("ModVarGlobal", ["almas_consagradas", "=", "GlobalVariable(almas)"])],
                    ),
                ],
            )
        ] if "FarolCheckpoint" in nombres_objetos else []),

        # Pisotón: el jugador viene desde arriba y ya tiene la pala.
        # Paridad audio.py: reproduce sfx_stomp + rebote exacto (360 px/s) + sacudida 6/0.18.
        *[
            evento(
                [
                    cond("CollisionNP", ["Jugador", enemigo_tipo, "no"]),
                    cond("PosY", ["Jugador", "<", f"{enemigo_tipo}.Y() - 10"]),
                    cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                ],
                [
                    accion("Delete", [enemigo_tipo]),
                    accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", str(int(REBOTE_ENEMIGO))]),
                    accion("PlatformBehavior::SetCanJump", ["Jugador", "PlatformerObject"]),
                    accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                    accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                    accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                    accion_sonido("Stomp"),
                    *acciones_sacudida(6.0, 0.18),
                ],
            )
            for enemigo_tipo in ("Enemy", "EnemyMelee", "Polilla", "Arana")
            if enemigo_tipo in nombres_objetos
        ],

        # Ciclo de Inteligencia Artificial de 4 Estados para MiniJefe (El Carcelero)
        *([
            # Temporizador de MiniJefe
            evento(
                [cond("NumberObjectVariable", ["MiniJefe", "timer", ">", "0"])],
                [accion("SetNumberObjectVariable", ["MiniJefe", "timer", "-", "TimeDelta()"])],
            ),
            # Estado 0: Patrulla (1.2 s a 70 px/s)
            evento(
                [
                    cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "0"]),
                    cond("NumberObjectVariable", ["MiniJefe", "dir", "=", "1"]),
                    cond("PosX", ["MiniJefe", ">=", "MiniJefe.Variable(max_x)"]),
                ],
                [accion("SetNumberObjectVariable", ["MiniJefe", "dir", "=", "-1"])],
            ),
            evento(
                [
                    cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "0"]),
                    cond("NumberObjectVariable", ["MiniJefe", "dir", "=", "-1"]),
                    cond("PosX", ["MiniJefe", "<=", "MiniJefe.Variable(min_x)"]),
                ],
                [accion("SetNumberObjectVariable", ["MiniJefe", "dir", "=", "1"])],
            ),
            evento(
                [cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "0"])],
                [
                    accion(
                        "SetX",
                        ["MiniJefe", "=", "MiniJefe.X() + MiniJefe.Variable(dir) * 70 * TimeDelta()"],
                    ),
                ],
            ),
            evento(
                [
                    cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "0"]),
                    cond("NumberObjectVariable", ["MiniJefe", "timer", "<=", "0"]),
                ],
                [
                    accion("SetNumberObjectVariable", ["MiniJefe", "estado", "=", "1"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "timer", "=", "0.55"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "vulnerable", "=", "0"]),
                ],
            ),
            # Estado 1: Telegrafía (0.55 s quieto apuntando al jugador)
            evento(
                [
                    cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "1"]),
                    cond("PosX", ["Jugador", ">", "MiniJefe.X()"]),
                ],
                [accion("SetNumberObjectVariable", ["MiniJefe", "dir", "=", "1"])],
            ),
            evento(
                [
                    cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "1"]),
                    cond("PosX", ["Jugador", "<=", "MiniJefe.X()"]),
                ],
                [accion("SetNumberObjectVariable", ["MiniJefe", "dir", "=", "-1"])],
            ),
            evento(
                [
                    cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "1"]),
                    cond("NumberObjectVariable", ["MiniJefe", "timer", "<=", "0"]),
                ],
                [
                    accion("SetNumberObjectVariable", ["MiniJefe", "estado", "=", "2"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "timer", "=", str(MINIJEFE_TIMER_EMBESTIDA)]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "vulnerable", "=", "0"]),
                ],
            ),
            # Estado 2: Embestida (0.40 s a 220 px/s)
            evento(
                [cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "2"])],
                [
                    accion(
                        "SetX",
                        ["MiniJefe", "=", "MiniJefe.X() + MiniJefe.Variable(dir) * 220 * TimeDelta()"],
                    ),
                ],
            ),
            evento(
                [
                    cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "2"]),
                    cond("NumberObjectVariable", ["MiniJefe", "timer", "<=", "0"]),
                ],
                [
                    accion("SetNumberObjectVariable", ["MiniJefe", "estado", "=", "3"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "timer", "=", "1.30"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "vulnerable", "=", "1"]),
                    accion("TextObject::String", ["HUD_Aviso", "=", '"¡EL CARCELERO ESTÁ CANSADO! ¡ATACA AHORA!"']),
                ],
            ),
            # Estado 3: Cansado / Vulnerable (1.30 s de ventana de castigo)
            evento(
                [
                    cond("NumberObjectVariable", ["MiniJefe", "estado", "=", "3"]),
                    cond("NumberObjectVariable", ["MiniJefe", "timer", "<=", "0"]),
                ],
                [
                    accion("SetNumberObjectVariable", ["MiniJefe", "estado", "=", "0"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "timer", "=", "1.20"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "vulnerable", "=", "0"]),
                ],
            ),
            # Pisotón sobre MiniJefe cuando es vulnerable
            evento(
                [
                    cond("CollisionNP", ["Jugador", "MiniJefe", "no"]),
                    cond("PosY", ["Jugador", "<", "MiniJefe.Y() - 10"]),
                    cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                    cond("NumberObjectVariable", ["MiniJefe", "vulnerable", "=", "1"]),
                ],
                [
                    accion("SetNumberObjectVariable", ["MiniJefe", "vida", "-", "1"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "vulnerable", "=", "0"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "estado", "=", "0"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "timer", "=", "0.50"]),
                    accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", str(int(REBOTE_ENEMIGO))]),
                    accion("PlatformBehavior::SetCanJump", ["Jugador", "PlatformerObject"]),
                    accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                    accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                    accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                    accion_sonido("Stomp"),
                    *acciones_sacudida(6.0, 0.18),
                ],
                [
                    evento(
                        [cond("NumberObjectVariable", ["MiniJefe", "vida", "<=", "0"])],
                        [
                            accion("Delete", ["MiniJefe"]),
                            accion("SetNumberVariable", ["almas", "+", "5"]),
                            accion("ModVarGlobal", ["minijefe_derrotado", "=", "1"]),
                            accion_sonido("Meta"),
                            accion("TextObject::String", ["HUD_Aviso", "=", '"¡CARCELERO DERROTADO!"']),
                        ],
                    ),
                ],
            ),
            # Pisotón sobre MiniJefe cuando está con armadura (rebota sin daño)
            evento(
                [
                    cond("CollisionNP", ["Jugador", "MiniJefe", "no"]),
                    cond("PosY", ["Jugador", "<", "MiniJefe.Y() - 10"]),
                    cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                    cond("NumberObjectVariable", ["MiniJefe", "vulnerable", "=", "0"]),
                ],
                [
                    accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", str(int(REBOTE_ENEMIGO))]),
                    accion("PlatformBehavior::SetCanJump", ["Jugador", "PlatformerObject"]),
                    accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"]),
                    accion_sonido("Stomp"),
                    accion("TextObject::String", ["HUD_Aviso", "=", '"¡ARMADURA IMPENETRABLE! Espera a que se canse"']),
                ],
            ),
            # Golpe de pala a MiniJefe vulnerable
            evento(
                [
                    cond("CollisionNP", ["GolpePala", "MiniJefe", "no"]),
                    cond("NumberObjectVariable", ["MiniJefe", "vulnerable", "=", "1"]),
                ],
                [
                    accion("SetNumberObjectVariable", ["MiniJefe", "vida", "-", "1"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "vulnerable", "=", "0"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "estado", "=", "0"]),
                    accion("SetNumberObjectVariable", ["MiniJefe", "timer", "=", "0.50"]),
                    accion("Delete", ["GolpePala"]),
                    accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                    accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                    accion_sonido("Golpe"),
                    *acciones_sacudida(5.0, 0.12),
                ],
                [
                    evento(
                        [cond("NumberObjectVariable", ["MiniJefe", "vida", "<=", "0"])],
                        [
                            accion("Delete", ["MiniJefe"]),
                            accion("SetNumberVariable", ["almas", "+", "5"]),
                            accion("ModVarGlobal", ["minijefe_derrotado", "=", "1"]),
                            accion_sonido("Meta"),
                            accion("TextObject::String", ["HUD_Aviso", "=", '"¡CARCELERO DERROTADO!"']),
                        ],
                    ),
                ],
            ),
            # Golpe de pala a MiniJefe invulnerable
            evento(
                [
                    cond("CollisionNP", ["GolpePala", "MiniJefe", "no"]),
                    cond("NumberObjectVariable", ["MiniJefe", "vulnerable", "=", "0"]),
                ],
                [
                    accion("Delete", ["GolpePala"]),
                    accion_sonido("Golpe"),
                    *acciones_sacudida(3.0, 0.10),
                    accion("TextObject::String", ["HUD_Aviso", "=", '"¡ARMADURA IMPENETRABLE! Espera a que se canse"']),
                ],
            ),
            # Daño por contacto lateral con MiniJefe (protegido por Manto del Farol)
            evento(
                [
                    cond("CollisionNP", ["Jugador", "MiniJefe", "no"]),
                    cond("PosY", ["Jugador", ">=", "MiniJefe.Y() - 10"]),
                ],
                [],
                [
                    evento(
                        [cond("VarGlobal", ["escudo_farol", "=", "1"])],
                        [
                            accion("ModVarGlobal", ["escudo_farol", "=", "0"]),
                            accion_sonido("UI"),
                            *acciones_sacudida(5.0, 0.15),
                            accion("TextObject::String", ["HUD_Aviso", "=", '"¡MANTO DEL FAROL ABSORBIÓ EL IMPACTO!"']),
                        ],
                    ),
                    evento(
                        [cond("VarGlobal", ["escudo_farol", "=", "0"])],
                        [
                            accion("SetNumberVariable", ["vidas", "-", "1"]),
                            accion_sonido("Dano"),
                            *acciones_sacudida(9.0, 0.22),
                        ],
                        subeventos_reintento(destino_muerte),
                    ),
                ],
            ),
        ] if "MiniJefe" in nombres_objetos else []),

        # Daño por enemigo: contacto lateral o sin pala (protegido por Manto del Farol).
        *[
            evento(
                [
                    cond("CollisionNP", ["Jugador", enemigo_tipo, "no"]),
                    cond("PosY", ["Jugador", ">=", f"{enemigo_tipo}.Y() - 10"]),
                ],
                [],
                [
                    evento(
                        [cond("VarGlobal", ["escudo_farol", "=", "1"])],
                        [
                            accion("ModVarGlobal", ["escudo_farol", "=", "0"]),
                            accion_sonido("UI"),
                            *acciones_sacudida(5.0, 0.15),
                            accion("TextObject::String", ["HUD_Aviso", "=", '"¡MANTO DEL FAROL ABSORBIÓ EL IMPACTO!"']),
                        ],
                    ),
                    evento(
                        [cond("VarGlobal", ["escudo_farol", "=", "0"])],
                        [
                            accion("SetNumberVariable", ["vidas", "-", "1"]),
                            accion_sonido("Dano"),
                            *acciones_sacudida(9.0, 0.22),
                        ],
                        subeventos_reintento(destino_muerte),
                    ),
                ],
            )
            for enemigo_tipo in ("Enemy", "EnemyMelee", "Polilla", "Arana")
            if enemigo_tipo in nombres_objetos
        ],

        # Daño por obstáculos voladores o tótems (protegido por Manto del Farol).
        *[
            evento(
                [cond("CollisionNP", ["Jugador", obstaculo, "no"])],
                [],
                [
                    evento(
                        [cond("VarGlobal", ["escudo_farol", "=", "1"])],
                        [
                            accion("ModVarGlobal", ["escudo_farol", "=", "0"]),
                            accion_sonido("UI"),
                            *acciones_sacudida(5.0, 0.15),
                            accion("TextObject::String", ["HUD_Aviso", "=", '"¡MANTO DEL FAROL ABSORBIÓ EL IMPACTO!"']),
                        ],
                    ),
                    evento(
                        [cond("VarGlobal", ["escudo_farol", "=", "0"])],
                        [
                            accion("SetNumberVariable", ["vidas", "-", "1"]),
                            accion_sonido("Dano"),
                            *acciones_sacudida(9.0, 0.22),
                        ],
                        subeventos_reintento(destino_muerte),
                    ),
                ],
            )
            for obstaculo in ("Cuervo", "Totem")
            if obstaculo in nombres_objetos
        ],

        # FlipX horizontal de enemigos según dir
        *[
            sub_ev
            for ename in ("Enemy", "EnemyMelee", "MiniJefe")
            if ename in nombres_objetos
            for sub_ev in [
                evento(
                    [cond("NumberObjectVariable", [ename, "dir", "=", "-1"])],
                    [accion("FlipX", [ename, "yes"])],
                ),
                evento(
                    [cond("NumberObjectVariable", [ename, "dir", "=", "1"])],
                    [accion("FlipX", [ename, "no"])],
                ),
            ]
        ],

        # Pinchos y caída al vacío.
        *eventos_dano(
            nivel.alto,
            destino_muerte=destino_muerte,
            tiene_pinchos="Pinchos" in nombres_objetos,
        ),

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

    # --- Gravedad del jugador: un único escritor del comportamiento (plan T302) ---
    _SIN_PISO = cond("PlatformBehavior::IsOnFloor", ["Jugador", "PlatformerObject"], invertida=True)
    _TECLA_SALTO_MANTENIDA = cond_or(
        cond("KeyFromTextPressed", ["Space"]),
        cond("KeyFromTextPressed", ["Up"]),
        cond("KeyFromTextPressed", ["w"]),
        cond("KeyFromTextPressed", ["W"]),
    )

    def _fijar_gravedad_actual(valor: str) -> dict:
        return accion("SetNumberObjectVariable", ["Jugador", "gravedad_actual", "=", valor])

    bloque_gravedad = [
        evento([], [_fijar_gravedad_actual(str(int(GRAVEDAD)))]),
        evento(
            [
                _SIN_PISO,
                _TECLA_SALTO_MANTENIDA,
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"]),
                cond("PlatformBehavior::CurrentJumpSpeed", ["Jugador", "PlatformerObject", "<", str(int(APEX_VY_UMBRAL))]),
            ],
            [_fijar_gravedad_actual(str(int(GRAVEDAD * APEX_GRAVEDAD_FACTOR)))],
        ),
        evento(
            [
                _SIN_PISO,
                _TECLA_SALTO_MANTENIDA,
                cond("PlatformBehavior::IsFalling", ["Jugador", "PlatformerObject"]),
                cond("PlatformBehavior::CurrentFallSpeed", ["Jugador", "PlatformerObject", "<", str(int(APEX_VY_UMBRAL))]),
            ],
            [_fijar_gravedad_actual(str(int(GRAVEDAD * APEX_GRAVEDAD_FACTOR)))],
        ),
        evento(
            [cond("NumberObjectVariable", ["Jugador", "post_dash", ">", "0"])],
            [_fijar_gravedad_actual(str(int(GRAVEDAD * POST_DASH_GRAVEDAD_FACTOR)))],
        ),
        evento(
            [cond("NumberObjectVariable", ["Jugador", "dashing", "=", "1"])],
            [_fijar_gravedad_actual("0")],
        ),
        evento(
            [],
            [
                accion(
                    "PlatformBehavior::Gravity",
                    ["Jugador", "PlatformerObject", "=", "Jugador.Variable(gravedad_actual)"],
                ),
            ],
        ),
    ]
    eventos += bloque_gravedad
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
        objeto_texto("HUD_Nivel", spec.titulo, 20, HUESO, "center"),
        objeto_texto("HUD_Almas", "ALMAS 0 · VIDA +0/10", 18, AMARILLO),
        objeto_texto("HUD_Vidas", "VIDAS 3/5", 18, ROJO),
        objeto_texto("HUD_Aviso", "", 12, ROJO),
        objeto_texto("HUD_Dash", spec.hud, 12, TURQUESA),
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
        instancia(
            "Jugador",
            nivel.spawn[0],
            nivel.spawn[1],
            6,
            tam=(PLAYER_W, PLAYER_H),
        )
    )
    instancias.extend(instancias_entidades(escena_modelo))
    instancias.extend(instancias_hud())
    return objetos, instancias


def instancias_hud() -> list[dict]:
    """Instancias del HUD superior (capa UI, tamaño de la vista del juego: 1280x720)."""
    return [
        instancia("HUD_Barra", 0, 0, 0, capa="UI", tam=(GAME_W, 52)),
        instancia("HUD_Nivel", 173, 12, 1, capa="UI", tam=(933, 40)),
        instancia("HUD_Almas", 24, 19, 1, capa="UI"),
        instancia("HUD_Vidas", GAME_W - 133, 19, 1, capa="UI"),
        instancia("HUD_Aviso", 827, 45, 1, capa="UI"),
        instancia("HUD_Dash", 24, 47, 1, capa="UI"),
    ]


def escena_titulo(specs_campana: list | None = None) -> dict:
    if specs_campana is None:
        specs_campana = escenas_campaña()
    objetos = [
        objeto_sprite("FondoTitulo", "FondoTitulo"),
        objeto_texto("Menu_Titulo", "IN CRYPTA", 58, ORO, "center"),
        objeto_texto("Menu_Sub", "PLATAFORMERO GÓTICO 2D", 17, NIEBLA, "center"),
        objeto_texto("Menu_Op1", ">> 1 · JUGAR <<", 24, ORO, "center"),
        objeto_texto("Menu_Op1_Sub", "Comenzar la travesía desde el Camposanto", 14, CREMA, "center"),
        objeto_texto("Menu_Op2", "2 · SELECCIÓN DE NIVEL", 24, HUESO, "center"),
        objeto_texto("Menu_Op2_Sub", "Descender directamente a los niveles de la cripta", 14, NIEBLA, "center"),
        objeto_texto("Menu_Op3", "3 · TUTORIAL", 24, HUESO, "center"),
        objeto_texto("Menu_Op3_Sub", "El Ritual del Sepulturero · Aprende las mecánicas", 14, NIEBLA, "center"),
        objeto_texto("Menu_Op4", "4 · SALAS DE PRUEBA", 24, HUESO, "center"),
        objeto_texto("Menu_Op4_Sub", "Mecánicas aisladas para evaluación del jurado", 14, NIEBLA, "center"),
        objeto_texto(
            "Menu_Ayuda",
            "FLECHAS / WASD: ELEGIR · ENTER: SELECCIONAR · U: TUTORIAL · T: SALAS · 1..3: NIVELES",
            14,
            NIEBLA,
            "center",
        ),
    ]
    instancias = [
        instancia("FondoTitulo", 0, 0, 0, tam=(GAME_W, GAME_H)),
        instancia("Menu_Titulo", 0, 56, 2, "UI", tam=(GAME_W, 70)),
        instancia("Menu_Sub", 0, 130, 2, "UI", tam=(GAME_W, 28)),
        instancia("Menu_Op1", 0, 188, 3, "UI", tam=(GAME_W, 34)),
        instancia("Menu_Op1_Sub", 0, 222, 3, "UI", tam=(GAME_W, 24)),
        instancia("Menu_Op2", 0, 268, 3, "UI", tam=(GAME_W, 34)),
        instancia("Menu_Op2_Sub", 0, 302, 3, "UI", tam=(GAME_W, 24)),
        instancia("Menu_Op3", 0, 348, 3, "UI", tam=(GAME_W, 34)),
        instancia("Menu_Op3_Sub", 0, 382, 3, "UI", tam=(GAME_W, 24)),
        instancia("Menu_Op4", 0, 428, 3, "UI", tam=(GAME_W, 34)),
        instancia("Menu_Op4_Sub", 0, 462, 3, "UI", tam=(GAME_W, 24)),
        instancia("Menu_Ayuda", 0, GAME_H - 46, 3, "UI", tam=(GAME_W, 26)),
    ]

    arriba = cond_or(
        cond("KeyFromTextJustPressed", ['"Up"']),
        cond("KeyFromTextJustPressed", ['"w"']),
        cond("KeyFromTextJustPressed", ['"W"']),
    )
    abajo = cond_or(
        cond("KeyFromTextJustPressed", ['"Down"']),
        cond("KeyFromTextJustPressed", ['"s"']),
        cond("KeyFromTextJustPressed", ['"S"']),
    )
    confirmar = cond_or(
        cond("KeyFromTextJustPressed", ['"Return"']),
        cond("KeyFromTextJustPressed", ['"Space"']),
    )

    opcion_1 = [
        accion("TextObject::String", ["Menu_Op1", "=", '">> 1 · JUGAR <<"']),
        accion("TextObject::String", ["Menu_Op2", "=", '"2 · SELECCIÓN DE NIVEL"']),
        accion("TextObject::String", ["Menu_Op3", "=", '"3 · TUTORIAL"']),
        accion("TextObject::String", ["Menu_Op4", "=", '"4 · SALAS DE PRUEBA"']),
    ]
    opcion_2 = [
        accion("TextObject::String", ["Menu_Op1", "=", '"1 · JUGAR"']),
        accion("TextObject::String", ["Menu_Op2", "=", '">> 2 · SELECCIÓN DE NIVEL <<"']),
        accion("TextObject::String", ["Menu_Op3", "=", '"3 · TUTORIAL"']),
        accion("TextObject::String", ["Menu_Op4", "=", '"4 · SALAS DE PRUEBA"']),
    ]
    opcion_3 = [
        accion("TextObject::String", ["Menu_Op1", "=", '"1 · JUGAR"']),
        accion("TextObject::String", ["Menu_Op2", "=", '"2 · SELECCIÓN DE NIVEL"']),
        accion("TextObject::String", ["Menu_Op3", "=", '">> 3 · TUTORIAL <<"']),
        accion("TextObject::String", ["Menu_Op4", "=", '"4 · SALAS DE PRUEBA"']),
    ]
    opcion_4 = [
        accion("TextObject::String", ["Menu_Op1", "=", '"1 · JUGAR"']),
        accion("TextObject::String", ["Menu_Op2", "=", '"2 · SELECCIÓN DE NIVEL"']),
        accion("TextObject::String", ["Menu_Op3", "=", '"3 · TUTORIAL"']),
        accion("TextObject::String", ["Menu_Op4", "=", '">> 4 · SALAS DE PRUEBA <<"']),
    ]

    eventos = [
        evento(
            [cond("SceneJustBegins", [""])],
            [
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
                accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["almas_totales", "=", "0"]),
                accion("SetNumberVariable", ["combo_almas", "=", "0"]),
                accion("SetNumberVariable", ["combo_timer", "=", "0"]),
                accion("SetNumberVariable", ["muertes_totales", "=", "0"]),
                accion("SetNumberVariable", ["reducir_movimiento", "=", "0"]),
                accion("SetNumberVariable", ["rango_mejorado", "=", "0"]),
                accion("SetNumberVariable", ["jefe_derrotado", "=", "0"]),
                *acciones_camara_inicial(),
            ],
        ),
        evento([cond("NumberVariable", ["menu_opcion", "=", "1"])], opcion_1),
        evento([cond("NumberVariable", ["menu_opcion", "=", "2"])], opcion_2),
        evento([cond("NumberVariable", ["menu_opcion", "=", "3"])], opcion_3),
        evento([cond("NumberVariable", ["menu_opcion", "=", "4"])], opcion_4),

        # Navegación hacia arriba
        evento(
            [arriba, cond("NumberVariable", ["menu_opcion", "=", "1"])],
            [accion_sonido("UI"), accion("SetNumberVariable", ["menu_opcion", "=", "4"])],
        ),
        evento(
            [arriba, cond("NumberVariable", ["menu_opcion", ">", "1"])],
            [accion_sonido("UI"), accion("SetNumberVariable", ["menu_opcion", "-", "1"])],
        ),

        # Navegación hacia abajo
        evento(
            [abajo, cond("NumberVariable", ["menu_opcion", "=", "4"])],
            [accion_sonido("UI"), accion("SetNumberVariable", ["menu_opcion", "=", "1"])],
        ),
        evento(
            [abajo, cond("NumberVariable", ["menu_opcion", "<", "4"])],
            [accion_sonido("UI"), accion("SetNumberVariable", ["menu_opcion", "+", "1"])],
        ),

        # Confirmación
        evento(
            [confirmar, cond("NumberVariable", ["menu_opcion", "=", "1"])],
            [accion_sonido("UI"), accion("Scene", ['"Tutorial"', "no"])],
        ),
        evento(
            [confirmar, cond("NumberVariable", ["menu_opcion", "=", "2"])],
            [accion_sonido("UI"), accion("Scene", ['"Salas"', "no"])],
        ),
        evento(
            [confirmar, cond("NumberVariable", ["menu_opcion", "=", "3"])],
            [accion_sonido("UI"), accion("Scene", ['"Tutorial"', "no"])],
        ),
        evento(
            [confirmar, cond("NumberVariable", ["menu_opcion", "=", "4"])],
            [accion_sonido("UI"), accion("Scene", ['"Salas"', "no"])],
        ),

        # Clics de ratón en las opciones
        evento(
            [cond("SourisSurObjet", ["Menu_Op1", "", "", ""]), cond("MouseButtonReleased", ["", "Left"])],
            [accion_sonido("UI"), accion("Scene", ['"Tutorial"', "no"])],
        ),
        evento(
            [cond("SourisSurObjet", ["Menu_Op2", "", "", ""]), cond("MouseButtonReleased", ["", "Left"])],
            [accion_sonido("UI"), accion("Scene", ['"Salas"', "no"])],
        ),
        evento(
            [cond("SourisSurObjet", ["Menu_Op3", "", "", ""]), cond("MouseButtonReleased", ["", "Left"])],
            [accion_sonido("UI"), accion("Scene", ['"Tutorial"', "no"])],
        ),
        evento(
            [cond("SourisSurObjet", ["Menu_Op4", "", "", ""]), cond("MouseButtonReleased", ["", "Left"])],
            [accion_sonido("UI"), accion("Scene", ['"Salas"', "no"])],
        ),

        # Atajos de teclado directos
        evento(
            [cond_or(cond("KeyFromTextJustPressed", ['"u"']), cond("KeyFromTextJustPressed", ['"U"']))],
            [accion_sonido("UI"), accion("Scene", ['"Tutorial"', "no"])],
        ),
        evento(
            [cond_or(cond("KeyFromTextJustPressed", ['"t"']), cond("KeyFromTextJustPressed", ['"T"']))],
            [accion_sonido("UI"), accion("Scene", ['"Salas"', "no"])],
        ),
        evento(
            [cond_or(cond("KeyFromTextJustPressed", ['"Num1"']), cond("KeyFromTextJustPressed", ['"1"']))],
            [accion_sonido("UI"), accion("Scene", ['"Nivel 1"', "no"])],
        ),
        evento(
            [cond_or(cond("KeyFromTextJustPressed", ['"Num2"']), cond("KeyFromTextJustPressed", ['"2"']))],
            [accion_sonido("UI"), accion("Scene", ['"Nivel 2"', "no"])],
        ),
        evento(
            [cond_or(cond("KeyFromTextJustPressed", ['"Num3"']), cond("KeyFromTextJustPressed", ['"3"']))],
            [accion_sonido("UI"), accion("Scene", ['"Nivel 3"', "no"])],
        ),
    ]
    titulo = escena("Titulo", objetos, instancias, eventos)
    titulo["variables"] = [{"name": "menu_opcion", "type": "number", "value": 1}]
    return titulo


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
            [cond("KeyFromTextJustPressed", ['"Return"'])],
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


def escena_derrota(
    specs_campana: list | None = None,
    specs_salas: list | None = None,
) -> dict:
    if specs_campana is None:
        specs_campana = escenas_campaña()
    if specs_salas is None:
        specs_salas = escenas_salas()
    pw, ph = 680, 440
    px = (GAME_W - pw) // 2
    py = (GAME_H - ph) // 2

    objetos = [
        objeto_sprite("FondoDerrota", "FondoDerrota"),
        objeto_texto("Derrota_Titulo", "LA OSCURIDAD TE RECLAMA", 34, ROJO, "center"),
        objeto_texto("Derrota_Causa", "LA CRIPTA COBRÓ SU TRIBUTO", 15, CREMA, "center"),
        objeto_texto("Derrota_Stat1", "CAÍDAS TOTALES: 0", 20, ROJO, "center"),
        objeto_texto("Derrota_Stat2", "ALMAS COSECHADAS: 0", 20, ORO, "center"),
        objeto_texto(
            "Derrota_Prompt",
            "ENTER O ESPACIO: REINTENTAR  ·  ESC: MENÚ PRINCIPAL",
            16,
            ORO,
            "center",
        ),
    ]
    instancias = [
        instancia("FondoDerrota", 0, 0, 0, tam=(GAME_W, GAME_H)),
        instancia("Derrota_Titulo", 0, py + 26, 2, "UI", tam=(GAME_W, 44)),
        instancia("Derrota_Causa", 0, py + 78, 2, "UI", tam=(GAME_W, 26)),
        instancia("Derrota_Stat1", 0, py + 140, 2, "UI", tam=(GAME_W, 36)),
        instancia("Derrota_Stat2", 0, py + 196, 2, "UI", tam=(GAME_W, 36)),
        instancia("Derrota_Prompt", 0, py + 360, 2, "UI", tam=(GAME_W, 30)),
    ]

    reiniciar_partida = [
        accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
        accion("SetNumberVariable", ["almas", "=", "0"]),
        accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
        accion("SetNumberVariable", ["combo_almas", "=", "0"]),
        accion("SetNumberVariable", ["combo_timer", "=", "0"]),
        accion_sonido("UI"),
    ]

    eventos = [
        evento(
            [cond("SceneJustBegins", [""])],
            [
                *acciones_camara_inicial(),
                accion(
                    "TextObject::String",
                    ["Derrota_Stat1", "=", '"CAÍDAS TOTALES: " + ToString(GlobalVariable(muertes_totales))'],
                ),
                accion(
                    "TextObject::String",
                    ["Derrota_Stat2", "=", '"ALMAS COSECHADAS: " + ToString(GlobalVariable(almas_totales))'],
                ),
            ],
        ),
        evento(
            [
                cond_or(
                    cond("KeyFromTextJustPressed", ['"Return"']),
                    cond("KeyFromTextJustPressed", ['"Space"']),
                )
            ],
            reiniciar_partida,
            [
                evento(
                    [cond("NumberVariable", ["nivel_actual", "=", "0"])],
                    [accion("Scene", ['"Tutorial"', "no"])],
                ),
                *[
                    evento(
                        [cond("NumberVariable", ["nivel_actual", "=", str(i)])],
                        [accion("Scene", [f'"{spec.nombre}"', "no"])],
                    )
                    for i, spec in enumerate(specs_campana, start=1)
                ],
                *[
                    evento(
                        [cond("NumberVariable", ["nivel_actual", "=", str(10 + i)])],
                        [accion("Scene", [f'"{spec.nombre}"', "no"])],
                    )
                    for i, spec in enumerate(specs_salas, start=1)
                ],
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ['"Escape"'])],
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
    return escena("Derrota", objetos, instancias, eventos)


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
                cond("KeyFromTextJustPressed", ['"Up"']),
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "3"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ['"Up"']),
                cond("NumberVariable", ["menu_opcion", ">", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "-", "1"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ['"Down"']),
                cond("NumberVariable", ["menu_opcion", "=", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ['"Down"']),
                cond("NumberVariable", ["menu_opcion", "<", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "+", "1"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ['"Return"']),
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("PopScene", []),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ['"Return"']),
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
                cond("KeyFromTextJustPressed", ['"Return"']),
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


def escena_salas(specs_salas: list | None = None) -> dict:
    if specs_salas is None:
        specs_salas = escenas_salas()
    n = len(specs_salas)

    objetos = [
        objeto_sprite("FondoSalas", "FondoPausa"),
        objeto_texto("Salas_Titulo", "SALAS DE PRUEBA", 46, ORO, "center"),
        objeto_texto("Salas_Sub", "MECÁNICAS AISLADAS PARA EVALUACIÓN", 17, NIEBLA, "center"),
    ]
    for i in range(1, n + 1):
        objetos.append(objeto_texto(f"Salas_Opcion{i}", "", 22 if n > 4 else 24, HUESO, "center"))
    objetos.extend([
        objeto_texto("Salas_Desc1", "", 15, CREMA, "center"),
        objeto_texto("Salas_Desc2", "", 15, CREMA, "center"),
        objeto_texto(
            "Salas_Ayuda",
            f"FLECHAS: ELEGIR · ENTER: ENTRAR · 1..{min(n, 9)}: DIRECTO · ESC: VOLVER",
            14,
            NIEBLA,
            "center",
        ),
    ])

    instancias = [
        instancia("FondoSalas", 0, 0, 0, tam=(GAME_W, GAME_H)),
        instancia("Salas_Titulo", 0, 50, 2, "UI", tam=(GAME_W, 60)),
        instancia("Salas_Sub", 0, 108, 2, "UI", tam=(GAME_W, 30)),
    ]
    row_h = 44 if n > 4 else 55
    y_start = 145
    for i in range(1, n + 1):
        instancias.append(
            instancia(f"Salas_Opcion{i}", 0, y_start + (i - 1) * row_h, 3, "UI", tam=(GAME_W, row_h - 6))
        )
    desc_y = y_start + n * row_h + 12
    instancias.extend([
        instancia("Salas_Desc1", 0, desc_y, 3, "UI", tam=(GAME_W, 24)),
        instancia("Salas_Desc2", 0, desc_y + 26, 3, "UI", tam=(GAME_W, 24)),
        instancia("Salas_Ayuda", 0, GAME_H - 45, 3, "UI", tam=(GAME_W, 26)),
    ])

    eventos_opciones = []
    for k, spec in enumerate(specs_salas, start=1):
        acciones_k = []
        for j, s_other in enumerate(specs_salas, start=1):
            if j == k:
                texto_item = f'">> {j} · {s_other.titulo} <<"'
            else:
                texto_item = f'"{j} · {s_other.titulo}"'
            acciones_k.append(accion("TextObject::String", [f"Salas_Opcion{j}", "=", texto_item]))
        limpio_pista = spec.pista.replace('"', "'")
        lines = textwrap.wrap(limpio_pista, width=86)
        d1 = lines[0] if lines else ""
        d2 = lines[1] if len(lines) > 1 else ""
        acciones_k.append(accion("TextObject::String", ["Salas_Desc1", "=", f'"{d1}"']))
        acciones_k.append(accion("TextObject::String", ["Salas_Desc2", "=", f'"{d2}"']))
        eventos_opciones.append(
            evento([cond("NumberVariable", ["menu_opcion", "=", str(k)])], acciones_k)
        )

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

    eventos = [
        evento(
            [cond("SceneJustBegins", [""])],
            [
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
                *acciones_camara_inicial(),
            ],
        ),
        *eventos_opciones,
        evento(
            [
                arriba,
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", str(n)]),
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
                cond("NumberVariable", ["menu_opcion", "=", str(n)]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
            ],
        ),
        evento(
            [
                abajo,
                cond("NumberVariable", ["menu_opcion", "<", str(n)]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "+", "1"]),
            ],
        ),
        *[
            evento(
                [
                    cond("KeyFromTextJustPressed", ['"Return"']),
                    cond("NumberVariable", ["menu_opcion", "=", str(k)]),
                ],
                [
                    accion_sonido("UI"),
                    accion("Scene", [f'"{spec.nombre}"', "no"]),
                ],
            )
            for k, spec in enumerate(specs_salas, start=1)
        ],
        *[
            evento(
                [cond("KeyFromTextJustPressed", [f'"{k}"'])],
                [
                    accion_sonido("UI"),
                    accion("Scene", [f'"{spec.nombre}"', "no"]),
                ],
            )
            for k, spec in enumerate(specs_salas[:9], start=1)
        ],
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
    sala_num = 1
    if "_" in spec.clave:
        try:
            sala_num = int(spec.clave.split("_")[-1])
        except ValueError:
            pass
    eventos = eventos_nivel(
        escena_modelo.nivel,
        10 + sala_num,
        1,
        siguiente=spec.siguiente,
        pala_inicial=spec.pala_inicial,
        texto_dash_sin_pala=f'"{spec.hud_sin_pala}"',
        destino_muerte=spec.destino_muerte,
        reiniciar_vidas=spec.reiniciar_vidas,
        nombres_objetos={obj["name"] for obj in objetos},
    )
    eventos.extend(reglas_escena(escena_modelo))
    return escena(spec.nombre, objetos, instancias, eventos)


# ------------------------------------------------------------
# Proyecto
# ------------------------------------------------------------
def construir_proyecto(escenas: list[Escena]) -> dict:
    base: dict = {
        "properties": {},
        "firstLayout": "",
        "resources": {"resources": []},
        "objects": [],
        "objectsGroups": [],
        "variables": [],
        "layouts": [],
        "usedResources": [],
        "externalEvents": [],
        "externalLayouts": [],
    }

    recursos = [
        recurso_imagen("FondoTitulo", "assets/titulo.png"),
        recurso_imagen("FondoVictoria", "assets/victoria.png"),
        recurso_imagen("FondoDerrota", "assets/derrota.png"),
        recurso_imagen("FondoPausa", "assets/pausa.png"),
        recurso_imagen("Jugador", "assets/jugador.png"),
        recurso_imagen("JugadorCaida1", "assets/jugador_caida_1.png"),
        recurso_imagen("JugadorCaida2", "assets/jugador_caida_2.png"),
        recurso_imagen("JugadorAtaque1", "assets/jugador_ataque_1.png"),
        recurso_imagen("JugadorAtaque2", "assets/jugador_ataque_2.png"),
        recurso_imagen("JugadorAtaque3", "assets/jugador_ataque_3.png"),
        recurso_imagen("JugadorIzq", "assets/jugador_izq.png"),
        recurso_imagen("JugadorCaidaIzq1", "assets/jugador_caida_izq_1.png"),
        recurso_imagen("JugadorCaidaIzq2", "assets/jugador_caida_izq_2.png"),
        recurso_imagen("JugadorAtaqueIzq1", "assets/jugador_ataque_izq_1.png"),
        recurso_imagen("JugadorAtaqueIzq2", "assets/jugador_ataque_izq_2.png"),
        recurso_imagen("JugadorAtaqueIzq3", "assets/jugador_ataque_izq_3.png"),
        recurso_imagen("JugadorSinPala", "assets/jugador_sin_pala.png"),
        recurso_imagen("JugadorCaidaSinPala1", "assets/jugador_caida_sin_pala_1.png"),
        recurso_imagen("JugadorCaidaSinPala2", "assets/jugador_caida_sin_pala_2.png"),
        recurso_imagen("JugadorIzqSinPala", "assets/jugador_izq_sin_pala.png"),
        recurso_imagen("JugadorCaidaIzqSinPala1", "assets/jugador_caida_izq_sin_pala_1.png"),
        recurso_imagen("JugadorCaidaIzqSinPala2", "assets/jugador_caida_izq_sin_pala_2.png"),
        recurso_imagen("Pala", "assets/pala.png"),
        recurso_imagen("Puerta", "assets/puerta.png"),
        recurso_imagen("Jefe", "assets/jefe.png"),
        recurso_imagen("OndaJefe", "assets/onda_jefe.png"),
        recurso_imagen("TexturaSolido", "assets/solido.png"),
        recurso_imagen("BarraHUD", "assets/barra_hud.png"),
        recurso_imagen("BarraPista", "assets/barra_pista.png"),
        recurso_imagen("GolpeDer1", "assets/golpe_der_1.png"),
        recurso_imagen("GolpeDer2", "assets/golpe_der_2.png"),
        recurso_imagen("GolpeDer3", "assets/golpe_der_3.png"),
        recurso_imagen("GolpeIzq1", "assets/golpe_izq_1.png"),
        recurso_imagen("GolpeIzq2", "assets/golpe_izq_2.png"),
        recurso_imagen("GolpeIzq3", "assets/golpe_izq_3.png"),
        recurso_fuente(FONT_RESOURCE, FONT_FILE),
        recurso_audio("SFX_Salto", "assets/sfx_salto.wav"),
        recurso_audio("SFX_Alma", "assets/sfx_alma.wav"),
        recurso_audio("SFX_Dash", "assets/sfx_dash.wav"),
        recurso_audio("SFX_Pala", "assets/sfx_pala.wav"),
        recurso_audio("SFX_PalaRecoger", "assets/sfx_pala_recoger.wav"),
        recurso_audio("SFX_Golpe", "assets/sfx_golpe.wav"),
        recurso_audio("SFX_Dano", "assets/sfx_dano.wav"),
        recurso_audio("SFX_Meta", "assets/sfx_meta.wav"),
        recurso_audio("SFX_Vida", "assets/sfx_vida.wav"),
        recurso_audio("SFX_UI", "assets/sfx_ui.wav"),
        # Nuevos (commit 020b19c): pisotón, muerte, combo de almas
        recurso_audio("SFX_Stomp", "assets/sfx_stomp.wav"),
        recurso_audio("SFX_Muerte", "assets/sfx_muerte.wav"),
        *[recurso_audio(f"SFX_Alma{i}", f"assets/sfx_alma_{i}.wav") for i in range(1, 7)],
    ]

    # Frames multipose Pixel-Art góticos (Prioridad 5)
    for pose, cnt in [("idle", 4), ("run", 6), ("jump", 2), ("caida", 2), ("dash", 3), ("ataque", 3)]:
        for f in range(1, cnt + 1):
            recursos.append(recurso_imagen(f"Jugador_{pose.capitalize()}_{f}", f"assets/jugador_{pose}_{f}.png"))
            recursos.append(recurso_imagen(f"Jugador_{pose.capitalize()}_Izq_{f}", f"assets/jugador_{pose}_izq_{f}.png"))
            recursos.append(recurso_imagen(f"Jugador_{pose.capitalize()}_SinPala_{f}", f"assets/jugador_{pose}_sin_pala_{f}.png"))
            recursos.append(recurso_imagen(f"Jugador_{pose.capitalize()}_Izq_SinPala_{f}", f"assets/jugador_{pose}_izq_sin_pala_{f}.png"))

    for f in range(1, 5):
        recursos.append(recurso_imagen(f"EnemyWalk{f}", f"assets/enemy_walk_{f}.png"))
        recursos.append(recurso_imagen(f"EnemyMeleeWalk{f}", f"assets/enemymelee_walk_{f}.png"))
        recursos.append(recurso_imagen(f"MiniJefeWalk{f}", f"assets/minijefe_walk_{f}.png"))
        recursos.append(recurso_imagen(f"JefeWalk{f}", f"assets/jefe_walk_{f}.png"))
        recursos.append(recurso_imagen(f"Alma{f}", f"assets/alma_{f}.png"))
        recursos.append(recurso_imagen(f"FarolOn{f}", f"assets/farolcheckpoint_on_{f}.png"))
        recursos.append(recurso_imagen(f"PowerUpDash{f}", f"assets/powerupdash_{f}.png"))
        recursos.append(recurso_imagen(f"PowerUpRango{f}", f"assets/poweruprango_{f}.png"))
        recursos.append(recurso_imagen(f"PalaRecogible{f}", f"assets/pala_{f}.png"))

    recursos.append(recurso_imagen("FarolOff", "assets/farolcheckpoint_off.png"))
    recursos.append(recurso_imagen("PaletaGothica", "assets/paleta_gothica.png"))

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
            recursos.append(recurso_imagen(nombre, f"assets/{nombre.lower()}.png"))
    for escena_modelo in escenas:
        recursos.append(
            recurso_imagen(
                escena_modelo.spec.fondo,
                f"assets/fondo_{escena_modelo.spec.clave}.png",
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
            "scaleMode": "nearest",
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
    specs_campana = [
        e.spec
        for e in escenas
        if not e.spec.es_sala and not getattr(e.spec, "es_tutorial", False)
    ]
    specs_salas = [e.spec for e in escenas if e.spec.es_sala]
    base["variables"] = [
        {"name": "vidas", "type": "number", "value": VIDAS_INICIALES},
        {"name": "almas", "type": "number", "value": 0},
        {"name": "almas_totales", "type": "number", "value": 0},
        {"name": "almas_para_vida", "type": "number", "value": 0},
        {"name": "combo_almas", "type": "number", "value": 0},
        {"name": "combo_timer", "type": "number", "value": 0},
        {"name": "muertes_totales", "type": "number", "value": 0},
        {"name": "reducir_movimiento", "type": "number", "value": 0},
        {"name": "nivel_actual", "type": "number", "value": 1},
        {"name": "reiniciar", "type": "number", "value": 0},
        {"name": "jefe_derrotado", "type": "number", "value": 0},
        {"name": "cam_x", "type": "number", "value": GAME_W // 2},
        {"name": "cam_y", "type": "number", "value": GAME_H // 2},
        {"name": "sacudida_f", "type": "number", "value": 0},
        {"name": "sacudida_t", "type": "number", "value": 0},
        {"name": "rango_mejorado", "type": "number", "value": 0},
        {"name": "checkpoint_x", "type": "number", "value": 0},
        {"name": "checkpoint_y", "type": "number", "value": 0},
        {"name": "checkpoint_activo", "type": "number", "value": 0},
        {"name": "checkpoint_escena", "type": "string", "value": ""},
        {"name": "escudo_farol", "type": "number", "value": 0},
        {"name": "almas_consagradas", "type": "number", "value": 0},
        {"name": "almas_vida_consagradas", "type": "number", "value": 0},
        {"name": "minijefe_derrotado", "type": "number", "value": 0},
        {"name": "menu_opcion", "type": "number", "value": 1},
    ]
    base["layouts"] = [
        escena_titulo(specs_campana),
        escena_pausa(),
        escena_derrota(specs_campana, specs_salas),
        escena_victoria(),
        escena_salas(specs_salas),
    ]
    total_campana = len(specs_campana)
    indice = 0
    for escena_modelo in escenas:
        spec = escena_modelo.spec
        if spec.es_sala:
            base["layouts"].append(escena_sala(escena_modelo))
            continue
        if getattr(spec, "es_tutorial", False):
            objetos, instancias = objetos_y_instancias_escena(escena_modelo)
            eventos = eventos_nivel(
                escena_modelo.nivel,
                0,
                total_campana,
                siguiente=spec.siguiente,
                pala_inicial=spec.pala_inicial,
                texto_dash_sin_pala=f'"{spec.hud_sin_pala}"',
                destino_muerte=spec.destino_muerte,
                reiniciar_vidas=spec.reiniciar_vidas,
                nombres_objetos={obj["name"] for obj in objetos},
            )
            eventos.extend(reglas_escena(escena_modelo))
            base["layouts"].append(escena(spec.nombre, objetos, instancias, eventos))
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
            nombres_objetos={obj["name"] for obj in objetos},
        )
        eventos.extend(reglas_escena(escena_modelo))
        base["layouts"].append(escena(spec.nombre, objetos, instancias, eventos))
    todos_recursos = [{"name": r["name"]} for r in recursos]
    for layout in base["layouts"]:
        layout["usedResources"] = list(todos_recursos)

    base["usedResources"] = list(todos_recursos)
    base["externalEvents"] = []
    base["externalLayouts"] = []
    return base


def limpiar_assets(proyecto: dict) -> list[str]:
    """Borra los archivos de assets que el proyecto ya no referencia.

    Sin esto se acumulan texturas y sonidos viejos (los que el generador
    cambió de nombre o dejó de generar) que confunden al abrir el proyecto.
    """
    usados = {
        Path(recurso.get("file", "")).name
        for recurso in proyecto["resources"]["resources"]
        if recurso.get("file")
    }
    borrados = []
    for archivo in sorted(ASSETS.iterdir()):
        if archivo.is_file() and archivo.name not in usados:
            archivo.unlink()
            borrados.append(archivo.name)
    return borrados


def main() -> int:
    pygame.init()
    OUT.mkdir(parents=True, exist_ok=True)
    specs = [escena_tutorial()] + escenas_campaña() + escenas_salas()
    escenas = [leer_escena(spec) for spec in specs]

    generar_assets(escenas)
    proyecto = construir_proyecto(escenas)
    borrados = limpiar_assets(proyecto)

    contenido_json = json.dumps(proyecto, ensure_ascii=False, indent=2)

    destino = OUT / PROJECT_NAME
    destino.write_text(contenido_json, encoding="utf-8")

    # Integración de assets pixel-art góticos y animaciones multipose (Prioridad 5)
    # Cualquier fallo aquí detiene la exportación con código distinto de cero.
    import integrar_assets_gdevelop
    integrar_assets_gdevelop.generar_todos_los_assets()
    integrar_assets_gdevelop.actualizar_proyecto_gdevelop(destino)

    # Limpiar posibles restos .autosave y .bak que GDevelop pueda haber creado
    for residuo in list(OUT.glob("*.autosave")) + list(OUT.glob("*.bak*")):
        try:
            residuo.unlink()
        except OSError:
            pass

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
