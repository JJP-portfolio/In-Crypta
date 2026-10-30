# ============================================================
# generar_proyecto_nativo.py — IN CRYPTA como proyecto GDevelop
# ============================================================
# Genera un proyecto GDevelop nativo (JSON + PNGs) a partir de
# los mismos mapas y entidades del juego Pygame. No usa el runtime
# JavaScript: el movimiento, las colisiones y los eventos viven en
# el proyecto de GDevelop.
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

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from config import (
    ALMAS_POR_VIDA,
    ALTO,
    AMARILLO,
    ANCHO,
    AZUL_OSCURO,
    BLANCO,
    CREMA,
    DASH_DURACION,
    DASH_VELOCIDAD,
    ENEMIGO_ALTO,
    ENEMIGO_ANCHO,
    GRAVEDAD,
    GRIS,
    HUESO,
    HUD_ALMA,
    HUD_BORDE,
    HUD_MUTED,
    HUD_ORO,
    HUD_PANEL,
    HUD_PANEL_ALTO,
    HUD_ROJO,
    HUD_TEXTO,
    HUD_VERDE,
    JEFE_ALTO,
    JEFE_ANCHO,
    JEFE_ONDA_VELOCIDAD,
    JEFE_VIDA,
    JUGADOR_ALTO,
    JUGADOR_ANCHO,
    MARRON,
    MAX_CAIDA,
    NEGRO,
    NIEBLA,
    ORO,
    ROJO,
    SALTO,
    SANGRE,
    TURQUESA,
    VELOCIDAD,
    VELOCIDAD_ENEMIGO,
    VIDAS_INICIALES,
    VIDAS_MAXIMAS,
)
from entidades import Alma, Custodio, Enemigo, Jugador, OndaCustodio, PalaRecogible
from nivel import Nivel, DECORACIONES
from niveles import NIVELES, SALAS_PRUEBA


OUT = ROOT / "export" / "gdevelop_nativo"
ASSETS = OUT / "assets"
PROJECT_NAME = "IN_CRYPTA_NATIVO.json"
BASE_PROJECT = (
    Path.home()
    / "Documentos"
    / "GDevelop projects"
    / "My project"
    / "Cryptus - Copy.json"
)
FONT_SOURCE = Path("/usr/share/fonts/noto/NotoSerifDisplay-Bold.ttf")
FONT_RESOURCE = "FuenteHUD"
FONT_FILE = "assets/NotoSerifDisplay-Bold.ttf"

GAME_W = ANCHO
GAME_H = ALTO
RENDER_W = 1920
RENDER_H = 1080
GAME_ZOOM = 2
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
def uid() -> str:
    return str(uuid.uuid4())


def cond(tipo: str, parametros=None, invertida: bool = False) -> dict:
    data = {"value": tipo}
    if invertida:
        data["inverted"] = True
    return {"type": data, "parameters": parametros or []}


def accion(tipo: str, parametros=None) -> dict:
    return {"type": {"value": tipo}, "parameters": parametros or []}


def evento(condiciones=None, acciones=None, subeventos=None) -> dict:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": condiciones or [],
        "actions": acciones or [],
        "events": subeventos or [],
    }


def cond_or(*condiciones) -> dict:
    return {
        "type": {"value": "BuiltinCommonInstructions::Or"},
        "parameters": [],
        "subInstructions": list(condiciones),
    }


def escena_mangled(nombre: str) -> str:
    return nombre.replace(" ", "_32_")


def recurso_imagen(nombre: str, archivo: str) -> dict:
    return {
        "file": archivo,
        "kind": "image",
        "metadata": "",
        "name": nombre,
        "smoothed": True,
        "userAdded": True,
    }


def recurso_fuente(nombre: str, archivo: str) -> dict:
    return {
        "file": archivo,
        "kind": "font",
        "metadata": "",
        "name": nombre,
        "userAdded": True,
    }


def recurso_audio(nombre: str, archivo: str) -> dict:
    return {
        "file": archivo,
        "kind": "audio",
        "metadata": "",
        "name": nombre,
        "preloadAsMusic": False,
        "preloadAsSound": True,
        "userAdded": True,
    }


def objeto_sprite(nombre: str, imagen: str, variables=None, comportamientos=None) -> dict:
    return {
        "adaptCollisionMaskAutomatically": False,
        "assetStoreId": "",
        "name": nombre,
        "persistentUuid": uid(),
        "type": "Sprite",
        "updateIfNotVisible": False,
        "variables": variables or [],
        "effects": [],
        "behaviors": comportamientos or [],
        "animations": [
            {
                "name": "Idle",
                "useMultipleDirections": False,
                "directions": [
                    {
                        "looping": False,
                        "timeBetweenFrames": 0.08,
                        "sprites": [
                            {
                                "hasCustomCollisionMask": False,
                                "image": imagen,
                                "points": [],
                                "originPoint": {"name": "origine", "x": 0, "y": 0},
                                "centerPoint": {
                                    "automatic": True,
                                    "name": "centre",
                                    "x": 0,
                                    "y": 0,
                                },
                            }
                        ],
                    }
                ],
            }
        ],
    }


def _animacion(nombre: str, imagenes: list[str], looping: bool, tiempo: float) -> dict:
    return {
        "name": nombre,
        "useMultipleDirections": False,
        "directions": [
            {
                "looping": looping,
                "timeBetweenFrames": tiempo,
                "sprites": [
                    {
                        "hasCustomCollisionMask": False,
                        "image": imagen,
                        "points": [],
                        "originPoint": {"name": "origine", "x": 0, "y": 0},
                        "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0},
                    }
                    for imagen in imagenes
                ],
            }
        ],
    }


def objeto_jugador() -> dict:
    data = objeto_sprite("Jugador", "Jugador", variables_jugador(), [comportamiento_jugador()])
    data["animations"] = [
        _animacion("Idle", ["Jugador"], True, 0.12),
        _animacion("Caida", ["JugadorCaida1", "JugadorCaida2"], True, 0.14),
        _animacion("Ataque", ["JugadorAtaque1", "JugadorAtaque2", "JugadorAtaque3"], False, 0.06),
        _animacion("IdleIzq", ["JugadorIzq"], True, 0.12),
        _animacion("CaidaIzq", ["JugadorCaidaIzq1", "JugadorCaidaIzq2"], True, 0.14),
        _animacion(
            "AtaqueIzq",
            ["JugadorAtaqueIzq1", "JugadorAtaqueIzq2", "JugadorAtaqueIzq3"],
            False,
            0.06,
        ),
        _animacion("IdleSinPala", ["JugadorSinPala"], True, 0.12),
        _animacion(
            "CaidaSinPala",
            ["JugadorCaidaSinPala1", "JugadorCaidaSinPala2"],
            True,
            0.14,
        ),
        _animacion("IdleIzqSinPala", ["JugadorIzqSinPala"], True, 0.12),
        _animacion(
            "CaidaIzqSinPala",
            ["JugadorCaidaIzqSinPala1", "JugadorCaidaIzqSinPala2"],
            True,
            0.14,
        ),
    ]
    return data


def objeto_pala() -> dict:
    return objeto_sprite("PalaRecogible", "Pala")


def objeto_plataforma() -> dict:
    return objeto_sprite(
        "PlataformaMovil",
        "PlataformaMovil",
        variables_plataforma(),
        [comportamiento_plataforma()],
    )


def objeto_golpe() -> dict:
    data = objeto_sprite(
        "GolpePala",
        "GolpePala",
        variables=[{"name": "vida", "type": "number", "value": 0.18}],
    )
    data["animations"] = [
        _animacion("Der1", ["GolpeDer1"], False, 0.18),
        _animacion("Der2", ["GolpeDer2"], False, 0.18),
        _animacion("Der3", ["GolpeDer3"], False, 0.18),
        _animacion("Izq1", ["GolpeIzq1"], False, 0.18),
        _animacion("Izq2", ["GolpeIzq2"], False, 0.18),
        _animacion("Izq3", ["GolpeIzq3"], False, 0.18),
    ]
    return data


def variables_jefe() -> list[dict]:
    return [
        {"name": "vida", "type": "number", "value": JEFE_VIDA},
        {"name": "fase", "type": "number", "value": 1},
        {"name": "estado", "type": "number", "value": 0},
        {"name": "timer", "type": "number", "value": 1.25},
        {"name": "vulnerable", "type": "number", "value": 0},
        {"name": "golpes_fase", "type": "number", "value": 0},
    ]


def variables_onda() -> list[dict]:
    return [
        {"name": "vida", "type": "number", "value": 3.4},
        {"name": "velocidad", "type": "number", "value": int(JEFE_ONDA_VELOCIDAD)},
    ]


def objeto_jefe() -> dict:
    return objeto_sprite("Jefe", "Jefe", variables_jefe())


def objeto_onda() -> dict:
    return objeto_sprite("OndaIzq", "OndaJefe", variables_onda())


def objeto_onda_der() -> dict:
    return objeto_sprite("OndaDer", "OndaJefe", variables_onda())


def objeto_tiled(nombre: str, textura: str, ancho: int, alto: int, comportamientos=None) -> dict:
    return {
        "assetStoreId": "",
        "height": alto,
        "name": nombre,
        "persistentUuid": uid(),
        "texture": textura,
        "type": "TiledSpriteObject::TiledSprite",
        "width": ancho,
        "variables": [],
        "effects": [],
        "behaviors": comportamientos or [],
    }


def objeto_texto(nombre: str, texto: str, tamano: int, color: tuple[int, int, int], alineacion: str = "left") -> dict:
    color_txt = f"{color[0]};{color[1]};{color[2]}"
    return {
        "assetStoreId": "",
        "bold": True,
        "italic": False,
        "name": nombre,
        "smoothed": False,
        "type": "TextObject::Text",
        "underlined": False,
        "variables": [],
        "effects": [],
        "behaviors": [],
        "string": texto,
        "font": FONT_RESOURCE,
        "textAlignment": alineacion,
        "characterSize": tamano,
        "color": {"b": color[2], "g": color[1], "r": color[0]},
        "content": {
            "bold": True,
            "isOutlineEnabled": True,
            "isShadowEnabled": True,
            "italic": False,
            "outlineColor": "9;8;13",
            "outlineThickness": 2,
            "shadowAngle": 90,
            "shadowBlurRadius": 0,
            "shadowColor": "0;0;0",
            "shadowDistance": 2,
            "shadowOpacity": 160,
            "smoothed": False,
            "underlined": False,
            "text": texto,
            "font": FONT_RESOURCE,
            "textAlignment": alineacion,
            "verticalTextAlignment": "top",
            "characterSize": tamano,
            "lineHeight": 0,
            "color": color_txt,
        },
    }


def instancia(nombre: str, x: float, y: float, z: int, capa: str = "", tam=None, variables=None) -> dict:
    ancho = 0
    alto = 0
    personalizado = False
    if tam is not None:
        ancho, alto = tam
        personalizado = True
    return {
        "angle": 0,
        "customSize": personalizado,
        "height": alto,
        "keepRatio": True,
        "layer": capa,
        "name": nombre,
        "persistentUuid": uid(),
        "width": ancho,
        "x": x,
        "y": y,
        "zOrder": z,
        "numberProperties": [],
        "stringProperties": [],
        "initialVariables": variables or [],
    }


def comportamiento_plataforma() -> dict:
    return {
        "name": "Platform",
        "type": "PlatformBehavior::PlatformBehavior",
        "canBeGrabbed": True,
        "platformType": "NormalPlatform",
        "yGrabOffset": 0,
    }


def comportamiento_jugador() -> dict:
    return {
        "name": "PlatformerObject",
        "type": "PlatformBehavior::PlatformerObjectBehavior",
        "acceleration": 20000,
        "canGoDownFromJumpthru": True,
        "canGrabPlatforms": False,
        "canGrabWithoutMoving": True,
        "deceleration": 20000,
        "gravity": 1500,
        "ignoreDefaultControls": True,
        "jumpSpeed": 620,
        "jumpSustainTime": 0,
        "ladderClimbingSpeed": 150,
        "maxFallingSpeed": 900,
        "maxSpeed": 250,
        "slopeMaxAngle": 60,
        "useLegacyTrajectory": False,
        "useRepeatedJump": False,
        "xGrabTolerance": 10,
        "yGrabOffset": 0,
    }


def comportamiento_enemigo() -> dict:
    data = comportamiento_jugador()
    data.update(
        {
            "acceleration": 1000,
            "deceleration": 1000,
            "gravity": 1500,
            "ignoreDefaultControls": True,
            "jumpSpeed": 0,
            "maxFallingSpeed": 900,
            "maxSpeed": VELOCIDAD_ENEMIGO,
        }
    )
    return data


def variables_jugador() -> list[dict]:
    return [
        {"name": "dir", "type": "number", "value": 1},
        {"name": "tiene_pala", "type": "number", "value": 0},
        {"name": "dashing", "type": "number", "value": 0},
        {"name": "dash_time", "type": "number", "value": 0},
        {"name": "dash_cd", "type": "number", "value": 0},
        {"name": "dash_aire", "type": "number", "value": 1},
        {"name": "coyote", "type": "number", "value": 0},
        {"name": "buffer_salto", "type": "number", "value": 0},
        {"name": "atacando", "type": "number", "value": 0},
        {"name": "ataque_time", "type": "number", "value": 0},
        {"name": "ataque_cd", "type": "number", "value": 0},
    ]


def variables_enemigo() -> list[dict]:
    return [
        {"name": "dir", "type": "number", "value": 1},
        {"name": "min_x", "type": "number", "value": 0},
        {"name": "max_x", "type": "number", "value": 0},
    ]


def variables_plataforma() -> list[dict]:
    return [
        {"name": "origen_x", "type": "number", "value": 0},
        {"name": "origen_y", "type": "number", "value": 0},
        {"name": "amplitud", "type": "number", "value": 96},
        {"name": "velocidad", "type": "number", "value": 1.35},
        {"name": "fase", "type": "number", "value": 0},
        {"name": "eje", "type": "number", "value": 1},
    ]


def capa_base() -> dict:
    return {
        "ambientLightColorB": 200,
        "ambientLightColorG": 200,
        "ambientLightColorR": 200,
        "camera2DPlaneMaxDrawingDistance": 5000,
        "camera3DFarPlaneDistance": 10000,
        "camera3DFieldOfView": 45,
        "camera3DNearPlaneDistance": 3,
        "cameraType": "",
        "followBaseLayerCamera": False,
        "isLightingLayer": False,
        "isLocked": False,
        "name": "",
        "renderingType": "",
        "visibility": True,
        "cameras": [
            {
                "defaultSize": True,
                "defaultViewport": True,
                "height": 0,
                "viewportBottom": 1,
                "viewportLeft": 0,
                "viewportRight": 1,
                "viewportTop": 0,
                "width": 0,
            }
        ],
        "effects": [],
    }


def capa_ui() -> dict:
    data = capa_base()
    data["name"] = "UI"
    data["cameras"] = capa_base()["cameras"]
    data["effects"] = []
    return data


def escena(nombre: str, objetos: list[dict], instancias: list[dict], eventos: list[dict]) -> dict:
    return {
        "b": 13,
        "disableInputWhenNotFocused": True,
        "mangledName": escena_mangled(nombre),
        "name": nombre,
        "r": 9,
        "renderer3DWorldScale": 100,
        "standardSortMethod": True,
        "stopSoundsOnStartup": False,
        "title": "",
        "v": 8,
        "uiSettings": {
            "grid": False,
            "gridType": "rectangular",
            "gridWidth": 32,
            "gridHeight": 32,
            "gridDepth": 32,
            "gridOffsetX": 0,
            "gridOffsetY": 0,
            "gridOffsetZ": 0,
            "gridColor": 10401023,
            "gridAlpha": 0.8,
            "snap": False,
            "zoomFactor": 0.36,
            "windowMask": False,
            "selectedLayer": "",
            "gameEditorMode": "instances-editor",
        },
        "objectsGroups": [],
        "variables": [],
        "instances": instancias,
        "objects": objetos,
        "objectsFolderStructure": {"folderName": "__ROOT"},
        "events": eventos,
        "layers": [capa_base(), capa_ui()],
        "behaviorsSharedData": [],
    }


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


def guardar_enemigo() -> None:
    surface = pygame.Surface((ENEMIGO_ANCHO, ENEMY_SPRITE_H), pygame.SRCALPHA)
    enemigo = Enemigo(pygame.Rect(0, 0, ENEMIGO_ANCHO, ENEMIGO_ALTO), -1000, 1000)
    enemigo.dibujar(surface, CamaraCompleta(), 0.0)
    guardar_2x(surface, "enemigo.png")


def guardar_alma() -> None:
    surface = pygame.Surface((SOUL_SPRITE, SOUL_SPRITE), pygame.SRCALPHA)
    alma = Alma(pygame.Rect(4, 4, 16, 16))
    alma.dibujar(surface, CamaraCompleta(), 0.0)
    guardar_2x(surface, "alma.png")


def guardar_pinchos() -> None:
    surface = pygame.Surface((PINCHOS_W, PINCHOS_H), pygame.SRCALPHA)
    for i in range(3):
        x = i * 8
        pygame.draw.polygon(surface, (130, 125, 112), [(x, PINCHOS_H), (x + 4, 0), (x + 8, PINCHOS_H)])
        pygame.draw.line(surface, HUESO, (x + 2, PINCHOS_H - 2), (x + 4, 2), 1)
    guardar_2x(surface, "pinchos.png")


def guardar_puerta() -> None:
    surface = pygame.Surface((GATE_W, GATE_H), pygame.SRCALPHA)
    dummy = object.__new__(Nivel)
    dummy.meta = pygame.Rect(11, GATE_H - 30, 20, 30)
    dummy.dibujar_meta(surface, CamaraCompleta())
    guardar_2x(surface, "puerta.png")


def guardar_solido() -> None:
    surface = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 1))
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

def guardar_pala() -> None:
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    pala = PalaRecogible(pygame.Rect(5, 1, 20, 30))
    pala.dibujar(surface, CamaraCompleta(), 0.0)
    guardar_2x(surface, "pala.png")


def guardar_plataforma() -> None:
    surface = pygame.Surface((96, 32), pygame.SRCALPHA)
    pygame.draw.rect(surface, (63, 57, 68), (0, 7, 96, 18), border_radius=4)
    pygame.draw.rect(surface, (28, 24, 32), (0, 7, 96, 18), 2, border_radius=4)
    pygame.draw.line(surface, ORO, (7, 9), (89, 9), 2)
    pygame.draw.line(surface, (115, 105, 122), (8, 22), (88, 22), 1)
    for x in (10, 86):
        pygame.draw.circle(surface, ORO, (x, 16), 2)
        pygame.draw.circle(surface, (20, 17, 24), (x, 16), 1)
    guardar_2x(surface, "plataforma_movil.png")


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


def guardar_paneles() -> None:
    panel = pygame.Surface((292, 70), pygame.SRCALPHA)
    pygame.draw.rect(panel, HUD_PANEL_ALTO, panel.get_rect(), border_radius=9)
    pygame.draw.rect(panel, (*HUD_BORDE, 180), panel.get_rect(), 1, border_radius=9)
    pygame.draw.line(panel, HUD_ORO, (12, 1), (280, 1), 1)
    guardar_2x(panel, "panel_hud.png")

    pista = pygame.Surface((780, 64), pygame.SRCALPHA)
    pygame.draw.rect(pista, HUD_PANEL_ALTO, pista.get_rect(), border_radius=9)
    pygame.draw.rect(pista, (*HUD_BORDE, 180), pista.get_rect(), 1, border_radius=9)
    pygame.draw.rect(pista, HUD_ORO, (0, 0, 4, 64), border_radius=2)
    guardar_2x(pista, "panel_pista.png")

    jefe = pygame.Surface((300, 30), pygame.SRCALPHA)
    pygame.draw.rect(jefe, HUD_PANEL_ALTO, jefe.get_rect(), border_radius=8)
    pygame.draw.rect(jefe, (*HUD_BORDE, 180), jefe.get_rect(), 1, border_radius=8)
    guardar_2x(jefe, "panel_jefe.png")


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


def generar_assets(niveles: list[Nivel]) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    titulo = pygame.image.load(str(ROOT / "capturas" / "titulo.png"))
    pygame.image.save(
        pygame.transform.smoothscale(titulo, (RENDER_W, RENDER_H)),
        ASSETS / "titulo.png",
    )
    shutil.copy2(FONT_SOURCE, ASSETS / FONT_SOURCE.name)

    guardar_jugador()
    guardar_enemigo()
    guardar_alma()
    guardar_pinchos()
    guardar_puerta()
    guardar_solido()
    guardar_golpe()
    guardar_pala()
    guardar_plataforma()
    guardar_jefe()
    guardar_onda()
    guardar_paneles()
    guardar_audio()
    guardar_barras()

    for i, nivel in enumerate(niveles, start=1):
        guardar_2x(generar_fondo_nivel(nivel), f"fondo_nivel_{i}.png")
    guardar_2x(generar_fondo_victoria(), "victoria.png")
    guardar_2x(generar_fondo_pausa(), "pausa.png")


# ------------------------------------------------------------
# Eventos compartidos
# ------------------------------------------------------------
def accion_sonido(nombre: str) -> dict:
    return accion("PlaySound", ["", f"SFX_{nombre}", '"no"', "100", "1"])


def eventos_dano(alto: int, destino_muerte: str = "Titulo") -> list[dict]:
    subeventos = [
        evento(
            [cond("NumberVariable", ["vidas", ">", "0"])],
            [
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("Scene", ["", "CurrentSceneName()", "no"]),
            ],
        ),
        evento(
            [cond("NumberVariable", ["vidas", "<=", "0"])],
            [
                accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["almas_totales", "=", "0"]),
                accion("Scene", ["", f'"{destino_muerte}"', "no"]),
            ],
        ),
    ]
    return [
        evento(
            [cond("CollisionNP", ["Jugador", "Pinchos", "", "", ""])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
            ],
            subeventos,
        ),
        evento(
            [cond("PosY", ["Jugador", ">", str(alto + 120)])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
            ],
            subeventos,
        ),
    ]


PISTAS_NATIVAS = {
    1: "FLECHAS: MOVERTE. ARRIBA: SALTAR. SHIFT: DASH. CRUZA EL PRIMER HUECO CON LA PLATAFORMA. LAS ALMAS DEL SALTO DE 3 BLOQUES MARCAN EL SALTO + DASH. EL POZO DE 7 NECESITA SHIFT EN EL AIRE. EN EL GRAN ABISMO SUBI EL ESCALON Y LA CORNISA, Y DASHEA DESDE ARRIBA.",
    2: "PRIMER ABISMO: SALTA Y USA SHIFT EN EL AIRE. LA PALA ESTA EN LA CORNISA. CRUZA EL HUECO GRANDE CON LA PLATAFORMA Y SUS ALMAS. EL ASCENSOR VERTICAL TE SUBE AL MURO. 10 ALMAS = 1 VIDA EXTRA.",
    3: "EL CUSTODIO TE PERSIGUE. ATACA SOLO CUANDO BRILLA EN ROJO. BUSCA LAS ALMAS Y ABRE EL PORTON.",
}


def acciones_camara_inicial() -> list[dict]:
    centro_x = str(GAME_W // 2)
    centro_y = str(GAME_H // 2)
    return [
        accion("ZoomCamera", ["", str(GAME_ZOOM), "", "0"]),
        accion("SetCameraCenterX", ["", "=", centro_x, "", "0"]),
        accion("SetCameraCenterY", ["", "=", centro_y, "", "0"]),
        accion("ZoomCamera", ["", str(GAME_ZOOM), '"UI"', "0"]),
        accion("SetCameraCenterX", ["", "=", centro_x, '"UI"', "0"]),
        accion("SetCameraCenterY", ["", "=", centro_y, '"UI"', "0"]),
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
                accion(
                    "Create",
                    [
                        "",
                        "OndaIzq",
                        "Jefe.X()",
                        "Jefe.Y() + Jefe.Height() / 2",
                        '""',
                    ],
                ),
                accion(
                    "Create",
                    [
                        "",
                        "OndaDer",
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
            [accion("Delete", ["OndaIzq", ""])],
        ),
        evento(
            [cond("PosX", ["OndaDer", ">", str(GAME_W)])],
            [accion("Delete", ["OndaDer", ""])],
        ),

        # --- Ondas dañan al jugador ---
        evento(
            [cond("CollisionNP", ["Jugador", "OndaIzq", "", "", ""])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                accion("Delete", ["OndaIzq", ""]),
                accion("Scene", ["", "CurrentSceneName()", "no"]),
            ],
        ),
        evento(
            [cond("CollisionNP", ["Jugador", "OndaDer", "", "", ""])],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                accion("Delete", ["OndaDer", ""]),
                accion("Scene", ["", "CurrentSceneName()", "no"]),
            ],
        ),

        # --- Contacto con jefe (daño si NO es vulnerable) ---
        evento(
            [
                cond("CollisionNP", ["Jugador", "Jefe", "", "", ""]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
            ],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
                accion("Scene", ["", "CurrentSceneName()", "no"]),
            ],
        ),

        # --- Golpe al jefe cuando es vulnerable ---
        evento(
            [
                cond("CollisionNP", ["GolpePala", "Jefe", "", "", ""]),
                cond("NumberObjectVariable", ["Jefe", "vulnerable", "=", "1"]),
            ],
            [
                accion("SetNumberObjectVariable", ["Jefe", "vida", "-", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "golpes_fase", "+", "1"]),
                accion("SetNumberObjectVariable", ["Jefe", "vulnerable", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "estado", "=", "0"]),
                accion("SetNumberObjectVariable", ["Jefe", "timer", "=", "2.0"]),
                accion_sonido("Golpe"),
                accion("Delete", ["GolpePala", ""]),
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
                accion("Delete", ["Jefe", ""]),
                accion("Delete", ["OndaIzq", ""]),
                accion("Delete", ["OndaDer", ""]),
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
    max_cam_x = max(0, nivel.ancho - GAME_W // 2)
    max_cam_y = max(0, nivel.alto - GAME_H // 2)
    centro_x = GAME_W // 2
    centro_y = GAME_H // 2
    if siguiente is None:
        siguiente = "Victoria" if indice == total else f"Nivel {indice + 1}"
    if pala_inicial is None:
        pala_inicial = indice == 3
    if texto_dash_sin_pala is None:
        texto_dash_sin_pala = (
            '"SHIFT: DASH · BUSCÁ LA PALA"' if indice == 2 else '"SHIFT: DASH"'
        )

    dash_input = cond_or(
        cond("KeyFromTextJustPressed", ["", '"LShift"']),
        cond("KeyFromTextJustPressed", ["", '"RShift"']),
    )
    ataque_input = cond("KeyFromTextJustPressed", ["", '"a"'])
    pausa_input = cond("KeyFromTextJustPressed", ["", '"Escape"'])
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
                accion("Scene", ["", "CurrentSceneName()", "no"]),
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
                    if reiniciar_vidas
                    else []
                ),
                *acciones_camara_inicial(),
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
                accion("PushScene", ["", '"Pausa"']),
            ],
        ),

        # Dirección horizontal: solo flechas. El comportamiento ya mueve con
        # Left/Right; estas variables guardan la última dirección para el dash.
        evento(
            [cond("KeyFromTextPressed", ["", '"Left"'])],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dir", "=", "-1"]),
                accion("PlatformBehavior::SimulateLeftKey", ["Jugador", "PlatformerObject"]),
            ],
        ),
        evento(
            [cond("KeyFromTextPressed", ["", '"Right"'])],
            [
                accion("SetNumberObjectVariable", ["Jugador", "dir", "=", "1"]),
                accion("PlatformBehavior::SimulateRightKey", ["Jugador", "PlatformerObject"]),
            ],
        ),

        # Salto con buffer y coyote time: ↑.
        evento(
            [cond("KeyFromTextJustPressed", ["", '"Up"'])],
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
                cond("KeyFromTextPressed", ["", '"Up"']),
                cond("PlatformBehavior::IsJumping", ["Jugador", "PlatformerObject"]),
            ],
            [accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"])],
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
                            ["", "GolpePala", "Jugador.X() + 24", "Jugador.Y() + 2", '""'],
                        ),
                    ],
                ),
                evento(
                    [cond("NumberObjectVariable", ["Jugador", "dir", "=", "-1"])],
                    [
                        accion("ChangeAnimation", ["Jugador", "=", "5"]),
                        accion(
                            "Create",
                            ["", "GolpePala", "Jugador.X() - 24", "Jugador.Y() + 2", '""'],
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
            [cond("CollisionNP", ["GolpePala", "Enemy", "", "", ""])],
            [
                accion("Delete", ["Enemy", ""]),
                accion("Delete", ["GolpePala", ""]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
            ],
        ),
        evento(
            [cond("NumberObjectVariable", ["GolpePala", "vida", ">", "0"])],
            [accion("SetNumberObjectVariable", ["GolpePala", "vida", "-", "TimeDelta()"])],
        ),
        evento(
            [cond("NumberObjectVariable", ["GolpePala", "vida", "<=", "0"])],
            [accion("Delete", ["GolpePala", ""])],
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
                    ["Jugador", "PlatformerObject", "=", "0", "yes"],
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
                    ["Jugador", "PlatformerObject", "=", "0", "yes"],
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
                    ["Jugador", "PlatformerObject", "=", str(int(MAX_CAIDA)), "yes"],
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

        # Cámara con zoom 2: muestra exactamente la misma zona de 960x540.
        evento(
            [],
            [
                accion(
                    "SetCameraCenterX",
                    [
                        "",
                        "=",
                        f"min(max(Jugador.X() + 16, {centro_x}), {max_cam_x})",
                        "",
                        "0",
                    ],
                ),
                accion(
                    "SetCameraCenterY",
                    [
                        "",
                        "=",
                        f"min(max(Jugador.Y() + 16, {centro_y}), {max_cam_y})",
                        "",
                        "0",
                    ],
                ),
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

        # Almas.
        evento(
            [cond("CollisionNP", ["Jugador", "Alma", "", "", ""])],
            [
                accion("Delete", ["Alma", ""]),
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
            [cond("CollisionNP", ["Jugador", "PalaRecogible", "", "", ""])],
            [
                accion("Delete", ["PalaRecogible", ""]),
                accion("SetNumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
                accion_sonido("PalaRecoger"),
            ],
        ),

        # Pisotón: el jugador viene desde arriba y ya tiene la pala.
        evento(
            [
                cond("CollisionNP", ["Jugador", "Enemy", "", "", ""]),
                cond("PosY", ["Jugador", "<", "Enemy.Y() - 10"]),
                cond("NumberObjectVariable", ["Jugador", "tiene_pala", "=", "1"]),
            ],
            [
                accion("Delete", ["Enemy", ""]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"]),
                accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"]),
                accion_sonido("Golpe"),
            ],
        ),

        # Daño por enemigo: contacto lateral o sin pala.
        evento(
            [
                cond("CollisionNP", ["Jugador", "Enemy", "", "", ""]),
                cond("PosY", ["Jugador", ">=", "Enemy.Y() - 10"]),
            ],
            [
                accion("SetNumberVariable", ["vidas", "-", "1"]),
                accion_sonido("Dano"),
            ],
            [
                evento(
                    [cond("NumberVariable", ["vidas", ">", "0"])],
                    [accion("Scene", ["", "CurrentSceneName()", "no"])],
                ),
                evento(
                    [cond("NumberVariable", ["vidas", "<=", "0"])],
                    [
                        accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                        accion("SetNumberVariable", ["almas", "=", "0"]),
                        accion("Scene", ["", f'"{destino_muerte}"', "no"]),
                    ],
                ),
            ],
        ),

        # Pinchos y caída al vacío.
        *eventos_dano(nivel.alto, destino_muerte=destino_muerte),

        # Portón. En niveles con jefe el portón está sellado hasta vencerlo.
        evento(
            (
                [cond("CollisionNP", ["Jugador", "Puerta", "", "", ""])]
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
                accion("Scene", ["", f'"{siguiente}"', "no"]),
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
                    ["HUD_Dash", "=", '"SHIFT: DASH · A: PALA"'],
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
def objetos_y_instancias_nivel(
    nivel: Nivel,
    indice: int,
    *,
    fondo: int | None = None,
    titulo: str | None = None,
    pista: str | None = None,
    pala_inicial: bool | None = None,
    hud_dash: str | None = None,
) -> tuple[list[dict], list[dict]]:
    if fondo is None:
        fondo = indice
    if titulo is None:
        titulo = f"NIVEL {indice} - {nivel.nombre.upper()}"
    if pista is None:
        pista = PISTAS_NATIVAS[indice]
    if pala_inicial is None:
        pala_inicial = indice == 3
    if hud_dash is None:
        hud_dash = (
            "SHIFT: DASH · A: PALA"
            if pala_inicial
            else ("SHIFT: DASH · BUSCÁ LA PALA" if indice == 2 else "SHIFT: DASH")
        )
    objetos = [
        objeto_sprite("Fondo", f"FondoNivel{fondo}"),
        objeto_tiled("Solido", "TexturaSolido", TILE, TILE, [comportamiento_plataforma()]),
        objeto_jugador(),
        objeto_sprite("Enemy", "Enemigo", variables_enemigo(), [comportamiento_enemigo()]),
        objeto_sprite("Alma", "Alma"),
        objeto_sprite("Pinchos", "Pinchos"),
        objeto_sprite("Puerta", "Puerta"),
        objeto_sprite("HUD_Barra", "BarraHUD"),
        objeto_sprite("HUD_BarraInferior", "BarraPista"),
        objeto_texto("HUD_Nivel", titulo, 20, HUESO, "center"),
        objeto_texto("HUD_Almas", "ALMAS 0 · VIDA +0/10", 18, AMARILLO),
        objeto_texto("HUD_Vidas", "VIDAS 3/5", 18, ROJO),
        objeto_texto("HUD_Aviso", "", 12, ROJO),
        objeto_texto("HUD_Dash", hud_dash, 12, TURQUESA),
        objeto_texto("HUD_Pista", "\n".join(textwrap.wrap(pista, width=84)), 15, CREMA, "center"),
        objeto_pala(),
        objeto_jefe(),
        objeto_onda(),
        objeto_onda_der(),
        objeto_plataforma(),
        objeto_golpe(),
    ]

    instancias = [
        instancia("Fondo", 0, 0, 0, tam=(nivel.ancho, nivel.alto)),
    ]
    for solido in nivel.solidos:
        instancias.append(
            instancia("Solido", solido.x, solido.y, 1, tam=(solido.width, solido.height))
        )
    for peligro in nivel.peligros:
        instancias.append(instancia("Pinchos", peligro.x, peligro.y, 2, tam=(PINCHOS_W, PINCHOS_H)))
    for alma in nivel.almas:
        instancias.append(
            instancia(
                "Alma",
                alma.rect.centerx - SOUL_SPRITE // 2,
                alma.rect.centery - SOUL_SPRITE // 2,
                3,
                tam=(SOUL_SPRITE, SOUL_SPRITE),
            )
        )
    for pala in nivel.palas:
        instancias.append(
            instancia(
                "PalaRecogible",
                pala.rect.x,
                pala.rect.y,
                4,
                tam=(pala.rect.width, pala.rect.height),
            )
        )
    for plataforma in nivel.plataformas:
        instancias.append(
            instancia(
                "PlataformaMovil",
                plataforma.rect.x,
                plataforma.rect.y,
                4,
                tam=(plataforma.rect.width, plataforma.rect.height),
                variables=[
                    {"name": "origen_x", "type": "number", "value": plataforma.inicial_rect.x},
                    {"name": "origen_y", "type": "number", "value": plataforma.inicial_rect.y},
                    {"name": "amplitud", "type": "number", "value": plataforma.amplitud},
                    {"name": "velocidad", "type": "number", "value": plataforma.velocidad},
                    {"name": "fase", "type": "number", "value": round(plataforma.fase, 4)},
                    {"name": "eje", "type": "number", "value": 1 if plataforma.eje == "h" else 0},
                ],
            )
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
    for enemigo in nivel.enemigos:
        instancias.append(
            instancia(
                "Enemy",
                enemigo.rect.x,
                enemigo.rect.y,
                5,
                tam=(ENEMIGO_ANCHO, ENEMIGO_ALTO),
                variables=[
                    {"name": "min_x", "type": "number", "value": enemigo.minimo_x},
                    {"name": "max_x", "type": "number", "value": enemigo.maximo_x},
                ],
            )
        )
    for jefe in nivel.jefes:
        min_x = jefe.rect.x - 80
        max_x = jefe.rect.x + 80
        instancias.append(
            instancia(
                "Jefe",
                jefe.rect.x,
                jefe.rect.y,
                5,
                tam=(JEFE_ANCHO, JEFE_ALTO),
                variables=[
                    {"name": "vida", "type": "number", "value": JEFE_VIDA},
                    {"name": "fase", "type": "number", "value": 1},
                    {"name": "estado", "type": "number", "value": 0},
                    {"name": "timer", "type": "number", "value": 1.25},
                    {"name": "vulnerable", "type": "number", "value": 0},
                    {"name": "golpes_fase", "type": "number", "value": 0},
                    {"name": "dir", "type": "number", "value": 1},
                    {"name": "min_x", "type": "number", "value": min_x},
                    {"name": "max_x", "type": "number", "value": max_x},
                ],
            )
        )
    instancias.append(
        instancia(
            "Jugador",
            nivel.spawn[0] - 4,
            nivel.spawn[1] - 1,
            6,
            tam=(PLAYER_W, PLAYER_H),
        )
    )

    instancias.extend(
        [
            instancia("HUD_Barra", 0, 0, 0, "UI", tam=(GAME_W, 52)),
            instancia("HUD_BarraInferior", 0, GAME_H - 58, 0, "UI", tam=(GAME_W, 58)),
            instancia("HUD_Nivel", 130, 9, 1, "UI", tam=(700, 30)),
            instancia("HUD_Almas", 18, 14, 1, "UI"),
            instancia("HUD_Vidas", 860, 14, 1, "UI"),
            instancia("HUD_Aviso", 620, 34, 1, "UI"),
            instancia("HUD_Dash", 18, 35, 1, "UI"),
            instancia("HUD_Pista", 20, GAME_H - 52, 1, "UI", tam=(920, 46)),
        ]
    )
    return objetos, instancias


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
            [cond("KeyFromTextJustPressed", ["", '"Return"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Nivel 1"', "no"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ["", '"t"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Salas"', "no"]),
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
            [cond("KeyFromTextJustPressed", ["", '"Return"'])],
            [
                accion("SetNumberVariable", ["vidas", "=", str(VIDAS_INICIALES)]),
                accion("SetNumberVariable", ["almas", "=", "0"]),
                accion("SetNumberVariable", ["almas_para_vida", "=", "0"]),
                accion("SetNumberVariable", ["almas_totales", "=", "0"]),
                accion_sonido("UI"),
                accion("Scene", ["", '"Titulo"', "no"]),
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
                cond("KeyFromTextJustPressed", ["", '"Up"']),
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "3"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ["", '"Up"']),
                cond("NumberVariable", ["menu_opcion", ">", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "-", "1"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ["", '"Down"']),
                cond("NumberVariable", ["menu_opcion", "=", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "=", "1"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ["", '"Down"']),
                cond("NumberVariable", ["menu_opcion", "<", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("SetNumberVariable", ["menu_opcion", "+", "1"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ["", '"Return"']),
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("PopScene", [""]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ["", '"Return"']),
                cond("NumberVariable", ["menu_opcion", "=", "2"]),
            ],
            [
                accion_sonido("UI"),
                accion("ModVarGlobal", ["reiniciar", "=", "1"]),
                accion("PopScene", [""]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ["", '"Return"']),
                cond("NumberVariable", ["menu_opcion", "=", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Titulo"', "yes"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ["", '"Escape"'])],
            [
                accion_sonido("UI"),
                accion("PopScene", [""]),
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
        cond("KeyFromTextJustPressed", ["", '"Up"']),
        cond("KeyFromTextJustPressed", ["", '"w"']),
    )
    abajo = cond_or(
        cond("KeyFromTextJustPressed", ["", '"Down"']),
        cond("KeyFromTextJustPressed", ["", '"s"']),
    )
    volver = cond_or(
        cond("KeyFromTextJustPressed", ["", '"Escape"']),
        cond("KeyFromTextJustPressed", ["", '"t"']),
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
                cond("KeyFromTextJustPressed", ["", '"Return"']),
                cond("NumberVariable", ["menu_opcion", "=", "1"]),
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Sala 1"', "no"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ["", '"Return"']),
                cond("NumberVariable", ["menu_opcion", "=", "2"]),
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Sala 2"', "no"]),
            ],
        ),
        evento(
            [
                cond("KeyFromTextJustPressed", ["", '"Return"']),
                cond("NumberVariable", ["menu_opcion", "=", "3"]),
            ],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Sala 3"', "no"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ["", '"1"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Sala 1"', "no"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ["", '"2"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Sala 2"', "no"]),
            ],
        ),
        evento(
            [cond("KeyFromTextJustPressed", ["", '"3"'])],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Sala 3"', "no"]),
            ],
        ),
        evento(
            [volver],
            [
                accion_sonido("UI"),
                accion("Scene", ["", '"Titulo"', "no"]),
            ],
        ),
    ]
    salas = escena("Salas", objetos, instancias, eventos)
    salas["variables"] = [{"name": "menu_opcion", "type": "number", "value": 1}]
    return salas


def escena_sala(numero: int, sala: dict) -> dict:
    nivel = Nivel(sala["mapa"], sala["nombre"], sala["pista"], sala["tema"])
    fondo = int(sala["nivel"]) + 1
    pala_inicial = bool(sala["pala"])
    pista = sala["pista"].replace("J", "A") if numero == 2 else sala["pista"]
    hud_dash = (
        "SHIFT: DASH · A: PALA"
        if pala_inicial
        else ("SHIFT: DASH · BUSCÁ LA PALA" if numero == 2 else "SHIFT: DASH")
    )
    objetos, instancias = objetos_y_instancias_nivel(
        nivel,
        fondo,
        fondo=fondo,
        titulo=sala["nombre"].upper(),
        pista=pista,
        pala_inicial=pala_inicial,
        hud_dash=hud_dash,
    )
    eventos = eventos_nivel(
        nivel,
        fondo,
        3,
        siguiente="Salas",
        pala_inicial=pala_inicial,
        texto_dash_sin_pala=(
            '"SHIFT: DASH · BUSCÁ LA PALA"' if numero == 2 else '"SHIFT: DASH"'
        ),
        destino_muerte="Salas",
        reiniciar_vidas=True,
    )
    return escena(f"Sala {numero}", objetos, instancias, eventos)


# ------------------------------------------------------------
# Proyecto
# ------------------------------------------------------------
def construir_proyecto(niveles: list[Nivel]) -> dict:
    base = json.loads(BASE_PROJECT.read_text(encoding="utf-8"))

    recursos = [
        recurso_imagen("FondoTitulo", "assets/titulo.png"),
        recurso_imagen("FondoVictoria", "assets/victoria.png"),
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
        recurso_imagen("PlataformaMovil", "assets/plataforma_movil.png"),
        recurso_imagen("Enemigo", "assets/enemigo.png"),
        recurso_imagen("Alma", "assets/alma.png"),
        recurso_imagen("Pinchos", "assets/pinchos.png"),
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
    ]
    for i in range(1, len(niveles) + 1):
        recursos.append(recurso_imagen(f"FondoNivel{i}", f"assets/fondo_nivel_{i}.png"))

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
    ]
    base["layouts"] = [escena_titulo(), escena_pausa(), escena_victoria(), escena_salas()]
    for i, sala in enumerate(SALAS_PRUEBA[:3], start=1):
        base["layouts"].append(escena_sala(i, sala))
    for i, nivel in enumerate(niveles, start=1):
        objetos, instancias = objetos_y_instancias_nivel(nivel, i)
        base["layouts"].append(
            escena(f"Nivel {i}", objetos, instancias, eventos_nivel(nivel, i, len(niveles)))
        )
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


def main() -> int:
    pygame.init()
    OUT.mkdir(parents=True, exist_ok=True)
    niveles = [Nivel(datos["mapa"], datos["nombre"], datos["pista"], datos["tema"]) for datos in NIVELES]

    generar_assets(niveles)
    proyecto = construir_proyecto(niveles)
    destino = OUT / PROJECT_NAME
    destino.write_text(json.dumps(proyecto, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Proyecto: {destino}")
    print(f"Resolución: {RENDER_W}x{RENDER_H} (zoom {GAME_ZOOM})")
    print(f"Escenas: {[l['name'] for l in proyecto['layouts']]}")
    print(
        "Datos: "
        + ", ".join(
            f"{n.nombre} {n.ancho}x{n.alto} ({len(n.solidos)} sólidos, "
            f"{len(n.almas)} almas, {len(n.enemigos)} enemigos, "
            f"{len(n.peligros)} peligros)"
            for n in niveles
        )
    )
    print(f"Recursos: {len(proyecto['resources']['resources'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
